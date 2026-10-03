# External Six-Component Strain Gauge Balance for Low Speed Wind Tunnels (2014)

Samardzic, Anastasijevic, Marinkovski, Curcic (Military Technical Institute VTI, Belgrade), Isakovic.
*Scientific Technical Review*, 2014, Vol. 64, No. 3, pp. 40-46. 7 PDF pages.
Page refs below: "p.N" = PDF page N (journal page = N + 39).

## 1. Summary

The paper describes a **platform-type external 6-component balance** for small low-speed tunnels
(test section 0.4-0.6 m x 0.4-0.6 m, up to 50 m/s; p.1-2). The model sits on two struts (main + tail)
that are fixed to a triangular platform. The platform is held by six rods with elastic pivot flexures,
and each rod loads one single-force strain-gauge load cell: 3 vertical and 3 horizontal. The cells sit
under the test-section floor. A pitch/yaw positioning system is built in. All six cells use the same
gauged closed-frame flexure ("binocular" style), made from PH 13-8 Mo stainless steel. Each cell was
calibrated on its own to 0.05% FS. The assembled balance was then calibrated with dead weights and a
linear 6x6 matrix fitted by least squares. Per-cell error is about 0.25% FS (3 sigma). Errors on the
composite components reach 0.89% FS for pitching moment because no combined loads were applied in the
calibration (p.4).

The paper is short. It gives **no flexure dimensions** (the symbols Lt, b, h are defined but no values),
no electronics/DAQ details beyond the excitation voltage, and no stiffness or deflection data.

## 2. Balance architecture (p.2, Fig.1, Fig.3; p.3, Fig.4)

- Platform-type external balance. Parts (Fig.1 legend): 1 model, 2 main support strut, 3 tail support
  strut, 4 triangular platform, 5 pivot flexures, 6 rods, 7 load cells, 8 rotating frame,
  9 fixed frame, 10 pitch mechanism, 11 yaw mechanism, 12 step motor.
- The model hangs on 2 struts (main strut near the CG, tail strut aft for pitch) and the struts attach
  to the triangular platform. The platform connects to the rotating frame through **rods with pivot
  flexures at both ends**. Each rod carries only axial load, so each cell sees a single force. This is
  the stated way of keeping mechanical interaction low (p.2).
- Pitch: a parallelogram mechanism with a lead screw drives the tail strut, range -20 to +30 deg.
  Yaw: worm gear on the fixed frame, range +/-180 deg. Both use step motors under PC control (p.2).
- Cell layout (Fig.3): vertical cells ZPD and ZPL (left and right, at +/- l laterally, offset +f
  longitudinally) and ZZ (on the centreline, at -2f). Horizontal drag-direction cells XD and XL
  (at +/- n laterally). One side-force cell YY. O is the model reference point and O1 the balance
  reference point, separated vertically by c1 (for the drag cells) and c2 (for the side cell).
- Load resolution (Eq.1, p.2):
  - X = XD + XL
  - Y = YY
  - Z = ZPD + ZPL + ZZ
  - L = c2*YY + l*ZPD - l*ZPL
  - M = -c1*XD - c1*XL + f*ZPD + f*ZPL - 2f*ZZ
  - N = -n*XD + n*XL
  
  Pitching moment is the difference between the vertical cells, combined with drag times the strut
  height c1. **The large transfer distance c1 multiplies drag into pitching moment**, so any drag error
  shows up in M.
- Fig.4 (p.3) shows three CAD renderings. They highlight in red which rods and cells are loaded under
  rolling moment, pitching moment, and drag.

## 3. Load ranges (Table 1, p.2; Table 2, p.4)

| Component | Design load | (US units) |
|---|---|---|
| Lift Z | 150 N | 33.7 lbf |
| Drag X | 100 N | 22.5 lbf |
| Side Y | 75 N | 16.9 lbf |
| Pitch M | 7 N*m | 62 in-lbf |
| Roll L | 7 N*m | 62 in-lbf |
| Yaw N | 7 N*m | 62 in-lbf |

Cell ranges: the vertical cells (ZPD, ZPL, ZZ) are 200 N each and the horizontal cells (XD, XL, YY)
are 100 N each (p.3, p.4 Table 2).

For comparison, our ranges are N = 15 lbf, A = 2 lbf, m = 10 in-lbf. Their drag range is **about 11x
ours** and their pitch range about 6x ours.

## 4. Element geometry and material (p.3 Fig.5; p.4 Eq.2-4)

- **Single-force cell (Fig.5):** a rectangular closed frame (a "binocular"/ring-frame cell). F is applied
  axially through a hole or stud at top and bottom. Inside the window there are two thin bending beams
  of length Lt, width b and thickness h. The beams act as guided (S-bending) beams. Gauges 1 and 2 sit at
  one end of the inner beam surface and gauges 3 and 4 at the other end, so two gauges are in tension and
  two in compression. The photo shows the cell in a loading fixture with a load stud on top.
- Bending stress as printed (Eq.2): sigma_b = (1/2 * F * Lt) / (b h^2 / 6), and eps = sigma_b / E.
  (The guided-beam end moment per beam with 2 beams would be F*Lt/4. Check this constant before reusing
  it. Our `balance_sizing.py` uses (A/2)*L/2.)
- **Full-scale design strain:** horizontal cells 966.7 ue (Eq.3), vertical cells 920.5 ue (Eq.4).
  These are about 2x the 500 ue target in our script.
- All six cells use the same design. Only the measuring-section dimensions change with range (p.3).
- Material: **ARMCO PH 13-8 Mo stainless steel**, chosen for its strength and corrosion resistance. The
  authors say VTI experience shows it is one of the best balance steels and that **material choice
  strongly affects hysteresis, creep and repeatability** (p.3-4).

## 5. Gauges, bridges and electronics (p.3-4)

- Each cell has one full 4-active-arm Wheatstone bridge, with 2 gauges in tension and 2 in compression
  placed close together for thermal compensation (Fig.5 bridge diagram, p.3).
- Gauges: **Vishay TK-06-S082R-350** for all cells. These are 350 ohm, K-alloy (Karma), self-temperature-
  compensated for steel (06), with a dual-grid "R" pattern. Selection followed Vishay TN-505-4 (p.4).
- Excitation: **6 V**. The material and gauges allow up to 20 V (per TN-502), and the lower value was
  chosen to limit self-heating (p.4).
- Output at FS: e1 = 11.6 mV for the horizontal cells (about 1.93 mV/V, consistent with GF = 2.0) and
  e2 = 11.97 mV for the vertical cells (Eq.5-6). Note that e2 implies k = 2.17, not 2.0, so either
  the strain or the output value is inconsistent in the paper.
- No DAQ, amplifier, filtering or ADC details are given. The paper says only that the cells are
  connected to a data acquisition system and that the motors are PC-controlled.

## 6. Calibration method and rig (p.4, Fig.6)

- Each load cell was calibrated individually **before** assembly, to **0.05% FS** (p.4).
- Balance calibration used manual dead weights applied at precise points relative to the balance
  reference centre, both positive and negative, at several stations. The rig was the VTI T-38
  calibration hall (p.1, p.4).
- **Calibration body:** two crossed beams with precisely located load points, mounted on the support
  struts in place of the model. Each component was loaded in at least 5 increments from zero to maximum (p.4).
- Data reduction is VTI's generalisation of Galway (NAE LR-600). It is related to the Single-Vector
  Force Calibration method (Parker et al., AIAA-2001-0170) and allows more than one composite load vector (p.4).
- Model: {e} = [C]{F}, a **linear 6x6 matrix** (6 terms per cell) fitted by least squares. Here {F} is the
  set of cell forces, not the aero components; the aero components then come from Eq.1 (p.5, Eq.7-8).
- **No combined loads** were used in this first calibration. The authors expect accuracy to improve
  when combined loads are added (p.5 Conclusion).

## 7. Accuracy and interactions (p.5, Eq.8, Fig.7, Tables 2-3)

- **Calibration matrix (Eq.8):** the diagonal terms are about 7.9e-6 (vertical cells) and about 1.85e-5
  (horizontal cells), in output units per N.
  - The largest off-diagonal terms are about 6.2e-7 (eZZ due to XL, about 8% of ZZ's own sensitivity)
    and about 5.9e-7 (eXL due to XD, about 3% of XL's own sensitivity).
  - Most other off-diagonal terms are 1e-8 to 2e-7, which is roughly 0.1-2%.
  - Conclusion: the rod/pivot decoupling is good but not perfect, and the matrix is needed.
- **Fig.7 (p.5):** six strips of Err (% FS) against applied load (% FS, about -140 to +140), one per cell.
  Horizontal lines mark the nominal accuracy band, and all residuals stay well inside +/-0.5% FS.
- **Table 2, per cell:**

  | Cell | Range | Max |Err| | Max |Err| | Std. dev. |
  |---|---|---|---|---|
  | ZPD | 200 N | 0.40 N | 0.198% FS | 0.056% FS |
  | ZPL | 200 N | 0.39 N | 0.195% FS | 0.064% FS |
  | ZZ | 200 N | 0.44 N | 0.222% FS | 0.080% FS |
  | XL | 100 N | 0.23 N | 0.226% FS | 0.082% FS |
  | XD | 100 N | 0.16 N | 0.162% FS | 0.039% FS |
  | YY | 100 N | 0.28 N | 0.281% FS | 0.084% FS |

  The checkout reused the same load set as the fit, so these errors are optimistic.
- **Table 3, composite components:**

  | Component | Range | Max error | Std. dev. |
  |---|---|---|---|
  | X | 100 N | 0.338% FS | 0.103% FS |
  | Y | 75 N | 0.374% FS | 0.112% FS |
  | Z | 150 N | 0.218% FS | 0.085% FS |
  | L | 7 N*m | 0.886% FS | 0.213% FS |
  | M | 7 N*m | 0.871% FS | 0.246% FS |
  | N | 7 N*m | 0.414% FS | 0.154% FS |

  The moment components are the worst because they are differences of large cell forces multiplied by
  arm lengths. Roll and pitch were only calibrated to about 50-60% of range.
- In our units, the drag error of 0.338 N equals 0.076 lbf, which is about **14 drag counts** on our
  qS = 5.48 lbf. That is **3.8% of our 2 lbf A full scale**.

## 8. Figure index

| Fig. | Page | Content |
|---|---|---|
| 1 | p.2 | Photo/CAD of the full balance with 12-item legend: model on main and tail struts, triangular platform, rods with pivot flexures, cells, rotating and fixed frames, pitch/yaw mechanisms, step motor |
| 2 | p.2 | Rendering of the model with lift, drag, side force and the three moments |
| 3 | p.2 | Schematic of the cell arrangement with lengths c1, c2, f, l, n and reference points O and O1 |
| 4 | p.3 | Three renderings showing loaded members (red) under roll, pitch and drag |
| 5 | p.3 | Photo of a cell in a load fixture; CAD of the frame cell with beam dimensions Lt, b, h; gauge positions 1-4; full-bridge diagram |
| 6 | p.4 | Two photos of the balance calibration setup in the T-38 calibration hall (calibration body on the struts, weight pans) |
| 7 | p.5 | Six residual-plot strips showing Err % FS against load % FS for each cell, with +/-0.5% lines |
| Tables 1-3 | p.2, p.5 | Design loads, per-cell accuracy, composite accuracy |
| Eq.8 | p.5 | Full 6x6 calibration matrix |

## 9. Relevance to our design

### Ideas that transfer to the internal sting balance (`balance_sizing.py`)

1. **Element type confirmation.** Their frame cell uses two guided beams with gauges at the beam ends.
   That is the same mechanics as our 2-plate Z-parallelogram axial flexure, with the same 4-arm
   +e/-e/+e/-e bridge and the same GF*eps*U output relation (our `bridge_mVV`). A closed rectangular
   frame like Fig.5 is a robust form for a stand-alone axial element. It could be EDM-cut as the axial
   section, with the end-moment constant checked first (see section 4).
2. **Strain level.** They run about 920-970 ue at FS (about 1.9 mV/V) in PH 13-8 Mo. Our 500 ue target
   in 7075 is conservative. Raising the axial plates toward about 700-800 ue would help the weak A
   signal, provided fatigue, creep and the overload stops allow it. They explicitly attribute hysteresis
   and creep behaviour to the material.
   - Option: make the balance from **17-4 PH H1025 or PH 13-8 Mo** instead of 7075-T651. Use the -06
     gauge STC, and consider K-alloy gauges for better creep and drift behaviour. Steel is about 3x
     stiffer, so a steel balance needs thinner sections for the same strain, which costs machining
     precision on our tiny A plates (0.025-in class).
3. **Rods with pivot flexures as load-path decouplers.** Each cell sees only axial force because the rods
   have flexure pivots at both ends. Internally, this argues for flexure-hinged guide or link elements
   that keep N and m out of the A gauges. That matters because our script flags N->A coupling from
   plate axial strain.
4. **Pre-calibrate the element before final assembly** (they reached 0.05% FS per cell). For a
   monolithic balance that is not possible, but an early bridge check is still worthwhile: a cantilever
   dead-weight check of each bridge before wiring the full harness.
5. **Calibration lessons.**
   - Use a crossed-beam calibration body with precisely located load points, and at least 5 increments
     in both signs.
   - **Include combined loads.** Leaving them out was their main accuracy shortfall: moment errors
     around 0.9% FS.
   - Do not quote accuracy from the same load set used for the fit.
6. Use **6 V excitation on 350 ohm gauges**. This matches our 5 V choice.

### External/platform balance as an alternative for our tunnel

The paper's tunnel is a good analogue: 0.4-0.6 m square section (15.7-23.6 in) at up to 50 m/s
(112 mph). Ours is 26.25 x 11.25 in at 70 mph.

**Pros**
- Size is not limited by the 2-in pod. The cells live under the floor, so they can be large, off-the-shelf
  or commercial (single-point or S-beam cells in the 5-25 lbf class), and no gauging inside the model
  is needed.
- The model pod can be simpler, and models are easy to swap.
- Cells sit out of the flow, so there are fewer thermal and flow effects on the gauges.
- 6 components are easy, and alpha/beta drives integrate naturally (as in their pitch -20/+30 deg and
  yaw +/-180 deg).
- Each cell can be calibrated individually.
- With the short height (11.25 in), floor struts stay short, about 5 in to the centreline.

**Cons**
- **Strut tare and interference** land directly in the drag measurement. Two struts, each about
  0.3-0.5 in across and 5 in long in the flow, can give drag comparable to our wing's minimum drag
  (only about 0.1-0.2 lbf). Shielding the struts with non-metric windshields is essentially mandatory,
  plus strut-tare runs (image or tare/interference procedure).
- **Accuracy scaled to our loads is marginal.** Their drag error is 0.34% of 100 N. With commercial
  cells sized for lift (about 15-30 lbf), drag resolution of a few hundredths of a lbf is hard. A
  dedicated low-range drag cell or flexure stage is needed.
- **Moment accuracy suffers from long arms.** Pitch is a difference of large forces and is coupled to
  drag through the strut height c1 (Eq.1). Their M error is 0.87% FS.
- **Mechanical complexity is high.** Their 6-component version needs a platform, 6 rods with 12
  flexure pivots, rotating and fixed frames, pitch and yaw mechanisms, a floor seal/labyrinth gap, and
  a pressure-balanced floor cut-out for the closed-return tunnel. That is roughly 3-5x the
  fabrication effort of one monolithic internal balance.
  - A **3-component platform** would be far simpler: 2 vertical cells plus 1 drag cell, a flexure-guided
    parallelogram platform, and a single strut with a tail pitch link. It is probably comparable in
    effort to the internal balance, with easier gauging (buy cells) but harder aerodynamic tares.
- **A sidewall (one-piece) balance**, which the paper notes is used for half-models (p.1), would require
  a half-span model or a long cross-flow support to the pod. That is a poor fit for an 18-in full-span
  wing in a 26.25-in-wide section.

**Verdict.** A platform external balance is credible at our scale and removes the hardest miniaturisation
problem (the A flexure in a 2-in pod). It trades that for strut-tare and interference corrections and
more machinery. For drag-polar quality data on a 2 lbf drag range, the internal sting balance remains
the better-resolution option. A 3-component floor platform with commercial cells and a shielded strut
is a reasonable fallback or prototype path.
