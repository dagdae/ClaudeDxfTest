"""Reusable composite symbols (relays, status lamps, MCBs, PS blocks)."""
from engine import Pin, Sheet


def relay_contacts(sh: Sheet, x, yc, tag, poles, sub, w=30.0):
    """Detached NO contacts (2 poles) of a muting relay. Returns (left pins, right pins)."""
    sh.rect(x, yc - 6.5, w, 13.0, "AV-DEVICE-REF")
    sh.text(tag, x + w / 2, yc + 7.4, 1.9, "BC", "AV-TEXT-DEV")
    sh.text(sub, x + w / 2, yc - 7.4, 1.1, "TC", "AV-NOTE")
    c1, n1, c2, n2 = poles
    L, R = [], []
    for i, (c, n) in enumerate(((c1, n1), (c2, n2))):
        y = yc + 2.5 - i * 5.0
        sh.no_contact(x, x + w, y, "AV-SYM", c, n)
        sh.dot((x, y), 0.5, "AV-TB")
        sh.dot((x + w, y), 0.5, "AV-TB")
        sh.line((x, y), (x - 2.0, y), "AV-TB")
        sh.line((x + w, y), (x + w + 2.0, y), "AV-TB")
        L.append(Pin(x - 2.0, y, -1, c))
        R.append(Pin(x + w + 2.0, y, 1, n))
    sh.line((x + w / 2 + 0.2, yc + 3.5), (x + w / 2 + 0.2, yc - 1.5), "AV-SYM", ltype="AV_HIDDEN")
    return L, R


def relay_coil(sh: Sheet, x, yc, tag, note):
    d = sh.device(x, yc + 10.5, 34.0, "FINDER", "55.34.9.024.0040", "MUTING RELAY", tag,
                  left=[dict(id="COIL", label="", conn="TB", g="", pins=["A1", "A2"])],
                  header=6.0, pad=1.5, title_h=1.6, min_h=11.0)
    yy = d["COIL"].y
    cx = x + 17.0
    sh.rect(cx - 4.0, yy - 2.5, 8.0, 5.0, "AV-SYM")
    sh.line((cx - 4.0, yy + 2.5), (cx + 4.0, yy - 2.5), "AV-SYM")
    p1, p2 = d["COIL"].pins
    sh.wire([(x, p1.y), (cx - 6.0, p1.y), (cx - 6.0, yy + 2.5), (cx - 4.0, yy + 2.5)], "AV-SYM")
    sh.wire([(x, p2.y), (cx - 7.0, p2.y), (cx - 7.0, yy - 2.5), (cx - 4.0, yy - 2.5)], "AV-SYM")
    sh.text("24VDC", cx + 5.0, yy, 1.1, "ML", "AV-NOTE")
    sh.text("+99.02 LED/DIODE", cx, d["_box"].pins[1].y - 3.0, 1.0, "MC", "AV-NOTE")
    sh.text("contacts: " + note, x + 17.0, d["_box"].pins[0].y - 7.6, 1.05, "TC", "AV-NOTE")
    return d


def led_group(sh: Sheet, x, ytop, tags):
    d = sh.device(x, ytop, 40.0, "SCHNEIDER", "XB5EVB4 (RD) / XB5EVB3 (GN)", "SYSTEM STATUS",
                  f"{tags[0]} / {tags[1]}",
                  left=[dict(id="MID", label="")],
                  right=[dict(id="P24", label=""), dict(id="P0", label="")],
                  header=8.0, pad=2.0, title_h=1.7)
    ym = d["MID"].y
    xl = x + 9.0
    sh.line((x, ym), (xl, ym), "AV-SYM")
    sh.dot((xl, ym), 0.5, "AV-SYM")
    sh.led(xl, ym, (230, 0, 0), w=31.0, flip=True)
    sh.line((xl, ym), (xl, d["P0"].y), "AV-SYM")
    sh.led(xl, d["P0"].y, (0, 170, 0), w=31.0)
    sh.text("MUTING", xl + 15.5, ym - 2.0, 1.1, "TC", "AV-NOTE")
    sh.text("RUNNING", xl + 15.5, d["P0"].y - 2.0, 1.1, "TC", "AV-NOTE")
    sh.text("X2 RD/X1 GN", x - 0.8, ym + 1.0, 1.0, "BR", "AV-NOTE")
    sh.text("X1 RD", x + 41.0, ym + 1.0, 1.0, "BL", "AV-NOTE")
    sh.text("X2 GN", x + 41.0, d["P0"].y + 1.0, 1.0, "BL", "AV-NOTE")
    return d


def breaker(sh: Sheet, x, ytop, tag, phases, spec="C16"):
    """Horizontal MCB, one pole per phase. Returns (in pins, out pins)."""
    n = len(phases)
    h = 7.5 + 6.0 * (n - 1) + 6.0
    sh.rect(x, ytop - h, 28.0, h, "AV-DEVICE")
    sh.text(tag, x + 14.0, ytop + 1.2, 2.1, "BC", "AV-TEXT-DEV")
    sh.text(f"{spec} {n}P 6kA", x + 14.0, ytop - h - 1.2, 1.4, "TC", "AV-TEXT")
    L, R = [], []
    for i, ph in enumerate(phases):
        y = ytop - 7.5 - 6.0 * i
        sh.line((x, y), (x + 8.0, y), "AV-SYM")
        sh.line((x + 8.0 - 0.6, y - 0.6), (x + 8.0 + 0.6, y + 0.6), "AV-SYM")
        sh.line((x + 8.0 - 0.6, y + 0.6), (x + 8.0 + 0.6, y - 0.6), "AV-SYM")
        sh.line((x + 8.0, y), (x + 15.0, y + 2.6), "AV-SYM")
        sh.pline([(x + 15.5, y), (x + 17.0, y), (x + 17.0, y + 1.3), (x + 18.6, y + 1.3), (x + 18.6, y),
                  (x + 28.0, y)], "AV-SYM")
        sh.text(str(2 * i + 1), x + 1.0, y + 0.5, 1.0, "BL", "AV-NOTE")
        sh.text(str(2 * i + 2), x + 27.0, y + 0.5, 1.0, "BR", "AV-NOTE")
        sh.text(ph, x - 2.5, y + 0.5, 1.1, "BR", "AV-NOTE")
        sh.line((x, y), (x - 2.0, y), "AV-SYM")
        sh.line((x + 28.0, y), (x + 30.0, y), "AV-SYM")
        L.append(Pin(x - 2.0, y, -1, str(2 * i + 1)))
        R.append(Pin(x + 30.0, y, 1, str(2 * i + 2)))
    sh.line((x + 11.5, ytop - 3.0), (x + 11.5, ytop - h + 2.0), "AV-SYM", ltype="AV_HIDDEN")
    return L, R


def ps_block(sh: Sheet, x, ytop, tag, sub, alloc, in_side="L"):
    """Compact 8-socket power strip (21xRWxx symbol) with hard-wired L/N/PE input."""
    port = dict(id="IN", label="", conn="TB", g="", pins=["L", "N", "PE"])
    d = sh.device(x, ytop, 46.0, "PS BLOCK 8x SCHUKO 230V", sub, "", tag,
                  left=[port] if in_side == "L" else [], right=[port] if in_side == "R" else [],
                  header=2.0, pad=1.5, title_h=1.6, tag_lines=[tag, alloc])
    (b0, b1) = d["_box"].pins[0], d["_box"].pins[1]
    cy = (b0.y + b1.y) / 2
    cx = (b0.x + b1.x) / 2
    for dx in (-9.0, 9.0):
        sh.circle((cx + dx, cy), 2.6, "AV-SYM")
        sh.dot((cx + dx - 0.9, cy), 0.45, "AV-SYM")
        sh.dot((cx + dx + 0.9, cy), 0.45, "AV-SYM")
    sh.text("8", cx, cy, 2.4, "MC", "AV-TEXT")
    return d
