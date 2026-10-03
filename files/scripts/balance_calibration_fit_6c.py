"""
Six-component calibration fitting for the 6-component balance, calibrated on the roll spindle (cad/calibration_6c).

Loads (balance axes at the BMC; x aft, y right, z up):  N = Fz, A = Fx, m = My, Y = Fy, n = Mz, l = Mx
Bridges (zero-subtracted mV/V):  M1, M2 (pitch, fwd/aft), Y1, Y2 (yaw, fwd/aft), L (roll chevron), X (axial)
Responses fitted (each dominated by one load):
    PD = M2 - M1 ~ N   PS = M2 + M1 ~ m   YD = Y2 - Y1 ~ Y   YS = Y2 + Y1 ~ n   L ~ l   X ~ A
Model: intercept + primary term + only the extra terms of the NASA 27-term set (6 linear, 6 squares, 15 products)
that pass |t| > t(p = 0.001), every VIF < 5 and improve PRESS (forward selection, as in balance_calibration_fit.py).
Loads are recovered from the six responses by Newton iteration.

Applied loads: dead weights hang in the LAB frame; the balance is rolled to phi by the spindle and tilted theta
(aft end up +) by the leveling stand. body->lab rotation R = Ry(-theta) Rx(phi); a lab force F acts on the balance as
R^T F at its attachment point:  yoke / corner stirrup / drag cable -> at the pin on the axis (x_s, 0, 0);
roll arm -> at the notch (0, y_n, z_top); sleeve and roll arm weights -> at their CG (CAD); thrust -> front eyebolt.

Usage
  python balance_calibration_fit_6c.py schedule schedule_6c.csv
  python balance_calibration_fit_6c.py fit data_6c.csv [cal_6c.json]
  python balance_calibration_fit_6c.py apply cal_6c.json readings.csv out.csv
  python balance_calibration_fit_6c.py demo
CSV columns: point, type (zero|fit|check), roll_deg, theta_deg, hang (yoke|stirrup|arm|none), station_in, arm_y_in,
             W_hang_lb, W_drag_lb, W_thrust_lb, temp_C, M1, M2, Y1, Y2, L, X   (bridge outputs in mV/V)
  Roll angles 0/45/90/135/180/270(-90)/315(-45): the spindle must be allowed -90..+180 deg in bench-calibration mode
  (flight is +-90), so the balance cable through the spindle needs a service loop for 270 deg of twist.
  'zero' rows: balance ALONE (sleeve off) at that roll angle; their mean is subtracted from every row at that roll.
"""
import csv
import json
import math
import sys
from itertools import combinations
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import six_component_balance_sizing as S6                       # noqa: E402
from balance_calibration_fit import ols, vifs, t_crit            # noqa: E402

LOADS = ["N", "A", "m", "Y", "n", "l"]
FS = dict(N=S6.N_FS, A=S6.A_FS, m=S6.M_FS, Y=S6.Y_FS, n=S6.NY_FS, l=S6.L_FS)
RESP = ["PD", "PS", "YD", "YS", "L", "X"]
PRIMARY = dict(PD="N", PS="m", YD="Y", YS="n", L="l", X="A")
BRIDGES = ["M1", "M2", "Y1", "Y2", "L", "X"]
TERMS = LOADS + [f"{a}2" for a in LOADS] + [a + b for a, b in combinations(LOADS, 2)]   # 27
A_ST = S6.a                                                     # 1.35 in: neck stations at -+A_ST
PITCH_LIM = S6.M_FS + A_ST * S6.N_FS                            # 48.75 in-lbf per pitch neck
YAW_LIM = S6.NY_FS + A_ST * S6.Y_FS                             # 20.8 in-lbf per yaw neck
MP = json.loads((HERE / "calibration_6c_mass_properties.json").read_text())
COLS = ["point", "type", "roll_deg", "theta_deg", "hang", "station_in", "arm_y_in", "W_hang_lb", "W_drag_lb",
        "W_thrust_lb", "temp_C"] + BRIDGES


# ------------------------------------------------------------------ theory
def theory():
    _, _, b, h = S6.size_neck()
    E, G, GF = S6.E, S6.G, S6.GF
    s_p = GF * 1e3 / (E * b * h ** 2 / 6)
    s_y = GF * 1e3 / (E * h * b ** 2 / 6)
    s_l = GF * 1e3 / (2 * G * S6.roark_alpha(h / b) * h * b ** 2)
    Mg = 0.5 * 0.75 / 2 * (1 - 2 * 0.10 / 0.75)
    s_a = GF * 1e3 * Mg / (E * 0.75 * 0.025 ** 2 / 6)
    return dict(s_p=s_p, s_y=s_y, s_l=s_l, s_a=s_a,
                PD_N=2 * A_ST * s_p, PS_m=2 * s_p, YD_Y=2 * A_ST * s_y, YS_n=2 * s_y, L_l=s_l, X_A=s_a)


# ------------------------------------------------------------------ applied loads
def rot(phi, theta):
    p, t = math.radians(phi), math.radians(-theta)
    Rx = np.array([[1, 0, 0], [0, math.cos(p), -math.sin(p)], [0, math.sin(p), math.cos(p)]])
    Ry = np.array([[math.cos(t), 0, math.sin(t)], [0, 1, 0], [-math.sin(t), 0, math.cos(t)]])
    return Ry @ Rx


def applied_loads(row):
    if row["type"] == "zero":
        return np.zeros(6)
    R = rot(float(row["roll_deg"]), float(row.get("theta_deg") or 0))
    down = R.T @ np.array([0, 0, -1.0])            # lab gravity in body axes
    aft = R.T @ np.array([1.0, 0, 0])              # lab +x (drag cable) in body axes
    F, M = np.zeros(3), np.zeros(3)

    def add(f, r):
        nonlocal F, M
        F += f
        M += np.cross(r, f)

    add(MP["sleeve"]["W"] * down, np.array(MP["sleeve"]["cg"]))
    hang = row.get("hang") or "none"
    xs = float(row.get("station_in") or 0)
    W = float(row.get("W_hang_lb") or 0)
    if hang == "yoke":
        add((W + MP["yoke"]["W"]) * down, np.array([xs, 0, 0]))
    elif hang == "stirrup":
        add((W + MP["stirrup"]["W"]) * down, np.array([xs, 0, 0]))
    elif hang == "arm":
        add(MP["roll_arm"]["W"] * down, np.array(MP["roll_arm"]["cg"]))
        add(W * down, np.array([0.0, float(row["arm_y_in"]), MP["arm_top_z"]]))
    Wd = float(row.get("W_drag_lb") or 0)
    if Wd:
        add(Wd * aft, np.array([xs, 0, 0]))
    Wt = float(row.get("W_thrust_lb") or 0)
    if Wt:
        add(-Wt * aft, np.array([MP["x_eye"], 0, 0]))
    return np.array([F[2], F[0], M[1], F[1], M[2], M[0]])        # N, A, m, Y, n, l


def neck_check(L):
    N, A, m, Y, n, l = L
    return max(abs(m) + A_ST * abs(N)) if False else max(abs(m - A_ST * N), abs(m + A_ST * N)) / PITCH_LIM, \
        max(abs(n + A_ST * Y), abs(n - A_ST * Y)) / YAW_LIM


def within_fs(L, margin=1.0):
    p, y = neck_check(L)
    comp = max(abs(L[i]) / FS[k] for i, k in enumerate(LOADS))
    return max(p, y, comp) <= margin


# ------------------------------------------------------------------ regression
def term_cols(L, names):
    L = np.atleast_2d(L)
    d = {k: L[:, i] for i, k in enumerate(LOADS)}
    cols = [np.ones(len(L))]
    for t in names:
        if t.endswith("2") and t[:-1] in d:
            cols.append(d[t[:-1]] ** 2)
        elif t in d:
            cols.append(d[t])
        else:
            cols.append(d[t[0]] * d[t[1]])
    return np.column_stack(cols)


def select_terms(L, y, primary, log, p=0.001):
    names = [primary]
    *_, press, _ = ols(term_cols(L, names), y)
    while True:
        best = None
        for t in TERMS:
            if t in names:
                continue
            X = term_cols(L, names + [t])
            if np.ptp(X[:, -1]) < 1e-6 * max(1.0, np.abs(X[:, -1]).max()):
                continue                    # never exercised by the schedule (e.g. Y*l): not estimable
            b, e, se, pr, dd = ols(X, y)
            if not np.all(np.isfinite(se)):
                continue
            tv = abs(b[-1] / se[-1]) if se[-1] > 0 else 0
            if tv > t_crit(dd, p) and max(vifs(X)) < 5 and pr < press and (best is None or pr < best[1]):
                best = (t, pr, tv)
        if best is None:
            break
        names.append(best[0])
        press = best[1]
        log.append(f"      + {best[0]:4s} |t| = {best[2]:7.1f}")
    b, e, se, press, dof = ols(term_cols(L, names), y)
    return names, b, e, press


def responses(rows):
    B = np.array([[float(r[k]) for k in BRIDGES] for r in rows])
    M1, M2, Y1, Y2, Lr, X = B.T
    return np.column_stack([M2 - M1, M2 + M1, Y2 - Y1, Y2 + Y1, Lr, X])


def predict(model, L):
    return np.column_stack([term_cols(L, model[k]["terms"]) @ np.array(model[k]["coef"]) for k in RESP])


def invert(model, resp, L0=None):
    L = np.zeros(6) if L0 is None else np.array(L0, float)
    for _ in range(40):
        f = predict(model, L)[0] - resp
        J = np.zeros((6, 6))
        for j in range(6):
            dL = np.zeros(6)
            dL[j] = 1e-4
            J[:, j] = (predict(model, L + dL)[0] - predict(model, L - dL)[0]) / 2e-4
        step = np.linalg.solve(J, f)
        L -= step
        if np.max(np.abs(step)) < 1e-10:
            break
    return L


# ------------------------------------------------------------------ data
def read_csv(path):
    with open(path, newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def write_csv(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)


def subtract_zeros(rows):
    z = {}
    for r in rows:
        if r["type"] == "zero":
            z.setdefault(round(float(r["roll_deg"])) % 360, []).append([float(r[k]) for k in BRIDGES])
    out = []
    for r in rows:
        if r["type"] == "zero":
            continue
        zz = np.mean(z[round(float(r["roll_deg"])) % 360], axis=0)
        r = dict(r)
        for k, v in zip(BRIDGES, zz):
            r[k] = float(r[k]) - v
        out.append(r)
    return out


def fit(rows, out_json=None):
    th = theory()
    rows = subtract_zeros(rows)
    fr = [r for r in rows if r["type"] == "fit"]
    cr = [r for r in rows if r["type"] == "check"]
    Lf = np.array([applied_loads(r) for r in fr])
    Yf = responses(fr)
    FSv = np.array([FS[k] for k in LOADS])
    print(f"6-COMPONENT CALIBRATION FIT: {len(fr)} fit points, {len(cr)} check points; "
          f"max VIF of the 6 linear terms = {max(vifs(term_cols(Lf, LOADS))):.2f}")
    print("  load ranges: " + ", ".join(f"{k} {Lf[:, i].min():+.1f}..{Lf[:, i].max():+.1f}" for i, k in enumerate(LOADS)))
    model, ok = {}, True
    for j, k in enumerate(RESP):
        log = []
        names, b, e, press = select_terms(Lf, Yf[:, j], PRIMARY[k], log)
        sd = float(np.std(e, ddof=len(b)))
        rfs = abs(b[1]) * FS[PRIMARY[k]]
        model[k] = dict(terms=names, coef=b.tolist(), resp_FS=rfs, resid_sd=sd)
        big = np.max(np.abs(e)) / sd
        print(f"\n  {k:2s} = {b[0]:+.4g} " + " ".join(f"{c:+.5g}*{n}" for n, c in zip(names, b[1:])))
        for line in log:
            print(line)
        print(f"     residual SD {sd*1e3:.3f} uV/V = {100*sd/rfs:.3f}% FS ; max |res| {big:.1f} SD ; "
              f"PRESS/n / var {press/len(e)/sd**2:.2f}")
        ok &= 100 * sd / rfs <= 0.25 and big <= 3.5
    print("\n  SENSITIVITY vs THEORY (magnitudes)")
    for k, key in (("PD", "PD_N"), ("PS", "PS_m"), ("YD", "YD_Y"), ("YS", "YS_n"), ("L", "L_l"), ("X", "X_A")):
        c = abs(model[k]["coef"][1])
        print(f"    {k:2s} per {PRIMARY[k]}: fitted {c:.5f}, theory {th[key]:.5f} mV/V ({100*(c/th[key]-1):+.1f}%)"
              + ("   ** >15% off theory **" if abs(c / th[key] - 1) > 0.15 else ""))
    print(f"    effective neck spacing: pitch {2*abs(model['PD']['coef'][1]/model['PS']['coef'][1]):.3f} in, "
          f"yaw {2*abs(model['YD']['coef'][1]/model['YS']['coef'][1]):.3f} in (design {2*A_ST:.2f})")
    print("\n  BACK-CALCULATED LOADS, % of full scale (2-sigma | max)")
    for lab, rr in (("fit", fr), ("check", cr)):
        La = np.array([applied_loads(r) for r in rr])
        Lb = np.array([invert(model, y) for y in responses(rr)])
        err = (Lb - La) / FSv * 100
        print(f"    {lab:5s}: " + "  ".join(f"{k} {2*err[:, i].std():.3f}|{np.abs(err[:, i]).max():.3f}"
                                            for i, k in enumerate(LOADS)))
        if lab == "check":
            ok &= bool(np.all(2 * err.std(axis=0) <= 0.5))
    print("\n  RESULT: " + ("PASS - calibration usable" if ok else "FAIL - investigate"))
    cal = dict(model=model, loads=LOADS, responses=RESP, bridges=BRIDGES, FS=FS, passed=bool(ok),
               definition="PD=M2-M1, PS=M2+M1, YD=Y2-Y1, YS=Y2+Y1, L, X; loads at the BMC in balance axes")
    if out_json:
        Path(out_json).write_text(json.dumps(cal, indent=2))
        print(f"  calibration written to {out_json}")
    return cal


# ------------------------------------------------------------------ schedule
def schedule():
    rows, k = [], 0

    def row(typ, roll, hang="none", xs="", W=0.0, Wd=0.0, Wt=0.0, ay=""):
        nonlocal k
        k += 1
        rows.append(dict(point=k, type=typ, roll_deg=roll, theta_deg="", hang=hang, station_in=xs, arm_y_in=ay,
                         W_hang_lb=round(W, 2), W_drag_lb=round(Wd, 2), W_thrust_lb=round(Wt, 2), temp_C="",
                         **{b: "" for b in BRIDGES}))

    def wmax(roll, hang, xs=0.0, ay=0.0, Wd=0.0):
        """Largest hanging weight (0.25 lb steps) keeping every component and neck within full scale."""
        W = 0.0
        while W < 40:
            r = dict(type="fit", roll_deg=roll, hang=hang, station_in=xs, arm_y_in=ay, W_hang_lb=W + 0.25, W_drag_lb=Wd)
            if not within_fs(applied_loads(r)):
                break
            W += 0.25
        return W

    for roll in (0, 180, 90, 270, 45, 135, 315):            # -90..+180: 270 deg of cable twist
        for _ in range(3):
            row("zero", roll)
        hang = "stirrup" if roll % 90 else "yoke"
        stations = (-1.0, 0.0, 1.0) if roll % 90 else (-2.0, -1.0, 0.0, 1.0, 2.0)
        fracs = (0.25, 0.5, 0.75, 1.0) if roll % 90 else (0.25, 0.5, 0.75, 1.0, 0.5)
        for xs in stations:
            Wm = wmax(roll, hang, xs)
            for f in fracs:
                row("fit", roll, hang, xs, Wm * f)
        if roll % 90 == 0:
            for wd in (1.0, 2.0, 3.0, 4.0, 2.0):                         # drag alone (yoke at 0, no weight)
                row("fit", roll, "yoke", 0.0, 0.0, wd)
            for wt in (1.0, 2.0):
                row("fit", roll, "none", "", 0.0, 0.0, wt)
            for xs in (-1.0, 0.0, 1.0):                                  # drag combined with the plane's loads
                for wd in (2.0, 3.5):
                    row("fit", roll, "yoke", xs, wmax(roll, "yoke", xs, Wd=wd) * 0.6, wd)
        if roll in (0, 180):                                             # rolling moment via the roll arm
            for ay in (-4.0, -2.0, 2.0, 4.0):
                Wm = wmax(roll, "arm", 0.0, ay)
                for f in (0.33, 0.67, 1.0):
                    row("fit", roll, "arm", 0.0, Wm * f, 0.0, 0.0, ay)
    for i, r in enumerate(rows):                                         # every 9th loaded point is held out
        if r["type"] == "fit" and i % 9 == 4:
            r["type"] = "check"
    return rows


# ------------------------------------------------------------------ demo
def demo():
    th = theory()
    rng = np.random.default_rng(11)
    t = dict(kM1=1.03, kM2=0.98, kY1=0.97, kY2=1.02, kL=1.04, kX=1.05,
             X_N=0.004, X_m=-0.003, X_Y=0.002, X_NA=0.0006, L_Y=0.003, L_N=-0.0015, Y_m=0.0008, M_n=-0.0006,
             self_wt=0.010, noise=0.0004)
    rows = schedule()
    for r in rows:
        r["theta_deg"] = round(float(rng.normal(0, 0.02)), 3)
        r["temp_C"] = round(22 + float(rng.normal(0, 0.2)), 2)
        N, A, m, Y, n, l = applied_loads(r)
        a = A_ST
        out = dict(M1=th["s_p"] * t["kM1"] * (m - a * N) + t["M_n"] * n,
                   M2=th["s_p"] * t["kM2"] * (m + a * N) + t["M_n"] * n,
                   Y1=th["s_y"] * t["kY1"] * (n + a * Y) + t["Y_m"] * m,
                   Y2=th["s_y"] * t["kY2"] * (n - a * Y) + t["Y_m"] * m,
                   L=th["s_l"] * t["kL"] * l + t["L_Y"] * Y + t["L_N"] * N,
                   X=th["s_a"] * t["kX"] * A + t["X_N"] * N + t["X_m"] * m + t["X_Y"] * Y + t["X_NA"] * N * A)
        phi = math.radians(float(r["roll_deg"]))                         # balance self-weight zero varies with roll
        sw = t["self_wt"]
        out["M1"] += sw * math.cos(phi); out["M2"] -= sw * math.cos(phi)
        out["Y1"] += sw * math.sin(phi); out["Y2"] -= sw * math.sin(phi)
        for kk in BRIDGES:
            r[kk] = round(out[kk] + float(rng.normal(0, t["noise"])), 6)
    path = HERE / "calibration_demo" / "demo_calibration_6c.csv"
    path.parent.mkdir(exist_ok=True)
    write_csv(rows, path)
    print(f"DEMO: synthetic 6-component balance -> {path.name}\n  built in: {t}\n")
    cal = fit(read_csv(path), str(path.with_suffix(".json")))
    print("\n  expected primary coefficients: "
          f"PD/N {th['s_p']*A_ST*(t['kM1']+t['kM2']):.5f}, PS/m {th['s_p']*(t['kM1']+t['kM2']):.5f}, "
          f"YD/Y {-th['s_y']*A_ST*(t['kY1']+t['kY2']):.5f}, YS/n {th['s_y']*(t['kY1']+t['kY2']):.5f}, "
          f"L/l {th['s_l']*t['kL']:.5f}, X/A {th['s_a']*t['kX']:.5f}")
    return cal


def apply(cal_path, readings, out):
    cal = json.loads(Path(cal_path).read_text())
    rows = read_csv(readings)
    res = []
    for r in rows:
        L = invert(cal["model"], responses([r])[0])
        res.append({**r, **{f"{k}": round(float(v), 5) for k, v in zip(LOADS, L)}})
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(res[0].keys()))
        w.writeheader()
        w.writerows(res)
    print(f"wrote {len(res)} rows with N, A, m, Y, n, l (balance axes at the BMC) to {out}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "schedule":
        rows = schedule()
        write_csv(rows, a[1])
        print(f"wrote {len(rows)} rows ({sum(r['type']=='fit' for r in rows)} fit, "
              f"{sum(r['type']=='check' for r in rows)} check, {sum(r['type']=='zero' for r in rows)} zero) to {a[1]}")
    elif len(a) >= 2 and a[0] == "fit":
        fit(read_csv(a[1]), a[2] if len(a) > 2 else None)
    elif len(a) == 4 and a[0] == "apply":
        apply(a[1], a[2], a[3])
    elif a and a[0] == "demo":
        demo()
    else:
        print(__doc__)
