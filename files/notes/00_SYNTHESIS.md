# Reference review — synthesis (2026-10-02)

Combined from 7 reader agents (276 pages, read as page images + text layer). Per-document notes are in this folder.
Reviewed against `balance_sizing.py` (7075-T651, 3-component, two-moment necks + 2-plate Z axial flexure).

## What the references confirm
- Monolithic balance; fwd moment section → axial section → aft moment section (LaRC Figs 4, 5, 8).
- 7075 is on LaRC's material list; 350 Ω gauges, 5 V excitation, 4-active-arm bridges, CEA-13 on aluminum.
- Necks 0.50 × 0.25 in → 1.03 mV/V, inside LaRC's 1–1.5 mV/V target; combined-load SF 10.7.
- Independent check: Bharath 8 mm square neck has the same section modulus (0.0052 in³) → same ~520 µε.
- Two-moment method with BMC midway between gauges is exactly the Gulfstream balance in the NASA 2010 calibration paper.

## Design changes indicated
| # | Issue | Source | Change |
|---|---|---|---|
| 1 | Axial output 0.78 mV/V < 1.0 target | LaRC p.8–9 | Raise strain. Note: plate t=0.020" gives 1.21 mV/V but is fragile and hard to gauge |
| 2 | Axial gauges sit on load-carrying plates (~107 µε of N/m strain vs 388 µε signal) | LaRC Fig 8 | Preferred: two ungauged outer flex plates + one centreline gauged measuring beam |
| 3 | Gauge centre 0.06" from root too close for gauge backing/tabs and fillets | Gage proc. p.7; LaRC p.9 | Root fillets r≈0.03–0.06"; gauge centres ≥0.08–0.10" from fillet; recompute |
| 4 | Clamping 60 psi on a 0.025" plate in a 0.75" window | Gage proc. p.7, p.30 | Clamp both inner gauges in one stack with backing blocks outside both plates; 0.75" window is minimum |
| 5 | Hot-cure adhesive (M-610/M-450 at 340–350°F, hours) over-ages 7075-T651 (aged ~250°F) | Gage proc. p.7, p.70 | Use reduced cure (M-610 250°F/3 h + 275°F post, p.32) or AE-10 room-temp; or switch to 17-4PH H1025 |
| 6 | Resolution assumption 0.05% FS too optimistic | LaRC Figs 14–15 | Budget 0.2–0.5% FS (LaRC itself: 0.06–0.17%, 2σ) |
| 7 | Cruise drag is only 5–15% of 2 lbf axial FS | LaRC p.3–4 | Consider ~1 lbf axial FS with hard stops, or a second low-range balance for polars |
| 8 | No temperature sensing | LaRC Fig 12; Gage proc. p.8–9 | RTD/thermistor on balance; matched-lot gauges; software temperature correction |
| 9 | Sting/pod ratio 1/2 = at limit | TN D-4021 p.5 + Love ref. | 7/8" sting or 2.25" pod (ratio ≈0.44); ≥10–12" straight sting before flare (≥5 base dia) |
| 10 | Base/cavity pressure not handled | TN D-4021 p.8 | 2–4 base taps + 1 cavity tap; subtract (p_base − p∞)·A_base from axial |
| 11 | Joints undefined | LaRC p.6–7 | Model end: bore fit + interference dowel; sting end: flange (preferred) or 1 in/ft taper + key + double nut |
| 12 | Wiring across flexures | Gage proc. p.7–8; part 2 p.57–64 | Terminals on shoulders/rails, not necks; groove for wires crossing axial flexure; strain-relief loops |

## Calibration plan (NASA 2010, Ulbrich & Bader)
- Responses: neck-output difference (∝ N) and sum (∝ m), plus axial. Regress against BMC loads.
- Term selection: start intercept + main term, add terms only if p < 0.001, VIF < 5, PRESS improves. Full quadratic overfits (VIF ~23,000).
- Schedule: ~90 fit points + 10–15 withheld check points; N at BMC and ±1, ±2 in (both sides of BMC to decorrelate N and m); pure couples; A alone and combined with N, m; load up and down; flip balance for negative loads.
- Re-level with an inclinometer after each load (0.18° deflection tilts N into A by 1.5–3% of A FS).
- Expected sensitivities: ~36.9 µV/V per in-lbf per neck; difference ≈ 88.6 µV/V per lbf; sum ≈ 73.9 µV/V per in-lbf.
- Acceptance: residual SD ≤ 0.1–0.25% FS, max residual ≤ 3σ, PRESS ≈ fit residual, check-point errors in load units.

## Gauge installation & checks (NASA TM-110327)
Degrease → abrade (hobby: acid conditioner/neutralizer) → bond (±0.005" placement) → cure → wire with equal-length leads → checks:
leakage > 10,000 MΩ at ≤15 V (megohmmeter), zero within ±0.4 mV/V (Manganin trim or amplifier offset), tap test, hand-load test,
warm-box zero drift test, thin moisture coat (≤0.005", identical on both plates; RTV over terminals only).
Avoid M-Bond 200 (cyanoacrylate) for a long-life balance.

## Alternative (2014 external 6-comp paper)
External platform balances reach ~0.3% FS but strut drag lands in the drag reading; roughly 3–5× the work for 6-comp.
Keep internal sting balance as primary; 3-component floor platform as fallback.

## Papers worth obtaining next (cited by the references)
- Love, NACA RM L53K12 (sting diameter and length effects) — free on NTRS
- Webb/Ladson 2001 monolithic balance thesis; Pieterse 2008; Lee et al. 2005
- "A Three-Component Strain-Gauged Sting Balance for Small Low-Speed Wind Tunnels", Aeronautical Journal (paywalled)
