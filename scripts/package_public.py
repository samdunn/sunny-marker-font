"""Create a history-free source ZIP using only Git-tracked project files."""
from pathlib import Path
import hashlib
import subprocess
import zipfile

from package_gf import VERSION

ROOT = Path(__file__).resolve().parents[1]
output = ROOT / "release" / f"sunny-marker-public-source-{VERSION}.zip"
files = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT, timeout=60).decode().split("\0")
manifest = {}
with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
    for name in sorted(filter(None, files)):
        path = ROOT / name
        if not path.is_file() or name.startswith("release/sunny-marker-public-source-"):
            continue
        parts = Path(name).parts
        if any(p in {".git", ".venv", ".sunny", ".wrangler", "qa", "build"} for p in parts):
            raise ValueError(f"Private or generated directory in export: {name}")
        if path.name.startswith((".env", ".dev.vars")) or path.suffix in {".key", ".pem", ".pickle"}:
            raise ValueError(f"Private file in export: {name}")
        if path.is_symlink():
            raise ValueError(f"Review symlinks before exporting: {name}")
        data = path.read_bytes()
        manifest[name] = hashlib.sha256(data).hexdigest()
        info = zipfile.ZipInfo(f"sunny-marker/{name}", (2026, 9, 15, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, data)
    info = zipfile.ZipInfo("sunny-marker/SNAPSHOT-SHA256SUMS.txt", (2026, 9, 15, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, "".join(f"{digest}  {name}\n" for name, digest in manifest.items()))
print(f"{output.name}: {len(manifest)} files; no Git history")
