"""Non-executable serialization for the local parametric master cache.

JSON objects cannot represent tuple kerning keys, so encode pairs explicitly.
The cache contains only coordinates, numbers, glyph names and contour commands.
"""
import json
from pathlib import Path


def save_master_data(path, data):
    result = dict(data)
    result["masters"] = {
        name: {**master, "kern": [[*pair, value] for pair, value in master["kern"].items()]}
        for name, master in data["masters"].items()
    }
    Path(path).write_text(json.dumps(result, allow_nan=False), encoding="utf-8")


def load_master_data(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    data["emit_pairs"] = [tuple(pair) for pair in data["emit_pairs"]]
    for master in data["masters"].values():
        master["kern"] = {(left, right): value for left, right, value in master["kern"]}
    return data
