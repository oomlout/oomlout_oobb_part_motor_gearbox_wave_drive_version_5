"""Explicit publication of the generated, standalone viewer and PDF to GitHub Pages.

Run from the repository root: python components/wave_drive/publish_github.py
Requires Git and an authenticated GitHub CLI. Never called by the CAD build.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]


def main(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("root", ROOT)
    root = Path(kwargs["root"])
    kwargs.setdefault("part_folder", next((root/"parts").glob("*/assembly/validation.json")).parent.parent)
    output = Path(kwargs["part_folder"])/"assembly"
    manifest = json.loads((output/"assembly_manifest.json").read_text())
    report = json.loads((output/"validation.json").read_text())
    assert report["status"] == "passed"
    for extension in ["pdf", "html"]:
        assert hashlib.sha256((output/("assembly_instructions."+extension)).read_bytes()).hexdigest() == report[extension+"_sha256"]
    repository = manifest["book"]["project_url"].removeprefix("https://github.com/")
    assert repository.count("/") == 1

    def run(args, **options):
        return subprocess.run(args, cwd=root, check=True, capture_output=True, **options)

    remote = run(["git", "ls-remote", "origin", "refs/heads/gh-pages"], text=True).stdout.strip()
    parent = remote.split()[0] if remote else None
    if parent:
        run(["git", "fetch", "origin", "gh-pages"])
    with tempfile.TemporaryDirectory(prefix="wave-drive-pages-") as temporary:
        environment = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary)/"index"))
        run(["git", "read-tree", parent if parent else "--empty"], env=environment)
        files = {
            "index.html": (output/"assembly_instructions.html").read_bytes(),
            "assembly_instructions.pdf": (output/"assembly_instructions.pdf").read_bytes(),
            ".nojekyll": b"",
        }
        for name, content in files.items():
            blob = run(["git", "hash-object", "-w", "--stdin"], input=content).stdout.decode().strip()
            run(["git", "update-index", "--add", "--cacheinfo", "100644", blob, name], env=environment)
        tree = run(["git", "write-tree"], env=environment, text=True).stdout.strip()
        command = ["git", "commit-tree", tree, "-m", "Publish wave-drive assembly viewer and booklet"]
        if parent:
            command.extend(["-p", parent])
        commit = run(command, text=True).stdout.strip()
        run(["git", "push", "origin", commit+":refs/heads/gh-pages"])
    api = "repos/"+repository+"/pages"
    check = subprocess.run(["gh", "api", api], cwd=root, text=True, capture_output=True)
    payload = {"build_type":"legacy", "source":{"branch":"gh-pages", "path":"/"}}
    if check.returncode:
        if "404" not in check.stderr:
            raise RuntimeError(check.stderr)
        try:
            run(["gh", "api", "--method", "POST", api, "--input", "-"], input=json.dumps(payload).encode())
        except subprocess.CalledProcessError as error:
            # Creating gh-pages can enable Pages automatically between GET/POST.
            if b"409" not in error.stderr:
                raise RuntimeError(error.stderr.decode()) from error
    else:
        existing = json.loads(check.stdout)
        if existing.get("source") != payload["source"] or existing.get("build_type") != "legacy":
            run(["gh", "api", "--method", "PUT", api, "--input", "-"], input=json.dumps(payload).encode())
    site = json.loads(run(["gh", "api", api], text=True).stdout)
    print(json.dumps({"pages_url":site["html_url"], "commit":commit, "status":site["status"]}))


if __name__ == "__main__":
    main()
