"""
Drive sizing for the motorized sting: pitch arc sector, roll spindle, yaw carriage (option B, +-15 deg).
All three use a self-locking worm gearbox so the steppers can be DISABLED while data are taken
(no stepper electrical noise near the strain-gauge signals, no vibration, no motor heat).
Units: inch, lbf, in-lbf, deg.

Updated 2026-10-03 to the as-designed drives (CAD + electronics page):
  pitch: 40:1 worm -> 20-tooth module 1.25 pinion (pitch radius 0.492 in) on the R22.0 in internal arc rack
         (the rack adds R_RACK / r_pinion = 44.7x to the worm ratio); max rate 2 deg/s
  yaw:   30:1 worm -> 20-tooth m1.25 pinion on the R19.6 in floor rack (39.8x); rails R14.4 / R21.6; 3 deg/s
  roll:  NMRV030 50:1 directly on the spindle; 18 deg/s
  drivers at 1/8 step (1600 microsteps / rev)
"""
import math

NM_PER_INLBF = 0.112985
# ---------------- full-scale aero loads (100 mph) ----------------
N, A, M = 25.0, 4.0, 15.0
Y, NYAW, L = 8.0, 10.0, 30.0
# ---------------- weights (lb) and CG x from the BMC (in) ----------------
W_MODEL, X_MODEL = 1.0, 0.0
W_STING, X_STING = 2.5, 11.0
W_SPINDLE, X_SPINDLE = 11.0, 20.5          # housing, bearings, NMRV030, NEMA 23, encoder (as in the pitch-sector CAD)
W_SECTOR = 12.0                             # braced sector frame
W_CARRIAGE = 10.0
R_PINION = 20 * 1.25 / 25.4 / 2             # 0.492 in pitch radius (module 1.25, 20 teeth)
R_RACK_PITCH = 22.0                         # pitch internal arc rack, radius about the BMC
R_RACK_YAW = 19.6                           # yaw floor rack
R_RAIL_IN, R_RAIL_OUT = 14.4, 21.6          # yaw rails, radii about the vertical axis through the BMC
H_AXIS = 11.35                              # BMC height above the duct floor (assumed - to confirm)
WORM_EFF = 0.35                             # single-start worm, self-locking (efficiency < 0.5)
MICROSTEPS = 1600                           # 1/8 step
MOTORS = {"NEMA 17 (0.45 N-m)": 0.45, "NEMA 23 (1.2 N-m)": 1.2}
RATES = {"pitch": 2.0, "yaw": 3.0, "roll": 18.0}   # deg/s


def motor_check(name, load_inlbf, worm, out_speed_dps, rack_ratio=1.0):
    """load at the worm output shaft (in-lbf); rack_ratio = rack radius / pinion radius (1 = direct drive)."""
    t_motor = load_inlbf / (worm * WORM_EFF) * NM_PER_INLBF
    total = worm * rack_ratio
    rpm = out_speed_dps * total / 6.0
    steps_deg = MICROSTEPS * total / 360
    usable = {k: v * 0.5 for k, v in MOTORS.items()}      # ~50% of holding torque available at speed
    pick = next((k for k, v in usable.items() if v >= 2.5 * t_motor), "larger motor")
    print(f"  {name}: {load_inlbf:.1f} in-lbf at the worm output, {worm}:1 worm x {rack_ratio:.1f} rack = {total:.0f}:1 "
          f"-> motor {t_motor * 1000:.0f} mN-m at {rpm:.0f} rpm ({out_speed_dps} deg/s); {steps_deg:.0f} steps/deg = "
          f"{1 / steps_deg:.6f} deg per microstep, {steps_deg * out_speed_dps / 1000:.1f} kHz; choose {pick}")
    return pick


if __name__ == "__main__":
    print(f"PITCH - arc sector about the BMC, internal rack R{R_RACK_PITCH} in, pinion r {R_PINION:.3f} in")
    m_grav = W_STING * X_STING + W_SPINDLE * X_SPINDLE
    m_tot = m_grav + M
    f_rack = m_tot / R_RACK_PITCH
    f_fric = 0.005 * 4 * 200                               # 4 cam followers, ~200 lbf each, rolling friction
    print(f"  gravity moment about BMC {m_grav:.0f} in-lbf (always the same sign -> preloads the gear mesh, "
          f"no backlash crossing) + aero m {M:.0f}")
    print(f"  rack force {f_rack:.1f} + follower friction {f_fric:.1f} lbf -> pinion torque "
          f"{R_PINION * (f_rack + f_fric):.1f} in-lbf")
    motor_check("pitch", R_PINION * (f_rack + f_fric), 40, RATES["pitch"], R_RACK_PITCH / R_PINION)

    print("\nROLL - spindle at the sting root (sting in a D-D bore, rotates in 2 x 6907 bearings)")
    t_roll = L + 2.0 + 3.0                                  # aero + wire loop + bearing friction
    print(f"  torque {t_roll:.0f} in-lbf (aero {L:.0f} + wire loop 2 + bearings 3); +-90 deg in 10 s = 18 deg/s")
    motor_check("roll", t_roll, 50, RATES["roll"])
    m_root = N * X_SPINDLE
    span = 3.0
    print(f"  bearing span {span} in: radial loads ~{m_root / span:.0f} lbf (lift) + weights -> 6907-2RS pair OK")
    print("  roll aero moment changes sign -> approach targets from one side; absolute AS5048A encoder on the spindle")

    print(f"\nYAW - carriage on two concentric curved floor rails, R{R_RAIL_IN} / R{R_RAIL_OUT} in about the BMC")
    w_all = W_MODEL + W_STING + W_SPINDLE + W_SECTOR + W_CARRIAGE
    pitch_couple = (N * 18.5 + m_grav) / (R_RAIL_OUT - R_RAIL_IN)
    roll_couple = (Y * H_AXIS + L) / 6.0                    # carriage wheel track ~6 in
    wheel = w_all / 4 + pitch_couple / 2 + roll_couple / 2
    print(f"  moving weight {w_all:.0f} lb ; pitch-plane couple between rails {pitch_couple:.0f} lbf ; "
          f"roll couple {roll_couple:.0f} lbf ; worst wheel load ~{wheel:.0f} lbf (captive V-wheels take uplift)")
    t_yaw = NYAW + 0.01 * 4 * wheel * 18.5                  # aero yawing moment + rolling resistance
    print(f"  yaw torque about the BMC axis {t_yaw:.0f} in-lbf -> rack force {t_yaw / R_RACK_YAW:.1f} lbf")
    motor_check("yaw", R_PINION * t_yaw / R_RACK_YAW, 30, RATES["yaw"], R_RACK_YAW / R_PINION)
