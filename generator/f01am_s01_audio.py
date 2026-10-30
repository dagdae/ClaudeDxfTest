"""ML/F01AM - sheet 01: audio signal path and 100V speaker lines."""
from common import INT_AUDIO, INT_SPK, info, legend_symbols, rec, table
from engine import PIN, Pin, Sheet

DRW = "07FRW01"

ZONES = [
    # name, loc, field cable, length, first, last, loop cables, relay, poles, dsp out, amp ch
    dict(name="CREW MESS", loc="CREW MESS Dk.4", k="K/ML07601", mt="Mt.27", n=16, first="F01", last="F16",
         loop=("K/ML07002", "K/ML07016"), mid=("F02", "F15"), rly="RLY-F01", poles=("11", "14", "21", "24"),
         spare="31-34 / 41-44 SPARE", dsp=5, ch=1, mmb="MMB-F01"),
    dict(name="OFFICER MESS", loc="OFFICER MESS Dk.4", k="K/ML07602", mt="Mt.17", n=16, first="F17", last="F32",
         loop=("K/ML07018", "K/ML07032"), mid=("F18", "F31"), rly="RLY-F02", poles=("11", "14", "21", "24"),
         spare="31-34 / 41-44 SPARE", dsp=6, ch=2, mmb="MMB-F02"),
    dict(name="PAX EMBARKATION PS", loc="PAX EMB. Dk3 PS", k="K/ML07603", mt="Mt.140", n=4, first="F33", last="F36",
         loop=("K/ML07034", "K/ML07036"), mid=("F34", "F35"), rly="RLY-F03", poles=("11", "14", "21", "24"),
         spare="POLES 1-2 OF 4", dsp=7, ch=3, mmb="MMB-F03"),
    dict(name="PAX EMBARKATION SB", loc="PAX EMB. Dk3 SB", k="K/ML07604", mt="Mt.140", n=4, first="F37", last="F40",
         loop=("K/ML07038", "K/ML07040"), mid=("F38", "F39"), rly="RLY-F03", poles=("31", "34", "41", "44"),
         spare="POLES 3-4 OF 4", dsp=8, ch=4, mmb="MMB-F03"),
]

ZC = [544.0, 474.0, 404.0, 334.0]   # y of each speaker zone (first speaker input)


def relay_contacts(sh: Sheet, x, yc, tag, poles, sub, w=30.0):
    """Detached NO contacts (2 poles) of a muting relay. Returns (left pins, right pins)."""
    sh.rect(x, yc - 6.5, w, 13.0, "AV-DEVICE-REF")
    sh.text(tag, x + w / 2, yc + 7.6, 2.0, "BC", "AV-TEXT-DEV")
    sh.text(sub, x + w / 2, yc - 7.6, 1.15, "TC", "AV-NOTE")
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
    # mechanical link
    sh.line((x + w / 2 + 0.2, yc + 3.5), (x + w / 2 + 0.2, yc - 1.5), "AV-SYM", ltype="AV_HIDDEN")
    return L, R


def speaker(sh, x, ytop, tag, last=False):
    left = [dict(id="IN", label="IN 100V", conn="TB", g="", pins=["+", "-"])]
    if last:
        right = [dict(id="LOOP", label="END", pins=None)]
    else:
        right = [dict(id="LOOP", label="LOOP", conn="TB", g="", pins=["+", "-"])]
    return sh.device(x, ytop, 32.0, "FOHHN", "CS-104 MED", "CEILING SPEAKER", tag, left, right,
                     icon="speaker", header=10.0, pad=3.0, note="15W/100V", title_h=1.9)


def build():
    sh = Sheet(DRW, "01", "AUDIO / SPEAKER LINES")
    sh.frame(info(DRW, "01 / 04", ["L.E.S. WIRING DIAGRAM", "RACK ML/F01AM", "AUDIO SIGNAL - 100V SPEAKER LINES"]))
    RX0, RX1 = 125.0, 565.0
    sh.rack_boundary(RX0, 298.0, RX1, 572.0, "ML/F01AM", "CREW & OFFICER MESS",
                     "SHEET 01 - AUDIO SIGNAL PATH / 100V SPEAKER LINES")

    # ------------------------------------------------------------------ TB1
    tb1 = sh.terminal_block(118.0, 499.0, "TB1", [
        dict(id="01"), dict(id="02"), dict(id="03"), dict(id="04", gap=2.0), dict(id="05"), dict(id="06"),
        dict(id="07", pe=True)], sec="2.5")
    sh.text("AUDIO IN", 125.5, 474.0, 1.3, "TC", "AV-NOTE")
    # field cable K/ML07101 from ML/B01AM
    fa = [tb1[i][0] for i in ("01", "02", "03", "04", "05", "06", "07")]
    sh.cable(fa, Pin(58.0, 487.0, 1), None, "W-AUDIO",
             names_a=["P1+", "P1-", "S1", "P2+", "P2-", "S2", "CS"], ytrunk_a=487.0,
             info=("K/ML07101  2x2x0.75 HF-TXISCS", "Mt.160 - FROM ML/B01AM"), info_at=(60.0, 487.0, "L"),
             rec=rec(sh, "K/ML07101", "K/ML07101", "2x2x0.75 HF-TXISCS", "ML/B01AM", "TB-B01 01-07", "TERM.",
                     "ML/F01AM", "TB1 01-07", "TERM.", "P1(+/-/S1) P2(+/-/S2) CS", "160 m", "AUDIO",
                     "Audio from ATRIUM system (dwg 006376A6F41026002). Screens S1/S2 earthed at DSP input only."))
    sh.mtext_lines(["ML/B01AM", "LES RACK ATRIUM", "DK04 FR149 SB", "(see 07BRW01)"], 56.0, 491.5, 1.35, "TR")

    # ------------------------------------------------------------------ DSP
    eb = dict(conn="EB", g="F", pins=["+", "-", "G"])
    dsp = sh.device(205.0, 515.0, 52.0, "QSC", "CORE 8 FLEX", "AUDIO DSP", "DSP-F01",
                    left=[dict(id="F1", label="FLEX 1 IN", **eb), dict(id="F2", label="FLEX 2 IN", **eb),
                          dict(id="F3", label="FLEX 3 (SPARE)"), dict(id="F4", label="FLEX 4 (SPARE)"),
                          dict(id="GPI", label="GPIO IN"), dict(id="GPO", label="GPIO OUT"),
                          dict(id="RSA", label="RS232 A"), dict(id="RSB", label="RS232 B"),
                          dict(id="USBC", label="USB C")],
                    right=[dict(id="F5", label="FLEX 5 OUT", **eb), dict(id="F6", label="FLEX 6 OUT", **eb),
                           dict(id="F7", label="FLEX 7 OUT", **eb), dict(id="F8", label="FLEX 8 OUT", **eb),
                           dict(id="LANA", label="LAN A", conn="RJ45", g="M"),
                           dict(id="LANB", label="LAN B", conn="RJ45", g="M"),
                           dict(id="USBA", label="USB A 1-4"), dict(id="USBB", label="USB B")],
                    icon="dsp", bottom=dict(id="PWR", label="230V UPS", conn="IEC C13", g="F"))
    # TB1 -> DSP inputs
    for grp, port, ytr in ((("01", "02", "03"), "F1", None), (("04", "05", "06"), "F2", None)):
        A = [tb1[i][1] for i in grp]
        B = dsp[port].pins
        n = int(port[1])
        sh.cable(A, B, f"TB1-{grp[0]}/DSP.F01-IN{n}", "W-AUDIO", names_a=["+", "-", "S"], names_b=["+", "-", "S"],
                 ytrunk_a=dsp[port].pins[1].y, ytrunk_b=dsp[port].pins[1].y,
                 rec=rec(sh, f"TB1-{grp[0]}/DSP.F01-IN{n}", "", INT_AUDIO, "TB1", "-".join(grp), "TERM.",
                         "DSP-F01", f"FLEX {n} IN", "EB 3P F", "+ / - / S", "1.5 m", "AUDIO",
                         "Screen to DSP G pin (receiving end)."))
    # DSP off-sheet references
    sh.xref(dsp["GPI"].p, "03", ["TB3 / MMB-F01...F03", "MUTE STATUS (DRY)"], wire_layer="W-GPIO")
    sh.xref(dsp["LANA"].p, "02", ["NPB-F01 P01", "Q-LAN A"], wire_layer="W-QLAN")
    sh.xref(dsp["LANB"].p, "02", ["NPB-F01 P05", "LES-NET"], wire_layer="W-LESNET")
    sh.xref(dsp["PWR"].p, "04", ["PSB-F03 / OUT 1", "230V UPS"], wire_layer="W-POWER")
    for pid in ("F3", "F4", "GPO", "RSA", "RSB", "USBC", "USBA", "USBB"):
        sh.text("n.c.", dsp[pid].p.x + (2.6 if dsp[pid].p.d > 0 else -2.6), dsp[pid].p.y, 1.1,
                "ML" if dsp[pid].p.d > 0 else "MR", "AV-NOTE")

    # ------------------------------------------------------------------ AMP
    px3 = dict(conn="PHX", g="M", pins=["+", "-", "G"])
    px2 = dict(conn="PHX", g="M", pins=["+", "-"])
    amp = sh.device(338.0, 515.0, 52.0, "POWERSOFT", "QUATTROCANALI 1204 DSP+D", "AMPLIFIER 4x300W", "AMP-F01",
                    left=[dict(id="L1", label="LINE IN 1", **px3), dict(id="L2", label="LINE IN 2", **px3),
                          dict(id="L3", label="LINE IN 3", **px3), dict(id="L4", label="LINE IN 4", **px3),
                          dict(id="LEV", label="REMOTE LEVEL 1-4"), dict(id="RON", label="REM. ON IN"),
                          dict(id="ROFF", label="REM. OFF IN"), dict(id="ALM", label="ALARM"),
                          dict(id="ETH", label="ETHERNET", conn="RJ45", g="M"),
                          dict(id="DAN", label="DANTE", conn="RJ45", g="M")],
                    right=[dict(id="O1", label="OUT CH1", **px2), dict(id="O2", label="OUT CH2", **px2),
                           dict(id="O3", label="OUT CH3", **px2), dict(id="O4", label="OUT CH4", **px2)],
                    icon="amp", bottom=dict(id="PWR", label="230V", conn="IEC C13", g="F"))
    for z in ZONES:
        n = z["ch"]
        sh.cable(dsp[f"F{z['dsp']}"].pins, amp[f"L{n}"].pins, f"DSP.F01-OUT{z['dsp']}/AMP.F01-IN{n}", "W-AUDIO",
                 names_a=["+", "-", "S"], names_b=["+", "-", "S"], cut_a={2},
                 rec=rec(sh, f"DSP.F01-OUT{z['dsp']}/AMP.F01-IN{n}", "", INT_AUDIO, "DSP-F01",
                         f"FLEX {z['dsp']} OUT", "EB 3P F", "AMP-F01", f"LINE IN {n}", "PHX 3P M", "+ / - / S",
                         "1.0 m", "AUDIO", f"Zone {z['name']}. Screen at AMP G pin only."))
    sh.xref(amp["ETH"].p, "02", ["NPB-F01 P06", "LES-NET"], wire_layer="W-LESNET")
    sh.xref(amp["DAN"].p, "02", ["NPB-F01 P04", "DANTE"], wire_layer="W-DANTE")
    sh.xref(amp["PWR"].p, "04", ["PSB-F01 / OUT 1", "230V"], wire_layer="W-POWER")
    for pid in ("LEV", "RON", "ROFF", "ALM"):
        sh.text("n.c.", amp[pid].p.x - 2.6, amp[pid].p.y, 1.1, "MR", "AV-NOTE")

    # ------------------------------------------------- relays, TB2, field zones
    XM = {1: 455.0, 2: 458.0, 3: 455.0, 4: 452.0}
    for k, z in enumerate(ZONES):
        zc = ZC[k]
        n = z["ch"]
        L, R = relay_contacts(sh, 472.0, zc, z["rly"] + ("" if n < 3 else (" (1/2)" if n == 3 else " (2/2)")),
                              z["poles"], f"FINDER 55.34 24VDC - {z['spare']}")
        sh.cable(amp[f"O{n}"].pins, L, f"AMP.F01-OUT{n}/{z['rly'].replace('-', '.')}-COM", "W-SPEAKER",
                 names_a=["+", "-"], names_b=["+", "-"], xm=XM[n], label_at=(430.0, None), ytrunk_b=zc,
                 rec=rec(sh, f"AMP.F01-OUT{n}/{z['rly'].replace('-', '.')}-COM", "", INT_SPK, "AMP-F01",
                         f"OUT CH{n}", "PHX 2P M", z["rly"], f"{z['poles'][0]}/{z['poles'][2]} (COM)", "TERM.",
                         "+ / -", "1.5 m", "SPEAKER 100V", f"Zone {z['name']}"))
        ids = [f"{5 * k + i:02d}" for i in range(1, 6)]
        tb2 = sh.terminal_block(556.0, zc + 7.5, "TB2" if k == 0 else "", [
            dict(id=ids[0]), dict(id=ids[1]), dict(id=ids[2], note="SPARE", note_side="L"),
            dict(id=ids[3], note="SPARE", note_side="L"), dict(id=ids[4], pe=True)], sec="2.5")
        sh.cable(R, [tb2[ids[0]][0], tb2[ids[1]][0]], f"{z['rly'].replace('-', '.')}-NO/TB2-{ids[0]}", "W-SPEAKER",
                 names_a=["+", "-"], names_b=["+", "-"], ytrunk_a=zc, ytrunk_b=zc,
                 rec=rec(sh, f"{z['rly'].replace('-', '.')}-NO/TB2-{ids[0]}", "", INT_SPK, z["rly"],
                         f"{z['poles'][1]}/{z['poles'][3]} (NO)", "TERM.", "TB2", f"{ids[0]}-{ids[1]}", "TERM.",
                         "+ / -", "1.0 m", "SPEAKER 100V", f"Zone {z['name']}"))
        # ---------------- field zone
        top = zc + 32.0
        sh.field_box(596.0, top - 66.0, 232.0, 66.0, f"{z['loc']}  -  100V LINE ZONE {k + 1}  ({z['name']})",
                     [f"{z['n']} x FOHHN CS-104 MED  ML*104SP-{z['first']}...{z['last']}  -  tap 15W @100V  -  "
                      f"total {15 * z['n']} W on AMP-F01 CH{n} (300W)"])
        s1 = speaker(sh, 668.0, zc + 16.0, f"ML*104SP-{z['first']}")
        s2 = speaker(sh, 792.0, zc + 16.0, f"ML*104SP-{z['last']}", last=True)
        # home-run field cable TB2 -> first speaker (2x2x1.5: pair1 line, pair2 spare, screen)
        ip = s1["IN"].pins
        virt = [Pin(ip[0].x, ip[1].y - PIN * (i + 1), -1, "") for i in range(3)]
        A = [tb2[i][1] for i in ids]
        sh.cable(A, ip + virt, None, "W-SPEAKER", names_a=["P1+", "P1-", "P2a", "P2b", "S"],
                 names_b=["P1+", "P1-", "P2a", "P2b", "S"], cut_b={2, 3, 4}, ytrunk_a=zc, ytrunk_b=zc,
                 info=(f"{z['k']}  2x2x1.5 HF-TXCS", f"{z['mt']} - TO ML*104SP-{z['first']}"),
                 info_at=(598.0, zc, "L"),
                 rec=rec(sh, z["k"], z["k"], "2x2x1.5 HF-TXCS", "ML/F01AM", f"TB2 {ids[0]}-{ids[4]}", "TERM.",
                         f"ML*104SP-{z['first']}", "IN 100V", "TERM.", "P1 +/- line, P2 spare, S", z["mt"].replace("Mt.", "") + " m",
                         "SPEAKER 100V", f"{z['loc']}. Screen earthed at rack TB2-{ids[4]} only; P2 spare."))
        sh.text("P2 + S isolated", ip[0].x - 1.0, virt[-1].y - 2.2, 1.1, "TR", "AV-NOTE")
        # daisy chain
        A = s1["LOOP"].pins
        B = s2["IN"].pins
        pts = sh.cable(A, B, None, "W-SPEAKER", names_a=["+", "-"], names_b=["+", "-"], ytrunk_a=zc, ytrunk_b=zc,
                       rec=rec(sh, f"{z['loop'][0]}...{z['loop'][1]}", f"{z['loop'][0]}...{z['loop'][1]}",
                               "1x2x1.5 HF-TXCS", f"ML*104SP-{z['first']}", "LOOP", "TERM.", f"ML*104SP-{z['last']}",
                               "IN 100V", "TERM.", "+ / -", "5 m each", "SPEAKER 100V",
                               f"Daisy chain ML*104SP-{z['first']}...{z['last']} (loop -> in)"))
        mx = (pts[0][0] + pts[-1][0]) / 2
        sh.line((mx - 1.2, zc - 2.0), (mx + 0.2, zc + 2.0), "W-SPEAKER")
        sh.line((mx + 0.2, zc - 2.0), (mx + 1.6, zc + 2.0), "W-SPEAKER")
        sh.mtext_lines([f"{z['loop'][0]}...{z['loop'][1]}", "1x2x1.5 HF-TXCS - Mt.5 each"], mx, zc + 2.4, 1.3, "BC")
        sh.mtext_lines([f"ML*104SP-{z['mid'][0]}...{z['mid'][1]}", "LOOP -> IN, same wiring"], mx, zc - 2.4, 1.3, "TC")
        sh.text("n.c.", s2["LOOP"].p.x + 2.6, s2["LOOP"].p.y, 1.1, "ML", "AV-NOTE")

    # ------------------------------------------------------------- tables / notes
    rows = []
    for z in ZONES:
        rows.append([z["name"], f"FLEX {z['dsp']} OUT", f"CH{z['ch']}", f"{z['rly']} {z['poles'][0]}-{z['poles'][1]}/"
                     f"{z['poles'][2]}-{z['poles'][3]}", f"TB2-{5 * (z['ch'] - 1) + 1:02d}...{5 * z['ch']:02d}",
                     z["k"], f"{z['n']} x 15W = {15 * z['n']}W", z["mmb"]])
    table(sh, 30.0, 285.0, [(36, "ZONE"), (22, "DSP-F01"), (14, "AMP-F01"), (46, "MUTING RELAY (COM-NO)"),
                             (28, "TB2"), (22, "FIELD CABLE"), (30, "LOAD @100V"), (20, "MUTE BY")], rows,
          title="AUDIO ZONE SUMMARY")
    sh.notes(30.0, 250.0, [
        "1. Balanced audio: screen connected to the G pin of the RECEIVING device only; sending end cut back and taped.",
        "2. Field cable screens earthed at rack side only (TB1-07 / TB2 PE terminals); field side cut back, isolated, taped.",
        "3. 100V lines switched on both conductors by muting relays (NO contacts, coil energised = audio enabled).",
        "   Relay coils, MMB boards and PAGA interface: see sheet 03.  Relays: FINDER 55.34.9.024.0040 + socket 94.04.",
        "4. DSP flex channels 1-2 configured as inputs, 5-8 as line outputs (+4 dBu) to AMP-F01 analogue inputs.",
        "   Dante link AMP-F01 / Q-LAN on NPB-F01 P04 kept as per functional diagram (sheet 02).",
        "5. AMP-F01 channels set to 100V constant voltage mode, high-pass 80 Hz (FOHHN CS-104 with 100V transformer).",
        "6. Spare pair P2 of 2x2x1.5 home-run cables parked on TB2 SPARE terminals, isolated at speaker side.",
        "7. Cable numbers K/MLxxxxx as per " + "006376A6F41026007; internal cables identified by FROM.DEV-OUT/TO.DEV-IN labels.",
    ])
    legend_symbols(sh, 470.0, 285.0)
    sh.legend(700.0, 285.0, [("W-AUDIO", "BALANCED AUDIO (+ / - / S)"), ("W-SPEAKER", "SPEAKER LINE 100V"),
                             ("W-QLAN", "Q-LAN (VLAN QLAN-A)"), ("W-LESNET", "LES-NET"), ("W-DANTE", "DANTE"),
                             ("W-GPIO", "GPIO / CONTROL"), ("W-POWER", "230V AC"), ("AV-RACK", "RACK LIMIT")],
              title="LINE TYPES")
    return sh


if __name__ == "__main__":
    s = build()
    s.save("/tmp/s01.dxf")
