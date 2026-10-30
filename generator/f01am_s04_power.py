"""ML/F01AM - sheet 04: 230V IT power distribution, UPS, PS blocks, outgoing feeders, earthing."""
from common import INT_PWR, INT_PWR25, info, legend_symbols, rec, table
from engine import PIN, Pin, Sheet

DRW = "07FRW01"


def breaker(sh, x, ytop, tag, phases, spec="C16"):
    """Horizontal MCB: one pole per phase. Returns (in pins, out pins)."""
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


def ps_block(sh, x, ytop, tag, sub, loads, in_side="L"):
    outs = []
    for i in range(1, 9):
        ld = loads.get(i)
        if ld:
            outs.append(dict(id=f"O{i}", label=f"{i} {ld[0]}", conn="SCHUKO", g="M"))
        else:
            outs.append(dict(id=f"O{i}", label=f"{i} SPARE"))
    inp = [dict(id="IN", label="IN", conn="TB", g="", pins=["L", "N", "PE"])]
    left, right = (inp, outs) if in_side == "L" else (outs, inp)
    return sh.device(x, ytop, 40.0, "PS BLOCK 8x SCHUKO", "230V 16A", sub, tag, left=left, right=right,
                     header=8.0, pad=2.0, title_h=1.8)


def tb_group(sh, x, ytop, ids, names, title="", gap_after=None, sec="4"):
    terms = []
    for i, (t, nm) in enumerate(zip(ids, names)):
        d = dict(id=t, note=nm, note_side="L" if False else "R", sec=sec)
        if nm == "PE":
            d["pe"] = True
            d["note"] = None
        if gap_after and i in gap_after:
            d["gap"] = 2.0
        terms.append(d)
    return sh.terminal_block(x, ytop, title, terms, sec=sec)


def build():
    sh = Sheet(DRW, "04", "POWER")
    sh.frame(info(DRW, "04 / 04", ["L.E.S. WIRING DIAGRAM", "RACK ML/F01AM",
                                   "230V AC (IT 3PH) DISTRIBUTION - UPS - EARTHING"]))
    sh.rack_boundary(125.0, 128.0, 716.0, 572.0, "ML/F01AM", "CREW & OFFICER MESS",
                     "SHEET 04 - 230V AC DISTRIBUTION / UPS / EARTHING")

    # ------------------------------------------------------------ incoming supply
    tba_in = sh.terminal_block(118.0, 538.0, "TBA1", [dict(id="01", note=None), dict(id="02"), dict(id="03"),
                                                      dict(id="04", pe=True)], sec="10")
    sh.cable([tba_in[i][0] for i in ("01", "02", "03", "04")], Pin(40.0, 532.0, 1), None, "W-POWER",
             names_a=["L1", "L2", "L3", "PE"], ytrunk_a=532.0,
             info=("U/A3A0043AAA  4x6 HF-P", "Mt.15 - FROM FZ/QFUA3A00"), info_at=(43.0, 532.0, "L"),
             rec=rec(sh, "U/A3A0043AAA", "U/A3A0043AAA", "4x6 HF-P", "FZ/QFUA3A00 (yard switchboard)", "UA31043",
                     "by yard", "ML/F01AM", "TBA1 01-04", "TERM. 10mm2", "L1 L2 L3 PE", "15 m", "230V AC 3PH IT",
                     "Supply by yard; terminated by Videlio on TBA1"))
    sh.mtext_lines(["YARD SWITCHBOARD", "FZ/QFUA3A00 - UA31043", "220V 3PH (IT)", "(BY YARD)"], 38.0, 537.0, 1.35,
                   "TR")
    i1, o1 = breaker(sh, 195.0, 546.0, "DJ01", ["L1", "L2", "L3"])
    sh.cable([tba_in[i][1] for i in ("01", "02", "03")], i1, "TBA1-01/DJ01-1", "W-POWER", names_a=["L1", "L2", "L3"],
             names_b=["L1", "L2", "L3"],
             rec=rec(sh, "TBA1-01/DJ01-1", "", "3x H07Z1-K 6mm2 LSZH", "TBA1", "01-03", "TERM.", "DJ01", "1/3/5",
                     "TERM.", "L1 L2 L3", "0.5 m", "230V AC 3PH", "Main switch"))
    # 3-phase bus
    BUS = {"L1": 238.0, "L2": 242.0, "L3": 246.0}
    bottoms = {"L1": 400.0, "L2": 220.0, "L3": 214.0}
    for p, ph in zip(o1, ("L1", "L2", "L3")):
        sh.line((p.x, p.y), (BUS[ph], p.y), "W-POWER")
        sh.dot((BUS[ph], p.y), 0.55, "W-POWER")
        sh.line((BUS[ph], p.y), (BUS[ph], bottoms[ph]), "W-POWER", lw=50)
        sh.text(ph, BUS[ph], p.y + 1.5 + (2.0 if ph == "L1" else 0.0), 1.2, "BC", "AV-NOTE")
    sh.text("COMB BUSBAR 3P 10mm2", 242.0, 549.0, 1.2, "BC", "AV-NOTE")

    def tap(phs, pins):
        for ph, p in zip(phs, pins):
            sh.line((BUS[ph], p.y), (p.x, p.y), "W-POWER")
            sh.dot((BUS[ph], p.y), 0.55, "W-POWER")

    # ---------------------------------------------------------------- DJ02 -> UPS + PSU
    i2, o2 = breaker(sh, 265.0, 520.0, "DJ02", ["L1", "L2"])
    tap(["L1", "L2"], i2)
    sh.text("L1-L2", 258.0, 521.0, 1.4, "BR", "AV-TEXT")
    t2 = sh.terminal_block(345.0, 516.0, "", [dict(id="05", sec="2.5"), dict(id="06", sec="2.5"),
                                              dict(id="07", pe=True, sec="2.5"),
                                              dict(id="08", gap=2.0, sec="2.5"), dict(id="09", sec="2.5"),
                                              dict(id="10", pe=True, sec="2.5")], sec="2.5")
    sh.tb_bridge([t2["05"][0], t2["08"][0]], off=1.2)
    sh.tb_bridge([t2["06"][0], t2["09"][0]], off=2.6)
    sh.cable(o2, [t2["05"][0], t2["06"][0]], "DJ02-2/TBA1-05", "W-POWER", names_a=["L1", "L2"],
             names_b=["L1", "L2"],
             rec=rec(sh, "DJ02-2/TBA1-05", "", "2x H07Z1-K 2.5mm2 LSZH", "DJ02", "2/4", "TERM.", "TBA1", "05-06",
                     "TERM.", "L1 L2", "0.5 m", "230V AC", "UPS + mute PSU supply (non-UPS)"))
    ups = sh.device(420.0, 528.0, 54.0, "SOCOMEC", "NRT4-U020B-C", "UPS", "UPS-F01",
                    left=[dict(id="IN", label="AC IN", conn="IEC C13", g="F")],
                    right=[dict(id="G11", label="GRP1-1", conn="IEC C14", g="M"),
                           dict(id="G12", label="GRP1-2", conn="IEC C14", g="M"),
                           dict(id="G13", label="GRP1-3"), dict(id="G14", label="GRP1-4"),
                           dict(id="G21", label="GRP2-1"), dict(id="G22", label="GRP2-2"),
                           dict(id="G23", label="GRP2-3"), dict(id="G24", label="GRP2-4"),
                           dict(id="ETH", label="ETH", conn="RJ45", g="M"),
                           dict(id="USB", label="USB"), dict(id="RS", label="RS-232")],
                    icon="ups", header=10.0, pad=3.0)
    for pid in ("G13", "G14", "G21", "G22", "G23", "G24", "USB", "RS"):
        sh.text("n.c.", ups[pid].p.x + 2.6, ups[pid].p.y, 1.1, "ML", "AV-NOTE")
    sh.xref(ups["ETH"].p, "02", ["NPB-F01 P07", "LES-NET"], wire_layer="W-LESNET")
    sh.cable([t2[i][1] for i in ("05", "06", "07")], ups["IN"].p, "TBA1-05/UPS.F01-IN", "W-POWER",
             names_a=["L1", "L2", "PE"],
             rec=rec(sh, "TBA1-05/UPS.F01-IN", "", INT_PWR, "TBA1", "05-07", "TERM.", "UPS-F01", "AC IN",
                     "IEC C13 F (cord)", "L1 L2 PE", "1.5 m", "230V AC", "DJ02 L1-L2"))
    sh.cable([t2[i][1] for i in ("08", "09", "10")], Pin(388.0, 470.0, 2), None, "W-POWER",
             names_a=["L1", "L2", "PE"], via=[(388.0, 499.5)],
             rec=rec(sh, "TBA1-08/PSU.F01-AC", "", INT_PWR, "TBA1", "08-10", "TERM.", "PSU-F01", "AC IN L/N/PE",
                     "TERM.", "L1 L2 PE", "1.0 m", "230V AC", "Mute PSU 24VDC (sheet 03)"))
    sh.xref(Pin(388.0, 470.0, -2), "03", ["TBA1-08/PSU.F01-AC", "PSU-F01 AC IN"], lead=0.0)

    # ---------------------------------------------------------------- UPS outputs
    ta = sh.terminal_block(530.0, 517.0, "TBA2", [dict(id="01"), dict(id="02"), dict(id="03", pe=True),
                                                  dict(id="04", gap=2.0), dict(id="05"), dict(id="06", pe=True)],
                           sec="2.5")
    sh.cable(ups["G11"].p, [ta[i][0] for i in ("01", "02", "03")], "UPS.F01-OUT1/TBA2-01", "W-POWER",
             names_b=["L", "N", "PE"], label_at=(502.0, None),
             rec=rec(sh, "UPS.F01-OUT1/TBA2-01", "", INT_PWR, "UPS-F01", "GRP1-1", "IEC C14 M (cord)", "TBA2",
                     "01-03", "TERM.", "L N PE", "1.0 m", "230V UPS", "UPS output -> DJ03"))
    sh.cable(ups["G12"].p, [ta[i][0] for i in ("04", "05", "06")], "UPS.F01-OUT2/TBA2-04", "W-POWER",
             names_b=["L", "N", "PE"], label_at=(502.0, None),
             rec=rec(sh, "UPS.F01-OUT2/TBA2-04", "", INT_PWR, "UPS-F01", "GRP1-2", "IEC C14 M (cord)", "TBA2",
                     "04-06", "TERM.", "L N PE", "1.0 m", "230V UPS", "UPS output -> DJ04"))
    i3, o3 = breaker(sh, 600.0, 532.0, "DJ03", ["L", "N"])
    i4, o4 = breaker(sh, 600.0, 500.0, "DJ04", ["L", "N"])
    sh.cable([ta["01"][1], ta["02"][1]], i3, "TBA2-01/DJ03-1", "W-POWER", names_a=["L", "N"], names_b=["L", "N"],
             rec=rec(sh, "TBA2-01/DJ03-1", "", "2x H07Z1-K 2.5mm2 LSZH", "TBA2", "01-02", "TERM.", "DJ03", "1/3",
                     "TERM.", "L N", "0.3 m", "230V UPS", ""))
    sh.cable([ta["04"][1], ta["05"][1]], i4, "TBA2-04/DJ04-1", "W-POWER", names_a=["L", "N"], names_b=["L", "N"],
             rec=rec(sh, "TBA2-04/DJ04-1", "", "2x H07Z1-K 2.5mm2 LSZH", "TBA2", "04-05", "TERM.", "DJ04", "1/3",
                     "TERM.", "L N", "0.3 m", "230V UPS", ""))
    tb = sh.terminal_block(680.0, 531.0, "", [dict(id="07"), dict(id="08"), dict(id="09", pe=True),
                                              dict(id="10", gap=2.0), dict(id="11"), dict(id="12", pe=True)],
                           sec="2.5")
    sh.tb_bridge([tb["07"][0], tb["10"][0]], off=1.2)
    sh.tb_bridge([tb["08"][0], tb["11"][0]], off=2.6)
    sh.cable(o3, [tb["07"][0], tb["08"][0]], "DJ03-2/TBA2-07", "W-POWER", names_a=["L", "N"], names_b=["L", "N"],
             rec=rec(sh, "DJ03-2/TBA2-07", "", "2x H07Z1-K 2.5mm2 LSZH", "DJ03", "2/4", "TERM.", "TBA2", "07-08",
                     "TERM.", "L N", "0.3 m", "230V UPS", "PSB-F03 / PSB-F04"))
    tc = sh.terminal_block(680.0, 499.0, "", [dict(id="13", sec="6"), dict(id="14", sec="6"),
                                              dict(id="15", pe=True, sec="6")], sec="6")
    sh.cable(o4, [tc["13"][0], tc["14"][0]], "DJ04-2/TBA2-13", "W-POWER", names_a=["L", "N"], names_b=["L", "N"],
             rec=rec(sh, "DJ04-2/TBA2-13", "", "2x H07Z1-K 6mm2 LSZH", "DJ04", "2/4", "TERM.", "TBA2", "13-14",
                     "TERM.", "L N", "0.3 m", "230V UPS", "Feeder to ML/B01AM"))
    # feeder to ML/B01AM
    b01 = sh.device(758.0, 512.0, 50.0, "LES RACK ATRIUM", "ML/B01AM (07BRW01)", "DK04 FR149 SB", "TBA-B01",
                    left=[dict(id="IN", label="230V UPS IN", conn="TB", g="", pins=["L", "N", "PE"])],
                    partial=True, header=8.0, pad=3.0, title_h=1.8)
    sh.cable([tc[i][1] for i in ("13", "14", "15")], b01["IN"].pins, None, "W-POWER", names_a=["L", "N", "PE"],
             names_b=["L", "N", "PE"],
             info=("K/ML07405  3G6 HF-P", "Mt.160 - TO ML/B01AM"), info_at=(668.0, None, "L") if False else None,
             rec=rec(sh, "K/ML07405", "K/ML07405", "3G6 HF-P", "ML/F01AM", "TBA2 13-15", "TERM.", "ML/B01AM",
                     "TBA-B01 230V UPS IN", "TERM.", "L N PE", "160 m", "230V UPS",
                     "POWER TO ATRIUM, CRYSTAL COVE (A6F41026007 sh.06) via DJ04 C16"))
    # UPS PS blocks (IN on the right side)
    pb3 = ps_block(sh, 610.0, 452.0, "PSB-F03", "UPS - FIXED MOUNT", {1: ("DSP-F01", "01"), 2: ("NSW-F01", "02")},
                   in_side="R")
    pb4 = ps_block(sh, 610.0, 362.0, "PSB-F04", "UPS - SWING MOUNT", {}, in_side="R")
    for pb, ids, xv in ((pb3, ("07", "08", "09"), 704.0), (pb4, ("10", "11", "12"), 708.0)):
        tag = "PSB.F03" if pb is pb3 else "PSB.F04"
        sh.cable([tb[i][1] for i in ids], pb["IN"].pins, f"TBA2-{ids[0]}/{tag}-IN", "W-POWER",
                 names_a=["L", "N", "PE"], names_b=["L", "N", "PE"],
                 via=[(xv, tb[ids[1]][1].y), (xv, pb["IN"].pins[1].y)], label_at=(688.0, pb["IN"].pins[1].y),
                 rec=rec(sh, f"TBA2-{ids[0]}/{tag}-IN", "", INT_PWR25, "TBA2", f"{ids[0]}-{ids[2]}", "TERM.",
                         tag.replace(".", "-"), "IN", "TERM.", "L N PE", "1.5 m", "230V UPS", ""))
    for pb, loads in ((pb3, {1: ("DSP-F01", "01"), 2: ("NSW-F01", "02")}), (pb4, {})):
        for i in range(1, 9):
            p = pb[f"O{i}"].p
            if i in loads:
                sh.xref(p, loads[i][1], [loads[i][0] + " IEC C14", "SCHUKO/C13 3G1.0"], wire_layer="W-POWER")
                lbl = f"{pb['_box'].dev.replace('-', '.')}-{i}/{loads[i][0].replace('-', '.')}-PWR"
                sh.records.append(rec(sh, lbl, "", "3G1.0 LSZH CORD SCHUKO/IEC C13", pb["_box"].dev, f"OUT {i}",
                                      "SCHUKO M", loads[i][0], "MAINS IN", "IEC C13 F", "L N PE", "1.5 m",
                                      "230V UPS", "Power cord"))

    # ---------------------------------------------------------------- DJ05 -> PSB-F01/F02
    i5, o5 = breaker(sh, 265.0, 420.0, "DJ05", ["L1", "L3"])
    tap(["L1", "L3"], i5)
    sh.text("L1-L3", 258.0, 421.0, 1.4, "BR", "AV-TEXT")
    t5 = sh.terminal_block(345.0, 416.0, "", [dict(id="11"), dict(id="12"), dict(id="13", pe=True),
                                              dict(id="14", gap=2.0), dict(id="15"), dict(id="16", pe=True)],
                           sec="2.5")
    sh.tb_bridge([t5["11"][0], t5["14"][0]], off=1.2)
    sh.tb_bridge([t5["12"][0], t5["15"][0]], off=2.6)
    sh.cable(o5, [t5["11"][0], t5["12"][0]], "DJ05-2/TBA1-11", "W-POWER", names_a=["L1", "L3"],
             names_b=["L1", "L3"],
             rec=rec(sh, "DJ05-2/TBA1-11", "", "2x H07Z1-K 2.5mm2 LSZH", "DJ05", "2/4", "TERM.", "TBA1", "11-12",
                     "TERM.", "L1 L3", "0.5 m", "230V AC", "Non-UPS internal distribution"))
    pb1 = ps_block(sh, 430.0, 420.0, "PSB-F01", "INTERNAL DISTR. - FIXED", {1: ("AMP-F01", "01")})
    pb2 = ps_block(sh, 430.0, 335.0, "PSB-F02", "INTERNAL DISTR. - SWING", {})
    sh.cable([t5[i][1] for i in ("11", "12", "13")], pb1["IN"].pins, "TBA1-11/PSB.F01-IN", "W-POWER",
             names_a=["L1", "L3", "PE"], names_b=["L", "N", "PE"],
             rec=rec(sh, "TBA1-11/PSB.F01-IN", "", INT_PWR25, "TBA1", "11-13", "TERM.", "PSB-F01", "IN", "TERM.",
                     "L N PE", "1.5 m", "230V AC", ""))
    sh.cable([t5[i][1] for i in ("14", "15", "16")], pb2["IN"].pins, "TBA1-14/PSB.F02-IN", "W-POWER",
             names_a=["L1", "L3", "PE"], names_b=["L", "N", "PE"], xm=385.0, label_at=(372.0, None) if False else None,
             rec=rec(sh, "TBA1-14/PSB.F02-IN", "", INT_PWR25, "TBA1", "14-16", "TERM.", "PSB-F02", "IN", "TERM.",
                     "L N PE", "1.5 m", "230V AC", ""))
    p = pb1["O1"].p
    sh.xref(p, "01", ["AMP-F01 IEC C14", "SCHUKO/C13 3G1.5"], wire_layer="W-POWER")
    sh.records.append(rec(sh, "PSB.F01-1/AMP.F01-PWR", "", "3G1.5 LSZH CORD SCHUKO/IEC C13", "PSB-F01", "OUT 1",
                          "SCHUKO M", "AMP-F01", "MAINS IN", "IEC C13 F", "L N PE", "1.5 m", "230V AC", "Power cord"))

    # ---------------------------------------------------------------- DJ06 -> connection panels
    i6, o6 = breaker(sh, 265.0, 240.0, "DJ06", ["L2", "L3"])
    tap(["L2", "L3"], i6)
    sh.text("L2-L3", 258.0, 241.0, 1.4, "BR", "AV-TEXT")
    ids = [f"{i:02d}" for i in range(17, 29)]
    terms = []
    for k, t in enumerate(ids):
        d = dict(id=t, sec="2.5")
        if k % 3 == 2:
            d["pe"] = True
        if k in (3, 6, 9):
            d["gap"] = 4.0
        terms.append(d)
    t6 = sh.terminal_block(345.0, 243.0, "", terms, sec="2.5")
    sh.tb_bridge([t6[i][0] for i in ("17", "20", "23", "26")], off=1.2)
    sh.tb_bridge([t6[i][0] for i in ("18", "21", "24", "27")], off=2.6)
    sh.cable(o6, [t6["17"][0], t6["18"][0]], "DJ06-2/TBA1-17", "W-POWER", names_a=["L2", "L3"],
             names_b=["L2", "L3"],
             rec=rec(sh, "DJ06-2/TBA1-17", "", "2x H07Z1-K 2.5mm2 LSZH", "DJ06", "2/4", "TERM.", "TBA1", "17-18",
                     "TERM.", "L2 L3", "0.5 m", "230V AC", "Connection panels feeders"))
    cps = [("K/ML07401", "ML*F01CP-F01", "PWR IN 1", ("17", "18", "19")),
           ("K/ML07402", "ML*F01CP-F01", "PWR IN 2", ("20", "21", "22")),
           ("K/ML07403", "ML*F02CP-F01", "PWR IN 1", ("23", "24", "25")),
           ("K/ML07404", "ML*F02CP-F01", "PWR IN 2", ("26", "27", "28"))]
    cp_dev = {}
    for tag, ytop, loc in (("ML*F01CP-F01", 266.0, "PAX EMB. Dk3 PS"), ("ML*F02CP-F01", 214.0, "PAX EMB. Dk3 SB")):
        cp_dev[tag] = sh.device(758.0, ytop, 50.0, "VIDELIO", "CONNECTION PANEL", loc + " (07BRW01)", tag,
                                left=[dict(id="PWR IN 1", label="PWR IN 1 -> SCHUKO 1", conn="TB", g="",
                                           pins=["L", "N", "PE"]),
                                      dict(id="PWR IN 2", label="PWR IN 2 -> SCHUKO 2", conn="TB", g="",
                                           pins=["L", "N", "PE"])],
                                partial=True, header=6.0, pad=2.0, title_h=1.7, icon=None)
    for k, (kno, tag, port, tids) in enumerate(cps):
        dst = cp_dev[tag][port].pins
        sh.cable([t6[i][1] for i in tids], dst, None, "W-POWER", names_a=["L2", "L3", "PE"], names_b=["L", "N", "PE"],
                 xm=718.0 + k * 3.0,
                 info=(f"{kno}  3G2.5 HF-P", f"Mt.150 - TO {tag} {port}"), info_at=(390.0, t6[tids[1]][1].y, "L"),
                 rec=rec(sh, kno, kno, "3G2.5 HF-P", "ML/F01AM", f"TBA1 {tids[0]}-{tids[2]}", "TERM.", tag, port,
                         "TERM.", "L N PE", "150 m", "230V AC", "DJ06 (A6F41026007 sh.06). Check voltage drop vs load."))

    # ---------------------------------------------------------------- earthing
    yb = 160.0
    sh.rect(140.0, yb - 1.5, 150.0, 3.0, "W-PE")
    sh.hatch_rect(140.0, yb - 1.5, 150.0, 3.0, "W-PE", rgb=(0, 150, 0), scale=0.4)
    sh.text("PE-F01  RACK EARTH BAR (Cu 25x4)", 140.0, yb + 3.0, 1.9, "BL", "AV-TEXT")
    drops = [(150.0, "TBA1-04 PE IN"), (172.0, "DIN RAILS TBA1/TBA2"), (194.0, "DIN RAILS TB1-TB4"),
             (216.0, "PSB-F01..F04 PE"), (238.0, "RACK FRAME/DOORS"), (260.0, "SWING FRAME"),
             (282.0, "HULL BOND (YARD)")]
    for x, t in drops:
        sh.line((x, yb - 1.5), (x, yb - 9.0), "W-PE")
        sh.dot((x, yb - 1.5), 0.5, "W-PE")
        sh.text(t, x, yb - 10.0, 1.05, "TC", "AV-NOTE")
    sh.ground(282.0, yb - 9.0)
    sh.text("16mm2 G/Y", 284.0, yb - 5.0, 1.0, "ML", "AV-NOTE")

    # ---------------------------------------------------------------- notes
    rows = [["DJ01", "C16 3P", "L1 L2 L3", "MAIN SWITCH", "-"],
            ["DJ02", "C16 2P", "L1-L2", "UPS-F01 IN, PSU-F01 (mute)", "non-UPS"],
            ["DJ03", "C16 2P", "UPS GRP1-1", "PSB-F03, PSB-F04", "UPS"],
            ["DJ04", "C16 2P", "UPS GRP1-2", "K/ML07405 -> ML/B01AM", "UPS"],
            ["DJ05", "C16 2P", "L1-L3", "PSB-F01, PSB-F02", "non-UPS"],
            ["DJ06", "C16 2P", "L2-L3", "K/ML07401-404 -> CP F01/F02", "non-UPS"]]
    table(sh, 28.0, 120.0, [(14, "MCB"), (16, "RATING"), (20, "SUPPLY"), (50, "LOADS"), (16, "")], rows,
          title="BREAKER SCHEDULE")
    sh.notes(160.0, 120.0, [
        "1. Ship supply 230V 3-phase IT (isolated neutral): single-phase",
        "   loads connected line-to-line (L1-L2 / L1-L3 / L2-L3) as per",
        "   A6F41026007 sh.06; all MCBs 2-pole (both lines switched).",
        "2. A6F41026007 sh.05 shows panels fed from DJ05, sh.06 from DJ06:",
        "   DJ06 (L2-L3) adopted. CONFIRM.",
        "3. K/ML07401-404 3G2.5 Mt.150: verify voltage drop / Zs with",
        "   actual connection-panel loads (16A not achievable at 4%).",
        "4. UPS GRP1-1/1-2 IEC C13 outlets used with C14 cords to TBA2.",
        "5. All PE terminals earthed on DIN rail to PE-F01 bar.",
        "6. Internal wiring LSZH; ferrules on all stranded conductors.",
    ])
    sh.legend(420.0, 120.0, [("W-POWER", "230V AC"), ("W-PE", "PE / EARTH"),
                                                 ("W-LESNET", "LES-NET"), ("AV-RACK", "RACK LIMIT")],
              title="LINE TYPES")
    legend_symbols(sh, 560.0, 120.0)
    return sh


if __name__ == "__main__":
    build().save("/tmp/s04.dxf")
