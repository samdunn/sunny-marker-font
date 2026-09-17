"""Build shared accent components and OpenType attachment from editable UFOs.

Run after curve fitting. Accent geometry is shared by precomposed and typed
combining sequences, with a separate compact set for capitals. Every master
receives the same components, anchors and feature structure.
"""

from copy import deepcopy
from pathlib import Path
import re

import numpy as np
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from ufoLib2 import Font
from ufoLib2.objects import Anchor, Component

from glyph_extensions import (
    LATIN,
    DOTLESS,
    COMMA_ACCENT,
    CARON_ALT,
    CCMP_FEA,
    curved_stroke,
)
from outline_geometry import FlattenPen

ROOT = Path(__file__).resolve().parents[1]
TOP = [
    "grave",
    "acute",
    "circumflex",
    "tilde",
    "macron",
    "breve",
    "dotaccent",
    "dieresis",
    "ring",
    "hungarumlaut",
    "caron",
]
BOTTOM = ["commaaccent", "cedilla", "ogonek", "macronbelow"]
ASCENDERS = {"b", "d", "f", "h", "k", "l", "t"}
EXTRA_COMPOSITES = {
    "Omacron": ("O", "macron", 0x14C),
    "omacron": ("o", "macron", 0x14D),
    "Ebreve": ("E", "breve", 0x114),
    "ebreve": ("e", "breve", 0x115),
    "Ibreve": ("I", "breve", 0x12C),
    "ibreve": ("dotlessi", "breve", 0x12D),
    "Obreve": ("O", "breve", 0x14E),
    "obreve": ("o", "breve", 0x14F),
    "Ubreve": ("U", "breve", 0x16C),
    "ubreve": ("u", "breve", 0x16D),
    "Etilde": ("E", "tilde", 0x1EBC),
    "etilde": ("e", "tilde", 0x1EBD),
    "Itilde": ("I", "tilde", 0x128),
    "itilde": ("dotlessi", "tilde", 0x129),
    "Utilde": ("U", "tilde", 0x168),
    "utilde": ("u", "tilde", 0x169),
    "Ucaron": ("U", "caron", 0x1D3),
    "ucaron": ("u", "caron", 0x1D4),
    "Acaron": ("A", "caron", 0x1CD),
    "acaron": ("a", "caron", 0x1CE),
    "Gcaron": ("G", "caron", 0x1E6),
    "gcaron": ("g", "caron", 0x1E7),
    "Kcaron": ("K", "caron", 0x1E8),
    "kcaron": ("k", "caron", 0x1E9),
    "Hcaron": ("H", "caron", 0x21E),
    "hcaron": ("h", "caron", 0x21F),
    "Scircumflex": ("S", "circumflex", 0x15C),
    "scircumflex": ("s", "circumflex", 0x15D),
    "Rcommaaccent": ("R", "commaaccent", 0x156),
    "rcommaaccent": ("r", "commaaccent", 0x157),
    "Tcedilla": ("T", "cedilla", 0x162),
    "tcedilla": ("t", "cedilla", 0x163),
}


def transform(font, source, target, matrix, unicode=None):
    old = deepcopy(font[source])
    glyph = font[target] if target in font else font.newGlyph(target)
    glyph.clearContours()
    glyph.clearComponents()
    glyph.clearAnchors()
    old.draw(TransformPen(glyph.getPen(), matrix))
    glyph.width = old.width
    if unicode is not None:
        glyph.unicodes = [unicode]
    elif source != target:
        glyph.unicodes = []
    return glyph


def anchor(glyph, name, x, y):
    glyph.anchors.append(Anchor(x=round(float(x), 3), y=round(float(y), 3), name=name))


def anchors(glyph):
    return {a.name: (a.x, a.y) for a in glyph.anchors}


def draw_ring(font, name, shear, width_factor, bottom):
    """An open ring at every weight, with nested counters and four clean arcs.

    The tiny counter cannot use the body letters' erosion amount: at Light
    Expanded that pushed it outside its enclosing contour.
    """
    glyph = font[name]
    old_bounds = glyph.getBounds(font)
    center = (old_bounds[0] + old_bounds[2]) / 2 - shear * (
        old_bounds[1] + old_bounds[3]
    ) / 2
    glyph.clearContours()
    radius = 76 + (font.info.openTypeOS2WeightClass - 400) * 0.035
    thickness = float(
        np.interp(
            font.info.openTypeOS2WeightClass, [300, 400, 500, 700], [29, 37, 41, 47]
        )
    )
    k = 0.55228475
    for r, reverse in ((radius, True), (radius - thickness, False)):
        pen = TransformPen(
            glyph.getPen(),
            Transform(
                width_factor,
                0,
                shear,
                1,
                center + shear * (bottom + radius),
                bottom + radius,
            ),
        )
        if reverse:
            pen = ReverseContourPen(pen)
        # UFO outer contours are counter-clockwise; ufo2ft reverses for TrueType.
        pen.moveTo((r, 0))
        pen.curveTo((r, -k * r), (k * r, -r), (0, -r))
        pen.curveTo((-k * r, -r), (-r, -k * r), (-r, 0))
        pen.curveTo((-r, k * r), (-k * r, r), (0, r))
        pen.curveTo((k * r, r), (r, k * r), (r, 0))
        pen.closePath()


def attach(font, name, base, mark, kind, code=None):
    glyph = font[name] if name in font else font.newGlyph(name)
    glyph.clearContours()
    glyph.clearComponents()
    glyph.clearAnchors()
    ax, ay = anchors(font[base])[kind]
    mx, my = anchors(font[mark])["_" + kind]
    glyph.components = [
        Component(base),
        Component(mark, Transform(1, 0, 0, 1, ax - mx, ay - my)),
    ]
    glyph.width = font[base].width
    if code is not None:
        glyph.unicodes = [code]
    for key, (x, y) in anchors(font[base]).items():
        if key == kind and kind in anchors(font[mark]):
            x, y = anchors(font[mark])[kind]
            x, y = x + ax - mx, y + ay - my
        anchor(glyph, key, x, y)
    return glyph


def main():
    for path in sorted((ROOT / "sources").glob("master-*.ufo")):
        font = Font.open(path)
        shear = np.tan(np.radians(-font.info.italicAngle))
        width_factor = {3: 0.75, 5: 1, 7: 1.25}[font.info.openTypeOS2WidthClass]
        math_signs = ["plus", "minus", "equal", "multiply", "divide", "less", "greater"]
        math_width = max(font[name].width for name in math_signs)
        for name in math_signs:
            glyph = font[name]
            transform(
                font,
                name,
                name,
                Transform().translate((math_width - glyph.width) / 2, 0),
            )
            glyph.width = math_width
        for ring_name, bottom in [
            ("ringcomb", 0),
            ("degree", 545),
            ("ring.spacing", 520),
        ]:
            draw_ring(font, ring_name, shear, width_factor, bottom)
        missing = font[".notdef"]
        missing.clearContours()
        p = missing.getPen()
        for corners in [
            [(65, 0), (65, 700), (435, 700), (435, 0)],
            [(120, 55), (380, 55), (380, 645), (120, 645)],
        ]:
            pts = [(x * width_factor + y * shear, y) for x, y in corners]
            p.moveTo(pts[0])
            for point in pts[1:]:
                p.lineTo(point)
            p.closePath()
        missing.width = 500 * width_factor + 700 * shear
        # A real, upright wedge for Czech/Slovak, distinct from an apostrophe.
        scale = 0.48 * width_factor
        wedge = font.newGlyph("caroncomb.alt")
        p = wedge.getPen()

        def xy(x, y):
            return (x * scale + y * shear, y)

        p.moveTo(xy(-24, 6))
        p.curveTo(xy(-47, 11), xy(-41, 28), xy(-24, 79))
        p.lineTo(xy(-9, 122))
        p.curveTo(xy(-3, 142), xy(42, 140), xy(41, 118))
        p.curveTo(xy(39, 94), xy(-6, 24), xy(-24, 6))
        p.closePath()
        # Missing macron below is drawn from the same nib as the top macron.
        transform(font, "macroncomb", "macronbelowcomb", Transform(), 0x331)
        # Spacing modifier letters have their own positive advance.
        transform(font, "quoteright", "apostrophemod", Transform(), 0x2BC)
        transform(font, "quoteleft", "turnedcomma", Transform(), 0x2BB)
        for name, code in [("lineSeparator", 0x2028), ("paragraphSeparator", 0x2029)]:
            glyph = font.newGlyph(name)
            glyph.unicodes = [code]
            glyph.width = 0
        # The black heart and the outlined heart are distinct Unicode symbols.
        transform(font, "heart", "heartblack", Transform(), 0x2764)
        font["heart"].unicodes = [0x2661]

        def area(contour):
            pen = AreaPen(None)
            contour.draw(pen)
            return abs(pen.value)

        largest = max(font["heartblack"].contours, key=area)
        font["heartblack"].contours = [deepcopy(largest)]
        # Eng is a letter, not an n with a generic mark. Use a continuous n
        # shoulder into a right-hand descender, matched to the existing nib.
        weight = font.info.openTypeOS2WeightClass
        nib = float(np.interp(weight, [300, 400, 500, 700], [88, 102, 112, 127]))
        xh = font.info.xHeight
        for name, code, cap in [("eng", 0x14B, False), ("Eng", 0x14A, True)]:
            glyph = font.newGlyph(name)
            glyph.unicodes = [code]
            height = 700 if cap else xh
            stem = height - nib / 2
            segments = (
                [
                    ("move", (0, 0)),
                    ("line", (0, stem)),
                    ("line", (295, 50)),
                    ("line", (295, stem)),
                ]
                if cap
                else [
                    ("move", (0, 0)),
                    ("line", (0, stem)),
                    ("curve", (130, stem + 30), (295, stem + 30), (295, stem - 140)),
                ]
            )
            if cap:
                # The N diagonal and right stem meet with a rounded marker join.
                segments += [("line", (295, -90))]
            else:
                segments += [("line", (295, -90))]
            segments += [("curve", (295, -185), (220, -220), (140, -170))]
            pen = TransformPen(
                glyph.getPen(),
                Transform(width_factor, 0, shear, 1, 70 * width_factor, 0),
            )
            if not cap:
                # Draw the two sides explicitly: boolean stroking can change
                # segmentation as x-height changes, which a VF cannot accept.
                r = nib / 2
                pen.moveTo((-r, 0))
                pen.lineTo((-r, xh - r))
                pen.curveTo((-r, xh + 12), (r, xh + 12), (r, xh - r))
                pen.lineTo((r, xh - 70))
                pen.curveTo((130, xh + 60), (295 + r, xh + 40), (295 + r, xh - 150))
                pen.lineTo((295 + r, -90))
                pen.curveTo((295 + r, -240), (170, -270), (100, -180))
                pen.curveTo((80, -150), (150, -110), (175, -140))
                pen.curveTo((220, -180), (295 - r, -140), (295 - r, -90))
                pen.lineTo((295 - r, xh - 150))
                pen.curveTo((295 - r, xh - 50), (120, xh - 50), (r, xh - 155))
                pen.lineTo((r, 0))
                pen.curveTo((r, -r), (-r, -r), (-r, 0))
                pen.closePath()
                glyph.width = 440 * width_factor
                continue
            contours = curved_stroke(segments, nib)
            for contour in contours:
                pen.moveTo(contour[0][1])
                for segment in contour[1:]:
                    if segment[0] == "line":
                        pen.lineTo(segment[1])
                    else:
                        pen.curveTo(*segment[1:])
                pen.closePath()
            glyph.width = 440 * width_factor
        # A dotted circle gives unattached combining marks a readable base.
        dotted = font.newGlyph("dottedCircle")
        dotted.unicodes = [0x25CC]
        dotbox = font["period"].getBounds(font)
        dotcx, dotcy = (dotbox[0] + dotbox[2]) / 2, (dotbox[1] + dotbox[3]) / 2
        radius = 178
        for t in np.linspace(0, 2 * np.pi, 12, endpoint=False):
            x, y = (250 + radius * np.cos(t)) * width_factor, 225 + radius * np.sin(t)
            matrix = Transform(
                0.36, 0, 0, 0.36, x + y * shear - 0.36 * dotcx, y - 0.36 * dotcy
            )
            font["period"].draw(TransformPen(dotted.getPen(), matrix))
        dotted.width = 500 * width_factor
        marks = TOP + BOTTOM
        # Normalize mark origins; above marks attach at their bottom ink edge,
        # below marks at their top edge. Retain the original slant in the ink.
        for name in marks:
            glyph = font[name + "comb"]
            b = glyph.getBounds(font)
            center = (b[0] + b[2]) / 2 - shear * (b[1] + b[3]) / 2
            y = b[1] if name in TOP else b[3]
            transform(
                font,
                name + "comb",
                name + "comb",
                Transform(1, 0, 0, 1, -center - shear * y, -y),
            )
            glyph.width = 0
            kind = (
                "top"
                if name in TOP
                else name if name in ("cedilla", "ogonek") else "bottom"
            )
            anchor(glyph, "_" + kind, 0, 0)
            b = glyph.getBounds(font)
            nexty = b[3] + 24 if name in TOP else b[1] - 24
            anchor(glyph, kind, shear * nexty, nexty)
            if name in TOP:
                case = transform(
                    font,
                    name + "comb",
                    name + "comb.case",
                    Transform().scale(0.75, 0.75),
                )
                case.width = 0
                anchor(case, "_top", 0, 0)
                nexty = case.getBounds(font)[3] + 22
                anchor(case, "top", shear * nexty, nexty)
        anchor(wedge, "_side", 0, 125)
        # Turned comma above (Latvian g), from the same comma-below drawing.
        gmark = transform(
            font,
            "commaaccentcomb",
            "commaaccentcomb.turn",
            Transform(-1, 0, 0, -1, 0, 0),
        )
        gmark.width = 0
        anchor(gmark, "_top", 0, 0)
        anchor(gmark, "top", 0, gmark.getBounds(font)[3] + 24)
        # Existing composited glyphs are replaced below. Work from genuine base
        # ink now, avoiding control handles and the detached dot of i/j.
        nonbases = (
            {x + "comb" for x in marks}
            | {x + "comb.case" for x in TOP}
            | {"caroncomb.alt", "commaaccentcomb.turn"}
        )
        for glyph in font:
            if glyph.name in nonbases or not glyph.contours:
                continue
            b = glyph.getBounds(font)
            glyph.clearAnchors()
            pen = FlattenPen(font)
            glyph.draw(pen)
            points = np.concatenate(pen.contours)
            band = points[points[:, 1] >= b[3] - (b[3] - b[1]) * 0.20]
            center = np.median(band[:, 0] - shear * band[:, 1])
            cap = glyph.name[0].isupper()
            y = b[3] + (26 if cap else 34)
            anchor(glyph, "top", center + shear * y, y)
            low = points[points[:, 1] <= b[1] + (b[3] - b[1]) * 0.20]
            cx = np.median(low[:, 0] - shear * low[:, 1])
            anchor(glyph, "bottom", cx + shear * (b[1] - 30), b[1] - 30)
            anchor(glyph, "cedilla", cx + shear * (b[1] + 12), b[1] + 12)
            rx = np.percentile(low[:, 0] - shear * low[:, 1], 85)
            anchor(glyph, "ogonek", rx + shear * (b[1] + 16), b[1] + 16)
            anchor(glyph, "side", b[2] + 22 * width_factor, b[3])
        recipes = {name: (base, mark) for name, (base, mark, pos) in LATIN.items()}
        recipes.update(DOTLESS)
        recipes.update(
            {name: (base, "commaaccent") for name, (base, pos) in COMMA_ACCENT.items()}
        )
        recipes.update({name: (base, "caron") for name, base in CARON_ALT.items()})
        recipes.update(
            {
                "jacute": ("dotlessj", "acute"),
                "Jacute": ("J", "acute"),
                "iogonek.dotless": ("dotlessi", "ogonek"),
            }
        )
        recipes.update({n: (b, m) for n, (b, m, c) in EXTRA_COMPOSITES.items()})
        for name, (base, mark) in recipes.items():
            cap = base[0].isupper() or base in ASCENDERS
            kind = (
                "top"
                if mark in TOP
                else mark if mark in ("ogonek", "cedilla") else "bottom"
            )
            mname = mark + "comb" + (".case" if cap and kind == "top" else "")
            if name in CARON_ALT:
                mname, kind = "caroncomb.alt", "side"
            if name == "gcommaaccent":
                mname, kind = "commaaccentcomb.turn", "top"
            code = EXTRA_COMPOSITES[name][2] if name in EXTRA_COMPOSITES else None
            attach(font, name, base, mname, kind, code)
        # Reuse the base's sidebearings and pair adjustments for accented forms.
        groups = {}
        for name, (base, mark) in recipes.items():
            if name in CARON_ALT:
                continue
            base = {"dotlessi": "i", "dotlessj": "j"}.get(base, base)
            groups.setdefault(base, [base]).append(name)
        features = font.features.text.replace(CCMP_FEA, "")

        # Expand kern operands only, never the alternate-substitution features.
        def expand(match):
            left, right, value = match.groups()
            operand = lambda n: (
                "[" + " ".join("\\" + g for g in groups[n]) + "]"
                if n in groups
                else "\\" + n
            )
            return "pos " + operand(left) + " " + operand(right) + " " + value + ";"

        features = re.sub(r"pos \\(\w+) \\(\w+) (-?\d+);", expand, features)
        topnames = " ".join(n + "comb" for n in TOP)
        case_bases = ASCENDERS | {
            n for n, (base, mark) in recipes.items() if base in ASCENDERS
        }
        upper = " ".join(
            g.name
            for g in font
            if g.name not in nonbases
            and (
                any(chr(c).isupper() for c in g.unicodes)
                or g.name == "Jacute"
                or g.name in case_bases
            )
        )
        feature = f"""@TopMarks = [{topnames}];
@CaseMarks = [{' '.join(n+'comb.case' for n in TOP)}];
@Uppercase = [{upper}];
feature ccmp {{
  sub j acutecomb by jacute;
  sub J acutecomb by Jacute;
  lookup soft_dotted {{
    lookupflag UseMarkFilteringSet @TopMarks;
    sub [i j iogonek]' @TopMarks by [dotlessi dotlessj iogonek.dotless];
  }} soft_dotted;
  sub [L d l t] caroncomb' by caroncomb.alt;
  sub g commaaccentcomb' by commaaccentcomb.turn;
  lookup case_marks {{
    lookupflag UseMarkFilteringSet @TopMarks;
    sub @Uppercase @TopMarks' by @CaseMarks;
  }} case_marks;
}} ccmp;
"""
        pos = features.index("feature salt")
        font.features.text = features[:pos] + feature + features[pos:]
        # Explicit classes prevent precomposed letters being inferred as marks
        # merely because they contain a mark component.
        font.lib["public.openTypeCategories"] = {
            g.name: "mark" if g.name in nonbases else "base" for g in font
        }
        order = font.lib["public.glyphOrder"]
        font.lib["public.glyphOrder"] = order + sorted(set(font.keys()) - set(order))
        # UFO serialization expects Python numbers, not numpy scalar reprs.
        for name in (".notdef", "eng", "caroncomb.alt"):
            glyph = font[name]
            old = deepcopy(glyph)
            glyph.clearContours()
            old.draw(ReverseContourPen(glyph.getPen()))
        for glyph in font:
            glyph.width = float(glyph.width)
            for contour in glyph.contours:
                for point in contour.points:
                    point.x, point.y = float(point.x), float(point.y)
            for component in glyph.components:
                component.transformation = Transform(
                    *(float(v) for v in component.transformation)
                )
        font.save(path, overwrite=True)
        print(path.name, len(font), flush=True)


if __name__ == "__main__":
    main()
