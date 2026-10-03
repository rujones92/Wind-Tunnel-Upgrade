# Bharath Institute - "Design and Fabrication of Three Components Internal Strain Gauge Balance"

Source: `references/Bharath_3comp_Internal_Balance.pdf` (68 PDF pages; B.Tech project report, Guru Sankar, Nikhil, Naga Saikiranmai, Navya; guides C. Suresh Kumar / M. Ramakrishna; Bharath Inst., Chennai, May 2021).
Page numbers below are **PDF page numbers** (report page number in brackets where useful). PDF has a usable OCR text layer; figures were checked from the page images.

## 1. Summary

A 4-student undergraduate report. They CAD-modelled (CATIA) a 300 mm long round cantilever "sting balance" with two reduced 8 mm square sections, ran a long series of linear ANSYS static cases (deflection and some von Mises stress) for steel vs aluminium under "longitudinal" (lift), "axial" (drag) and "torque" (they call it pitching moment) loads, compared tip deflection against hand formulas, and machined one aluminium part with a gauge stuck on it. **There is no bridge design, no gauge layout, no output/sensitivity calculation, no calibration, no interaction matrix and no wind-tunnel test.** The conclusion's "sensitivity" and load-range claims are not supported by any data. Credibility: low. It is useful mainly as a list of mistakes to avoid.

## 2. Page map

| PDF p. | Content |
|---|---|
| 1-16 | Title, certificates, acknowledgements, abstract (p6), contents/lists |
| 17-19 | Ch.1 strain-gauge basics (generic, partly copied vendor marketing text, e.g. Encardio-Rite, p18) |
| 20-22 | Ch.2 literature review (Pieterse 2008, Hou & Twu, Lee et al. water-tunnel balance, Ladson/Webb monolithic balance, Tomin 2020) - one-paragraph summaries |
| 23-25 | Ch.3 concept: 15 mm dia x 300 mm cantilever with two 8 mm square sections |
| 26-27 | Ch.4 CAD (Fig 4.1-4.3) and dimensioned drawing |
| 28-34 | 5.1 lift-only loading: FEA pictures, Table 1 (FEA) & Table 2 (hand calc) deflection 1-300 N, Fig 5.1.7 |
| 35 | 5.2 mesh (tet, 233,328 nodes / 156,000 elements) and "mesh independence" (tip deflection only) |
| 36-38 | 5.3 "torsional" (pitching-moment) analysis, Table 3 twist angles |
| 38-48 | 5.4 combined drag + lift: FEA pics, Table 4 (FEA), beam-column formula and Table 5 (hand) |
| 49-63 | 5.5/5.6 moment + lift, moment + axial: FEA pics, Table 6 (von Mises stress), Tables 7-9, charts |
| 64-65 | Ch.6 results/discussion: bridge types in words, model mounting, DAQ, Fig 6.1-6.2 photos of fabricated part |
| 66 | Ch.7 conclusion (load range / "sensitivity" claims) |
| 67 | References (7) |
| 68 | blank |

## 3. Their balance geometry (p24-27, p65)

- One-piece round bar, overall 300 mm. Drawing Fig 4.3 (p27) dimension string: **60 | 40 | 100 | 40 | 60 mm**.
  - Two 60 mm end lugs (round, ~15 mm dia) each with two transverse cross-holes (dims read Ø5.04 / Ø5.09 mm) for screws/pins: one end attaches to the model, the other to the sting.
  - Two 40 mm long **8 x 8 mm square necks** (gauge sections), milled from the round stock.
  - A 100 mm round centre section between the necks.
  - Neck centre-to-centre spacing therefore ~140 mm (5.5 in). Neck-to-shoulder transitions drawn with sharp corners (no fillets).
- Body diameter: text says 15 mm (p24); front view label is hard to read.
- Text: "incentive of circular cross-section is to extract the pitching moment" (p24) - no actual explanation of how N, A, m are separated.
- Material: aluminium (E = 71.7 GPa, G = 26.9 GPa - the MatWeb 7075-T6 modulus, but alloy/temper never stated) and steel (E = 210 GPa, G = 77.2 GPa) both analysed; the fabricated part (p65) is aluminium.
- **No dedicated axial (drag) element.** Abstract (p6) admits axial strain is too small to measure with gauges directly, yet the report still claims 3 components.

## 4. Design loads

- Never derived from any tunnel/model aerodynamics. Arbitrary sweeps: lift 0.1-300 N, drag 5-300 N, "torque" 2-10 N.m (p28-63).
- "Beam is designed to withhold maximum sensitivity of 100 grams" (p24) vs "minimum load of 100 grams" (p25) - contradictory.
- Conclusion (p66): aluminium "load capacity 1-100 N, sensitivity 1 N with full bridge"; steel "5-300 N, sensitivity 5 N". No calculation or test supports these numbers.

## 5. Calculations (and errors)

**Bending deflection (p31-34):** I_circle = pi d^4/64 = 0.2485e-8 m^4 (correct for 15 mm). Then:
- I_square computed as bd^3/12 + db^3/12 = 0.0682e-8 m^4 - this is the polar value; bending I of 8 mm square is 0.0341e-8.
- Then "I = I_c - 2 I_sq - 2 I_screw" = 0.107e-8 m^4 - physically meaningless (subtracting the inertia of the neck from that of the round bar). A stepped cantilever must be handled by integrating M/EI along the length.
- delta = WL^3/3EI = 11.73 mm at 100 N (Al) - arithmetic consistent with their I, and FEA gives 14 mm (Table 1, p30-31), so the agreement is ~15-20% and partly luck.
- p60 uses yet another I (1.04e-9) for the same beam.

**"Torsion" = pitching moment (p36-38, p61):** they apply the pitching moment as a torque about the balance's long axis (FEA images p36-37 show twist about the bar axis) and compute twist = TL/GJ. Pitching moment is a bending moment about the lateral axis, not torsion - torsion about the sting axis is rolling moment. Additionally Table 3 values labelled "rad" are actually **degrees** for aluminium (my check: 10 N.m, 0.3 m, G 26.9 GPa, J of 15 mm rod -> 0.0224 rad = 1.286 deg; table says "1.286 rad"); steel column is ~2x the correct 0.448 deg.

**Combined lift + axial (p46-48):** beam-column formula delta = (W/P)(tan(uL)/u - L), u = sqrt(P/EI) (compressive axial). Reasonable formula, but Table 5 is garbled and the values repeat in blocks (0.0006, 0.006, 0.012 ...) independent of axial load - looks copy-pasted. Pcr of their beam ~2.1 kN (Al), so 300 N axial gives only modest amplification anyway.

**Stress (p53-58, Table 6 p58):** von Mises max = 35.7e7 Pa (2 N.m + 5 N) up to **103-104e7 Pa = ~1030 MPa** at 300 N lateral, identical for steel and aluminium (expected - statically determinate). They never compare this to yield: 1 GPa is ~2x 7075-T6 yield and above most steels. Table 6 is also internally inconsistent (6 N.m + 5 N gives 100 MPa, less than 2 N.m + 5 N at 357 MPa). Torque column units given as "N/m".

**Strain / bridge output:** never calculated. My check with their geometry (moment arm to the root-side neck ~0.24 m, Z_sq = 8.53e-8 m^3): 1 N -> 2.8 MPa, 39 ue; 15 N -> 590 ue; 100 N -> 281 MPa, 3900 ue (Al) - i.e. their claimed 100 N "capacity" is ~8x the usual 500 ue design strain and at/above yield for 6061. Axial: 8.9 N (2 lbf) on 64 mm^2 -> **~2 ue** - unmeasurable, confirming the abstract.

**Text errors on bridges (p19, p64-65):** "strain gauges don't get influenced by temperature" (wrong); "full bridge sensitivity is twice the quarter bridge" (a 4-active-arm full bridge is ~4x a quarter bridge; 2x is a half bridge); bridge output formula garbled.

## 6. FEA

ANSYS R18 static structural, tetrahedral mesh 233,328 nodes / 156,000 elements (p35). Mesh "independence" checked only on tip deflection (flat at ~0.005 m, p35) - not on stress at the neck, which is what matters. One end fixed, point load / moment at the other end. Results are deflection contours and a few von Mises plots; no strain extraction at gauge locations, no cross-coupling study. Load sweeps are huge in number (~90 figures) but low in information.

## 7. Gauge placement, wiring, fabrication, calibration

- Gauges: "attached on the square sections" (p24). Photo Fig 6.2 (p65) shows one foil gauge on a neck flat with two red leads - looks like a quarter-bridge trial ("we had tried with quarter bridge configuration", p65). No gauge type, resistance, GF, adhesive, layout, bridge assignment or temperature compensation stated.
- Fabrication (p65 Fig 6.1): aluminium bar, turned round with milled square necks and cross-drilled end lugs. Looks lathe + mill; no surface finish, fillet or heat-treat info.
- Mounting: model "mounted rigidly with the screws ... model gets in contact with the balance only at the point of contact with the strain gauges" (p65) - confused; if the model touches the gauged sections it creates a load short-circuit.
- DAQ: generic "DAQ connected via serial connector ... report software" (p65).
- **Calibration: none.** "Further scope of work is to practically analyze the beam" (p65). No sensitivities, interactions, linearity or errors.

## 8. Assessment

Student work with fundamental errors: pitching moment modelled as torsion; wrong section property method; degrees reported as radians; FEA stress far beyond yield not noticed; no axial element; no strain/bridge/output sizing; no calibration or test data; conclusion numbers unsupported. Literature review is superficial but the reference list points to better sources (Pieterse 2008 Stellenbosch thesis; Lee et al. 2005 water-tunnel balance; Webb/Ladson 2001 monolithic balance thesis - those are worth reading instead). **Do not use any numbers from this report as design data.**

## 9. Comparison with our design (balance_sizing.py)

**Numbers that check/contradict:**
- Their 8 mm (0.315 in) square neck has section modulus 0.00521 in^3 - essentially identical to our 0.50 W x 0.25 H neck (0.00521 in^3). At our worst neck moment (28 in-lbf = 3.16 N.m) both give ~5,400 psi / ~520 ue, which is what our script targets. Independent geometry, same answer - mild sanity check of our sizing, nothing more.
- Their beam with no axial flexure gives ~2 ue for our 2 lbf drag -> strongly supports our decision to use a dedicated parallelogram axial flexure (~500 ue).
- Their neck spacing is 5.5 in on a 11.8 in long balance; ours is 2.4 in. Their balance would not fit our ~2 in pod / 30 in test section layout; our shorter spacing is appropriate but costs N resolution (script already accounts via sqrt(2)*M_res/s).
- Their 1 N "sensitivity" claim would correspond to ~39 ue (~0.08 mV/V full bridge), plausible as a resolution figure but they never measured it.

**Mistakes to avoid (all relevant to us):**
1. Pitching moment is bending about the lateral (y) axis, not torsion; roll is the torsion load - our script already treats roll as torsion on the necks (correct). Make sure FEA load cases apply m as a bending moment.
2. Do mesh convergence on **stress/strain at the gauge location**, not tip deflection.
3. Always compare FEA von Mises to yield with an overload case (they reached ~1 GPa unnoticed). Our script does SF checks - keep that for the FEA too, including cross-hole and fillet stress concentrations.
4. Fillet neck/flexure transitions; keep attachment cross-holes well away from gauged sections (their lugs with Ø5 mm cross-holes sit right next to the necks).
5. Use 4-active-arm bridges with temperature-matched gauges (STC for 7075); a single gauge in quarter bridge is not a balance.
6. The model must touch the balance only at the model-end attachment - any contact elsewhere (they describe contact "at the strain gauges") short-circuits load.
7. Plan calibration from the start (load jig, weights, interaction matrix) - the report stops at fabrication.

**Useful ideas (minor):** round bar with milled flats for necks is an easy, cheap manufacturing route; cross-drilled pin/screw lugs at both ends for model and sting attachment (we would prefer a taper or keyed/dowelled flange for repeatability).
