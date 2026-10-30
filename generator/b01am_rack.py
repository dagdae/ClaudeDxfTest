"""ML/B01AM (ATRIUM rack) - rack wiring of the system 07 interfaces, single A1 sheet.

Only the terminations of system 07 cables are shown; equipment and internal wiring of
ML/B01AM are defined on drawing 006376A6F41026002 (continuations shown as diamonds).
"""
from common import INT_CAT6A, info, legend_symbols, rec, table
from engine import Pin, Sheet

DRW = "07BRW01"
REF002 = "DWG 006376A6F41026002"
FX_L = 58.0
FX_R = 760.0


def build():
    sh = Sheet(DRW, "01", "RACK WIRING ML-B01AM")
    sh.frame(info(DRW, "01 / 01", ["L.E.S. RACK WIRING DIAGRAM", "RACK ML/B01AM (ATRIUM)",
                                   "INTERFACES OF SYSTEM 07 - CREW & OFFICER MESS"],
                  area=["07 - CREW & OFFICER MESS", "ML/B01AM - DK04 FR149 SB", "CABINET (ATRIUM)"]))
    sh.rack_boundary(150.0, 150.0, 600.0, 572.0, "ML/B01AM", "ATRIUM",
                     "SYSTEM 07 INTERFACES ONLY - INTERNAL WIRING: " + REF002)

    # ------------------------------------------------------------------ RF bulkheads
    icp = sh.device(135.0, 530.0, 30.0, "RF BULKHEAD", "BNC F/F 50 OHM", "", "",
                    left=[dict(id="L1", label="#1", conn="BNC", g="M"), dict(id="L2", label="#2", conn="BNC", g="M")],
                    right=[dict(id="R1", label="#1", conn="BNC", g="M"), dict(id="R2", label="#2", conn="BNC", g="M")],
                    header=4.0, pad=2.0, title_h=1.8, tag_lines=["INTERCONNECT PANEL", "ICP1"])
    ants = [("ML*864AN-F01", "PAX EMB. Dk3 PS", "DK03 FR208 PS", "K/ML07201", "Mt.16", "L1", "R1", "A"),
            ("ML*864AN-F02", "PAX EMB. Dk3 SB", "DK03 FR208 SB", "K/ML07202", "Mt.28", "L2", "R2", "B")]
    for k, (tag, loc, pos, kno, mt, lp, rp, ant) in enumerate(ants):
        pin = icp[lp].p
        yf = pin.y + (6.0 if k == 0 else -6.0)
        sh.cable(Pin(FX_L, yf, 1), pin, None, "W-RF", via=[(112.0, yf), (112.0, pin.y)],
                 rec=rec(sh, kno, kno, "RG8/U BELDEN 7810SB (50 ohm)", tag, "RF OUT (UA864LO)", "BNC M (7810 crimp)",
                         "ML/B01AM", f"ICP1 #{k + 1}", "BNC M (7810 crimp)", "coax + braid", mt.replace("Mt.", "") + " m",
                         "RF UHF", "Active antenna, DC bias via coax from RF distribution (dwg 002)"))
        sh.field_end(FX_L, yf, "L", ["ACTIVE ANTENNA SHURE UA864LO", tag, f"{loc} - {pos}"],
                     f"{kno}  RG8/U BELDEN 7810SB", f"FROM {tag}  {mt}")
        lb = f"ICP1-{k + 1}/ATR.RF-ANT.IN.{ant}"
        p = icp[rp].p
        sh.cable(p, Pin(260.0, p.y, -1), lb, "W-RF",
                 rec=rec(sh, lb, "", "RG58 LL BNC/BNC 50 ohm", "ICP1", f"#{k + 1} REAR", "BNC M", "ATRIUM RF SYSTEM",
                         f"ANTENNA IN {ant} ({REF002})", "BNC M", "coax", "1.0 m", "RF UHF",
                         "Destination port per ATRIUM drawing"))
        sh.xref(Pin(260.0, p.y, 1), "002", ["ATRIUM WIRELESS SYSTEM", f"ANTENNA IN {ant}"], lead=0.0)

    # ------------------------------------------------------------------ network
    nets = [("ML*F01CP-F01", "LES-NET 1", "K/ML07303", "Mt.14", "LES-NET", "CONNECTION PANEL", "PAX EMB. Dk3 PS"),
            ("ML*F01CP-F01", "LES-NET 2", "K/ML07304", "Mt.14", "LES-NET", "CONNECTION PANEL", "PAX EMB. Dk3 PS"),
            ("ML*070TP-F03", "LAN PoE", "K/ML07305", "Mt.14", "QLAN-A", '7" TOUCH PANEL QSC TSC-70-G3',
             "PAX EMB. Dk3 PS"),
            ("ML*F02CP-F01", "LES-NET 1", "K/ML07306", "Mt.26", "LES-NET", "CONNECTION PANEL", "PAX EMB. Dk3 SB"),
            ("ML*F02CP-F01", "LES-NET 2", "K/ML07307", "Mt.26", "LES-NET", "CONNECTION PANEL", "PAX EMB. Dk3 SB"),
            ("ML*070TP-F04", "LAN PoE", "K/ML07308", "Mt.26", "QLAN-A", '7" TOUCH PANEL QSC TSC-70-G3',
             "PAX EMB. Dk3 SB")]
    lay = {"LES-NET": "W-LESNET", "QLAN-A": "W-QLAN"}
    npb = sh.device(300.0, 470.0, 26.0, "NETPATCH ATRIUM", "CAT6A STP", "NETPATCH (ATRIUM)", "NPB-B01",
                    left=[dict(id=f"L{i}", label=f"T{i}", conn="IDC", g="") for i in range(1, 7)],
                    right=[dict(id=f"R{i}", label=f"T{i}", conn="RJ45", g="M") for i in range(1, 7)],
                    header=8.0, pad=3.0, title_h=1.8, partial=True, icon="net", spacing=9.0)
    for i, (dev, port, kno, mt, vlan, kind, loc) in enumerate(nets, start=1):
        pin = npb[f"L{i}"].p
        conn = "IDC keystone (panel rear)" if "CP" in dev else "RJ45 M (field plug)"
        sh.cable(Pin(FX_L, pin.y, 1), pin, None, lay[vlan],
                 rec=rec(sh, kno, kno, "CAT6A U/FTP BELDEN 10GXE03", dev, port, conn, "ML/B01AM", f"NPB-B01 T{i}",
                         "IDC keystone", "4x2 + drain T568B", mt.replace("Mt.", "") + " m", vlan,
                         f"NPB-B01 port to be assigned on {REF002}"))
        sh.field_end(FX_L, pin.y, "L", [kind, f"{dev} {port}", loc], f"{kno}  CAT6A U/FTP BELDEN 10GXE03",
                     f"FROM {dev}  {mt}")
        lb = f"NPB.B01-T{i}/ATR.NSW-{vlan}"
        p = npb[f"R{i}"].p
        sh.cable(p, Pin(410.0, p.y, -1), lb, lay[vlan],
                 rec=rec(sh, lb, "", INT_CAT6A, "NPB-B01", f"T{i} FRONT", "RJ45 M", "ATRIUM NETSWITCH",
                         f"{vlan} access port ({REF002})", "RJ45 M", "4x2 T568B", "0.5 m", vlan,
                         "PoE 802.3at" if "TP" in dev else ""))
        sh.xref(Pin(410.0, p.y, 1), "002", [f"ATRIUM NETSWITCH - {vlan}", "PoE 802.3at" if "TP" in dev else ""],
                lead=0.0)

    # ------------------------------------------------------------------ from ML/F01AM (right side)
    tb1 = sh.terminal_block(593.0, 312.0, "TB1", [dict(id="01", levels=3), dict(id="02", levels=3, gap=2.0),
                                                  dict(id="03", pe=True, gap=2.0)], sec="2.5")
    A = [p[1] for p in tb1["01"]] + [p[1] for p in tb1["02"]] + [tb1["03"][1]]
    yt = (A[0].y + A[-1].y) / 2
    sh.cable(A, Pin(FX_R, yt, -1), None, "W-AUDIO", names_a=["P1+", "P1-", "S1", "P2+", "P2-", "S2", "CS"],
             cut_a={2, 5, 6}, ytrunk_a=yt)
    sh.field_end(FX_R, yt, "R", ["AUDIO TO CREW MESS", "LES RACK ML/F01AM", "TB1 01-03 (07FRW01)"],
                 "K/ML07101  2x2x0.75 HF-TXISCS", "FROM/TO ML/F01AM  Mt.160")
    sh.text("screens isolated here (earthed at ML/F01AM)", 612.0, A[-1].y - 3.0, 1.1, "TL", "AV-NOTE")
    lb = "ATR.AUDIO-OUT/TB1-01"
    B = [p[0] for p in tb1["01"]] + [p[0] for p in tb1["02"]]
    sh.cable(Pin(500.0, (B[0].y + B[-1].y) / 2, 1), B, lb, "W-AUDIO", names_b=["+", "-", "S", "+", "-", "S"],
             cut_b={2, 5},
             rec=rec(sh, lb, "", "2x 1x2x0.25 SCREENED LSZH", "ATRIUM AUDIO SOURCE", f"OUT 1/2 ({REF002})",
                     "per source", "TB1", "01-02 (3 levels)", "TERM. 3-LEVEL", "+/-/S x2", "1.5 m", "AUDIO",
                     "Feeds DSP-F01 FLEX IN 1/2 in ML/F01AM. Source assignment on dwg 002"))
    sh.xref(Pin(500.0, (B[0].y + B[-1].y) / 2, -1), "002", ["ATRIUM AUDIO OUT 1/2", "(source per dwg 002)"],
            lead=0.0)

    tba = sh.terminal_block(593.0, 238.0, "TBA1", [dict(id="01", sec="6"), dict(id="02", sec="6"),
                                                   dict(id="03", pe=True, sec="6")], sec="6")
    A = [tba[i][1] for i in ("01", "02", "03")]
    sh.cable(A, Pin(FX_R, A[1].y, -1), None, "W-POWER", names_a=["L", "N", "PE"])
    sh.field_end(FX_R, A[1].y, "R", ["230V UPS FEED", "FROM ML/F01AM DJ04", "TBA1 70-72 (07FRW01)"],
                 "K/ML07405  3G6 HF-P", "FROM ML/F01AM  Mt.160")
    lb = "TBA1-01/ATR.PWR-IN"
    B = [tba[i][0] for i in ("01", "02", "03")]
    sh.cable(B, Pin(500.0, B[1].y, 1), lb, "W-POWER", names_a=["L", "N", "PE"],
             rec=rec(sh, lb, "", "3G2.5 LSZH", "TBA1", "01-03", "TERM. 1-LEVEL", "ATRIUM POWER DISTRIBUTION",
                     f"UPS FEED IN ({REF002})", "TERM.", "L N PE", "1.0 m", "230V UPS", ""))
    sh.xref(Pin(500.0, B[1].y, -1), "002", ["ATRIUM DISTRIBUTION", "230V UPS FEED"], lead=0.0)

    # ------------------------------------------------------------------ notes
    rows = [["ICP1 #1", "K/ML07201", "ML*864AN-F01", "RF", "ANT IN A (dwg 002)"],
            ["ICP1 #2", "K/ML07202", "ML*864AN-F02", "RF", "ANT IN B (dwg 002)"]]
    for i, (dev, port, kno, mt, vlan, kind, loc) in enumerate(nets, start=1):
        rows.append([f"NPB-B01 T{i}", kno, f"{dev} {port}", vlan, "NSW ATRIUM (dwg 002)"])
    rows += [["TB1 01-03", "K/ML07101", "ML/F01AM TB1", "AUDIO", "AUDIO OUT 1/2 (dwg 002)"],
             ["TBA1 01-03", "K/ML07405", "ML/F01AM DJ04", "230V UPS", "DISTRIBUTION (dwg 002)"]]
    table(sh, 612.0, 566.0, [(22, "TERMINATION"), (19, "CABLE"), (42, "FIELD / ORIGIN"), (17, "SIGNAL"),
                             (38, "INTERNAL DESTINATION")], rows, title="INTERFACE LIST ML/B01AM", h=1.35, rh=3.9)
    sh.notes(612.0, 500.0, [
        "1. Only the terminations of system 07 cables are shown; equipment",
        "   and internal wiring of ML/B01AM: " + REF002 + ".",
        "2. T1...T6 = NPB-B01 spare ports to be allocated on dwg 002.",
        "   VLAN: LES-NET connection panels, QLAN-A + PoE TSC-70-G3.",
        "3. RG8/U 7810SB: 7810-type BNC crimp plugs both ends.",
        "4. TB1: 3-level signal terminals; TBA1: 1-level power terminals.",
        "5. A6F41026007 sh.03 K/ML07408 read as K/ML07308.",
        "6. CP panel 230V outlets fed from ML/F01AM DJ06 (07FRW01).",
    ])
    legend_symbols(sh, 612.0, 470.0)
    sh.legend(612.0, 412.0, [("W-RF", "RF COAX 50 OHM"), ("W-LESNET", "LES-NET"), ("W-QLAN", "Q-LAN (QLAN-A)"),
                             ("W-AUDIO", "BALANCED AUDIO"), ("W-POWER", "230V AC"), ("AV-RACK", "RACK LIMIT")],
              title="LINE TYPES")
    return sh


if __name__ == "__main__":
    build().save("/tmp/b01.dxf")
