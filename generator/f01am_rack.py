"""ML/F01AM - LES rack executive wiring diagram, single A0 sheet (21xRWxx method).

Terminal blocks:
  TB1  = signals: 3-level terminals for signal cables, 1-level downstream of amplification
  TBA1 = power + muting interface: PAGA 24V out / return under relay on disconnect terminals,
         everything else 1-level
Field equipment is not drawn: field cables are identified by ship number, type and FROM/TO.
"""
from common import (INT_24V, INT_AUDIO, INT_CAT6A, INT_CTRL2, INT_GPIO, INT_LC, INT_PWR, INT_PWR25, INT_SPK,
                    info, legend_symbols, rec, table)
from engine import PIN, Pin, Sheet
from symbols import breaker, led_group, ps_block, relay_coil, relay_contacts

DRW = "07FRW01"
FX_L = 60.0     # field cable end, left side
FX_R = 788.0    # field cable end, right side

ZONES = [
    dict(name="CREW MESS", loc="CREW MESS Dk.4", k="K/ML07601", mt="Mt.27", n=16, first="F01", last="F16",
         rly="RLY-F01", poles=("11", "14", "21", "24"), spare="31-34 / 41-44 SPARE", dsp=5, ch=1, mmb="MMB-F01"),
    dict(name="OFFICER MESS", loc="OFFICER MESS Dk.4", k="K/ML07602", mt="Mt.17", n=16, first="F17", last="F32",
         rly="RLY-F02", poles=("11", "14", "21", "24"), spare="31-34 / 41-44 SPARE", dsp=6, ch=2, mmb="MMB-F02"),
    dict(name="PAX EMBARKATION PS", loc="PAX EMB. Dk3 PS", k="K/ML07603", mt="Mt.140", n=4, first="F33",
         last="F36", rly="RLY-F03", poles=("11", "14", "21", "24"), spare="POLES 1-2 OF 4", dsp=7, ch=3,
         mmb="MMB-F03"),
    dict(name="PAX EMBARKATION SB", loc="PAX EMB. Dk3 SB", k="K/ML07604", mt="Mt.140", n=4, first="F37",
         last="F40", rly="RLY-F03", poles=("31", "34", "41", "44"), spare="POLES 3-4 OF 4", dsp=8, ch=4,
         mmb="MMB-F03"),
]
ROWS = [
    dict(mmb="MMB-F01", zone="CREW MESS", jb="CB/403D", k="K/CB98002", rly="RLY-F01", leds=("LED-F01", "LED-F02"),
         contacts="11-14 / 21-24 CREW MESS line"),
    dict(mmb="MMB-F02", zone="OFFICER MESS", jb="CB/303C", k="K/CB98003", rly="RLY-F02", leds=("LED-F03", "LED-F04"),
         contacts="11-14 / 21-24 OFFICER MESS line"),
    dict(mmb="MMB-F03", zone="PAX EMBARKATION", jb="CB/203B", k="K/CB98001", rly="RLY-F03",
         leds=("LED-F05", "LED-F06"), contacts="11-14/21-24 PS, 31-34/41-44 SB"),
]
VLAN_LAYER = {"QLAN-A": "W-QLAN", "DANTE": "W-DANTE", "LES-NET": "W-LESNET", "UPLINK": "W-UPLINK"}
PORTS = [
    (1, "DSP-F01", "LAN A", "DSP.F01-LANA", "QLAN-A", "int"),
    (2, "ML*070TP-F01", "LAN PoE", None, "QLAN-A", "field"),
    (3, "ML*070TP-F02", "LAN PoE", None, "QLAN-A", "field"),
    (4, "AMP-F01", "DANTE", "AMP.F01-DANTE", "DANTE", "int"),
    (5, "DSP-F01", "LAN B", "DSP.F01-LANB", "LES-NET", "int"),
    (6, "AMP-F01", "ETHERNET", "AMP.F01-ETH", "LES-NET", "int"),
    (7, "UPS-F01", "ETH", "UPS.F01-ETH", "LES-NET", "int"),
]
TPS = {2: dict(tag="ML*070TP-F01", loc="CREW MESS Dk.4", pos="DK03 FR84 SB", k="K/ML07301", mt="Mt.38"),
       3: dict(tag="ML*070TP-F02", loc="OFFICER MESS Dk.4", pos="DK03 FR52 SB", k="K/ML07302", mt="Mt.22")}
T568B = ["WH/OR", "OR", "WH/GN", "BU", "WH/BU", "GN", "WH/BN", "BN", "DRAIN"]
FIBRE = ["1 BU", "2 OR", "3 GN", "4 BN", "5 SL", "6 WH", "7 RD", "8 BK"]


def lbl(dev):
    return dev.replace("-", ".")


# =====================================================================================  AUDIO
def audio(sh: Sheet):
    eb = dict(conn="EB", g="F", pins=["+", "-", "G"])
    dsp = sh.device(250.0, 1125.0, 52.0, "QSC", "CORE 8 FLEX", "AUDIO DSP", "DSP-F01",
                    left=[dict(id="F1", label="FLEX 1 IN", **eb), dict(id="F2", label="FLEX 2 IN", **eb),
                          dict(id="F3", label="FLEX 3 (SPARE)"), dict(id="F4", label="FLEX 4 (SPARE)"),
                          dict(id="GPI", label="GPIO IN", conn="EB", g="F",
                               pins=["+12V", "1", "2", "3", "4", "5", "6", "7", "8", "GND"]),
                          dict(id="GPO", label="GPIO OUT"), dict(id="RSA", label="RS232 A"),
                          dict(id="RSB", label="RS232 B"), dict(id="USBC", label="USB C")],
                    right=[dict(id="F5", label="FLEX 5 OUT", **eb), dict(id="F6", label="FLEX 6 OUT", **eb),
                           dict(id="F7", label="FLEX 7 OUT", **eb), dict(id="F8", label="FLEX 8 OUT", **eb),
                           dict(id="LANA", label="LAN A", conn="RJ45", g="M"),
                           dict(id="LANB", label="LAN B", conn="RJ45", g="M"),
                           dict(id="USBA", label="USB A 1-4"), dict(id="USBB", label="USB B")],
                    icon="dsp", bottom=dict(id="PWR", label="IEC C14 - 230V UPS (PSB-F03/1)"))
    for pid in ("F3", "F4", "GPO", "RSA", "RSB", "USBC", "USBA", "USBB"):
        p = dsp[pid].p
        sh.text("n.c.", p.x + (2.6 if p.d > 0 else -2.6), p.y, 1.1, "ML" if p.d > 0 else "MR", "AV-NOTE")

    # TB1 signal terminals (3-level) - audio from ATRIUM
    y1 = dsp["F1"].y + 4.5
    tb1 = sh.terminal_block(133.0, y1, "TB1", [
        dict(id="01", levels=3),
        dict(id="02", levels=3, gap=2.0),
        dict(id="03", pe=True, gap=2.0)], sec="2.5")
    fa = [p[0] for p in tb1["01"]] + [p[0] for p in tb1["02"]] + [tb1["03"][0]]
    yt = (fa[0].y + fa[-1].y) / 2
    sh.cable(fa, Pin(FX_L, yt, 1), None, "W-AUDIO", names_a=["P1+", "P1-", "S1", "P2+", "P2-", "S2", "CS"],
             ytrunk_a=yt,
             rec=rec(sh, "K/ML07101", "K/ML07101", "2x2x0.75 HF-TXISCS", "ML/B01AM", "TB1 01-03 (07BRW01)",
                     "TERM.", "ML/F01AM", "TB1 01-03", "TERM. 3-LEVEL", "P1(+/-/S1) P2(+/-/S2) CS", "160 m",
                     "AUDIO", "Audio from ATRIUM system. S1/S2 earthed at DSP input only, CS at TB1-03 PE."))
    sh.field_end(FX_L, yt, "L", ["AUDIO FROM ATRIUM", "LES RACK ML/B01AM", "DK04 FR149 SB"],
                 "K/ML07101  2x2x0.75 HF-TXISCS", "FROM/TO ML/B01AM  Mt.160")
    for t, port, n in (("01", "F1", 1), ("02", "F2", 2)):
        A = [p[1] for p in tb1[t]]
        sh.cable(A, dsp[port].pins, f"TB1-{t}/DSP.F01-IN{n}", "W-AUDIO", names_a=["+", "-", "S"],
                 names_b=["+", "-", "S"],
                 rec=rec(sh, f"TB1-{t}/DSP.F01-IN{n}", "", INT_AUDIO, "TB1", f"{t} (3 levels)", "TERM.", "DSP-F01",
                         f"FLEX {n} IN", "EB 3P F", "+ / - / S", "1.5 m", "AUDIO", "Screen to DSP G pin."))
    # DSP GPIO IN -> TB1-04/05 (muting section)
    gp = dsp["GPI"].pins
    sh.cable([gp[1], gp[2], gp[3], gp[9]], Pin(178.0, dsp["GPI"].y, -1), "TB1-04/DSP.F01-GPI", "W-GPIO",
             names_a=["1", "2", "3", "GND"], label_seg=None,
             rec=rec(sh, "TB1-04/DSP.F01-GPI", "", "4x0.5 LSZH", "TB1", "04/05/06 L1 + 04 L2", "TERM. 3-LEVEL",
                     "DSP-F01", "GPIO IN 1/2/3/GND", "EB 10P F", "IN1 IN2 IN3 COM", "2.0 m", "GPIO",
                     "Mute status MMB-F01/F02/F03 (contact closure)"))
    sh.xref(Pin(178.0, dsp["GPI"].y, -1), "G0", ["TB1-04/05/06", "MUTE STATUS"], lead=0.0)
    sh.text("GPIO IN 4-8, +12V : n.c.", gp[9].x - 2.0, gp[9].y - 3.5, 1.1, "TR", "AV-NOTE")

    # ----------------------------------------------------------------- AMP
    px3 = dict(conn="PHX", g="M", pins=["+", "-", "G"])
    px2 = dict(conn="PHX", g="M", pins=["+", "-"])
    amp = sh.device(383.0, 1125.0, 52.0, "POWERSOFT", "QUATTROCANALI 1204 DSP+D", "AMPLIFIER 4x300W", "AMP-F01",
                    left=[dict(id="L1", label="LINE IN 1", **px3), dict(id="L2", label="LINE IN 2", **px3),
                          dict(id="L3", label="LINE IN 3", **px3), dict(id="L4", label="LINE IN 4", **px3),
                          dict(id="LEV", label="REMOTE LEVEL 1-4"), dict(id="RON", label="REM. ON IN"),
                          dict(id="ROFF", label="REM. OFF IN"), dict(id="ALM", label="ALARM"),
                          dict(id="ETH", label="ETHERNET", conn="RJ45", g="M"),
                          dict(id="DAN", label="DANTE", conn="RJ45", g="M")],
                    right=[dict(id="O1", label="OUT CH1", **px2), dict(id="O2", label="OUT CH2", **px2),
                           dict(id="O3", label="OUT CH3", **px2), dict(id="O4", label="OUT CH4", **px2)],
                    icon="amp", bottom=dict(id="PWR", label="IEC C14 - 230V (PSB-F01/1)"))
    for pid in ("LEV", "RON", "ROFF", "ALM"):
        sh.text("n.c.", amp[pid].p.x - 2.6, amp[pid].p.y, 1.1, "MR", "AV-NOTE")
    for z in ZONES:
        n = z["ch"]
        sh.cable(dsp[f"F{z['dsp']}"].pins, amp[f"L{n}"].pins, f"DSP.F01-OUT{z['dsp']}/AMP.F01-IN{n}", "W-AUDIO",
                 names_a=["+", "-", "S"], names_b=["+", "-", "S"], cut_a={2},
                 rec=rec(sh, f"DSP.F01-OUT{z['dsp']}/AMP.F01-IN{n}", "", INT_AUDIO, "DSP-F01",
                         f"FLEX {z['dsp']} OUT", "EB 3P F", "AMP-F01", f"LINE IN {n}", "PHX 3P M", "+ / - / S",
                         "1.0 m", "AUDIO", f"Zone {z['name']}. Screen at AMP G pin only."))
    # network ports of DSP / AMP -> netpatch (reference style diamonds)
    sh.xref(dsp["LANA"].p, "01", ["NETPATCH NPB-F01 - P01", "Q-LAN A"], wire_layer="W-QLAN")
    sh.xref(dsp["LANB"].p, "05", ["NETPATCH NPB-F01 - P05", "LES-NET"], wire_layer="W-LESNET")
    sh.xref(amp["ETH"].p, "06", ["NETPATCH NPB-F01 - P06", "LES-NET"], wire_layer="W-LESNET")
    sh.xref(amp["DAN"].p, "04", ["NETPATCH NPB-F01 - P04", "DANTE"], wire_layer="W-DANTE")

    # --------------------------------------------- relays (contacts) + TB1 1-level speaker terminals
    zc_list = [1110.0, 1084.0, 1058.0, 1032.0]
    XM = {1: 509.0, 2: 515.0, 3: 509.0, 4: 503.0}
    for k, z in enumerate(ZONES):
        zc = zc_list[k]
        n = z["ch"]
        tag = z["rly"] + ("" if n < 3 else (" (1/2)" if n == 3 else " (2/2)"))
        L, R = relay_contacts(sh, 575.0, zc, tag, z["poles"], f"FINDER 55.34 - coil: muting - {z['spare']}")
        sh.cable(amp[f"O{n}"].pins, L, f"AMP.F01-OUT{n}/{lbl(z['rly'])}-COM", "W-SPEAKER", names_a=["+", "-"],
                 names_b=["+", "-"], xm=XM[n], label_at=(474.0, None), ytrunk_b=zc,
                 rec=rec(sh, f"AMP.F01-OUT{n}/{lbl(z['rly'])}-COM", "", INT_SPK, "AMP-F01", f"OUT CH{n}",
                         "PHX 2P M", z["rly"], f"{z['poles'][0]}/{z['poles'][2]} (COM)", "TERM.", "+ / -",
                         "1.5 m", "SPEAKER 100V", f"Zone {z['name']}"))
        ids = [f"{5 * k + i + 6:02d}" for i in range(1, 6)]
        tbs = sh.terminal_block(705.0, zc + 7.5, "TB1" if k == 0 else "", [
            dict(id=ids[0], sec="4"), dict(id=ids[1], sec="4"), dict(id=ids[2], sec="4"),
            dict(id=ids[3], sec="4"), dict(id=ids[4], pe=True, sec="4")], sec="4")
        sh.cable(R, [tbs[ids[0]][0], tbs[ids[1]][0]], f"{lbl(z['rly'])}-NO/TB1-{ids[0]}", "W-SPEAKER",
                 names_a=["+", "-"], names_b=["+", "-"], ytrunk_a=zc, ytrunk_b=zc,
                 rec=rec(sh, f"{lbl(z['rly'])}-NO/TB1-{ids[0]}", "", INT_SPK, z["rly"],
                         f"{z['poles'][1]}/{z['poles'][3]} (NO)", "TERM.", "TB1", f"{ids[0]}-{ids[1]}",
                         "TERM. 1-LEVEL", "+ / -", "1.0 m", "SPEAKER 100V", f"Zone {z['name']}"))
        A = [tbs[i][1] for i in ids]
        sh.cable(A, Pin(FX_R, zc, -1), None, "W-SPEAKER", names_a=["P1+", "P1-", "P2a", "P2b", "S"], ytrunk_a=zc,
                 rec=rec(sh, z["k"], z["k"], "2x2x1.5 HF-TXCS", "ML/F01AM", f"TB1 {ids[0]}-{ids[4]}",
                         "TERM. 1-LEVEL", f"ML*104SP-{z['first']}", "IN 100V", "TERM.", "P1 +/- line, P2 spare, S",
                         z["mt"].replace("Mt.", "") + " m", "SPEAKER 100V",
                         f"{z['loc']}: ML*104SP-{z['first']}...{z['last']} daisy chain. Screen earthed at TB1 PE only."))
        sh.field_end(FX_R, zc, "R", ["CEILING SPEAKERS", f"ML*104SP-{z['first']}...{z['last']}", z["loc"]],
                     f"{z['k']}  2x2x1.5 HF-TXCS", f"TO ML*104SP-{z['first']}  {z['mt']}")
    sh.text("1-LEVEL TERMINALS", 712.5, 1004.0, 1.2, "TC", "AV-NOTE")
    sh.text("(DOWNSTREAM OF AMPLIFICATION)", 712.5, 1001.5, 1.0, "TC", "AV-NOTE")
    sh.text("3-LEVEL SIGNAL TERMINALS", 140.5, tb1["_bottom"] - 1.5, 1.1, "TC", "AV-NOTE")
    return dsp, amp


# =====================================================================================  NETWORK
def network(sh: Sheet):
    rear, front = [], []
    used = {p[0]: p for p in PORTS}
    for i in range(1, 25):
        if i in used:
            kind = used[i][5]
            rear.append(dict(id=f"P{i:02d}", label=f"{i:02d}", conn="IDC" if kind == "field" else "RJ45",
                             g="" if kind == "field" else "M"))
        else:
            rear.append(dict(id=f"P{i:02d}", label=f"{i:02d}"))
    npb = sh.device(345.0, 965.0, 24.0, "NETPATCH", "24P CAT6A STP", "NETPATCH", "NPB-F01", left=rear, right=[],
                    icon="net", header=10.0, pad=4.0, spacing=1.0)
    npb_f = {}
    for i in range(1, 25):
        yc = npb[f"P{i:02d}"].y
        sh.text(f"{i:02d}", 345.0 + 24.0 - 1.6, yc, 1.45, "MR", "AV-TEXT")
        if i in used:
            npb_f[i] = sh.connector(369.0, yc, "R", "RJ45", "M")[0]
    sh.text("REAR", 346.5, 951.0, 1.2, "ML", "AV-NOTE")
    sh.text("FRONT", 367.5, 951.0, 1.2, "MR", "AV-NOTE")
    left = []
    for i in range(1, 25):
        left.append(dict(id=f"{i}", label=f"#{i}", conn="RJ45", g="M") if i in used else dict(id=f"{i}",
                                                                                             label=f"#{i}"))
    for j in range(1, 5):
        left.append(dict(id=f"SFP{j}", label=f"#{j} SFP+ (10G SR)", conn="LC-D", g="M") if j == 1 else
                    dict(id=f"SFP{j}", label=f"#{j} SFP+"))
    nsw = sh.device(440.0, 965.0, 52.0, "HPE ARUBA", "CX 6200F 24G CL4 PoE 4SFP+ (JL725B)", "NETSWITCH", "NSW-F01",
                    left=left, right=[dict(id="CON", label="CONSOLE (RJ45)"), dict(id="CONU", label="CONSOLE (USB-C)"),
                                      dict(id="MGMT", label="MGMT (OOBM)")],
                    icon="net", header=10.0, pad=4.0, spacing=1.0,
                    bottom=dict(id="PWR", label="IEC C14 - 230V UPS (PSB-F03/2)"))
    for pid in ("CON", "CONU", "MGMT"):
        sh.text("n.c.", nsw[pid].p.x + 2.6, nsw[pid].p.y, 1.1, "ML", "AV-NOTE")
    for (i, dev, dport, code, vlan, kind) in PORTS:
        lay = VLAN_LAYER[vlan]
        lb = f"NPB.F01-P{i:02d}/NSW.F01-{i:02d}"
        sh.cable(npb_f[i], nsw[f"{i}"].p, lb, lay,
                 rec=rec(sh, lb, "", INT_CAT6A, "NPB-F01", f"P{i:02d} FRONT", "RJ45 M", "NSW-F01", f"PORT {i}",
                         "RJ45 M", "4x2 T568B", "0.5 m", vlan, f"{dev} {dport}"))
        pin = npb[f"P{i:02d}"].p
        if kind == "int":
            lb = f"{code}/NPB.F01-P{i:02d}"
            sh.cable(Pin(272.0, pin.y, 1), pin, lb, lay, label_at=(304.0, pin.y),
                     rec=rec(sh, lb, "", INT_CAT6A, dev, dport, "RJ45 M", "NPB-F01", f"P{i:02d} REAR", "RJ45 M",
                             "4x2 T568B", "1.5 m", vlan, "In-rack patch, straight T568B"))
            sh.xref(Pin(272.0, pin.y, -1), f"{i:02d}", [f"{dev} - {dport}", vlan], lead=0.0)
        else:
            t = TPS[i]
            yf = pin.y + (5.0 if i == 2 else -5.0)
            sh.cable(Pin(FX_L, yf, 1), pin, None, "W-QLAN", via=[(126.0, yf), (126.0, pin.y)],
                     rec=rec(sh, t["k"], t["k"], "CAT6A U/FTP BELDEN 10GXE03", t["tag"], "LAN PoE",
                             "RJ45 M (field plug T568B)", "NPB-F01", f"P{i:02d} REAR", "IDC keystone",
                             "4x2 + drain T568B", t["mt"].replace("Mt.", "") + " m", "QLAN-A",
                             f"{t['loc']} {t['pos']} - PoE 802.3at from NSW-F01 port {i}"))
            sh.field_end(FX_L, yf, "L", ['7" TOUCH PANEL', t["tag"], t["loc"]],
                         f"{t['k']}  CAT6A U/FTP BELDEN 10GXE03", f"FROM {t['tag']}  {t['mt']}")

    # fibre box
    fpb = sh.device(170.0, 905.0, 56.0, "LEVITON", "000-5WMNT-1C", "FIBER BOX", "FPB-F01",
                    left=[dict(id="SPL", label="", conn="SPLICE", g="", pins=[f[:1] for f in FIBRE])],
                    right=[dict(id=f"LC{j}", label=f"{j} A/B", conn="LC-D", g="M") for j in range(1, 5)],
                    icon="fiber", header=10.0, pad=3.0, min_h=28.0)
    spl = fpb["SPL"].pins
    for c, p in enumerate(spl):
        j = c // 2 + 1
        tgt = fpb[f"LC{j}"].p
        ye = tgt.y + (0.8 if c % 2 == 0 else -0.8)
        xb = 170.0
        sh.line((xb, p.y), (xb + 7.0, p.y), "W-FIBER")
        sh.splice(xb + 7.9, p.y, "AV-SYM")
        sh.wire([(xb + 8.8, p.y), (xb + 20.0 + c * 1.2, p.y), (xb + 20.0 + c * 1.2, ye), (xb + 42.0, ye)], "W-FIBER")
        sh.dot((xb + 42.0, ye), 0.4, "AV-SYM")
    sh.text("FUSION SPLICE + LC PIGTAIL OM4", 198.0, fpb["_box"].pins[0].y + 2.0, 1.1, "BC", "AV-NOTE")
    yt = (spl[0].y + spl[-1].y) / 2
    sh.cable(list(spl), Pin(FX_L, yt, 1), None, "W-UPLINK", names_a=FIBRE, ytrunk_a=yt,
             rec=rec(sh, "K/ML07501", "K/ML07501", "MM OM4 8 CORE BELDEN GURNE08", "MDF2 CY*001RK-002",
                     "ODF (by others)", "by others", "FPB-F01", "SPLICE 1-8", "fusion splice", "8 fibres OM4",
                     "170 m", "UPLINK", "Cores 1-2 uplink on LC1, 3-8 spare on LC2-LC4"))
    sh.field_end(FX_L, yt, "L", ["UPLINK DATA CENTER", "MDF2 CY*001RK-002", "DK08 FR179 PS"],
                 "K/ML07501  MM OM4 8 CORE BELDEN GURNE08", "FROM MDF2 (BY OTHERS)  Mt.170")
    lb = "FPB.F01-1AB/NSW.F01-SFP1"
    sh.cable(fpb["LC1"].p, nsw["SFP1"].p, lb, "W-UPLINK",
             via=[(255.0, fpb["LC1"].p.y), (255.0, 777.0), (425.0, 777.0), (425.0, nsw["SFP1"].p.y)],
             label_at=(330.0, 777.0),
             rec=rec(sh, lb, "", INT_LC, "FPB-F01", "LC 1 A/B", "LC-D M", "NSW-F01", "SFP+ #1 (10GBASE-SR)",
                     "LC-D M", "2 fibres OM4 (A-B crossed)", "2.0 m", "UPLINK", "Trunk to ship LAN, all VLANs tagged"))
    for j in (2, 3, 4):
        sh.text("SPARE", fpb[f"LC{j}"].p.x + 2.6, fpb[f"LC{j}"].p.y, 1.1, "ML", "AV-NOTE")

    # port table + T568B detail
    rows = []
    for (i, dev, dport, code, vlan, kind) in PORTS:
        cab = TPS[i]["k"] if kind == "field" else f"{code}/NPB.F01-P{i:02d}"
        rows.append([f"P{i:02d}", f"#{i}", dev, dport, vlan, "802.3at" if kind == "field" else "OFF", cab])
    rows.append(["-", "SFP+ #1", "FPB-F01 LC1 A/B", "UPLINK MDF2", "TRUNK (ALL)", "-", "K/ML07501"])
    rows.append(["P08-P24", "#8-#24", "NOT USED", "-", "-", "-", "-"])
    table(sh, 520.0, 960.0, [(15, "NPB"), (15, "NSW"), (28, "DEVICE"), (17, "PORT"), (19, "VLAN"),
                             (13, "PoE"), (78, "CABLE")], rows, title="PORT ASSIGNMENT (A6F41026007 sh.07)", h=1.35,
          rh=3.9)
    yv = 912.0
    for n, (v, lay) in enumerate(VLAN_LAYER.items()):
        sh.line((520.0 + n * 46.0, yv), (534.0 + n * 46.0, yv), lay)
        sh.text(v, 536.0 + n * 46.0, yv, 1.4, "ML", "AV-TEXT")
    sh.text("DETAIL A - CAT6A TERMINATION T568B (K/ML07301-302 and all patch cords)", 520.0, 904.0, 1.7, "TL",
            "AV-TEXT")
    ks = sh.device(533.0, 895.0, 30.0, "KEYSTONE CAT6A STP", "NPB-F01 REAR", "IDC KEYSTONE", "",
                   right=[dict(id="IDC", label="IDC", conn="IDC", g="", pins=[str(i) for i in range(1, 9)] + ["SH"])],
                   header=5.0, pad=2.0, title_h=1.5, partial=True, tag_lines=["IDC KEYSTONE"])
    pl = sh.device(668.0, 895.0, 30.0, "RJ45 PLUG CAT6A STP", "FIELD TERMINABLE", "TOUCH PANEL END", "",
                   left=[dict(id="RJ", label="PIN", conn="RJ45", g="M", pins=[str(i) for i in range(1, 9)] + ["SH"])],
                   header=5.0, pad=2.0, title_h=1.5, partial=True, tag_lines=["TOUCH PANEL END"])
    sh.cable(ks["IDC"].pins, pl["RJ"].pins, "CAT6A U/FTP 4x2xAWG23 + DRAIN", "W-QLAN", names_a=T568B,
             names_b=T568B, label_at=(615.5, None))
    return nsw


# =====================================================================================  MUTING
def muting(sh: Sheet):
    tops = [742.0, 652.0, 562.0]
    # PSU + TBA1 24V feed (top right of section)
    psu = sh.device(545.0, 778.0, 46.0, "MEAN WELL", "NDR-120-24 (24VDC 5A DIN)", "MUTE PSU", "PSU-F01",
                    left=[dict(id="AC", label="AC IN", conn="TB", g="", pins=["L", "N", "PE"])],
                    right=[dict(id="DC", label="DC OUT", conn="TB", g="", pins=["+V", "-V"])],
                    icon="psu", header=10.0, pad=3.0, title_h=1.8)
    sh.xref(Pin(psu["AC"].pins[1].x, psu["AC"].pins[1].y, -1), "P1", ["TBA1-37/38/39", "DJ02 L1-L2 (NON-UPS)"],
            wire_layer="W-POWER", lead=6.0)
    feed = sh.terminal_block(660.0, psu["DC"].pins[0].y + 1.5, "TBA1",
                             [dict(id="16", note="+24V"), dict(id="17", note="0V")], sec="2.5")
    sh.cable(psu["DC"].pins, [feed["16"][0], feed["17"][0]], "PSU.F01-OUT/TBA1-16", "W-24VDC", names_a=["+", "-"],
             names_b=["+", "-"],
             rec=rec(sh, "PSU.F01-OUT/TBA1-16", "", INT_24V, "PSU-F01", "DC OUT +V/-V", "TERM.", "TBA1", "16-17",
                     "TERM. 1-LEVEL", "+24V / 0V", "0.5 m", "24VDC", "Jumper bars to all +24V / 0V terminals"))
    comb_p, comb_n = [feed["16"][1]], [feed["17"][1]]

    # TB1-04/05 GPIO common (3-level)
    gtb = sh.terminal_block(585.0, 588.0, "TB1", [
        dict(id="04", levels=3),
        dict(id="05", levels=3, gap=2.0),
        dict(id="06", levels=3, gap=2.0)], sec="1.5")
    # level-2 plug-in bridge (COM)
    yb = [gtb[t][1][0].y for t in ("04", "05", "06")]
    sh.line((585.0 + 13.6, yb[0]), (585.0 + 13.6, yb[-1]), "AV-TB", ltype="AV_HIDDEN")
    for yy in yb:
        sh.dot((585.0 + 13.6, yy), 0.45, "AV-TB")
    sh.text("L2 BRIDGED", 592.5, gtb["_bottom"] - 1.2, 1.0, "TC", "AV-NOTE")
    gpi_out = [gtb["04"][0][1], gtb["04"][1][1], gtb["05"][0][1], gtb["06"][0][1]]
    yo = (gpi_out[0].y + gpi_out[-1].y) / 2
    sh.cable(gpi_out, Pin(626.0, yo, -1), None, "W-GPIO", names_a=["IN1", "COM", "IN2", "IN3"], ytrunk_a=yo)
    sh.xref(Pin(626.0, yo, 1), "G0", ["DSP-F01 GPIO IN"], lead=0.0)

    XV = 640.0
    for r, row in enumerate(ROWS):
        top = tops[r]
        n = r + 1
        mmb = sh.device(225.0, top, 60.0, "VIDELIO", "MASTER BOARD", "PA MASTER", row["mmb"],
                        left=[dict(id="PA", label="PAGA I/F", conn="EB", g="F", pins=["+24V", "MUTE", "EN", "GND"]),
                              dict(id="OV1", label="OVERRIDE 1"), dict(id="OV2", label="OVERRIDE 2"),
                              dict(id="BUS", label="BUS MUTING DB9")],
                        right=[dict(id="LED", label="LED", conn="EB", g="F", pins=["LED"]),
                               dict(id="CH", label="CHAIN OUT", conn="EB", g="F", pins=["OUT+", "OUT-"], gap=12.0),
                               dict(id="PWR", label="POWER 24V", conn="EB", g="F", pins=["+24V", "0V"], gap=14.0),
                               dict(id="DRY", label="DRY DSP", conn="EB", g="F", pins=["D1", "D2"])],
                        icon="mmb", header=10.0, pad=3.0, note=f"*{row['zone']}*", title_h=2.0)
        for pid in ("OV1", "OV2", "BUS"):
            sh.text("n.c.", mmb[pid].p.x - 2.6, mmb[pid].p.y, 1.1, "MR", "AV-NOTE")
        # TBA1 muting interface: 24V out and returns under PA relay on disconnect terminals
        ids = [f"{5 * r + i:02d}" for i in range(1, 6)]
        pa = mmb["PA"].pins
        tba = sh.terminal_block(133.0, pa[0].y + 1.5, "TBA1" if r == 0 else "", [
            dict(id=ids[0], disc=True), dict(id=ids[1], disc=True), dict(id=ids[2], disc=True),
            dict(id=ids[3]), dict(id=ids[4], pe=True)], sec="2.5")
        sh.cable([tba[i][1] for i in ids[:4]], pa, f"TBA1-{ids[0]}/{lbl(row['mmb'])}-PA", "W-GPIO",
                 names_a=["+24V", "MUTE", "EN", "GND"], names_b=["+24V", "MUTE", "EN", "GND"],
                 rec=rec(sh, f"TBA1-{ids[0]}/{lbl(row['mmb'])}-PA", "", INT_GPIO, "TBA1",
                         f"{ids[0]}-{ids[3]}", "TERM. (disconnect 01-03)", row["mmb"], "PAGA I/F", "EB 4P F",
                         "+24V MUTE EN GND", "1.5 m", "GPIO", f"Zone {row['zone']}"))
        A = [tba[i][0] for i in ids]
        yt = (A[0].y + A[-1].y) / 2
        sh.cable(A, Pin(FX_L, yt, 1), None, "W-GPIO", names_a=["+24V", "MUTE", "EN", "GND", "S"], ytrunk_a=yt,
                 rec=rec(sh, row["k"], row["k"], "BY PAGA SUPPLIER (min. 4 cond. screened)", row["jb"],
                         "MUTE I/F", "by others", "ML/F01AM", f"TBA1 {ids[0]}-{ids[4]}", "TERM. (disconnect)",
                         "+24V(to PA) MUTE ENABLE GND + S", "-", "GPIO",
                         f"MUTE FROM PA {row['zone']} - JB/zone match to be confirmed by PAGA supplier"))
        sh.field_end(FX_L, yt, "L", [f"MUTE FROM PA - {row['zone']}", f"PAGA J.BOX {row['jb']}",
                                    "DK2 FR62 SB EL. LOCKER"], f"{row['k']}  (SUPPLIED BY OTHERS)",
                     f"FROM/TO PAGA J.BOX {row['jb']}")
        # relay coil
        ch = mmb["CH"].pins
        rc = relay_coil(sh, 370.0, (ch[0].y + ch[1].y) / 2, row["rly"], row["contacts"])
        sh.cable(ch, rc["COIL"].pins, f"{lbl(row['mmb'])}-OUT/{lbl(row['rly'])}-A1", "W-GPIO",
                 names_a=["+", "-"], names_b=["A1", "A2"],
                 rec=rec(sh, f"{lbl(row['mmb'])}-OUT/{lbl(row['rly'])}-A1", "", INT_CTRL2, row["mmb"],
                         "CHAIN OUT +/-", "EB 2P F", row["rly"], "COIL A1/A2", "TERM. (socket 94.04)", "OUT+ / OUT-",
                         "1.0 m", "GPIO", "Coil energised = audio enabled (fail-safe mute)"))
        # status lamps
        lp = mmb["LED"].pins[0]
        lg = led_group(sh, 430.0, lp.y + 12.5, row["leds"])
        sh.cable(lp, lg["MID"].p, f"{lbl(row['mmb'])}-LED/{lbl(row['leds'][0])}-X2", "W-24VDC",
                 label_at=(335.0, None),
                 rec=rec(sh, f"{lbl(row['mmb'])}-LED/{lbl(row['leds'][0])}-X2", "", "1x1.0 LSZH", row["mmb"], "LED",
                         "EB 1P F", f"{row['leds'][0]}/{row['leds'][1]}", "X2 RD / X1 GN", "TERM.", "1 cond.",
                         "1.5 m", "24VDC", "Status lamps (rack front)"))
        t = [f"{4 * r + i + 17:02d}" for i in range(1, 5)]
        tb4 = sh.terminal_block(660.0, lg["P24"].y + 1.5, "", [
            dict(id=t[0], note="+24V"), dict(id=t[1], note="0V"), dict(id=t[2], note="+24V"),
            dict(id=t[3], note="0V")], sec="1.5")
        sh.cable([tb4[t[0]][0], tb4[t[1]][0]], [lg["P24"].p, lg["P0"].p], f"TBA1-{t[0]}/{lbl(row['leds'][0])}-X1",
                 "W-24VDC", names_a=["+", "-"], names_b=["+", "-"],
                 rec=rec(sh, f"TBA1-{t[0]}/{lbl(row['leds'][0])}-X1", "", INT_24V, "TBA1", f"{t[0]}-{t[1]}",
                         "TERM. 1-LEVEL", f"{row['leds'][0]}/{row['leds'][1]}", "X1 RD / X2 GN", "TERM.",
                         "+24V / 0V", "1.5 m", "24VDC", ""))
        pw = mmb["PWR"].pins
        sh.cable([tb4[t[2]][0], tb4[t[3]][0]], pw, f"TBA1-{t[2]}/{lbl(row['mmb'])}-PWR", "W-24VDC",
                 names_a=["+", "-"], names_b=["+24V", "0V"], xm=XV - 2.0 * r, label_at=(335.0, None),
                 rec=rec(sh, f"TBA1-{t[2]}/{lbl(row['mmb'])}-PWR", "", INT_24V, "TBA1", f"{t[2]}-{t[3]}",
                         "TERM. 1-LEVEL", row["mmb"], "POWER 24V", "EB 2P F", "+24V / 0V", "1.5 m", "24VDC", ""))
        comb_p += [tb4[t[0]][1], tb4[t[2]][1]]
        comb_n += [tb4[t[1]][1], tb4[t[3]][1]]
        # dry contact -> TB1-04/05 (via reference)
        dr = mmb["DRY"].pins
        yd = (dr[0].y + dr[1].y) / 2
        sh.cable(dr, Pin(352.0, yd, -1), f"{lbl(row['mmb'])}-DRY/TB1-{3 + n:02d}", "W-GPIO", names_a=["D1", "D2"],
                 rec=rec(sh, f"{lbl(row['mmb'])}-DRY/TB1-{3 + n:02d}", "", INT_CTRL2, row["mmb"], "DRY DSP", "EB 2P F",
                         "TB1", f"{3 + n:02d} L1 / L2", "TERM. 3-LEVEL", "D1 / D2", "2.0 m", "GPIO",
                         f"Mute status {row['zone']} -> DSP GPIO IN {n}"))
        sh.xref(Pin(352.0, yd, 1), f"G{n}", [f"TB1-{3 + n:02d} L1/L2"], lead=0.0)
        # matching reference at TB1-04/05/06
        tl = gtb[f"{3 + n:02d}"]
        p1, p2 = tl[0][0], tl[1][0]
        sh.cable([p1, p2], Pin(560.0, (p1.y + p2.y) / 2, 1), None, "W-GPIO", names_a=["D1", "D2"])
        sh.xref(Pin(560.0, (p1.y + p2.y) / 2, -1), f"G{n}", [f"{row['mmb']} DRY"], lead=0.0)
    for comb, dx in ((comb_p, 3.0), (comb_n, 6.0)):
        xs = comb[0].x + dx
        ys = [p.y for p in comb]
        sh.line((xs, min(ys)), (xs, max(ys)), "W-24VDC", lw=50)
        for p in comb:
            sh.line((p.x, p.y), (xs, p.y), "W-24VDC")
            sh.dot((xs, p.y), 0.55, "W-24VDC")
    sh.text("JUMPER BARS +24V / 0V", comb_p[0].x + 8.0, comb_p[0].y + 3.0, 1.1, "BL", "AV-NOTE")
    sh.text("DISCONNECT TERMINALS:", 140.5, 484.0, 1.1, "TC", "AV-NOTE")
    sh.text("24V TO PA / MUTE / ENABLE", 140.5, 481.6, 1.1, "TC", "AV-NOTE")


# =====================================================================================  POWER
def power(sh: Sheet):
    tin = sh.terminal_block(133.0, 452.0, "TBA1", [dict(id="30", sec="10"), dict(id="31", sec="10"),
                                                   dict(id="32", sec="10"), dict(id="33", pe=True, sec="10")],
                            sec="10")
    A = [tin[i][0] for i in ("30", "31", "32", "33")]
    yt = (A[0].y + A[-1].y) / 2
    sh.cable(A, Pin(FX_L, yt, 1), None, "W-POWER", names_a=["L1", "L2", "L3", "PE"], ytrunk_a=yt,
             rec=rec(sh, "U/A3A0043AAA", "U/A3A0043AAA", "4x6 HF-P", "FZ/QFUA3A00 (yard switchboard)", "UA31043",
                     "by yard", "ML/F01AM", "TBA1 30-33", "TERM. 10mm2", "L1 L2 L3 PE", "15 m", "230V AC 3PH IT",
                     "Supply by yard"))
    sh.field_end(FX_L, yt, "L", ["YARD SWITCHBOARD", "FZ/QFUA3A00 - UA31043", "220V 3PH (IT)"],
                 "U/A3A0043AAA  4x6 HF-P", "FROM FZ/QFUA3A00  Mt.15")
    i1, o1 = breaker(sh, 205.0, 458.0, "DJ01", ["L1", "L2", "L3"])
    sh.cable([tin[i][1] for i in ("30", "31", "32")], i1, "TBA1-30/DJ01-1", "W-POWER", names_a=["L1", "L2", "L3"],
             names_b=["L1", "L2", "L3"], ytrunk_a=446.0, ytrunk_b=446.0,
             rec=rec(sh, "TBA1-30/DJ01-1", "", "3x H07Z1-K 6mm2 LSZH", "TBA1", "30-32", "TERM.", "DJ01", "1/3/5",
                     "TERM.", "L1 L2 L3", "0.5 m", "230V AC 3PH", "Main switch"))
    BUS = {"L1": 248.0, "L2": 252.0, "L3": 256.0}
    bottoms = {"L1": 310.0, "L2": 234.0, "L3": 228.0}
    for p, ph in zip(o1, ("L1", "L2", "L3")):
        sh.line((p.x, p.y), (BUS[ph], p.y), "W-POWER")
        sh.dot((BUS[ph], p.y), 0.55, "W-POWER")
        sh.line((BUS[ph], p.y), (BUS[ph], bottoms[ph]), "W-POWER", lw=50)
        sh.text(ph, BUS[ph], p.y + 1.5 + (2.0 if ph == "L1" else 0.0), 1.2, "BC", "AV-NOTE")
    sh.text("COMB BUSBAR 3P", 252.0, 462.0, 1.2, "BC", "AV-NOTE")

    def tap(phs, pins):
        for ph, p in zip(phs, pins):
            sh.line((BUS[ph], p.y), (p.x, p.y), "W-POWER")
            sh.dot((BUS[ph], p.y), 0.55, "W-POWER")

    # DJ02 -> UPS-F01 + PSU-F01
    i2, o2 = breaker(sh, 275.0, 428.0, "DJ02", ["L1", "L2"])
    tap(["L1", "L2"], i2)
    sh.text("L1-L2", 268.0, 429.0, 1.4, "BR", "AV-TEXT")
    t2 = sh.terminal_block(368.0, 424.0, "", [dict(id="34"), dict(id="35"), dict(id="36", pe=True),
                                              dict(id="37", gap=2.0), dict(id="38"), dict(id="39", pe=True)])
    sh.tb_bridge([t2["34"][0], t2["37"][0]], off=1.2)
    sh.tb_bridge([t2["35"][0], t2["38"][0]], off=2.6)
    sh.cable(o2, [t2["34"][0], t2["35"][0]], "DJ02-2/TBA1-34", "W-POWER", names_a=["L1", "L2"],
             names_b=["L1", "L2"], ytrunk_a=419.0, ytrunk_b=419.0,
             rec=rec(sh, "DJ02-2/TBA1-34", "", "2x H07Z1-K 2.5mm2 LSZH", "DJ02", "2/4", "TERM.", "TBA1", "34-35",
                     "TERM.", "L1 L2", "0.5 m", "230V AC", "UPS + mute PSU (non-UPS)"))
    ups = sh.device(440.0, 434.0, 54.0, "SOCOMEC", "NRT4-U020B-C", "UPS", "UPS-F01",
                    left=[dict(id="IN", label="AC IN", conn="IEC C13", g="F")],
                    right=[dict(id="G11", label="GRP1-1", conn="IEC C14", g="M"),
                           dict(id="G12", label="GRP1-2", conn="IEC C14", g="M"),
                           dict(id="G13", label="GRP1-3"), dict(id="G14", label="GRP1-4"),
                           dict(id="G2", label="GRP2-1...4"),
                           dict(id="ETH", label="ETH", conn="RJ45", g="M"),
                           dict(id="USB", label="USB"), dict(id="RS", label="RS-232")],
                    icon="ups", header=10.0, pad=3.0)
    for pid in ("G13", "G14", "G2", "USB", "RS"):
        sh.text("n.c.", ups[pid].p.x + 2.6, ups[pid].p.y, 1.1, "ML", "AV-NOTE")
    sh.xref(ups["ETH"].p, "07", ["NETPATCH NPB-F01 - P07", "LES-NET"], wire_layer="W-LESNET")
    sh.cable([t2[i][1] for i in ("34", "35", "36")], ups["IN"].p, "TBA1-34/UPS.F01-IN", "W-POWER",
             names_a=["L1", "L2", "PE"],
             rec=rec(sh, "TBA1-34/UPS.F01-IN", "", INT_PWR, "TBA1", "34-36", "TERM.", "UPS-F01", "AC IN",
                     "IEC C13 F (cord)", "L1 L2 PE", "1.5 m", "230V AC", "DJ02 L1-L2"))
    sh.cable([t2[i][1] for i in ("37", "38", "39")], Pin(410.0, 355.0, 2), "TBA1-37/PSU.F01-AC", "W-POWER",
             names_a=["L1", "L2", "PE"], via=[(410.0, t2["38"][1].y)], pill=False,
             rec=rec(sh, "TBA1-37/PSU.F01-AC", "", INT_PWR, "TBA1", "37-39", "TERM.", "PSU-F01", "AC IN L/N/PE",
                     "TERM.", "L1 L2 PE", "2.0 m", "230V AC", "Mute PSU 24VDC"))
    sh.xref(Pin(410.0, 355.0, -2), "P1", ["TBA1-37/PSU.F01-AC", "PSU-F01 AC IN"], lead=0.0)

    # UPS outputs -> DJ03 / DJ04
    i3, o3 = breaker(sh, 555.0, 428.0, "DJ03", ["L", "N"])
    i4, o4 = breaker(sh, 555.0, 398.0, "DJ04", ["L", "N"])
    sh.cable(ups["G11"].p, i3, "UPS.F01-OUT1/DJ03-1", "W-POWER", names_b=["L", "N"], label_at=(524.0, None),
             rec=rec(sh, "UPS.F01-OUT1/DJ03-1", "", INT_PWR, "UPS-F01", "GRP1-1", "IEC C14 M (cord)", "DJ03",
                     "1/3", "TERM.", "L N (PE to TBA1 PE)", "1.0 m", "230V UPS", ""))
    sh.cable(ups["G12"].p, i4, "UPS.F01-OUT2/DJ04-1", "W-POWER", names_b=["L", "N"], label_at=(524.0, None),
             xm=542.0,
             rec=rec(sh, "UPS.F01-OUT2/DJ04-1", "", INT_PWR, "UPS-F01", "GRP1-2", "IEC C14 M (cord)", "DJ04",
                     "1/3", "TERM.", "L N (PE to TBA1 PE)", "1.0 m", "230V UPS", ""))
    tb3 = sh.terminal_block(632.0, 433.0, "", [dict(id="64"), dict(id="65"), dict(id="66", pe=True),
                                               dict(id="67", gap=2.0), dict(id="68"), dict(id="69", pe=True)])
    sh.tb_bridge([tb3["64"][0], tb3["67"][0]], off=1.2)
    sh.tb_bridge([tb3["65"][0], tb3["68"][0]], off=2.6)
    sh.cable(o3, [tb3["64"][0], tb3["65"][0]], "DJ03-2/TBA1-64", "W-POWER", names_a=["L", "N"], names_b=["L", "N"],
             ytrunk_a=424.0, ytrunk_b=424.0, pill=False,
             rec=rec(sh, "DJ03-2/TBA1-64", "", "2x H07Z1-K 2.5mm2 LSZH", "DJ03", "2/4", "TERM.", "TBA1", "64-65",
                     "TERM.", "L N", "0.3 m", "230V UPS", "PSB-F03 / PSB-F04"))
    sh.text("DJ03-2/TBA1-64", 608.0, 426.0, 1.3, "BC", "AV-TEXT")
    tb4 = sh.terminal_block(705.0, 401.0, "TBA1", [dict(id="70", sec="6"), dict(id="71", sec="6"),
                                                   dict(id="72", pe=True, sec="6")], sec="6")
    sh.cable(o4, [tb4["70"][0], tb4["71"][0]], "DJ04-2/TBA1-70", "W-POWER", names_a=["L", "N"], names_b=["L", "N"],
             rec=rec(sh, "DJ04-2/TBA1-70", "", "2x H07Z1-K 6mm2 LSZH", "DJ04", "2/4", "TERM.", "TBA1", "70-71",
                     "TERM.", "L N", "0.5 m", "230V UPS", "Feeder to ML/B01AM"))
    A = [tb4[i][1] for i in ("70", "71", "72")]
    sh.cable(A, Pin(FX_R, A[1].y, -1), None, "W-POWER", names_a=["L", "N", "PE"],
             rec=rec(sh, "K/ML07405", "K/ML07405", "3G6 HF-P", "ML/F01AM", "TBA1 70-72", "TERM.", "ML/B01AM",
                     "TBA1 01-03 (07BRW01)", "TERM.", "L N PE", "160 m", "230V UPS",
                     "POWER TO ATRIUM, CRYSTAL COVE via DJ04 C16 (UPS)"))
    sh.field_end(FX_R, A[1].y, "R", ["POWER TO ATRIUM", "LES RACK ML/B01AM", "DK04 FR149 SB"],
                 "K/ML07405  3G6 HF-P", "TO ML/B01AM  Mt.160")
    pb3 = ps_block(sh, 560.0, 360.0, "PSB-F03", "UPS - FIXED MOUNT", "1 DSP-F01 / 2 NSW-F01 / 3-8 SPARE",
                   in_side="R")
    pb4 = ps_block(sh, 560.0, 326.0, "PSB-F04", "UPS - SWING MOUNT", "1-8 SPARE", in_side="R")
    for pb, ids, xv, tag in ((pb3, ("64", "65", "66"), 662.0, "PSB.F03"), (pb4, ("67", "68", "69"), 666.0, "PSB.F04")):
        sh.cable([tb3[i][1] for i in ids], pb["IN"].pins, f"TBA1-{ids[0]}/{tag}-IN", "W-POWER",
                 names_a=["L", "N", "PE"], names_b=["L", "N", "PE"],
                 via=[(xv, tb3[ids[1]][1].y), (xv, pb["IN"].pins[1].y)], label_at=(xv - 0.0, None), pill=False,
                 rec=rec(sh, f"TBA1-{ids[0]}/{tag}-IN", "", INT_PWR25, "TBA1", f"{ids[0]}-{ids[2]}", "TERM.",
                         tag.replace(".", "-"), "IN", "TERM.", "L N PE", "1.5 m", "230V UPS", ""))
        sh.text(f"TBA1-{ids[0]}/{tag}-IN", xv + 1.2, pb["IN"].pins[1].y + 4.0 + (3.0 if tag.endswith("3") else 0.0),
                1.25, "BL", "AV-TEXT")

    # DJ05 -> PSB-F01 / PSB-F02
    i5, o5 = breaker(sh, 275.0, 322.0, "DJ05", ["L1", "L3"])
    tap(["L1", "L3"], i5)
    sh.text("L1-L3", 268.0, 323.0, 1.4, "BR", "AV-TEXT")
    t5 = sh.terminal_block(368.0, 318.0, "", [dict(id="40"), dict(id="41"), dict(id="42", pe=True),
                                              dict(id="43", gap=2.0), dict(id="44"), dict(id="45", pe=True)])
    sh.tb_bridge([t5["40"][0], t5["43"][0]], off=1.2)
    sh.tb_bridge([t5["41"][0], t5["44"][0]], off=2.6)
    sh.cable(o5, [t5["40"][0], t5["41"][0]], "DJ05-2/TBA1-40", "W-POWER", names_a=["L1", "L3"],
             names_b=["L1", "L3"], ytrunk_a=313.0, ytrunk_b=313.0,
             rec=rec(sh, "DJ05-2/TBA1-40", "", "2x H07Z1-K 2.5mm2 LSZH", "DJ05", "2/4", "TERM.", "TBA1", "40-41",
                     "TERM.", "L1 L3", "0.5 m", "230V AC", "Non-UPS internal distribution"))
    pb1 = ps_block(sh, 452.0, 322.0, "PSB-F01", "NON-UPS - FIXED MOUNT", "1 AMP-F01 / 2-8 SPARE")
    pb2 = ps_block(sh, 452.0, 290.0, "PSB-F02", "NON-UPS - SWING MOUNT", "1-8 SPARE")
    sh.cable([t5[i][1] for i in ("40", "41", "42")], pb1["IN"].pins, "TBA1-40/PSB.F01-IN", "W-POWER",
             names_a=["L1", "L3", "PE"], names_b=["L", "N", "PE"],
             rec=rec(sh, "TBA1-40/PSB.F01-IN", "", INT_PWR25, "TBA1", "40-42", "TERM.", "PSB-F01", "IN", "TERM.",
                     "L N PE", "1.5 m", "230V AC", ""))
    sh.cable([t5[i][1] for i in ("43", "44", "45")], pb2["IN"].pins, "TBA1-43/PSB.F02-IN", "W-POWER",
             names_a=["L1", "L3", "PE"], names_b=["L", "N", "PE"], xm=396.0,
             rec=rec(sh, "TBA1-43/PSB.F02-IN", "", INT_PWR25, "TBA1", "43-45", "TERM.", "PSB-F02", "IN", "TERM.",
                     "L N PE", "1.5 m", "230V AC", ""))
    # power cords (schedule only; shown on device boxes)
    for psb, o, dev, ups_ in (("PSB-F03", 1, "DSP-F01", "230V UPS"), ("PSB-F03", 2, "NSW-F01", "230V UPS"),
                              ("PSB-F01", 1, "AMP-F01", "230V")):
        sh.records.append(rec(sh, f"{lbl(psb)}-{o}/{lbl(dev)}-PWR", "", "3G1.0 LSZH CORD SCHUKO/IEC C13", psb,
                              f"OUT {o}", "SCHUKO M", dev, "MAINS IN", "IEC C13 F", "L N PE", "1.5 m", ups_,
                              "Power cord"))

    # DJ06 -> connection panels (outgoing field feeders, right side)
    i6, o6 = breaker(sh, 275.0, 252.0, "DJ06", ["L2", "L3"])
    tap(["L2", "L3"], i6)
    sh.text("L2-L3", 268.0, 253.0, 1.4, "BR", "AV-TEXT")
    ids = [f"{i:02d}" for i in range(46, 58)]
    terms = []
    for k, t in enumerate(ids):
        d = dict(id=t)
        if k % 3 == 2:
            d["pe"] = True
        if k in (3, 6, 9):
            d["gap"] = 6.0
        terms.append(d)
    t6 = sh.terminal_block(705.0, 256.0, "", terms)
    sh.tb_bridge([t6[i][0] for i in ("46", "49", "52", "55")], off=1.2)
    sh.tb_bridge([t6[i][0] for i in ("47", "50", "53", "56")], off=2.6)
    sh.cable(o6, [t6["46"][0], t6["47"][0]], "DJ06-2/TBA1-46", "W-POWER", names_a=["L2", "L3"],
             names_b=["L2", "L3"],
             rec=rec(sh, "DJ06-2/TBA1-46", "", "2x H07Z1-K 2.5mm2 LSZH", "DJ06", "2/4", "TERM.", "TBA1", "46-47",
                     "TERM.", "L2 L3", "1.0 m", "230V AC", "Connection panel feeders"))
    cps = [("K/ML07401", "ML*F01CP-F01", "PWR IN 1", ("46", "47", "48"), "PAX EMB. Dk3 PS"),
           ("K/ML07402", "ML*F01CP-F01", "PWR IN 2", ("49", "50", "51"), "PAX EMB. Dk3 PS"),
           ("K/ML07403", "ML*F02CP-F01", "PWR IN 1", ("52", "53", "54"), "PAX EMB. Dk3 SB"),
           ("K/ML07404", "ML*F02CP-F01", "PWR IN 2", ("55", "56", "57"), "PAX EMB. Dk3 SB")]
    for kno, tag, port, tids, loc in cps:
        A = [t6[i][1] for i in tids]
        sh.cable(A, Pin(FX_R, A[1].y, -1), None, "W-POWER", names_a=["L", "N", "PE"],
                 rec=rec(sh, kno, kno, "3G2.5 HF-P", "ML/F01AM", f"TBA1 {tids[0]}-{tids[2]}", "TERM.", tag, port,
                         "TERM.", "L N PE", "150 m", "230V AC", "DJ06 L2-L3. Check voltage drop vs actual load."))
        sh.field_end(FX_R, A[1].y, "R", ["CONNECTION PANEL", f"{tag} {port}", loc], f"{kno}  3G2.5 HF-P",
                     f"TO {tag}  Mt.150")

    # earthing
    yb = 222.0
    sh.rect(150.0, yb - 1.5, 160.0, 3.0, "W-PE")
    sh.hatch_rect(150.0, yb - 1.5, 160.0, 3.0, "W-PE", rgb=(0, 150, 0), scale=0.4)
    sh.text("PE-F01  RACK EARTH BAR (Cu 25x4)", 150.0, yb + 3.0, 1.9, "BL", "AV-TEXT")
    drops = [(160.0, "TBA1 PE IN (33)"), (183.0, "DIN RAIL TBA1"), (206.0, "DIN RAIL TB1"),
             (229.0, "PSB-F01..F04"), (252.0, "RACK FRAME/DOORS"), (275.0, "SWING FRAME"), (298.0, "HULL (YARD)")]
    for x, t in drops:
        sh.line((x, yb - 1.5), (x, yb - 9.0), "W-PE")
        sh.dot((x, yb - 1.5), 0.5, "W-PE")
        sh.text(t, x, yb - 10.0, 1.05, "TC", "AV-NOTE")
    sh.ground(298.0, yb - 9.0)
    sh.text("16mm2 G/Y", 300.0, yb - 5.0, 1.0, "ML", "AV-NOTE")


# =====================================================================================  SHEET
def build():
    sh = Sheet(DRW, "01", "RACK WIRING ML-F01AM", fmt=(841.0, 1189.0))
    sh.frame(info(DRW, "01 / 01", ["L.E.S. RACK WIRING DIAGRAM", "RACK ML/F01AM",
                                   "AUDIO - NETWORK - MUTING - POWER"], print_fmt="A0"), nc=8, nr=12)
    sh.rack_boundary(140.0, 198.0, 712.0, 1158.0, "ML/F01AM", "CREW & OFFICER MESS",
                     "LES RACK - DK02 FR62 STBD - ELA EL. CABINET")
    audio(sh)
    network(sh)
    muting(sh)
    power(sh)

    # ---- breaker schedule / notes / legends (lower part of the rack)
    rows = [["DJ01", "C16 3P", "L1 L2 L3", "MAIN SWITCH", "-"],
            ["DJ02", "C16 2P", "L1-L2", "UPS-F01 IN, PSU-F01", "non-UPS"],
            ["DJ03", "C16 2P", "UPS GRP1-1", "PSB-F03, PSB-F04", "UPS"],
            ["DJ04", "C16 2P", "UPS GRP1-2", "K/ML07405 -> ML/B01AM", "UPS"],
            ["DJ05", "C16 2P", "L1-L3", "PSB-F01, PSB-F02", "non-UPS"],
            ["DJ06", "C16 2P", "L2-L3", "K/ML07401-404 -> CP F01/F02", "non-UPS"]]
    table(sh, 340.0, 172.0, [(13, "MCB"), (15, "RATING"), (20, "SUPPLY"), (46, "LOADS"), (16, "")], rows,
          title="BREAKER SCHEDULE", h=1.35, rh=3.9)
    sh.notes(470.0, 172.0, [
        "1. TB1 = signal terminals: 3-level for signal cables (+/-/S), 1-level downstream of amplification.",
        "2. TBA1 = power + muting interface: TBA1-01...15 PAGA I/F, 24V to PA and returns",
        "   under PA relay on DISCONNECT terminals; all other TBA1 terminals 1-level.",
        "3. Screens: audio at receiving device only; field screens earthed at rack side only.",
        "4. Muting relays FINDER 55.34 (4CO, 24VDC): coil energised = audio enabled (fail-safe).",
        "5. Ship supply 230V 3-phase IT: single-phase loads line-to-line, 2-pole MCBs.",
        "6. DSP FLEX 5-8 -> AMP LINE IN 1-4 analogue; Dante kept on NPB-F01 P04. CONFIRM.",
        "7. A6F41026007 discrepancies: UPS LAN P13 (sh.06) -> P07; CP feed DJ05 (sh.05) -> DJ06;",
        "   K/ML07408 (sh.03) -> K/ML07308.  PAGA JB/zone match TO BE CONFIRMED.",
        "8. Diamonds: same-sheet / other-drawing continuation (number = link id).",
    ])
    legend_symbols(sh, 150.0, 140.0)
    sh.legend(340.0, 140.0, [("W-AUDIO", "BALANCED AUDIO"), ("W-SPEAKER", "SPEAKER 100V"), ("W-QLAN", "Q-LAN"),
                             ("W-LESNET", "LES-NET"), ("W-DANTE", "DANTE"), ("W-UPLINK", "FIBRE UPLINK"),
                             ("W-GPIO", "GPIO / PAGA I/F"), ("W-24VDC", "24VDC"), ("W-POWER", "230V AC"),
                             ("W-PE", "PE / EARTH")], title="LINE TYPES")
    # disconnect terminal legend
    sh.rect(470.0, 138.0 - 6.0, 15.0, 3.0, "AV-TB")
    sh.line((475.0, 132.0), (475.0, 135.0), "AV-TB")
    sh.knife(470.0, 133.5)
    sh.text("05", 480.0, 133.5, 1.3, "MC", "AV-TB")
    sh.text("DISCONNECT (KNIFE) TERMINAL", 488.0, 133.5, 1.4, "ML", "AV-TEXT")
    sh.rect(470.0, 121.0, 15.0, 9.0, "AV-TB")
    sh.line((475.0, 121.0), (475.0, 130.0), "AV-TB")
    for k in (1, 2):
        sh.line((470.0, 130.0 - 3.0 * k), (475.0, 130.0 - 3.0 * k), "AV-TB")
    for k in range(3):
        sh.text(str(k + 1), 472.5, 128.5 - 3.0 * k, 1.0, "MC", "AV-TB")
    sh.text("01", 480.0, 125.5, 1.3, "MC", "AV-TB")
    sh.text("3-LEVEL TERMINAL (+ / - / S)", 488.0, 125.5, 1.4, "ML", "AV-TEXT")
    return sh


if __name__ == "__main__":
    build().save("/tmp/f01.dxf")
