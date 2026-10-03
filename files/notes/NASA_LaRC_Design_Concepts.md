# NASA LaRC Strain Gage Balance Design Concepts (Rhew, 1999) - reading notes

Source: `references/NASA_LaRC_Strain_Gage_Balance_Design_Concepts_1999.pdf` (18 PDF pages; journal pages 525-541, PDF p.18 is blank).
Page references below are given as **PDF page (journal page)**, e.g. p.10 (534).

## 1. Summary

An overview of how NASA Langley designs, builds, gauges and calibrates internal sting-mounted six-component balances. It is a process and philosophy paper, not a design handbook. It gives only a few hard numbers (output target, materials and hardness, EDM tolerances, bridge zero-balance limit, gauge and adhesive part numbers, calibration matrix size and achieved accuracy). It has **no sizing formulas** apart from the strain-output relation. Its core messages:

1. Make the balance from **one piece of material** (no joints). Joints cause hysteresis and zero shift.
2. **Match the balance's full-scale loads to the test's expected loads** to get the best resolution.
3. Size each measuring section for **1-1.5 mV/V at full scale**, while keeping strain safe under **all six loads applied together**.
4. Make each bridge sensitive to its own component and insensitive to the others. Do this through the section geometry, gauge placement and bridge wiring.
5. Do the work carefully: EDM finishing passes, tolerances of 0.0002-0.0005 in, an experienced gauger, temperature compensation, and a full second-order calibration.

## 2. Design rules and numeric criteria

### Inputs needed before design (p.4 / 528)
Expected loads in all 6 DOF; where the balance sits in the model; maximum diameter and length; environment (temperature, pressure, moisture, dynamics, airflow, corrosion); model-end (metric) and sting-end (non-metric) interfaces; required accuracy and resolution; electrical interfaces; DAQ specs; data-reduction software; set-up and checkout equipment. Start from a similar past design. Iterate with strength-of-materials code; FEA is "beginning to be evaluated" for stress concentrations, thermal behaviour and optimisation.

### Load matching (p.3-4 / 527-528)
- Make full-scale (FS) loads match the expected test loads as closely as possible. This gives the best resolution.
- If one test spans very different regimes, it is better to build **two balances** (e.g. one for performance and one for stability and control).

### Materials and heat treatment (p.6 / 530)
| # | Material | Condition | Use |
|---|---|---|---|
| 1 | 17-4 PH or 15-5 PH stainless | H925, Rc 40-42 | most common |
| 2 | C-200 18% Ni maraging | H900, Rc 41-45 | cryogenic |
| 3 | C-300 18% Ni maraging | H900, Rc 52-55 | high capacity |
| 4 | 2024-T4 aluminium | | |
| 5 | **7075-T6 aluminium** | | |
| 6 | Be-Cu | | extreme temperatures |
- The material must have "transducer quality". Choose it early using simple diameter-to-load calculations. A more ductile, lower-strength material is sometimes preferred.
- Also consider corrosion and moisture, and how well gauges bond to and behave on the material.
- Heat treat to the vendor's spec **after rough machining and before EDM**. Certify with a Rockwell C hardness test (p.10 / 534).

### Sting and model interfaces (p.6-8 / 530-532; Figs 6, 7)
- **Sting end:** a tapered cylinder at **1 in/ft taper**, with a **keyway for roll reaction**, held by a **double nut** (standard) or set screws (for small balances or cryogenic use). Taper maximum diameters range from 0.3125 to 5.0 in.
  - Drawbacks: the taper is hard to machine and wears. The keyway is a sliding fit, so it has roll slop, and the key bears on a small area.
  - LaRC prefers a **flange fit** where the diameter allows. Most semi-span balances use one.
- **Model end:** a cylindrical fit with an **interference-fit dowel pin** that locates the model. This joint defines the load axes, so any misalignment shows up directly as error.
  - The "front-end expander" (Fig 7) expands a sleeve into the model bore. Sizes range from 0.625 to 3.1 in. It is not used for cryogenic work or for high load-to-diameter performance balances.
  - Roundness, cylindricity and the true position of the dowel hole are critical.

### Measuring sections (p.8-10 / 532-534; Figs 8, 9)
- There are usually **three sections**: one **axial** section, and two **"cage" sections** (forward and aft) that between them resolve N, m, Y, n and roll. This is the two-moment (two-station) concept.
- **Output target: 1 to 1.5 mV/V at FS.**
- Strain relation for a 4-active-arm bridge: `strain = Vout / (Vin x GF)`, i.e. Vout/Vin = GF x strain (p.9 / 533).
- Iterate the design to reach that output while keeping strain "safe" with all six components applied at once.
- **Axial section (Fig 8):**
  - The gauged **measuring beam** is a "slotted-T" beam (one per side), placed **as close to the balance centreline as possible** to minimise moment effects.
  - The slot makes it act as a **single bending beam** and reduces its strain under normal force.
  - **Separate flex beams** (14 per side on the NTF balance) carry the other loads, which reduces the load passed into the measuring beam.
  - In short, the gauged element is **separated from the load-carrying flexures**.
- **Cage sections (Fig 9):**
  - Beams usually have a rectangular cross-section.
  - **Notched or "stress-riser" beams** are used to raise sensitivity when needed.
  - **Stiffening end shoulders** transition the beams into the model and sting ends to **minimise nonlinearities**.

### Fabrication (p.10-11 / 534-535; Fig 10)
1. Material certification plus ultrasonic inspection for voids (NASA TM 84625), for fatigue and fracture reasons.
2. Conventional rough machining (turn, mill, grind), followed by an in-process QA check.
3. Heat treat, with certification and an Rc hardness test.
4. Wire and plunge EDM.
   - Use wire EDM wherever possible for flats and through-holes (cages, axial outline).
   - **Three EDM passes:** one rough pass in fast mode to within about **0.050 in** of final size, then **two slow finishing passes**. The finishing passes control tolerance and limit the EDM recast damage that reduces fatigue life.
   - Measuring-beam tolerance is **0.0005 to 0.0002 in**.
5. QA to about 0.0002 in (CMM, height gauges, bore, ring, plug and taper gauges), with a report of actual versus design dimensions.

### Strain gauging (p.11-13 / 535-537; Fig 11)
- Use a gauger with more than 5 years of transducer-quality experience. Check all surfaces under a microscope for sharp edges and defects first. Procedures: NASA TM 110327 (Moore, 1997).
- Materials:
  - **Gauges:** Micro-Measurements C-891113-A or -B, **350 ohm**
  - **Adhesive:** **M-Bond 610** (heat-cured epoxy)
  - **Moisture protection:** GageCoat 8 or **M-Coat B**
  - **Solder:** MM 361A
  - **Wire:** stranded **silver-clad copper, Teflon insulated, AWG 30-44**
  - **Temperature sensors:** type J or T thermocouples, Hy-Cal EL-700T platinum RTD
- After installation, a QA check of gauge location and alignment.
- **Bridge (Fig 11):** 4 active arms. Gauges 1 and 3 are in tension and 2 and 4 in compression, placed in opposite arms so their outputs add.
  - A **thermal-compensation wire** (nickel, with silver-clad copper) sits in series in one arm.
  - A **bridge-balance wire** (Manganin) sits in another arm.
- **Zero balance within 0.4 mV/V** using Manganin wire.
- **Temperature compensation:** add nickel wire to cancel output drift with steady temperature at constant load.
  - Fig 12 shows a typical acceptance run from 80 to 180 to 80 F.
- **Wiring:**
  - Use twisted shielded pairs (signal and power) where possible, with an outer sleeve of nylon or fibreglass.
  - After wiring, **temperature-cycle the balance over its operating range +50 F** to relieve the wiring.

### Calibration (p.13-16 / 537-540; Figs 13-15)
- Calibrate in conditions as close to the tunnel's as possible. Most LaRC balances are calibrated at room temperature to full scale.
- **Math model:** a 6x27 **second-order iterative** model. Each output is a sum of 6 linear terms, 6 squares and 15 cross-products. It is inverted to give: corrected load = output x sensitivity - sum of interaction terms.
- **Load schedule:**
  - **729 loading points**, followed by **3 proof loadings** (two three-component and one six-component combined) to verify the matrix.
  - Accuracy is reported as **2-sigma of back-calculated residuals**.
- **Hardware and technique:**
  - Manual dead-weight stands.
  - Loads applied through a **double knife edge**.
  - Moments applied by the **long-arm technique**.
  - The balance is **re-levelled after every load**.
  - Horizontal loads use cables over a **bell crank** instead of a pulley, to cut friction.
  - Precision-machined fixtures.
- Temperature calibrations use strip heaters or LN2. Automatic calibration systems were under review at the time.

## 3. Figures - what each one teaches
| Fig | PDF p. (jnl) | Content | Lesson |
|---|---|---|---|
| 1 | 2 (526) | Transport model with an internal balance; arrows for N, A, Y, roll, pitch, yaw | LaRC sign and naming convention for the 6 components |
| 2 | 2 (526) | Photo of LaRC's first internal balance, 1940s, multi-piece | Bolted, screwed or welded construction leads to slop |
| 3 | 3 (527) | Calibration curve: output (uV/5V, 0-60) vs load (% FS); loading and unloading branches differ (hysteresis, a few uV), and the curve does not return to 0 (zero shift, ~5 uV) | Joints and friction show up as hysteresis and zero shift. One-piece construction fixes this (EDM made it possible, c.1958). |
| 4 | 5 (529) | UT-57 balance photo: model end with expander and dowel hole on top; three measuring sections; sting-end taper, threads, keyway | General layout: model end -> cage -> axial -> cage -> taper |
| 5 | 5 (529) | NTF balance photo: model end (diameter fit, dowel), cage-axial-cage, taper with keyway | Same layout, cryogenic version |
| 6 | 7 (531) | Drawing of a tapered sting end: 1 in/ft taper, keyway, thread for double nut, set screw at 30 deg | Standard sting joint. Note the roll slop from the sliding key. |
| 7 | 8 (532) | Expander front-end: forward taper, expander sleeve, expander guide key, gear and pinion drive, model dowel | Adjustable cylindrical model fit; complex |
| eq. | 9 (533) | strain = Vout / (Vin x GF) | For 4 active arms, 1 mV/V = 500 ue at GF 2 |
| 8 | 9 (533) | NTF measuring sections: axial slotted-T beam (one per side) between flex beams (14 per side); two cage sections, each with "two 6-sided beams" gauged for 5 components | **Gauged axial beam is separate from and on the centreline of the flexures that carry N and m** |
| 9 | 10 (534) | Two cage cross-sections (Section AA). (a) **0.65 in dia, scale 2:1**, for N 50 lb, A 10 lb, m 100 in-lb, roll 10, yaw 15 in-lb, Y 15 lb. Small rectangular beams (~0.08 x 0.04 in, 0.06/0.09 in features, ~0.03 in slots) around a thin central web. (b) **1.50 in dia, 1:1**, for N 800 lb, A 60 lb, m 2000 in-lb, roll 800, yaw 1000 in-lb, Y 400 lb. Centre beams 0.25 in wide top and bottom, flanked by 0.125 in beams, side beams ~0.20 in, overall depth 0.68/0.48 in. | Each beam arrangement is tuned to the component ratios. Small balances still use beams only a few hundredths of an inch thick. (Small digits are hard to read; values ~+/-0.005.) |
| 10 | 11 (535) | Balance in a plunge EDM machine | EDM is the main finishing process |
| 11 | 12 (536) | Bridge diagram: G1 (T) and G3 (T), G2 (C) and G4 (C) in opposite arms; thermal-compensation wire in the G4 arm; bridge-balance wire in the G2/G3 corner; +/-V and +/-signal | 4-arm bridge with series nickel thermal compensation and Manganin zero balance |
| 12 | 13 (537) | Temperature run, output (uV per 5 V) vs T, 70-180-80 F. Output drifts from ~0 to ~-15 uV/5V (~3 uV/V) over ~100 F, with a small loop between up and down | Typical *accepted* thermal zero drift is ~0.03 uV/V/F, i.e. ~0.3% FS per 100 F on a 1 mV/V balance |
| 13 | 15 (539) | Dead-weight stand photo: bell crank, pitch/yaw moment arms, double knife edge, balance in fixture | Calibration rig elements worth copying in a DIY version |
| 14 | 15 (539) | Calibration cover sheet for balance UT62A at 5 V excitation. N 500/-600 lb gives 1.214 mV/V, accuracy 0.06% FS. A 60 lb gives 1.003 mV/V, 0.17%. Pitch 1800 in-lb gives 1.548 mV/V, 0.06%. Roll 400 in-lb gives 1.032 mV/V, 0.14%. Yaw 600 in-lb gives 1.258 mV/V, 0.16%. Y 200 lb gives 0.996 mV/V, 0.14%. | Real LaRC outputs are **1.0-1.55 mV/V**. Achieved accuracy is **0.06-0.17% FS (2 sigma)**. Axial is the hardest. 5 V excitation is standard. |
| 15 | 16 (540) | Interaction sheet for the N bridge. Linear: pitch +1.28% FS, roll -1.14%, side -0.09%. Second-order terms are all <=0.12%. | Even LaRC balances have **~1% first-order interactions**. The calibration matrix must remove them. |

## 4. Directly applicable to our design
- **Monolithic 7075 aluminium** is on LaRC's approved list (#5, as 7075-T6; our T651 is the same temper, stress-relieved, which is better for machining stability).
- The **1-1.5 mV/V target** and the 4-arm `GF x strain` relation are exactly what `balance_sizing.py` uses. Our design is at the bottom of the band.
- The **two-station (fwd and aft cage) plus separate axial section** layout matches our fwd neck - axial - aft neck layout (Figs 4, 5, 8).
- **350 ohm gauges** and **5 V excitation** match LaRC practice (Fig 14).
- Calibration approach, scaled down to 3 components: a **3x9 second-order model** (3 linear, 3 squares, 3 cross-products), dead weights through knife edges, long moment arms, re-levelling after each load, and combined-load proof checks.

---

## 5. Critique of the current first-pass design (balance_sizing.py)

Script results: necks 0.50 W x 0.25 H, 517 ue, 1.03 mV/V, SF 13.6 (10.7 von Mises with Y, l, n). Axial plates 0.025 x 0.75 x 0.75 in, 388 ue, **0.78 mV/V**. Plate axial load from N and m is 20.8 lbf (1,111 psi, ~107 ue).

### Confirmed by the paper
1. One-piece construction (p.3 / 527): yes.
2. Two moment stations plus a separate axial section (Figs 4, 5, 8): yes.
3. Neck output of 1.03 mV/V is inside the 1-1.5 mV/V target (p.8 / 532).
4. The stress check with all loads applied together, including the unmeasured Y, roll and yaw, follows LaRC's rule of a safe strain "when all six components are applied simultaneously" (p.8 / 532).
5. 7075 aluminium, 350 ohm gauges and 5 V excitation are all LaRC practice (p.6, p.12, Fig 14).

### Contradicted or weak
1. **Axial output 0.78 mV/V is below LaRC's 1.0 mV/V minimum** (p.8 / 532). Axial is also the component with the worst achieved accuracy (0.17% FS, Fig 14).
2. **The gauged axial element also carries the main load.** Our gauges sit on the same two plates that carry N and m. Each plate sees ~107 ue of direct strain against a 388 ue signal, and only bridge symmetry cancels it. LaRC deliberately separates a **centreline gauged measuring beam** from the **load-carrying flex beams**, and slots it so it acts as a single bending beam (p.9 / 533, Fig 8). Our N->A interaction will depend heavily on how well the plates are matched and how accurately the gauges are placed.
3. **Load matching** (p.3-4 / 527-528).
   - Expected N is ~7.1 lbf against 15 lbf FS (47%).
   - Cruise drag is ~0.1-0.3 lbf against 2 lbf FS (5-15% of FS).
   - LaRC would suggest a lower axial FS (protected by overload stops), or a separate "performance" balance with a lower FS.
4. **Accuracy assumption is too optimistic.** The script uses 0.05% FS. LaRC's best balances achieve 0.06-0.17% FS (2 sigma) (Fig 14). A DIY balance should budget **0.2-0.5% FS**.
5. **No transition shoulders or fillets** are specified at the neck and plate roots. LaRC uses stiffening end shoulders to reduce nonlinearity (p.9 / 533). Our plate gauges sit only 0.06 in from the root, right in the root stress gradient.
6. **Interfaces are undefined.** LaRC treats the model joint as the most critical in the test (p.7 / 531).
7. **No temperature compensation or temperature sensor is planned.** A closed-return tunnel heats up during a run. Fig 12 shows that even a compensated balance drifts ~3 uV/V per 100 F (~0.3% FS).

### Recommended changes
1. **Raise axial output to at least 1.0 mV/V.**
   - Reduce plate thickness to **0.022 in** (501 ue, 1.00 mV/V, buckling SF 5.8, k = 394 lbf/in).
   - Or reduce it to **0.020 in** (606 ue, 1.21 mV/V, buckling SF 4.4, k = 296 lbf/in). This is preferred: it sits mid-band.
   - Narrowing the plate to about 0.60 in has a similar effect.
   - Re-set the stop gap so engagement is about 1.2-1.5x FS. At 0.020 in plates, a 0.010 in gap engages at ~3.0 lbf. A 0.008 in gap gives ~2.4 lbf.
2. **Consider the LaRC axial topology.**
   - Use two outer flex plates (carry N and m; ungauged; can be thicker) plus **one central, slotted gauged measuring beam on the balance centreline**.
   - Or, as a minimum, specify plate thickness matching within **0.0005 in** between plates and place the gauges symmetrically. Then check the N->A interaction in FEA.
3. **Add root fillets and shoulders** (about r = 0.03-0.06 in) at the plate and neck ends. Move the gauge centres to about 0.10 in or more from the fillet tangent and verify uniform strain under the grid with FEA.
4. **Machine the necks and plates by wire EDM** (a job shop can do this). Specify one rough pass plus two skim (finishing) passes and hold ±0.0005 in. Fatigue and recast matter less at our low stresses (5-14 ksi) but still matter.
5. **Gauging:**
   - Use **M-Bond 610** (heat-cured), not cyanoacrylate.
   - Protect with **M-Coat B**.
   - Wire with stranded silver-plated Teflon AWG 30-36 and run leads in twisted shielded pairs.
   - Zero the bridges to **within 0.4 mV/V** with Manganin trim.
   - Plan for **nickel-wire thermal-zero compensation**.
   - Temperature-cycle the finished balance over the expected range +50 F.
   - **Fit an RTD or thermocouple on the balance.**
6. **Interfaces:**
   - Model end: a cylindrical bore fit plus an interference dowel inside the 2 in pod.
   - Sting end: a **1 in/ft taper with key and double nut**, or (since we are not diameter-limited) a **flange fit**, which LaRC prefers for roll stiffness.
7. **Calibration:**
   - 3x9 second-order matrix.
   - Knife-edge load points and long moment arms.
   - **Re-level after each load.** Model pitch deflection at FS is 0.18 deg, which is not negligible.
   - Combined N+A+m proof loads.
   - Report 2-sigma back-calculated error.
   - Expect ~1% FS first-order interactions (Fig 15).
8. **Keep the design loads honest.** Consider an axial FS of about 1 lbf with hard stops, or plan a second, lower-range axial element if drag polars at cruise are the main goal (p.4 / 528).
