r"""
Electronics diagrams for the motorized 6-component sting balance.

Writes SVG (text converted to paths: no font dependency, white card background so it reads on light and dark pages)
and a PNG copy of each diagram into this folder:
  block          system block diagram (station, rig box, moving rig, balance + model)
  power_safety   power distribution, E-stop / safety chain, star ground
  steppers       Arduino Uno + CNC shield v3 (grbl 1.1) pins, drivers, motors, limit switches
  bridge         one strain-gauge bridge in detail + the 6-bridge harness to the ADCs
  pinmap         Raspberry Pi 4 header assignments, I2C address map, Pico sensor-node pins
  harness_route  balance cable route through balance, sting and spindle, with bore fill
Run:  ..\..\.venv\Scripts\python make_electronics_diagrams.py
"""
import math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon, Arc

plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "path", "svg.hashsalt": "wt-electronics"})
OUT = Path(__file__).resolve().parent

C = dict(power="#c0392b", motor="#d35400", analog="#1f5fbf", digital="#1e8449", safety="#8e44ad",
         shield="#7f8c8d", gnd="#2c3e50", ac="#5d4037", ink="#1d2430", sub="#4a5566", fill="#f5f7fb",
         hi="#e9f1fd", zone="#fcfcfe", warn="#b9770e", grey="#9aa3ae")


class D:
    def __init__(self, W, H, title, subtitle=""):
        self.W, self.H = W, H
        self.fig = plt.figure(figsize=(W, H), facecolor="white")
        ax = self.fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off"); ax.set_facecolor("white")
        self.ax = ax
        ax.text(0.35, H - 0.32, title, fontsize=17, weight="bold", color=C["ink"], va="center")
        if subtitle:
            ax.text(0.35, H - 0.68, subtitle, fontsize=10.5, color=C["sub"], va="center")

    # ---------------------------------------------------------------- primitives
    def text(self, x, y, s, size=9, color=None, ha="left", va="center", weight="normal", rot=0, bg=None, z=6):
        kw = {}
        if bg:
            kw["bbox"] = dict(boxstyle="round,pad=0.18", fc=bg, ec="none")
        return self.ax.text(x, y, s, fontsize=size, color=color or C["ink"], ha=ha, va=va, weight=weight,
                            rotation=rot, zorder=z, linespacing=1.3, **kw)

    def box(self, x, y, w, h, title, lines=(), fc=None, ec=None, ts=11, ls=8.6, tc=None, lw=1.3, dy=0.27):
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.08",
                                         fc=fc or C["fill"], ec=ec or C["ink"], lw=lw, zorder=2))
        ty = y + h - 0.24
        if title:
            self.text(x + 0.12, ty, title, size=ts, weight="bold", color=tc, va="center", z=4)
        for i, t in enumerate(lines):
            self.text(x + 0.12, ty - 0.30 - i * dy, t, size=ls, color=C["sub"], z=4)

    def zone(self, x, y, w, h, label, color=None):
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12", fc=C["zone"],
                                         ec=color or C["grey"], lw=1.3, ls=(0, (5, 3)), zorder=1))
        self.text(x + 0.15, y + h - 0.2, label, size=9.5, weight="bold", color=color or C["sub"], z=3)

    def wire(self, pts, color, lw=1.8, ls="-", arrow=False, label=None, at=0.5, lsize=8.2, loff=(0, 0.13),
             lha="center", z=3, both=False):
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=color, lw=lw, ls=ls, zorder=z, solid_capstyle="round")
        if arrow or both:
            self._head(pts[-2], pts[-1], color)
        if both:
            self._head(pts[1], pts[0], color)
        if label:
            # label on the segment holding the 'at' fraction of the length
            seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
            tgt, acc = at * sum(seg), 0
            for i, L in enumerate(seg):
                if acc + L >= tgt:
                    f = (tgt - acc) / L if L else 0
                    x = pts[i][0] + f * (pts[i + 1][0] - pts[i][0])
                    y = pts[i][1] + f * (pts[i + 1][1] - pts[i][1])
                    break
                acc += L
            self.text(x + loff[0], y + loff[1], label, size=lsize, color=color, ha=lha, bg="white", z=5)

    def _head(self, p0, p1, color, L=0.16, Wd=0.07):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        n = math.hypot(dx, dy) or 1
        ux, uy = dx / n, dy / n
        bx, by = p1[0] - ux * L, p1[1] - uy * L
        self.ax.add_patch(Polygon([p1, (bx - uy * Wd, by + ux * Wd), (bx + uy * Wd, by - ux * Wd)], closed=True,
                                  fc=color, ec=color, zorder=4))

    def dot(self, x, y, color, r=0.045):
        self.ax.add_patch(Circle((x, y), r, fc=color, ec=color, zorder=5))

    def term(self, x, y, color=None):
        self.ax.add_patch(Circle((x, y), 0.05, fc="white", ec=color or C["ink"], lw=1.1, zorder=5))

    def resistor(self, p0, p1, label="", color=None, lpos=(0, 0.2), lsize=8.5, n=6, amp=0.07, lead=0.25):
        """Zig-zag resistor between p0 and p1 (straight leads of length `lead` at both ends)."""
        color = color or C["ink"]
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        a = (p0[0] + ux * lead, p0[1] + uy * lead)
        b = (p1[0] - ux * lead, p1[1] - uy * lead)
        seg = (L - 2 * lead) / n
        pts = [p0, a]
        for i in range(n):
            s = (i + 0.5) * seg
            sgn = 1 if i % 2 == 0 else -1
            pts.append((a[0] + ux * s + nx * amp * sgn, a[1] + uy * s + ny * amp * sgn))
        pts += [b, p1]
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=color, lw=1.6, zorder=4)
        if label:
            mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            self.text(mx + lpos[0], my + lpos[1], label, size=lsize, ha="center", color=color, bg="white")

    def nc_switch(self, x, y, label="", color=None, vertical=False, size=0.42, lsize=8):
        """Normally-closed contact drawn horizontally (or vertically) starting at (x, y), length `size`."""
        color = color or C["ink"]
        if not vertical:
            x1 = x + size
            self.ax.plot([x, x + 0.12], [y, y], color=color, lw=1.6, zorder=4)
            self.ax.plot([x1 - 0.12, x1], [y, y], color=color, lw=1.6, zorder=4)
            self.ax.plot([x + 0.12, x1 - 0.05], [y + 0.0, y - 0.06], color=color, lw=1.6, zorder=4)   # closed blade
            self.ax.plot([x1 - 0.12, x1 - 0.12], [y, y - 0.1], color=color, lw=1.6, zorder=4)            # NC stop
            if label:
                self.text(x + size / 2, y + 0.17, label, size=lsize, ha="center", color=color)
            return (x1, y)
        y1 = y - size
        self.ax.plot([x, x], [y, y - 0.12], color=color, lw=1.6, zorder=4)
        self.ax.plot([x, x], [y1 + 0.12, y1], color=color, lw=1.6, zorder=4)
        self.ax.plot([x, x + 0.06], [y - 0.12, y1 + 0.05], color=color, lw=1.6, zorder=4)
        self.ax.plot([x, x + 0.1], [y1 + 0.12, y1 + 0.12], color=color, lw=1.6, zorder=4)
        if label:
            self.text(x + 0.17, y - size / 2, label, size=lsize, color=color)
        return (x, y1)

    def no_button(self, x, y, label="", color=None, size=0.42):
        color = color or C["ink"]
        x1 = x + size
        self.ax.plot([x, x + 0.12], [y, y], color=color, lw=1.6, zorder=4)
        self.ax.plot([x1 - 0.12, x1], [y, y], color=color, lw=1.6, zorder=4)
        self.ax.plot([x + 0.1, x1 - 0.1], [y + 0.1, y + 0.1], color=color, lw=1.6, zorder=4)
        self.ax.plot([x + size / 2, x + size / 2], [y + 0.1, y + 0.2], color=color, lw=1.6, zorder=4)
        if label:
            self.text(x + size / 2, y + 0.33, label, size=8, ha="center", color=color)

    def gnd(self, x, y, color=None):
        color = color or C["gnd"]
        self.ax.plot([x, x], [y, y - 0.12], color=color, lw=1.5, zorder=4)
        for i, w in enumerate((0.16, 0.10, 0.04)):
            self.ax.plot([x - w, x + w], [y - 0.12 - i * 0.05] * 2, color=color, lw=1.5, zorder=4)

    def fuse(self, x, y, label="", color=None, w=0.36):
        color = color or C["power"]
        self.ax.add_patch(Rectangle((x - w / 2, y - 0.07), w, 0.14, fc="white", ec=color, lw=1.3, zorder=5))
        self.ax.plot([x - w / 2, x + w / 2], [y, y], color=color, lw=1.0, zorder=6)
        if label:
            self.text(x, y + 0.2, label, size=7.8, ha="center", color=color, bg="white")

    def legend(self, x, y, items, w=2.7):
        h = 0.32 + 0.27 * len(items)
        self.ax.add_patch(FancyBboxPatch((x, y - h), w, h, boxstyle="round,pad=0,rounding_size=0.06", fc="white",
                                         ec=C["grey"], lw=1.0, zorder=2))
        self.text(x + 0.12, y - 0.18, "Legend", size=9, weight="bold", z=4)
        for i, (lab, col, ls) in enumerate(items):
            yy = y - 0.45 - i * 0.27
            self.ax.plot([x + 0.15, x + 0.65], [yy, yy], color=col, lw=2.2, ls=ls, zorder=4)
            self.text(x + 0.78, yy, lab, size=8.3, z=4)

    def note(self, x, y, s, size=8.4, color=None, w=None):
        self.text(x, y, s, size=size, color=color or C["sub"], va="top")

    def save(self, name):
        self.fig.savefig(OUT / f"{name}.svg", facecolor="white")
        self.fig.savefig(OUT / f"{name}.png", dpi=110, facecolor="white")
        plt.close(self.fig)
        print("wrote", name)


LEG = [("mains AC", C["ac"], "-"), ("DC power", C["power"], "-"), ("motor phases", C["motor"], "-"),
       ("bridge / analog", C["analog"], "-"), ("digital: USB, I2C, SPI, step/dir", C["digital"], "-"),
       ("safety chain", C["safety"], "-"), ("shield / ground", C["shield"], "--")]


# ====================================================================== (a) block diagram
def block():
    d = D(16, 11.0, "System block diagram",
          "Station Pi -> rig Pi -> grbl motion controller + bridge DAQ; motors and sensors on the moving rig; "
          "gauges and pod sensors inside the model")
    # zones
    d.zone(0.3, 5.5, 2.75, 3.75, "CONTROL STATION")
    d.zone(3.35, 0.35, 6.75, 8.9, "RIG BOX  (beside the tunnel, DIN rail, steel enclosure)")
    d.zone(10.4, 3.85, 5.35, 5.4, "MOVING RIG  (yaw carriage > pitch sector > roll spindle)")
    d.zone(10.4, 0.35, 5.35, 3.0, "BALANCE + MODEL  (inside the pod)")
    # station
    d.box(0.5, 7.0, 2.35, 1.75, "Station Pi 4", ["GUI: attitude, sweeps,", "live plots, data reduction,", "reports"],
          fc=C["hi"])
    d.box(0.5, 5.75, 2.35, 0.95, "Station E-stop S2", ["2 NC channels, J7"], ec=C["safety"], tc=C["safety"])
    d.box(0.5, 0.5, 2.35, 1.95, "Tunnel", ["pitot-static probe", "fan drive run contact", "air temperature probe",
                                            "(DS18B20)"])
    d.legend(0.45, 5.15, LEG, w=2.55)
    # rig box - left column
    d.box(3.65, 7.0, 2.85, 1.85, "Rig Pi 4", ["rig service: sequencer,", "envelope interlock, DAQ,",
                                              "zeros & tares, logging,", "watchdog heartbeat"], fc=C["hi"])
    d.box(3.65, 4.95, 2.85, 1.7, "Bridge DAQ", ["6x NAU7802 24-bit, 1 per bridge", "TCA9548A I2C mux (0x70)",
                                                "2x ADS1115: sense, NTC", "LTC4311 pod-bus terminator"])
    d.box(3.65, 3.75, 2.85, 0.95, "Excitation", ["LT3042 low-noise 3.30 V, 60 mA"], ec=C["power"])
    d.box(3.65, 0.9, 2.85, 2.55, "Flow + air", ["pitot dP: Honeywell ABP2,", "0-10 inH2O, I2C 0x28",
                                                "BMP390 ambient (I2C)", "DS18B20 air temp (1-Wire)",
                                                "wind-on input (opto)"])
    # rig box - right column
    d.box(6.95, 7.0, 2.9, 1.85, "Arduino Uno + CNC shield v3", ["grbl 1.1: X yaw, Y pitch, Z roll",
                                                                 "2x TMC2209 (yaw, pitch)",
                                                                 "step/dir/enable -> DM542T"], ts=10.2)
    d.box(6.95, 5.6, 2.9, 1.05, "DM542T roll driver", ["24 V, 2.0 A, 1/8 step"])
    d.box(6.95, 3.9, 2.9, 1.3, "Power", ["PSU1 24 V 150 W -> K1 -> drivers", "PSU2 5 V 35 W (logic)"], ec=C["power"])
    d.box(6.95, 0.9, 2.9, 2.65, "Safety", ["E-stops S1 (rig) + S2 (station)", "+ watchdog relay contact",
                                           "-> safety relay -> K1", "K1 cuts the 24 V motor bus",
                                           "aux contacts -> Pi + grbl A0"], ec=C["safety"], tc=C["safety"])
    # moving rig
    d.box(10.65, 7.05, 2.4, 1.85, "Motors", ["yaw NEMA 17 + 30:1 worm", "pitch NEMA 17 + 40:1 worm",
                                             "roll NEMA 23 + NMRV030 50:1"], ls=8.3)
    d.box(13.2, 7.05, 2.35, 1.85, "Limit / home", ["6 NC switches", "(2 per axis, in series)", "junction box on",
                                                   "the carriage"])
    d.box(10.65, 4.1, 2.4, 2.6, "J0 balance breakout", ["DC-37 on a plastic bracket", "on the roll housing",
                                                        "fed by the 270 deg", "clock-spring loop from", "the spindle wire exit"],
          ls=8.3)
    d.box(13.2, 4.1, 2.35, 2.6, "Sensor node", ["Raspberry Pi Pico (USB)", "3x AS5048A encoders", "SCL3300 inclinometer",
                                                "(all SPI, < 1 m runs)", "on the sector base"], ls=8.3)
    # balance + model
    d.box(10.65, 0.6, 2.4, 2.3, "Balance", ["6 bridges, 24 gauges, 350 ohm", "shared EX bus + remote", "sense, NTC on the",
                                            "aft block"], ls=8.3)
    d.box(13.2, 0.6, 2.35, 2.3, "Pod sensor bay", ["2x BMP390 (base, cavity)", "LSM6DSOX accelerometer", "I2C bus 3, 50 kHz"],
          ls=8.3)
    # links
    g, a, p, m, s = C["digital"], C["analog"], C["power"], C["motor"], C["safety"]
    d.wire([(2.85, 7.9), (3.65, 7.9)], g, both=True, label="Ethernet", loff=(0, 0.16))
    d.wire([(6.5, 7.9), (6.95, 7.9)], g, arrow=True, label="USB", loff=(0, 0.16))
    d.wire([(5.05, 7.0), (5.05, 6.65)], g, both=True, label="I2C-1", loff=(0.35, 0))
    d.wire([(5.05, 4.7), (5.05, 4.95)], p, arrow=True)
    d.wire([(4.6, 8.85), (4.6, 9.85), (15.9, 9.85), (15.9, 5.4), (15.55, 5.4)], g, arrow=True,
           label="USB to the sensor node (high-flex, in the cable chain)", at=0.32)
    d.wire([(14.4, 8.9), (14.4, 9.55), (8.4, 9.55), (8.4, 8.85)], g, arrow=True,
           label="limit switches -> D9 / D10 / D12", at=0.42, loff=(0, 0))
    d.wire([(9.85, 8.3), (10.65, 8.3)], m, arrow=True, label="yaw, pitch", loff=(0, 0.15), lsize=7.8)
    d.wire([(9.85, 6.1), (10.25, 6.1), (10.25, 7.55), (10.65, 7.55)], m, arrow=True, label="roll", at=0.75,
           loff=(-0.22, 0), lsize=7.8)
    d.wire([(10.65, 5.4), (6.5, 5.4)], a, arrow=True, lw=2.2,
           label="12-pair shielded trunk, J0 -> J1", at=0.5, loff=(0, 0.15))
    d.wire([(11.85, 2.9), (11.85, 4.1)], a, arrow=True, lw=2.2)
    d.text(11.75, 3.6, "26 x 32 AWG\nPTFE, sting bore", size=7.4, color=a, ha="right", bg="white")
    d.wire([(13.6, 2.9), (13.6, 3.6), (12.75, 3.6), (12.75, 4.1)], g, arrow=True)
    d.text(13.7, 3.6, "pod I2C (thin loops\nacross the balance)", size=7.6, color=g, bg="white")
    d.wire([(8.4, 3.55), (8.4, 3.9)], s, arrow=True, label="K1", loff=(0.25, 0))
    d.wire([(9.5, 6.65), (9.5, 7.0)], p, arrow=True)
    d.wire([(2.85, 6.2), (3.2, 6.2), (3.2, 0.2), (8.9, 0.2), (8.9, 0.9)], s, arrow=True,
           label="station E-stop loop (J7)", at=0.62, loff=(0, -0.15))
    d.wire([(3.65, 7.4), (3.5, 7.4), (3.5, 0.6), (7.9, 0.6), (7.9, 0.9)], s, arrow=True,
           label="watchdog heartbeat (GPIO22)", at=0.72, loff=(0, 0.15))
    d.wire([(2.85, 1.6), (3.65, 1.6)], a, arrow=True, label="tubes", loff=(0, 0.15))
    d.save("block")


# ====================================================================== (b) power + safety
def power_safety():
    d = D(16, 10.6, "Power distribution, E-stop chain and grounding",
          "Cutting the 24 V motor bus is the safe stop; the self-locking worm gearboxes hold every axis where it is")
    ac, p, s, gr = C["ac"], C["power"], C["safety"], C["shield"]
    # mains
    d.box(0.4, 7.6, 2.4, 1.55, "AC inlet", ["IEC C14, 2 A fuse,", "switch; PE -> chassis"], fc="white", ec=ac, tc=ac)
    d.box(3.4, 8.25, 2.6, 0.9, "PSU1 24 V 150 W", ["Mean Well LRS-150-24"], ec=p)
    d.box(3.4, 6.65, 2.6, 0.9, "PSU2 5 V 35 W", ["Mean Well LRS-35-5"], ec=p)
    d.wire([(2.8, 8.6), (3.1, 8.6), (3.1, 8.7), (3.4, 8.7)], ac, lw=2.2)
    d.wire([(3.1, 8.6), (3.1, 7.1), (3.4, 7.1)], ac, lw=2.2)
    d.text(3.18, 7.85, "L, N", size=8, color=ac)
    # 24 V
    d.wire([(6.0, 8.7), (6.75, 8.7)], p, lw=2.2)
    d.fuse(6.4, 8.7, "F1 8 A")
    d.dot(6.75, 8.7, p)
    # K1 contacts (2 poles drawn as one)
    d.wire([(6.75, 8.7), (7.25, 8.7)], p, lw=2.2)
    d.ax.plot([7.25, 7.75], [8.7, 8.88], color=s, lw=2, zorder=4)
    d.ax.plot([7.75, 7.75], [8.62, 8.78], color=s, lw=1.5, zorder=4)
    d.text(7.5, 9.08, "K1 (NO, 2-pole,\n16 A DC)", size=7.8, color=s, ha="center")
    d.wire([(7.75, 8.7), (8.35, 8.7)], p, lw=2.2)
    d.dot(8.35, 8.7, p)
    d.text(8.22, 8.5, "motor bus", size=7.8, color=p, ha="right")
    d.wire([(8.35, 8.7), (8.35, 9.2), (9.25, 9.2)], p, lw=2.0)
    d.fuse(8.8, 9.2, "F2 5 A")
    d.wire([(8.35, 8.7), (8.35, 8.25), (9.25, 8.25)], p, lw=2.0)
    d.fuse(8.8, 8.25, "F3 4 A")
    d.box(9.25, 8.82, 1.45, 0.78, "DM542T", ["roll driver"], ts=9, ls=7.8, dy=0.2)
    d.box(9.25, 7.87, 1.45, 0.78, "CNC shield", ["2x TMC2209"], ts=9, ls=7.8, dy=0.2)
    # 24 V unswitched control
    d.wire([(6.75, 8.7), (6.75, 7.95), (6.95, 7.95)], p, lw=1.6)
    d.fuse(6.95 + 0.25, 7.95, "F4 1 A", w=0.3)
    d.wire([(7.35, 7.95), (7.6, 7.95)], p, lw=1.6)
    d.text(7.65, 7.95, "24 V control: safety relay,\nK1 coil, box fan, stack light", size=7.8, color=p)
    # 5 V
    d.wire([(6.0, 7.1), (6.6, 7.1)], p, lw=2.0)
    d.dot(6.6, 7.1, p)
    d.wire([(6.6, 7.1), (7.3, 7.1)], p, lw=2.0)
    d.fuse(6.95, 7.1, "F5 3 A", w=0.3)
    d.box(7.3, 6.72, 1.5, 0.78, "Rig Pi 4", ["5.1 V, 3 A"], ts=9, ls=7.8, dy=0.2)
    d.wire([(8.8, 7.1), (9.2, 7.1)], C["digital"], lw=1.6)
    d.text(9.25, 7.1, "USB 5 V -> Uno, Pico,\nsensor node", size=7.8, color=C["digital"])
    d.wire([(6.6, 7.1), (6.6, 5.9), (7.0, 5.9)], p, lw=1.8)
    d.fuse(6.85, 5.9, "F6 0.5 A", w=0.3)
    d.box(7.15, 5.55, 1.35, 0.7, "LC filter", ["10 uH + 100 uF"], ts=8.8, ls=7.6, dy=0.2)
    d.wire([(8.5, 5.9), (8.8, 5.9)], p, lw=1.8)
    d.box(8.8, 5.45, 1.9, 0.9, "LT3042", ["3.30 V low-noise,", "200 mA max"], ts=9, ls=7.6, dy=0.19)
    d.wire([(9.75, 5.45), (9.75, 5.0)], C["analog"], lw=2.0, arrow=True)
    d.text(9.75, 4.82, "EX+ bus: 6 bridges (6 x 9.4 mA)\n+ 6 NAU7802 AVDD  ~ 65 mA", size=7.8, color=C["analog"],
           ha="center", va="top")
    # ground star
    d.zone(0.4, 0.4, 10.3, 4.05, "STAR GROUND (one point, in the rig box)", color=C["gnd"])
    cx, cy = 4.3, 2.2
    d.ax.add_patch(Circle((cx, cy), 0.22, fc="white", ec=C["gnd"], lw=2, zorder=5))
    d.text(cx, cy, "SP", size=9, weight="bold", ha="center", color=C["gnd"], z=6)
    spokes = [("PSU1 0 V", 1.2, 3.6), ("PSU2 0 V", 1.2, 2.95), ("Pi GND", 1.2, 2.3),
              ("NAU7802 + ADS1115 AGND", 1.2, 1.65), ("LT3042 GND (EX- bus)", 1.2, 1.0),
              ("bridge trunk shields\n(box end only)", 7.3, 3.55), ("chassis / PE (one bond)", 7.3, 2.55),
              ("motor cable shields\n-> chassis glands", 7.3, 1.5)]
    for lab, x, y in spokes:
        right = x > cx
        x0 = x - 0.08 if right else x + 0.12 + 0.072 * len(lab)
        d.wire([(x0, y), (cx + (0.22 if right else -0.22), cy)], C["gnd"] if "shield" not in lab else gr, lw=1.4,
               ls="-" if "shield" not in lab else "--")
        d.text(x, y, lab, size=8.2, ha="left", color=C["ink"], bg="white")
    d.note(0.6, 0.85 - 0.1 + 0.0, "", size=8)
    d.text(5.55, 0.58, "Sting, balance body and rig frame are bonded to PE through the steel frame; gauges are insulated "
                     "from the balance (> 10 Gohm at 50 V).", size=7.8, color=C["sub"], ha="center")
    # ------------------------------------------------ safety chain (right)
    d.zone(10.95, 0.4, 4.8, 9.15, "E-STOP / SAFETY CHAIN", color=s)
    x1, x2 = 11.75, 13.0          # channel 1, channel 2
    d.text(11.2, 8.85, "24 V control", size=8.3, color=p)
    d.wire([(11.2, 8.65), (13.55, 8.65)], p, lw=1.6)
    for x in (x1, x2):
        d.wire([(x, 8.65), (x, 8.3)], s, lw=1.6)
    y = 8.3
    for lab in ("S1 rig E-stop", "S2 station E-stop (J7)", "WD watchdog relay"):
        for i, x in enumerate((x1, x2)):
            d.nc_switch(x, y, color=s, vertical=True, size=0.55)
        d.text(x2 + 0.18, y - 0.27, lab, size=8.0, color=s)
        d.wire([(x1, y - 0.55), (x1, y - 0.75)], s, lw=1.6)
        d.wire([(x2, y - 0.55), (x2, y - 0.75)], s, lw=1.6)
        y -= 0.75
    d.box(11.35, 3.75, 3.95, 1.25, "Safety relay", ["Omron G9SE-201 (or PNOZ s3): CH1, CH2,",
                                                     "manual reset S3, outputs 13-14 / 23-24"],
          ec=s, tc=s, ts=9.5, ls=7.8, dy=0.22)
    d.wire([(x1, y), (x1, 5.0)], s, lw=1.6, arrow=True)
    d.wire([(x2, y), (x2, 5.0)], s, lw=1.6, arrow=True)
    d.no_button(13.75, 5.35, "S3 reset", color=s)
    d.wire([(14.17, 5.35), (14.6, 5.35), (14.6, 5.0)], s, lw=1.4)
    d.wire([(13.75, 5.35), (13.45, 5.35), (13.45, 5.0)], s, lw=1.4)
    # K1 coil
    d.wire([(12.4, 3.75), (12.4, 3.25)], s, lw=1.6)
    d.ax.add_patch(Rectangle((12.1, 2.75), 0.6, 0.5, fc="white", ec=s, lw=1.6, zorder=5))
    d.text(12.4, 3.0, "K1", size=9, weight="bold", ha="center", color=s, z=6)
    d.text(12.85, 3.0, "coil 24 V; contacts in the\nmotor bus (left)", size=7.8, color=s)
    d.wire([(12.4, 2.75), (12.4, 2.45)], s, lw=1.6)
    d.gnd(12.4, 2.45)
    # aux signals
    d.text(11.15, 1.75, "Aux contacts / sensing to software:", size=8.3, weight="bold", color=C["ink"])
    for i, t in enumerate(("S1/S2 aux NC -> opto -> Pi GPIO17 (E-STOP OK)",
                           "motor bus after K1 -> opto -> Pi GPIO27",
                           "E-stop aux -> grbl A0 (abort, pull-up)",
                           "Pi GPIO22 10 Hz heartbeat -> WD relay")):
        d.text(11.2, 1.43 - i * 0.26, t, size=7.8, color=C["sub"])
    d.save("power_safety")


# ====================================================================== (c) steppers
def steppers():
    d = D(16, 10.6, "Stepper drivers, motors and limit switches (grbl 1.1 on Arduino Uno + CNC shield v3)",
          "Axes in grbl units of DEGREES: X = yaw, Y = pitch, Z = roll. Drivers are disabled after each move ($1) - "
          "the worm gearboxes hold position while data are taken")
    g, m, p = C["digital"], C["motor"], C["power"]
    ux, uw = 5.7, 3.7
    top = 8.85
    rows = [("D2", "X STEP", "yaw TMC2209"), ("D3", "Y STEP", "pitch TMC2209"), ("D4", "Z STEP", "-> DM542T PUL+"),
            ("D5", "X DIR", "yaw TMC2209"), ("D6", "Y DIR", "pitch TMC2209"), ("D7", "Z DIR", "-> DM542T DIR+"),
            ("D8", "STEPPERS EN", "all; -> DM542T ENA+"), ("D9", "X LIMIT", "yaw switches"),
            ("D10", "Y LIMIT", "pitch switches"), ("D12", "Z LIMIT", "roll switches"),
            ("D11", "spindle PWM", "not used"), ("D13", "spindle dir", "not used"),
            ("A0", "ABORT", "E-stop aux NC"), ("A1", "FEED HOLD", "spare"), ("A2", "CYCLE START", "spare"),
            ("GND", "0 V", "DM542T PUL-/DIR-/ENA-"), ("USB", "serial 115200", "rig Pi")]
    rh = 0.37
    h = rh * len(rows) + 0.5
    d.box(ux, top - h, uw, h, "Arduino Uno + CNC shield v3", [], ts=10.5)
    pin_y = {}
    for i, (pin, fn, to) in enumerate(rows):
        y = top - 0.62 - i * rh
        pin_y[pin] = y
        col = C["grey"] if "not used" in to or to == "spare" else g
        d.ax.add_patch(Rectangle((ux + 0.12, y - 0.13), 0.55, 0.26, fc=col, ec="none", zorder=4))
        d.text(ux + 0.395, y, pin, size=8, ha="center", color="white", weight="bold", z=5)
        d.text(ux + 0.8, y, fn, size=8.3, weight="bold", z=5)
        d.text(ux + 2.05, y, to, size=8, color=C["sub"], z=5)
    # TMC2209 boxes
    d.box(10.55, 7.55, 2.15, 1.3, "TMC2209  X (yaw)", ["shield socket X, 1/8 step", "1.2 A rms (set Vref)"],
          ts=9, ls=7.8, dy=0.21)
    d.box(10.55, 5.95, 2.15, 1.3, "TMC2209  Y (pitch)", ["shield socket Y, 1/8 step", "1.2 A rms (set Vref)"],
          ts=9, ls=7.8, dy=0.21)
    d.box(10.55, 2.3, 2.15, 3.1, "DM542T  Z (roll)", ["external driver, 24 V", "SW: 2.0 A rms, 1600 pulse/rev",
                                                      "opto inputs, common", "cathode (5 V logic)", "",
                                                      "PUL+  <- D4", "DIR+  <- D7", "ENA+  <- D8",
                                                      "PUL-/DIR-/ENA- <- GND"], ts=9, ls=7.8, dy=0.22)
    for pin, ybox in (("D2", 8.35), ("D5", 8.1), ("D3", 6.65), ("D6", 6.4)):
        d.wire([(ux + uw, pin_y[pin]), (10.2, pin_y[pin]), (10.2, ybox), (10.55, ybox)], g, lw=1.2, arrow=True)
    for pin, yb in (("D4", 4.0), ("D7", 3.78), ("D8", 3.56)):
        d.wire([(ux + uw, pin_y[pin]), (9.95 - 0.08 * ("D4", "D7", "D8").index(pin), pin_y[pin]),
                (9.95 - 0.08 * ("D4", "D7", "D8").index(pin), yb), (10.55, yb)], g, lw=1.2, arrow=True)
    d.wire([(ux + uw, pin_y["GND"]), (10.3, pin_y["GND"]), (10.3, 3.34), (10.55, 3.34)], C["gnd"], lw=1.2, arrow=True)
    d.text(10.2, 9.05, "(on the shield: socket traces)", size=7.5, color=C["sub"], ha="center")
    d.wire([(ux + uw, pin_y["D8"]), (9.75, pin_y["D8"]), (9.75, 7.3), (10.55, 7.3)], g, lw=1.0, ls=":")
    # motors
    mot = [("NEMA 17  yaw", "2.0 A, 0.59 N-m class; 30:1 worm", 8.35),
           ("NEMA 17  pitch", "same motor; 40:1 worm, 20T pinion", 6.25),
           ("NEMA 23  roll", "1.2-1.9 N-m, 2.8 A; NMRV030 50:1", 3.6)]
    cols = ("#111111", "#2e7d32", "#c62828", "#1565c0")
    for name, sub, yc in mot:
        d.ax.add_patch(Circle((14.55, yc), 0.42, fc="#e8eaee", ec=C["ink"], lw=1.4, zorder=4))
        d.text(14.55, yc, "M", size=12, weight="bold", ha="center", z=5)
        d.text(13.6, yc + 0.68, name, size=9, weight="bold", ha="left")
        d.text(14.55, yc - 0.55, sub, size=7.3, color=C["sub"], ha="center", va="top")
        for k, c in enumerate(cols):
            yy = yc + 0.24 - k * 0.16
            d.ax.plot([12.7, 14.15], [yy, yy], color=c, lw=1.6, zorder=3)
    d.text(13.4, 9.5, "A+  A-  B+  B-  (colours vary by vendor -\nidentify coil pairs with a meter)", size=7.4,
           color=C["sub"], ha="center")
    d.text(12.78, 5.0, "motor cables: 4-core\nshielded, shield ->\nchassis gland", size=7.3, color=m)
    # 24 V
    d.wire([(11.6, 1.45), (11.6, 2.3)], p, lw=1.8, arrow=True)
    d.text(11.6, 1.25, "24 V motor bus (after K1)\n-> DM542T V+/GND and shield VMOT", size=7.8, color=p, ha="center",
           va="top")
    # limit switches
    d.zone(0.35, 2.15, 4.95, 6.95, "LIMIT / HOME SWITCHES  (NC, wired in series per axis)")
    sw = [("D9", "yaw", "-16 deg (home)", "+16 deg"), ("D10", "pitch", "-7 deg (home)", "+21 deg"),
          ("D12", "roll", "-95 deg (home)", "+185 deg")]
    for i, (pin, ax_, a1, a2) in enumerate(sw):
        y = 8.1 - i * 2.05
        d.text(0.55, y + 0.45, f"{ax_} -> {pin}", size=9, weight="bold")
        d.gnd(0.7, y - 0.02)
        d.wire([(0.7, y - 0.02), (0.7, y), (1.0, y)], C["gnd"], lw=1.4)
        d.nc_switch(1.0, y, a1, color=C["ink"], size=0.5, lsize=7.8)
        d.wire([(1.5, y), (2.45, y)], C["ink"], lw=1.4)
        d.nc_switch(2.45, y, a2, color=C["ink"], size=0.5, lsize=7.8)
        d.wire([(2.95, y), (3.55, y)], g, lw=1.4)
        d.ax.add_patch(Rectangle((3.55, y - 0.16), 0.5, 0.32, fc="white", ec=C["sub"], lw=1, zorder=5))
        d.text(3.8, y, "RC", size=7.5, ha="center", z=6)
        d.wire([(4.05, y), (ux, y), (ux, pin_y[pin]), (ux + 0.12, pin_y[pin])], g, lw=1.4, arrow=True)
    d.text(0.55, 2.8, "RC = 1 k + 100 nF at the Uno pin (internal pull-up);\nshielded 8-core cable J5, shield to chassis "
                      "at the box.\nAn open circuit or broken wire reads as 'limit hit'.", size=7.8, color=C["sub"],
           va="center")
    # grbl settings
    d.box(0.35, 0.3, 9.1, 1.65, "Key grbl settings (degrees)", [
        "$100 = 5310 (yaw)   $101 = 7947 (pitch)   $102 = 222.2 (roll)   steps/deg at 1/8 step",
        "$110 = 180   $111 = 120   $112 = 1080   deg/min  (3, 2, 18 deg/s -> 15.9, 15.9, 4.0 kHz; grbl max ~30 kHz)",
        "$5 = 1 (invert: NC switches)   $21 = 1 hard limits   $22 = 1 homing   $20 = 1 soft limits   $1 = 25 ms idle -> disable",
        "compile with STEP_PULSE_DELAY 10 (DM542T needs 5 us DIR set-up)   $0 = 10 us pulse"], ts=9.5, ls=7.9, dy=0.27,
          fc="white")
    d.save("steppers")


# ====================================================================== (d) bridge wiring
def bridge():
    d = D(16, 10.6, "Strain-gauge bridge wiring",
          "Shared 3.30 V excitation bus with remote sense; one 24-bit NAU7802 per bridge (simultaneous, ratiometric)")
    a, p, gr = C["analog"], C["power"], C["shield"]
    # ---------------- one bridge in detail (left)
    d.zone(0.35, 3.25, 7.6, 6.0, "ONE BRIDGE IN DETAIL  (M1, forward pitch neck)")
    T, B, L_, R_ = (2.2, 8.15), (2.2, 4.25), (0.95, 6.2), (3.45, 6.2)
    d.resistor(T, R_, "T1 top (+)", color=C["ink"], lpos=(0.5, 0.25))
    d.resistor(R_, B, "B1 bottom (-)", color=C["ink"], lpos=(0.6, -0.2))
    d.resistor(T, L_, "B2 bottom (-)", color=C["ink"], lpos=(-0.55, 0.25))
    d.resistor(L_, B, "T2 top (+)", color=C["ink"], lpos=(-0.5, -0.2))
    for q in (T, B, L_, R_):
        d.dot(*q, C["ink"])
    d.text(2.2, 8.4, "EX+", size=9, weight="bold", ha="center", color=p)
    d.text(2.2, 3.98, "EX-", size=9, weight="bold", ha="center", color=C["gnd"])
    d.text(0.75, 6.2, "SIG-", size=9, weight="bold", ha="right", color=a)
    d.text(3.5, 5.93, "SIG+", size=9, weight="bold", ha="left", color=a)
    d.text(2.2, 6.2, "4 x 350 ohm\nCEA-13-..-350", size=7.6, ha="center", color=C["sub"])
    # terminal pads on the balance
    d.ax.add_patch(Rectangle((4.15, 4.0), 0.55, 4.45, fc="#fff7e6", ec=C["warn"], lw=1.2, zorder=3))
    d.text(4.42, 8.62, "pads on\naft block", size=7.4, ha="center", color=C["warn"])
    pads = {"EX+": 8.15, "S+": 7.6, "SIG+": 6.45, "SIG-": 5.65, "S-": 4.8, "EX-": 4.25}
    for k, y in pads.items():
        d.term(4.42, y, C["warn"])
    d.wire([T, (4.42, 8.15)], p, lw=1.6)
    d.wire([(2.45, 8.15), (2.45, 7.6), (4.42, 7.6)], p, lw=1.0, ls="--")
    d.text(3.35, 7.75, "sense taps at the bridge", size=7.0, color=p, ha="center")
    d.wire([R_, (3.8, 6.2), (3.8, 6.45), (4.42, 6.45)], a, lw=1.6)
    d.wire([L_, (0.6, 6.2), (0.6, 5.65 - 0.0), (0.6, 3.6), (3.95, 3.6), (3.95, 5.65), (4.42, 5.65)], a, lw=1.6)
    d.wire([B, (4.42, 4.25)], C["gnd"], lw=1.6)
    d.wire([(2.45, 4.25), (2.45, 4.8), (4.42, 4.8)], C["gnd"], lw=1.0, ls="--")
    # cable path
    d.ax.add_patch(Rectangle((4.95, 3.85), 1.0, 4.75, fc="#eef1f5", ec=gr, lw=1.0, ls="--", zorder=1))
    d.text(5.45, 8.78, "sting +\nspindle", size=7.4, ha="center", color=gr)
    d.text(5.45, 3.63, "32 AWG PTFE,\npairs twisted", size=7.0, ha="center", color=gr, va="top")
    d.ax.add_patch(Rectangle((6.05, 3.85), 0.35, 4.75, fc="white", ec=C["ink"], lw=1.2, zorder=3))
    d.text(6.22, 8.8, "J0", size=8.5, weight="bold", ha="center")
    for k, y in pads.items():
        col = p if "EX+" in k or k == "S+" else (C["gnd"] if k in ("EX-", "S-") else a)
        d.wire([(4.42, y), (6.22, y)], col, lw=1.4)
        d.term(6.22, y)
    d.text(7.0, 8.15, "trunk pair 1\n(EX doubled)", size=7.0, color=p, ha="center")
    d.text(7.0, 7.6 - 0.05, "pair 2", size=7.0, color=p, ha="center")
    d.text(7.0, 6.05, "own shielded\npair", size=7.0, color=a, ha="center")
    d.text(7.0, 4.5, "pair 1 / 2", size=7.0, color=C["gnd"], ha="center")
    for y in pads.values():
        d.wire([(6.22, y), (7.95, y)], C["ink"], lw=0.8, ls=":")
    # ---------------- rig box side (bottom-left)
    d.zone(0.35, 0.3, 7.6, 2.7, "RIG BOX  (J1)")
    d.box(0.55, 0.55, 2.2, 2.05, "NAU7802 #1", ["VIN1P <- SIG+", "VIN1N <- SIG-", "AVDD <- EX bus", "REF = AVDD",
                                                "mux ch0, 0x2A"], ts=9, ls=7.6, dy=0.22)
    d.box(2.95, 0.55, 2.2, 2.05, "LT3042 3.30 V", ["OUT -> EX+ bus", "(J1 pins 1-2)", "GND -> EX- bus",
                                                   "-> AGND star"], ts=9, ls=7.6, dy=0.22, ec=p)
    d.box(5.35, 0.55, 2.4, 2.05, "ADS1115 #1 (0x48)", ["A0-A1: S+ / S- at the", "balance (remote sense)",
                                                       "A2-A3: EX at the box", "-> k = V_bal / V_box"], ts=9, ls=7.6,
          dy=0.22)
    d.text(4.15, 3.12, "Input RC per channel: 100 ohm series + 0.1 uF differential (+ 10 nF to AGND each side).",
           size=7.6, color=C["sub"], ha="center")
    # ---------------- harness (right)
    d.zone(8.3, 0.3, 7.45, 8.95, "6-BRIDGE HARNESS AND J0 PINOUT  (DC-37, 26 conductors used)")
    bridges = ["M1", "M2", "Y1", "Y2", "L", "A"]
    bx0, by0 = 8.65, 7.9
    d.wire([(bx0 - 0.05, 8.45), (11.6, 8.45)], p, lw=2.4)
    d.text(bx0, 8.65, "EX+ bus (pads)", size=7.8, color=p)
    d.wire([(bx0 - 0.05, 4.05), (11.6, 4.05)], C["gnd"], lw=2.4)
    d.text(bx0, 3.85, "EX- bus (pads)", size=7.8, color=C["gnd"])
    for i, b in enumerate(bridges):
        cy = 7.75 - i * 0.62
        cx = 9.4
        pts = [(cx, cy + 0.22), (cx + 0.28, cy), (cx, cy - 0.22), (cx - 0.28, cy)]
        d.ax.add_patch(Polygon(pts, closed=True, fc="white", ec=C["ink"], lw=1.2, zorder=4))
        d.text(cx - 0.45, cy, b, size=8.6, weight="bold", ha="right")
        d.wire([(cx, cy + 0.22), (cx, cy + 0.32), (cx + 0.55, cy + 0.32), (cx + 0.55, 8.45)], p, lw=0.9)
        d.wire([(cx, cy - 0.22), (cx, cy - 0.3), (cx + 0.75, cy - 0.3), (cx + 0.75, 4.05)], C["gnd"], lw=0.9)
        d.wire([(cx + 0.28, cy), (11.6, cy)], a, lw=1.3)
        d.wire([(cx - 0.28, cy), (cx - 0.28, cy - 0.12), (cx + 0.95, cy - 0.12), (cx + 0.95, cy - 0.08),
                (11.6, cy - 0.08)], a, lw=1.0)
        d.text(11.35, cy + 0.14, f"NAU7802 ch{i}", size=6.8, color=a, ha="right")
    d.text(8.55, 3.2, "NTC 10k on the aft block -> ADS1115 #2\npod 3V3 / GND / SDA / SCL -> I2C bus 3 (LTC4311)",
           size=7.6, color=C["sub"], va="top")
    # pinout table
    rows = [("1, 2", "EX+ (doubled)"), ("3, 4", "EX- (doubled)"), ("5, 6", "SENSE+, SENSE-"),
            ("7, 8", "M1 SIG+, SIG-"), ("9, 10", "M2 SIG+, SIG-"), ("11, 12", "Y1 SIG+, SIG-"),
            ("13, 14", "Y2 SIG+, SIG-"), ("15, 16", "L SIG+, SIG-"), ("17, 18", "A SIG+, SIG-"),
            ("19, 20", "NTC a, b"), ("21, 22", "pod 3V3, GND"), ("23, 24", "pod SDA, SCL"),
            ("25, 26", "spare (pair)"), ("27-36", "not used"), ("37", "braid / overall shield"),
            ("shell", "isolated from housing")]
    tx, ty = 12.0, 8.55
    d.text(tx, ty + 0.05, "J0 / J1 pin", size=8.2, weight="bold")
    d.text(tx + 1.15, ty + 0.05, "signal", size=8.2, weight="bold")
    for i, (pn, sig) in enumerate(rows):
        y = ty - 0.3 - i * 0.29
        if i % 2 == 0:
            d.ax.add_patch(Rectangle((tx - 0.08, y - 0.14), 3.6, 0.28, fc="#f1f4f9", ec="none", zorder=2))
        d.text(tx, y, pn, size=7.9)
        d.text(tx + 1.15, y, sig, size=7.9)
    d.text(tx - 0.05, 2.55, "Trunk J0 -> J1: 12 individually\nshielded pairs, 24 AWG, high-flex.\nPair shields + overall "
                           "shield to\nAGND at the rig box ONLY.\nAt J0 the sting braid joins the\noverall shield; the "
                           "shell is\nisolated from the roll housing.", size=7.6, color=C["sub"], va="top")
    d.save("bridge")


# ====================================================================== (e) Pi pin map
def pinmap():
    d = D(16, 10.6, "Raspberry Pi 4 (rig computer) pin map, I2C addresses and the sensor node",
          "Physical header pins, BCM GPIO numbers; unused pins grey. Station Pi uses no GPIO (Ethernet only).")
    names = {1: "3V3", 2: "5V", 3: "GPIO2 SDA1", 4: "5V", 5: "GPIO3 SCL1", 6: "GND", 7: "GPIO4", 8: "GPIO14 TXD",
             9: "GND", 10: "GPIO15 RXD", 11: "GPIO17", 12: "GPIO18", 13: "GPIO27", 14: "GND", 15: "GPIO22",
             16: "GPIO23", 17: "3V3", 18: "GPIO24", 19: "GPIO10 MOSI", 20: "GND", 21: "GPIO9 MISO", 22: "GPIO25",
             23: "GPIO11 SCLK", 24: "GPIO8 CE0", 25: "GND", 26: "GPIO7 CE1", 27: "ID_SD", 28: "ID_SC", 29: "GPIO5",
             30: "GND", 31: "GPIO6", 32: "GPIO12", 33: "GPIO13", 34: "GND", 35: "GPIO19", 36: "GPIO16",
             37: "GPIO26", 38: "GPIO20", 39: "GND", 40: "GPIO21"}
    use = {1: ("3V3 -> TCA9548A, NAU7802 DVDD, ADS1115", "pwr3"), 2: ("5 V in (from PSU2 via F5)", "pwr5"),
           3: ("I2C-1 SDA -> TCA9548A (100 kHz)", "i2c"), 5: ("I2C-1 SCL", "i2c"),
           7: ("I2C-3 SDA -> LTC4311 -> pod bus", "i2c"), 29: ("I2C-3 SCL (dtoverlay=i2c3)", "i2c"),
           11: ("in: E-STOP OK (opto)", "safe"), 13: ("in: MOTOR POWER present (opto)", "safe"),
           15: ("out: WATCHDOG heartbeat 10 Hz", "safe"), 16: ("in: WIND ON (tunnel drive, opto)", "io"),
           18: ("out: stack light (MOSFET)", "io"), 12: ("out: box fan PWM", "io"),
           37: ("1-Wire DS18B20 air temp (4k7 pull-up)", "io"), 31: ("in: ADS1115 ALERT/RDY (optional)", "io"),
           19: ("SPI0 reserved (ADS1263 upgrade)", "spare"), 21: ("SPI0 reserved", "spare"),
           23: ("SPI0 reserved", "spare"), 24: ("SPI0 CE0 reserved", "spare"), 8: ("UART debug console", "spare"),
           10: ("UART debug console", "spare")}
    colmap = {"pwr3": "#e67e22", "pwr5": C["power"], "gnd": "#222222", "i2c": C["digital"], "safe": C["safety"],
              "io": C["analog"], "spare": "#b0b7c0", None: "#d5d9df"}
    hx0, hx1, ytop, dy = 5.55, 6.05, 9.15, 0.385
    d.ax.add_patch(FancyBboxPatch((hx0 - 0.3, ytop - 19 * dy - 0.3), 1.1, 19 * dy + 0.6,
                                  boxstyle="round,pad=0,rounding_size=0.06", fc="#1f3b2d", ec="none", zorder=2))
    for n in range(1, 41):
        r = (n - 1) // 2
        x = hx0 if n % 2 else hx1
        y = ytop - r * dy
        kind = use.get(n, (None, None))[1]
        if names[n] == "GND":
            kind = "gnd"
        fc = colmap[kind]
        d.ax.add_patch(Circle((x, y), 0.14, fc=fc, ec="white", lw=1.0, zorder=4))
        d.text(x, y, str(n), size=6.3, ha="center", color="white", weight="bold", z=5)
        lab = names[n] + ("  " + use[n][0] if n in use else "")
        col = C["ink"] if n in use and use[n][1] != "spare" else C["sub"]
        if n % 2:
            d.text(hx0 - 0.4, y, lab if n not in use else f"{use[n][0]}   {names[n]}", size=7.6, ha="right",
                   color=col, weight="bold" if n in use and use[n][1] != "spare" else "normal")
        else:
            d.text(hx1 + 0.4, y, lab, size=7.6, ha="left", color=col,
                   weight="bold" if n in use and use[n][1] != "spare" else "normal")
    d.text((hx0 + hx1) / 2, ytop + 0.45, "40-pin header", size=8.5, ha="center", weight="bold")
    # USB / Ethernet box
    d.box(0.35, 0.3, 4.6, 1.25, "USB + Ethernet", ["USB: Uno (grbl)  -> /dev/grbl   (udev rule by serial no.)",
                                                    "USB: Pico node   -> /dev/sensornode", "Ethernet -> station Pi (static IP, "
                                                    "UDP/TCP rig protocol)"], ts=9.2, ls=7.6, dy=0.25, fc="white")
    # I2C map
    d.box(10.55, 4.35, 5.2, 4.95, "I2C address map", [
        "I2C-1 (100 kHz) -> TCA9548A mux 0x70",
        "   ch0  NAU7802  M1    0x2A",
        "   ch1  NAU7802  M2    0x2A",
        "   ch2  NAU7802  Y1    0x2A",
        "   ch3  NAU7802  Y2    0x2A",
        "   ch4  NAU7802  L     0x2A",
        "   ch5  NAU7802  A     0x2A",
        "   ch6  ADS1115 #1 0x48 (sense), #2 0x49 (NTC)",
        "         ABP2 pitot 0x28, BMP390 ambient 0x77",
        "   ch7  spare",
        "I2C-3 (50 kHz, LTC4311) -> pod, via J0/J1",
        "   BMP390 base 0x76, BMP390 cavity 0x77,",
        "   LSM6DSOX accelerometer 0x6A",
        "1-Wire GPIO26: DS18B20 air temperature"], ts=9.5, ls=7.7, dy=0.3, fc="white")
    d.box(10.55, 0.35, 5.2, 3.7, "Sensor node: Raspberry Pi Pico", [
        "USB to the rig Pi (power + CDC serial, 100 Hz)",
        "SPI0: GP18 SCK, GP19 MOSI, GP16 MISO",
        "  GP17 CS  roll AS5048A   (spindle end)",
        "  GP20 CS  pitch AS5048A  (pinion shaft)",
        "  GP21 CS  yaw AS5048A    (pinion shaft)",
        "  GP22 CS  SCL3300 inclinometer (roll housing)",
        "3V3(OUT) -> sensors (AS5048A in 3.3 V mode)",
        "1 MHz, 100 ohm series at each driver; < 1 m runs",
        "AS5048A SPI mode 1; SCL3300 mode 0"], ts=9.5, ls=7.6, dy=0.3, fc="white")
    d.legend(8.5, 5.0, [("3.3 V", "#e67e22", "-"), ("5 V", C["power"], "-"),
                                          ("ground", "#222222", "-"), ("I2C", C["digital"], "-"),
                                          ("safety I/O", C["safety"], "-"), ("other I/O", C["analog"], "-"),
                                          ("spare / reserved", "#b0b7c0", "-")], w=1.9)
    d.save("pinmap")


# ====================================================================== (f) harness route
def harness_route():
    d = D(16, 6.6, "Balance cable route and bore fill",
          "26 conductors of 32 AWG PTFE (OD ~0.017 in) from the gauges to J0; fill = conductor area / hole area")
    a = C["analog"]
    stages = [("Pod sensor bay", "2x BMP390 + LSM6DSOX;\n4 wires through the puck\nwire hole d .188", 0.4),
              ("Balance", "24 gauges -> pads on the\naft block; model-side wires\ncross as thin loops", 2.75),
              ("Entry hole d .188", "26 x 32 AWG\nfill 21 %", 5.1),
              ("Spigot bore d .250", "fill 12 %", 6.9),
              ("Sting bore d .300", "17.45 in; braid sleeve\nover the bundle; fill 8 %\n(25 % with braid)", 8.7),
              ("Spindle exit d .250", "radial, x = 20.53 in;\nPTFE grommet; fill 12 %", 10.85),
              ("Clock-spring loop", "270 deg (-90..+180) in\nthe gearbox-adapter\nwire window -> J0", 13.05)]
    w = 1.95
    for i, (t, s_, _) in enumerate(stages):
        x = 0.4 + i * 2.25
        d.box(x, 2.6, w, 2.1, t, [], ts=9.0, fc=C["hi"] if i in (2, 3, 4, 5) else C["fill"])
        d.text(x + 0.12, 3.95, s_, size=7.7, color=C["sub"], va="top")
        if i < len(stages) - 1:
            d.wire([(x + w, 3.65), (x + 2.25, 3.65)], a, lw=2.2, arrow=True)
    d.wire([(0.4 + 6 * 2.25 + w / 2, 2.6), (0.4 + 6 * 2.25 + w / 2, 1.75)], a, lw=2.2, arrow=True)
    d.box(10.7, 0.35, 4.95, 1.4, "J0 DC-37 -> 12-pair shielded trunk -> J1", ["high-flex (cable-chain) cable, ~4 m,",
                                                                              "through the pitch and yaw service loops"],
          ts=9.2, ls=7.8, dy=0.25)
    d.text(0.45, 1.7, "Check:  32 AWG PTFE OD 0.017 in -> 26 x 0.000227 = 0.0059 in^2.\n"
                      "Pull-through guideline <= 40 % fill: every hole passes; the d .188 entry hole is the bottleneck.\n"
                      "Calibrate with all wires installed - the loops that cross the flexures carry a little load.",
           size=8.3, color=C["ink"], va="center")
    d.text(0.45, 0.6, "Flag: gearbox adapter WT-6C-204 wire window is drawn for +-90 deg; bench calibration needs "
                      "-90..+180 deg -> check / widen it.", size=8.3, color=C["warn"], weight="bold", va="center")
    d.save("harness_route")


if __name__ == "__main__":
    block()
    power_safety()
    steppers()
    bridge()
    pinmap()
    harness_route()
