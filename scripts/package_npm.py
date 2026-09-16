"""Pack the allowlisted npm distribution from the verified release font."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages/sunny-marker"


def main():
    metadata = json.loads((PACKAGE / "package.json").read_text())
    manifest = json.loads((ROOT / "fonts/manifest.json").read_text())
    assert metadata["version"] == manifest["version"] + ".0"
    source = ROOT / "fonts/webfonts/SunnyMarker-Variable.woff2"
    record = next(f for f in manifest["files"] if f["path"] == str(source.relative_to(ROOT)))
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest == record["sha256"], "Font does not match the release manifest"
    (PACKAGE / "files").mkdir(exist_ok=True)
    shutil.copyfile(source, PACKAGE / "files" / source.name)
    shutil.copyfile(ROOT / "OFL.txt", PACKAGE / "OFL.txt")
    output = ROOT / "web/downloads"
    output.mkdir(exist_ok=True)
    # No lifecycle hooks are needed to install or pack this distribution.
    result = subprocess.run(
        ["npm", "pack", "--ignore-scripts", "--json", "--pack-destination", str(output)],
        cwd=PACKAGE, check=True, capture_output=True, text=True,
    )
    packed = json.loads(result.stdout)[0]
    allowed = {"package.json", "index.css", "next.js", "next.d.ts", "README.md", "OFL.txt",
               "files/SunnyMarker-Variable.woff2"}
    assert {f["path"] for f in packed["files"]} == allowed, "Unexpected npm package contents"
    archive = output / packed["filename"]
    with tarfile.open(archive) as tar:
        assert all(m.isfile() for m in tar.getmembers()), "Non-file archive entry"
        assert tar.extractfile("package/files/SunnyMarker-Variable.woff2").read() == source.read_bytes()
        assert tar.extractfile("package/OFL.txt").read() == (ROOT / "OFL.txt").read_bytes()
    print(json.dumps({"package": metadata["name"], "version": metadata["version"],
                      "file": str(archive.relative_to(ROOT)), "files": sorted(allowed),
                      "bytes": archive.stat().st_size, "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
