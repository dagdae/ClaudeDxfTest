"""ML/F01AM - sheet 02: network (Q-LAN / Dante / LES-NET) and fibre uplink."""
from common import INT_CAT6A, INT_LC, info, legend_symbols, rec, table
from engine import PIN, Pin, Sheet

DRW = "07FRW01"

VLAN_LAYER = {"QLAN-A": "W-QLAN", "DANTE": "W-DANTE", "LES-NET": "W-LESNET", "UPLINK": "W-UPLINK"}

# NPB-F01 / NSW-F01 port map (A6F41026007 sheet 07)
PORTS = [
    # port, device, dev port, label code, vlan, kind ('int' xref / 'field'), xref sheet
    (1, "DSP-F01", "LAN A", "DSP.F01-LANA", "QLAN-A", "int", "01"),
    (2, "ML*070TP-F01", "LAN PoE", None, "QLAN-A", "field", None),
    (3, "ML*070TP-F02", "LAN PoE", None, "QLAN-A", "field", None),
    (4, "AMP-F01", "DANTE", "AMP.F01-DANTE", "DANTE", "int", "01"),
    (5, "DSP-F01", "LAN B", "DSP.F01-LANB", "LES-NET", "int", "01"),
    (6, "AMP-F01", "ETHERNET", "AMP.F01-ETH", "LES-NET", "int", "01"),
    (7, "UPS-F01", "ETH", "UPS.F01-ETH", "LES-NET", "int", "04"),
]
TPS = {2: dict(tag="ML*070TP-F01", loc="CREW MESS Dk.4", pos="DK03 FR84 SB", k="K/ML07301", mt="Mt.38"),
       3: dict(tag="ML*070TP-F02", loc="OFFICER MESS Dk.4", pos="DK03 FR52 SB", k="K/ML07302", mt="Mt.22")}

T568B = ["WH/OR", "OR", "WH/GN", "BU", "WH/BU", "GN", "WH/BN", "BN", "DRAIN"]
FIBRE = ["1 BU", "2 OR", "3 GN", "4 BN", "5 SL", "6 WH", "7 RD", "8 BK"]


def touch_panel(sh, x, ytop, tag, loc):
    return sh.device(x, ytop, 36.0, "QSC", "TSC-70-G3", '7" TOUCH PANEL', tag,
                     right=[dict(id="LAN", label="LAN PoE", conn="RJ45", g="M"),
                            dict(id="USB", label="USB")], icon="touch", header=10.0, pad=3.0,
                     note=loc, title_h=1.9)


def build():
    sh = Sheet(DRW, "02", "NETWORK")
    sh.frame(info(DRW, "02 / 04", ["L.E.S. WIRING DIAGRAM", "RACK ML/F01AM",
                                   "NETWORK Q-LAN / DANTE / LES-NET - FIBRE UPLINK"]))
    sh.rack_boundary(150.0, 300.0, 505.0, 572.0, "ML/F01AM", "CREW & OFFICER MESS",
                     "SHEET 02 - NETWORK / FIBRE UPLINK")

    # ------------------------------------------------------------- NETPATCH
    rear, front = [], []
    used = {p[0]: p for p in PORTS}
    for i in range(1, 25):
        if i in used:
            kind = used[i][5]
            rear.append(dict(id=f"P{i:02d}", label=f"{i:02d}", conn="IDC" if kind == "field" else "RJ45",
                             g="" if kind == "field" else "M"))
            front.append(dict(id=f"P{i:02d}", label=f"{i:02d}", conn="RJ45", g="M"))
        else:
            rear.append(dict(id=f"P{i:02d}", label=f"{i:02d}"))
            front.append(dict(id=f"P{i:02d}", label=f"{i:02d}"))
    npb_r = sh.device(330.0, 545.0, 24.0, "NETPATCH", "24P CAT6A STP", "NETPATCH", "NPB-F01", left=rear,
                      right=[], icon="net", header=10.0, pad=4.0)
    # front side ports (same y as rear) drawn on the right edge
    npb_f = {}
    for sp in front:
        yc = npb_r[sp["id"]].y
        sh.text(sp["label"], 330.0 + 24.0 - 1.6, yc, 1.45, "MR", "AV-TEXT")
        if sp.get("conn"):
            npb_f[sp["id"]] = sh.connector(354.0, yc, "R", sp["conn"], sp["g"])[0]
    sh.text("REAR", 331.5, 531.0, 1.2, "ML", "AV-NOTE")
    sh.text("FRONT", 352.5, 531.0, 1.2, "MR", "AV-NOTE")

    # --------------------------------------------------------------- SWITCH
    left = []
    for i in range(1, 25):
        if i in used:
            left.append(dict(id=f"{i}", label=f"#{i}", conn="RJ45", g="M"))
        else:
            left.append(dict(id=f"{i}", label=f"#{i}"))
    for j in range(1, 5):
        if j == 1:
            left.append(dict(id=f"SFP{j}", label=f"#{j} SFP+ (10G SR)", conn="LC-D", g="M"))
        else:
            left.append(dict(id=f"SFP{j}", label=f"#{j} SFP+"))
    nsw = sh.device(420.0, 545.0, 52.0, "HPE ARUBA", "CX 6200F 24G CL4 PoE 4SFP+ (JL725B)", "NETSWITCH", "NSW-F01",
                    left=left, right=[dict(id="CON", label="CONSOLE (RJ45)"), dict(id="CONU", label="CONSOLE (USB-C)"),
                                      dict(id="MGMT", label="MGMT (OOBM)")],
                    icon="net", header=10.0, pad=4.0, bottom=dict(id="PWR", label="230V UPS", conn="IEC C13", g="F"))
    for pid in ("CON", "CONU", "MGMT"):
        sh.text("n.c.", nsw[pid].p.x + 2.6, nsw[pid].p.y, 1.1, "ML", "AV-NOTE")
    sh.xref(nsw["PWR"].p, "04", ["PSB-F03 / OUT 2", "230V UPS"], wire_layer="W-POWER")

    # front patch cords NPB -> NSW
    for (i, dev, dport, code, vlan, kind, xs) in PORTS:
        lay = VLAN_LAYER[vlan]
        lbl = f"NPB.F01-P{i:02d}/NSW.F01-{i:02d}"
        sh.cable(npb_f[f"P{i:02d}"], nsw[f"{i}"].p, lbl, lay,
                 rec=rec(sh, lbl, "", INT_CAT6A, "NPB-F01", f"P{i:02d} FRONT", "RJ45 M", "NSW-F01", f"PORT {i}",
                         "RJ45 M", "4x2 T568B", "0.5 m", vlan, f"{dev} {dport}"))
    # rear: in-rack devices (off-sheet) and field cables
    for (i, dev, dport, code, vlan, kind, xs) in PORTS:
        lay = VLAN_LAYER[vlan]
        pin = npb_r[f"P{i:02d}"].p
        if kind == "int":
            lbl = f"{code}/NPB.F01-P{i:02d}"
            x_end = 252.0
            sh.cable(Pin(x_end, pin.y, 1), pin, lbl, lay, label_at=(290.0, pin.y),
                     rec=rec(sh, lbl, "", INT_CAT6A, dev, dport, "RJ45 M", "NPB-F01", f"P{i:02d} REAR", "RJ45 M",
                             "4x2 T568B", "1.5 m", vlan, "In-rack patch, straight T568B"))
            sh.xref(Pin(x_end, pin.y, -1), xs, [f"{dev} {dport}", vlan])
    # field touch panels
    for i, ytop, xv in ((2, 566.0, 98.0), (3, 470.0, 104.0)):
        t = TPS[i]
        tp = touch_panel(sh, 30.0, ytop, t["tag"], t["loc"])
        sh.text("n.c.", tp["USB"].p.x + 2.6, tp["USB"].p.y, 1.1, "ML", "AV-NOTE")
        sh.mtext_lines([t["pos"]], 48.0, ytop - 37.5, 1.4, "TC")
        pin = npb_r[f"P{i:02d}"].p
        sh.cable(tp["LAN"].p, pin, None, "W-QLAN", via=[(xv, tp["LAN"].p.y), (xv, pin.y)],
                 info=(f"{t['k']}  CAT6A U/FTP BELDEN 10GXE03", f"{t['mt']} - FROM {t['tag']}"),
                 info_at=(xv + 4.0, pin.y, "L"),
                 rec=rec(sh, t["k"], t["k"], "CAT6A U/FTP BELDEN 10GXE03", t["tag"], "LAN PoE", "RJ45 M (field plug)",
                         "NPB-F01", f"P{i:02d} REAR", "IDC keystone", "4x2 + drain T568B (DETAIL A)",
                         t["mt"].replace("Mt.", "") + " m", "QLAN-A", f"{t['loc']} - PoE 802.3at from NSW-F01 port {i}"))

    # ---------------------------------------------------------- FIBRE BOX
    fpb = sh.device(172.0, 372.0, 56.0, "LEVITON", "000-5WMNT-1C", "FIBER BOX", "FPB-F01",
                    left=[dict(id="SPL", label="", conn="SPLICE", g="", pins=[f[:1] for f in FIBRE])],
                    right=[dict(id=f"LC{j}", label=f"{j} A/B", conn="LC-D", g="M") for j in range(1, 5)],
                    icon="fiber", header=10.0, pad=3.0, min_h=28.0)
    spl = fpb["SPL"].pins
    for c, p in enumerate(spl):
        j = c // 2 + 1
        ab = c % 2
        tgt = fpb[f"LC{j}"].p
        ye = tgt.y + (0.8 if ab == 0 else -0.8)
        xb = 172.0
        sh.line((xb, p.y), (xb + 7.0, p.y), "W-FIBER")
        sh.splice(xb + 7.0 + 0.9, p.y, "AV-SYM")
        sh.wire([(xb + 8.8, p.y), (xb + 20.0 + c * 1.2, p.y), (xb + 20.0 + c * 1.2, ye), (xb + 42.0, ye)],
                "W-FIBER")
        sh.dot((xb + 42.0, ye), 0.4, "AV-SYM")
    sh.text("FUSION SPLICE + LC PIGTAIL OM4", 200.0, fpb["_box"].pins[0].y + 2.0, 1.1, "BC", "AV-NOTE")
    fa = list(spl)
    sh.cable(fa, Pin(60.0, 336.0, 1), None, "W-UPLINK", names_a=FIBRE, ytrunk_a=336.0,
             info=("K/ML07501  MM OM4 8 CORE BELDEN GURNE08", "Mt.170 - FROM MDF2 CY*001RK-002"),
             info_at=(62.0, 336.0, "L"),
             rec=rec(sh, "K/ML07501", "K/ML07501", "MM OM4 8 CORE BELDEN GURNE08", "MDF2 CY*001RK-002",
                     "ODF (by others)", "by others", "FPB-F01", "SPLICE 1-8", "fusion splice", "8 fibres OM4",
                     "170 m", "UPLINK", "Cores 1-2 active uplink (LC1), 3-8 spare spliced to LC2-LC4"))
    sh.mtext_lines(["MDF2 - DATA CENTER", "DK08 FR179 PS", "CY*001RK-002", "(BY OTHERS)"], 58.0, 341.0, 1.35, "TR")
    # uplink patch
    lbl = "FPB.F01-1AB/NSW.F01-SFP1"
    sh.cable(fpb["LC1"].p, nsw["SFP1"].p, lbl, "W-UPLINK", via=[(250.0, fpb["LC1"].p.y), (250.0, 318.0),
                                                                (395.0, 318.0), (395.0, nsw["SFP1"].p.y)],
             label_at=(300.0, 318.0),
             rec=rec(sh, lbl, "", INT_LC, "FPB-F01", "LC 1 A/B", "LC-D M", "NSW-F01", "SFP+ #1 (10GBASE-SR)",
                     "LC-D M", "2 fibres OM4 (A-B crossed)", "2.0 m", "UPLINK", "Trunk to ship LAN, all VLANs tagged"))
    for j in (2, 3, 4):
        sh.text("SPARE", fpb[f"LC{j}"].p.x + 2.6, fpb[f"LC{j}"].p.y, 1.1, "ML", "AV-NOTE")

    # ------------------------------------------------------------- tables
    rows = []
    for (i, dev, dport, code, vlan, kind, xs) in PORTS:
        cab = TPS[i]["k"] if kind == "field" else f"{code}/NPB.F01-P{i:02d}"
        poe = "802.3at" if kind == "field" else "OFF"
        rows.append([f"P{i:02d}", f"#{i}", dev, dport, vlan, poe, cab])
    rows.append(["-", "SFP+ #1", "FPB-F01 LC1 A/B", "UPLINK MDF2", "TRUNK (ALL)", "-", "K/ML07501"])
    rows.append(["P08-P24", "#8-#24", "NOT USED", "-", "-", "-", "-"])
    rows.append(["-", "SFP+ #2-#4", "SPARE (FPB LC2-LC4)", "-", "-", "-", "-"])
    table(sh, 515.0, 566.0, [(16, "NPB-F01"), (17, "NSW-F01"), (34, "DEVICE"), (22, "PORT"), (22, "VLAN"),
                             (14, "PoE"), (52, "CABLE")], rows, title="PORT ASSIGNMENT (ref. A6F41026007 sh.07)")
    # VLAN legend
    yv = 506.0
    sh.text("VLAN COLOURS", 515.0, yv, 2.2, "TL", "AV-TEXT")
    for n, (v, lay) in enumerate(VLAN_LAYER.items()):
        sh.line((515.0 + n * 45.0, yv - 6.0), (531.0 + n * 45.0, yv - 6.0), lay)
        sh.text(v, 533.0 + n * 45.0, yv - 6.0, 1.5, "ML", "AV-TEXT")

    # ----------------------------------------------- DETAIL A: T568B termination
    sh.text("DETAIL A - CAT6A U/FTP TERMINATION T568B (K/ML07301, K/ML07302)", 515.0, 488.0, 2.0, "TL", "AV-TEXT")
    ks = sh.device(530.0, 478.0, 30.0, "KEYSTONE CAT6A STP", "NPB-F01 P02/P03 REAR", "IDC KEYSTONE", "(NPB-F01)",
                   right=[dict(id="IDC", label="IDC", conn="IDC", g="", pins=[str(i) for i in range(1, 9)] + ["SH"])],
                   header=6.0, pad=2.0, title_h=1.6, partial=True)
    pl = sh.device(700.0, 478.0, 30.0, "RJ45 PLUG CAT6A STP", "FIELD TERMINABLE", "TOUCH PANEL SIDE", "(TP-F01/F02)",
                   left=[dict(id="RJ", label="PIN", conn="RJ45", g="M", pins=[str(i) for i in range(1, 9)] + ["SH"])],
                   header=6.0, pad=2.0, title_h=1.6, partial=True)
    sh.cable(ks["IDC"].pins, pl["RJ"].pins, "CAT6A U/FTP 4x2xAWG23 + DRAIN", "W-QLAN", names_a=T568B, names_b=T568B,
             label_at=(615.0, None))
    sh.notes(515.0, 432.0, [
        "Pair 1: pins 4-5 BU / WH-BU     Pair 2: pins 1-2 WH-OR / OR",
        "Pair 3: pins 3-6 WH-GN / GN     Pair 4: pins 7-8 WH-BN / BN",
        "Drain + foil bonded to keystone / plug metal shell (360 deg).",
        "Max untwist 6 mm. Test: Cat6A permanent link (TIA-568.2-D), report required.",
    ], title="T568B")

    sh.notes(515.0, 400.0, [
        "1. Field Cat6A cables punched down on shielded IDC keystones (NPB-F01 rear); in-rack devices patched",
        "   with factory CAT6A S/FTP LSZH cords (T568B straight).  Front patch cords NPB-F01 -> NSW-F01 1:1.",
        "2. VLANs as per A6F41026007 sheet 07: ports 1-3 QLAN-A, 4 DANTE, 5-7 LES-NET (access, untagged).",
        "   SFP+ #1 uplink to MDF2: 802.1Q trunk, all VLANs tagged.  IP plan / VLAN IDs by ship IT.",
        "3. PoE 802.3at enabled on ports 2-3 only (QSC TSC-70-G3).  Q-LAN QoS (DSCP) per QSC guidelines.",
        "4. Fibre K/ML07501: 8 x OM4 fusion spliced to LC pigtails (TIA-598 colours); cores 1-2 -> LC1 A/B uplink,",
        "   cores 3-8 spare on LC2-LC4.  A/B polarity crossed on the LC duplex patch (A->B).  OTDR test both ends.",
        "5. Discrepancy found: A6F41026007 sh.06 shows UPS LAN on NPB-F01 P13; sheet 05 / 07 show P07 -> P07 used.",
        "6. Device sheets: DSP-F01 / AMP-F01 = sheet 01, UPS-F01 = sheet 04, touch panels F03/F04 = 07BRW01.",
    ])
    legend_symbols(sh, 515.0, 352.0)
    return sh


if __name__ == "__main__":
    build().save("/tmp/s02.dxf")
