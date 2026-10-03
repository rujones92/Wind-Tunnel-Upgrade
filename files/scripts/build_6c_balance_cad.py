r"""
Six-component aluminum sting balance - CAD (sizes from ../../analysis/six_component_balance_sizing.py).

One piece 7075-T651:  front block | FWD neck | block | axial Z-flexure | block | AFT neck | aft block | 0.750 spigot
  - Necks 0.220 W (y) x 0.510 H (z) x 0.90 L, stations at x = +-1.35 in, cut from all four sides with r 0.06 fillets
    in both planes (pitch AND yaw bending, roll torsion).
  - Axial flexure, slots, front-face pattern and spigot details as the 3-component balance.
Also builds the matching model puck, instrumented 2.25 in pod (longer) and the 17.45 in sting (clamp flats stay at
x = 17..20 in for the roll spindle / pitch sector).
Coordinates (inches, exported mm): x aft, y spanwise, z up, BMC at x = 0.
Run (from this folder):  ..\..\.venv\Scripts\python build_6c_balance_cad.py
"""
import math
import sys
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "aluminum_balance"))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[1] / "analysis"))
from build_balance_cad import box, xz_cut          # noqa: E402
import pod_instrumentation as PI                   # noqa: E402
import six_component_balance_sizing as S6          # noqa: E402

IN = 25.4
W, H = S6.BAR_W, S6.BAR_H
_, _, NB, NH = S6.size_neck()                       # 0.220, 0.510
LN, RF = S6.L_NECK, S6.R_FIL
XS = S6.a                                           # 1.35
FWD = (-XS - LN / 2, -XS + LN / 2)
AFT = (XS - LN / 2, XS + LN / 2)
BLOCK_END = 0.75
X_FRONT = FWD[0] - BLOCK_END                        # -2.55
X_AFT = AFT[1] + BLOCK_END                          # +2.55
RAIL, T_P, E_P, X_AX, SLOT, R_W = 0.25, 0.025, 0.75, 0.60, 0.012, 0.03
SPIG_D, SPIG_L = 0.75, 1.25
PIN_X = X_AFT + 0.90
STING_D = 0.875
STING_L = 20.0 - X_AFT                              # flats at x = 17..20 as before
PUCK_D, PUCK_T = 1.70, 0.30
POD_D, POD_BASE_D, POD_BORE_R = 2.25, 1.50, 0.8525


def xy_cut(x0, x1, y0, y1, r=0.0, sel=None):
    """Through-all (z) prism with optional fillets on its z-parallel edges."""
    c = box(x0, x1, y0, y1, -2, 2)
    if r > 0:
        c = c.edges("|Z").edges(sel).fillet(r)
    return c


def make_balance(with_plates=True):
    b = box(X_FRONT, X_AFT, -W / 2, W / 2, -H / 2, H / 2)
    for x0, x1 in (FWD, AFT):
        b = b.cut(xz_cut(x0, x1, NH / 2, H, RF, "<Z")).cut(xz_cut(x0, x1, -H, -NH / 2, RF, ">Z"))   # pitch flats
        b = b.cut(xy_cut(x0, x1, NB / 2, 1.0, RF, "<Y")).cut(xy_cut(x0, x1, -1.0, -NB / 2, RF, ">Y"))  # yaw flats
    zi = H / 2 - RAIL
    xa, xb = -E_P / 2, E_P / 2
    b = b.cut(xz_cut(xa + T_P / 2, xb - T_P / 2, -zi, zi, R_W))
    b = b.cut(xz_cut(-X_AX, xa - T_P / 2, -zi, zi, R_W))
    b = b.cut(xz_cut(xb + T_P / 2, X_AX, -zi, zi, R_W))
    b = b.cut(xz_cut(-X_AX - SLOT, -X_AX, zi - 0.075, H))
    b = b.cut(xz_cut(X_AX, X_AX + SLOT, -H, -zi + 0.075))
    if not with_plates:
        for xc in (xa, xb):
            b = b.cut(xz_cut(xc - T_P, xc + T_P, -zi - 0.01, zi + 0.01))
    # spigot: set-screw flat, 3/16 cross pin, wire bore + exit through the top of the aft block
    b = b.union(cq.Workplane("YZ").circle(SPIG_D / 2).extrude(SPIG_L).translate((X_AFT, 0, 0)))
    b = b.cut(box(X_AFT + 0.15, X_AFT + SPIG_L + 0.1, -1, 1, SPIG_D / 2 - 0.075, 1))
    b = b.cut(cq.Workplane("XZ").center(PIN_X, 0).circle(0.09375).extrude(1, both=True))
    b = b.cut(cq.Workplane("YZ").circle(0.125).extrude(X_AFT + SPIG_L - (X_AFT - 0.25)).translate((X_AFT - 0.25, 0, 0)))
    b = b.cut(cq.Workplane("XY").center(X_AFT - 0.25, 0).circle(0.094).extrude(1))
    # front face: 2x #10-32 tapped (z = +-0.42), 2x 1/8 dowels (z = +-0.17)
    for z, d, dep in ((0.42, 0.159, 0.5), (-0.42, 0.159, 0.5), (0.17, 0.125, 0.3), (-0.17, 0.125, 0.3)):
        b = b.cut(cq.Workplane("YZ").center(0, z).circle(d / 2).extrude(dep).translate((X_FRONT, 0, 0)))
    return b


def make_puck():
    x0 = X_FRONT - PUCK_T
    p = cq.Workplane("YZ").circle(PUCK_D / 2).extrude(PUCK_T).translate((x0, 0, 0))
    p = p.union(cq.Workplane("YZ").circle(0.25).extrude(0.10).translate((x0 - 0.10, 0, 0)))
    for z in (0.42, -0.42):
        p = p.cut(cq.Workplane("YZ").center(0, z).circle(0.098).extrude(1).translate((x0 - 0.5, 0, 0)))
        p = p.cut(cq.Workplane("YZ").center(0, z).circle(0.16).extrude(0.20).translate((x0 - 0.10, 0, 0)))
    for z in (0.17, -0.17):
        p = p.cut(cq.Workplane("YZ").center(0, z).circle(0.0625).extrude(1).translate((x0 - 0.5, 0, 0)))
    xm = x0 + PUCK_T / 2
    for ang in (45, 135, 225, 315):
        p = p.cut(cq.Workplane("XY").circle(0.068).extrude(0.35).translate((0, 0, PUCK_D / 2 - 0.35))
                  .rotate((0, 0, 0), (1, 0, 0), ang).translate((xm, 0, 0)))
    return p.cut(cq.Workplane("YZ").center(0.60, 0).circle(0.094).extrude(1).translate((x0 - 0.5, 0, 0)))


def make_sting():
    x0 = X_AFT
    s = cq.Workplane("YZ").circle(STING_D / 2).extrude(STING_L).translate((x0, 0, 0))
    s = s.cut(cq.Workplane("YZ").circle(0.3755).extrude(SPIG_L + 0.05).translate((x0, 0, 0)))
    s = s.cut(cq.Workplane("YZ").circle(0.15).extrude(STING_L).translate((x0, 0, 0)))
    s = s.cut(cq.Workplane("XZ").center(PIN_X, 0).circle(0.09375).extrude(1, both=True))
    for xs in (x0 + 0.40, x0 + 1.10):
        s = s.cut(cq.Workplane("XY").center(xs, 0).circle(0.1065).extrude(1))
    xc = x0 + STING_L - 3.0
    s = s.cut(box(xc, xc + 3.1, -1, 1, 0.35, 1)).cut(box(xc, xc + 3.1, -1, 1, -1, -0.35))
    for xh in (xc + 0.75, xc + 2.25):
        s = s.cut(cq.Workplane("XY").center(xh, 0).circle(0.1405).extrude(1, both=True))
    return s


def pod_geom():
    x_puck0 = X_FRONT - PUCK_T
    return dict(nose_tip=x_puck0 - 2.2, cyl0=x_puck0 - 0.2, cyl1=X_AFT + 0.05, base=X_AFT + 1.80,
                r=POD_D / 2, rb=POD_BASE_D / 2, bore_r=POD_BORE_R, sting_clear=STING_D / 2 + 0.10,
                x_cav=x_puck0 - 0.12, x_screw=x_puck0 + PUCK_T / 2, r_bay=0.70)


def make_pod():
    g = pod_geom()
    pts = [(g["nose_tip"], 0)]
    for i in range(1, 13):
        f = i / 12
        pts.append((g["nose_tip"] + f * (g["cyl0"] - g["nose_tip"]), g["r"] * math.sqrt(1 - (1 - f) ** 2)))
    pts += [(g["cyl1"], g["r"]), (g["base"], g["rb"]), (g["base"], 0)]
    outer = cq.Workplane("XY").polyline(pts).close().revolve(360, (0, 0, 0), (1, 0, 0))
    inner = (cq.Workplane("XY").polyline([(g["x_cav"], 0), (g["x_cav"], g["bore_r"]), (g["cyl1"], g["bore_r"]),
                                          (g["base"] + 0.01, g["sting_clear"]), (g["base"] + 0.01, 0)])
             .close().revolve(360, (0, 0, 0), (1, 0, 0)))
    pod = outer.cut(inner)
    for ang in (45, 135, 225, 315):
        pod = pod.cut(cq.Workplane("XY").circle(0.09).extrude(0.5).translate((0, 0, g["r"] - 0.45))
                      .rotate((0, 0, 0), (1, 0, 0), ang).translate((g["x_screw"], 0, 0)))
    pod, make_pod.report = PI.instrument_pod(pod, g)
    return pod


def nsol(wp):
    return len(wp.solids().vals())


if __name__ == "__main__":
    bal = make_balance()
    print(f"balance: {nsol(bal)} solid (expect 1); plates removed -> {nsol(make_balance(False))} (expect 2); "
          f"length {X_AFT - X_FRONT:.2f} in + {SPIG_L} in spigot; volume {bal.val().Volume():.3f} in^3 "
          f"({bal.val().Volume()*0.101:.2f} lb)")
    print(f"necks {NB:.3f} W x {NH:.3f} H x {LN} L at x = +-{XS}; front face x = {X_FRONT}, aft block end x = {X_AFT}; "
          f"sting {STING_L:.2f} in")
    parts = {"balance_6c_7075": bal, "model_puck_6061": make_puck(), "sting_4140": make_sting(),
             "pod_reference_2.25in_printed": make_pod()}
    PI.print_report(make_pod.report, "6-component pod")
    for n, wp in parts.items():
        cq.exporters.export(cq.Workplane().add(wp.val().scale(IN)), str(HERE / f"{n}.step"))
        print(f"  {n}.step ({nsol(wp)} solid)")
    names = list(parts)
    worst = 0.0
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            v = parts[names[i]].val().intersect(parts[names[j]].val()).Volume()
            if v > 1e-6:
                print(f"  overlap {names[i]} x {names[j]}: {v:.5f}")
            worst = max(worst, v)
    print(f"assembly max interference {worst:.5f} in^3")
    col = {"balance_6c_7075": (0.75, 0.75, 0.8), "model_puck_6061": (0.55, 0.6, 0.9), "sting_4140": (0.35, 0.35, 0.35),
           "pod_reference_2.25in_printed": (0.2, 0.7, 0.4, 0.35)}
    asm = cq.Assembly(name="six_component_balance_flight")
    for n, wp in parts.items():
        asm.add(cq.Workplane().add(wp.val().scale(IN)), name=n, color=cq.Color(*col[n]))
    asm.export(str(HERE / "assembly_6c_flight.step"))
    print("  assembly_6c_flight.step")
