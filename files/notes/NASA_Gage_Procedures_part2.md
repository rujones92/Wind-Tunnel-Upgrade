# NASA TM-110327 (Moore, March 1997) "Recommended Strain Gage Application Procedures for Various LaRC Balances and Test Articles" — Part 2 (PDF pages 48–94)

Page numbering: "p." = PDF page. Printed page number = PDF page − 6 (e.g., PDF p.58 = printed "-52-").
Pages 78–93 are scanned photos / blank; text pages were OCR'd and checked against page images.

## Bottom line for our balance

**None of pages 48–94 shows a balance gauge layout, bridge wiring diagram, or temperature-compensation procedure for a balance.** That material, if it is in this report, is in pages 1–47 (the other reader's range). This section covers:
- the end of Application Class IV (high-temperature gauges on titanium-matrix composites (TMC), C/C and ceramics, flame-sprayed),
- Application Class V (unusual materials: Al-Li, the inside of NTF model cavities, Ti/Al, polymer composites),
- a LaRC memo on **matching gauges for four-active-arm cryogenic balance bridges**,
- reprinted Micro-Measurements instruction bulletins for **M-Bond 450** and **M-Bond 200**,
- Addendum #4 (a high-temperature LaRC-CKAI-1B gauge install with 15 photos), and the SF-298 page.

The parts that apply to us are the **wiring and checkout steps**, the **acceptance numbers** (insulation leakage >10,000 MΩ, gauge resistance logged to 0.01 Ω, a 0.5 Ω drift rejection rule, bridge zero consistent with arm mismatch), the **adhesive cure schedules** (AE-10 room/low-temperature cure; M-Bond 450 hot cure; M-Bond 200 limits), the **moisture-coating practice** (RTV kept off the active grid), and the **gauge-matching idea** for 4-arm bridges.

---

## Page-by-page summary

### p.48–49 (printed 42–43): Class IV, Installation Type 1 (continued). LaRC compensated high-temperature gauge on TMC
- Flame-sprayed Al2O3 (Rokide) installation. Prep: micro-sandblast with 50 µm Al2O3, then coarse blast with #30 SiC. Optional plasma-sprayed basecoat ~0.001" applied within 30 min of blasting, then Rokide to a ~0.003" total basecoat.
- Active and compensating gauge pair. Check resistance after placement (Step 11). Initial bond with Norton SA rods. Remove carrier tapes and dress ridges under a microscope. Final coat gives a completed installation about **0.015" thick**.
- Optional "window-frame" Al2O3 border (0.030" gap) so the active and compensating elements stay at the same temperature when there is airflow or fast heating. Thermal blanket: 0.010" Nextel 312 with a 0.005" Al2O3 top coat, held by spot-welded straps or ceramic cement.
- Step 22: final microscopic inspection, plus a check of **gauge resistance and resistance to ground**. Lead attachment is by spot welding (no details given).
- *Relevance to us:* none for the process. The only transferable idea is that the active and compensating elements must see the same temperature (see the thermal notes below).

### p.50–51 (printed 44–45): Class IV Type 2. JP Technologies NZ-2104-120L free-filament foil gauge on Beta 21S TMC
- Leads: Hoskins 875, AWG 25, 3-conductor, with Nextel sleeving and overbraid. Inconel strap hold-downs.
- Same blast and flame-spray sequence. Extra carrier strips (~0.030" wide at 0.050" spacing) stop the convolutes from buckling. Resistance is logged on **Form FL-1**.
- **Acceptance rule (p.51, Step 16): if gauge resistance changes by more than 0.5 Ω between the Step-15 check and the pre-lead check, replace the gauge.**
- p.50 notes that Addendum #4 (p.75–92) has the detailed write-up with photos.

### p.52–55 (printed 46–49): Class IV Types 3 and 4. SiC-coated carbon/carbon and coarse ceramic composites
- Gauges must have **at least 1/4" active grid length and 2-mil wire** (foil is excluded). Short or thin grids fail at seams in the SiC coating, and gauges ≥1/4" long reduce scatter in the measured modulus.
- Lead hold-down on ~3/8" dia. blasted spots: an Omega CC cement collar on the lead (225 °F 15 min + 300 °F 1 h), then LEX-10 (0.001", air-dry 1 h, 300 °F 1 h). Omega CC is used because it has higher leakage resistance than LEX-10 and stops LEX-10 from corroding the Hoskins 875 leads.
- Type 4 basecoat: LEX-10 at ~0.002" per layer (air-dry ½ h, 225 °F ½ h, 300 °F 1 h), repeated as needed and honed, then ~0.002" plasma-sprayed Al2O3.
- p.55 contains only the closing note on lead connection (spot welding, no details).
- *Relevance to us:* none.

### p.56–58 (printed 50–52): Class V Type 1. Aluminum-lithium, room temperature to −320 °F, **no elevated-temperature cure allowed**
- Gauges: **CEA series for room temperature**, SK/WK for cryogenic. Adhesive **M-Bond AE-10**. Terminals CPF-25C/38C/50C. Jumpers AWG 38 silver-clad copper. Leads typically 3-conductor flat AWG 30 (Teflon insulation for cryogenic use). Solder 361-A.
- Surface prep: wipe with ENSOLV (never wipe back into an area already cleaned), microscopic inspection, wipe again with ENSOLV, mask and micro-blast with 50 µm abrasive, ENSOLV, then alcohol. **Start bonding immediately after the final wipe.**
- **Methyl-cyanoacrylate (including M-Bond 200) did not give enough bond strength on Al-Li**, as found in LaRC and Marshall testing. AE-10 was verified to 15,000 µε.
- **AE-10 cure (p.57):** coat both the gauge and the surface. Cover with thin Teflon tape and a silicone-rubber pad. Clamp at **15 psi**. Hold at **100 °F for at least 4 h**, or overnight at **80 °F minimum** if 100 °F is not allowed. Inspect for alignment, voids in the glue line, and debris. If a second cure cycle is needed for more gauges, blast and prep the remaining sites again.
- **Wiring good practice (p.57–58), applicable to us:**
  1. Record each gauge's resistance **to two decimal places at the solder dots**.
  2. Clean oxide off CPF terminals with a hard rubber eraser.
  3. Solder the jumpers (per NASA NHB 5300.4(3A-1)).
  4. Remove flux with a brush and Borothene.
  5. **Measure resistance again at the terminals** to confirm the jumpers and joints are good.
  6. Strip and tin all intra- and inter-bridge wires, and inspect for nicked strands before tinning.
  7. **Make intra-bridge wires equal in length and resistance.**
  8. Plan routing ahead. **Never run wires over active grids or jumpers.**
  9. Clean off all solder residue.
  10. Check the total resistance at the end of the leads.
  11. **For bridges, confirm the zero is consistent with the arbitrary resistance differences of the four gauges.**
  12. **Leakage to ground > 10,000 MΩ (10 GΩ).**
- Moisture-proofing (p.58): no single recipe. The coating is chosen for the temperature range, the moisture exposure, the **"reinforcing effect on thin surfaces to be strained,"** and how long the test runs.

### p.58–60 (printed 52–54): Class V Type 2. Gauges inside wind-tunnel model cavities (NTF, maraging steel, −275 °F to 180 °F), covered with body filler
- Gauge **WK-06-060BN-350 with option W** ("works well"). Adhesive **M-Bond GA-2** (preferred) or AE-10. Leads 3-conductor stranded AWG 30 silver-plated copper. Solder 361-A.
- GA-2 cure: air-dry the coated parts ≥5 min, Teflon and rubber pad, **10 psi**, then **≥6 h at ≥125 °F** (or 4 h at 150 °F). **Post-cure 8 h at ≥125 °F** (or 6 h at 150 °F, or 2 h at 200 °F) before filling the cavity.
- Wiring checks are the same as above, plus **etching (Tetra-Etch) any Teflon leads that will be potted**.
- Cavity fill: Insta-Pak 200 foam (1:1 by weight), set 2 h, trimmed to about 1/16" over the gauge. Then Hysol 9309 at about 1/32", cured ≥4 h at ≥75 °F. Then Hysol 9309 with S-100 CarboSpheres (1.5:1 spheres to adhesive by weight) to fill, and sand to contour. Record final electrical checks.
- *Relevance to us:* useful if gauges are ever placed in the wing or pod. The foam layer keeps the hard filler from loading the gauge.

### p.60–62 (printed 54–56): Class V Type 3. Titanium/aluminum alloys, −300 °F to 650 °F (not validated)
- WK gauges, BLH TL-56 terminals, **BLH PLD-700** adhesive (manufacturer's cure, then **post-cure 700 °F for 30 min**). Leads 326-GJF. Gold-alloy solder spheres (81.5Au/8.5Ag/10Ge, melting at 770 °F). Thermocouple INC-E-MO-062.
- Wiring: record resistance to two decimals at the terminals and again at the end of the leads. Leakage **>10 GΩ**.
- **Moisture-proofing (p.62):** clean with alcohol. Apply **GE RTV-159 about 0.050" thick over the terminals, solder joints and ribbons, and keep it off the active grid**. Apply with the part and the RTV at **≥72 °F and ≤40 % RH**. **Air-cure overnight** before testing. Keep RTV low over wiring so it does not crack in cold excursions. Lightly micro-blast the RTV sites first.

### p.62–64 (printed 56–58): Class V Type 4. Adhesive/polymer composites to 450 °F (adhesive cure limited to 250 °F)
- WK gauges, **M-Bond 600**, CPF terminals. Leads AWG 30 7/38 silver-plated copper with Teflon insulation. Solder 570-28R.
- Optional M-Bond 600 basecoat: air-dry 10 min, **30 psi**, ramp to 250 °F over ≥30 min, hold 1 h, then lightly blast.
- Gauge bond: air-dry 10 min, CHR type C tape, rubber pad, **30 psi, 250 °F for 2 h. Do not post-cure** (composite temperature limit).
- Wiring (p.63–64): check gauge resistance against the manufacturer's spec. **Provide mechanical strain-relief loops in both the gauge ribbons and the lead wires near the gauge.** Inspect stripped wire for nicks. Remove flux. Check the end-of-lead resistance. **Leakage >10 GΩ.**
- Moisture: usually none needed. If required, **3140 RTV or RTV-159**.

### p.65–68 (printed 59–62): LaRC memo, 18 Apr 1994, "Matching Cryogenic Strain Gages" (T. Moore)
- Problem: each gauge has its own apparent-strain (thermal output) curve. If four gauges are picked at random for a **four-active-arm bridge**, their mismatch shows up as bridge thermal output. The effect is larger at cryogenic temperatures.
- Method: temporarily bond **16 gauges from one type and one lot** (MM C-891113-B) to a matching disc with **M-Bond 200**. Wire each for **3-wire quarter-bridge** readout (AWG 40 jumpers, equal length and resistance; AWG 32 silver-clad Teflon leads). Run them through a temperature cycle and record each gauge's apparent-strain curve.
- **Fig. 1 (p.68), gauge matching disc:** a 4" dia. × 1" thick disc carrying two Kapton strips (0.2" × 2.5" × 0.002") and 16 CPF-38C terminals bonded with M-Bond 610. There are 8 SK-series gauges on each side of a central type-T thermocouple.
- Removal: soak at **170 °C for 2 h**. The M-Bond 200 breaks down and the gauges lift off. Then clean with Inhibisol, pumice (S.S. White #3), ammonia neutralizer plus hot water, and 200-proof alcohol. Inspect under a microscope.
- Pre-test check (p.67): excitation reads 5.000 V, each channel reads **within ±0.005 V** on the DAS, temperature reads 1 mV/°C. Turn off excitation once the part warms back to −10 °C, so condensation does not short the gauges.
- **Matching criteria (p.67):** gauges are grouped in fours by (1) peak output over the temperature excursion, (2) loop (difference between the cooling and warming runs at the same temperature), and (3) nonlinearity. **Each must be within ±0.015 mV at 5 V excitation (±3 µV/V).** Matched sets are catalogued for four-arm bridges in cryogenic transducers, **including wind-tunnel balances**.

### p.69–70: Micro-Measurements M-Bond 450 bulletin (reprint)
- Two-part solvent-thinned epoxy. Glue line can be as thin as 0.0001". Service: short term −452 to +750 °F, long term −452 to +500 °F. Elongation >5 %. Shelf life 6 months. **Pot life 6 weeks** after mixing. Let it stand **24 h after mixing** before use.
- Cure process:
  1. Coat the part and air-dry 10–30 min (75 °F, 50 % RH).
  2. **B-stage at 225 °F for 30 min** (ramp 5–20 °F/min). B-staged parts can be stored up to 1 week; re-dry 10 min at 225 °F if they may have picked up humidity.
  3. Transfer the gauge on MJG-2 Mylar tape and add no more adhesive.
  4. Lay on Teflon film, a 3/32" silicone pad and a backup plate. Clamp at **40–100 psi**.
  5. **Cure at 350 °F for 1 h.**
  6. **Post-cure ≥1 h at ≥50 °F above maximum operating temperature** (maximum 550 °F), stepping up 50 °F at a time with 60 min at each step.
- Do not use a general-purpose forced-air oven, because it spreads contaminants.

### p.71–74: Micro-Measurements bulletin B-127, "Strain Gage Installations with M-Bond 200"
- Cyanoacrylate, room-temperature cure. Normal range **−25 to +150 °F**. Apply at 70–85 °F and 30–65 % RH. Shelf life 9 months unopened (refrigerate unopened bottles, warm to room temperature before opening).
- **Humidity weakens the bond, so a protective coat is required. It embrittles with age and heat, and is not recommended for installations meant to last more than 1–2 years.**
- Surface prep:
  1. Degrease with CSM-1A, or GC-6 isopropyl alcohol on titanium and plastics.
  2. Dry-abrade with 220/320 grit, then wet-abrade with 320/400 grit and M-Prep Conditioner A.
  3. **Burnish layout lines with a 4H pencil on aluminum** (do not scribe).
  4. Scrub with Conditioner A until a clean swab stays clean, then wipe in one slow stroke.
  5. Apply Neutralizer 5A and wipe in one slow stroke, never back and forth.
- Bonding:
  1. Place the gauge face-down on clean glass with the terminal ~1/16" away, and pick both up on PCT-2A tape.
  2. Align the triangle marks, then lift the tape at about 45°.
  3. Apply catalyst thinly (wipe the brush about 10 strokes first) and let it dry ≥1 min.
  4. **Do the next three actions within 3–5 s:** put 1–2 drops of adhesive at the fold ½" outside the gauge area, make one firm wipe-down with gauze at about 30°, then hold thumb pressure for ≥1 min (several minutes if below 30 % RH or below 70 °F).
  5. Wait 2 min, then peel the tape back over itself.
- Figures 1–11 are hand-sketch illustrations of each step (p.72–74).
- Final installation (p.74): mask open-faced grids with PDT-1 tape before soldering, remove flux with RSK-1 rosin solvent, and choose a coating from Catalog A-110.

### p.75–92 (printed 69–71 plus photos): Addendum #4. LaRC-CKAI-1B compensated high-temperature gauge on Inconel 100 and Beta 21S TMC (Moore and Lamm)
- Expanded version of Class IV Type 1, with a 0.6" × 0.7" blast area and 3M #64 tape.
- **Photos #1–#15 (p.78–92, some printed upside down):** coupon with Al2O3 basecoat, gauge on carrier, first flame spray, tape removal, final spray, remasking for the window-frame border (#8–#11), completed elements, thermal blanket, strapped blanket, and the finished installation ready for leads.
- *Relevance to us:* none.

### p.93: blank. p.94: SF-298
NASA TM-110327, March 1997, WU 519-20-21-01, 90 pages. LaRC uses more than 10,000 gauges per year.

---

## What applies to our 7075-T651 3-component balance

### 1. Bridge wiring (necks and axial flexure)
- This range has **no balance wiring diagrams**; see the part-1 notes. The general rules it does give:
  - **Equal-length, equal-resistance intra-bridge jumpers** (p.57/58, p.60). On our necks, arms that are physically far apart (top and bottom faces) should get matched jumper lengths, so the jumpers do not add unequal resistance and unequal TCR (zero shift with temperature).
  - **No wires over active grids or jumpers** (p.58). This matters on the 0.50" neck faces and inside the 0.75" axial window. Plan terminal positions (CPF-type tabs on the rails or on the body, off the flexure) before bonding.
  - **Strain-relief loops** in gauge ribbons and leads (p.64). This is critical where leads cross from the live (model) side to the ground (sting) side of each flexure. A taut wire across the 0.025" axial plates would carry load and cause hysteresis.
  - 3-wire quarter-bridge wiring for testing single gauges (p.65). This is a handy way to check each gauge's response before closing the full bridges.

### 2. Temperature compensation
- The matching memo (p.65–67) confirms that **four-active-arm bridge thermal output comes from arm-to-arm mismatch in apparent strain**. LaRC solved it at cryogenic temperature by matching gauges in fours to within ±3 µV/V.
- For us (room temperature with tunnel heating of about 10–30 °F), **buy all 12 gauges from one lot**, with STC-13 to match aluminum's ~13 ppm/°F.
- A hobbyist version of the match is possible. Before final bridge closure, wire each bridge (or each gauge in quarter-bridge), then warm the whole balance slowly by 20–30 °F (oven or warm box, uniform temperature, no load) and log the zero drift. Compensate any remaining zero-vs-temperature with a small series resistor in the correct arm (the procedure itself should be in part 1).
- Keep both sides of each bridge at the same temperature (p.48–49, window frame and blanket). In a closed-return tunnel that warms as it runs, avoid airflow hitting one face of a neck. A pod or windshield over the balance helps.

### 3. Adhesive and cure. **Possible geometry and material conflict**
- **M-Bond 450 or M-Bond 600/610 at 350 °F (p.70) is the transducer-grade choice, but 7075-T651 is aged at about 250 °F.** One hour at 350 °F, plus post-cure steps, starts to over-age it. That means some loss of yield strength (it moves toward T73) and possible distortion of the 0.025" plates if they are not clamped evenly.
  - Our stress margins (SF on yield in `balance_sizing.py`) should allow for a few percent loss. Otherwise choose a lower-temperature cure such as M-Bond 610 at about 250 °F (check its datasheet) or AE-10.
  - Flag for the design team. Also check the 350 °F rating of the gauge backing (EA vs. CEA) and the solder.
- **AE-10 (p.57):** room or low-temperature cure, **15 psi, 100 °F for ≥4 h** (or overnight at ≥80 °F). It is hobbyist-friendly, does not affect the 7075 temper, and is validated on aluminum alloy (Al-Li) to 15,000 µε. It is a reasonable fallback, but expect more creep and hysteresis than with a hot-cured epoxy at our 500 µε level.
- **M-Bond 200 (p.71):** fastest option, but humidity-sensitive, embrittles, has a **1–2 year life**, and **was rejected by LaRC on Al-Li for bond strength** (p.57). Use it only for a prototype or proof balance, not the final transducer.
- Clamping needs a backup plate and a 3/32" silicone pad at 40–100 psi (p.70). Inside the 0.75" axial window, design a small clamp block or wedge that fits between the plates and supports the 0.025" plate from the opposite side so it does not bend.

### 4. Moisture protection
- Coat the terminals, solder joints and ribbons with **RTV 3140 or RTV-159 about 0.050" thick, kept off the active grid** (p.62, p.64). Apply at ≥72 °F and ≤40 % RH and cure overnight.
- **Geometry flag (p.58):** LaRC warns about the "reinforcing effect on thin surfaces." On our **0.025" axial plates**, the gauge, adhesive and any coating over the grid add stiffness and can creep. Keep coatings thin over the grid (or use a thin film such as M-Coat A/D on the grid and put RTV only on the joints), and apply them the same way on both plates and both faces. The calibration will absorb whatever reinforcement remains, as long as it is stable.

### 5. Acceptance checks a hobbyist can do
| Check | Criterion | Tool | Source |
|---|---|---|---|
| Gauge R at solder dots after bonding | Log to 0.01 Ω; within manufacturer tolerance (e.g., 350 ± 0.3–0.5 %) | 4½-digit DMM, 4-wire if possible | p.57, p.63 |
| R again at terminals after jumpers | Matches dot reading to within lead/jumper resistance | DMM | p.57 |
| R drift between steps | **>0.5 Ω change means replace the gauge** (stated for high-temperature gauges; a strict but useful rule for 350 Ω foil) | DMM | p.51 |
| End-of-lead total R | Gauge plus lead R as expected | DMM | p.58, p.64 |
| Bridge zero | Consistent with measured arm mismatch (ΔR/R/4 → mV/V) | DMM + excitation supply | p.58 |
| Insulation leakage to ground | **>10,000 MΩ (10 GΩ)** | Megohmmeter at low test voltage (≤50 V; never high voltage through gauges, short each bridge's leads together first) | p.58, 60, 62, 64 |
| Visual | Alignment, glue-line voids, debris (magnifier) | Loupe or USB microscope | p.57, 59 |
| Thermal match (optional) | Bridge zero drift vs. ΔT; LaRC cryogenic standard ±3 µV/V | DMM / ADC + warm box | p.67 |
| Instrumentation sanity | Excitation reads exactly (e.g., 5.000 V); unloaded channels stable near zero | DMM | p.66–67 |

A cheap DMM cannot test the 10 GΩ requirement. A megohmmeter or a high-impedance electrometer method is needed. Readings of only tens of MΩ point to moisture or flux residue: clean, dry and coat.

### 6. Gauge-choice notes
- LaRC uses **CEA-series** gauges on aluminum at room temperature (p.56) and WK-06-060BN-350 inside models (p.58). Our 350 Ω STC-13 (CEA-13 or EA-13) choice is consistent with LaRC practice.
- The ≥1/4" grid rule (p.52) applies only to coated C/C composites, not to our 0.062" grids on aluminum.
- If we use CEA (polyimide with pre-attached copper tabs), the cure temperature limits above still apply. Check the cure and solder temperature compatibility for whichever adhesive is chosen.
