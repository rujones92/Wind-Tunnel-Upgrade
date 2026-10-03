# Notes: Ulbrich & Bader, "Analysis of Sting Balance Calibration Data Using Optimized Regression Models"

- File: `references/NASA_Sting_Balance_Calibration_Regression_2010.pdf` (29 pp.). Published as AIAA 2009-5372, 45th Joint Propulsion Conf., Denver, Aug 2009. Authors: N. Ulbrich (Jacobs/NASA Ames), J. Bader (NASA Ames).
- I read every page. Page images were checked for every equation, table and figure (pp. 5-16, 18-29).
- Page numbers below are the PDF page numbers, which match the printed folios.

---

## 1. Summary

- **What was calibrated (p. 4).** A Gulfstream sting balance with only two **moment gauges**, one forward and one aft of the balance moment center (BMC).
  - Gauge spacing d = 5.5 in (p. 15).
  - Total length about 28 in, with a 30 deg bend.
- **How it was loaded (p. 4, Fig. 4 p. 24).** Dead weights only. The balance was inverted to get positive normal force.
  - Four moment arms were used: 16.52, 18.52, 20.52 and 25.92 in, all on the same side of the BMC.
  - The load range was about ±20 lbf and ±410 in-lbf.
- **Key modelling choice (Table 1, p. 5).** The regressors are the BMC loads F (normal force) and M (pitching moment). The responses are the **difference R2 - R1**, which is nearly proportional to F, and the **sum R1 + R2**, which is nearly proportional to M. Each response is then dominated by one linear term (Fig. 5a/5b, p. 24).
- **Term selection (pp. 3-4, Fig. 1 p. 22).** NASA's BALFIT "candidate math model search" picked:
  - R2 - R1 = ε0 + ε1·F (intercept plus F only).
  - R1 + R2 = η0 + η1·M + η2·M² (intercept, M and M²).
  - The search started from a linear lower bound and stopped at a full quadratic upper bound (pp. 6-7).
- **Why the full quadratic is worse.** It fits slightly better: residual std 0.084% / 0.039% of the largest response, against 0.106% / 0.047% for the optimized models. But its VIFs run up to about 23,000, so it is **overfitted** and predicts poorly (Figs. 6, 7, pp. 25-26).
- **First-principles check (pp. 7-16).** Classical moment-balance load transformations give R2 - R1 = γ·d·F. Cantilever-beam deflection of the sting explains the M² term: under load the moment arm changes. Theory and fit agree:
  - ε1: 11.94 (theory) vs 12.21 (fit) µV/V per lbf.
  - η1: 4.342 (theory) vs 4.345 (fit) µV/V per in-lbf.
  - η2 has the opposite sign to the simple theory and is 4-6x smaller. The paper explains this by **re-levelling the calibration fixture after each load**, which removes most of the arm change and leaves a slightly shortened arm (Fig. 10, p. 28; p. 16).
- **Lesson.** Pick regressors and responses that match the physics of the balance. Then use a statistically disciplined term search (significance, VIF, PRESS) rather than defaulting to a full quadratic. Control and record fixture geometry (levelling, load-point height) during dead-weight calibration, because it creates "nonlinear" terms on its own.

---

## 2. The sting-balance concept: how gauge outputs relate to loads

### 2.1 Moment-type vs force-type balance (Appendix, pp. 18-21; Figs. 11-12, p. 29)

- A **force-type balance** has gauges that respond to a force at the gauge location (F1, F2).
- A **moment-type balance** has gauges that respond to the bending moment at the gauge location (M1, M2). It uses the "two-moment method", and that is exactly our design.

Coordinates run along the balance axis:
- c1 = forward gauge centre.
- c2 = aft gauge centre.
- μ = BMC.

**Force-type, general BMC location (Table I, p. 19):**

```
F  = F1 + F2                                        (A.8a)
M  = F1(μ - c1) - F2(c2 - μ)                        (A.8b)
F1 = F (c2-μ)/(c2-c1) + M/(c2-c1)                   (A.8c)
F2 = F (μ-c1)/(c2-c1) - M/(c2-c1)                   (A.8d)
```

**Moment-type, general BMC location (Table II, p. 20):**

```
F  = (M2 - M1)/(c2 - c1)                            (A.21a)
M  = M1 (c2-μ)/(c2-c1) + M2 (μ-c1)/(c2-c1)          (A.21b)
M1 = M - F(μ - c1)                                  (A.21c)
M2 = M + F(c2 - μ)                                  (A.21d)
```

**Simplified forms with the BMC midway, d = c2 - c1, μ = d/2 (Tables III/IV, p. 21):**

```
Force type:   F = F1+F2 ;  M = (F1-F2) d/2 ;  F1 = F/2 + M/d ;  F2 = F/2 - M/d
Moment type:  F = (M2-M1)/d ;  M = (M1+M2)/2 ;  M1 = M - F d/2 ;  M2 = M + F d/2   (A.24a-d)
```

Sign convention: +F is up, +M is nose-up as in Fig. 12. The aft gauge (nearer the sting support) sees the larger moment from a forward-applied F.

### 2.2 Gauge outputs (pp. 8-9)

Each bridge output is assumed proportional to the moment at its electrical centre:

```
R1 = γ1·M1 ,  R2 = γ2·M2                            (9a,b)
```

Fitted sensitivities:
- γ1 = 2.1643 µV/V per in-lbf, σ = 0.0046 (Eq. 10a).
- γ2 = 2.1774, σ = 0.0044 (Eq. 10b).
- Common value γ = 2.1709, σ = 0.0079 (Eq. 11b).

The two differ by about 0.6%.

With γ1 = γ2 = γ:

```
R2 - R1 = γ (M2 - M1) = γ·d·F          ->  ε1' = γ·d        (13a, 13b, 14a, 14b)
R1 + R2 = γ (M1 + M2) = 2γ·M           ->  η1' = 2γ          (15a-c, 58b)
```

The theoretical intercept is 0. The fitted intercept is non-zero because it absorbs systematic offsets in the gauge outputs (p. 9).

**My extension (not in the paper).** If γ1 ≠ γ2, the exact forms are:

```
R2 - R1 = (γ1+γ2)/2 · d·F + (γ2 - γ1)·M
R1 + R2 = (γ1+γ2)·M      + (γ2 - γ1)·d/2·F
```

So a sensitivity mismatch between the two bridges shows up as a small **M term in the difference** model and a small **F term in the sum** model. In the paper, F and M were nearly collinear: every load went on with a fixed, one-sided arm, so M ≈ F·l. With F and M that strongly correlated, the search could not separate these terms. The balance's two load components remain fully coupled through the arm.

### 2.3 Why the sum carries an M² term (pp. 9-14, Figs. 8-10, pp. 27-28)

The true arm is l = lo + Δl, where lo is the nominal arm and Δl is the change from elastic bending. Then M = F(lo + Δl), and with Mo = F·lo:

```
R1 + R2 = 2γ·Mo + 2γ·F·Δl                                       (21)
```

Geometry: the cranked sting has its load point at a vertical offset h below the balance axis, with crank angle φ (15-20 deg).

- Similar triangles give Δl = l1 + l2 with l1/δ1 = l2/δ2 = h/(lo/cosφ) (Eq. 23).
- The tip deflection from the force dominates the deflection from the end moment: δ1/δ2 ≈ (2/3)·lo/(s·sinφ), roughly 20-26 (Eq. 25a/b). Therefore l2 ≈ 0 (Eq. 26).
- This gives Δl = h·δ/(lo/cosφ) (Eq. 27).

Deflection by the area-moment method (Eq. 28): δ = ∫ M(x)·x / (E(x)I(x)) dx. With the mean-value theorem (Eq. 29) and M(x) = F cosφ·x (Eq. 32):

```
δ  = F·lo³ / (3·E(ξ)I(ξ)·cos²φ)                                 (33b)
Δl = (1/(E(ξ)I(ξ))) · (h/3) · (1/cosφ) · F·lo²                  (35)
```

E(ξ)I(ξ) is unknown. It is estimated from the measured free-end slope angle Θ, assuming dΘ/dx is constant: δ ≈ (lo/cosφ)·Θ/2 (Eq. 40).

```
1/(E I) ≈ 3Θ / (2·Mo·sqrt(h² + lo²))                             (44)
Θ ≈ (k1·Mo + k2·F)·π/180 ,  k1 = +0.00329615 deg/(in-lbf), k2 = -0.01702055 deg/lbf   (45a-c)
```

- Over the arm range, |k2/lo| = 0.00066-0.00103, so it is neglected relative to k1 (Eqs. 48-51): Θ ≈ k1·(π/180)·Mo.
- Using sinφ = h/sqrt(h² + lo²) (Eq. 54):

```
Δl ≈ (k1·π/360) · tanφ · F·lo²                                  (55)
R1 + R2 ≈ η1'·Mo + η2'·Mo² ,  η1' = 2γ ,  η2' = γ·k1·π/180 · tanφ(lo)     (58a-c)
```

So the **M² term is a geometric nonlinearity**: deflection changes the moment arm. It is not a gauge nonlinearity.

Comparison with the fit:
- Theory (p. 16): η2' = 3.4e-5 to 4.5e-5 (µV/V)/(in-lbf)², Eq. 63a.
- Fit: η2 = -7.3e-6, Eq. 63b.

The paper's explanation (Fig. 10, p. 28; Observations 1-3, p. 16):
- After each load the fixture was **re-levelled** with an AMS inclinometer.
- Re-levelling removes most of the arm growth.
- The remaining curvature of the sting (A'B'C is not straight) shortens the effective arm, so l' = lo - Δl' < lo.
- Hence the small negative coefficient.

---

## 3. Regression model forms and term selection

### 3.1 Models (pp. 5-6)

```
Traditional quadratic (1a): R2 - R1 = α0 + α1 F + α2 M + α3 F² + α4 M² + α5 F·M
Traditional quadratic (1b): R1 + R2 = β0 + β1 F + β2 M + β3 F² + β4 M² + β5 F·M
Search bounds (2a/2b, 3a/3b): lower = intercept + principal linear term; upper = full quadratic
Optimized Model 1 (2c):     R2 - R1 = ε0 + ε1 F
Optimized Model 2 (3c):     R1 + R2 = η0 + η1 M + η2 M²
```

The loads are the regressors and the gauge outputs are the responses. This is the "calibration" direction. In use, the fitted equations have to be inverted, usually by iteration, to get loads from outputs.

### 3.2 BALFIT candidate math-model search (pp. 3-4, Fig. 1 p. 22)

1. **Pick a function-class combination.** Here: intercept, linear, squares and cross products in the loads.
2. **Find the "permitted math model".** This is the largest non-singular model for the data set. Treat each term as a column vector and test them one at a time with SVD: keep a column only if it is linearly independent of the columns already kept. This takes n - 1 SVD tests, and testing low-order terms first is the clearest order.
3. **Search** from the lower bound (intercept + the principal load term for that gauge) towards the upper bound. The search minimizes the **standard deviation of the PRESS residuals** (leave-one-out prediction residuals), which is the measure of predictive capability. It is subject to two constraints:
   - **Primary constraint:** every term must be significant. The t-statistic p-value must be below a threshold; the paper uses the most conservative value, **0.0001**.
   - **Secondary constraint:** no near-linear dependencies. The **VIF** must be below a threshold; the paper uses **5**, and the literature's "liberal" limit is 10.
4. **Optional "hierarchy rule"** applied after the search: add any missing lower-order terms. It is no longer allowed during the search because that gave suboptimal results (p. 4).
5. Only 20 candidate models were tested for the difference response (p. 6).

### 3.3 Results tables (Figs. 6a/6b p. 25, 7a/7b p. 26)

| Model | Term: coefficient (std err), VIF | Residual std |
|---|---|---|
| R2-R1, quadratic (6a) | Int -0.1051; F +12.0427 (0.0196), VIF 107; M +0.0083, VIF 107; F² +0.0050 (p 0.71), VIF 6358; M² 5.6e-6 (p 0.86), VIF 5291; F·M -0.0004 (p 0.78), VIF 22934 | 0.2044 µV/V = 0.0836% of largest response (244.5 µV/V) |
| R1+R2, quadratic (6b) | Int +0.1407; F +0.3110, VIF 107; M +4.3289; F² +0.1096 (p 0.019); M² 0.0002 (p 0.12); F·M -0.0091 (p 0.045); same VIFs | 0.7026 µV/V = 0.0393% of 1785.7 µV/V |
| R2-R1, optimized (7a) | Int -0.1116 (0.0229); F +12.2069 (0.0024), t = 5174, VIF 1.0 | 0.2583 µV/V = 0.1056% |
| R1+R2, optimized (7b) | Int +0.2028 (0.0996); M +4.3446 (0.0004), t = 11128; M² -7.3372e-6 (1.77e-6), t = -4.15, VIF 1.0 | 0.8430 µV/V = 0.0472% |

- The plots also report the ratio of largest residual to standard deviation: 4.07 / 2.57 for the quadratic models and 2.91 / 2.07 for the optimized models.
- The VIF of about 107 between F and M is a property of the **load schedule**: every point lies on M = F·l with l between 16.5 and 25.9 in, all on one side (Fig. 4). That makes F and M about 99.5% correlated.

---

## 4. Load-schedule notes from the paper

- **Dead weights through a calibration fixture at four horizontal stations** (moment arms). Positive and negative loads were obtained by flipping the balance upside-down (pp. 4, 23).
- **An AMS inclinometer on the model plate** was used to **re-level the fixture after each load**, which restores the load direction and most of the arm (pp. 4, 16, Fig. 10).
- The applied loads are plotted in the F-M plane (Fig. 4, p. 24). Only four lines through the origin are covered, so the F and M terms are poorly decoupled. A better schedule would include pure-F (load at the BMC), pure-M (couple) and arms on both sides of the BMC.
- The nominal moment Mo = F·lo uses the unloaded geometry. Any elastic change of arm, or any vertical offset h between the load point and the balance axis, therefore turns into an apparent M² (or F·M) term.

## 5. Accuracy metrics used

- Residual standard deviation expressed as a **% of the largest response magnitude**: 0.04-0.11% here.
- **Ratio of the largest residual to the standard deviation**: about 2-3 for a good model, about 4 for the overfitted one.
- **PRESS residual standard deviation**, the search metric for predictive capability.
- **t-statistic and p-value** of each coefficient.
- **VIF**: below 5 (strict) or below 10 (liberal). Thousands means the model is unusable.
- Physical **sanity check of the coefficients against theory**: γ·d and 2γ. This was within 2.2% and 0.06%. The ε1 mismatch implies an effective gauge spacing of 5.62 in instead of 5.5 in, i.e. the electrical centres are not exactly at the drawing locations.

## 6. Figure and table index

| Item | Page | Content |
|---|---|---|
| Fig. 1 | 22 | Flowchart of the BALFIT search: function class -> SVD -> p-value -> VIF -> PRESS -> optional hierarchy |
| Fig. 2 | 22 | Sting balance schematic: model moment centre, forward gauge M1, BMC M, aft gauge M2 at ±d/2 |
| Fig. 3a-c | 23 | Photos: sting balance with gauge fairings, the forward/aft gauge necks, inverted dead-weight calibration with AMS |
| Table 1 | 5 | Regressor/response options: (M1,M2 -> R1,R2) or (F,M -> R2-R1, R1+R2) |
| Fig. 4 | 24 | Calibration load points in the F-M plane, four arm lines |
| Fig. 5a/5b | 24 | R2-R1 vs F and R1+R2 vs M; both nearly linear (±245 and ±1786 µV/V) |
| Fig. 6a/6b | 25 | Quadratic fits: coefficients, VIFs (red), residual plots |
| Fig. 7a/7b | 26 | Optimized fits: coefficients, VIF = 1, residual plots |
| Fig. 8 | 27 | Calibration loads on the cranked sting: h, φ, lo, τ, μ, d/2 |
| Fig. 9a/9b | 27-28 | Arm correction from force-induced and moment-induced deflection |
| Fig. 10 | 28 | Effect of re-levelling on the arm: l = lo+Δl before, l' = lo-Δl' after |
| Figs. 11-12 | 29 | Force and moment definitions for the appendix load transformations |
| Tables I-IV | 19-21 | Load transformation equation sets |

---

## 7. Calibration plan for OUR 3-component balance (N, A, m)

The design comes from `balance_sizing.py`:
- Two bending necks at s = d = 2.4 in, with the BMC midway.
- Full scale: N = 15 lbf, A = 2 lbf, m = 10 in-lbf.
- At full scale the neck moment is 28 in-lbf, giving about 1.03 mV/V.
- So γ ≈ 1034/28 ≈ **36.9 µV/V per in-lbf** per neck bridge, if the necks are identical.
- The axial bridge gives about 0.78 mV/V at 2 lbf.

### 7.1 Responses and expected coefficients

Wire and record three bridges: R1 (forward neck), R2 (aft neck) and RA (axial flexure). Use the paper's Option 2 (Table 1, p. 5):

| Response | Physics | Expected principal coefficient | FS signal |
|---|---|---|---|
| D = R2 - R1 | γ·d·N | ε1 ≈ 36.9 × 2.4 ≈ **88.6 µV/V per lbf** | ≈ 1330 µV/V at N = 15 |
| S = R1 + R2 | 2γ·m | η1 ≈ **73.9 µV/V per in-lbf** | ≈ 740 µV/V at m = 10 |
| RA | axial flexure | λ1 ≈ 390 µV/V per lbf | ≈ 780 µV/V at A = 2 |

- The sum channel reaches only about 55% of the difference channel at full scale. That follows from sizing the necks for m + N·d/2. It is acceptable, but m resolution in in-lbf is set by noise on S.
- Compare the fitted ε1 and η1 with γ·d and 2γ, as the paper does on p. 15. γ comes from regressing R1 on M1 and R2 on M2 separately (Eqs. 9-11). Agreement within a few % confirms the gauge electrical centres. ε1/γ gives the **effective** d, which you should use for the BMC location.

### 7.2 Recommended regression terms

Regress outputs on loads, with candidate terms drawn from the full quadratic in (N, A, m): 10 terms including the intercept.

- **D = R2 - R1**
  - Start from: d0 + d1·N.
  - Expected additions: d2·m from γ1 ≠ γ2 mismatch, which our decorrelated schedule will resolve; d3·A from axial-load sensitivity of imperfectly matched neck bridges.
  - Accept N² or N·m only if they pass the significance and VIF tests.
- **S = R1 + R2**
  - Start from: s0 + s1·m.
  - Expected additions: s2·N from mismatch or BMC not exactly midway; s3·m² or s3·N·m from fixture-geometry or deflection effects (Section 7.4); s4·A if present.
- **RA**
  - Start from: a0 + a1·A.
  - Expected additions: a2·N and a3·m, the strong candidates. The plate axial strain from N and m (20.8 lbf per plate at full scale, per the script) only partly cancels in the bridge; the script estimates about 0.2% of A FS per N FS with 2% gauge mismatch. Also consider a4·N² and a5·N·m, because pitch rotation tilts gravity into the axial direction (Section 7.4), and a6·A·N.
- **Selection procedure.** This is BALFIT-style and easy to do in Python with numpy/statsmodels.
  1. Build the full-quadratic design matrix and drop any linearly dependent columns (rank or SVD test, low-order terms first).
  2. Starting from the lower bound, try adding each candidate term. Keep the model that gives the lowest **PRESS std**, where e_PRESS,i = e_i/(1 - h_ii), subject to **p < 0.001** for every term (0.0001 is the paper's most conservative value) and **VIF < 5**.
  3. Stop when no addition reduces PRESS std.
  4. Expect 2-4 terms per response. **Do not** default to the full 10-term quadratic.
- **Inversion for test use.** Write R = c0 + C1·x + C2·g(x), where x = [N, A, m] and g holds the selected nonlinear terms. Solve iteratively: x_{k+1} = C1⁻¹ [R - c0 - C2·g(x_k)]. Start from x_0 = C1⁻¹(R - c0); this converges in 2-3 iterations for small nonlinear terms.
- **Alternative (Option 1).** Regress R1 on (M1, M2, A) and R2 on (M1, M2, A). This is equivalent and also gives γ1 and γ2 directly as a diagnostic.

### 7.3 Dead-weight load schedule (about 90 points + about 15 check points)

**General practice:**
- Mount the calibration body (dummy pod with load stations) on the balance with the sting clamped to a rigid stand.
- Record a zero before and after each series (return-to-zero tells you about drift and hysteresis).
- Load up and down within each series.
- Invert the balance 180 deg in roll for the opposite sign of N, as the paper does (p. 4).
- Use a pulley with a low-friction bearing for A and for the opposite signs.
- Include the weight of the calibration body and hangers in the applied loads. Alternatively, define the zero with them on and account for their moment explicitly.

**Load stations.** Put knife-edge or ball load points on the balance centreline height (h = 0), at x = -2, -1, 0 (BMC), +1 and +2 in from the BMC. Add a pure-couple fixture: a horizontal arm with equal, opposite weights or pulleys.

| Series | Loads | Points (approx.) | Purpose |
|---|---|---|---|
| 1. N at BMC | N = 0, ±3.75, ±7.5, ±11.25, ±15 lbf, up and down | 18 | pure N: ε1 and N-sensitivity of S and RA |
| 2. N at offset stations | x = ±1 in: N up to ±10 lbf (m ≤ 10); x = ±2 in: N up to ±5 lbf; 3 levels each | 24 | **decorrelates N and m** (the paper's weakness, VIF 107) |
| 3. Pure pitching couple | m = ±2.5, ±5, ±7.5, ±10 in-lbf | 8-10 | pure m: η1, m² term, m→D mismatch term |
| 4. Axial alone | A = 0, ±0.5, ±1.0, ±1.5, ±2.0 lbf, up and down | 16 | λ1, A→D and A→S interactions |
| 5. Combined A + N | N = 0, ±7.5, ±15 at the BMC × A = 0.5, 1, 2 | 12-15 | A·N, N→RA, gravity-tilt effect |
| 6. Combined A + m | m = ±5, ±10 × A = 1, 2 | 8 | A·m |
| 7. Check (validation) points | random combinations inside the envelope, not used in the fit | 10-15 | true prediction error |

- **Sizing.** About 90 fitting points against at most 10 candidate terms per response gives plenty of degrees of freedom. Check that the load points fill the N-m envelope (|N| ≤ 15, |m| ≤ 10), not just lines through the origin. Plot it like the paper's Fig. 4, and check that the VIF between the N and m columns is close to 1.
- **Side force, roll and yaw.** These are not measured, but apply a few points at the survival levels (Y = 1 lbf, l = 16 in-lbf, n = 3 in-lbf) to quantify their interaction on D, S and RA. If an interaction is significant, budget for it in the uncertainty or reduce it with gauge placement on the neck sides.

### 7.4 How to judge fit quality

- Residual std as a % of the largest response:
  - Target ≤ 0.1-0.25% FS for a DIY build.
  - The paper's professional balance reached 0.05-0.1%.
  - 0.05% of FS corresponds to about 0.66 µV/V on D and about 0.37 µV/V on S, roughly 2-3 µV at 5 V excitation. Amplifier noise and stability will likely set the floor.
- Ratio of largest residual to std of 3 or less, and no structure in the residuals plotted against each load: a curve means a missing term, scatter by series means hysteresis or fixture problems.
- PRESS std close to the fit std. If it is much larger, the model is overfitted.
- Every term passes p < 0.001 and VIF < 5.
- **Check-point errors** (Series 7) expressed in load units, as % of N, A and m full scale. This is the number to quote for balance accuracy.
- **Physics checks:**
  - ε1 ≈ γ·d.
  - η1 ≈ 2γ.
  - Mismatch terms consistent with γ2 - γ1 from Option 1.
  - Any N→RA coefficient of about the size the script predicts.
- Repeatability: return-to-zero shift and up/down hysteresis, each below the target residual.

### 7.5 Design implications from the paper

1. **Two-moment geometry.**
   - Put the BMC exactly midway between the **electrical centres** of the two neck bridges, so the simplified transforms (A.24) apply and D ∝ N, S ∝ m.
   - Make the necks and gauge placement as identical as possible (γ1 ≈ γ2). A 1% mismatch puts about 0.01·m into D, and about 0.01·N·d/2 into S.
   - The paper's balance achieved 0.6% mismatch.
2. **Gauge spacing.** ε1 = γ·d, so increasing d raises N sensitivity relative to m. Our d = 2.4 in already gives a larger D signal than S signal at full scale. If m resolution matters more (Cm ~ 0.1 gives only about 1.9 in-lbf of aerodynamic m), consider a neck section that puts more strain into the sum output, or accept that S runs at about 19% of its FS in normal testing.
3. **Calibration-fixture geometry is part of the math model.** Any vertical offset h between a load point and the balance axis, combined with the elastic rotation θ of the necks and sting, changes the arm by about h·θ.
   - The script gives model pitch rotation ≈ 0.18 deg (0.0032 rad) at full scale.
   - A 1 in offset would therefore shift the arm by 0.003 in. On a 1 in arm that is a 0.3% error in m, larger than the fit target.
   - So put load points at h = 0 (knife edges on the centreline), or measure the angle.
4. **Gravity tilt into the axial bridge.** The same rotation tilts dead-weight N loads into the axial direction: A_spurious ≈ N·θ ≈ 15 × (0.002-0.004) ≈ 0.03-0.06 lbf. That is about 1.5-3% of A FS, a significant error.
   - Mitigation: mount a small inclinometer or accelerometer on the calibration body, as the paper's AMS unit does. Either re-level after each load as in the paper (Fig. 10), or compute the applied N and A in balance axes from the measured angle.
   - Do not let the regression absorb this as N² or N·m terms. In the tunnel, aerodynamic loads rotate with the model, so the error is not the same.
   - Also make the sting and calibration stand stiff. The 1 in steel sting rotates 0.035 deg at 12 lbf, per the script.
5. **Keep intercepts in every model.** They absorb bridge offsets and fixture tares, as discussed on p. 9.
6. **Prefer a parsimonious model.** A 2-4 term model with VIF ≈ 1 will predict better at untested load combinations than a full quadratic. This matters because tunnel loads (N with m about c/4 lift times its offset from the BMC) won't land exactly on calibration points.
