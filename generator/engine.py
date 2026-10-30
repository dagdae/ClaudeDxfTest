"""
AV rack executive wiring - DXF drawing engine.

Graphic conventions follow the Videlio HMS "21xRWxx" wiring diagrams:
- equipment drawn as blue boxes (brand/model above, function + tag below)
- every physical connector drawn outside the box with type, gender and pins
- multi-conductor cables fan out at both ends with sheath oval and conductor ids
- internal cables identified by a pill label  FROM.DEV-OUT/TO.DEV-IN
- field cables identified by ship cable number (K/MLxxxxx), type and length
- off-sheet continuations drawn as diamonds with the target sheet number
- rack limit drawn as magenta dash-dot line

All coordinates are paper millimetres (model space 1:1 = plotted sheet).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import ezdxf
from ezdxf.enums import TextEntityAlignment
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath

FONT_FILE = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
_FP = FontProperties(fname=FONT_FILE)
_W_CACHE: dict[str, float] = {}

PIN = 3.0       # pin / terminal pitch
STUB = 6.0      # conductor stub length at a fan-out
SINGLE_H = 5.0  # height reserved for a single connector

ALIGN = {
    "BL": TextEntityAlignment.BOTTOM_LEFT, "BC": TextEntityAlignment.BOTTOM_CENTER,
    "BR": TextEntityAlignment.BOTTOM_RIGHT, "ML": TextEntityAlignment.MIDDLE_LEFT,
    "MC": TextEntityAlignment.MIDDLE_CENTER, "MR": TextEntityAlignment.MIDDLE_RIGHT,
    "TL": TextEntityAlignment.TOP_LEFT, "TC": TextEntityAlignment.TOP_CENTER,
    "TR": TextEntityAlignment.TOP_RIGHT,
}

# layer: (rgb or None for ACI7, linetype, lineweight 1/100 mm)
LAYERS = {
    "AV-FRAME":      ((120, 0, 255), "Continuous", 70),
    "AV-TITLE":      ((120, 0, 255), "Continuous", 25),
    "AV-ZONE":       ((120, 0, 255), "Continuous", 18),
    "AV-RACK":       ((255, 0, 255), "AV_DASHDOT", 50),
    "AV-FIELDBOX":   (None, "Continuous", 35),
    "AV-DEVICE":     ((70, 130, 255), "Continuous", 25),
    "AV-DEVICE-REF": ((70, 130, 255), "AV_HIDDEN", 25),
    "AV-CONN":       (None, "Continuous", 18),
    "AV-TEXT":       (None, "Continuous", 18),
    "AV-TEXT-DEV":   (None, "Continuous", 18),
    "AV-LABEL":      (None, "Continuous", 18),
    "AV-NOTE":       (None, "Continuous", 18),
    "AV-XREF":       ((0, 175, 0), "Continuous", 18),
    "AV-TB":         (None, "Continuous", 18),
    "AV-SYM":        ((70, 130, 255), "Continuous", 25),
    "W-AUDIO":       (None, "Continuous", 25),
    "W-SPEAKER":     ((0, 160, 160), "Continuous", 35),
    "W-RF":          ((0, 0, 255), "Continuous", 25),
    "W-QLAN":        ((110, 190, 0), "AV_DASHED", 25),
    "W-DANTE":       ((230, 0, 0), "AV_DASHED", 25),
    "W-LESNET":      ((0, 160, 235), "AV_DASHED", 25),
    "W-UPLINK":      ((31, 56, 140), "AV_DASHED", 25),
    "W-FIBER":       ((31, 56, 140), "Continuous", 25),
    "W-GPIO":        ((150, 75, 0), "Continuous", 25),
    "W-24VDC":       ((200, 0, 60), "Continuous", 25),
    "W-POWER":       ((235, 140, 0), "Continuous", 35),
    "W-PE":          ((0, 150, 0), "Continuous", 25),
}

WIRE_RGB = {k: v[0] for k, v in LAYERS.items()}


def text_width(s: str, h: float) -> float:
    """Approximate drawn width of an Arial/Liberation string with cap height h."""
    if not s:
        return 0.0
    key = s
    if key not in _W_CACHE:
        tp = TextPath((0, 0), s.replace(" ", " "), size=1.0, prop=_FP)
        ext = tp.get_extents()
        _W_CACHE[key] = ext.x1 if ext.x1 > 0 else len(s) * 0.6
    return _W_CACHE[key] * h / 0.716


@dataclass
class Pin:
    """Wire attachment point. d=+1 wire leaves to the right, -1 to the left,
    +2 upward, -2 downward."""
    x: float
    y: float
    d: int
    name: str = ""


@dataclass
class Port:
    dev: str
    pid: str
    label: str
    pins: list[Pin]
    conn: str | None = None
    y: float = 0.0

    @property
    def p(self) -> Pin:  # single anchor
        return self.pins[0]

    def __getitem__(self, i):
        return self.pins[i]


@dataclass
class CableRecord:
    label: str
    cable_no: str
    ctype: str
    from_dev: str
    from_port: str
    from_conn: str
    to_dev: str
    to_port: str
    to_conn: str
    cores: str
    length: str
    sheet: str
    signal: str
    note: str = ""


class Sheet:
    def __init__(self, code: str, sheet_no: str, title: str, fmt=(841.0, 594.0)):
        self.code = code
        self.sheet_no = sheet_no
        self.title = title
        self.W, self.H = fmt
        self.doc = ezdxf.new("R2013", units=4)
        self.doc.header["$MEASUREMENT"] = 1
        self.doc.header["$LTSCALE"] = 1.0
        self.doc.header["$PSLTSCALE"] = 0
        self.doc.header["$LWDISPLAY"] = 1
        self._setup()
        self.msp = self.doc.modelspace()
        self.records: list[CableRecord] = []

    # ------------------------------------------------------------------ setup
    def _setup(self):
        lt = self.doc.linetypes
        lt.add("AV_DASHED", pattern=[8.0, 5.5, -2.5], description="AV dashed __  __  __")
        lt.add("AV_DASHDOT", pattern=[12.0, 8.0, -2.0, 0.0, -2.0], description="AV dash-dot __ . __ .")
        lt.add("AV_HIDDEN", pattern=[3.0, 2.0, -1.0], description="AV short dash - - -")
        self.doc.styles.add("AV", font="arial.ttf")
        for name, (rgb, ltype, lw) in LAYERS.items():
            if rgb is None:
                self.doc.layers.add(name, color=7, linetype=ltype, lineweight=lw)
            else:
                self.doc.layers.add(name, color=7, true_color=ezdxf.rgb2int(rgb),
                                    linetype=ltype, lineweight=lw)

    # -------------------------------------------------------------- primitives
    def _attr(self, layer, rgb=None, lw=None, ltype=None):
        a = {"layer": layer}
        if rgb is not None:
            a["true_color"] = ezdxf.rgb2int(rgb)
        if lw is not None:
            a["lineweight"] = lw
        if ltype is not None:
            a["linetype"] = ltype
        return a

    def line(self, p1, p2, layer="AV-CONN", **kw):
        self.msp.add_line(p1, p2, dxfattribs=self._attr(layer, **kw))

    def pline(self, pts, layer="AV-CONN", closed=False, **kw):
        pts = [tuple(p[:2]) for p in pts]
        # drop consecutive duplicates
        clean = [pts[0]]
        for p in pts[1:]:
            if abs(p[0] - clean[-1][0]) > 1e-6 or abs(p[1] - clean[-1][1]) > 1e-6:
                clean.append(p)
        if len(clean) < 2:
            return
        self.msp.add_lwpolyline(clean, close=closed, dxfattribs=self._attr(layer, **kw))

    def rect(self, x, y, w, h, layer="AV-DEVICE", **kw):
        self.pline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], layer, closed=True, **kw)

    def text(self, s, x, y, h=2.0, align="ML", layer="AV-TEXT", rot=0.0, rgb=None):
        if s is None or s == "":
            return
        t = self.msp.add_text(str(s), height=h, rotation=rot,
                              dxfattribs=dict(self._attr(layer, rgb=rgb), style="AV", width=1.0))
        t.set_placement((x, y), align=ALIGN[align])

    def mtext_lines(self, lines, x, y, h=2.0, align="TL", gap=1.55, layer="AV-TEXT", rgb=None):
        """Stack of single-line texts, first line at y (top)."""
        step = h * gap
        va = align[0]
        n = len(lines)
        if va == "T":
            y0 = y - h / 2
        elif va == "B":
            y0 = y + (n - 1) * step + h / 2
        else:
            y0 = y + (n - 1) * step / 2
        for i, s in enumerate(lines):
            self.text(s, x, y0 - i * step, h, "M" + align[1], layer, rgb=rgb)

    def circle(self, c, r, layer="AV-CONN", **kw):
        self.msp.add_circle(c, r, dxfattribs=self._attr(layer, **kw))

    def arc(self, c, r, a0, a1, layer="AV-CONN", **kw):
        self.msp.add_arc(c, r, a0, a1, dxfattribs=self._attr(layer, **kw))

    def ellipse(self, c, rx, ry, layer="AV-CONN", **kw):
        if rx >= ry:
            self.msp.add_ellipse(c, major_axis=(rx, 0), ratio=ry / rx, dxfattribs=self._attr(layer, **kw))
        else:
            self.msp.add_ellipse(c, major_axis=(0, ry), ratio=rx / ry, dxfattribs=self._attr(layer, **kw))

    def dot(self, c, r=0.45, layer="AV-CONN", **kw):
        x, y = c
        pl = self.msp.add_lwpolyline([(x - r / 2, y, 0, 0, 1), (x + r / 2, y, 0, 0, 1)],
                                     format="xyseb", close=True, dxfattribs=self._attr(layer, **kw))
        pl.dxf.const_width = r

    def solid_rect(self, x, y, w, h, layer, rgb=None):
        hatch = self.msp.add_hatch(dxfattribs=self._attr(layer, rgb=rgb))
        hatch.set_solid_fill(color=7 if rgb is None else 256, rgb=rgb)
        hatch.paths.add_polyline_path([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], is_closed=True)

    def hatch_rect(self, x, y, w, h, layer, rgb=None, pattern="ANSI31", scale=0.35):
        hatch = self.msp.add_hatch(dxfattribs=self._attr(layer, rgb=rgb))
        hatch.set_pattern_fill(pattern, scale=scale)
        hatch.paths.add_polyline_path([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], is_closed=True)

    # ---------------------------------------------------------- annotations
    def pill(self, cx, cy, s, h=1.7, layer="AV-LABEL"):
        w = text_width(s, h) + 4.0
        r = 1.9
        x0, x1 = cx - w / 2, cx + w / 2
        self.msp.add_lwpolyline(
            [(x0 + r, cy - r, 0, 0, 0), (x1 - r, cy - r, 0, 0, 1),
             (x1 - r, cy + r, 0, 0, 0), (x0 + r, cy + r, 0, 0, 1)],
            format="xyseb", close=True, dxfattribs=self._attr(layer))
        self.text(s, cx, cy, h, "MC", layer)
        return w

    @staticmethod
    def pill_w(s, h=1.7):
        return text_width(s, h) + 4.0

    def xref(self, pin: Pin, sheet: str, lines, layer="AV-XREF", lead=4.0, wire_layer=None):
        """Off-sheet continuation: short lead from pin, diamond with target sheet."""
        d = 1 if pin.d in (1, 2) else -1
        horiz = pin.d in (1, -1)
        s = 3.2
        if horiz:
            x0 = pin.x + d * lead
            if wire_layer:
                self.line((pin.x, pin.y), (x0, pin.y), wire_layer)
            cx = x0 + d * s
            cy = pin.y
            pts = [(cx - s, cy), (cx, cy + s), (cx + s, cy), (cx, cy - s)]
            self.pline(pts, layer, closed=True)
            # chevron
            k = 1.3
            self.pline([(cx + d * k, cy + s), (cx + d * (s + k), cy), (cx + d * k, cy - s)], layer)
            self.text(sheet, cx, cy, 1.7, "MC", "AV-TEXT")
            tx = cx + d * (s + k + 1.8)
            self.mtext_lines(lines, tx, cy, 1.7, "ML" if d > 0 else "MR")
            return (tx, cy)
        else:
            y0 = pin.y + d * lead
            if wire_layer:
                self.line((pin.x, pin.y), (pin.x, y0), wire_layer)
            cx, cy = pin.x, y0 + d * s
            self.pline([(cx - s, cy), (cx, cy + s), (cx + s, cy), (cx, cy - s)], layer, closed=True)
            k = 1.3
            self.pline([(cx - s, cy + d * k), (cx, cy + d * (s + k)), (cx + s, cy + d * k)], layer)
            self.text(sheet, cx, cy, 1.7, "MC", "AV-TEXT")
            self.mtext_lines(lines, cx + s + 1.5, cy + d * 0.0, 1.7, "ML")
            return (cx, cy)

    def nc(self, pin: Pin, layer="AV-CONN"):
        """Not-connected marker: short stub with a cross."""
        d = pin.d
        if d in (1, -1):
            x1 = pin.x + d * 2.5
            self.line((pin.x, pin.y), (x1, pin.y), layer)
            self.line((x1 - 0.7, pin.y - 0.7), (x1 + 0.7, pin.y + 0.7), layer)
            self.line((x1 - 0.7, pin.y + 0.7), (x1 + 0.7, pin.y - 0.7), layer)
        else:
            s = 1 if d == 2 else -1
            y1 = pin.y + s * 2.5
            self.line((pin.x, pin.y), (pin.x, y1), layer)
            self.line((pin.x - 0.7, y1 - 0.7), (pin.x + 0.7, y1 + 0.7), layer)
            self.line((pin.x - 0.7, y1 + 0.7), (pin.x + 0.7, y1 - 0.7), layer)

    def ground(self, x, y, layer="W-PE", down=True):
        s = -1 if down else 1
        self.line((x, y), (x, y + s * 1.6), layer)
        for i, w in enumerate((1.8, 1.2, 0.6)):
            yy = y + s * (1.6 + i * 0.6)
            self.line((x - w, yy), (x + w, yy), layer)

    # ------------------------------------------------------------- connectors
    def connector(self, xe, yc, side, ctype, gender="M", pins=None, layer="AV-CONN"):
        """Draw a cable-side connector at device edge xe (side 'L'/'R'/'B'/'T').
        Returns list[Pin] (wire attachment points)."""
        if side in ("L", "R"):
            d = 1 if side == "R" else -1
            if pins:
                n = len(pins)
                h = n * PIN
                ytop = yc + h / 2
                x_type0 = xe + d * 1.2
                x_type1 = xe + d * 5.2
                x_pin1 = xe + d * 10.2
                self.line((xe, yc), (x_type0, yc), layer)
                xa, xb = sorted((x_type0, x_type1))
                self.rect(xa, ytop - h, xb - xa, h, layer)
                lbl = f"{ctype} {gender}".strip()
                self.text(lbl, (xa + xb) / 2, yc, 1.05 if h > 8 else 0.95, "MC", layer, rot=90)
                xa2, xb2 = sorted((x_type1, x_pin1))
                out = []
                for i, pn in enumerate(pins):
                    y0 = ytop - (i + 1) * PIN
                    self.rect(xa2, y0, xb2 - xa2, PIN, layer)
                    self.text(pn, (xa2 + xb2) / 2, y0 + PIN / 2, 1.15, "MC", layer)
                    out.append(Pin(x_pin1, y0 + PIN / 2, d, pn))
                return out
            else:
                x0 = xe + d * 1.2
                x1 = xe + d * 10.2
                self.line((xe, yc), (x0, yc), layer)
                xa, xb = sorted((x0, x1))
                self.rect(xa, yc - 2.2, xb - xa, 4.4, layer)
                self.text(ctype, (xa + xb) / 2, yc + 0.95, 1.05, "MC", layer)
                self.text(gender, (xa + xb) / 2, yc - 1.05, 1.05, "MC", layer)
                return [Pin(x1, yc, d, ctype)]
        else:
            d = 2 if side == "T" else -2
            s = 1 if side == "T" else -1
            y0 = yc + s * 1.2
            y1 = yc + s * 6.2
            self.line((xe, yc), (xe, y0), layer)
            ya, yb = sorted((y0, y1))
            self.rect(xe - 5.0, ya, 10.0, yb - ya, layer)
            self.text(ctype, xe, (ya + yb) / 2 + 0.95, 1.05, "MC", layer)
            self.text(gender, xe, (ya + yb) / 2 - 1.05, 1.05, "MC", layer)
            return [Pin(xe, y1, d, ctype)]

    # ------------------------------------------------------------------ icons
    def icon(self, kind, x, y, w=12.0, h=9.0, layer="AV-SYM"):
        """x,y = top-left of icon cell (inside device)."""
        self.rect(x, y - h, w, h, "AV-DEVICE")
        cx, cy = x + w / 2, y - h / 2
        if kind == "amp":
            self.pline([(cx - 2.5, cy + 3), (cx + 3, cy), (cx - 2.5, cy - 3)], layer, closed=True)
        elif kind == "net":
            self.line((cx - 3, cy), (cx, cy), layer)
            self.line((cx, cy + 2.8), (cx, cy - 2.8), layer)
            for yy in (cy + 2.8, cy, cy - 2.8):
                self.line((cx, yy), (cx + 2.5, yy), layer)
                self.dot((cx + 2.5, yy), 0.7, layer)
            self.dot((cx - 3, cy), 0.7, layer)
        elif kind == "dsp":
            self.line((cx - 3.5, cy + 1.2), (cx + 3.5, cy + 1.2), layer)
            self.pline([(cx + 2.3, cy + 2.0), (cx + 3.5, cy + 1.2), (cx + 2.3, cy + 0.4)], layer)
            self.line((cx - 3.5, cy - 1.2), (cx + 3.5, cy - 1.2), layer)
            self.pline([(cx - 2.3, cy - 0.4), (cx - 3.5, cy - 1.2), (cx - 2.3, cy - 2.0)], layer)
        elif kind == "ups":
            self.rect(cx - 3, cy - 2.6, 6, 4.4, layer)
            self.rect(cx - 2.2, cy + 1.8, 1.2, 0.8, layer)
            self.rect(cx + 1.0, cy + 1.8, 1.2, 0.8, layer)
            self.text("+  -", cx, cy + 3.6, 1.2, "MC", layer)
        elif kind == "antenna":
            self.line((cx, cy - 3.2), (cx, cy + 3.2), layer)
            self.line((cx, cy - 1), (cx - 2.5, cy + 3.2), layer)
            self.line((cx, cy - 1), (cx + 2.5, cy + 3.2), layer)
        elif kind == "speaker":
            self.rect(cx - 3.2, cy - 1.4, 2.0, 2.8, layer)
            self.pline([(cx - 1.2, cy + 1.4), (cx + 1.8, cy + 3.2), (cx + 1.8, cy - 3.2), (cx - 1.2, cy - 1.4)], layer)
        elif kind == "touch":
            self.rect(cx - 3.8, cy - 2.6, 7.6, 5.2, layer)
            self.rect(cx - 3.0, cy - 1.8, 6.0, 3.6, layer)
        elif kind == "switch":
            self.line((cx - 3.5, cy), (cx - 1.0, cy), layer)
            self.line((cx - 1.0, cy), (cx + 2.2, cy + 1.8), layer)
            self.line((cx + 1.8, cy), (cx + 3.5, cy), layer)
        elif kind == "fiber":
            self.circle((cx, cy), 2.6, layer)
            self.circle((cx, cy), 0.9, layer)
        elif kind == "psu":
            self.line((cx - 3.5, cy - 3.0), (cx + 3.5, cy + 3.0), layer)
            self.text("~", cx - 1.8, cy - 1.0, 1.8, "MC", layer)
            self.text("=", cx + 1.8, cy + 1.2, 1.8, "MC", layer)
        elif kind == "panel":
            for i in range(3):
                self.rect(cx - 3.6 + i * 2.6, cy - 1.2, 2.0, 2.4, layer)
        elif kind == "mmb":
            self.text("MA", cx, cy, 3.0, "MC", layer)

    # ----------------------------------------------------------------- device
    def device(self, x, ytop, w, brand, model, func, tag, left=(), right=(),
               icon=None, partial=False, header=12.0, pad=4.0, min_h=0.0,
               bottom=None, title_h=2.2, tag_lines=None, note=None, spacing=2.0):
        """Draw a device box. Port spec: dict(id, label, conn=None, g='M', pins=None,
        gap=0.0). Returns dict id -> Port."""
        lay = "AV-DEVICE-REF" if partial else "AV-DEVICE"
        ports: dict[str, Port] = {}

        def col_h(specs):
            t = 0.0
            for i, sp in enumerate(specs):
                ph = len(sp["pins"]) * PIN if sp.get("pins") else SINGLE_H
                t += sp.get("gap", 0.0) + ph + (spacing if i else 0.0)
            return t

        body = max(col_h(left), col_h(right), min_h)
        bot_h = 7.0 if bottom else 0.0
        h = header + pad + body + pad + bot_h
        ybot = ytop - h
        self.rect(x, ybot, w, h, lay)
        # header line + icon
        if icon:
            self.icon(icon, x, ytop, 12.0, min(header, 10.0))
        # titles
        self.mtext_lines([brand, model], x + w / 2, ytop + 1.4, title_h, "BC", gap=1.45, layer="AV-TEXT-DEV")
        tl = tag_lines if tag_lines else [func, tag]
        tx = x + w / 2 if not (bottom and bottom.get("conn") and w >= 40) else x + (w - 14.0) / 2
        self.mtext_lines(tl, tx, ybot - 1.3, title_h, "TC", gap=1.45, layer="AV-TEXT-DEV")
        if note:
            nx = x + 12.0 + (w - 12.0) / 2 if icon else x + w / 2
            self.text(note, nx, ytop - min(header, 10.0) / 2, 1.35, "MC", "AV-TEXT")

        def place(specs, side):
            yy = ytop - header - pad
            first = True
            for sp in specs:
                pins = sp.get("pins")
                ph = len(pins) * PIN if pins else SINGLE_H
                yy -= sp.get("gap", 0.0) + (0.0 if first else spacing)
                first = False
                yc = yy - ph / 2
                xe = x if side == "L" else x + w
                lbl = sp.get("label", sp["id"])
                if side == "L":
                    self.text(lbl, x + 1.6, yc, 1.45, "ML", "AV-TEXT")
                else:
                    self.text(lbl, x + w - 1.6, yc, 1.45, "MR", "AV-TEXT")
                conn = sp.get("conn")
                if conn:
                    pl = self.connector(xe, yc, side, conn, sp.get("g", "M"), pins)
                else:
                    d = -1 if side == "L" else 1
                    if pins:
                        pl = [Pin(xe, yc + (len(pins) - 1) * PIN / 2 - i * PIN, d, pn) for i, pn in enumerate(pins)]
                    else:
                        pl = [Pin(xe, yc, d, lbl)]
                    self.line((xe, yc), (xe + d * 2.0, yc), "AV-DEVICE")
                ports[sp["id"]] = Port(tag, sp["id"], lbl, pl, conn, yc)
                yy -= ph

        place(left, "L")
        place(right, "R")
        if bottom:
            bw = max(14.0, text_width(bottom.get("label", ""), 1.4) + 3)
            bxc = x + w - 7.0 if w >= 40 else x + w / 2
            self.rect(bxc - bw / 2, ybot, bw, 4.5, lay)
            self.text(bottom.get("label", ""), bxc, ybot + 2.25, 1.4, "MC", "AV-TEXT")
            bx = x + w - 7.0 if w >= 40 else x + w / 2
            if bottom.get("conn"):
                pl = self.connector(bx, ybot, "B", bottom["conn"], bottom.get("g", "F"))
            else:
                pl = [Pin(bx, ybot, -2, "PWR")]
            ports[bottom.get("id", "PWR")] = Port(tag, bottom.get("id", "PWR"), bottom.get("label", ""), pl,
                                                  bottom.get("conn"), ybot)
        ports["_box"] = Port(tag, "_box", "", [Pin(x, ybot, 0), Pin(x + w, ytop, 0)])
        return ports

    # --------------------------------------------------------- terminal block
    def knife(self, x, yc, layer="AV-TB"):
        """Disconnect (knife) symbol inside a terminal cell starting at x."""
        self.circle((x + 1.0, yc), 0.35, layer)
        self.circle((x + 4.0, yc), 0.35, layer)
        self.line((x + 1.3, yc + 0.15), (x + 3.6, yc + 1.15), layer)

    def terminal_block(self, x, ytop, name, terms, w=15.0, title_side="T", sec="2.5"):
        """terms: list of dict(id, sec=None, pe=False, disc=False, levels=1, gap=0, note=None,
        notes=None, note_side='R').
        Returns id -> (Pin left, Pin right) for 1-level terminals, or
        id -> [(Pin left, Pin right), ...] (top level first) for multi-level terminals."""
        res = {}
        y = ytop
        if name and title_side == "T":
            self.text(name, x + w / 2, ytop + 1.6, 2.6, "BC", "AV-TEXT-DEV")
        for t in terms:
            y -= t.get("gap", 0.0)
            n = t.get("levels", 1)
            hh = n * PIN
            y0 = y - hh
            pe = t.get("pe", False)
            self.rect(x, y0, w, hh, "AV-TB")
            self.line((x + 5.0, y0), (x + 5.0, y), "AV-TB")
            if pe:
                self.hatch_rect(x + 5.0, y0, w - 5.0, hh, "AV-TB", rgb=(0, 150, 0), pattern="ANSI31", scale=0.25)
            levels = []
            notes = t.get("notes") or ([t.get("note")] if t.get("note") else [])
            side = t.get("note_side", "R")
            for k in range(n):
                yc = y - PIN * (k + 0.5)
                if k > 0:
                    self.line((x, y - PIN * k), (x + 5.0, y - PIN * k), "AV-TB")
                    self.line((x + 5.0, y - PIN * k), (x + 6.2, y - PIN * k), "AV-TB")
                    self.line((x + w - 1.2, y - PIN * k), (x + w, y - PIN * k), "AV-TB")
                if t.get("disc"):
                    self.knife(x, yc)
                elif n > 1:
                    self.text(str(k + 1), x + 2.5, yc, 1.0, "MC", "AV-TB")
                else:
                    self.text(t.get("sec", sec), x + 2.5, yc, 1.0, "MC", "AV-TB")
                self.dot((x - 0.8, yc), 0.55, "AV-TB")
                self.dot((x + w + 0.8, yc), 0.55, "AV-TB")
                self.line((x - 0.8, yc), (x - 2.0, yc), "AV-TB")
                self.line((x + w + 0.8, yc), (x + w + 2.0, yc), "AV-TB")
                if k < len(notes) and notes[k]:
                    if side == "R":
                        self.text(notes[k], x + w + 2.6, yc + 0.9, 1.1, "BL", "AV-NOTE")
                    else:
                        self.text(notes[k], x - 2.6, yc + 0.9, 1.1, "BR", "AV-NOTE")
                levels.append((Pin(x - 2.0, yc, -1, t["id"]), Pin(x + w + 2.0, yc, 1, t["id"])))
            self.text(t["id"], x + 5.0 + (w - 5.0) / 2, y0 + hh / 2, 1.3, "MC", "AV-TB",
                      rgb=(0, 0, 0) if not pe else None)
            if n > 1:
                self.text(f"{n}L {t.get('sec', sec)}", x + 5.0 + (w - 5.0) / 2, y0 + 0.5, 0.8, "BC", "AV-NOTE")
            res[t["id"]] = levels if n > 1 else levels[0]
            y = y0
        res["_bottom"] = y
        return res

    def tb_bridge(self, pins: list[Pin], layer="AV-TB", off=1.2):
        """Jumper between terminals (pins on same side)."""
        d = pins[0].d
        xs = pins[0].x - d * off
        ys = sorted(p.y for p in pins)
        self.line((xs, ys[0]), (xs, ys[-1]), layer, lw=35)
        for p in pins:
            self.dot((xs, p.y), 0.5, layer)
            if off > 1.3:
                self.line((xs, p.y), (p.x - d * 0.9, p.y), layer)

    # ------------------------------------------------------------------ cables
    @staticmethod
    def ortho(pts):
        out = [pts[0]]
        for p in pts[1:]:
            q = out[-1]
            if abs(p[0] - q[0]) > 1e-6 and abs(p[1] - q[1]) > 1e-6:
                out.append((p[0], q[1]))
            out.append(p)
        return out

    def _fan(self, pins: list[Pin], layer, names=None, oval=True, ytrunk=None, cut=None):
        """Fan conductors of one cable end into a trunk point. Returns trunk start (x,y,d)."""
        if len(pins) == 1:
            p = pins[0]
            return (p.x, p.y, p.d)
        d = pins[0].d
        ys = [p.y for p in pins]
        ymin, ymax = min(ys), max(ys)
        yc = ytrunk if ytrunk is not None else (ymin + ymax) / 2
        spread = max(abs(ymax - yc), abs(ymin - yc))
        L = STUB + max(3.0, 0.45 * spread)
        xp = pins[0].x
        xc = xp + d * L
        cut = cut or set()
        for i, p in enumerate(pins):
            xs = p.x + d * STUB
            if i in cut:
                # isolated conductor (spare / screen not connected at this end)
                self.line((p.x + d * 1.5, p.y), (xs, p.y), layer)
                self.line((p.x + d * 1.5 - 0.6, p.y - 0.6), (p.x + d * 1.5 + 0.6, p.y + 0.6), layer)
                self.line((p.x + d * 1.5 - 0.6, p.y + 0.6), (p.x + d * 1.5 + 0.6, p.y - 0.6), layer)
            else:
                self.line((p.x, p.y), (xs, p.y), layer)
            self.line((xs, p.y), (xc, yc), layer)
            if names and i < len(names) and names[i]:
                self.text(names[i], p.x + d * 3.6, p.y + 0.35, 0.95, "BC", "AV-NOTE")
        if oval:
            self.ellipse((xp + d * STUB, (ymin + ymax) / 2), 0.9, (ymax - ymin) / 2 + 1.3, "AV-CONN")
        return (xc, yc, d)

    def _trunk_start(self, pin: Pin):
        return (pin.x, pin.y)

    def cable(self, A, B, label=None, layer="W-AUDIO", names_a=None, names_b=None,
              via=None, xm=None, label_at=None, info=None, info_at=None, oval=True,
              cut_a=None, cut_b=None, ytrunk_a=None, ytrunk_b=None, rec=None,
              label_seg=None, pill=True):
        """Draw a cable from pins A to pins B (lists of Pin, same order = same conductor).
        via: list of intermediate trunk points (orthogonalised). Returns trunk points."""
        if isinstance(A, Pin):
            A = [A]
        if isinstance(B, Pin):
            B = [B]
        ta = self._fan(A, layer, names_a, oval and len(A) > 1, ytrunk_a, cut_a)
        tb = self._fan(B, layer, names_b, oval and len(B) > 1, ytrunk_b, cut_b)
        pts = [(ta[0], ta[1])]
        if via:
            pts += list(via)
        else:
            if abs(ta[1] - tb[1]) > 1e-6:
                xmid = xm if xm is not None else (ta[0] + tb[0]) / 2
                pts += [(xmid, ta[1]), (xmid, tb[1])]
        pts.append((tb[0], tb[1]))
        pts = self.ortho(pts)
        # find label segment
        segs = list(zip(pts[:-1], pts[1:]))
        hsegs = [(i, s) for i, s in enumerate(segs) if abs(s[0][1] - s[1][1]) < 1e-6]
        cut_seg = None
        if label and pill:
            pw = self.pill_w(label)
            if label_seg is not None:
                i, s = label_seg, segs[label_seg]
            elif label_at is not None:
                # segment containing label_at x (horizontal) - prefer the one
                cand = [(i, s) for i, s in hsegs if min(s[0][0], s[1][0]) <= label_at[0] <= max(s[0][0], s[1][0])
                        and (len(label_at) < 2 or label_at[1] is None or abs(s[0][1] - label_at[1]) < 1e-3)]
                i, s = cand[0] if cand else max(hsegs, key=lambda t: abs(t[1][1][0] - t[1][0][0]))
            else:
                i, s = max(hsegs, key=lambda t: abs(t[1][1][0] - t[1][0][0])) if hsegs else (0, segs[0])
            y = s[0][1]
            if label_at is not None:
                cx = label_at[0]
            else:
                cx = (s[0][0] + s[1][0]) / 2
            seg_len = abs(s[1][0] - s[0][0])
            if label_at is None and seg_len < pw + 1.0:
                # not enough room inline: tag the cable above the segment
                self.pill(cx, y + 3.4, label)
            else:
                cut_seg = (i, cx - pw / 2, cx + pw / 2)
                self.pill(cx, y, label)
        # draw trunk
        for i, (p, q) in enumerate(segs):
            if cut_seg and i == cut_seg[0]:
                x0, x1 = sorted((p[0], q[0]))
                a, b = cut_seg[1], cut_seg[2]
                if a > x0:
                    self.line((x0, p[1]), (a, p[1]), layer)
                if b < x1:
                    self.line((b, p[1]), (x1, p[1]), layer)
            else:
                self.line(p, q, layer)
        # field cable info
        if info:
            if info_at is not None:
                ix, iy, ia = info_at
            else:
                s = hsegs[0][1] if hsegs else segs[0]
                ix, iy, ia = (min(s[0][0], s[1][0]) + 3.0, s[0][1], "L")
            above, below = info if isinstance(info, (tuple, list)) else (info, None)
            al = "BL" if ia == "L" else "BR"
            tl = "TL" if ia == "L" else "TR"
            if above:
                self.text(above, ix, iy + 0.9, 1.75, al, "AV-TEXT")
            if below:
                self.text(below, ix, iy - 0.9, 1.75, tl, "AV-TEXT")
        if rec:
            self.records.append(rec)
        return pts

    def field_end(self, x, y, side, descr, above, below, h=1.85):
        """Field cable termination text (21xRWxx style) at the free end (x, y) of a trunk.
        side 'L': field on the left of the rack; 'R': field on the right."""
        if side == "L":
            self.mtext_lines(descr, x - 1.5, y, 1.3, "MR", gap=1.45)
            self.text(above, x + 2.0, y + 0.9, h, "BL", "AV-TEXT")
            self.text(below, x + 2.0, y - 0.9, h, "TL", "AV-TEXT")
        else:
            self.mtext_lines(descr, x + 1.5, y, 1.3, "ML", gap=1.45)
            self.text(above, x - 2.0, y + 0.9, h, "BR", "AV-TEXT")
            self.text(below, x - 2.0, y - 0.9, h, "TR", "AV-TEXT")

    def wire(self, pts, layer="W-AUDIO"):
        self.pline(self.ortho(pts), layer)

    # ------------------------------------------------------------- symbols
    def no_contact(self, x0, x1, y, layer="AV-SYM", t0="", t1=""):
        """Normally-open contact between x0 (COM) and x1 (NO)."""
        m = (x0 + x1) / 2
        self.line((x0, y), (m - 2.2, y), layer)
        self.line((m - 2.2, y), (m + 2.0, y + 2.0), layer)
        self.line((m + 2.2, y), (x1, y), layer)
        self.line((m + 2.2, y), (m + 2.2, y + 1.0), layer)
        if t0:
            self.text(t0, x0 + 0.6, y + 0.5, 1.15, "BL", "AV-TEXT")
        if t1:
            self.text(t1, x1 - 0.6, y + 0.5, 1.15, "BR", "AV-TEXT")
        return (m, y + 1.0)

    def led(self, x, y, rgb, layer="AV-SYM", w=8.0, flip=False):
        """Indicator lamp (LED) symbol between x and x+w at y (anode left, or right if flip)."""
        cx = x + w / 2
        s = -1 if flip else 1
        a, k = cx - s * 1.5, cx + s * 1.3
        self.line((x, y), (min(a, k), y), layer)
        self.pline([(a, y + 1.6), (k, y), (a, y - 1.6)], layer, closed=True)
        self.solid_tri((a, y + 1.6), (k, y), (a, y - 1.6), rgb)
        self.line((k, y + 1.6), (k, y - 1.6), layer)
        self.line((max(a, k), y), (x + w, y), layer)
        for k in (0, 1):
            ax = cx - 0.6 + k * 1.3
            self.line((ax, y + 2.0), (ax + 1.0, y + 3.2), layer, rgb=rgb)
            self.pline([(ax + 0.45, y + 3.25), (ax + 1.0, y + 3.2), (ax + 0.95, y + 2.65)], layer, rgb=rgb)

    def solid_tri(self, a, b, c, rgb):
        hatch = self.msp.add_hatch(dxfattribs=self._attr("AV-SYM", rgb=rgb))
        hatch.set_solid_fill(color=256, rgb=rgb)
        hatch.paths.add_polyline_path([a, b, c], is_closed=True)

    def splice(self, x, y, layer="AV-SYM"):
        self.circle((x, y), 0.9, layer)
        self.line((x - 0.9, y), (x + 0.9, y), layer)

    def breaker_pole(self, x, ytop, ybot, layer="AV-SYM"):
        """Vertical MCB pole between ytop (line) and ybot (load) at x."""
        m = (ytop + ybot) / 2
        self.line((x, ytop), (x, m + 3.0), layer)
        self.line((x - 0.7, m + 3.0 - 0.7), (x + 0.7, m + 3.0 + 0.7), layer)
        self.line((x - 0.7, m + 3.0 + 0.7), (x + 0.7, m + 3.0 - 0.7), layer)
        self.line((x, m + 3.0), (x - 2.2, m - 1.6), layer)
        self.line((x, m - 1.8), (x, ybot), layer)
        # thermal-magnetic marks
        self.pline([(x, m - 3.5), (x + 1.0, m - 3.5), (x + 1.0, m - 2.6), (x + 1.8, m - 2.6),
                    (x + 1.8, m - 3.5)], layer)

    # -------------------------------------------------------------- sheet frame
    def frame(self, info: dict, nc=12, nr=8):
        W, H = self.W, self.H
        self.rect(0, 0, W, H, "AV-ZONE", lw=13)
        x0, y0, x1, y1 = 20.0, 10.0, W - 10.0, H - 10.0
        self.rect(x0, y0, x1 - x0, y1 - y0, "AV-FRAME")
        # zone grid
        cw, rh = (x1 - x0) / nc, (y1 - y0) / nr
        for i in range(nc + 1):
            xx = x0 + i * cw
            self.line((xx, y1), (xx, y1 + 4), "AV-ZONE")
            self.line((xx, y0), (xx, y0 - 4), "AV-ZONE")
        for i in range(nc):
            self.text(str(i + 1), x0 + (i + 0.5) * cw, y1 + 2.0, 2.2, "MC", "AV-ZONE", rgb=(120, 0, 255))
            self.text(str(i + 1), x0 + (i + 0.5) * cw, y0 - 2.0, 2.2, "MC", "AV-ZONE", rgb=(120, 0, 255))
        for j in range(nr + 1):
            yy = y0 + j * rh
            self.line((x1, yy), (x1 + 4, yy), "AV-ZONE")
            self.line((x0, yy), (x0 - 4, yy), "AV-ZONE")
        for j in range(nr):
            ch = "ABCDEFGHJKLMNP"[j]
            self.text(ch, x1 + 2.0, y1 - (j + 0.5) * rh, 2.2, "MC", "AV-ZONE", rgb=(120, 0, 255))
            self.text(ch, x0 - 2.0, y1 - (j + 0.5) * rh, 2.2, "MC", "AV-ZONE", rgb=(120, 0, 255))
        self._title_block(x0, y0, x1, info)

    def _cell(self, x, y, w, h, cap, lines, hs=None, align="L", lay="AV-TITLE"):
        self.rect(x, y, w, h, lay)
        self.text(cap, x + 1.5, y + h - 1.6, 1.3, "TL", "AV-TEXT", rgb=(120, 0, 255))
        hs = hs or [3.0] * len(lines)
        n = len(lines)
        tot = sum(hs) + 1.2 * (n - 1)
        yy = y + (h - 3.0) / 2 + tot / 2
        for s, hh in zip(lines, hs):
            yy -= hh
            if align == "L":
                self.text(s, x + 3.0, yy, hh, "BL", "AV-TEXT")
            else:
                self.text(s, x + w / 2, yy, hh, "BC", "AV-TEXT")
            yy -= 1.2

    def _title_block(self, x0, y0, x1, info):
        h = 32.0
        y = y0
        self.rect(x0, y, x1 - x0, h, "AV-FRAME")
        x = x0
        # logo cell
        w = 66.0
        self.rect(x, y, w, h, "AV-TITLE")
        self.text("videlio", x + 6, y + 15.5, 9.0, "BL", "AV-TEXT")
        self.text("HMS", x + 50.5, y + 15.5, 3.2, "BL", "AV-TEXT", rgb=(230, 0, 0))
        self.text("Videlio HMS Italy srl", x + 6, y + 9.6, 2.0, "BL", "AV-TEXT")
        self.text("via G. Deledda 3, 34079 Staranzano (GO)", x + 6, y + 6.2, 1.5, "BL", "AV-TEXT")
        x += w
        cells = [
            (72.0, "Client / Shipyard:", ["FINCANTIERI S.p.A.", "CRYSTAL CRUISES - HULL 6376"], [2.6, 2.2]),
            (50.0, "Project:", [info["project"]], [6.0]),
            (52.0, "Drawing No:", [info["drawing"]], [5.0]),
            (78.0, "Area:", info["area"], [3.2] * len(info["area"])),
            (128.0, "System:", info["system"], [3.0] + [2.4] * (len(info["system"]) - 1)),
            (30.0, "Sheet:", [info["sheet"]], [4.2]),
        ]
        for cw, cap, lines, hs in cells:
            self._cell(x, y, cw, h, cap, lines, hs, align="C")
            x += cw
        # revision table
        w = 168.0
        self.rect(x, y, w, h, "AV-TITLE")
        cols = [(12, "Rev."), (22, "Date"), (88, "Description"), (23, "Drawn"), (23, "Appr.")]
        rh = h / 5
        yy = y + h
        xx = x
        for cw, cap in cols:
            self.text(cap, xx + 1.2, yy - rh / 2, 1.4, "ML", "AV-TEXT", rgb=(120, 0, 255))
            xx += cw
        for r in range(1, 5):
            self.line((x, y + h - r * rh), (x + w, y + h - r * rh), "AV-TITLE")
        xx = x
        for cw, _ in cols[:-1]:
            xx += cw
            self.line((xx, y), (xx, y + h), "AV-TITLE")
        for r, rev in enumerate(info.get("revs", [])):
            yy = y + h - (r + 1.5) * rh
            xx = x
            for (cw, _), val in zip(cols, rev):
                self.text(val, xx + 1.2, yy, 1.5, "ML", "AV-TEXT")
                xx += cw
        x += w
        # print / scale / date
        w = 30.0
        self._cell(x, y + h / 2, w, h / 2, "Print:", [info.get("print", "A1")], [3.0], align="C")
        self._cell(x, y, w, h / 2, "Scale:", ["N.T.S."], [2.6], align="C")
        x += w
        w = 44.0
        self._cell(x, y + 2 * h / 3, w, h / 3, "Date:", [info["date"]], [2.2], align="C")
        self._cell(x, y + h / 3, w, h / 3, "Drawn by:", [info.get("drawn", "")], [2.0], align="C")
        self._cell(x, y, w, h / 3, "Approved:", [info.get("approved", "")], [2.0], align="C")
        x += w
        w = x1 - x
        self.rect(x, y, w, h, "AV-TITLE")
        self.mtext_lines(["COPYRIGHT, REPRODUCTION", "AND/OR DISCLOSURE IS", "FORBIDDEN WITHOUT",
                          "VIDELIO HMS WRITTEN", "AUTHORIZATION", "", "Ref.: " + info.get("ref", "")],
                         x + w / 2, y + h - 3.0, 1.35, "TC", gap=1.6)

    def rack_boundary(self, x0, y0, x1, y1, rack, area, subtitle):
        self.rect(x0, y0, x1 - x0, y1 - y0, "AV-RACK")
        self.text(rack, x0 + 4, y1 - 4, 8.0, "TL", "AV-TEXT-DEV")
        self.text(area, x0 + 4 + text_width(rack, 8.0) + 22, y1 - 4, 8.0, "TL", "AV-TEXT-DEV")
        self.text(subtitle, x0 + 4, y1 - 15.5, 3.6, "TL", "AV-TEXT-DEV")

    def field_box(self, x, y, w, h, title, lines=()):
        """Rounded field area box (location of field equipment)."""
        r = 2.0
        self.msp.add_lwpolyline(
            [(x + r, y, 0, 0, 0), (x + w - r, y, 0, 0, 0.4142), (x + w, y + r, 0, 0, 0),
             (x + w, y + h - r, 0, 0, 0.4142), (x + w - r, y + h, 0, 0, 0),
             (x + r, y + h, 0, 0, 0.4142), (x, y + h - r, 0, 0, 0), (x, y + r, 0, 0, 0.4142)],
            format="xyseb", close=True, dxfattribs=self._attr("AV-FIELDBOX"))
        self.text(title, x + 1.8, y + h - 1.6, 1.9, "TL", "AV-TEXT")
        for i, s in enumerate(lines):
            self.text(s, x + 1.8, y + h - 4.8 - i * 2.4, 1.4, "TL", "AV-NOTE")

    def legend(self, x, ytop, items, title="LEGENDA / LEGEND"):
        self.text(title, x, ytop, 2.2, "TL", "AV-TEXT")
        y = ytop - 5.0
        for layer, txt in items:
            self.line((x, y), (x + 14, y), layer)
            self.text(txt, x + 17, y, 1.5, "ML", "AV-TEXT")
            y -= 3.6
        return y

    def notes(self, x, ytop, lines, title="NOTE"):
        self.text(title, x, ytop, 2.2, "TL", "AV-TEXT")
        y = ytop - 5.0
        for s in lines:
            self.text(s, x, y, 1.5, "ML", "AV-NOTE")
            y -= 2.7
        return y

    # ------------------------------------------------------------------ output
    def save(self, path):
        self.doc.saveas(path)


def render_pdf(sheets_paths, pdf_path, png_dir=None, dpi=110):
    """Render DXF files (list of (Sheet, dxfpath)) to a multipage PDF (vector)."""
    import fitz
    from ezdxf.addons.drawing import Frontend, RenderContext, config, layout, pymupdf

    out = fitz.open()
    pngs = []
    for sh, path in sheets_paths:
        doc = ezdxf.readfile(path)
        doc.styles.get("AV").dxf.font = "LiberationSans-Regular.ttf"
        ctx = RenderContext(doc)
        backend = pymupdf.PyMuPdfBackend()
        cfg = config.Configuration(background_policy=config.BackgroundPolicy.WHITE,
                                   color_policy=config.ColorPolicy.COLOR,
                                   lineweight_scaling=1.0, min_lineweight=0.09)
        Frontend(ctx, backend, config=cfg).draw_layout(doc.modelspace(), finalize=True)
        page = layout.Page(sh.W, sh.H, layout.Units.mm, margins=layout.Margins.all(0))
        settings = layout.Settings(fit_page=True)
        pdf_bytes = backend.get_pdf_bytes(page, settings=settings)
        src = fitz.open("pdf", pdf_bytes)
        out.insert_pdf(src)
        if png_dir:
            png = backend.get_pixmap_bytes(page, fmt="png", settings=settings, dpi=dpi)
            p = f"{png_dir}/{path.split('/')[-1].replace('.dxf', '.png')}"
            with open(p, "wb") as f:
                f.write(png)
            pngs.append(p)
    out.save(pdf_path)
    return pngs
