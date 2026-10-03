r"""
Bench calibration stand, universal loading yoke and pulleys for both sting balances.

Layout (coordinates as the balance: inches, x aft, z up, BMC at origin; STEP exported in mm):
  - Balance axis 14 in above the bench (Z_BENCH = -14) so all weights hang free above the bench.
  - Base: 3 x 1.5 x 1/8 in 6061 rectangular tube, x = -8.5 .. 22.5, C-clamped to the bench.
  - Head: two 1/2 in 6061 plates on a foot block. The AoA sting clamp block (../aoa_mechanism) is reused between them:
    pivot bolt through its x = 17.2 side hole, LEVELING slot (+-1 deg) at its x = 19.8 hole, and a 1/4-28 jack screw in a
    bridge block pressing down on the clamp block (loads always lift its aft end) for fine pitch adjustment.
    Roll 180 deg (negative N and m): pull the sting out of the clamp block, rotate, re-insert (flats are symmetric).
  - DRAG pulleys: two 2 in ball-bearing pulleys at x = 7.0 on one axle under the sting; cables leave the yoke lugs on the
    balance axis (z = 0) either side of the sting and drop to a spreader bar + weights.
  - THRUST pulley: one pulley at x = -6.5 on the axis; cable from an eyebolt in the sleeve's front 1/4-20 hole.
  - Universal YOKE (one per balance, sized to its calibration sleeve): two side straps pinned to a sleeve load station
    (x = -2..+2) by 1/4 in clevis pins, a bottom bar with a central hanger hole, and aft cable lugs on the axis.
Run (from this folder):  ..\..\.venv\Scripts\python build_calibration_stand_cad.py
"""
import math
import sys
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
for d in ("aluminum_balance", "printed_pps_balance", "aoa_mechanism"):
    sys.path.insert(0, str(HERE.parent / d))
sys.path.insert(0, str(HERE.parents[1] / "analysis"))
import build_balance_cad as B        # noqa: E402
import build_pps_balance_cad as C    # noqa: E402
import build_aoa_cad as A            # noqa: E402
from build_balance_cad import box    # noqa: E402

IN = 25.4
Z_BENCH = -14.0
TUBE_W, TUBE_H, TUBE_T = 3.0, 1.5, 0.125
X_BASE = (-8.5, 22.5)
Z_TT = Z_BENCH + TUBE_H                  # tube top
HEAD_X = (16.4, 21.0)
PLATE_T = 0.50
Y_PIN = A.BLK_W / 2 + 0.005              # plate inner face
X_PIVOT, X_LEVEL = A.R_F1, A.R_F2        # 17.2, 19.8 (clamp-block side holes, 5/16-18)
LEVEL_TRAVEL = 0.06                      # +-0.06 in at 2.6 in -> +-1.3 deg
FOOT_H = 1.0
BRIDGE = (19.4, 20.2, 1.20, 1.80)        # x0, x1, z0, z1
PULLEY_R, GROOVE, PULLEY_W = 1.0, 0.10, 0.30
AXLE_Z = -(PULLEY_R - GROOVE)            # cable leaves the groove at z = 0 (balance axis)
X_DRAG, X_THRUST = 7.0, -6.5
STRAP_T, PIN_D = 0.25, 0.25

SLEEVE = {"aluminum": dict(hw=1.05 / 2 + 0.20, hh=1.45 / 2 + 0.20),
          "pps": dict(hw=1.25 / 2 + 0.20, hh=1.75 / 2 + 0.20)}


def ycable(variant):
    return SLEEVE[variant]["hw"] + 0.03 + STRAP_T / 2


# ================================================================== stand
def make_base_tube():
    t = box(*X_BASE, -TUBE_W / 2, TUBE_W / 2, Z_BENCH, Z_TT)
    t = t.cut(box(X_BASE[0] - 1, X_BASE[1] + 1, -TUBE_W / 2 + TUBE_T, TUBE_W / 2 - TUBE_T, Z_BENCH + TUBE_T, Z_TT - TUBE_T))
    for x in (X_PIVOT, 20.2):                                     # foot-block bolts through the top wall
        t = t.cut(cq.Workplane("XY").center(x, 0).circle(0.133).extrude(1).translate((0, 0, Z_TT - 0.5)))
    for xp in (X_DRAG, X_THRUST):                                 # pulley-upright bolts through the side walls
        for z in (Z_BENCH + 0.45, Z_BENCH + 1.05):
            t = t.cut(cq.Workplane("XZ").center(xp, z).circle(0.133).extrude(3, both=True))
    return t


def make_head_plate(side):
    y0, y1 = (Y_PIN, Y_PIN + PLATE_T) if side > 0 else (-Y_PIN - PLATE_T, -Y_PIN)
    p = box(*HEAD_X, y0, y1, Z_TT, 1.90)
    cut = lambda wp: p.cut(wp.extrude(3, both=True))             # noqa: E731
    p = cut(cq.Workplane("XZ").center(X_PIVOT, 0).circle(0.166))                         # 5/16 pivot
    p = cut(cq.Workplane("XZ").center(X_LEVEL, 0).slot2D(0.332 + 2 * LEVEL_TRAVEL, 0.332, 90))  # leveling slot
    for x in (BRIDGE[0] + 0.2, BRIDGE[1] - 0.2):
        p = cut(cq.Workplane("XZ").center(x, (BRIDGE[2] + BRIDGE[3]) / 2).circle(0.133))
    for x in (HEAD_X[0] + 0.5, HEAD_X[1] - 0.5):
        p = cut(cq.Workplane("XZ").center(x, Z_TT + FOOT_H / 2).circle(0.133))
    return p


def make_foot_block():
    f = box(*HEAD_X, -Y_PIN, Y_PIN, Z_TT, Z_TT + FOOT_H)
    for x in (HEAD_X[0] + 0.5, HEAD_X[1] - 0.5):                  # 1/4-20 tapped from both sides
        f = f.cut(cq.Workplane("XZ").center(x, Z_TT + FOOT_H / 2).circle(0.1005).extrude(3, both=True))
    for x in (X_PIVOT, 20.2):                                     # 1/4-20 tapped from below (tube bolts)
        f = f.cut(cq.Workplane("XY").center(x, 0).circle(0.1005).extrude(0.6).translate((0, 0, Z_TT)))
    return f


def make_jack_bridge():
    x0, x1, z0, z1 = BRIDGE
    b = box(x0, x1, -Y_PIN, Y_PIN, z0, z1)
    for x in (x0 + 0.2, x1 - 0.2):
        b = b.cut(cq.Workplane("XZ").center(x, (z0 + z1) / 2).circle(0.1005).extrude(3, both=True))
    return b.cut(cq.Workplane("XY").center(X_LEVEL, 0).circle(0.1065).extrude(2, both=True))   # 1/4-28 jack screw


def make_pulley_upright(xp, side):
    y0, y1 = (TUBE_W / 2, TUBE_W / 2 + 0.375) if side > 0 else (-TUBE_W / 2 - 0.375, -TUBE_W / 2)
    u = box(xp - 0.75, xp + 0.75, y0, y1, Z_BENCH + 0.15, AXLE_Z + 0.6)
    u = u.cut(cq.Workplane("XZ").center(xp, AXLE_Z).circle(0.158).extrude(3, both=True))
    for z in (Z_BENCH + 0.45, Z_BENCH + 1.05):
        u = u.cut(cq.Workplane("XZ").center(xp, z).circle(0.133).extrude(3, both=True))
    return u


def make_axle(xp):
    return cq.Workplane("XZ").center(xp, AXLE_Z).circle(0.156).extrude(2.2, both=True)


def make_pulley(xp, yc):
    r_in, r_out = PULLEY_R - GROOVE, PULLEY_R
    r_b = 0.25                                                       # bore for one R5-2Z bearing (5/16 x 1/2 in)
    prof = [(0.0, r_b), (0.0, r_out), (PULLEY_W * 0.15, r_out), (PULLEY_W / 2, r_in),
            (PULLEY_W * 0.85, r_out), (PULLEY_W, r_out), (PULLEY_W, r_b)]
    p = cq.Workplane("XY").polyline(prof).close().revolve(360, (0, 0, 0), (1, 0, 0))   # axis = x, then turn to y
    p = p.rotate((0, 0, 0), (0, 0, 1), 90).translate((xp, yc - PULLEY_W / 2, AXLE_Z))
    return p


# ================================================================== universal yoke
def make_yoke(variant, xs=0.0):
    hw, hh = SLEEVE[variant]["hw"], SLEEVE[variant]["hh"]
    z_bot = -hh - 0.75
    parts = []
    for side in (1, -1):
        y0 = side * (hw + 0.03)
        y1 = y0 + side * STRAP_T
        ya, yb = min(y0, y1), max(y0, y1)
        s = box(xs - 0.3, xs + 1.1, ya, yb, -0.3, 0.3).union(box(xs - 0.3, xs + 0.3, ya, yb, z_bot, 0.3))
        s = s.cut(cq.Workplane("XZ").center(xs, 0).circle(PIN_D / 2 + 0.002).extrude(3, both=True))      # pin
        s = s.cut(cq.Workplane("XZ").center(xs + 0.9, 0).circle(0.065).extrude(3, both=True))             # cable lug
        parts.append(s)
    bar = box(xs - 0.3, xs + 0.3, -(hw + 0.03 + STRAP_T), hw + 0.03 + STRAP_T, z_bot, z_bot + 0.5)
    bar = bar.cut(cq.Workplane("XY").center(xs, 0).circle(0.1285).extrude(3, both=True))                 # hanger
    y = parts[0].union(parts[1]).union(bar)
    return y


def cable(p0, p1, d=0.06):
    v = cq.Vector(*p1) - cq.Vector(*p0)
    return cq.Workplane().add(cq.Solid.makeCylinder(d / 2, v.Length, cq.Vector(*p0), v.normalized()))


# ================================================================== variants (balance-side parts)
def balance_side(variant):
    if variant == "aluminum":
        parts = {"balance": B.make_balance(), "sleeve": B.make_cal_sleeve(), "sting": B.make_sting()}
    else:
        parts = {"balance": C.make_body(), "aft_fitting": C.make_aft_fitting(), "sleeve": C.make_cal_sleeve(),
                 "sting": C.make_sting()}
    parts["clamp_block"] = A.make_clamp_block()
    return parts


def stand_parts():
    s = {"base_tube": make_base_tube(), "head_plate_p": make_head_plate(1), "head_plate_m": make_head_plate(-1),
         "foot_block": make_foot_block(), "jack_bridge": make_jack_bridge()}
    for xp, n in ((X_DRAG, "drag"), (X_THRUST, "thrust")):
        s[f"{n}_upright_p"] = make_pulley_upright(xp, 1)
        s[f"{n}_upright_m"] = make_pulley_upright(xp, -1)
        s[f"{n}_axle"] = make_axle(xp)
    s["thrust_pulley"] = make_pulley(X_THRUST, 0.0)
    return s


def drag_pulleys(variant):
    yc = ycable(variant)
    return {"drag_pulley_p": make_pulley(X_DRAG, yc), "drag_pulley_m": make_pulley(X_DRAG, -yc)}


def vol(a, b):
    return a.val().intersect(b.val()).Volume()


if __name__ == "__main__":
    st = stand_parts()
    print("STAND CHECKS")
    for variant in ("aluminum", "pps"):
        bs = balance_side(variant)
        dp = drag_pulleys(variant)
        worst, hits = 0.0, []
        for kb, vb in bs.items():
            for ks, vs in list(st.items()) + list(dp.items()):
                v = vol(vb, vs)
                if v > 1e-6:
                    hits.append(f"{kb} x {ks}: {v:.4f}")
                worst = max(worst, v)
        # yoke at every station vs sleeve / balance / stand
        for xs in (-2.0, -1.0, 0.0, 1.0, 2.0):
            yk = make_yoke(variant, xs)
            for kb, vb in list(bs.items()) + list(st.items()) + list(dp.items()):
                v = vol(yk, vb)
                if v > 1e-6:
                    hits.append(f"yoke@{xs:+.0f} x {kb}: {v:.4f}")
                worst = max(worst, v)
        # drag cables (yoke at x = 0) to the pulley tops, thrust cable from the sleeve front to the thrust pulley
        yc = ycable(variant)
        x_front = B.X_FRONT - 0.30 if variant == "aluminum" else -C.XE - C.FIT_T   # sleeve front face
        cab = [cable((0.9, s * yc, 0), (X_DRAG, s * yc, 0)) for s in (1, -1)]
        cab.append(cable((X_THRUST, 0, 0), (x_front - 0.6, 0, 0)))
        for c in cab:
            for kb, vb in bs.items():
                v = vol(c, vb)
                if v > 1e-6:
                    hits.append(f"cable x {kb}: {v:.4f}")
                worst = max(worst, v)
        print(f"  {variant:8s}: max interference {worst:.5f} in^3 ; drag cables at y = +-{yc:.3f} in" +
              ("".join("\n     " + h for h in hits) if hits else ""))
        yk0 = make_yoke(variant, 0.0)
        w = yk0.val().Volume() * 0.0975                   # 6061, lb/in^3
        cg = yk0.val().Center()
        print(f"            yoke weight {w:.3f} lb (6061), CG {cg.x:+.3f} in aft of its pin -> add to applied N "
              f"and m (m = W x (station + {cg.x:.3f}))")
        # export variant-specific parts and assembly
        cq.exporters.export(cq.Workplane().add(yk0.val().scale(IN)), str(HERE / f"yoke_{variant}_6061.step"))
        asm = cq.Assembly(name=f"calibration_stand_{variant}")
        for k, v in bs.items():
            asm.add(cq.Workplane().add(v.val().scale(IN)), name=k, color=cq.Color(0.75, 0.75, 0.8))
        for k, v in list(st.items()) + list(dp.items()):
            asm.add(cq.Workplane().add(v.val().scale(IN)), name=k, color=cq.Color(0.85, 0.65, 0.25))
        asm.add(cq.Workplane().add(yk0.val().scale(IN)), name="yoke", color=cq.Color(0.3, 0.5, 0.9))
        for i, c in enumerate(cab):
            asm.add(cq.Workplane().add(c.val().scale(IN)), name=f"cable{i}", color=cq.Color(0.9, 0.1, 0.1))
        asm.export(str(HERE / f"assembly_calibration_stand_{variant}.step"))
        print(f"            yoke_{variant}_6061.step, assembly_calibration_stand_{variant}.step")

    # leveling range and drag-cable geometry
    print(f"LEVELING: slot +-{LEVEL_TRAVEL} in at {X_LEVEL - X_PIVOT:.1f} in from pivot -> "
          f"+-{math.degrees(math.atan(LEVEL_TRAVEL / (X_LEVEL - X_PIVOT))):.2f} deg ; 1/4-28 jack screw: "
          f"{math.degrees(1 / 28 / (X_LEVEL - X_PIVOT)):.2f} deg per turn")
    for n, wp in st.items():
        if n.endswith("_m") or n.startswith("drag_axle"):
            continue
        cq.exporters.export(cq.Workplane().add(wp.val().scale(IN)), str(HERE / f"{n.removesuffix('_p')}.step"))
    cq.exporters.export(cq.Workplane().add(make_pulley(0, 0).val().scale(IN)), str(HERE / "pulley_2in.step"))
    print("exported stand parts: base_tube, head_plate (x2), foot_block, jack_bridge, *_upright (x2 each), "
          "*_axle, pulley_2in (x3)")
