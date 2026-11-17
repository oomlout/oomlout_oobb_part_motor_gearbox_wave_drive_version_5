"""Blender-only renderer. Run using working_blender.py; CAD coordinates are mm."""
import copy
import json
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
import numpy as np


def finish(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("roughness", 0.4)
    kwargs.setdefault("metallic", 0.0)
    rgb = [int(kwargs["color"][i:i+2], 16)/255 for i in [0, 2, 4]]
    linear = [v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4 for v in rgb]
    mat = bpy.data.materials.new(kwargs["name"])
    mat.use_nodes = True
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*linear, 1)
    shader.inputs["Roughness"].default_value = kwargs["roughness"]
    shader.inputs["Metallic"].default_value = kwargs["metallic"]
    mat.diffuse_color = (*linear, 1)
    return mat


def main(**kwargs):
    folder = Path(kwargs["folder"])
    style = json.loads((folder/"style.json").read_text())
    records = json.loads((folder/"cache"/"instances.json").read_text())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    materials = {key: finish(**value) for key, value in style["materials"].items()}
    prefs = bpy.context.preferences.addons["cycles"].preferences
    device = "CPU"
    for backend in ["OPTIX", "CUDA", "HIP", "METAL"]:
        try:
            prefs.compute_device_type = backend
            prefs.get_devices()
            available = [d for d in prefs.devices if d.type == backend]
            if available:
                for d in prefs.devices:
                    d.use = d in available
                device = "GPU"
                break
        except (TypeError, ValueError):
            continue
    (folder/"raw").mkdir(exist_ok=True)
    (folder/"scenes").mkdir(exist_ok=True)
    anchors = {}
    scene_log = {}
    with np.load(folder/"cache"/"meshes.npz") as arrays:
        for key, view in style["views"].items():
            scene = bpy.data.scenes.new(key)
            bpy.context.window.scene = scene
            scene.render.engine = "CYCLES"
            scene.cycles.samples = style["samples"]
            scene.cycles.use_denoising = True
            scene.cycles.device = device
            scene.render.film_transparent = True
            scene.render.image_settings.file_format = "PNG"
            scene.render.image_settings.color_mode = "RGBA"
            scene.view_settings.view_transform = style["view_transform"]
            scene.unit_settings.system = "METRIC"
            scene.unit_settings.scale_length = 0.001
            scene.world = bpy.data.worlds.new(key+" softbox surroundings")
            scene.world.use_nodes = True
            background = scene.world.node_tree.nodes["Background"]
            background.inputs[0].default_value = style["world_color"]
            background.inputs[1].default_value = style["world_strength"]
            samples, objects, positions = [], {}, {}
            groups = {}
            for record in records:
                if "include_names" in view and record["name"] not in view["include_names"]:
                    continue
                if "include_names" not in view and "views" in record and key not in record["views"]:
                    continue
                if key == "open_mechanism" and not record["open"]:
                    continue
                if key == "parts" and record["kind"] != "printed":
                    continue
                name = record["name"]
                points = arrays[name+("_layout" if key == "parts" else "_v")].copy()
                faces = arrays[name+("_layout_f" if key == "parts" else "_f")]
                points += np.array(view.get("offsets", {}).get(name, [0, 0, 0]))
                if key in ["exploded", "exploded_motor"]:
                    points[:, 2] += (record["level"]-8)*view["spacing"]
                mesh = bpy.data.meshes.new(name)
                mesh.from_pydata(points.tolist(), [], faces.tolist())
                mesh.update()
                obj = bpy.data.objects.new(name, mesh)
                group = record["group"]
                if group not in groups:
                    groups[group] = bpy.data.collections.new(group)
                    scene.collection.children.link(groups[group])
                groups[group].objects.link(obj)
                material = "context" if name in view.get("muted_names", []) else record["material"]
                obj.data.materials.append(materials[material])
                obj["scad_part"] = record["part"]
                obj["inventory_kind"] = record["kind"]
                objects[name] = obj
                positions[name] = points
                samples.append(points)
            eye = Vector(view["eye"])
            rot = eye.to_track_quat("Z", "Y")
            axes = np.array(rot.to_matrix())
            coords = np.concatenate(samples) @ axes
            low, high = coords.min(axis=0), coords.max(axis=0)
            target = Vector(axes @ ((low+high)/2))
            width, height = view["size"]
            span = high-low
            camera_data = bpy.data.cameras.new(key+" orthographic")
            camera_data.type = "ORTHO"
            camera_data.clip_end = 3000
            camera_data.ortho_scale = max(span[0]*max(1, height/width), span[1]*max(1, width/height))*view["margin"]
            camera = bpy.data.objects.new(key+" camera", camera_data)
            scene.collection.objects.link(camera)
            camera.rotation_euler = rot.to_euler()
            camera.location = target+eye.normalized()*800
            scene.camera = camera
            for index, item in enumerate(style["lights"]):
                light = bpy.data.lights.new(f"{key} softbox {index+1}", "AREA")
                light.energy = item["power"]
                light.shape = "DISK"
                light.size = item["size"]
                lamp = bpy.data.objects.new(light.name, light)
                scene.collection.objects.link(lamp)
                offset = Vector(item["offset"])
                # Enlarge the studio for laid-out parts while preserving illumination.
                factor = max(1, float(max(span[:2]))/190) if key in ["parts", "exploded", "exploded_motor"] else 1
                lamp.location = target+offset*factor
                lamp.rotation_euler = (-offset).to_track_quat("-Z", "Y").to_euler()
                light.energy *= factor**2
                light.size *= factor
            scene.render.resolution_x = width
            scene.render.resolution_y = height
            scene.render.resolution_percentage = 100
            scene.render.filepath = str(folder/"raw"/(key+".png"))
            bpy.context.view_layer.update()
            bpy.ops.render.render(write_still=True)
            anchors[key] = {}
            for name, points in positions.items():
                projected = points @ axes
                point = points[np.argmax(projected[:, 0])]
                screen = world_to_camera_view(scene, camera, Vector(point))
                anchors[key][name] = [float(screen.x*width), float((1-screen.y)*height)]
            anchors[key]["insertion_arrows"] = []
            for name, offset in view.get("arrow_offsets", {}).items():
                point = positions[name].mean(axis=0)
                # The leader runs alongside the insertion axis, outside the part.
                radius = max(positions[name].max(axis=0)-positions[name].min(axis=0))/2
                side = Vector(axes[:, 0])*(radius+3)
                ends = [Vector(point)+side, Vector(point)-Vector(offset)+side]
                screens = [world_to_camera_view(scene, camera, p) for p in ends]
                anchors[key]["insertion_arrows"].append({
                    "name": name,
                    "points": [[float(p.x*width), float((1-p.y)*height)] for p in screens],
                })
            scene_log[key] = {
                "objects": list(objects),
                "size": view["size"],
                "camera_eye": view["eye"],
                "ortho_scale_mm": camera_data.ortho_scale,
                "device": device,
            }
    empty = bpy.data.scenes.get("Scene")
    if empty:
        bpy.data.scenes.remove(empty)
    bpy.context.window.scene = bpy.data.scenes.get("assembly") or bpy.data.scenes[0]
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"
                area.spaces.active.shading.color_type = "MATERIAL"
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/"scenes"/"wave_drive.blend"))
    (folder/"raw"/"anchors.json").write_text(json.dumps(anchors, indent=2))
    (folder/"raw"/"scenes.json").write_text(json.dumps(scene_log, indent=2))


if __name__ == "__main__":
    main(folder=sys.argv[-1])
