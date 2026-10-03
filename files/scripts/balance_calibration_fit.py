"""
Calibration data fitting for the 3-component sting balances (aluminum and printed PPS-CF).

Method after Ulbrich & Bader (NASA calibration-regression paper, references/notes/NASA_Calibration_Regression.md):
  responses  D = R_aft - R_fwd  (mainly N),  S = R_aft + R_fwd  (mainly m),  X = R_ax  (mainly A)
  each response = intercept + primary load term + only those extra terms (N, A, m, squares, products) that are
  statistically justified: |t| above the p < 0.001 threshold, every VIF < 5, and the PRESS statistic improves.
  Loads are recovered from outputs by Newton iteration on the fitted model.

Applied loads are computed from the stand geometry (cad/calibration_stand):
  - hanging weight, yoke weight and drag cable act at the yoke PIN (the yoke swings freely, so no CG offset);
  - the bolted calibration sleeve's weight acts at its CG (from CAD);
  - thrust acts at the front eyebolt on the axis;
  - measured tilt theta (balance x axis, aft end up positive) and roll (0 or 180 deg) resolve everything into balance axes.
Balance axes: x aft, z up (in tunnel), BMC at origin; m positive nose-up (+ rotation about +y): m = z*Fx - x*Fz.

Usage
  python balance_calibration_fit.py schedule aluminum|pps  schedule.csv   -> load schedule to fill in at the bench
  python balance_calibration_fit.py fit      aluminum|pps  data.csv [cal.json]
  python balance_calibration_fit.py apply    cal.json readings.csv out.csv -> N, A, m from tunnel readings
  python balance_calibration_fit.py demo     aluminum|pps                  -> synthetic end-to-end check

CSV columns: point, type (zero|fit|check), roll_deg, station_in (yoke pin station, blank = no yoke), W_hang_lb,
             W_drag_lb, W_thrust_lb, theta_deg, temp_C, R_fwd_mVV, R_aft_mVV, R_ax_mVV
  'zero' rows: balance ALONE (sleeve removed) at that roll angle; their mean is subtracted from every row of that roll.
"""
import csv
import json
import math
import sys
from itertools import combinations_with_replacement
import numpy as np

# ------------------------------------------------------------------ variant configuration (from CAD + sizing scripts)
GF = 2.0
VARIANTS = {
    "aluminum": dict(E=10.4e6, neck_b=0.75, neck_h=0.265, a=1.2, plate_t=0.025, plate_w=0.75, plate_L=0.75, g_off=0.10,
                     N_FS=25.0, A_FS=4.0, m_FS=15.0, neck_limit=45.0,
                     sleeve_W=0.5417, sleeve_cg=(-0.2619, -0.0739), yoke_W=0.1197, x_eye=-3.05),
    "pps": dict(E=8.0e9 / 6894.76, neck_b=1.00, neck_h=0.500, a=1.3, plate_t=0.0531, plate_w=1.00, plate_L=0.75,
                g_off=0.12, N_FS=25.0, A_FS=4.0, m_FS=15.0, neck_limit=47.5,
                sleeve_W=0.7034, sleeve_cg=(-0.2757, -0.0851), yoke_W=0.1299, x_eye=-3.25),
}
TERMS = ["N", "A", "m", "N2", "A2", "m2", "NA", "Nm", "Am"]
PRIMARY = {"D": "N", "S": "m", "X": "A"}
COLS = ["point", "type", "roll_deg", "station_in", "W_hang_lb", "W_drag_lb", "W_thrust_lb", "theta_deg", "temp_C",
        "R_fwd_mVV", "R_aft_mVV", "R_ax_mVV"]


def theory(cfg):
    """Ideal sensitivities: neck mV/V per in-lbf, axial mV/V per lbf, and the D/S/X coefficients they imply."""
    Zn = cfg["neck_b"] * cfg["neck_h"] ** 2 / 6
    s_neck = GF * 1e3 / (cfg["E"] * Zn)
    Mg = 0.5 * cfg["plate_L"] / 2 * (1 - 2 * cfg["g_off"] / cfg["plate_L"])
    Zp = cfg["plate_w"] * cfg["plate_t"] ** 2 / 6
    s_ax = GF * 1e3 * Mg / (cfg["E"] * Zp)
    return dict(s_neck=s_neck, s_ax=s_ax, D_N=2 * cfg["a"] * s_neck, S_m=2 * s_neck, X_A=s_ax)


# ------------------------------------------------------------------ applied loads
def applied_loads(row, cfg):
    th = math.radians(float(row.get("theta_deg") or 0))
    s = 1.0 if round(float(row["roll_deg"])) % 360 == 0 else -1.0
    sn, cs = math.sin(th), math.cos(th)
    N = A = m = 0.0
    if row["type"] == "zero":
        return 0.0, 0.0, 0.0

    def add(Fx, Fz, x, z):
        nonlocal N, A, m
        A += Fx
        N += Fz
        m += z * Fx - x * Fz

    xs_, zs_ = cfg["sleeve_cg"]
    add(-cfg["sleeve_W"] * sn, -s * cfg["sleeve_W"] * cs, xs_, s * zs_)          # sleeve (bolted): at its CG
    st = row.get("station_in")
    if st not in (None, ""):
        xs = float(st)
        Wv = float(row.get("W_hang_lb") or 0) + cfg["yoke_W"]
        add(-Wv * sn, -s * Wv * cs, xs, 0.0)                                        # hanging + yoke, at the pin
        Wd = float(row.get("W_drag_lb") or 0)
        add(Wd * cs, -s * Wd * sn, xs, 0.0)                                         # drag cable, at the pin
    Wt = float(row.get("W_thrust_lb") or 0)
    if Wt:
        add(-Wt * cs, s * Wt * sn, cfg["x_eye"], 0.0)                               # thrust eyebolt
    return N, A, m


# ------------------------------------------------------------------ regression machinery
def term_cols(L, names):
    N, A, m = L[:, 0], L[:, 1], L[:, 2]
    d = {"N": N, "A": A, "m": m, "N2": N * N, "A2": A * A, "m2": m * m, "NA": N * A, "Nm": N * m, "Am": A * m}
    return np.column_stack([np.ones(len(L))] + [d[t] for t in names])


def ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ beta
    n, p = X.shape
    dof = max(n - p, 1)
    s2 = e @ e / dof
    XtXi = np.linalg.pinv(X.T @ X)
    se = np.sqrt(np.diag(XtXi) * s2)
    h = np.einsum("ij,jk,ik->i", X, XtXi, X)
    press = float(np.sum((e / np.clip(1 - h, 1e-9, None)) ** 2))
    return beta, e, se, press, dof


def vifs(X):
    out = []
    for j in range(1, X.shape[1]):
        others = np.delete(X, j, axis=1)
        b, *_ = np.linalg.lstsq(others, X[:, j], rcond=None)
        r = X[:, j] - others @ b
        ss = np.sum((X[:, j] - X[:, j].mean()) ** 2)
        r2 = 1 - (r @ r) / ss if ss > 0 else 1.0
        out.append(1 / max(1 - r2, 1e-12))
    return out


def t_crit(dof, p=0.001):
    try:
        from scipy.stats import t
        return float(t.ppf(1 - p / 2, dof))
    except ImportError:                       # normal approximation with a small-sample correction
        return 3.2905 * (1 + 1.5 / max(dof, 1))


def select_terms(L, y, primary, log):
    names = [primary]
    beta, e, se, press, dof = ols(term_cols(L, names), y)
    while True:
        best = None
        for t in TERMS:
            if t in names:
                continue
            trial = names + [t]
            X = term_cols(L, trial)
            b, ee, sse, pr, dd = ols(X, y)
            tval = abs(b[-1] / sse[-1]) if sse[-1] > 0 else 0
            vmax = max(vifs(X))
            if tval > t_crit(dd) and vmax < 5 and pr < press and (best is None or pr < best[1]):
                best = (t, pr, tval, vmax)
        if best is None:
            break
        names.append(best[0])
        press = best[1]
        log.append(f"      + {best[0]:3s} (|t| = {best[2]:.1f}, max VIF {best[3]:.2f}, PRESS {best[1]:.3e})")
    beta, e, se, press, dof = ols(term_cols(L, names), y)
    return names, beta, e, se, press


def responses(rows):
    R = np.array([[float(r["R_fwd_mVV"]), float(r["R_aft_mVV"]), float(r["R_ax_mVV"])] for r in rows])
    return np.column_stack([R[:, 1] - R[:, 0], R[:, 1] + R[:, 0], R[:, 2]])


def predict(model, L):
    L = np.atleast_2d(L)
    return np.column_stack([term_cols(L, model[k]["terms"]) @ np.array(model[k]["coef"]) for k in ("D", "S", "X")])


def invert(model, resp, L0=None):
    """Newton iteration: find (N, A, m) whose predicted responses match the measured ones."""
    L = np.zeros(3) if L0 is None else np.array(L0, float)
    for _ in range(30):
        f = predict(model, L)[0] - resp
        J = np.zeros((3, 3))
        for j in range(3):
            dL = np.zeros(3)
            dL[j] = 1e-4
            J[:, j] = (predict(model, L + dL)[0] - predict(model, L - dL)[0]) / 2e-4
        step = np.linalg.solve(J, f)
        L = L - step
        if np.max(np.abs(step)) < 1e-9:
            break
    return L


# ------------------------------------------------------------------ data handling
def read_csv(path):
    with open(path, newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def subtract_zeros(rows):
    zeros = {}
    for r in rows:
        if r["type"] == "zero":
            zeros.setdefault(round(float(r["roll_deg"])) % 360, []).append(
                [float(r["R_fwd_mVV"]), float(r["R_aft_mVV"]), float(r["R_ax_mVV"])])
    out = []
    for r in rows:
        if r["type"] == "zero":
            continue
        z = np.mean(zeros[round(float(r["roll_deg"])) % 360], axis=0)
        r = dict(r)
        for k, zz in zip(("R_fwd_mVV", "R_aft_mVV", "R_ax_mVV"), z):
            r[k] = float(r[k]) - zz
        out.append(r)
    return out


def fit(variant, rows, out_json=None, quiet=False):
    cfg = VARIANTS[variant]
    th = theory(cfg)
    rows = subtract_zeros(rows)
    fit_rows = [r for r in rows if r["type"] == "fit"]
    chk_rows = [r for r in rows if r["type"] == "check"]
    Lf = np.array([applied_loads(r, cfg) for r in fit_rows])
    Yf = responses(fit_rows)
    FS = np.array([cfg["N_FS"], cfg["A_FS"], cfg["m_FS"]])
    p = print if not quiet else (lambda *a, **k: None)
    p(f"CALIBRATION FIT - {variant} balance: {len(fit_rows)} fit points, {len(chk_rows)} check points")
    p(f"  load ranges: N {Lf[:,0].min():+.2f}..{Lf[:,0].max():+.2f} lbf, A {Lf[:,1].min():+.2f}..{Lf[:,1].max():+.2f} lbf, "
      f"m {Lf[:,2].min():+.2f}..{Lf[:,2].max():+.2f} in-lbf ; max VIF of N, A, m = {max(vifs(term_cols(Lf, ['N','A','m']))):.2f}")
    model, ok = {}, True
    for k, idx in (("D", 0), ("S", 1), ("X", 2)):
        log = []
        names, beta, e, se, press = select_terms(Lf, Yf[:, idx], PRIMARY[k], log)
        resp_FS = abs(beta[1]) * FS[["N", "A", "m"].index(PRIMARY[k])]
        sd = float(np.std(e, ddof=len(beta)))
        model[k] = dict(terms=names, coef=beta.tolist(), resp_FS=resp_FS, resid_sd=sd)
        p(f"\n  response {k} = " + " ".join(f"{c:+.5g}{'' if n == '1' else '*' + n}"
                                             for n, c in zip(["1"] + names, beta)) + "   (mV/V)")
        for line in log:
            p(line)
        big = np.max(np.abs(e)) / sd if sd > 0 else 0
        p(f"    residual SD {sd*1e3:.3f} uV/V = {100*sd/resp_FS:.3f}% of FS response ; max |residual| = {big:.1f} SD ; "
          f"PRESS/n vs residual variance: {press/len(e)/sd**2:.2f}")
        ok &= 100 * sd / resp_FS <= 0.25 and big <= 3.5
    # theory comparison
    D_N = model["D"]["coef"][1]
    S_m = model["S"]["coef"][1]
    X_A = model["X"]["coef"][1]
    p("\n  SENSITIVITY vs THEORY (sign depends on wiring; magnitudes compared)")
    for lab, val, ref in (("D per lbf N", D_N, th["D_N"]), ("S per in-lbf m", S_m, th["S_m"]), ("X per lbf A", X_A, th["X_A"])):
        p(f"    {lab:16s}: fitted {abs(val):.5f}, theory {ref:.5f} mV/V  ({100*(abs(val)/ref-1):+.1f}%)")
        if abs(abs(val) / ref - 1) > 0.15:
            p("      ** more than 15% from theory: check gauge positions, wiring, gauge factor, excitation units **")
    p(f"    effective neck spacing from D/S = {2*abs(D_N/S_m):.3f} in (design {2*cfg['a']:.2f} in)")
    # back-calculated loads
    p("\n  BACK-CALCULATED LOADS (load errors, % of load full scale)")
    for lab, rr in (("fit", fit_rows), ("check", chk_rows)):
        if not rr:
            continue
        La = np.array([applied_loads(r, cfg) for r in rr])
        Lb = np.array([invert(model, y) for y in responses(rr)])
        err = (Lb - La) / FS * 100
        p(f"    {lab:5s}: 2-sigma  N {2*err[:,0].std():.3f}%  A {2*err[:,1].std():.3f}%  m {2*err[:,2].std():.3f}%   |   "
          f"max  N {np.abs(err[:,0]).max():.3f}%  A {np.abs(err[:,1]).max():.3f}%  m {np.abs(err[:,2]).max():.3f}%")
        if lab == "check":
            ok &= bool(np.all(2 * err.std(axis=0) <= 0.5))
    p("\n  RESULT: " + ("PASS - calibration usable" if ok else
                        "FAIL - investigate (residual too large, outliers, or check points off)"))
    cal = dict(variant=variant, model=model, FS=dict(N=cfg["N_FS"], A=cfg["A_FS"], m=cfg["m_FS"]),
               units=dict(outputs="mV/V (zero-subtracted)", N="lbf", A="lbf", m="in-lbf about BMC"),
               responses="D = R_aft - R_fwd, S = R_aft + R_fwd, X = R_ax", passed=bool(ok))
    if out_json:
        with open(out_json, "w") as f:
            json.dump(cal, f, indent=2)
        p(f"  calibration written to {out_json}")
    return cal


# ------------------------------------------------------------------ schedule
def schedule(variant):
    cfg = VARIANTS[variant]
    rows, k = [], 0

    def row(typ, roll, st="", wh=0.0, wd=0.0, wt=0.0):
        nonlocal k
        k += 1
        rows.append(dict(point=k, type=typ, roll_deg=roll, station_in=st, W_hang_lb=round(wh, 2), W_drag_lb=round(wd, 2),
                         W_thrust_lb=round(wt, 2), theta_deg="", temp_C="", R_fwd_mVV="", R_aft_mVV="", R_ax_mVV=""))

    def wmax(x):
        lim = cfg["neck_limit"] / (abs(x) + cfg["a"])
        if x:
            lim = min(lim, cfg["m_FS"] / abs(x))
        return min(lim, cfg["N_FS"]) - cfg["yoke_W"] - cfg["sleeve_W"]

    for roll in (0, 180):
        for _ in range(3):
            row("zero", roll)
        for x in (-2, -1, 0, 1, 2):
            W = math.floor(wmax(x) * 4) / 4
            for f in (0.25, 0.5, 0.75, 1.0, 0.5):                       # up, then one down point (hysteresis)
                row("fit", roll, x, W * f)
        for wd in (1.0, 2.0, 3.0, 4.0, 2.0):                            # drag alone (yoke at station 0, no hanger)
            row("fit", roll, 0, 0.0, wd)
        for wt in (1.0, 2.0):                                          # thrust alone, no yoke
            row("fit", roll, "", 0, 0, wt)
        for x in (-1, 0, 1):                                           # combined drag + lift/moment
            for wd in (2.0, 4.0):
                row("fit", roll, x, math.floor(wmax(x) * 0.6 * 4) / 4, wd)
        for x, fw, wd in ((-2, 0.6, 1.0), (-1, 0.3, 3.0), (0, 0.8, 1.5), (1, 0.45, 2.5), (2, 0.9, 0.5), (0, 0.15, 3.5)):
            row("check", roll, x, math.floor(wmax(x) * fw * 4) / 4, wd)  # held out of the fit
    return rows


def write_csv(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)


# ------------------------------------------------------------------ demo: a synthetic balance with known behaviour
def demo(variant):
    cfg = VARIANTS[variant]
    th = theory(cfg)
    rng = np.random.default_rng(7)
    true = dict(k_fwd=1.03, k_aft=0.98, k_ax=1.05,          # sensitivity errors vs theory
                N_to_ax=0.004, m_to_ax=-0.003,               # cross-talk into the axial bridge (mV/V per lbf / in-lbf)
                NA_ax=0.0006, m2=0.00002,                    # second-order terms
                self_wt=0.012, noise=0.0004)                 # balance self-weight zero (flips with roll), noise
    rows = schedule(variant)
    for r in rows:
        r["theta_deg"] = round(float(rng.normal(0, 0.02)), 3)   # re-levelled to within ~0.02 deg
        r["temp_C"] = round(22 + float(rng.normal(0, 0.2)), 2)
        N, A, m = applied_loads(r, cfg)
        s = 1 if r["roll_deg"] == 0 else -1
        Mf, Ma = m - cfg["a"] * N, m + cfg["a"] * N
        R_fwd = th["s_neck"] * true["k_fwd"] * Mf + true["m2"] * m * m + s * true["self_wt"]
        R_aft = th["s_neck"] * true["k_aft"] * Ma + true["m2"] * m * m - s * true["self_wt"]
        R_ax = th["s_ax"] * true["k_ax"] * A + true["N_to_ax"] * N + true["m_to_ax"] * m + true["NA_ax"] * N * A
        for key, v in (("R_fwd_mVV", R_fwd), ("R_aft_mVV", R_aft), ("R_ax_mVV", R_ax)):
            r[key] = round(v + float(rng.normal(0, true["noise"])), 6)
    path = f"demo_calibration_{variant}.csv"
    write_csv(rows, path)
    print(f"DEMO: synthetic data written to {path}; true behaviour {true}\n")
    cal = fit(variant, read_csv(path), f"demo_calibration_{variant}.json")
    print(f"\n  expected: D per N ~ {th['s_neck']*cfg['a']*(true['k_fwd']+true['k_aft']):.5f}, "
          f"S per m ~ {th['s_neck']*(true['k_fwd']+true['k_aft']):.5f}, X per A ~ {th['s_ax']*true['k_ax']:.5f} ; "
          f"X should also pick up N ({true['N_to_ax']}), m ({true['m_to_ax']}) and NA ({true['NA_ax']})")
    return cal


def apply(cal_path, readings, out):
    cal = json.load(open(cal_path))
    rows = read_csv(readings)
    res = []
    for r in rows:
        y = np.array([float(r["R_aft_mVV"]) - float(r["R_fwd_mVV"]), float(r["R_aft_mVV"]) + float(r["R_fwd_mVV"]),
                      float(r["R_ax_mVV"])])
        N, A, m = invert(cal["model"], y)
        res.append({**r, "N_lbf": round(N, 5), "A_lbf": round(A, 5), "m_inlbf": round(m, 5)})
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(res[0].keys()))
        w.writeheader()
        w.writerows(res)
    print(f"wrote {len(res)} rows with N, A, m to {out} (balance axes; resolve with alpha for lift and drag)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 3 and a[0] == "schedule":
        rows = schedule(a[1])
        write_csv(rows, a[2])
        print(f"wrote {len(rows)} rows ({sum(r['type']=='fit' for r in rows)} fit, "
              f"{sum(r['type']=='check' for r in rows)} check, {sum(r['type']=='zero' for r in rows)} zero) to {a[2]}")
    elif len(a) >= 3 and a[0] == "fit":
        fit(a[1], read_csv(a[2]), a[3] if len(a) > 3 else None)
    elif len(a) == 4 and a[0] == "apply":
        apply(a[1], a[2], a[3])
    elif len(a) == 2 and a[0] == "demo":
        demo(a[1])
    else:
        print(__doc__)
