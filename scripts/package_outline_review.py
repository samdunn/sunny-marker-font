"""Package a development VF without changing any released downloads."""
from pathlib import Path

from fontTools.ttLib import TTFont, newTable
from fontTools.varLib.instancer import instantiateVariableFont
import package_gf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/outline-review/candidate"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    font = TTFont(ROOT / "build/SunnyMarkerVariable.ttf")
    font = instantiateVariableFont(font, {"opsz": (10, 14, 36)}, inplace=True)
    font["fvar"].instances = [i for i in font["fvar"].instances if i.coordinates["wdth"] == 100]
    for instance in font["fvar"].instances:
        instance.coordinates["opsz"] = 14
    if "avar" not in font:
        font["avar"] = newTable("avar")
        font["avar"].segments = {a.axisTag: {-1.0: -1.0, 0.0: 0.0, 1.0: 1.0} for a in font["fvar"].axes}
    for nid, value in ((1, "Sunny Marker"), (2, "Regular"), (4, "Sunny Marker Regular"),
                       (6, "SunnyMarker-Regular"), (25, "SunnyMarker")):
        package_gf.set_name(font, value, nid)
    for nid in (16, 17):
        font["name"].removeNames(nameID=nid)
    font["OS/2"].fsSelection = 0xC0
    font["head"].macStyle = 0
    font["post"].italicAngle = 0
    package_gf.VERSION = "1.313"
    package_gf.apply_metadata(font)
    package_gf.build_stat(font)
    package_gf.set_name(font, "Version 1.313; development outline review", 5)
    font.save(OUT / "SunnyMarker[opsz,slnt,wdth,wght].ttf")
    package_gf.save_woff2(font, OUT / "SunnyMarker-Variable.woff2")
    print(OUT)


if __name__ == "__main__":
    main()
