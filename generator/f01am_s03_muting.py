"""ML/F01AM - sheet 03: PAGA muting interface, MMB boards, relay coils, status LEDs, 24VDC, DSP GPIO."""
from common import INT_24V, INT_CTRL2, INT_GPIO, info, legend_symbols, rec, table
from engine import PIN, Pin, Sheet

DRW = "07FRW01"

ROWS = [
    dict(mmb="MMB-F01", zone="CREW MESS", jb="CB/403D", k="K/CB98002", rly="RLY-F01", leds=("LED-F01", "LED-F02"),
         gpi=1, contacts="11-14 / 21-24 : CREW MESS line (sheet 01)"),
    dict(mmb="MMB-F02", zone="OFFICER MESS", jb="CB/303C", k="K/CB98003", rly="RLY-F02", leds=("LED-F03", "LED-F04"),
         gpi=2, contacts="11-14 / 21-24 : OFFICER MESS line (sheet 01)"),
    dict(mmb="MMB-F03", zone="PAX EMBARKATION", jb="CB/203B", k="K/CB98001", rly="RLY-F03", leds=("LED-F05", "LED-F06"),
         gpi=3, contacts="11-14/21-24 PS line, 31-34/41-44 SB line"),
]
MMB_TOP = [538.0, 428.0, 318.0]


def led_group(sh, x, ytop, tags):
    d = sh.device(x, ytop, 40.0, "SCHNEIDER", "XB5EVB4 (RD) / XB5EVB3 (GN)", "SYSTEM STATUS",
                  f"{tags[0]} / {tags[1]}",
                  left=[dict(id="MID", label="")],
                  right=[dict(id="P24", label=""), dict(id="P0", label="")],
                  header=8.0, pad=2.0, title_h=1.7)
    ym = d["MID"].y
    xl = x + 9.0
    # internal wiring: +24V -> RD (anode) -> MID <- GN (anode) -> 0V
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


def relay_coil(sh, x, yc, tag, note):
    d = sh.device(x, yc + 10.5, 34.0, "FINDER", "55.34.9.024.0040", "MUTING RELAY", tag,
                  left=[dict(id="COIL", label="", conn="TB", g="", pins=["A1", "A2"])],
                  header=6.0, pad=1.5, title_h=1.6, min_h=11.0)
    yy = d["COIL"].y
    cx = x + 17.0
    sh.rect(cx - 4.0, yy - 2.5, 8.0, 5.0, "AV-SYM")
    sh.line((cx - 4.0, yy + 2.5), (cx + 4.0, yy - 2.5), "AV-SYM")
    sh.line((x, d["COIL"].pins[0].y), (cx - 6.0, d["COIL"].pins[0].y), "AV-SYM")
    sh.line((cx - 6.0, d["COIL"].pins[0].y), (cx - 6.0, yy + 2.5), "AV-SYM")
    sh.line((cx - 6.0, yy + 2.5), (cx - 4.0, yy + 2.5), "AV-SYM")
    sh.line((x, d["COIL"].pins[1].y), (cx - 7.0, d["COIL"].pins[1].y), "AV-SYM")
    sh.line((cx - 7.0, d["COIL"].pins[1].y), (cx - 7.0, yy - 2.5), "AV-SYM")
    sh.line((cx - 7.0, yy - 2.5), (cx - 4.0, yy - 2.5), "AV-SYM")
    sh.text("24VDC", cx + 5.0, yy, 1.1, "ML", "AV-NOTE")
    sh.text("+99.02 LED/DIODE", cx, d["_box"].pins[1].y - 3.0, 1.0, "MC", "AV-NOTE")
    sh.text("contacts: " + note, x + 17.0, d["_box"].pins[0].y - 8.0, 1.05, "TC", "AV-NOTE")
    return d


def build():
    sh = Sheet(DRW, "03", "MUTING / GPIO")
    sh.frame(info(DRW, "03 / 04", ["L.E.S. WIRING DIAGRAM", "RACK ML/F01AM",
                                   "PAGA MUTING - STATUS - 24VDC - DSP GPIO"]))
    sh.rack_boundary(111.0, 150.0, 670.0, 572.0, "ML/F01AM", "CREW & OFFICER MESS",
                     "SHEET 03 - PAGA MUTING / STATUS LEDs / 24VDC / DSP GPIO")

    # ------------------------------------------------------------ DSP + TB3 GPIO
    dsp = sh.device(622.0, 430.0, 40.0, "QSC", "CORE 8 FLEX", "AUDIO DSP (see sheet 01)", "DSP-F01",
                    left=[dict(id="GPI", label="GPIO IN", conn="EB", g="F",
                               pins=["+12V", "1", "2", "3", "4", "5", "6", "7", "8", "GND"])],
                    partial=True, header=8.0, pad=3.0, title_h=1.8)
    gtb = sh.terminal_block(540.0, 410.0, "TB3", [
        dict(id="16", note="GPI1"), dict(id="17", note="GPI2"), dict(id="18", note="GPI3"),
        dict(id="19", note="COM"), dict(id="20", note="COM"), dict(id="21", note="COM"),
        dict(id="22", pe=True)], sec="1.5")
    sh.tb_bridge([gtb["19"][1], gtb["20"][1], gtb["21"][1]])
    gp = dsp["GPI"].pins
    sh.cable([gtb[i][1] for i in ("16", "17", "18", "19", "22")],
             [gp[1], gp[2], gp[3], gp[9], Pin(gp[9].x, gp[9].y - PIN, -1, "S")],
             "TB3-16/DSP.F01-GPI", "W-GPIO", names_a=["IN1", "IN2", "IN3", "COM", "S"],
             names_b=["1", "2", "3", "GND", "S"], cut_b={4}, label_at=(577.0, None),
             rec=rec(sh, "TB3-16/DSP.F01-GPI", "", INT_GPIO, "TB3", "16-19 (+22 PE)", "TERM.", "DSP-F01",
                     "GPIO IN 1/2/3/GND", "EB 10P F", "IN1 IN2 IN3 COM + S", "1.5 m", "GPIO",
                     "Q-SYS GPIO inputs as contact closure (internal pull-up)."))
    sh.text("GPIO IN 4-8, +12V : n.c.", 622.0 - 12.0, dsp["GPI"].pins[9].y - 6.0, 1.1, "TR", "AV-NOTE")

    # ------------------------------------------------------------------- PSU + TB4 feed
    psu = sh.device(330.0, 205.0, 46.0, "MEAN WELL", "NDR-120-24 (24VDC 5A DIN)", "MUTE PSU", "PSU-F01",
                    left=[dict(id="AC", label="AC IN", conn="TB", g="", pins=["L", "N", "PE"])],
                    right=[dict(id="DC", label="DC OUT", conn="TB", g="", pins=["+V", "-V"])],
                    icon="psu", header=10.0, pad=3.0, title_h=1.9)
    sh.xref(Pin(psu["AC"].pins[1].x, psu["AC"].pins[1].y, -1), "04", ["TBA1 / DJ02 OUT (L1-L2)", "230V NON-UPS"],
            wire_layer="W-POWER", lead=10.0)
    feed = sh.terminal_block(478.0, 199.0, "TB4", [dict(id="01", note="+24V"), dict(id="02", note="0V")], sec="2.5")
    sh.cable(psu["DC"].pins, [feed["01"][0], feed["02"][0]], "PSU.F01-OUT/TB4-01", "W-24VDC", names_a=["+", "-"],
             names_b=["+", "-"],
             rec=rec(sh, "PSU.F01-OUT/TB4-01", "", INT_24V, "PSU-F01", "DC OUT +V/-V", "TERM.", "TB4", "01-02",
                     "TERM.", "+24V / 0V", "0.5 m", "24VDC", "Jumper bars: TB4 odd terminals +24V, even 0V"))
    comb_p, comb_n = [feed["01"][1]], [feed["02"][1]]

    # ------------------------------------------------------------------- rows
    XV = {1: 515.0, 2: 518.0, 3: 523.0}
    for r, row in enumerate(ROWS):
        top = MMB_TOP[r]
        n = r + 1
        mmb = sh.device(200.0, top, 60.0, "VIDELIO", "MASTER BOARD", "PA MASTER", row["mmb"],
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
        # TB3 PAGA group
        ids = [f"{5 * r + i:02d}" for i in range(1, 6)]
        pa = mmb["PA"].pins
        tb3 = sh.terminal_block(104.0, pa[0].y + 1.5, "TB3" if r == 0 else "", [
            dict(id=ids[0]), dict(id=ids[1]), dict(id=ids[2]), dict(id=ids[3]), dict(id=ids[4], pe=True)], sec="1.5")
        sh.cable([tb3[i][1] for i in ids[:4]], pa, f"TB3-{ids[0]}/{row['mmb'].replace('-', '.')}-PA", "W-GPIO",
                 names_a=["+24V", "MUTE", "EN", "GND"], names_b=["+24V", "MUTE", "EN", "GND"],
                 rec=rec(sh, f"TB3-{ids[0]}/{row['mmb'].replace('-', '.')}-PA", "", INT_GPIO, "TB3",
                         f"{ids[0]}-{ids[3]}", "TERM.", row["mmb"], "PAGA I/F", "EB 4P F", "+24V MUTE EN GND",
                         "1.5 m", "GPIO", f"Zone {row['zone']}"))
        # PAGA junction box (by others)
        jb = sh.device(24.0, pa[0].y + 12.5, 34.0, "PAGA (BY OTHERS)", "JUNCTION BOX", "DK2 FR62 SB EL. LOCKER",
                       row["jb"], right=[dict(id="T", label="MUTE I/F", conn="TB", g="",
                                              pins=["+24V", "MUTE", "EN", "GND"])],
                       partial=True, header=8.0, pad=3.0, title_h=1.7)
        jp = jb["T"].pins
        virt = Pin(jp[0].x, jp[3].y - PIN, 1, "S")
        sh.cable(jp + [virt], [tb3[i][0] for i in ids], None, "W-GPIO", names_a=["1", "2", "3", "4", "S"],
                 names_b=["1", "2", "3", "4", "S"], cut_a={4},
                 info=(row["k"], "BY OTHERS"),
                 rec=rec(sh, row["k"], row["k"], "BY PAGA SUPPLIER (min. 4 cond. screened)", row["jb"],
                         "MUTE I/F", "TERM. (by others)", "ML/F01AM", f"TB3 {ids[0]}-{ids[4]}", "TERM.",
                         "+24V(to PA) MUTE ENABLE GND + S", "-", "GPIO",
                         f"MUTE FROM PA {row['zone']}. JB<->zone match to be confirmed by PAGA supplier."))
        # relay coil
        ch = mmb["CH"].pins
        rc = relay_coil(sh, 330.0, (ch[0].y + ch[1].y) / 2, row["rly"], row["contacts"])
        sh.cable(ch, rc["COIL"].pins, f"{row['mmb'].replace('-', '.')}-OUT/{row['rly'].replace('-', '.')}-A1",
                 "W-GPIO", names_a=["+", "-"], names_b=["A1", "A2"],
                 rec=rec(sh, f"{row['mmb'].replace('-', '.')}-OUT/{row['rly'].replace('-', '.')}-A1", "", INT_CTRL2,
                         row["mmb"], "CHAIN OUT +/-", "EB 2P F", row["rly"], "COIL A1/A2", "TERM. (socket 94.04)",
                         "OUT+ / OUT-", "1.0 m", "GPIO", "Coil energised = audio enabled (fail-safe mute)"))
        # status LEDs
        lp = mmb["LED"].pins[0]
        lg = led_group(sh, 380.0, lp.y + 12.5, row["leds"])
        sh.cable(lp, lg["MID"].p, f"{row['mmb'].replace('-', '.')}-LED/{row['leds'][0].replace('-', '.')}-X2",
                 "W-24VDC", label_at=(300.0, None),
                 rec=rec(sh, f"{row['mmb'].replace('-', '.')}-LED/{row['leds'][0].replace('-', '.')}-X2", "",
                         "1x1.0 LSZH", row["mmb"], "LED", "EB 1P F", f"{row['leds'][0]}/{row['leds'][1]}",
                         "X2 RD / X1 GN", "TERM.", "1 cond.", "1.5 m", "24VDC", "Status LED drive (front panel)"))
        # TB4 group for this row
        t = [f"{4 * r + i + 2:02d}" for i in range(1, 5)]
        tb4 = sh.terminal_block(478.0, lg["P24"].y + 1.5, "", [
            dict(id=t[0], note="+24V"), dict(id=t[1], note="0V"), dict(id=t[2], note="+24V"), dict(id=t[3], note="0V")],
            sec="1.5")
        sh.cable([tb4[t[0]][0], tb4[t[1]][0]], [lg["P24"].p, lg["P0"].p],
                 f"TB4-{t[0]}/{row['leds'][0].replace('-', '.')}-X1", "W-24VDC", names_a=["+", "-"],
                 names_b=["+", "-"],
                 rec=rec(sh, f"TB4-{t[0]}/{row['leds'][0].replace('-', '.')}-X1", "", INT_24V, "TB4",
                         f"{t[0]}-{t[1]}", "TERM.", f"{row['leds'][0]}/{row['leds'][1]}", "X1 RD / X2 GN", "TERM.",
                         "+24V / 0V", "1.5 m", "24VDC", "Status LEDs supply"))
        pw = mmb["PWR"].pins
        sh.cable([tb4[t[2]][0], tb4[t[3]][0]], pw, f"TB4-{t[2]}/{row['mmb'].replace('-', '.')}-PWR", "W-24VDC",
                 names_a=["+", "-"], names_b=["+24V", "0V"], xm=455.0, label_at=(300.0, None),
                 rec=rec(sh, f"TB4-{t[2]}/{row['mmb'].replace('-', '.')}-PWR", "", INT_24V, "TB4",
                         f"{t[2]}-{t[3]}", "TERM.", row["mmb"], "POWER 24V", "EB 2P F", "+24V / 0V", "1.5 m",
                         "24VDC", "Fused terminal 2A on +24V"))
        comb_p += [tb4[t[0]][1], tb4[t[2]][1]]
        comb_n += [tb4[t[1]][1], tb4[t[3]][1]]
        # dry contact -> TB3 GPIO
        dr = mmb["DRY"].pins
        a, b = f"{15 + n}", f"{18 + n}"
        yc = (gtb[a][0].y + gtb[b][0].y) / 2
        sh.cable(dr, [gtb[a][0], gtb[b][0]], f"{row['mmb'].replace('-', '.')}-DRY/TB3-{a}", "W-GPIO",
                 names_a=["D1", "D2"], names_b=["D1", "D2"], ytrunk_b=yc,
                 via=[(XV[n], dr[0].y - 1.5), (XV[n], yc)], label_at=(300.0, None),
                 rec=rec(sh, f"{row['mmb'].replace('-', '.')}-DRY/TB3-{a}", "", INT_CTRL2, row["mmb"], "DRY DSP",
                         "EB 2P F", "TB3", f"{a} / {b}", "TERM.", "D1 / D2", "2.0 m", "GPIO",
                         f"Mute status {row['zone']} -> DSP GPIO IN {n}"))
    # jumper combs TB4 (+24V / 0V)
    for comb, dx, lay in ((comb_p, 3.0, "W-24VDC"), (comb_n, 6.0, "W-24VDC")):
        xs = comb[0].x + dx
        ys = [p.y for p in comb]
        sh.line((xs, min(ys)), (xs, max(ys)), lay, lw=50)
        for p in comb:
            sh.line((p.x, p.y), (xs, p.y), lay)
            sh.dot((xs, p.y), 0.55, lay)
    sh.text("JUMPER BAR +24V", comb_p[0].x + 4.0, max(p.y for p in comb_p) + 4.0, 1.2, "BL", "AV-NOTE")
    sh.text("JUMPER BAR 0V", comb_p[0].x + 7.0, max(p.y for p in comb_p) + 1.6, 1.2, "BL", "AV-NOTE")

    # ------------------------------------------------------------------- notes
    rows = [[r["mmb"], r["zone"], r["jb"], r["k"], f"TB3-{5 * i + 1:02d}...{5 * i + 5:02d}", r["rly"],
             f"GPI {r['gpi']}", f"{r['leds'][0]}/{r['leds'][1]}"] for i, r in enumerate(ROWS)]
    table(sh, 676.0, 566.0, [(16, "BOARD"), (28, "ZONE"), (15, "PAGA JB"), (17, "CABLE"), (24, "TB3"),
                             (15, "RELAY"), (12, "DSP"), (34, "LEDs")], rows, title="MUTING SUMMARY")
    sh.notes(676.0, 535.0, [
        "1. PAGA interface per A6F41026007 sh.04/06: MMB sends 24V TO PA, PA returns MUTE and ENABLE.",
        "   Cables K/CB98001-003 and terminations at PAGA JB by PAGA supplier.",
        "   JB <-> zone assignment (CB/403D, CB/303C, CB/203B) TO BE CONFIRMED with PAGA supplier.",
        "2. Fail-safe: CHAIN OUT energises the muting relay coil when no PA call is active;",
        "   PA call or MMB/PSU failure de-energises the coil and opens the 100V line (sheet 01).",
        "3. MMB DRY DSP contact (closed = muted) reported to Q-SYS GPIO IN 1/2/3 for logic and fade.",
        "4. SYSTEM STATUS lamps on rack front: RD = MUTING, GN = RUNNING (MMB LED output drives midpoint).",
        "5. TB4: +24V terminals with fuse (2A MMB, 1A LEDs), 0V common; PSU-F01 fed from DJ02 (sheet 04).",
        "6. Screens of PAGA cables earthed on TB3 PE terminals (rack side only).",
        "7. Override 1/2 and BUS MUTING DB9 of MMB not used in this project.",
    ])
    legend_symbols(sh, 676.0, 495.0)
    sh.legend(676.0, 430.0, [("W-GPIO", "GPIO / CONTROL / PAGA I/F"), ("W-24VDC", "24VDC"),
                             ("W-POWER", "230V AC"), ("AV-RACK", "RACK LIMIT")], title="LINE TYPES")
    return sh


if __name__ == "__main__":
    build().save("/tmp/s03.dxf")
