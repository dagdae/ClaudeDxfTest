"""Shared project data for Hull 6376 - 07 Officer & Crew Mess LES racks."""
from engine import CableRecord, Pin, Sheet, text_width

DATE = "30/10/2026"
REF_DOC = "006376A6F41026007 rev.00"
REVS = [("A", DATE, "FIRST ISSUE - EXECUTIVE WIRING (from " + REF_DOC + ")", "", "")]

# internal (in-rack) cable types
INT_AUDIO = "1x2x0.25 SCREENED LSZH"
INT_SPK = "1x2x1.5 HF-TXCS"
INT_CAT6A = "CAT6A S/FTP LSZH PATCH"
INT_LC = "LC/LC DUPLEX OM4 PATCH"
INT_GPIO = "4x0.5 SCREENED LSZH"
INT_CTRL2 = "2x0.75 LSZH"
INT_24V = "2x1.0 LSZH"
INT_PWR = "3G1.5 LSZH"
INT_PWR25 = "3G2.5 LSZH"


def info(drawing, sheet, system, area=None, print_fmt="A1"):
    return dict(project="HULL 6376", drawing=drawing, sheet=sheet,
                area=area or ["07 - CREW & OFFICER MESS", "ML/F01AM - DK02 FR62 STBD", "ELA - EL. CABINET"],
                system=system, date=DATE, revs=REVS, ref=REF_DOC, print=print_fmt,
                drawn="", approved="")


def rec(sh: Sheet, label, cable_no, ctype, fdev, fport, fconn, tdev, tport, tconn, cores, length, signal, note=""):
    return CableRecord(label, cable_no, ctype, fdev, fport, fconn, tdev, tport, tconn, cores, length,
                       f"{sh.code}/{sh.sheet_no}", signal, note)


def legend_symbols(sh: Sheet, x, ytop):
    """Symbol legend block (graphic conventions of the 21xRWxx standard)."""
    sh.text("SYMBOLS", x, ytop, 2.2, "TL", "AV-TEXT")
    y = ytop - 6.0
    w = sh.pill(x + 16, y, "DEV.F01-OUT/DEV.F02-IN")
    sh.text("internal cable label: FROM.DEVICE-OUTPUT/TO.DEVICE-INPUT", x + 34 + 4, y, 1.45, "ML", "AV-TEXT")
    y -= 6.0
    sh.connector(x + 2, y, "R", "RJ45", "M")
    sh.text("cable connector: type / gender (M plug, F socket)", x + 16, y, 1.45, "ML", "AV-TEXT")
    y -= 7.5
    pins = sh.connector(x + 2, y, "R", "EB", "F", ["+", "-", "G"])
    sh.text("multi-pin connector: pins drawn one by one", x + 16, y, 1.45, "ML", "AV-TEXT")
    y -= 8.0
    sh.ellipse((x + 6, y), 0.9, 3.0, "AV-CONN")
    for dy in (-1.5, 0, 1.5):
        sh.line((x + 2, y + dy), (x + 10, y + dy), "AV-CONN")
    sh.text("cable sheath / screen (conductors fanned out)", x + 16, y, 1.45, "ML", "AV-TEXT")
    y -= 5.5
    sh.line((x + 2, y), (x + 10, y), "AV-CONN")
    sh.line((x + 4.8, y - 0.6), (x + 6.0, y + 0.6), "AV-CONN")
    sh.line((x + 4.8, y + 0.6), (x + 6.0, y - 0.6), "AV-CONN")
    sh.text("conductor cut back, isolated and taped (not connected)", x + 16, y, 1.45, "ML", "AV-TEXT")
    y -= 5.5
    sh.rect(x + 2, y - 1.5, 10, 3.0, "AV-TB")
    sh.hatch_rect(x + 5, y - 1.5, 7, 3.0, "AV-TB", rgb=(0, 150, 0), scale=0.25)
    sh.text("PE terminal (green/yellow, earthed on DIN rail)", x + 16, y, 1.45, "ML", "AV-TEXT")
    y -= 7.0
    sh.xref(Pin(x + 1, y, 1), "02", [])
    sh.text("continues on sheet nn (number in diamond)", x + 16, y, 1.45, "ML", "AV-TEXT")
    y -= 6.0
    sh.rect(x + 2, y - 2.0, 10, 4.0, "AV-DEVICE-REF")
    sh.text("device drawn in full on another sheet (partial view)", x + 16, y, 1.45, "ML", "AV-TEXT")
    return y - 4


def table(sh: Sheet, x, ytop, cols, rows, title=None, h=1.5, rh=4.2):
    """Simple grid table. cols: list of (width, header)."""
    y = ytop
    if title:
        sh.text(title, x, y, 2.2, "BL", "AV-TEXT")
        y -= 1.5
    W = sum(c[0] for c in cols)
    n = len(rows) + 1
    sh.rect(x, y - n * rh, W, n * rh, "AV-TITLE")
    for i in range(1, n):
        sh.line((x, y - i * rh), (x + W, y - i * rh), "AV-TITLE")
    xx = x
    for cw, hd in cols:
        sh.text(hd, xx + 1.0, y - rh / 2, h, "ML", "AV-TEXT", rgb=(120, 0, 255))
        xx += cw
        sh.line((xx, y), (xx, y - n * rh), "AV-TITLE")
    for r, row in enumerate(rows):
        xx = x
        for (cw, _), v in zip(cols, row):
            sh.text(v, xx + 1.0, y - (r + 1.5) * rh, h, "ML", "AV-TEXT")
            xx += cw
    return y - n * rh
