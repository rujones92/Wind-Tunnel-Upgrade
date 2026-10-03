"""
Pressure instrumentation for the reference pods (shared by the aluminum and printed balance builds).

Adds to a revolved pod (axis = x, nose forward at -x, base aft at +x):
  - BASE TAPS: 4x 1/16 in taps in the base annulus at 30/150/210/330 deg (theta measured from +z toward +y),
    clear of the 45 deg pod screws and of the wing roots at +-90 deg.
  - Each tap feeds a printed internal channel along the boattail mid-wall, then forward along the cylinder mid-wall
    into the solid nose, where a MANIFOLD RING averages the four taps (pneumatic averaging) and one port exits into
    the sensor bay -> one sensor reads mean base pressure.
  - CAVITY TAP: radial hole from the pod bore near the aft fitting at 0 deg (top), own channel forward to the bay.
  - SENSOR BAY: cylindrical pocket in the solid nose, opening aft into the space in front of the puck.
    Holds the base and cavity barometric sensors (e.g. BMP390 breakouts, 25 x 18 mm) and the alpha accelerometer.
Print the pod standing on its base (nose up) so the channels print as vertical round holes.
Units: inch.
"""
import math
import cadquery as cq

CH_D = 0.060            # channel / tap diameter (1.5 mm)
RING_R = 0.030          # manifold ring tube radius
PORT_CB_D, PORT_CB_L = 0.075, 0.15   # counterbore at each bay port for a 1/16 in OD tube stub
BASE_ANGLES = (30, 150, 210, 330)
CAV_ANGLE = 0
RING_EXIT_ANGLE = 90


def _pt(x, r, th):
    t = math.radians(th)
    return cq.Vector(x, r * math.sin(t), r * math.cos(t))


def _seg(p0, p1, d=CH_D):
    v = p1 - p0
    return cq.Solid.makeCylinder(d / 2, v.Length, p0, v.normalized())


def _x_at_nose_radius(R, g):
    """x on the ogive nose where the outer radius equals R."""
    f = 1 - math.sqrt(max(0.0, 1 - (R / g["r"]) ** 2))
    return g["nose_tip"] + f * (g["cyl0"] - g["nose_tip"])


def layout(g):
    """g: nose_tip, cyl0, cyl1, base, r, rb, bore_r, sting_clear, x_cav (front of pod bore), x_screw, r_bay."""
    r_ch = (g["r"] + g["bore_r"]) / 2                       # cylinder mid-wall
    r_tap = (g["rb"] + g["sting_clear"]) / 2                # base-annulus mid-wall (= boattail mid-line at base)
    x_nose_lim = _x_at_nose_radius(r_ch + RING_R + 0.07, g)  # channels must stay aft of this in the nose
    x_ring = x_nose_lim + 0.12
    x_cav_exit = (x_ring + g["x_cav"]) / 2
    x_bay_fwd = _x_at_nose_radius(g["r_bay"] + 0.15, g) + 0.05
    return dict(r_ch=r_ch, r_tap=r_tap, x_ring=x_ring, x_cav_exit=x_cav_exit, x_bay_fwd=x_bay_fwd)


def networks(g):
    """Return (base_network, cavity_network) as solids (the air passages)."""
    L = layout(g)
    r_ch, r_tap, x_ring = L["r_ch"], L["r_tap"], L["x_ring"]
    base_net = []
    for th in BASE_ANGLES:
        base_net.append(_seg(_pt(g["base"] + 0.02, r_tap, th), _pt(g["base"] - 0.25, r_tap, th)))     # tap
        base_net.append(_seg(_pt(g["base"] - 0.25, r_tap, th), _pt(g["cyl1"], r_ch, th)))            # boattail
        base_net.append(_seg(_pt(g["cyl1"] + 0.03, r_ch, th), _pt(x_ring, r_ch, th)))               # cylinder + nose
    base_net.append(cq.Solid.makeTorus(r_ch, RING_R, cq.Vector(x_ring, 0, 0), cq.Vector(1, 0, 0)))
    base_net.append(_seg(_pt(x_ring, r_ch, RING_EXIT_ANGLE), _pt(x_ring, g["r_bay"] - 0.05, RING_EXIT_ANGLE)))
    base_net.append(_seg(_pt(x_ring, g["r_bay"] + PORT_CB_L, RING_EXIT_ANGLE),
                         _pt(x_ring, g["r_bay"] - 0.05, RING_EXIT_ANGLE), PORT_CB_D))
    x_ct = g["cyl1"] - 0.40
    cav_net = [
        _seg(_pt(x_ct, g["bore_r"] - 0.05, CAV_ANGLE), _pt(x_ct, r_ch, CAV_ANGLE)),                 # cavity tap
        _seg(_pt(x_ct + 0.03, r_ch, CAV_ANGLE), _pt(L["x_cav_exit"], r_ch, CAV_ANGLE)),
        _seg(_pt(L["x_cav_exit"], r_ch + 0.03, CAV_ANGLE), _pt(L["x_cav_exit"], g["r_bay"] - 0.05, CAV_ANGLE)),
        _seg(_pt(L["x_cav_exit"], g["r_bay"] + PORT_CB_L, CAV_ANGLE),
             _pt(L["x_cav_exit"], g["r_bay"] - 0.05, CAV_ANGLE), PORT_CB_D),
    ]

    def fuse(lst):
        s = lst[0]
        for o in lst[1:]:
            s = s.fuse(o)
        return s.clean()
    return fuse(base_net), fuse(cav_net)


def bay(g):
    L = layout(g)
    return cq.Solid.makeCylinder(g["r_bay"], g["x_cav"] - L["x_bay_fwd"] + 0.02,
                                 cq.Vector(L["x_bay_fwd"], 0, 0), cq.Vector(1, 0, 0))


def instrument_pod(pod_wp, g):
    """Cut bay + both air networks into a pod Workplane; returns (pod, report dict)."""
    base_net, cav_net = networks(g)
    bay_s = bay(g)
    pod = pod_wp.val()
    solid_pod_volume = pod.Volume()
    # how much of each network lies outside the pod material before cutting (should be only the open ends)
    rep = {}
    for name, net in (("base", base_net), ("cavity", cav_net)):
        inside = net.intersect(pod).Volume()
        rep[name] = dict(volume=net.Volume(), outside_pct=100 * (1 - inside / net.Volume()),
                         pieces=len(net.Solids()))
    rep["bay_vs_networks"] = bay_s.intersect(base_net.fuse(cav_net)).Volume()
    rep["base_vs_cavity_network"] = base_net.intersect(cav_net).Volume()
    out = pod.cut(bay_s).cut(base_net).cut(cav_net)
    rep["pod_solids"] = len(out.Solids())
    rep["removed"] = solid_pod_volume - out.Volume()
    L = layout(g)
    rep.update({k: round(v, 3) for k, v in L.items()})
    rep["base_area_in2"] = math.pi * (g["rb"] ** 2 - g["sting_clear"] ** 2)
    return cq.Workplane().add(out), rep


def print_report(rep, label):
    print(f"POD INSTRUMENTATION ({label})")
    for n in ("base", "cavity"):
        r = rep[n]
        print(f"  {n:6s} network: {r['pieces']} connected piece(s), {r['outside_pct']:.1f}% of passage volume "
              f"outside the pod wall (open ends only)")
    print(f"  base network x cavity network overlap {rep['base_vs_cavity_network']:.6f} in^3 (must be 0: separate pressures)")
    print(f"  pod still {rep['pod_solids']} solid ; channel mid-wall radius {rep['r_ch']} in, tap radius {rep['r_tap']} in, "
          f"manifold ring x = {rep['x_ring']}, bay x = {rep['x_bay_fwd']}..front of bore")
    print(f"  base annulus area {rep['base_area_in2']:.2f} in^2 (for the base-pressure drag correction)")
