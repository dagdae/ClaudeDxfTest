# ClaudeDxfTest – Schemi di cablaggio esecutivo rack LES · Hull 6376 · 07 Officer & Crew Mess

Tavole di **cablaggio esecutivo** dei rack in item list del documento Crystal/Fincantieri
`006376A6F41026007 rev.00` (07 – Officer & Crew Mess, One Line Diagram). Sono redatte con il metodo
e la grafica degli schemi Videlio HMS `21xRWxx` (rif. `21JRW10_RCK-J01`).

## Elaborati

| File | Contenuto |
|---|---|
| `output/pdf/07FRW01.pdf` | Rack **ML/F01AM** – 4 tavole A1 (PDF vettoriale) |
| `output/dxf/07FRW01_S01_AUDIO_SPEAKER-LINES.dxf` | 01/04 – Percorso audio TB1 → DSP → AMP → relè di muting → TB2 → linee 100V e altoparlanti |
| `output/dxf/07FRW01_S02_NETWORK.dxf` | 02/04 – Q-LAN / Dante / LES-NET, NPB-F01 ↔ NSW-F01, uplink in fibra K/ML07501 (giunzione per singola fibra), dettaglio T568B |
| `output/dxf/07FRW01_S03_MUTING_GPIO.dxf` | 03/04 – Interfaccia PAGA, schede MMB, bobine relè, LED di stato, 24 Vcc (PSU-F01/TB4), GPIO verso DSP |
| `output/dxf/07FRW01_S04_POWER.dxf` | 04/04 – Rete 230 V IT trifase, DJ01…DJ06, UPS-F01, TBA1/TBA2, PS block, partenze verso pannelli CP e ML/B01AM, terra |
| `output/pdf/07BRW01.pdf`, `output/dxf/07BRW01_S01_INTERFACES.dxf` | Rack **ML/B01AM** (Atrium) – attestazioni dei cavi del sistema 07 (RF antenne, LES-NET, Q-LAN, audio, alimentazione) |
| `output/cable_schedule.csv` | Cable schedule (105 righe, separatore `;`): etichetta, n° cavo nave, tipo, da/a apparato-porta-connettore, conduttori, lunghezza, foglio |
| `generator/` | Sorgente Python (ezdxf) che genera DXF, PDF e cable schedule |

I DXF sono AutoCAD R2013, in millimetri carta 1:1 (formato A1 841×594). Hanno layer separati per tipo di
segnale (`W-AUDIO`, `W-SPEAKER`, `W-QLAN`, `W-DANTE`, `W-LESNET`, `W-UPLINK`, `W-RF`, `W-GPIO`, `W-24VDC`,
`W-POWER`, `W-PE`), testo `arial.ttf` e linetype propri (`AV_DASHED`, `AV_DASHDOT`, `AV_HIDDEN`).

Rigenerazione:

```bash
pip install ezdxf matplotlib pymupdf
```

```bash
python3 generator/build.py
```

## Metodo di rappresentazione

- Ogni apparato è disegnato singolarmente (marca/modello sopra, funzione e sigla sotto) con tutte le sue
  porte. Le porte non usate sono marcate `n.c.`.
- Ogni collegamento mostra il connettore fisico lato cavo (tipo + genere: `RJ45 M`, `BNC M`, `EB F` =
  Euroblock, `PHX` = Phoenix, `IEC C13/C14`, `SCHUKO`, `LC-D`, `IDC`, `TB` = morsetto). Per i connettori
  multipolari è disegnato ogni pin.
- I cavi multipolari sono aperti a ventaglio su entrambe le estremità, con l'ovale di guaina/schermo e la
  sigla di ogni conduttore (`+ / - / S`, `P1+ P1- P2a P2b S`, `L1 L2 PE`, colori T568B, fibre TIA-598).
  I conduttori non collegati (coppie di riserva, schermi lato campo) sono marcati `×`.
- Cavi interni: etichetta a pillola `DA.DEVICE-USCITA/A.DEVICE-INGRESSO` (es. `DSP.F01-OUT5/AMP.F01-IN1`).
  Cavi di campo: numero nave `K/MLxxxxx`, tipo e lunghezza da item list.
- Morsettiere con numero morsetto, sezione, morsetti PE G/V e ponticelli; rimandi tra fogli a rombo.
- Percorsi ortogonali, incroci ridotti al minimo.

## Scelte progettuali introdotte (da confermare)

1. **DSP → AMP in analogico**: FLEX 1-2 del Core 8 Flex come ingressi (audio Atrium K/ML07101), FLEX 5-8
   come uscite verso LINE IN 1-4 del Quattrocanali. Lo schema funzionale non mostra il collegamento audio
   DSP→AMP; il link Dante dell'AMP (NPB-F01 P04) resta come da schema. Se il percorso previsto è solo
   Dante, i 4 cavi `DSP.F01-OUTn/AMP.F01-INn` vanno eliminati.
2. **Relè di muting**: FINDER 55.34.9.024.0040 (4 poli, 24 Vcc) con zoccolo 94.04 e modulo 99.02. Le linee
   100V sono interrotte su entrambi i conduttori con contatti NA. Logica fail-safe: bobina eccitata =
   audio abilitato. RLY-F03 usa i poli 1-2 per PAX PS e i poli 3-4 per PAX SB.
3. **Schermi**: audio bilanciato con schermo a massa solo sull'apparato ricevente; cavi di campo con
   schermo a terra solo lato rack, isolato e nastrato lato campo. Coppia 2 dei 2x2x1.5 lasciata di riserva su TB2.
4. **24 Vcc di muting**: PSU-F01 MEAN WELL NDR-120-24 alimentato da DJ02 (non UPS, come da sh.06), TB4
   con morsetti fusibili. LED di stato SCHNEIDER XB5EVB4/XB5EVB3 cablati come da sh.06 (punto medio pilotato da MMB).
5. **Rete IT 230 V**: carichi monofase fase-fase (L1-L2, L1-L3, L2-L3) con interruttori bipolari; uscite
   UPS GRP1-1/1-2 portate a TBA2 con cordoni IEC C14.
6. **Uplink**: SFP+ 10GBASE-SR su NSW-F01 #1, fibre 1-2 su LC1. Le fibre 3-8 sono giuntate di riserva su LC2-LC4.

## Incongruenze rilevate in 006376A6F41026007

| Punto | Fogli | Adottato |
|---|---|---|
| Cavo touch panel F04 indicato `K/ML07408` | sh.03 | `K/ML07308` (range item list K/ML07301…07308) |
| LAN dell'UPS su NPB-F01 P13 | sh.06 vs sh.05/07 (P07) | **P07** |
| Prese dei pannelli CP alimentate da DJ05 | sh.05 vs sh.06 (DJ06) | **DJ06** (L2-L3) |

## Punti aperti

- **ML/B01AM**: equipaggiamento e cablaggio interno sono definiti su `006376A6F41026002`, non fornito. La
  tavola 07BRW01 riporta solo le attestazioni dei cavi del sistema 07. Le porte NPB-B01 (T1…T6) e le
  destinazioni interne (ricevitori RF, switch, sorgente audio) vanno assegnate su quel disegno.
- **Abbinamento PAGA**: corrispondenza tra junction box (CB/403D, CB/303C, CB/203B) e zone/MMB da
  confermare con il fornitore PAGA. Tipo cavo K/CB9800x a cura PAGA.
- **Pannelli CP**: le partenze K/ML07401-404 in 3G2.5 su 150 m richiedono la verifica di caduta di
  tensione e impedenza di guasto rispetto ai carichi reali delle prese.
- Piedinature GPIO del Core 8 Flex e connettori I/O del Quattrocanali 1204 DSP+D vanno verificati sui
  datasheet di costruttore prima dell'emissione per costruzione.
- Campi "Drawn by / Approved" del cartiglio lasciati vuoti per la firma del progettista.
