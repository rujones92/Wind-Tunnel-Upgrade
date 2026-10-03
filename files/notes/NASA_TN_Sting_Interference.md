# NASA TN D-4021 — Sting-Support Interference (Loving & Luoma, 1967)

**Title:** *Sting-Support Interference on Longitudinal Aerodynamic Characteristics of Cargo-Type Airplane Models at Mach 0.70 to 0.84*
**Authors:** Donald L. Loving and Arvo A. Luoma, NASA Langley Research Center
**Number/date:** NASA TN D-4021, July 1967 (60 PDF pages, scanned)

Page citations: "p. N" = printed page number; PDF page = printed + 2 (e.g. printed p. 5 = PDF p. 7; Fig. 1 = printed p. 14 = PDF p. 16).

**What this paper is not:** it is *not* a parametric study of sting diameter or length. It is a single-geometry tare study. It measures how one fixed, carefully designed sting interferes with three high-wing transport models that have strongly upswept aft fuselages. The general design rules (sting length, d/D, flare angle) are borrowed from its Ref. 1 (Love, NACA RM L53K12, 1954) and are only quoted here. For parametric d/D and L/D data, read Refs. 1–4 (Love; Tunnell, NACA RM A54K16a; Lee & Summers, NACA RM A57I09; Cahn, NACA Rept. 1353).

---

## 1. Test setup

| Item | Value | Source |
|---|---|---|
| Facility | Langley 8-ft Transonic Pressure Tunnel: closed-circuit with slotted walls. Model span/tunnel width ≈ 0.7 | p. 4, Fig. 1 (p. 14) |
| Mach / Re | M = 0.70–0.84; Re = 19.7×10⁶/m (6.0×10⁶/ft); α = −2° to 4° | p. 1, p. 7 |
| Models | A, B, C: high swept-wing cargo transports with 4 flow-through nacelles, ~130–157 cm long, span ~150 cm, fuselage width 16.0 / 14.8 / 17.5 cm | Fig. 3 (pp. 17–19) |
| Aft end | Bottom upsweep of 19° (A), 16.5° (B) and 15° (C). Afterbody fineness (length ÷ height at start of upsweep) is 2.8, 4.0 and 3.9 | p. 5, Fig. 4 (p. 20) |
| Live sting | **Oval** section, 5.72 cm wide × 8.90 cm tall. The oval is meant to stay streamlined at angle of attack. It was sized for stiffness: **≤ 1.5 cm deflection at the balance center** under design cruise load | p. 5, Fig. 5 (p. 21) |
| Sting length | **Constant section aft of the fuselage base ≈ 5 × average aft-end diameter** "to minimize any interference of the sting flare" (citing Ref. 1) | p. 5 |
| Flare | Fairing plus strengthening collar. Total included angle ≈ **11° in planform and 15° in side view** | p. 5, Fig. 1, Fig. 6 (p. 22) |
| Stiffening | Preset-tension guy wires to the support barrel at the α pivot | p. 6, Figs. 1, 2, 7 |
| Fouling check | **Electrical fouling indicators** between model and support, wind-on and wind-off | p. 6 |
| Dorsal strut (tare rig) | NACA 65A008 sections, LE sweep 41.7°, taper ≈ 0.67. Enters the fuselage top with its leading edge ~15 cm aft of the wing TE/fuselage junction. Overhead boom ~2 body diameters above the fuselage. A low-force sponge-rubber seal around the cut-out keeps the balance-chamber pressure uniform | p. 6, Figs. 5–7 |
| Dummy sting | Identical to the live sting but ending in a sealed cavity inside the fuselage; it touches nothing. The cavity is deep enough for uniform pressure on the sting's front end. Its gaps and angle were set to match the **loaded** live sting at design-cruise load | pp. 6–7, p. 9 |
| Instrumentation | 6-component internal strain-gauge balance; scanivalve pressures on the sting top, side and bottom, the cavity top wall, the dummy-sting front face and the balance chamber; α from a nose accelerometer | p. 7, Fig. 8 |
| Accuracy | CL ±0.004, **CD ±0.0003**, Cm ±0.0015, Cp ±0.005, α ±0.05° | p. 9 |

## 2. Method (the useful part for us)

**Tare procedure (Fig. 9, p. 28):**
- **Normal run:** model on the live sting. The balance reads the model force plus sting interference.
- **Tare run A:** model on the dorsal strut, with the dummy sting in place. The balance reads the model force plus strut interference plus sting interference.
- **Tare run B:** model on the dorsal strut, no dummy sting, and the aft end closed in as on the real airplane. The balance reads the model force plus strut interference.
- **Sting tare = A − B.**
- **Model force = Normal − (A − B).**

The strut interference cancels out of the subtraction. The balance always sees the same kind of support, so the result does not depend on how the strut is attached.

**Cavity/base pressure adjustment (p. 8):**
- **Axial force:** the coefficients are adjusted to free-stream static pressure in the cavity.
  - Live sting: subtract the base axial force, computed as balance-chamber pressure × cavity cross-sectional area.
  - Dummy sting: use the average of the pressures on the dummy-sting front face × cavity area.
- **Normal force:** integrate the longitudinal Cp distributions on the top and bottom of the cavity over the cavity planform areas. The pitching-moment correction uses that ΔN times the arm from the area centroid to 0.25 c̄.
- The cavity-wall pressures matched the sting-surface pressures at the same station. The live-sting and dummy-sting cavity pressures also matched. That agreement validates the dummy sting (p. 8).

**Incremental presentation:** coefficients are referenced to the condition at CD,min (Fig. 10, p. 29). This removes run-to-run constants when two runs are differenced.

**How tares are applied (Fig. 15, p. 38):**
- In α vs CL, only the CL tare shifts the curve.
- In the CD–CL and Cm–CL plots, both CL and CD (or Cm) shift.
- The **net drag tare** is ΔCD at constant CL, and it can be much smaller than the sting drag tare at constant α.

## 3. Key findings

1. **Cavity pressure is strongly non-uniform when the cavity is open to an afterbody** (Fig. 8a–c, pp. 25–27; M = 0.80, α = 1°).
   - Where the sting sits deep in the closed part of the cavity, Cp is flat: about +0.05 (A), +0.02 (B) and −0.03 (C).
   - Where the cavity opens through the upswept underside, Cp swings from about −0.06 to +0.18 within ~20–30 cm.
   - **Lesson:** one base tap is not enough when the sting exits through a sloped or cut afterbody. Use several taps along the cavity, or keep the cavity closed and use a small annular gap at a square base.
2. **Sting tare magnitudes** (Fig. 14, pp. 35–37; text p. 10):
   - Over the full range: CL 0 to 0.020, CD −0.0005 to +0.0016, Cm −0.019 to +0.0035.
   - At cruise (M = 0.80):
     - CL: 0.0135, 0.0200, 0 (models A, B, C)
     - CD: 0.0004, 0.0010, 0.0005
     - Cm: −0.024, −0.033, +0.002
   - The quoted cruise Cm values fall outside the report's own stated range. Fig. 14 shows Cm tares of about −0.02 to −0.035 for models A and B, so the "range" sentence on p. 10 appears to be a typo.
3. **Pitching-moment tare is the largest relative effect.** For models A and B it is ~−0.02 to −0.035. That is comparable to a tail-deflection effect, so it **shifts trim** even though the slopes dCL/dα and dCm/dCL barely change (p. 11; Figs. 16–18, pp. 39–57). The data plots show Cm curves offset almost parallel. Model C was measured tail-off and shows almost no Cm tare (Fig. 14c, p. 37). This suggests most of the Cm and CL tare comes from the **sting changing the flow over the horizontal tail and aft fuselage**, not from base pressure.
4. **Drag tare is positive and grows slowly with α** (Fig. 14). At design conditions, drag with the sting in place (base-pressure adjusted) was greater than with the aft end closed (p. 11). The Mach effect is small and irregular. More negative tail deflection lowers the drag tare.
5. **Lift and drag tares partly cancel on the polar.** The **net drag tare at constant CL is 0 to 0.0004** in the cruise range: 0 for A at M 0.82, α 0.5°; 0.0004 for B; 0.0002 for C (pp. 11–12; Figs. 16–18). The authors conclude that the design approach (≥5 base diameters of constant section, small-angle flare, stiff streamlined sting) kept interference "small" (p. 12).
6. **Wall correction:** Δα = 0.10 CL, which is negligible here (p. 9).

## 4. Quantitative design rules (as stated or implied)

| Rule | Value | Source |
|---|---|---|
| Constant-section sting length behind the model base before any flare | **≥ 5 base (aft-end) diameters** | p. 5 (from Love, Ref. 1) |
| Flare included angle | ~11°–15° was acceptable at 5 diameters | p. 5 |
| Sting stiffness | Set by deflection, not stress (≤ 1.5 cm at the balance center for a ~150 cm model). Needed so the gaps can be reproduced with a dummy sting | p. 5 |
| Sting/fuselage size | Implied by the drawings, not stated as a rule: width 5.72 / fuselage width 14.8–17.5 → **≈ 0.33–0.39**; height 8.9 / fuselage height ~14–15 → ≈ 0.6. The sting nearly fills the aft end where it exits | Figs. 3, 5 |
| Dorsal strut placement | Leading edge ≥ ~15 cm (≈ 1 fuselage diameter) aft of the wing TE junction; boom ≥ ~2 body diameters above the model | p. 6 |
| Gap matching for the dummy sting | Reproduce the **loaded** gaps and angle | p. 9 |

No maximum d/D rule is given in this document.

---

## 5. Application to our tunnel (M ≈ 0.09, 70 mph)

**Relevance.** The physics carry over, but the magnitudes are smaller at M ≈ 0.09. There are no compressibility or shock effects, and the upstream pressure field of a sting flare decays faster in incompressible flow. Ref. 1 and the other classic sting studies show that the required sting length shrinks at low subsonic speed; about 3 diameters is often enough. **Keeping the 5-diameter rule is a conservative, cheap choice for us.**

The part that matters most for us is **base/cavity pressure**, because our model is small:
- q at 70 mph ≈ 600 Pa (12.5 psf).
- Wing area S = 18 × 3.5 = 63 in² (0.0406 m²), so qS ≈ 24 N.
- With a 2.0" pod and a 1.0" sting, the base annulus is ≈ 2.36 in² (0.00152 m²).
- **A base Cp error of 0.1 gives ΔCD ≈ 0.0037** on wing area.
- The Fig. 8 spread (ΔCp ≈ 0.24) would give **ΔCD ≈ 0.009**. That is about half of a typical CD0 for this wing.

So base-pressure measurement is mandatory, not optional.

### Recommendations

1. **Sting/base diameter.**
   - A 1.0" sting in a 2.0" pod gives d/D = 0.5. That is about the upper end of common practice (≈ 0.3–0.5), and higher than this paper's sting/fuselage-width ratio of ~0.35.
   - It is acceptable at M 0.09 if the base is handled well (item 3).
   - If stiffness allows (see `balance_sizing.py`), a 7/8" sting (d/D ≈ 0.44) or a 2.25" pod (1"/2.25" ≈ 0.44) gives some margin.
   - Do not go above 0.5. Do not neck the sting down right behind the base: a sudden diameter change inside ~2–3 D acts like a flare.
2. **Constant-diameter length before any flare, collar, coupling or guy-wire attachment:**
   - **≥ 5 pod base diameters, so ≥ 10" for a 2" pod.** Prefer 12" or more.
   - Keep the flare ≤ ~10–15° included angle, and put the strut-attachment fairing in the diffuser.
   - With a 30" test section, a pod base near mid-section plus 12" of clean sting puts the flare in or near the diffuser entrance. That is good.
   - Check the 12" sting deflection against the cavity gap. This paper sized its sting for deflection, so the gap stays clear under load and can be reproduced in tare runs.
3. **Pod afterbody shape:**
   - Make it axisymmetric, unlike the upswept transports in this paper.
   - Use a gentle boattail (≤ ~10° half-angle, closure fineness ≥ ~1.5) down to a **flat base only slightly larger than the sting**: about 1.2–1.3" base OD over the 1" sting, leaving a 0.05–0.1" annular gap.
   - This cuts the base area, and with it the base-pressure correction, by roughly 3–4×. It also avoids the open-slot pressure gradients of Fig. 8.
   - Keep the cavity forward of the base closed (bulkhead/seal), as the paper did for the dummy-sting cavity (p. 7). The balance chamber then sits at one uniform pressure.
   - Size the annular gap for maximum sting deflection plus balance deflection, plus margin.
4. **Measuring and correcting base/cavity pressure:**
   - Put 2–4 static taps in the base annulus/cavity (top, bottom, sides), plus one in the balance chamber. Run them to a differential manometer or MEMS transducer referenced to test-section static.
   - Correct axial force by subtracting (p_base − p∞) × A_base, using the average tap pressure and the annulus area. This matches the paper's live-sting method (p. 8).
   - Present drag "base-corrected".
   - If the taps disagree by more than ~0.02 in Cp, add taps or close the gap.
5. **Sting-interference tares:**
   - At our scale, a full dorsal-strut and dummy-sting rig (Fig. 9) is optional but doable.
   - Mount the model on a thin streamlined dorsal or ventral blade through a sealed slot. Run once with a **dummy 1" sting** (fixed to the tunnel, gapped by about the loaded clearance, not touching the model) and once without it, with the pod tail closed.
   - The difference is the sting tare. Apply it at constant CL as in Fig. 15.
   - Simpler minimum: run with the sting length varied (e.g. 12" vs 18" of clean sting). If the coefficients do not change within balance resolution, the flare/strut interference is negligible.
6. **Practical items copied from the paper:**
   - Electrical fouling indicator: a continuity circuit between pod and sting.
   - Seal any strut cut-out with a low-force foam seal.
   - Static-load the model before testing to measure the loaded gaps.
   - Use incremental (ΔC relative to CD,min) comparisons for tare differencing.
   - Expect a **Cm tare more than a CD tare** if a tail is ever added near the sting.

Note: the paper's tare magnitudes are ΔCD ~0.0005–0.001 and ΔCm ~0.02–0.03, but they are referenced to large transport wings. On our small wing on a relatively large pod, they should be treated as order-of-magnitude only.
