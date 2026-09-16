"""Run a checksum-pinned Gitleaks binary with redacted, private reports."""
import hashlib
import io
from pathlib import Path
import platform
import subprocess
import sys
import tarfile
import tempfile
import requests

VERSION = "8.30.1"
HASHES = {
    "darwin_arm64": "b40ab0ae55c505963e365f271a8d3846efbc170aa17f2607f13df610a9aeb6a5",
    "darwin_x64": "dfe101a4db2255fc85120ac7f3d25e4342c3c20cf749f2c20a18081af1952709",
    "linux_arm64": "e4a487ee7ccd7d3a7f7ec08657610aa3606637dab924210b3aee62570fb4b080",
    "linux_x64": "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb",
}


def main():
    target = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    architecture = {"aarch64": "arm64", "arm64": "arm64", "x86_64": "x64", "AMD64": "x64"}[platform.machine()]
    key = f"{platform.system().lower()}_{architecture}"
    expected = HASHES[key]
    url = f"https://github.com/gitleaks/gitleaks/releases/download/v{VERSION}/gitleaks_{VERSION}_{key}.tar.gz"
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    archive = response.content
    if hashlib.sha256(archive).hexdigest() != expected:
        raise RuntimeError("Gitleaks checksum mismatch")
    with tempfile.TemporaryDirectory(prefix="sunny-marker-audit-") as directory:
        binary = Path(directory) / "gitleaks"
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            binary.write_bytes(tar.extractfile("gitleaks").read())
        binary.chmod(0o700)
        commands = [[str(binary), "dir", "--redact", "--max-archive-depth", "3", str(target)]]
        if (target / ".git").exists():
            commands.append([str(binary), "git", "--redact", "--log-opts=--all", str(target)])
        for command in commands:
            subprocess.run(command, check=True, timeout=300)


if __name__ == "__main__":
    main()
