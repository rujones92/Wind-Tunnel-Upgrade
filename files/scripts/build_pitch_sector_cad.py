r"""
Motorized pitch arc sector (-6 .. +20 deg) for the 6-component balance + roll spindle.

Pitch is a rotation about the lateral (y) axis through the BMC, so the model stays on the tunnel centreline.
MOVING (pitches): roll housing assembly (housing, caps, adapter, NMRV030 + NEMA 23, encoder), spindle, sting, balance,
                  puck, pod, 4 cam-follower rollers on the housing studs, drive bracket, pinion, pitch gearmotor.
FIXED (on the yaw carriage): 2 cheek plates with arc tracks, rack plate with an internal curved rack, base plate,
                  2 bottom spacers + top tie.
  - 4x 3/4 in cam followers (3/8-24 stud) at x = 17.3 / 19.4 in on both housing side faces run in arc tracks of
    radius 17.3 / 19.4 in cut through the 1/2 in cheeks (y = +-1.50 .. +-2.00).
  - +y cheek stays inside r = 20.5 in: the roll NEMA 23 sticks out in +y beyond r = 20.65 in.
  - Pitch drive on the -y side: module 1.25 internal curved rack, pitch radius 22.0 in, on a fixed rack plate
    (y = -2.60 .. -3.10); 20-tooth pinion on a bearing block bolted to the roll gearbox's -y face; 40:1 worm gearmotor
    (NEMA 17) outboard. Gravity always loads the mesh the same way (no backlash crossing).
  - Base plate 0.75 in = interface to the yaw carriage (to be designed); its underside is 1.5 in above the duct floor.
Coordinates: inches, x aft of the BMC, y spanwise, z up; STEP exported in mm.
Run (from this folder):  ..\..\.venv\Scripts\python build_pitch_sector_cad.py
"""
import math
import sys
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
for d in ("aluminum_balance", "six_component_balance", "roll_spindle"):
    sys.path.insert(0, str(HERE.parent / d))
from build_balance_cad import box          # noqa: E402
import build_6c_balance_cad as K           # noqa: E402
import build_roll_spindle_cad as R         # noqa: E402

IN = 25.4
ALPHA_MIN, ALPHA_MAX = -6.0, 20.0
TS_L, TS_W, TS_H, X_TS_BMC = 30.0, 26.25, 11.25, 17.0
Z_FLOOR = -22.7 / 2                          # downstream duct floor (assumed - confirm on the tunnel)
CARRIAGE_GAP = 1.5                           # yaw carriage + rails between floor and sector base
BASE_T = 0.75
Z_BASE_BOT = Z_FLOOR + CARRIAGE_GAP
Z_BASE_TOP = Z_BASE_BOT + BASE_T             # cheeks stand on this

# followers / tracks
R_TRK = R.FOLLOWERS                          # (17.3, 19.4) - follower stud x on the sting axis = track radii
ROLLER_D, ROLLER_W = 0.75, 0.50
SLOT_W = ROLLER_D + 0.002
CH_T = 0.50
Y_CH_IN = R.HOUS_HALF + 0.05                 # 1.50
Y_CH_OUT = Y_CH_IN + CH_T                    # 2.00
CH_R_IN, CH_R_OUT = 15.8, 20.5               # cheek band
CH_TH_LO, CH_TH_HI = -32.0, 16.0             # polar-angle range of the band (deg, + = above the axis)
# rack / drive
MODULE = 1.25 / 25.4                         # in
R_RACK = 22.0                                # rack pitch radius (internal teeth, facing the BMC)
PIN_Z = 20                                   # pinion teeth
R_PIN = PIN_Z * MODULE / 2                   # 0.492 in pitch radius
R_PIN_C = R_RACK - R_PIN                     # pinion centre radius 21.51
RK_Y0, RK_Y1 = -3.10, -2.60                  # rack plate
RK_R_OUT = 23.3
RK_TH_LO, RK_TH_HI = -27.0, 12.0
PIN_Y0, PIN_Y1 = -3.02, -2.68                # pinion face width 0.34 in


def polar(r, th):
    t = math.radians(th)
    return (r * math.cos(t), r * math.sin(t))


def xz_prism(pts, y0, y1):
    return cq.Workplane("XZ").polyline(pts).close().extrude(y1 - y0).translate((0, y1, 0))


def band(r0, r1, t0, t1, y0, y1, n=80):
    pts = [polar(r1, t0 + (t1 - t0) * i / n) for i in range(n + 1)] + \
          [polar(r0, t1 - (t1 - t0) * i / n) for i in range(n + 1)]
    return xz_prism(pts, y0, y1)


def arc_slot(r, w, t0, t1, y0, y1):
    s = band(r - w / 2, r + w / 2, t0, t1, y0, y1)
    for t in (t0, t1):
        cx, cz = polar(r, t)
        s = s.union(cq.Workplane("XZ").center(cx, cz).circle(w / 2).extrude(y1 - y0).translate((0, y1, 0)))
    return s


def above_base(shape):
    return shape.intersect(box(-50, 60, -10, 10, Z_BASE_TOP, 30))


# ================================================================== fixed parts
def follower_theta_range(extra=1.5):
    """Polar angles a follower on the sting axis visits (+ roller radius margin)."""
    return -ALPHA_MAX - extra, -ALPHA_MIN + extra


def make_cheek(side):
    y0, y1 = (Y_CH_IN, Y_CH_OUT) if side > 0 else (-Y_CH_OUT, -Y_CH_IN)
    c = band(CH_R_IN, CH_R_OUT, CH_TH_LO, CH_TH_HI, y0, y1)
    # foot forward of the band down to the base (keeps clear of the sting, which is between the cheeks)
    pi = polar(CH_R_IN, CH_TH_LO)
    c = c.union(xz_prism([(13.6, Z_BASE_TOP - 0.01), (pi[0] + 0.4, pi[1] + 0.2), (pi[0] + 2.0, pi[1] - 0.5),
                          (pi[0] + 2.0, Z_BASE_TOP - 0.01)], y0, y1))
    c = above_base(c)
    t0, t1 = follower_theta_range()
    for r in R_TRK:
        c = c.cut(arc_slot(r, SLOT_W, t0, t1, y0 - 0.1, y1 + 0.1))
    # top tie and spacer bolt holes (1/4 clearance) + base bolts (1/4-20 tapped into the bottom edge)
    for (x, z) in TIE_HOLES + SPACER_HOLES:
        c = c.cut(cq.Workplane("XZ").center(x, z).circle(0.1405).extrude(1).translate((0, y1 + 0.3, 0)))
    for x in BASE_BOLTS_X:
        c = c.cut(cq.Workplane("XY").center(x, (y0 + y1) / 2).circle(0.1005).extrude(0.75).translate((0, 0, Z_BASE_TOP)))
    return c


TOP_TIE = (polar(17.6, 14.0), polar(19.6, 14.0))       # tie block between the cheeks, above the swept region
TIE_HOLES = [polar(17.9, 14.2), polar(19.3, 14.2)]
SPACER_POS = [(14.6, Z_BASE_TOP + 0.5), (17.0, Z_BASE_TOP + 0.45)]
SPACER_HOLES = SPACER_POS
BASE_BOLTS_X = [14.2, 15.6, 17.4]


def make_top_tie():
    (xa, za), (xb, zb) = TOP_TIE
    pts = [polar(17.4, 13.0), polar(19.8, 13.0), polar(19.8, 15.5), polar(17.4, 15.5)]
    t = xz_prism(pts, -Y_CH_IN, Y_CH_IN)
    for (x, z) in TIE_HOLES:
        t = t.cut(cq.Workplane("XZ").center(x, z).circle(0.1005).extrude(4).translate((0, 2, 0)))
    return t


def make_spacer(x, z, h):
    s = box(x - 0.5, x + 0.5, -Y_CH_IN, Y_CH_IN, Z_BASE_TOP, Z_BASE_TOP + h)
    return s.cut(cq.Workplane("XZ").center(x, z).circle(0.1005).extrude(4).translate((0, 2, 0)))


def make_rack_plate(teeth=True):
    rp = band(R_RACK + 1.25 * MODULE, RK_R_OUT, RK_TH_LO, RK_TH_HI, RK_Y0, RK_Y1)   # root circle inside
    if teeth:   # cosmetic internal teeth (module 1.25), tips at r = R_RACK - module
        pitch_ang = math.degrees(math.pi * MODULE / R_RACK)
        n = int((RK_TH_HI - RK_TH_LO - 2) / pitch_ang)
        th = RK_TH_LO + 1
        for _ in range(n):
            a, b = th + pitch_ang * 0.12, th + pitch_ang * 0.88
            pts = [polar(R_RACK + 1.25 * MODULE + 0.002, a), polar(R_RACK - MODULE, th + pitch_ang * 0.32),
                   polar(R_RACK - MODULE, th + pitch_ang * 0.68), polar(R_RACK + 1.25 * MODULE + 0.002, b)]
            rp = rp.union(xz_prism(pts, RK_Y0, RK_Y1))
            th += pitch_ang
    # leg to the base (outer side) and two 1/4-20 holes in its foot
    po = polar(RK_R_OUT, RK_TH_LO)
    pi = polar(R_RACK + 0.3, RK_TH_LO)
    rp = rp.union(xz_prism([(pi[0], pi[1]), (po[0], po[1]), (po[0] + 0.6, Z_BASE_TOP - 0.01),
                            (pi[0] - 0.3, Z_BASE_TOP - 0.01)], RK_Y0, RK_Y1))
    rp = above_base(rp)
    for x in (pi[0] + 0.1, po[0] + 0.3):
        rp = rp.cut(cq.Workplane("XY").center(x, (RK_Y0 + RK_Y1) / 2).circle(0.1005).extrude(0.75)
                    .translate((0, 0, Z_BASE_TOP)))
    return rp


BASE_NOTCH_X = 18.4                          # aft of this, only a -y strip remains: the roll gearbox and NEMA 23
BASE_STRIP_Y = -2.3                          # swing down through the notch at high pitch


def make_base():
    x0, x1 = 13.4, 22.6
    b = box(x0, BASE_NOTCH_X, RK_Y0 - 0.3, Y_CH_OUT + 0.3, Z_BASE_BOT, Z_BASE_TOP)
    b = b.union(box(BASE_NOTCH_X - 0.01, x1, RK_Y0 - 0.3, BASE_STRIP_Y, Z_BASE_BOT, Z_BASE_TOP))
    for x in BASE_BOLTS_X:                                     # cheek bolts (clearance, c'bored from below)
        for y in ((Y_CH_IN + Y_CH_OUT) / 2, -(Y_CH_IN + Y_CH_OUT) / 2):
            b = b.cut(cq.Workplane("XY").center(x, y).circle(0.1405).extrude(2, both=True))
    po, pi = polar(RK_R_OUT, RK_TH_LO), polar(R_RACK + 0.3, RK_TH_LO)
    for x in (pi[0] + 0.1, po[0] + 0.3):
        b = b.cut(cq.Workplane("XY").center(x, (RK_Y0 + RK_Y1) / 2).circle(0.1405).extrude(2, both=True))
    for (x, y) in ((x0 + 0.5, RK_Y0), (x0 + 0.5, Y_CH_OUT), (BASE_NOTCH_X - 0.5, Y_CH_OUT), (x1 - 0.5, RK_Y0)):
        b = b.cut(cq.Workplane("XY").center(x, y).circle(0.203).extrude(2, both=True))   # 4x 3/8 to the carriage
    return b


def make_test_section():
    x0, x1, t = -X_TS_BMC, TS_L - X_TS_BMC, 0.5
    ts = box(x0, x1, -TS_W / 2 - t, TS_W / 2 + t, -TS_H / 2 - t, TS_H / 2 + t)
    ts = ts.cut(box(x0 - 1, x1 + 1, -TS_W / 2, TS_W / 2, -TS_H / 2, TS_H / 2))
    return ts.union(box(x1, x1 + 14, -18, 18, Z_FLOOR - t, Z_FLOOR))


# ================================================================== moving parts added by this design
def make_followers():
    out = []
    for xf in R_TRK:
        for s in (1, -1):
            yr0 = s * (R.HOUS_HALF + 0.05)
            roller = (cq.Workplane("XZ").center(xf, 0).circle(ROLLER_D / 2).extrude(ROLLER_W)
                      .translate((0, (yr0 + ROLLER_W) if s > 0 else yr0, 0)))
            stud = (cq.Workplane("XZ").center(xf, 0).circle(0.1875).extrude(0.05 + 0.001)
                    .translate((0, (R.HOUS_HALF + 0.05) if s > 0 else -R.HOUS_HALF, 0)))
            out.append(roller.union(stud))
    return out


G_X0, G_X1 = R.GBX
G_YM = -R.GBX_HALF                            # gearbox -y face


def make_drive_bracket():
    """Plate on the roll gearbox -y face + bearing block carrying the pinion shaft (axis along y) at r = 21.51."""
    xc = R_PIN_C                              # pinion centre at alpha = 0: (21.51, 0)
    p = box(G_X0 + 0.15, G_X1 - 0.15, G_YM - 0.25, G_YM, -1.15, 1.15)           # plate on the gearbox face
    blk = box(xc - 0.65, xc + 0.65, -2.55, G_YM - 0.25, -0.65, 0.65)             # bearing block (outboard of cheek)
    b = p.union(blk)
    b = b.cut(cq.Workplane("XZ").center(xc, 0).circle(0.4331).extrude(1.05).translate((0, G_YM - 0.25, 0)))  # 22 H7: 2x 608
    b = b.cut(cq.Workplane("XZ").center(xc, 0).circle(0.20).extrude(3).translate((0, 0, 0)))  # shaft clearance thru plate
    for x in (G_X0 + 0.45, G_X1 - 0.45):                                          # 4x M6 to the gearbox (CONFIRM vendor)
        for z in (-0.90, 0.90):                                                   # clear of the bearing block
            b = b.cut(cq.Workplane("XZ").center(x, z).circle(0.128).extrude(1).translate((0, G_YM + 0.2, 0)))
    return b


def make_pinion():
    return (cq.Workplane("XZ").center(R_PIN_C, 0).circle(R_PIN - 1.25 * MODULE * 0.1).extrude(PIN_Y1 - PIN_Y0)
            .translate((0, PIN_Y1, 0))
            .union(cq.Workplane("XZ").center(R_PIN_C, 0).circle(0.157).extrude(1.2).translate((0, -2.55 + 0.6, 0))))


def make_pitch_gearmotor():
    """Envelope: small 40:1 worm gearbox (output along -y into the pinion) + NEMA 17 pointing aft."""
    xc = R_PIN_C
    g = box(xc - 0.75, xc + 0.75, -4.55, -3.20, -0.75, 0.75)
    m = box(xc + 0.75, xc + 2.35, -4.38, -3.36, -0.83, 0.83)
    return g.union(m)


def roll_assembly_parts():
    parts = {"spindle": R.make_spindle(), "sting": K.make_sting(), "balance": K.make_balance(), "puck": K.make_puck(),
             "pod": K.make_pod()}
    parts.update({k: v for k, v in R.fixed().items()})
    return parts


def moving(alpha):
    parts = roll_assembly_parts()
    for i, f in enumerate(make_followers()):
        parts[f"follower{i}"] = f
    parts["drive_bracket"] = make_drive_bracket()
    parts["pinion"] = make_pinion()
    parts["pitch_gearmotor"] = make_pitch_gearmotor()
    return {k: v.rotate((0, 0, 0), (0, 1, 0), alpha) for k, v in parts.items()}


def fixed():
    f = {"cheek_plus_y": make_cheek(+1), "cheek_minus_y": make_cheek(-1), "rack_plate": make_rack_plate(),
         "base_plate": make_base(), "top_tie": make_top_tie()}
    for i, (x, z) in enumerate(SPACER_POS):
        f[f"spacer{i}"] = make_spacer(x, z, 0.9 if i == 0 else 0.8)
    return f


def vol(a, b):
    return a.val().intersect(b.val()).Volume()


# ================================================================== run
if __name__ == "__main__":
    fx = fixed()
    ts = make_test_section()
    print(f"sector: cheeks r {CH_R_IN}-{CH_R_OUT} in, tracks r {R_TRK}, rack pitch r {R_RACK} (module 1.25, "
          f"{PIN_Z}-tooth pinion r {R_PIN:.3f}), base plate z {Z_BASE_BOT:.2f}..{Z_BASE_TOP:.2f}")
    print("INTERFERENCE SWEEP (in^3; rack x pinion is the gear mesh and is excluded)")
    worst_all = 0.0
    for a in (ALPHA_MIN, -3, 0, 5, 10, 15, ALPHA_MAX):
        mv = moving(a)
        worst, hits = 0.0, []
        for km, vm in mv.items():
            for kf, vf in list(fx.items()) + [("test_section", ts)]:
                if km == "pinion" and kf == "rack_plate":
                    continue
                v = vol(vm, vf)
                if v > 1e-6:
                    hits.append(f"{km} x {kf} = {v:.4f}")
                worst = max(worst, v)
        worst_all = max(worst_all, worst)
        print(f"  alpha {a:+5.1f}: max {worst:.5f}" + ("".join("\n     " + h for h in hits) if hits else ""))
    # mesh check: pinion pitch circle tangent to the rack pitch circle at every alpha
    for a in (ALPHA_MIN, ALPHA_MAX):
        c = cq.Vector(R_PIN_C, 0, 0)
        cr = c.toTuple()
        ca = (cr[0] * math.cos(math.radians(a)), -cr[0] * math.sin(math.radians(a)))
        print(f"  alpha {a:+.0f}: pinion centre radius {math.hypot(*ca):.3f} in, polar angle "
              f"{math.degrees(math.atan2(ca[1], ca[0])):+.1f} deg (rack teeth span {RK_TH_LO + 1:+.0f}..{RK_TH_HI - 1:+.0f})")

    # loads
    m_grav = 2.5 * 11.0 + 11.0 * 20.5          # sting + roll assembly (~11 lb incl. NEMA 23, gearbox, housing) about the BMC
    m_tot = m_grav + 15.0
    f_t = m_tot / R_RACK
    print(f"\nLOADS: gravity moment about the BMC ~{m_grav:.0f} in-lbf + aero m 15 -> rack force {f_t:.1f} lbf, "
          f"pinion torque {f_t * R_PIN:.1f} in-lbf, NEMA 17 + 40:1 worm (35 % eff.) needs "
          f"{f_t * R_PIN / (40 * 0.35) * 0.113 * 1000:.0f} mN-m")
    N = 25.0
    d = R_TRK[1] - R_TRK[0]
    print(f"  followers at N = {N} lbf: {N * R_TRK[1] / d:.0f} / {N * R_TRK[0] / d:.0f} lbf (shared by 2 rollers each; "
          "3/4 in cam follower static rating ~1,000+ lbf)")
    print(f"  pitch resolution: 1/16 step, 40:1 -> {360 / 3200 / 40 * R_PIN / R_RACK:.5f} deg per microstep")

    # export parts + assemblies
    exports = {**fx, "drive_bracket_6061": cq.Workplane().add(make_drive_bracket().val()),
               "pinion_m1.25_20T": make_pinion(), "pitch_gearmotor_envelope": make_pitch_gearmotor(),
               "cam_follower_3-4in_envelope": make_followers()[0]}
    for n, wp in exports.items():
        cq.exporters.export(cq.Workplane().add(wp.val().scale(IN)), str(HERE / f"{n}.step"))
    print("exported:", ", ".join(exports))
    for a in (ALPHA_MIN, 0, ALPHA_MAX):
        asm = cq.Assembly(name=f"pitch_sector_alpha{a:+.0f}")
        for k, v in moving(a).items():
            asm.add(cq.Workplane().add(v.val().scale(IN)), name=f"m_{k}", color=cq.Color(0.6, 0.6, 0.66))
        for k, v in fx.items():
            asm.add(cq.Workplane().add(v.val().scale(IN)), name=f"f_{k}", color=cq.Color(0.85, 0.62, 0.22))
        asm.export(str(HERE / f"assembly_pitch_sector_alpha{a:+.0f}.step"))
    print(f"assemblies at alpha {ALPHA_MIN:+.0f}, 0, {ALPHA_MAX:+.0f} written; worst interference {worst_all:.5f} in^3")
