"""Export parametric masters as editable UFO 3 sources for fontmake.

The design generator supplies the outlines, advances and feature source before
compilation. UFOs are committed so contributors can use standard font editors
without installing the raster tracing toolchain.
"""
from pathlib import Path

from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.pens.pointPen import ReverseContourPointPen
from ufoLib2 import Font


def export_master(ttfont, features, path, outlines=None, sidebearings=None):
    font = Font()
    info = font.info
    info.familyName = "Sunny Marker"
    info.styleName = ttfont["name"].getDebugName(2)
    info.unitsPerEm = ttfont["head"].unitsPerEm
    info.ascender = 960
    info.descender = -340
    info.capHeight = ttfont["OS/2"].sCapHeight
    info.xHeight = ttfont["OS/2"].sxHeight
    info.italicAngle = ttfont["post"].italicAngle
    info.styleMapStyleName = "italic" if info.italicAngle else "regular"
    info.openTypeOS2WeightClass = ttfont["OS/2"].usWeightClass
    info.openTypeOS2WidthClass = ttfont["OS/2"].usWidthClass
    info.openTypeOS2VendorID = "NONE"
    info.openTypeOS2Type = []
    info.openTypeOS2Selection = [7]
    info.openTypeOS2TypoAscender = 960
    info.openTypeOS2TypoDescender = -340
    info.openTypeOS2TypoLineGap = 0
    info.openTypeOS2WinAscent = 960
    info.openTypeOS2WinDescent = 340
    info.openTypeHheaAscender = 960
    info.openTypeHheaDescender = -340
    info.openTypeHheaLineGap = 0
    # A common rise lets the caret angle interpolate with the slant axis.
    info.openTypeHheaCaretSlopeRise = 1000
    info.openTypeHheaCaretSlopeRun = ttfont["hhea"].caretSlopeRun
    info.versionMajor = 1
    info.versionMinor = 310
    info.copyright = ("Copyright 2026 The Sunny Marker Project Authors "
                      "(https://github.com/buildinternet/sunny-marker-font)")
    info.openTypeNameLicense = ("This Font Software is licensed under the SIL Open "
                                "Font License, Version 1.1.")
    info.openTypeNameLicenseURL = "https://openfontlicense.org"
    info.postscriptUnderlinePosition = ttfont["post"].underlinePosition
    info.postscriptUnderlineThickness = ttfont["post"].underlineThickness
    font.lib["public.glyphOrder"] = ttfont.getGlyphOrder()
    reverse_cmap = {}
    for code, name in ttfont.getBestCmap().items():
        reverse_cmap.setdefault(name, []).append(code)
    glyph_set = ttfont.getGlyphSet()
    for name in ttfont.getGlyphOrder():
        glyph = font.newGlyph(name)
        glyph.width = ttfont["hmtx"][name][0]
        glyph.unicodes = reverse_cmap.get(name, [])
        pen = glyph.getPointPen()
        # These legacy contours were drawn in the opposite direction. Keep
        # their geometry while making their UFO winding agree with the family.
        if name in {".notdef", "braceright"}:
            pen = ReverseContourPointPen(pen)
        if outlines is not None and name in outlines:
            # Keep source precision. Going through a rounded TrueType master
            # before curve fitting turns sub-unit samples into tiny zigzags.
            for contour in outlines[name]:
                pen.beginPath()
                for x, y in contour:
                    pen.addPoint((float(x+sidebearings.get(name,(0,0))[0]), float(y)), segmentType='line')
                pen.endPath()
        else:
            glyph_set[name].drawPoints(pen)
    font.features.text = features
    target = Path(path).with_suffix(".ufo")
    target.parent.mkdir(parents=True, exist_ok=True)
    font.save(target, overwrite=True)


def export_designspace(document, target):
    doc = DesignSpaceDocument.fromstring(document.tostring())
    for source in doc.sources:
        source.path = str(Path(target).parent / Path(source.filename).with_suffix(".ufo").name)
        source.familyName = "Sunny Marker"
    for instance in doc.instances:
        instance.familyName = "Sunny Marker"
    doc.write(target)
