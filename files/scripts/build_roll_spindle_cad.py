r"""
Roll spindle (+-90 deg) at the sting root, for the six-component balance (cad/six_component_balance).

Layout along the sting axis (x, inches from the BMC; the housing does not roll, everything inside it does):
  16.45  front cap             retains the front bearing outer ring
  16.65  front bearing 6907    35 x 55 x 10 mm deep-groove, sealed
  17.0-20.0  sting flats in the spindle's D-D bore; 2x 1/4-20 bolts at x = 17.75 / 19.25 (top clearance + c'bore,
             bottom tapped) reached through the housing's top windows at roll 0
  19.66  rear bearing 6907     (bearing span 3.0 in), preloaded by a KM7 (M35x1.5) locknut inside the rear cap
  20.50  wire exit             the sting wire bore turns radially out through the spindle, into the adapter window
  20.80-22.80  NMRV030 50:1 worm gearbox (purchased; self-locking), hollow 14 mm output keyed onto the spindle;
               NEMA 23 on its input, pointing +y (sideways)
  23.30  spindle end           6 mm diametric magnet on axis -> AS5048A absolute encoder on a bracket
All drive parts sit more than 21 in from the BMC, outside the pitch-sector cheek band (16.4..20.7 in), so pitch rotation
never sweeps them into the cheeks; the motor points sideways so it stays off the floor at +20 deg pitch.
Purchased parts (gearbox, motor, bearings, locknut) are modelled as envelopes - check the vendor drawings.
Run (from this folder):  ..\..\.venv\Scripts\python build_roll_spindle_cad.py
"""
import math
import sys
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "aluminum_balance"))
sys.path.insert(0, str(HERE.parent / "six_component_balance"))
sys.path.insert(0, str(HERE.parent))
from build_balance_cad import box          # noqa: E402
import build_6c_balance_cad as K           # noqa: E402

IN = 25.4
MM = 1 / 25.4
# bearings 6907: 35 x 55 x 10 mm
B_ID, B_OD, B_W = 35 * MM, 55 * MM, 10 * MM
LIP = 0.04                          # cap pilot lip that clamps each bearing outer ring
X_BF0 = 16.65                       # front bearing front face
X_BR1 = X_BF0 + 3.0 + B_W           # rear bearing rear face (span 3.0 in centre-centre)
X_BR0 = X_BR1 - B_W
HOUS_HALF = 1.45                    # housing 2.90 x 2.90 square
CAP_T = 0.20
REAR_CAP_BORE = 2.10                # clears the KM7 locknut (52 mm = 2.047 in), lip still bears on the outer ring
X_HOUS0, X_HOUS1 = X_BF0 - LIP, X_BR1 + LIP     # housing body
X_CAPF0 = X_HOUS0 - CAP_T
X_CAPR1 = X_HOUS1 + CAP_T
SHOULDER_D = 1.50                   # spindle body between bearings
HOUSING_INNER_D = 1.70
ADAPTER = (X_CAPR1, X_CAPR1 + 0.55)
GBX = (ADAPTER[1] + 0.05, ADAPTER[1] + 2.05)      # NMRV030 envelope along x
GBX_HALF = 1.25
GBX_CD = 30 * MM                    # worm centre distance (input axis below the output)
DRIVE_D = 14 * MM
X_END = GBX[1] + 0.50
X_WIRE = ADAPTER[0] + 0.25
STING_BOLTS = (17.75, 19.25)
FOLLOWERS = (17.3, 19.4)            # cam-follower studs, both side faces: kept over the clearance bore
STUD_DEPTH = 0.45                   # (wall there is 0.60 thick; deeper would break into the bore)


def cyl(d, x0, x1, y=0.0, z=0.0):
    return cq.Workplane("YZ").center(y, z).circle(d / 2).extrude(x1 - x0).translate((x0, 0, 0))


def ring(od, idd, x0, x1):
    return cyl(od, x0, x1).cut(cyl(idd, x0 - 0.01, x1 + 0.01))


# ================================================================== spindle (4140, rotates with the sting)
def make_spindle():
    x_nose = X_CAPF0
    s = cyl(1.30, x_nose, X_BF0)                                   # nose through the front cap
    s = s.union(cyl(B_ID, X_BF0, X_BF0 + B_W))                     # front bearing seat
    s = s.union(cyl(SHOULDER_D, X_BF0 + B_W, X_BR0))               # body / bearing shoulders
    s = s.union(cyl(B_ID, X_BR0, X_BR1))                           # rear bearing seat
    s = s.union(cyl(B_ID - 0.02, X_BR1, X_BR1 + 0.38))             # M35x1.5 thread for the KM7 locknut
    s = s.union(cyl(1.0, X_BR1 + 0.38, ADAPTER[1] + 0.02))         # wire-exit neck
    s = s.union(cyl(DRIVE_D, ADAPTER[1] + 0.02, GBX[1] + 0.05))    # 14 mm keyed drive shaft through the gearbox
    s = s.union(cyl(0.50, GBX[1] + 0.05, X_END))                   # encoder end
    # sting bore: round ahead of the flats, D-D over the flats (x 17..20)
    r_st = K.STING_D / 2 + 0.0025
    x_flat0, x_sting_end = 20.0 - 3.0, 20.0
    s = s.cut(cyl(2 * r_st, x_nose - 0.01, x_flat0))
    dd = cyl(2 * r_st, x_flat0, x_sting_end + 0.01).intersect(box(x_flat0 - 0.1, x_sting_end + 0.1, -1, 1, -0.3525, 0.3525))
    s = s.cut(dd)
    # wire path: axial 0.30 bore from the sting end to the exit neck, radial exits up and down
    s = s.cut(cyl(0.30, x_sting_end - 0.01, X_WIRE + 0.15))
    s = s.cut(cq.Workplane("XY").center(X_WIRE, 0).circle(0.125).extrude(2, both=True))
    # sting bolts: top clearance + c'bore, bottom tapped 1/4-20
    for xb in STING_BOLTS:
        s = s.cut(cq.Workplane("XY").center(xb, 0).circle(0.1405).extrude(1.0))
        s = s.cut(cq.Workplane("XY").center(xb, 0).circle(0.21).extrude(0.3).translate((0, 0, SHOULDER_D / 2 - 0.28)))
        s = s.cut(cq.Workplane("XY").center(xb, 0).circle(0.1005).extrude(-1.0))
    # 5 mm key on the drive shaft, 6 x 2.5 mm magnet pocket on the end
    s = s.cut(box(ADAPTER[1] + 0.15, GBX[1] - 0.10, -2.5 * MM, 2.5 * MM, DRIVE_D / 2 - 3 * MM, 1))
    s = s.cut(cyl(6 * MM, X_END - 2.5 * MM, X_END + 0.01))
    return s


# ================================================================== fixed parts
def make_housing():
    h = box(X_HOUS0, X_HOUS1, -HOUS_HALF, HOUS_HALF, -HOUS_HALF, HOUS_HALF)
    h = h.cut(cyl(B_OD + 0.0005, X_HOUS0 - 0.01, X_BF0 + B_W))       # front bearing bore (+ cap lip)
    h = h.cut(cyl(B_OD + 0.0005, X_BR0, X_HOUS1 + 0.01))             # rear bearing bore (+ cap lip)
    h = h.cut(cyl(HOUSING_INNER_D, X_HOUS0, X_HOUS1))                 # clearance bore / outer-ring shoulders
    for xb in STING_BOLTS:                                            # top access windows for the sting bolts
        h = h.cut(cq.Workplane("XY").center(xb, 0).circle(0.30).extrude(2))
    for xf in FOLLOWERS:                                              # 3/8-24 cam-follower studs, both sides
        h = h.cut(cq.Workplane("XZ").center(xf, 0).circle(0.166).extrude(STUD_DEPTH).translate((0, HOUS_HALF + 0.01, 0)))
        h = h.cut(cq.Workplane("XZ").center(xf, 0).circle(0.166).extrude(-STUD_DEPTH).translate((0, -HOUS_HALF - 0.01, 0)))
    for x in (X_HOUS0 + 0.35, X_HOUS1 - 0.35):                        # 1/4-20 mounting holes, both sides, z = +-1.0
        for z in (-1.0, 1.0):
            h = h.cut(cq.Workplane("XZ").center(x, z).circle(0.1005).extrude(0.6).translate((0, HOUS_HALF + 0.01, 0)))
            h = h.cut(cq.Workplane("XZ").center(x, z).circle(0.1005).extrude(-0.6).translate((0, -HOUS_HALF - 0.01, 0)))
    for x in (X_HOUS0, X_HOUS1):                                      # #8-32 cap screws, 4 per end
        for y, z in ((1.15, 1.15), (-1.15, 1.15), (1.15, -1.15), (-1.15, -1.15)):
            d0 = x if x == X_HOUS0 else x - 0.5
            h = h.cut(cyl(0.136, d0, d0 + 0.5, y, z))
    return h


def make_cap(front=True):
    """End cap with a pilot lip that enters the bearing bore and clamps the outer ring."""
    x0, x1 = (X_CAPF0, X_HOUS0) if front else (X_HOUS1, X_CAPR1)
    bore = 1.40 if front else REAR_CAP_BORE
    c = box(x0, x1, -HOUS_HALF, HOUS_HALF, -HOUS_HALF, HOUS_HALF).cut(cyl(bore, x0 - 0.01, x1 + 0.01))
    c = c.union(ring(B_OD - 0.001, bore, x1, x1 + LIP) if front else ring(B_OD - 0.001, bore, x0 - LIP, x0))
    for y, z in ((1.15, 1.15), (-1.15, 1.15), (1.15, -1.15), (-1.15, -1.15)):
        c = c.cut(cyl(0.177, x0 - 0.05, x1 + 0.05, y, z))
    return c


def make_adapter():
    """Spacer between the rear cap and the gearbox: locknut clearance, top/bottom wire-exit windows (+-100 deg arc)."""
    x0, x1 = ADAPTER
    a = box(x0, x1, -HOUS_HALF, HOUS_HALF, -HOUS_HALF, HOUS_HALF)
    a = a.cut(cyl(2.20, x0 - 0.01, x1 + 0.01))
    a = a.cut(box(X_WIRE - 0.20, X_WIRE + 0.20, -HOUS_HALF - 0.1, HOUS_HALF + 0.1, 0.4, HOUS_HALF + 0.1))  # wire window
    for y, z in ((1.15, 1.15), (-1.15, 1.15), (1.15, -1.15), (-1.15, -1.15)):
        a = a.cut(cyl(0.177, x0 - 0.01, x1 + 0.01, y, z))
    return a


def make_gearbox_envelope():
    """NMRV030 50:1 (purchased): body around the output axis, input boss + NEMA 23 flange along +y, input axis below."""
    g = box(*GBX, -GBX_HALF, GBX_HALF, -GBX_HALF - 0.3, GBX_HALF)
    g = g.cut(cyl(DRIVE_D + 0.004, GBX[0] - 0.01, GBX[1] + 0.01))          # hollow output
    xm = (GBX[0] + GBX[1]) / 2
    flange = box(xm - 1.12, xm + 1.12, GBX_HALF, GBX_HALF + 0.45, -GBX_CD - 1.12, -GBX_CD + 1.12)
    return g.union(flange)


def make_motor():
    xm = (GBX[0] + GBX[1]) / 2
    y0 = GBX_HALF + 0.45
    m = box(xm - 1.11, xm + 1.11, y0, y0 + 2.2, -GBX_CD - 1.11, -GBX_CD + 1.11)       # NEMA 23, 56 mm body
    return m.union(cq.Workplane("XZ").center(xm, -GBX_CD).circle(0.30).extrude(-0.4).translate((0, y0 + 2.2, 0)))


ENC_T = 0.12                         # encoder bracket plate thickness
ENC_GAP = 1.5 * MM                   # magnet face to AS5048A chip (datasheet range ~0.5-2.5 mm)


def make_encoder_bracket():
    """1/8 in plate bolted flat to the gearbox output face; spindle end passes through; 4x M3 standoffs carry the
    AS5048A board on axis, ENC_GAP from the magnet face. Gearbox holes: 2 slots fit the vendor's tapped holes."""
    x0 = GBX[1]
    b = box(x0, x0 + ENC_T, -0.75, 0.75, -0.75, 0.75)
    b = b.cut(cyl(0.60, x0 - 0.01, x0 + ENC_T + 0.01))                          # spindle end clearance
    for z in (-0.58, 0.58):                                                     # 2x slots for gearbox screws
        b = b.cut(cq.Workplane("YZ").center(0, z).slot2D(0.45, 0.22, 0).extrude(ENC_T + 0.02)
                  .translate((x0 - 0.01, 0, 0)))
    for y, z in ((0.40, 0.30), (-0.40, 0.30), (0.40, -0.30), (-0.40, -0.30)):    # 4x M3 tapped (2.5 mm drill)
        b = b.cut(cyl(2.5 * MM, x0 - 0.01, x0 + ENC_T + 0.01, y, z))
    return b


def make_encoder_board():
    """AS5048A adapter board envelope (~0.9 in square) + 4 standoffs."""
    xb = X_END + ENC_GAP
    brd = box(xb, xb + 1.6 * MM, -0.45, 0.45, -0.45, 0.45)
    for y, z in ((0.40, 0.30), (-0.40, 0.30), (0.40, -0.30), (-0.40, -0.30)):
        brd = brd.union(cyl(5 * MM, GBX[1] + ENC_T, xb, y, z))
    return brd


def make_bearings():
    return [ring(B_OD, B_ID, X_BF0, X_BF0 + B_W), ring(B_OD, B_ID, X_BR0, X_BR1)]


def make_locknut():
    return ring(52 * MM, B_ID - 0.02, X_BR1 + 0.01, X_BR1 + 0.01 + 0.315)


# ================================================================== build, check, export
def rotating(phi=0.0):
    parts = {"spindle_4140": make_spindle(), "sting": K.make_sting(), "balance": K.make_balance(),
             "puck": K.make_puck(), "pod": K.make_pod()}
    return {k: v.rotate((0, 0, 0), (1, 0, 0), phi) for k, v in parts.items()}


def fixed():
    f = {"housing_6061": make_housing(), "front_cap_6061": make_cap(True), "rear_cap_6061": make_cap(False),
         "gearbox_adapter_6061": make_adapter(), "gearbox_NMRV030_envelope": make_gearbox_envelope(),
         "motor_NEMA23_envelope": make_motor(), "encoder_bracket": make_encoder_bracket(),
         "encoder_board_AS5048A_envelope": make_encoder_board()}
    return f


def vol(a, b):
    return a.val().intersect(b.val()).Volume()


if __name__ == "__main__":
    fx = fixed()
    brg = make_bearings()
    nut = make_locknut()
    sp = make_spindle()
    print(f"spindle: x {X_CAPF0:.2f}..{X_END:.2f} in, bearings centres {X_BF0 + B_W/2:.3f} / {X_BR0 + B_W/2:.3f} "
          f"(span {X_BR0 - X_BF0:.2f}), drive {GBX[0]:.2f}..{GBX[1]:.2f}, wire exit x {X_WIRE:.2f}")
    print(f"  min radius of drive parts from the BMC: {math.hypot(GBX[0], 0):.2f} in (cheek band ends at 20.7)")
    # bearing fits: bearing vs spindle seat and housing bore should touch (tiny/zero overlap), nothing else
    print("CHECKS (in^3; 0 = clear)")
    for phi in (-90, -45, 0, 45, 90):
        rot = rotating(phi)
        w, hits = 0.0, []
        for kr, vr in rot.items():
            for kf, vf in fx.items():
                v = vol(vr, vf)
                if v > 1e-6:
                    hits.append(f"{kr} x {kf} {v:.4f}")
                w = max(w, v)
        print(f"  roll {phi:+4d}: rotating parts vs housing/caps/gearbox/motor/encoder max {w:.5f}"
              + ("".join("\n     " + h for h in hits) if hits else ""))
    print(f"  sting x spindle {vol(K.make_sting(), sp):.5f} ; bearings x spindle "
          f"{max(vol(b, sp) for b in brg):.5f} ; bearings x housing {max(vol(b, fx['housing_6061']) for b in brg):.5f} ; "
          f"locknut x rear cap {vol(nut, fx['rear_cap_6061']):.5f}")
    # loads / stresses
    N = 25.0
    x_bf, x_br = X_BF0 + B_W / 2, X_BR0 + B_W / 2
    R_r = N * x_bf / (x_br - x_bf)
    R_f = N + R_r
    M = N * x_bf
    Z = math.pi * (B_ID**4 - K.STING_D**4) / (32 * B_ID)
    print(f"LOADS at N = {N} lbf: front bearing {R_f:.0f} lbf, rear {R_r:.0f} lbf (6907 C ~ 2,700 lbf) ; "
          f"spindle bending at the front seat {M:.0f} in-lbf -> {M/Z:,.0f} psi (4140 HT yield ~100 ksi)")
    print(f"ROLL DRIVE: 35 in-lbf / (50 x 0.35) = {35/(50*0.35)*0.113:.2f} N-m at the NEMA 23 ; +-90 deg in 10 s = 150 rpm")

    exports = {**fx, "spindle_4140": sp, "bearing_6907_envelope": cq.Workplane().add(brg[0].val()),
               "locknut_KM7_envelope": nut}
    for n, wp in exports.items():
        cq.exporters.export(cq.Workplane().add(wp.val().scale(IN)), str(HERE / f"{n}.step"))
    print("exported:", ", ".join(exports))
    for phi in (0, 90):
        asm = cq.Assembly(name=f"roll_spindle_phi{phi:+d}")
        for k, v in rotating(phi).items():
            asm.add(cq.Workplane().add(v.val().scale(IN)), name=k,
                    color=cq.Color(*{"spindle_4140": (0.45, 0.45, 0.5), "sting": (0.35, 0.35, 0.35),
                                     "balance": (0.75, 0.75, 0.8), "puck": (0.55, 0.6, 0.9),
                                     "pod": (0.2, 0.7, 0.4, 0.35)}[k]))
        for k, v in fx.items():
            asm.add(cq.Workplane().add(v.val().scale(IN)), name=k, color=cq.Color(0.85, 0.62, 0.22))
        for i, b in enumerate(brg + [nut]):
            asm.add(cq.Workplane().add(b.val().scale(IN)), name=f"bearing_or_nut_{i}", color=cq.Color(0.2, 0.2, 0.25))
        asm.export(str(HERE / f"assembly_roll_spindle_phi{phi:+d}.step"))
        print(f"  assembly_roll_spindle_phi{phi:+d}.step")
