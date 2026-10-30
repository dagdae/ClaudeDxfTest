# ClaudeDxfTest – Schemi di cablaggio rack LES · Hull 6376 · 07 Officer & Crew Mess

Rack wiring esecutivo dei rack in item list del documento Crystal/Fincantieri `006376A6F41026007 rev.00`
(07 – Officer & Crew Mess). Metodo e grafica seguono gli schemi Videlio HMS `21xRWxx`
(rif. `21JRW10_RCK-J01`): **un unico foglio per rack**, nessun apparato di campo disegnato, cavi di campo
identificati da numero nave, tipologia e FROM/TO.

## Elaborati

| File | Contenuto |
|---|---|
| `output/dxf/07FRW01_RACK-WIRING-ML-F01AM.dxf` · `output/pdf/07FRW01.pdf` | Rack **ML/F01AM**, foglio unico **A0 verticale**: audio e linee 100V, rete Q-LAN/Dante/LES-NET con uplink in fibra, interfaccia muting PAGA/MMB/24 Vcc, distribuzione 230 V IT con UPS e terra |
| `output/dxf/07BRW01_RACK-WIRING-ML-B01AM.dxf` · `output/pdf/07BRW01.pdf` | Rack **ML/B01AM** (Atrium), foglio unico **A1**: attestazioni dei cavi del sistema 07 |
| `output/cable_schedule.csv` | Cable schedule (99 righe, separatore `;`): etichetta, n° cavo nave, tipo, da/a apparato-porta-connettore, conduttori, lunghezza |
| `generator/` | Sorgente Python (ezdxf) che genera DXF, PDF e cable schedule |

DXF AutoCAD R2013 in mm carta 1:1. Layer per tipo di segnale (`W-AUDIO`, `W-SPEAKER`, `W-QLAN`, `W-DANTE`,
`W-LESNET`, `W-UPLINK`, `W-RF`, `W-GPIO`, `W-24VDC`, `W-POWER`, `W-PE`), testo `arial.ttf`.

Rigenerazione:

```bash
pip install ezdxf matplotlib pymupdf
```

```bash
python3 generator/build.py
```

## Convenzioni di morsettiera

**TB1 – segnali**
- Morsetti a **3 livelli** per i cavi di segnale: livelli 1/2/3 = `+ / - / S`.
  - TB1-01/02: audio K/ML07101 dall'Atrium; TB1-03 è il PE dello schermo complessivo.
  - TB1-04/05/06: stato muting MMB → GPIO DSP (livello 1 = GPI, livello 2 = COM con ponte, livello 3 di riserva).
- Morsetti a **1 livello** a valle dell'amplificazione: TB1-07…26, linee 100V. Per ogni zona: `+`, `-`,
  coppia di riserva e PE dello schermo.

**TBA1 – alimentazione e interfaccia muting**
- TBA1-01…15: interfaccia PAGA. **Sezionabili** (coltello) i morsetti del 24 V verso PA e dei rientri
  MUTE/ENABLE sotto relè PA; GND e PE a 1 livello.
- Tutto il resto è a 1 livello:
  - 16…29: distribuzione 24 Vcc;
  - 30…33: arrivo quadro cantiere;
  - 34…57: partenze DJ02/DJ05/DJ06;
  - 64…72: valle UPS (DJ03/DJ04).

## Metodo di rappresentazione

- Apparati del rack disegnati singolarmente con tutte le porte. Ogni connettore lato cavo riporta tipo e
  genere e, se multipolare, i singoli pin.
- Cavi multipolari aperti a ventaglio con ovale di guaina/schermo e sigla di ogni conduttore. I conduttori
  isolati sono marcati `×`.
- Cavi interni: etichetta `DA.DEVICE-USCITA/A.DEVICE-INGRESSO` (es. `DSP.F01-OUT5/AMP.F01-IN1`).
- Cavi di campo: solo testo al bordo rack (descrizione, `K/MLxxxxx` + tipologia, FROM/TO + metri), come nel 21JRW10.
- Rimandi a rombo:
  - numeri `01…07` = porte NETPATCH;
  - `G0…G3` = stato muting → GPIO;
  - `P1` = alimentazione PSU muting;
  - `002` = disegno Atrium.
- Alimentazione degli apparati indicata nel riquadro inferiore di ciascuno (es. `IEC C14 - 230V UPS (PSB-F03/1)`).
  I cordoni sono elencati nella cable schedule.

## Scelte progettuali introdotte (da confermare)

1. **DSP → AMP in analogico**: FLEX 5-8 del Core 8 Flex verso LINE IN 1-4 del Quattrocanali; il Dante dell'AMP
   resta su NPB-F01 P04 come da schema. Se il percorso previsto è solo Dante, vanno eliminati i 4 cavi
   `DSP.F01-OUTn/AMP.F01-INn`.
2. **Relè di muting** FINDER 55.34 (4 poli, 24 Vcc, contatti NA su entrambi i conduttori). Logica fail-safe:
   bobina eccitata = audio abilitato. RLY-F03 serve PAX PS (poli 1-2) e PAX SB (poli 3-4).
3. **Schermi**: audio a massa sul solo apparato ricevente; cavi di campo a terra solo lato rack.
4. **24 Vcc di muting**: PSU-F01 MEAN WELL NDR-120-24 da DJ02 (non UPS, come da sh.06). LED di stato
   SCHNEIDER XB5EVB4/XB5EVB3.
5. **Rete IT 230 V**: carichi fase-fase con MCB bipolari; uscite UPS GRP1-1/1-2 con cordoni C14 verso DJ03/DJ04.

## Incongruenze rilevate in 006376A6F41026007

| Punto | Fogli | Adottato |
|---|---|---|
| Cavo touch panel F04 indicato `K/ML07408` | sh.03 | `K/ML07308` |
| LAN dell'UPS su NPB-F01 P13 | sh.06 vs sh.05/07 (P07) | **P07** |
| Prese dei pannelli CP alimentate da DJ05 | sh.05 vs sh.06 (DJ06) | **DJ06** (L2-L3) |

## Punti aperti

- **ML/B01AM**: equipaggiamento e cablaggio interno sono su `006376A6F41026002` (non fornito). Porte NPB-B01
  T1…T6 e destinazioni interne da assegnare su quel disegno.
- **Abbinamento PAGA**: corrispondenza junction box (CB/403D, CB/303C, CB/203B) ↔ zone/MMB e tipo cavo
  K/CB9800x da confermare con il fornitore PAGA.
- **Pannelli CP**: K/ML07401-404 in 3G2.5 su 150 m, verificare caduta di tensione e Zs con i carichi reali.
- Verificare sui datasheet di costruttore le piedinature GPIO del Core 8 Flex e i connettori del
  Quattrocanali 1204 DSP+D.
- Campi "Drawn by / Approved" del cartiglio da compilare.
