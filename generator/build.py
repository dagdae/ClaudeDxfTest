"""Build all executive wiring sheets: DXF + multipage PDF + PNG previews + cable schedule."""
import csv
import os
import sys

from engine import render_pdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DXF = os.path.join(ROOT, "output", "dxf")
OUT_PDF = os.path.join(ROOT, "output", "pdf")


def sheets():
    import b01am_rack
    import f01am_rack
    return [f01am_rack, b01am_rack]


def main(png_dir=None):
    os.makedirs(OUT_DXF, exist_ok=True)
    os.makedirs(OUT_PDF, exist_ok=True)
    built = []
    records = []
    for m in sheets():
        sh = m.build()
        fname = f"{sh.code}_{sh.title.replace(' / ', '_').replace(' ', '-')}.dxf"
        path = os.path.join(OUT_DXF, fname)
        sh.save(path)
        built.append((sh, path))
        records += sh.records
        print("saved", path)
    sets = {}
    for sh, path in built:
        sets.setdefault(sh.code, []).append((sh, path))
    pngs = []
    for code, items in sets.items():
        pngs += render_pdf(items, os.path.join(OUT_PDF, f"{code}.pdf"), png_dir=png_dir)
        print("pdf", code)
    with open(os.path.join(ROOT, "output", "cable_schedule.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["CABLE LABEL", "SHIP CABLE No.", "CABLE TYPE", "FROM DEVICE", "FROM PORT", "FROM CONNECTOR",
                    "TO DEVICE", "TO PORT", "TO CONNECTOR", "CONDUCTORS", "LENGTH", "SHEET", "SIGNAL", "NOTE"])
        for r in records:
            w.writerow([r.label, r.cable_no, r.ctype, r.from_dev, r.from_port, r.from_conn, r.to_dev, r.to_port,
                        r.to_conn, r.cores, r.length, r.sheet, r.signal, r.note])
    print("records", len(records))
    return pngs


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
