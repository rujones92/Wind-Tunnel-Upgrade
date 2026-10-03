r"""
Six-component calibration hardware for the 6-component balance (cad/six_component_balance).

The balance is calibrated ON THE REAL ROLL SPINDLE (cad/roll_spindle): the spindle housing pivots between two new head
plates on its own cam-follower studs (front stud = pivot, rear stud in a +-1.6 deg leveling slot, jack screw above),
and the spindle's motor + encoder index the roll to 0 / 45 / 90 / 135 / 180 / 270 / 315 deg (bench mode -90..+180). Dead weights hung from the same
stations then load the pitch plane (roll 0/180), the yaw plane (90/270) or both together (45, 135).

New parts
  sleeve_6c        square 1.85 in sleeve bolted to the balance front face; 1/4 in load holes in ALL FOUR walls on the
                   balance axis at x = -2..+2 in (stub pins + yoke on whichever pair of walls is horizontal)
  roll_arm         plate that slides over the sleeve at x = 0, located by dowels in the top/bottom wall holes;
                   knife-edge notches at y = +-2 and +-4 in give rolling moment (used at roll 0 / 180)
  yoke_6c          universal yoke sized for the square sleeve (works at every roll angle)
  head plates v2 + jack bridge v2 + base tube v2 (holes for the plates)
Reused unchanged: drag / thrust pulleys, uprights, axles (cad/calibration_stand).
Coordinates as everywhere: inches, x aft of the BMC, y spanwise, z up; STEP in mm.
Run (from this folder):  ..\..\.venv\Scripts\python build_calibration_6c_cad.py
"""
import json
import math
import sys
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
for d in ("aluminum_balance", "six_component_balance", "roll_spindle", "aoa_mechanism", "calibration_stand"):
    sys.path.insert(0, str(HERE.parent / d))
from build_balance_cad import box                # noqa: E402
import build_6c_balance_cad as K                 # noqa: E402
import build_roll_spindle_cad as R               # noqa: E402
import build_calibration_stand_cad as S          # noqa: E402

IN = 25.4
AL, STEEL = 0.0975, 0.284                        # lb/in^3
# ---------------- sleeve
SL_IN, SL_T = 1.45, 0.20                         # square inner, wall
SL_OUT = SL_IN + 2 * SL_T                        # 1.85
X_SL0 = K.X_FRONT - 0.30                         # front plate -2.85..-2.55
X_SL1 = K.X_AFT + 0.20                           # aft end 2.75 (around the sting, clear of the aft block)
STATIONS = (-2.0, -1.0, 0.0, 1.0, 2.0)
# ---------------- roll arm
ARM_HALF_SPAN, ARM_T = 4.6, 0.50
ARM_NOTCH_Y = (-4.0, -2.0, 2.0, 4.0)
ARM_TOP = SL_OUT / 2 + 0.30                      # 1.225
ARM_BOT = -(SL_OUT / 2 + 0.30)
# ---------------- head v2 (holds the roll housing by its studs)
HP_Y0 = R.HOUS_HALF + 0.05                       # 1.50 (plate inner face)
HP_T = 0.50
HP_X = (16.45, 20.30)
HP_Z_TOP = 2.25
PIVOT_X, LEVEL_X = R.FOLLOWERS                   # 17.3 (pivot), 19.4 (leveling slot)
LEVEL_TRAVEL = 0.06
JACK_X = 19.75
S.SLEEVE["6c"] = dict(hw=SL_OUT / 2, hh=SL_OUT / 2)
R_CORNER = SL_OUT / 2 * math.sqrt(2)              # 1.308: corner distance from the axis


def yz_hole(y, z, d, x0, length):
    return cq.Workplane("YZ").center(y, z).circle(d / 2).extrude(length).translate((x0, 0, 0))


# ================================================================== sleeve
def make_sleeve():
    o, i = SL_OUT / 2, SL_IN / 2
    s = box(X_SL0, X_SL1, -o, o, -o, o).cut(box(K.X_FRONT, X_SL1 + 0.1, -i, i, -i, i))
    for z in (0.42, -0.42):                                   # 2x #10 clearance, c'bored from the front
        s = s.cut(yz_hole(0, z, 0.196, X_SL0 - 0.1, 0.6)).cut(yz_hole(0, z, 0.32, X_SL0 - 0.01, 0.21))
    for z in (0.17, -0.17):                                   # 2x 1/8 dowels
        s = s.cut(yz_hole(0, z, 0.125, X_SL0 - 0.1, 0.6))
    s = s.cut(yz_hole(0, 0, 0.201, X_SL0 - 0.05, 0.4))       # 1/4-20 tapped: thrust eyebolt
    for x in STATIONS:                                        # 1/4 reamed load holes, all four walls, on the axis
        s = s.cut(cq.Workplane("XZ").center(x, 0).circle(0.126).extrude(2, both=True))
        s = s.cut(cq.Workplane("XY").center(x, 0).circle(0.126).extrude(2, both=True))
        for k in range(4):                                    # V-notch across each corner: locates the 45 deg stirrup
            n = box(x - 0.03, x + 0.03, -0.4, 0.4, R_CORNER - 0.05, R_CORNER + 0.6).rotate((0, 0, 0), (1, 0, 0), 45 + 90 * k)
            s = s.cut(n)
    return s


def make_stirrup(xs):
    """Corner stirrup for roll 45/135/225/315 (lab frame): V-seat on the upper corner, side straps, bottom hanger bar.
    The load line passes vertically through the corner, i.e. through the balance axis -> no rolling moment."""
    top = box(xs - 0.15, xs + 0.15, -0.7, 0.7, R_CORNER - 0.30, R_CORNER + 0.35)   # .30 deep V-seat
    top = top.cut(make_sleeve_body().rotate((0, 0, 0), (1, 0, 0), 45))
    straps = box(xs - 0.15, xs + 0.15, 1.42, 1.62, -R_CORNER - 0.6, R_CORNER + 0.35).union(
        box(xs - 0.15, xs + 0.15, -1.62, -1.42, -R_CORNER - 0.6, R_CORNER + 0.35))
    top = top.union(box(xs - 0.15, xs + 0.15, -1.62, 1.62, R_CORNER + 0.15, R_CORNER + 0.35))
    # knife-edge rib .050 wide in the V apex: drops into the sleeve's .060 corner groove and fixes the station
    rib = box(xs - 0.025, xs + 0.025, -0.38, 0.38, R_CORNER - 0.045, R_CORNER + 0.02)
    top = top.union(rib.intersect(make_sleeve_body().rotate((0, 0, 0), (1, 0, 0), 45)))
    bottom = box(xs - 0.15, xs + 0.15, -1.62, 1.62, -R_CORNER - 0.6, -R_CORNER - 0.35)
    bottom = bottom.cut(cq.Workplane("XY").center(xs, 0).circle(0.1285).extrude(2, both=True))
    return top.union(straps).union(bottom)


def make_sleeve_body():
    o = SL_OUT / 2
    return box(X_SL0, X_SL1, -o, o, -o, o)


# ================================================================== roll arm (at x = 0)
def make_roll_arm():
    h, t = SL_OUT / 2 + 0.008, ARM_T / 2
    a = box(-t, t, -ARM_HALF_SPAN, ARM_HALF_SPAN, ARM_BOT, ARM_TOP)
    a = a.cut(box(-t - 0.1, t + 0.1, -h, h, -h, h))                               # window over the sleeve
    for y in ARM_NOTCH_Y:                                                       # 90 deg knife-edge V-notches
        v = (cq.Workplane("YZ").polyline([(y - 0.07, ARM_TOP + 0.001), (y + 0.07, ARM_TOP + 0.001),
                                          (y, ARM_TOP - 0.07)]).close().extrude(1).translate((-0.5, 0, 0)))
        a = a.cut(v)
    for z in (1, -1):                                                           # dowels into the sleeve top/bottom holes
        a = a.cut(cq.Workplane("XY").center(0, 0).circle(0.126).extrude(0.6).translate((0, 0, z * h - (0.6 if z < 0 else 0))))
    for y in (0.55, -0.55):                                                     # 2x 1/4-20 nylon-tip set screws, top rim
        a = a.cut(cq.Workplane("XY").center(0, y).circle(0.1005).extrude(0.5).translate((0, 0, h - 0.1)))
    # lightening: keep it stiff but light
    for y in (-3.0, 3.0):
        a = a.cut(box(-t - 0.1, t + 0.1, y - 0.55, y + 0.55, -0.55, 0.55))
    return a


# ================================================================== head v2
def make_head_plate(side):
    y0, y1 = (HP_Y0, HP_Y0 + HP_T) if side > 0 else (-HP_Y0 - HP_T, -HP_Y0)
    p = box(*HP_X, y0, y1, S.Z_BENCH + 0.1, HP_Z_TOP)
    cut = lambda wp: p.cut(wp.extrude(3, both=True))          # noqa: E731
    p = cut(cq.Workplane("XZ").center(PIVOT_X, 0).circle(0.19))                     # 3/8 stud pivot
    p = cut(cq.Workplane("XZ").center(LEVEL_X, 0).slot2D(0.38 + 2 * LEVEL_TRAVEL, 0.38, 90))
    for x in (JACK_X - 0.3, JACK_X + 0.3):                                       # jack-bridge screws
        p = cut(cq.Workplane("XZ").center(x, HP_Z_TOP - 0.25).circle(0.133))
    for x in (HP_X[0] + 0.5, HP_X[1] - 0.5):                                     # through the tube side walls
        for z in (S.Z_BENCH + 0.45, S.Z_BENCH + 1.05):
            p = cut(cq.Workplane("XZ").center(x, z).circle(0.133))
    for x, z in ((HP_X[0] + 0.5, -6.0), (HP_X[1] - 0.5, -6.0)):                  # cross-spacer bolts
        p = cut(cq.Workplane("XZ").center(x, z).circle(0.133))
    # lightening window (below the housing)
    return p.cut(box(HP_X[0] + 1.0, HP_X[1] - 1.0, -5, 5, S.Z_TT + 1.0, -3.0))


def make_cross_spacer(x):
    s = box(x - 0.4, x + 0.4, -HP_Y0, HP_Y0, -6.4, -5.6)
    return s.cut(cq.Workplane("XZ").center(x, -6.0).circle(0.1005).extrude(4, both=True))


def make_jack_bridge():
    b = box(JACK_X - 0.55, JACK_X + 0.55, -HP_Y0, HP_Y0, HP_Z_TOP - 0.5, HP_Z_TOP)
    for x in (JACK_X - 0.3, JACK_X + 0.3):
        b = b.cut(cq.Workplane("XZ").center(x, HP_Z_TOP - 0.25).circle(0.1005).extrude(4, both=True))
    return b.cut(cq.Workplane("XY").center(JACK_X, 0).circle(0.1065).extrude(3, both=True))   # 1/4-28 jack screw


def make_base_tube():
    t = S.make_base_tube()
    for x in (HP_X[0] + 0.5, HP_X[1] - 0.5):
        for z in (S.Z_BENCH + 0.45, S.Z_BENCH + 1.05):
            t = t.cut(cq.Workplane("XZ").center(x, z).circle(0.133).extrude(3, both=True))
    return t


def make_studs():
    """3/8-24 studs in the housing (pivot + leveling) with outside nuts - envelopes."""
    out = []
    for x in (PIVOT_X, LEVEL_X):
        for s in (1, -1):
            y0 = R.HOUS_HALF if s > 0 else -R.HOUS_HALF - (HP_T + 0.05 + 0.35)
            st = cq.Workplane("XZ").center(x, 0).circle(0.1875).extrude(HP_T + 0.05 + 0.35).translate((0, y0 + HP_T + 0.4, 0))
            nut = (cq.Workplane("XZ").center(x, 0).polygon(6, 0.65).extrude(0.3)
                   .translate((0, (HP_Y0 + HP_T + 0.3) if s > 0 else -(HP_Y0 + HP_T), 0)))
            out.append(st.union(nut))
    return out


# ================================================================== assemblies
def rolling(phi, station=0.0, with_arm=False):
    """Balance-side parts rolled to phi; the yoke (0/90/180/270) or corner stirrup (45/135/...) hangs in the lab frame."""
    p = {"spindle": R.make_spindle(), "sting": K.make_sting(), "balance": K.make_balance(), "sleeve_6c": make_sleeve()}
    if with_arm:
        p["roll_arm"] = make_roll_arm()
    p = {k: v.rotate((0, 0, 0), (1, 0, 0), phi) for k, v in p.items()}
    if phi % 90 == 0:
        p["yoke_6c"] = S.make_yoke("6c", station)
    else:
        p["stirrup_45"] = make_stirrup(station)
    return p


def fixed():
    f = {f"roll_{k}": v for k, v in R.fixed().items()}
    f.update({"head_plate_p": make_head_plate(1), "head_plate_m": make_head_plate(-1), "jack_bridge_v2": make_jack_bridge(),
              "base_tube_v2": make_base_tube()})
    for i, x in enumerate((HP_X[0] + 0.5, HP_X[1] - 0.5)):
        f[f"cross_spacer{i}"] = make_cross_spacer(x)
    for i, st in enumerate(make_studs()):
        f[f"stud{i}"] = st
    for k, v in S.stand_parts().items():
        if k.startswith(("drag_", "thrust_")):
            f[k] = v
    f.update(S.drag_pulleys("6c"))
    return f


def vol(a, b):
    return a.val().intersect(b.val()).Volume()


def mass_props(wp, dens):
    s = wp.val()
    c = s.Center()
    return dict(W=round(s.Volume() * dens, 4), cg=[round(c.x, 4), round(c.y, 4), round(c.z, 4)])


if __name__ == "__main__":
    fx = fixed()
    print(f"sleeve {SL_OUT:.2f} in square, x {X_SL0:.2f}..{X_SL1:.2f}; stations {STATIONS}; head plates on the roll "
          f"housing studs (pivot x {PIVOT_X}, leveling slot x {LEVEL_X} +-{math.degrees(math.atan(LEVEL_TRAVEL / (LEVEL_X - PIVOT_X))):.1f} deg)")
    print("INTERFERENCE (in^3; studs are bolted into the housing by design)")
    worst = 0.0
    for phi in (0, 45, 90, 135, 180, 270, 315):
        for st in (-2.0, 0.0, 2.0):
            arm = (phi in (0, 180) and st == -2.0)
            rp = rolling(phi, st, with_arm=arm)
            hits = []
            for kr, vr in rp.items():
                for kf, vf in fx.items():
                    if kf.startswith("stud") and kr == "spindle":
                        continue
                    v = vol(vr, vf)
                    if v > 1e-6:
                        hits.append(f"{kr} x {kf} = {v:.4f}")
                    worst = max(worst, v)
            hang = "yoke_6c" if phi % 90 == 0 else "stirrup_45"
            for a, b in ((hang, "balance"), ("sleeve_6c", "sting"), (hang, "sting"), (hang, "sleeve_6c")) + \
                        ((("roll_arm", hang),) if arm else ()):
                v = vol(rp[a], rp[b])
                if v > 1e-6:
                    hits.append(f"{a} x {b} = {v:.4f}")
                worst = max(worst, v)
            print(f"  roll {phi:3d}  {hang} at x {st:+.0f}{' + roll arm' if arm else ''}: "
                  + ("clear" if not hits else "; ".join(hits)))
    for kf in ("head_plate_p", "head_plate_m", "jack_bridge_v2"):
        v = vol(fx[kf], fx["roll_housing_6061"])
        print(f"  {kf} x roll housing: {v:.5f}")
    # mass properties for the fit script (balance frame at roll 0)
    mp = {"sleeve": mass_props(cq.Workplane().add(make_sleeve().val()), AL),
          "yoke": mass_props(S.make_yoke("6c", 0.0), AL),
          "roll_arm": mass_props(make_roll_arm(), AL),
          "stirrup": mass_props(make_stirrup(0.0), AL),
          "x_eye": round(X_SL0 - 0.5, 3), "arm_top_z": round(ARM_TOP - 0.07, 3),          # knife-edge apex
          "arm_notch_y": list(ARM_NOTCH_Y)}
    (HERE.parents[1] / "analysis" / "calibration_6c_mass_properties.json").write_text(json.dumps(mp, indent=2))
    print("mass properties:", mp)
    exports = {"sleeve_6c_6061": make_sleeve(), "roll_arm_6061": make_roll_arm(), "stirrup_45_6061": make_stirrup(0.0), "yoke_6c_6061": S.make_yoke("6c", 0.0),
               "head_plate_v2_6061": fx["head_plate_p"], "jack_bridge_v2_6061": fx["jack_bridge_v2"],
               "cross_spacer_6061": fx["cross_spacer0"], "base_tube_v2": fx["base_tube_v2"]}
    for n, wp in exports.items():
        cq.exporters.export(cq.Workplane().add(wp.val().scale(IN)), str(HERE / f"{n}.step"))
    print("exported:", ", ".join(exports))
    for phi, arm in ((0, True), (45, False), (90, False)):
        asm = cq.Assembly(name=f"calibration_6c_roll{phi}")
        for k, v in rolling(phi, -2.0 if arm else 0.0, with_arm=arm).items():  # noqa
            asm.add(cq.Workplane().add(v.val().scale(IN)), name=k, color=cq.Color(0.7, 0.72, 0.78))
        for k, v in fx.items():
            asm.add(cq.Workplane().add(v.val().scale(IN)), name=k, color=cq.Color(0.85, 0.62, 0.22))
        asm.export(str(HERE / f"assembly_calibration_6c_roll{phi}.step"))
    print(f"assemblies written; worst interference {worst:.5f} in^3")
