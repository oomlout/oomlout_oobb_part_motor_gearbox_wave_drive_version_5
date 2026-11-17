# Read-only cycloidal reference

The source project was used only for inspection and copying. Nothing in its folder was edited or executed.

`sources.json` records the four exact source paths and SHA-256 digests copied here. These copies are reference material; the wave-drive runtime does not import them or depend on the cycloidal checkout.

Retained interfaces:

- Two 6810 bearings: 50 mm bore, 65 mm outside diameter, 7 mm width.
- 6704 bearing family: 20 mm bore, 27 mm outside diameter, 4 mm width. This mechanism uses two shaft supports and one eccentric wave bearing.
- OOBB's 15 mm M6 grid, 7.5 mm M3 intermediate stations, and the inner M3 half-grid mounting pattern.
- Removable bearing seats and retainers, with hardware pockets built from OOBB primitives.
- One catalogue item for a complete gearbox, with separate named printed pieces inside it.

Changed mechanism:

- The profile ring is stationary; the slotted roller cage is the output.
- Twenty loose 6 x 8 mm cylinders replace stationary pin contacts.
- A single 0.75 mm eccentric drives a free-running circular wave wheel.
- Output rotation is opposite the input at 20:1. The previous cycloidal architecture's output direction is not reused.
- Native OpenSCAD replaces SolidCraft. There is no native STEP pipeline.

