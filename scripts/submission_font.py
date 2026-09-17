"""Shared, import-safe Google Fonts style export and naming."""

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.otlLib.builder import buildStatTable
from package_gf import set_name


def prepare_submission_font(source, destination, italic=False, version="1.313", optimize=True):
    font = TTFont(source, recalcTimestamp=False)
    font = instantiateVariableFont(font, {"slnt": -9 if italic else 0}, inplace=True, optimize=optimize)
    style = "Italic" if italic else "Regular"
    for nid, value in (
        (1, "Sunny Marker"),
        (2, style),
        (4, "Sunny Marker " + style),
        (6, "SunnyMarker-" + style),
        (25, "SunnyMarkerItalic" if italic else "SunnyMarker"),
    ):
        set_name(font, value, nid)
    font["OS/2"].fsSelection = 0x180 | (1 if italic else 0x40)
    font["head"].macStyle = 2 if italic else 0
    font["post"].italicAngle = -9 if italic else 0
    font["hhea"].caretSlopeRise = 1000 if italic else 1
    font["hhea"].caretSlopeRun = 158 if italic else 0
    for name_id, value in (
        (9, "Sam Dunn"),
        (12, "https://samdunn.org"),
        (5, "Version " + version),
        (3, f"{version};NONE;{font['name'].getDebugName(6)}"),
    ):
        set_name(font, value, name_id)
    font["head"].fontRevision = float(version)
    for instance in font["fvar"].instances:
        style = font["name"].getDebugName(instance.subfamilyNameID)
        instance.postscriptNameID = font["name"].addName(
            "SunnyMarker-" + style.replace(" ", ""), platforms=((3, 1, 0x409),)
        )
    buildStatTable(
        font,
        [
            {
                "tag": "opsz",
                "name": "Optical size",
                "values": [{"value": 14, "name": "14pt"}],
            },
            {
                "tag": "wdth",
                "name": "Width",
                "values": [
                    {"value": v, "name": n, **({"flags": 2} if v == 100 else {})}
                    for v, n in [
                        (75, "Condensed"),
                        (87.5, "SemiCondensed"),
                        (100, "Normal"),
                        (112.5, "SemiExpanded"),
                        (125, "Expanded"),
                    ]
                ],
            },
            {
                "tag": "wght",
                "name": "Weight",
                "values": [
                    {
                        "value": v,
                        "name": n,
                        **({"flags": 2, "linkedValue": 700} if v == 400 else {}),
                    }
                    for v, n in [
                        (300, "Light"),
                        (400, "Regular"),
                        (500, "Medium"),
                        (600, "SemiBold"),
                        (700, "Bold"),
                    ]
                ],
            },
            {
                "tag": "ital",
                "name": "Italic",
                "values": [
                    {
                        "value": 1 if italic else 0,
                        "name": "Italic" if italic else "Roman",
                        **({} if italic else {"flags": 2, "linkedValue": 1}),
                    }
                ],
            },
        ],
        macNames=False,
    )
    font.save(destination)

