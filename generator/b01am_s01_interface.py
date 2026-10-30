"""ML/B01AM (ATRIUM rack) - interface sheet for system 07 cables."""
from common import INT_CAT6A, info, legend_symbols, rec, table
from engine import PIN, Pin, Sheet

DRW = "07BRW01"
REF002 = "DWG 006376A6F41026002"


def build():
    sh = Sheet(DRW, "01", "INTERFACES")
    sh.frame(info(DRW, "01 / 01", ["L.E.S. WIRING DIAGRAM", "RACK ML/B01AM (ATRIUM)",
                                   "INTERFACES OF SYSTEM 07 - CREW & OFFICER MESS"],
                  area=["07 - CREW & OFFICER MESS", "ML/B01AM - DK04 FR149 SB", "CABINET (ATRIUM)"]))
    sh.rack_boundary(300.0, 150.0, 600.0, 572.0, "ML/B01AM", "ATRIUM",
                     "INTERFACES OF SYSTEM 07 ONLY - INTERNAL WIRING: " + REF002)

    # ------------------------------------------------------------------ RF
    icp = sh.device(285.0, 538.0, 30.0, "RF BULKHEAD", "BNC F/F 50 OHM", "ICP-B01", "",
                    left=[dict(id="L1", label="#1", conn="BNC", g="M"), dict(id="L2", label="#2", conn="BNC", g="M")],
                    right=[dict(id="R1", label="#1", conn="BNC", g="M"), dict(id="R2", label="#2", conn="BNC", g="M")],
                    header=4.0, pad=2.0, title_h=1.8, tag_lines=["INTERCONNECT PANEL", "ICP-B01"])
    ants = [("ML*864AN-F01", "PAX EMB. Dk3 PS", "DK03 FR208 PS", "K/ML07201", "Mt.16", "L1", "R1", "ANT.A"),
            ("ML*864AN-F02", "PAX EMB. Dk3 SB", "DK03 FR208 SB", "K/ML07202", "Mt.28", "L2", "R2", "ANT.B")]
    for k, (tag, loc, pos, kno, mt, lp, rp, ant) in enumerate(ants):
        a = sh.device(40.0, 562.0 - k * 42.0, 40.0, "SHURE", "UA864LO ACTIVE ANTENNA", loc, tag,
                      right=[dict(id="RF", label="RF OUT (BNC F)", conn="BNC", g="M")], icon="antenna",
                      header=10.0, pad=3.0, title_h=1.8, note="+12VDC via coax")
        sh.text(pos, 60.0, a["_box"].pins[0].y - 8.0, 1.3, "TC", "AV-NOTE")
        sh.cable(a["RF"].p, icp[lp].p, None, "W-RF", xm=200.0 + k * 6.0,
                 info=(f"{kno}  RG8/U BELDEN 7810SB", f"{mt} - FROM {tag}"), info_at=(210.0, icp[lp].p.y, "L"),
                 rec=rec(sh, kno, kno, "RG8/U BELDEN 7810SB (50 ohm)", tag, "RF OUT", "BNC M (7810 crimp)", "ML/B01AM",
                         f"ICP-B01 #{k + 1}", "BNC M (7810 crimp)", "coax + braid", mt.replace("Mt.", "") + " m",
                         "RF UHF", "Active antenna DC bias from receiver/distribution (dwg 002)"))
        lbl = f"ICP.B01-{k + 1}/ATR.RF-{ant}"
        pin = icp[rp].p
        sh.cable(pin, Pin(400.0, pin.y, -1), lbl, "W-RF",
                 rec=rec(sh, lbl, "", "RG58 LL / BNC-BNC 50 ohm", "ICP-B01", f"#{k + 1} REAR", "BNC M",
                         "ATRIUM RF SYSTEM", f"ANTENNA IN {ant[-1]} ({REF002})", "BNC M", "coax", "1.0 m", "RF UHF",
                         "Destination port per ATRIUM drawing"))
        sh.xref(Pin(400.0, pin.y, 1), "002", ["ATRIUM WIRELESS SYSTEM", f"ANTENNA IN {ant[-1]}"], lead=0.0)

    # ---------------------------------------------------------------- network
    nets = [("ML*F01CP-F01", "LES-NET 1", "K/ML07303", "Mt.14", "LES-NET"),
            ("ML*F01CP-F01", "LES-NET 2", "K/ML07304", "Mt.14", "LES-NET"),
            ("ML*070TP-F03", "LAN PoE", "K/ML07305", "Mt.14", "QLAN-A"),
            ("ML*F02CP-F01", "LES-NET 1", "K/ML07306", "Mt.26", "LES-NET"),
            ("ML*F02CP-F01", "LES-NET 2", "K/ML07307", "Mt.26", "LES-NET"),
            ("ML*070TP-F04", "LAN PoE", "K/ML07308", "Mt.26", "QLAN-A")]
    npb = sh.device(285.0, 452.0, 30.0, "NETPATCH ATRIUM", "CAT6A STP", "NETPATCH (ATRIUM)", "NPB-B01",
                    left=[dict(id=f"L{i}", label=f"T{i}", conn="IDC", g="") for i in range(1, 7)],
                    right=[dict(id=f"R{i}", label=f"T{i}", conn="RJ45", g="M") for i in range(1, 7)],
                    header=8.0, pad=3.0, title_h=1.8, partial=True, icon="net")
    lay = {"LES-NET": "W-LESNET", "QLAN-A": "W-QLAN"}
    # field devices
    cp1 = sh.device(40.0, 470.0, 46.0, "VIDELIO", "CONNECTION PANEL", "PAX EMB. Dk3 PS - DK03 FR206 PS", "ML*F01CP-F01",
                    right=[dict(id="LES-NET 1", label="LES-NET 1 (rear IDC)", conn="IDC", g=""),
                           dict(id="LES-NET 2", label="LES-NET 2 (rear IDC)", conn="IDC", g=""),
                           dict(id="P1", label="SCHUKO 1 <- PWR IN 1"), dict(id="P2", label="SCHUKO 2 <- PWR IN 2")],
                    icon="panel", header=10.0, pad=3.0, title_h=1.8, note="front: 2x RJ45 F + 2x SCHUKO")
    tp3 = sh.device(40.0, 404.0, 46.0, "QSC", "TSC-70-G3", '7" TOUCH PANEL - DK03 FR206 PS', "ML*070TP-F03",
                    right=[dict(id="LAN PoE", label="LAN PoE", conn="RJ45", g="M"), dict(id="USB", label="USB")],
                    icon="touch", header=10.0, pad=3.0, title_h=1.8, note="PAX EMB. Dk3 PS")
    cp2 = sh.device(40.0, 346.0, 46.0, "VIDELIO", "CONNECTION PANEL", "PAX EMB. Dk3 SB - DK03 FR206 SB", "ML*F02CP-F01",
                    right=[dict(id="LES-NET 1", label="LES-NET 1 (rear IDC)", conn="IDC", g=""),
                           dict(id="LES-NET 2", label="LES-NET 2 (rear IDC)", conn="IDC", g=""),
                           dict(id="P1", label="SCHUKO 1 <- PWR IN 1"), dict(id="P2", label="SCHUKO 2 <- PWR IN 2")],
                    icon="panel", header=10.0, pad=3.0, title_h=1.8, note="front: 2x RJ45 F + 2x SCHUKO")
    tp4 = sh.device(40.0, 280.0, 46.0, "QSC", "TSC-70-G3", '7" TOUCH PANEL - DK03 FR206 SB', "ML*070TP-F04",
                    right=[dict(id="LAN PoE", label="LAN PoE", conn="RJ45", g="M"), dict(id="USB", label="USB")],
                    icon="touch", header=10.0, pad=3.0, title_h=1.8, note="PAX EMB. Dk3 SB")
    devs = {"ML*F01CP-F01": cp1, "ML*070TP-F03": tp3, "ML*F02CP-F01": cp2, "ML*070TP-F04": tp4}
    for d in (tp3, tp4):
        sh.text("n.c.", d["USB"].p.x + 2.6, d["USB"].p.y, 1.1, "ML", "AV-NOTE")
    for cp in (cp1, cp2):
        for pid in ("P1", "P2"):
            sh.xref(cp[pid].p, "04", ["07FRW01: K/ML0740x 3G2.5", "from ML/F01AM DJ06"], wire_layer="W-POWER")
    XV = [150.0, 156.0, 162.0, 168.0, 174.0, 180.0]
    for i, (dev, port, kno, mt, vlan) in enumerate(nets, start=1):
        src = devs[dev][port].p
        dst = npb[f"L{i}"].p
        conn = "IDC keystone" if "CP" in dev else "RJ45 M (field plug)"
        sh.cable(src, dst, None, lay[vlan], via=[(XV[i - 1], src.y), (XV[i - 1], dst.y)],
                 info=(f"{kno}  CAT6A U/FTP 10GXE03", f"{mt} - FROM {dev}"), info_at=(196.0, dst.y, "L"),
                 rec=rec(sh, kno, kno, "CAT6A U/FTP BELDEN 10GXE03", dev, port, conn, "ML/B01AM", f"NPB-B01 T{i}",
                         "IDC keystone", "4x2 + drain T568B", mt.replace("Mt.", "") + " m", vlan,
                         f"Port of NPB-B01 to be assigned on {REF002}"))
        lbl = f"NPB.B01-T{i}/ATR.NSW-{vlan}"
        pin = npb[f"R{i}"].p
        sh.cable(pin, Pin(410.0, pin.y, -1), lbl, lay[vlan],
                 rec=rec(sh, lbl, "", INT_CAT6A, "NPB-B01", f"T{i} FRONT", "RJ45 M", "ATRIUM NETSWITCH",
                         f"{vlan} access port ({REF002})", "RJ45 M", "4x2 T568B", "0.5 m", vlan, "PoE if touch panel"))
        sh.xref(Pin(410.0, pin.y, 1), "002", [f"ATRIUM NETSWITCH - {vlan}", "PoE 802.3at" if "TP" in dev else ""],
                lead=0.0)

    # ------------------------------------------------------- from ML/F01AM (right side)
    tbb = sh.terminal_block(593.0, 300.0, "TB-B01", [dict(id="01", note=None), dict(id="02"), dict(id="03"),
                                                     dict(id="04")], sec="2.5")
    virt = [Pin(tbb["04"][1].x, tbb["04"][1].y - PIN * (j + 1), 1, "") for j in range(3)]
    sh.cable([tbb[i][1] for i in ("01", "02", "03", "04")] + virt, Pin(700.0, 293.0, -1), None, "W-AUDIO",
             names_a=["P1+", "P1-", "P2+", "P2-", "S1", "S2", "CS"], cut_a={4, 5, 6}, ytrunk_a=293.0,
             info=("K/ML07101  2x2x0.75 HF-TXISCS", "Mt.160 - TO ML/F01AM TB1"), info_at=(630.0, 293.0, "L"))
    sh.xref(Pin(700.0, 293.0, 1), "01", ["07FRW01: ML/F01AM TB1 01-07", "DSP-F01 FLEX IN 1/2"], lead=0.0)
    sh.text("screens isolated (earthed at ML/F01AM side)", 612.0, virt[-1].y - 2.2, 1.1, "TL", "AV-NOTE")
    lbl = "ATR.AUDIO-OUT/TB-B01-01"
    sh.cable(Pin(520.0, 295.5, 1), [tbb[i][0] for i in ("01", "02", "03", "04")], lbl, "W-AUDIO",
             names_b=["1+", "1-", "2+", "2-"],
             rec=rec(sh, lbl, "", "2x 1x2x0.25 SCREENED LSZH", "ATRIUM AUDIO SOURCE", f"OUT 1/2 ({REF002})",
                     "per source", "TB-B01", "01-04", "TERM.", "+/- x2", "1.5 m", "AUDIO",
                     "Feeds DSP-F01 FLEX 1/2 (sheet 07FRW01-01). Source assignment on dwg 002"))
    sh.xref(Pin(520.0, 295.5, -1), "002", ["ATRIUM AUDIO OUT 1/2", "(source per dwg 002)"], lead=0.0)

    tba = sh.terminal_block(593.0, 232.0, "TBA-B01", [dict(id="01", sec="6"), dict(id="02", sec="6"),
                                                      dict(id="03", pe=True, sec="6")], sec="6")
    sh.cable([tba[i][1] for i in ("01", "02", "03")], Pin(700.0, 229.0, -1), None, "W-POWER",
             names_a=["L", "N", "PE"], ytrunk_a=229.0,
             info=("K/ML07405  3G6 HF-P", "Mt.160 - FROM ML/F01AM DJ04"), info_at=(630.0, 229.0, "L"))
    sh.xref(Pin(700.0, 229.0, 1), "04", ["07FRW01: ML/F01AM TBA2 13-15", "DJ04 (UPS-F01)"], lead=0.0)
    lbl = "TBA-B01-01/ATR.PWR-IN"
    sh.cable([tba[i][0] for i in ("01", "02", "03")], Pin(520.0, 229.0, 1), lbl, "W-POWER",
             names_a=["L", "N", "PE"],
             rec=rec(sh, lbl, "", "3G2.5 LSZH", "TBA-B01", "01-03", "TERM.", "ATRIUM POWER DISTR.",
                     f"UPS FEED IN ({REF002})", "TERM.", "L N PE", "1.0 m", "230V UPS", ""))
    sh.xref(Pin(520.0, 229.0, -1), "002", ["ATRIUM DISTRIBUTION", "230V UPS FEED"], lead=0.0)

    # ------------------------------------------------------------------ notes
    rows = [["ICP-B01 #1", "K/ML07201", "ML*864AN-F01", "RF", "ANT IN A (dwg 002)"],
            ["ICP-B01 #2", "K/ML07202", "ML*864AN-F02", "RF", "ANT IN B (dwg 002)"]]
    for i, (dev, port, kno, mt, vlan) in enumerate(nets, start=1):
        rows.append([f"NPB-B01 T{i}", kno, f"{dev} {port}", vlan, "NSW ATRIUM (dwg 002)"])
    rows += [["TB-B01 01-04", "K/ML07101", "ML/F01AM TB1", "AUDIO", "AUDIO OUT 1/2 (dwg 002)"],
             ["TBA-B01 01-03", "K/ML07405", "ML/F01AM DJ04", "230V UPS", "DISTRIBUTION (dwg 002)"]]
    table(sh, 610.0, 566.0, [(26, "TERMINATION"), (20, "CABLE"), (40, "FIELD / ORIGIN"), (18, "SIGNAL"),
                             (40, "INTERNAL DESTINATION")], rows, title="INTERFACE LIST ML/B01AM")
    sh.notes(610.0, 500.0, [
        "1. Only the terminations of system 07 cables are shown; equipment and",
        "   internal wiring of ML/B01AM are defined on " + REF002 + ".",
        "2. T1...T6 = NPB-B01 ports to be allocated on dwg 002 (spare ports).",
        "   VLAN: LES-NET for connection panels, QLAN-A + PoE for TSC-70-G3.",
        "3. RG8/U 7810SB terminated with 7810-type BNC crimp plugs both ends;",
        "   active antennas UA864 powered via coax from the RF distribution.",
        "4. A6F41026007 sh.03 shows K/ML07408 for TP-F04: read K/ML07308",
        "   (item list range K/ML07301...K/ML07308).",
        "5. CP panel 230V outlets fed from ML/F01AM DJ06 (sheet 07FRW01-04).",
    ])
    legend_symbols(sh, 610.0, 460.0)
    sh.legend(610.0, 400.0, [("W-RF", "RF COAX 50 OHM"), ("W-LESNET", "LES-NET"), ("W-QLAN", "Q-LAN (QLAN-A)"),
                             ("W-AUDIO", "BALANCED AUDIO"), ("W-POWER", "230V AC"), ("AV-RACK", "RACK LIMIT")],
              title="LINE TYPES")
    return sh


if __name__ == "__main__":
    build().save("/tmp/b01.dxf")
