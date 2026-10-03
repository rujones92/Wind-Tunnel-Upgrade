"""
Motion envelope and kinematics for the motorized sting: yaw carriage -> pitch sector -> roll spindle.

Gimbal order (outermost first), all rotations about axes through the BMC (model stays on the tunnel centreline):
  psi   yaw carriage on a curved floor rail, about the vertical axis   (+ = nose left, wind from the right), +-15 deg
  theta pitch arc sector, about the carriage's lateral axis           (+ = nose up),                          -6..+20 deg
  phi   roll spindle at the sting root, about the sting/body axis      (+ = right wing down),                  +-90 deg
Lab axes: x aft (flow direction), y = right wing at zero attitude, z up; BMC at origin; BMC is X_TS_BMC aft of the
test-section entrance. Body attitude R = Rz(psi) Ry(theta) Rx(-phi) (body x aft, y right wing, z up).

Usage:  python motion_envelope.py            -> envelope tables for the reference models
        from motion_envelope import attitude, angles_for   (forward / inverse kinematics for the control software)
"""
import math
import numpy as np

TS_L, TS_W, TS_H = 30.0, 26.25, 11.25
X_TS_BMC = 17.0                       # BMC aft of test-section entrance
MARGIN = 0.50                         # minimum model clearance to any wall (in)
STING_MARGIN = 0.25                   # sting at the exit lip: stiff and slow-moving, smaller margin
STING_D = 0.875
PSI_LIM, THETA_LIM, PHI_LIM = (-15, 15), (-6, 20), (-90, 90)


def Rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def R_body(psi, theta, phi):
    return Rz(math.radians(psi)) @ Ry(math.radians(theta)) @ Rx(math.radians(-phi))


def attitude(psi, theta, phi):
    """Aerodynamic angles (deg) for machine angles: alpha, beta, bank (roll about the velocity vector ~ phi)."""
    R = R_body(psi, theta, phi)
    fwd, right, down = R @ [-1, 0, 0], R @ [0, 1, 0], R @ [0, 0, -1]
    vac = np.array([-1.0, 0, 0])                 # model moves forward (-x) relative to the air
    u, v, w = vac @ fwd, vac @ right, vac @ down
    return math.degrees(math.atan2(w, u)), math.degrees(math.asin(max(-1, min(1, v)))), phi


def angles_for(alpha, beta, phi=0.0, guess=(0.0, 0.0)):
    """Inverse kinematics: machine (psi, theta) that give the requested alpha, beta at roll phi (Newton)."""
    x = np.array(guess, float)
    for _ in range(40):
        a, b, _ = attitude(x[0], x[1], phi)
        f = np.array([a - alpha, b - beta])
        if np.max(np.abs(f)) < 1e-7:
            break
        J = np.zeros((2, 2))
        for j in range(2):
            d = np.zeros(2)
            d[j] = 1e-4
            a1, b1, _ = attitude(*(x + d), phi)
            a0, b0, _ = attitude(*(x - d), phi)
            J[:, j] = [(a1 - a0) / 2e-4, (b1 - b0) / 2e-4]
        x = x - np.linalg.solve(J, f)
    return float(x[0]), float(x[1])


# ------------------------------------------------------------------ model and sting geometry (points in body axes)
def model_points(span, chord, pod_d, pod_x0, pod_x1, c4_x=0.0, n=8):
    """Wing outline (thin plate) + pod surface points; wing quarter chord at c4_x (BMC = 0)."""
    le, te = c4_x - chord / 4, c4_x + 3 * chord / 4
    pts = []
    for y in np.linspace(-span / 2, span / 2, 2 * n + 1):
        pts += [(le, y, 0), (te, y, 0)]
    r = pod_d / 2
    for x in np.linspace(pod_x0, pod_x1, n + 1):
        for a in np.linspace(0, 2 * math.pi, 16, endpoint=False):
            pts.append((x, r * math.cos(a), r * math.sin(a)))
    return np.array(pts, float)


def sting_points(x0=3.75, n=40):
    """Sting surface from pod base aft to past the test-section exit."""
    r = STING_D / 2
    pts = []
    for x in np.linspace(x0, TS_L - X_TS_BMC + 3, n):
        for a in np.linspace(0, 2 * math.pi, 12, endpoint=False):
            pts.append((x, r * math.cos(a), r * math.sin(a)))
    return np.array(pts, float)


def clearance(pts_lab, inside_ts_only=True):
    """Minimum clearance (in) of lab points to the test-section walls (only points inside the test-section length)."""
    x0, x1 = -X_TS_BMC, TS_L - X_TS_BMC
    sel = pts_lab[(pts_lab[:, 0] >= x0) & (pts_lab[:, 0] <= x1)] if inside_ts_only else pts_lab
    if len(sel) == 0:
        return 99.0
    cy = TS_W / 2 - np.abs(sel[:, 1])
    cz = TS_H / 2 - np.abs(sel[:, 2])
    return float(min(cy.min(), cz.min()))


def worst_clearance(model_pts, psi_rng=PSI_LIM, th_rng=THETA_LIM, phi_rng=PHI_LIM, step=2.0):
    """Worst MODEL clearance over the attitude grid (the sting is checked separately: theta_max_for_sting)."""
    worst = (99.0, None)
    for psi in np.arange(psi_rng[0], psi_rng[1] + 1e-9, step * 2.5):
        for th in np.arange(th_rng[0], th_rng[1] + 1e-9, step):
            for ph in np.arange(phi_rng[0], phi_rng[1] + 1e-9, step * 5):
                c = clearance(model_pts @ R_body(psi, th, ph).T)
                if c < worst[0]:
                    worst = (c, (float(psi), float(th), float(ph)))
    return worst


def max_roll_for(model_pts, psi_rng=PSI_LIM, th_rng=THETA_LIM):
    """Largest |phi| (5 deg steps) that keeps MARGIN model clearance over the given yaw/pitch range."""
    best = 0
    for ph in range(0, 91, 5):
        c, _ = worst_clearance(model_pts, psi_rng, th_rng, (-ph, ph), step=2.0)
        if c >= MARGIN:
            best = ph
        else:
            break
    return best


def theta_max_for_sting(psi):
    """Largest nose-up pitch (0.5 deg steps) keeping the sting STING_MARGIN off the walls at yaw psi."""
    st = sting_points()
    best = 0.0
    for th in np.arange(0, 30.01, 0.5):
        if clearance(st @ R_body(psi, th, 0).T) >= STING_MARGIN:
            best = float(th)
        else:
            break
    return best


def allowed(psi, theta, phi, model_pts):
    """Interlock for the control software: True if the attitude is inside the limits and clear of the walls."""
    if not (PSI_LIM[0] <= psi <= PSI_LIM[1] and THETA_LIM[0] <= theta <= THETA_LIM[1]
            and PHI_LIM[0] <= phi <= PHI_LIM[1]):
        return False
    R = R_body(psi, theta, phi)
    return clearance(model_pts @ R.T) >= MARGIN and clearance(sting_points() @ R.T) >= STING_MARGIN


if __name__ == "__main__":
    print("KINEMATICS CHECK (machine psi, theta, phi -> alpha, beta)")
    for m in ((0, 10, 0), (10, 0, 0), (10, 10, 0), (0, 10, 90), (15, 20, 45)):
        a, b, _ = attitude(*m)
        print(f"  psi {m[0]:+4d} theta {m[1]:+4d} phi {m[2]:+4d}  ->  alpha {a:+7.2f}  beta {b:+7.2f}")
    p, t = angles_for(10.0, 5.0)
    print(f"  inverse: alpha 10, beta 5, phi 0 -> psi {p:+.3f}, theta {t:+.3f}")

    print(f"\nSTING LIMIT AT THE TEST-SECTION EXIT (margin {STING_MARGIN} in): max nose-up pitch vs yaw")
    print("  " + "   ".join(f"|psi| {p:2d}: {theta_max_for_sting(p):4.1f}" for p in (0, 5, 10, 15)) + "  (deg)")

    print(f"\nMODEL ENVELOPE (model wall margin {MARGIN} in, 2.25 in pod)")
    print("  span x chord | max |roll| with full yaw +-15 & pitch -6..+20 | with yaw 0 | worst clearance at full range")
    for span, chord in ((18, 3.5), (15, 3.5), (12, 3.0), (10, 3.0), (9, 2.5), (8, 2.5)):
        pts = model_points(span, chord, 2.25, -4.75, 3.75)
        c, at = worst_clearance(pts)
        print(f"  {span:4.0f} x {chord:3.1f}   | {max_roll_for(pts):3d} deg"
              f"                                     | {max_roll_for(pts, (0, 0)):3d} deg    "
              f"| {c:+.2f} in at psi {at[0]:+.0f}, theta {at[1]:+.0f}, phi {at[2]:+.0f}")
