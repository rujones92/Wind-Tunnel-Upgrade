"""
Six-component aluminum sting balance - first-pass sizing (supersedes the 3-component aluminum_balance_sizing.py).

Same concept: one-piece 7075-T651, FWD neck -> axial 2-plate Z-flexure -> AFT neck. Changes for yaw/roll testing:
  - Necks become TALL and NARROW (h > b) so pitch AND yaw bending both give useful strain:
        pitch plane:  N, m  from top/bottom-face bridges at both necks (two-moment, as before)
        yaw plane:    Y, n  from side-face bridges at both necks (two-moment in the yaw plane)
        roll:         l     from a +-45 deg shear (chevron) bridge on the FWD neck side faces, at mid-height
  - Necks lengthened to 0.90 in so each side face carries a tandem pair of yaw gauges plus a chevron between them;
    neck spacing 2.70 in (necks at +-1.35 in).
  - Axial flexure unchanged (plates 0.025 in), re-checked for side force, yawing and rolling moment.
Full-scale loads at 100 mph; side-load values are the agreed defaults.  Units: inch, lbf, psi.
"""
import math

E, G, SY = 10.4e6, 3.9e6, 73e3        # 7075-T651
GF = 2.0
EPS_T = 500e-6                         # target full-scale strain -> ~1 mV/V

# full scale
N_FS, A_FS, M_FS = 25.0, 4.0, 15.0     # lift, drag, pitching moment
Y_FS, NY_FS, L_FS = 8.0, 10.0, 30.0    # side force, yawing moment, rolling moment

S = 2.70                               # neck spacing
a = S / 2
L_NECK = 0.90
R_FIL = 0.06
BAR_W, BAR_H = 0.75, 1.25


def roark_alpha(r):
    """Torsion max-shear coefficient for a b x h rectangle, h/b = r (Roark): tau = T / (alpha h b^2)."""
    tab = [(1.0, 0.208), (1.5, 0.231), (2.0, 0.246), (2.5, 0.258), (3.0, 0.267), (4.0, 0.282)]
    for (r0, a0), (r1, a1) in zip(tab, tab[1:]):
        if r0 <= r <= r1:
            return a0 + (a1 - a0) * (r - r0) / (r1 - r0)
    return tab[-1][1]


def roark_beta(r):
    """Torsion stiffness coefficient: J = beta h b^3."""
    tab = [(1.0, 0.141), (1.5, 0.196), (2.0, 0.229), (2.5, 0.249), (3.0, 0.263), (4.0, 0.281)]
    for (r0, b0), (r1, b1) in zip(tab, tab[1:]):
        if r0 <= r <= r1:
            return b0 + (b1 - b0) * (r - r0) / (r1 - r0)
    return tab[-1][1]


def size_neck():
    Mp = M_FS + a * N_FS               # worst pitch-plane neck moment
    My = NY_FS + a * Y_FS              # worst yaw-plane neck moment
    sig = EPS_T * E
    r = Mp / My                        # h/b that equalises pitch and yaw strain
    b = (6 * My / (sig * r)) ** (1 / 3)   # from h b^2/6 = My/sig with h = r b
    h = r * b
    return Mp, My, math.ceil(b * 200) / 200, math.ceil(h * 200) / 200


if __name__ == "__main__":
    Mp, My, b, h = size_neck()
    Zp, Zy = b * h**2 / 6, h * b**2 / 6
    sp, sy = Mp / Zp, My / Zy
    r = h / b
    al, be = roark_alpha(r), roark_beta(r)
    tau = L_FS / (al * h * b**2)
    gam = tau / G
    print("SIX-COMPONENT ALUMINUM BALANCE - NECKS")
    print(f"  neck spacing {S} in (stations at +-{a}), length {L_NECK} in, section {b:.3f} W (y) x {h:.3f} H (z), "
          f"h/b = {r:.2f}")
    print(f"  pitch plane : worst moment m + {a}N = {Mp:.1f} in-lbf -> {sp:,.0f} psi, {sp/E*1e6:.0f} ue, "
          f"{GF*sp/E*1e3:.2f} mV/V")
    print(f"  yaw plane   : worst moment n + {a}Y = {My:.1f} in-lbf -> {sy:,.0f} psi, {sy/E*1e6:.0f} ue, "
          f"{GF*sy/E*1e3:.2f} mV/V")
    print(f"  roll        : {L_FS} in-lbf -> max shear {tau:,.0f} psi at side-face mid-height, shear strain "
          f"{gam*1e6:.0f} ue -> chevron bridge {GF*gam/2*1e3:.2f} mV/V")
    vm_corner = sp + sy
    vm_side = math.sqrt(sy**2 + 3 * tau**2)
    vm = max(vm_corner, vm_side)
    print(f"  combined: corner {vm_corner:,.0f} psi, side mid-face von Mises {vm_side:,.0f} psi -> SF(yield) {SY/vm:.1f}")
    EIp, EIy = E * b * h**3 / 12, E * h * b**3 / 12
    GJ = G * be * h * b**3
    th_p = (Mp + abs(M_FS - a * N_FS)) * L_NECK / EIp
    th_y = (My + abs(NY_FS - a * Y_FS)) * L_NECK / EIy
    th_r = 2 * L_NECK * L_FS / GJ
    print(f"  model deflection at FS: pitch {math.degrees(th_p):.2f} deg, yaw {math.degrees(th_y):.2f} deg, "
          f"roll {math.degrees(th_r):.2f} deg (pod IMU measures true attitude)")
    usable = L_NECK - 2 * R_FIL
    print(f"  gauge space: side faces {h:.3f} tall x {usable:.2f} long -> yaw tandem pair at x_c +-0.26 + chevron at x_c ;"
          f" top/bottom faces {b:.3f} wide -> pitch tandem pair at x_c +-0.15 (use 0.031-0.062 in narrow-pattern gauges)")

    # axial flexure re-check with the new lateral loads
    t, w, Lp, e = 0.025, 0.75, 0.75, 0.75
    Zin = t * w**2 / 6
    s_roll = (L_FS / 2) / Zin
    s_drag_root = 6 * ((A_FS / 2) * Lp / 2) / (w * t**2)
    s_yaw = (NY_FS / e) / (w * t) * 1.5        # in-plane shear from yawing moment (parabolic peak)
    print("\nAXIAL FLEXURE (plates 0.025 x 0.75 x 0.75, spacing 0.75) - lateral load check")
    print(f"  roll {L_FS} in-lbf -> plate in-plane edge bending {s_roll:,.0f} psi ; drag root bending {s_drag_root:,.0f} psi ; "
          f"yaw in-plane shear {s_yaw:,.0f} psi")
    print(f"  worst combined edge stress {s_roll + s_drag_root:,.0f} psi -> SF {SY/(s_roll + s_drag_root):.1f} ; "
          "edge strains cancel in the centred drag gauges (calibrate the residual)")

    print("\nGAUGES / BRIDGES (24 grids, 6 bridges, 6 ADC channels)")
    for nm, txt in (("N, m (x2)", "top + bottom faces, tandem pairs, both necks -> 2 pitch bridges (two-moment)"),
                    ("Y, n (x2)", "side faces at z = 0 (pitch-neutral), tandem pairs, both necks -> 2 yaw bridges"),
                    ("l", "2 chevron (+-45 deg) gauges, fwd-neck side faces at z = 0 -> 1 shear bridge"),
                    ("A", "4 gauges on the axial plates (unchanged)")):
        print(f"  {nm:10s}: {txt}")
    print(f"\nENVELOPE: necks at +-{a} in -> balance ~{2*(a + L_NECK/2 + 0.75):.1f} in long + spigot "
          f"(was 4.5 in); pod lengthens ~0.6 in")
