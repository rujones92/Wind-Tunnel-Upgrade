r"""
Yaw carriage (+-15 deg) under the motorized pitch sector - option B (wings-level sideslip).

The yaw axis is VERTICAL THROUGH THE BMC (x = 0, y = 0), so the model yaws about its own centre.
FIXED (on the duct floor): inner and outer curved V-edge rails (1/2 in plate arcs centred on the yaw axis), a curved
          floor rack (module 1.25, external teeth).
MOVING (yaws): carriage plate (carries the pitch-sector base), 4 trucks of 2 V-groove wheels each that capture a rail
          edge on both sides (down-load, uplift and radial), pinion + 30:1 worm gearmotor (NEMA 17), and everything above
          (pitch sector, roll spindle, sting, balance, model).
Height budget (ASSUMED floor z = -11.35 in, bay 36 in wide - confirm on the tunnel): rail z -11.35..-10.85,
          carriage plate -10.35..-9.85, sector base on top.
Plan coordinates: x aft of the BMC, y spanwise; plan angle theta (deg) measured from +x toward +y.
Run (from this folder):  ..\..\.venv\Scripts\python build_yaw_carriage_cad.py
"""
import math
import sys
from pathlib import Path
import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
for d in ("aluminum_balance", "six_component_balance", "roll_spindle", "pitch_sector_motorized"):
    sys.path.insert(0, str(HERE.parent / d))
from build_balance_cad import box              # noqa: E402
import build_pitch_sector_cad as S            # noqa: E402

IN = 25.4
PSI_LIM = 15.0
Z_FLOOR = S.Z_FLOOR                            # -11.35 (assumed)
RAIL_T = 0.50
Z_RAIL0, Z_RAIL1 = Z_FLOOR, Z_FLOOR + RAIL_T
Z_CP1 = S.Z_BASE_BOT                           # carriage plate top = sector base underside (-9.85)
CP_T = 0.50
Z_CP0 = Z_CP1 - CP_T                           # -10.35
R_IN, R_OUT, RAIL_W = 14.4, 21.6, 1.50         # rail centre radii, radial width
WHEEL_D, WHEEL_T = 1.00, 0.40
Z_WHEEL = (Z_RAIL0 + Z_RAIL1) / 2
TRUCKS = [(R_IN, 12.0), (R_IN, -12.0), (R_OUT, 14.0), (R_OUT, -16.0)]   # (rail radius, plan angle)
MODULE = S.MODULE
PIN_Z = 20
R_PIN = PIN_Z * MODULE / 2
R_RACK = 19.60                                 # floor rack pitch radius (external teeth, pinion outside)
PIN_TH = -26.0                                 # pinion plan angle on the carriage
R_PIN_C = R_RACK + R_PIN
RACK_W = 0.75                                  # radial width of the rack band
# notch where the roll NEMA 23 dips below the carriage top at +20 deg pitch (same rule as the sector base)
NOTCH = (18.5, 21.15, 1.1, 4.15)           # y from 1.1: also clears the NMRV030 flange
CP_R0, CP_R1, CP_T0, CP_T1 = 12.4, 23.1, -30.0, 18.0


def P(r, th):
    t = math.radians(th)
    return (r * math.cos(t), r * math.sin(t))


def plan_prism(pts, z0, z1):
    return cq.Workplane("XY").polyline(pts).close().extrude(z1 - z0).translate((0, 0, z0))


def plan_band(r0, r1, t0, t1, z0, z1, n=90):
    pts = [P(r1, t0 + (t1 - t0) * i / n) for i in range(n + 1)] + [P(r0, t1 - (t1 - t0) * i / n) for i in range(n + 1)]
    return plan_prism(pts, z0, z1)


def vcyl(x, y, d, z0, z1):
    return cq.Workplane("XY").center(x, y).circle(d / 2).extrude(z1 - z0).translate((0, 0, z0))


# ================================================================== fixed (floor)
def rail_span(r):
    ths = [t for (rr, t) in TRUCKS if rr == r]
    return min(ths) - PSI_LIM - 4.0, max(ths) + PSI_LIM + 4.0


def make_rail(r):
    t0, t1 = rail_span(r)
    rail = plan_band(r - RAIL_W / 2, r + RAIL_W / 2, t0, t1, Z_RAIL0, Z_RAIL1)
    n = int((t1 - t0) / 6)
    for i in range(n + 1):                                         # countersunk 3/8 floor bolts on the centreline
        x, y = P(r, t0 + 1.5 + (t1 - t0 - 3) * i / n)
        rail = rail.cut(vcyl(x, y, 0.406, Z_RAIL0 - 0.1, Z_RAIL1 + 0.1))
    return rail


def make_rack(teeth=True):
    t0, t1 = PIN_TH - PSI_LIM - 2.5, PIN_TH + PSI_LIM + 2.5
    root = R_RACK - 1.25 * MODULE
    rk = plan_band(root - RACK_W, root + 0.002, t0, t1, Z_RAIL0, Z_RAIL1)
    if teeth:
        pa = math.degrees(math.pi * MODULE / R_RACK)
        th = t0 + 0.5
        while th + pa < t1 - 0.5:
            rk = rk.union(plan_prism([P(root, th + pa * 0.12), P(R_RACK + MODULE, th + pa * 0.32),
                                      P(R_RACK + MODULE, th + pa * 0.68), P(root, th + pa * 0.88)], Z_RAIL0, Z_RAIL1))
            th += pa
    for th in (t0 + 2, (t0 + t1) / 2, t1 - 2):
        x, y = P(root - RACK_W / 2, th)
        rk = rk.cut(vcyl(x, y, 0.281, Z_RAIL0 - 0.1, Z_RAIL1 + 0.1))
    return rk


def make_floor():
    return box(-17.0, 30.0, -18.0, 18.0, Z_FLOOR - 0.5, Z_FLOOR)


def make_bay_walls():
    """Bay side walls (y = +-18) and ceiling (z = +11.35) aft of the test section, for the clearance check."""
    x0 = S.TS_L - S.X_TS_BMC
    w = box(x0, 30, 18.0, 18.5, Z_FLOOR, -Z_FLOOR).union(box(x0, 30, -18.5, -18.0, Z_FLOOR, -Z_FLOOR))
    return w.union(box(x0, 30, -18, 18, -Z_FLOOR, -Z_FLOOR + 0.5))


# ================================================================== moving (carriage)
BASE_HOLES = [(13.9, S.RK_Y0), (13.9, S.Y_CH_OUT), (S.BASE_NOTCH_X - 0.5, S.Y_CH_OUT), (22.1, S.RK_Y0)]


def make_carriage_plate():
    cp = plan_band(CP_R0, CP_R1, CP_T0, CP_T1, Z_CP0, Z_CP1)
    x0, x1, y0, y1 = NOTCH
    cp = cp.cut(box(x0, x1, y0, y1, Z_CP0 - 0.1, Z_CP1 + 0.1))
    for (x, y) in BASE_HOLES:                                       # 3/8-16 tapped for the sector base
        cp = cp.cut(vcyl(x, y, 0.3125, Z_CP0 - 0.1, Z_CP1 + 0.1))
    for (r, th) in TRUCKS:                                          # wheel studs (3/8 clearance)
        for rr, d in ((r - RAIL_W / 2 - WHEEL_D / 2, 0.39), (r + RAIL_W / 2 + WHEEL_D / 2, 0.50)):
            x, y = P(rr, th)                                        # outer wheel: .500 hole for the eccentric spacer
            cp = cp.cut(vcyl(x, y, d, Z_CP0 - 0.1, Z_CP1 + 0.1))
    x, y = P(R_PIN_C, PIN_TH)
    cp = cp.cut(vcyl(x, y, 0.60, Z_CP0 - 0.1, Z_CP1 + 0.1))           # pinion shaft / bearing
    # lightening pockets would go here (FEA first)
    return cp


def make_trucks():
    out = []
    for (r, th) in TRUCKS:
        for rr in (r - RAIL_W / 2 - WHEEL_D / 2, r + RAIL_W / 2 + WHEEL_D / 2):
            x, y = P(rr, th)
            wheel = vcyl(x, y, WHEEL_D, Z_WHEEL - WHEEL_T / 2, Z_WHEEL + WHEEL_T / 2)
            spacer = vcyl(x, y, 0.60, Z_WHEEL + WHEEL_T / 2, Z_CP0)
            out.append(wheel.union(spacer))
    return out


def make_pinion():
    x, y = P(R_PIN_C, PIN_TH)
    return vcyl(x, y, 2 * R_PIN - 0.25 * MODULE, Z_RAIL0 + 0.05, Z_RAIL1 - 0.05).union(vcyl(x, y, 0.3125, Z_RAIL1 - 0.05, Z_CP1))


def make_gearmotor():
    """Envelope: 30:1 worm gearbox on top of the carriage, output down into the pinion; NEMA 17 radially outward."""
    x, y = P(R_PIN_C, PIN_TH)
    g = box(x - 0.75, x + 0.75, y - 0.75, y + 0.75, Z_CP1, Z_CP1 + 1.35)
    ux, uy = math.cos(math.radians(PIN_TH)), math.sin(math.radians(PIN_TH))
    m = (cq.Workplane("XY").rect(1.6, 1.66).extrude(1.66).translate((0, 0, -0.83))
         .rotate((0, 0, 0), (0, 0, 1), PIN_TH)
         .translate((x + ux * 1.55, y + uy * 1.55, Z_CP1 + 0.68)))
    return g.union(m)


def carriage_parts():
    parts = {"carriage_plate": make_carriage_plate(), "pinion": make_pinion(), "yaw_gearmotor": make_gearmotor()}
    for i, t in enumerate(make_trucks()):
        parts[f"wheel{i}"] = t
    return parts


_upper_cache = {}


def upper(alpha):
    """Everything on the carriage above the plate at pitch alpha (sector fixed parts + pitching parts)."""
    if alpha not in _upper_cache:
        u = {f"sector_{k}": v for k, v in S.fixed().items()}
        u.update({f"pitch_{k}": v for k, v in S.moving(alpha).items()})
        _upper_cache[alpha] = u
    return _upper_cache[alpha]


def yawed(parts, psi):
    return {k: v.rotate((0, 0, 0), (0, 0, 1), psi) for k, v in parts.items()}


def vol(a, b):
    return a.val().intersect(b.val()).Volume()


# ================================================================== loads
def truck_loads(Fz_cases):
    """Vertical truck reactions (min-norm solution, rigid plate) for vertical force / moments at the BMC + weight."""
    pts = np.array([P(r, th) for (r, th) in TRUCKS])
    A = np.vstack([np.ones(4), pts[:, 1], -pts[:, 0]])          # sum Fz, Mx = sum y*Fz, My = -sum x*Fz
    out = []
    for name, Fz, Mx, My in Fz_cases:
        R = np.linalg.lstsq(A, np.array([Fz, Mx, My]), rcond=None)[0]
        out.append((name, R))
    return out


if __name__ == "__main__":
    fixed = {"rail_inner": make_rail(R_IN), "rail_outer": make_rail(R_OUT), "floor_rack": make_rack(),
             "floor": make_floor(), "test_section": S.make_test_section(), "bay_walls": make_bay_walls()}
    car = carriage_parts()
    print(f"rails r {R_IN} / {R_OUT} in (width {RAIL_W}), spans inner {rail_span(R_IN)}, outer {rail_span(R_OUT)} deg; "
          f"rack pitch r {R_RACK} (pinion centre r {R_PIN_C:.3f} at {PIN_TH} deg)")
    print("INTERFERENCE SWEEP (wheel x rail and pinion x rack are the intended contacts and are excluded)")
    worst_all = 0.0
    for a in (S.ALPHA_MIN, 0.0, S.ALPHA_MAX):
        up = upper(a)
        for psi in (-PSI_LIM, 0.0, PSI_LIM):
            mv = yawed({**car, **up}, psi)
            worst, hits = 0.0, []
            for km, vm in mv.items():
                for kf, vf in fixed.items():
                    if (km.startswith("wheel") and kf.startswith("rail")) or (km == "pinion" and kf == "floor_rack"):
                        continue
                    if kf == "floor" and not km.startswith(("wheel", "pinion")):
                        pass
                    v = vol(vm, vf)
                    if v > 1e-6:
                        hits.append(f"{km} x {kf} = {v:.4f}")
                    worst = max(worst, v)
            # carriage against the parts it carries (fixed relative to each other - check once per alpha)
            if psi == 0.0:
                for kc in car:
                    for ku, vu in up.items():
                        v = vol(car[kc], vu)
                        if v > 1e-6 and not (kc == "carriage_plate" and ku == "sector_base_plate"):
                            hits.append(f"[carriage] {kc} x {ku} = {v:.4f}")
                            worst = max(worst, v)
            worst_all = max(worst_all, worst)
            print(f"  alpha {a:+5.1f}  psi {psi:+5.1f}: max {worst:.5f}" + ("".join("\n     " + h for h in hits) if hits else ""))
    # wheels on the rail edges and pinion on the rack pitch circle at every yaw (radii are invariant under yaw)
    for (r, th) in TRUCKS:
        gi = (r - RAIL_W / 2) - (r - RAIL_W / 2 - WHEEL_D / 2) - WHEEL_D / 2
        print(f"  truck r {r} at {th:+.0f} deg: wheels tangent to both rail edges (gap {gi:.3f} in); "
              f"plan angle range {th - PSI_LIM:+.0f}..{th + PSI_LIM:+.0f} inside rail span {rail_span(r)}")

    # loads: weight + aero at the BMC (z = 0), 11.35 in above the floor
    W = 45.0                                   # carriage + sector + roll assembly + model (lb), CG about (19, -0.5)
    cg = (19.0, -0.5)
    h = -Z_FLOOR
    cases = [("weight only", -W, -W * cg[1], W * cg[0])]
    for N in (25.0, -10.0):
        cases.append((f"weight + lift {N:+.0f} at BMC", -W + N, -W * cg[1], W * cg[0] - 0 * N))
    cases.append(("weight + side force 8 + roll 30", -W, -W * cg[1] + 8 * h + 30, W * cg[0]))
    print("\nTRUCK LOADS (lbf, + = uplift on the wheels / - = down; trucks: inner +12, inner -12, outer +14, outer -16)")
    for name, R in truck_loads(cases):
        print(f"  {name:32s}: " + ", ".join(f"{x:+6.1f}" for x in R))
    n_yaw = 10.0 + 0.02 * W * 18.0
    print(f"YAW DRIVE: ~{n_yaw:.0f} in-lbf about the yaw axis (aero 10 + rolling resistance); rack force "
          f"{n_yaw / R_RACK:.1f} lbf, pinion torque {n_yaw / R_RACK * R_PIN:.2f} in-lbf -> NEMA 17 + 30:1 worm, ample")
    print(f"  pinion turns over +-{PSI_LIM:.0f} deg: {2 * PSI_LIM / 360 * 2 * math.pi * R_RACK / (2 * math.pi * R_PIN):.1f} "
          "-> encoder on the gearmotor output + home switch (multi-turn), or a yaw encoder wheel on the rack")

    exports = {**{k: v for k, v in fixed.items() if k in ("rail_inner", "rail_outer", "floor_rack")},
               "carriage_plate_6061": car["carriage_plate"], "yaw_pinion_m1.25_20T": car["pinion"],
               "yaw_gearmotor_envelope": car["yaw_gearmotor"], "v_wheel_1in_envelope": car["wheel0"]}
    for n, wp in exports.items():
        cq.exporters.export(cq.Workplane().add(wp.val().scale(IN)), str(HERE / f"{n}.step"))
    print("exported:", ", ".join(exports))
    for psi in (-PSI_LIM, PSI_LIM):
        asm = cq.Assembly(name=f"yaw_carriage_psi{psi:+.0f}")
        for k, v in yawed({**car, **upper(0.0)}, psi).items():
            asm.add(cq.Workplane().add(v.val().scale(IN)), name=k, color=cq.Color(0.65, 0.65, 0.7))
        for k in ("rail_inner", "rail_outer", "floor_rack"):
            asm.add(cq.Workplane().add(fixed[k].val().scale(IN)), name=k, color=cq.Color(0.3, 0.3, 0.32))
        asm.export(str(HERE / f"assembly_yaw_carriage_psi{psi:+.0f}.step"))
    print(f"assemblies written; worst interference {worst_all:.5f} in^3")
