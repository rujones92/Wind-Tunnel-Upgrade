"""
Minimal GD&T drawing engine (ASME Y14.5-2018 style, ANSI B sheet, third-angle projection).

Views are true hidden-line projections of the CadQuery/OCCT solids (HLRBRep); sections cut the solid and hatch the
cut faces. Annotations are placed with 3D model points, mapped into each view, so they stay attached to the geometry.
Units on the sheet: inches.
"""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.set_loglevel("error")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, PathPatch
from matplotlib.path import Path as MPath
import cadquery as cq
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.TopoDS import TopoDS

plt.rcParams["font.family"] = ["DejaVu Sans", "Segoe UI Symbol"]
plt.rcParams["pdf.fonttype"] = 42

SW, SH = 17.0, 11.0
TXT = 0.115 * 72                 # text height 0.115 in, in points
SYM = {"position": "⌖", "perp": "⟂", "parallel": "∥", "flat": "⏥", "circ": "○",
       "cyl": "⌭", "runout": "↗", "trunout": "⌰", "profile": "⌓", "line": "⌒",
       "angular": "∠", "conc": "◎", "sym": "⌯", "dia": "⌀", "M": "Ⓜ", "L": "Ⓛ",
       "cbore": "⌴", "straight": "⏤", "csink": "⌵", "depth": "⌄"}
D = SYM["dia"]
VIEWS = {  # X (sheet right), Y (sheet up), Z (towards the eye)
    "front": ((1, 0, 0), (0, 0, 1), (0, -1, 0)),
    "top": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    "right": ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
    "left": ((0, -1, 0), (0, 0, 1), (-1, 0, 0)),
    "bottom": ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
}


def _edges_to_polylines(comp, defl):
    out = []
    if comp is None or comp.IsNull():
        return out
    ex = TopExp_Explorer(comp, TopAbs_EDGE)
    while ex.More():
        e = TopoDS.Edge_s(ex.Current())
        c = BRepAdaptor_Curve(e)
        d = GCPnts_QuasiUniformDeflection(c, defl)
        if d.IsDone() and d.NbPoints() > 1:
            out.append(np.array([(d.Value(i).X(), d.Value(i).Y()) for i in range(1, d.NbPoints() + 1)]))
        ex.Next()
    return out


def hlr(shape, kind, defl=1e-3):
    X, Y, Z = VIEWS[kind]
    algo = HLRBRep_Algo()
    algo.Add(shape.wrapped)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*Z), gp_Dir(*X))))
    algo.Update()
    algo.Hide()
    h = HLRBRep_HLRToShape(algo)
    vis = _edges_to_polylines(h.VCompound(), defl) + _edges_to_polylines(h.OutLineVCompound(), defl)
    hid = _edges_to_polylines(h.HCompound(), defl) + _edges_to_polylines(h.OutLineHCompound(), defl)
    return vis, hid


class View:
    def __init__(self, sheet, shape, kind, scale, center, label=None, section=None, hidden=True, hatch_faces=None,
                 label_pos="below"):
        self.sheet, self.kind, self.scale = sheet, kind, scale
        self.X, self.Y, _ = (np.array(v, float) for v in VIEWS[kind])
        vis, hid = hlr(shape, kind)
        allp = np.vstack(vis) if vis else np.zeros((1, 2))
        self.u0 = (allp[:, 0].min() + allp[:, 0].max()) / 2
        self.v0 = (allp[:, 1].min() + allp[:, 1].max()) / 2
        self.cx, self.cy = center
        self.half_w = (allp[:, 0].max() - allp[:, 0].min()) / 2 * scale
        self.half_h = (allp[:, 1].max() - allp[:, 1].min()) / 2 * scale
        ax = sheet.ax
        if hidden:
            for pl in hid:
                s = self._uv(pl)
                ax.plot(s[:, 0], s[:, 1], color="0.45", lw=0.45, ls=(0, (4, 2.5)), zorder=2)
        for f in (hatch_faces or []):
            self._hatch(f)
        for pl in vis:
            s = self._uv(pl)
            ax.plot(s[:, 0], s[:, 1], color="k", lw=0.8, zorder=3)
        if label:
            if label_pos == "below":
                ax.text(self.cx, self.cy - self.half_h - 0.38, label, ha="center", va="top", fontsize=TXT * 1.05,
                        weight="bold")
            elif label_pos == "above":
                ax.text(self.cx, self.cy + self.half_h + 0.2, label, ha="center", va="bottom", fontsize=TXT * 1.05,
                        weight="bold")
            else:
                ax.text(label_pos[0], label_pos[1], label, ha="center", va="center", fontsize=TXT * 1.05,
                        weight="bold")

    def _uv(self, pl):
        return np.c_[self.cx + (pl[:, 0] - self.u0) * self.scale, self.cy + (pl[:, 1] - self.v0) * self.scale]

    def m(self, p):
        p = np.asarray(p, float)
        return np.array([self.cx + (p @ self.X - self.u0) * self.scale, self.cy + (p @ self.Y - self.v0) * self.scale])

    def _hatch(self, face):
        verts, codes = [], []
        for w in [face.outerWire()] + list(face.innerWires()):
            pts = np.array([(p.x, p.y, p.z) for p in w.positions(list(np.linspace(0, 1, 160)))])
            s = np.array([self.m(p) for p in pts])
            verts += list(s) + [s[0]]
            codes += [MPath.MOVETO] + [MPath.LINETO] * (len(s) - 1) + [MPath.CLOSEPOLY]
        self.sheet.ax.add_patch(PathPatch(MPath(verts, codes), fc="none", ec="none", hatch="////", lw=0, zorder=1))


def section_cut(shape, axis, value, keep="+"):
    """Cut a solid with an axis-aligned plane; return (kept solid, list of cut faces on the plane)."""
    big = 200.0
    lo, hi = (value, big) if keep == "+" else (-big, value)
    rng = {"x": (lo, hi, -big, big, -big, big), "y": (-big, big, lo, hi, -big, big), "z": (-big, big, -big, big, lo, hi)}[axis]
    b = cq.Solid.makeBox(rng[1] - rng[0], rng[3] - rng[2], rng[5] - rng[4], cq.Vector(rng[0], rng[2], rng[4]))
    kept = shape.intersect(b)
    idx = "xyz".index(axis)
    faces = [f for f in kept.Faces() if abs(f.Center().toTuple()[idx] - value) < 1e-6
             and abs(abs(f.normalAt().toTuple()[idx]) - 1) < 1e-6]
    return kept, faces


class Sheet:
    def __init__(self, dwg_no, title, material, finish, scale_txt, sheet_no, sheets, mass=None, rev="A",
                 date="2026-10-02", notes=(), next_assy=""):
        self.fig = plt.figure(figsize=(SW, SH))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        ax = self.ax
        ax.set_xlim(0, SW); ax.set_ylim(0, SH); ax.set_aspect("equal"); ax.axis("off")
        ax.add_patch(Rectangle((0.4, 0.4), SW - 0.8, SH - 0.8, fc="none", ec="k", lw=1.6))
        for i, z in enumerate("87654321"):                           # zone marks
            x = 0.4 + (i + 0.5) * (SW - 0.8) / 8
            ax.text(x, SH - 0.28, z, ha="center", fontsize=8); ax.text(x, 0.22, z, ha="center", fontsize=8)
        for j, z in enumerate("DCBA"):
            y = 0.4 + (j + 0.5) * (SH - 0.8) / 4
            ax.text(0.2, y, z, va="center", fontsize=8); ax.text(SW - 0.24, y, z, va="center", fontsize=8)
        self.dwg_no, self.notes = dwg_no, list(notes)
        self._title_block(dwg_no, title, material, finish, scale_txt, sheet_no, sheets, mass, rev, date, next_assy)

    # ------------------------------------------------------------------ title block / notes
    def _title_block(self, dwg, title, mat, fin, scale, n, N, mass, rev, date, nxt):
        ax = self.ax
        x0, y0, w, h = SW - 0.4 - 7.2, 0.4, 7.2, 2.35
        ax.add_patch(Rectangle((x0, y0), w, h, fc="white", ec="k", lw=1.2, zorder=5))

        def cell(x, y, cw, ch, lab, val, vs=9, bold=False):
            ax.add_patch(Rectangle((x, y), cw, ch, fc="none", ec="k", lw=0.6, zorder=6))
            ax.text(x + 0.05, y + ch - 0.05, lab, fontsize=5.5, va="top", zorder=7)
            ax.text(x + 0.08, y + 0.07, val, fontsize=vs, va="bottom", zorder=7, weight="bold" if bold else "normal")
        cell(x0, y0 + 1.75, 4.2, 0.6, "PROJECT", "Wind tunnel - motorized 6-component sting balance", 9)
        cell(x0 + 4.2, y0 + 1.75, 3.0, 0.6, "DRAWN / DATE", f"Claude (AI-generated)  {date}", 7.5)
        cell(x0, y0 + 1.05, 4.2, 0.7, "TITLE", title, 11, True)
        cell(x0 + 4.2, y0 + 1.05, 1.5, 0.7, "CHECKED", "", 8)
        cell(x0 + 5.7, y0 + 1.05, 1.5, 0.7, "APPROVED", "", 8)
        cell(x0, y0 + 0.5, 4.2, 0.55, "MATERIAL", mat, 8)
        cell(x0 + 4.2, y0 + 0.5, 3.0, 0.55, "FINISH", fin, 7.5)
        cell(x0, y0, 2.4, 0.5, "DWG NO.", dwg, 10, True)
        cell(x0 + 2.4, y0, 0.6, 0.5, "REV", rev, 10, True)
        cell(x0 + 3.0, y0, 0.6, 0.5, "SIZE", "B", 10)
        cell(x0 + 3.6, y0, 1.2, 0.5, "SCALE", scale, 9)
        cell(x0 + 4.8, y0, 1.2, 0.5, "WEIGHT", f"{mass:.2f} lb" if mass else "-", 8)
        cell(x0 + 6.0, y0, 1.2, 0.5, "SHEET", f"{n} OF {N}", 9)
        # tolerance block + projection symbol
        tx, ty, tw, th = x0 - 3.55, 0.4, 3.55, 2.35
        ax.add_patch(Rectangle((tx, ty), tw, th, fc="white", ec="k", lw=1.2, zorder=5))
        lines = ["UNLESS OTHERWISE SPECIFIED:", "DIMENSIONS ARE IN INCHES", "TOLERANCES:",
                 "  .X  ±.03    .XX  ±.010", "  .XXX ±.005  .XXXX ±.0005",
                 "  ANGLES ±0°30'", "BREAK SHARP EDGES .005-.015", "SURFACE FINISH 63 µin Ra MAX",
                 "INTERPRET PER ASME Y14.5-2018", "UNDIMENSIONED GEOMETRY PER STEP MODEL"]
        for i, t in enumerate(lines):
            ax.text(tx + 0.08, ty + th - 0.12 - i * 0.2, t, fontsize=6.6, va="top", zorder=7)
        px, py = tx + 2.75, ty + 0.35                                # third-angle symbol
        ax.add_patch(Polygon([(px - 0.25, py - 0.12), (px - 0.25, py + 0.12), (px + 0.05, py + 0.2),
                              (px + 0.05, py - 0.2)], closed=True, fc="none", ec="k", lw=0.7, zorder=7))
        for r in (0.2, 0.12):
            ax.add_patch(matplotlib.patches.Circle((px + 0.42, py), r, fc="none", ec="k", lw=0.7, zorder=7))
        ax.text(px + 0.1, py - 0.3, "THIRD ANGLE", fontsize=5, ha="center", zorder=7)
        if nxt:
            ax.text(x0 + 0.05, y0 + h + 0.08, f"NEXT ASSY: {nxt}", fontsize=7)

    def draw_notes(self, x=0.6, y=2.95, width_chars=80):
        ax = self.ax
        ax.text(x, y, "NOTES:", fontsize=TXT, weight="bold", va="top")
        yy = y - 0.22
        for i, n in enumerate(self.notes, 1):
            words, line, first = n.split(), "", True
            for wd in words + [None]:
                if wd is None or len(line) + len(wd) + 1 > width_chars:
                    ax.text(x + (0 if first else 0.25), yy, (f"{i}. " if first else "") + line, fontsize=7.4, va="top")
                    yy -= 0.17
                    first, line = False, ""
                    if wd is None:
                        break
                line = (line + " " + wd).strip()

    # ------------------------------------------------------------------ annotation primitives
    def _txt(self, x, y, s, ha="center", va="center", rot=0, basic=False, size=None, box_fc="white"):
        t = self.ax.text(x, y, s, ha=ha, va=va, rotation=rot, fontsize=size or TXT, zorder=8,
                         bbox=dict(boxstyle="square,pad=0.15", fc=box_fc, ec="k" if basic else "none", lw=0.6))
        return t

    def _arrow(self, x0, y0, x1, y1):
        self.ax.annotate("", (x1, y1), (x0, y0), zorder=7,
                         arrowprops=dict(arrowstyle="-|>,head_length=0.55,head_width=0.18", lw=0.6, color="k",
                                         shrinkA=0, shrinkB=0))

    def lin(self, v, p1, p2, d="h", off=0.4, text=None, basic=False, tol=None, side=None):
        """Linear dimension between model points p1, p2 in view v. d='h' horizontal, 'v' vertical. off: sheet in."""
        a, b = v.m(p1), v.m(p2)
        ax = self.ax
        if d == "h":
            yd = (a[1] if side is None else side) + off
            for q in (a, b):
                s = np.sign(yd - q[1]) or 1
                ax.plot([q[0], q[0]], [q[1] + 0.05 * s, yd + 0.09 * s], "k", lw=0.45, zorder=6)
            mid, L = (a[0] + b[0]) / 2, abs(b[0] - a[0])
            if L > 0.5:
                self._arrow(mid, yd, a[0], yd); self._arrow(mid, yd, b[0], yd)
            else:                                                   # short: arrows from outside
                lo, hi = sorted((a[0], b[0]))
                self._arrow(lo - 0.3, yd, lo, yd); self._arrow(hi + 0.3, yd, hi, yd)
            self._txt(mid, yd, text, basic=basic)
        else:
            xd = (a[0] if side is None else side) + off
            for q in (a, b):
                s = np.sign(xd - q[0]) or 1
                ax.plot([q[0] + 0.05 * s, xd + 0.09 * s], [q[1], q[1]], "k", lw=0.45, zorder=6)
            mid = (a[1] + b[1]) / 2
            if abs(b[1] - a[1]) > 0.5:
                self._arrow(xd, mid, xd, a[1]); self._arrow(xd, mid, xd, b[1])
            else:
                lo, hi = sorted((a[1], b[1]))
                self._arrow(xd, lo - 0.3, xd, lo); self._arrow(xd, hi + 0.3, xd, hi)
            self._txt(xd, mid, text, basic=basic, rot=90)

    def leader(self, v, p, dx, dy, text, ha=None):
        a = v.m(p)
        tx, ty = a[0] + dx, a[1] + dy
        self.ax.plot([tx, tx + (0.2 if dx >= 0 else -0.2)], [ty, ty], "k", lw=0.5, zorder=6)
        self._arrow(tx, ty, a[0], a[1])
        self.ax.text(tx + (0.25 if dx >= 0 else -0.25), ty, text, ha=ha or ("left" if dx >= 0 else "right"),
                     va="center", fontsize=TXT, zorder=8, linespacing=1.25)
        return tx, ty

    def call(self, v, p, x, y, text, ha="left"):
        """Callout text at absolute sheet (x, y) with a leader + shoulder to model point p."""
        a = v.m(p)
        sx = x - 0.12 if ha == "left" else x + 0.12
        self.ax.plot([sx - (0.18 if ha == "left" else -0.18), sx], [y, y], "k", lw=0.5, zorder=6)
        self._arrow(sx - (0.18 if ha == "left" else -0.18), y, a[0], a[1])
        self.ax.text(x, y, text, ha=ha, va="center", fontsize=TXT, zorder=8, linespacing=1.25)

    def datum_at(self, x, y, letter, tx, ty, triangle=True):
        """Datum feature symbol box at (x, y), attached to sheet point (tx, ty)."""
        self.ax.plot([tx, x], [ty, y], "k", lw=0.6, zorder=6)
        if triangle:
            ang = math.atan2(y - ty, x - tx)
            nx, ny = -math.sin(ang), math.cos(ang)
            self.ax.add_patch(Polygon([(tx + nx * 0.07, ty + ny * 0.07), (tx - nx * 0.07, ty - ny * 0.07),
                                       (tx + math.cos(ang) * 0.12, ty + math.sin(ang) * 0.12)], closed=True,
                                      fc="k", ec="k", zorder=7))
        self.ax.add_patch(Rectangle((x - 0.13, y - 0.13), 0.26, 0.26, fc="white", ec="k", lw=0.8, zorder=8))
        self.ax.text(x, y, letter, ha="center", va="center", fontsize=TXT * 1.1, weight="bold", zorder=9)

    def fcf(self, x, y, cells, v=None, p=None, attach="left"):
        """Feature control frame at sheet (x, y) (lower-left). cells: ['position', 'Ø.005Ⓜ', 'A', 'B']."""
        ax = self.ax
        hgt, cx = 0.24, x
        boxes = []
        for i, c in enumerate(cells):
            s = SYM.get(c, c) if i == 0 else c
            w = 0.28 if i == 0 else max(0.24, 0.085 * len(s) + 0.12)
            ax.add_patch(Rectangle((cx, y), w, hgt, fc="white", ec="k", lw=0.7, zorder=8))
            ax.text(cx + w / 2, y + hgt / 2, s, ha="center", va="center", fontsize=TXT * (1.15 if i == 0 else 1),
                    zorder=9)
            boxes.append((cx, w))
            cx += w
        if v is not None and p is not None:
            a = v.m(p)
            sx = x if attach == "left" else cx
            self._arrow(sx, y + hgt / 2, a[0], a[1])
        return cx

    def datum(self, v, p, letter, dx, dy):
        a = v.m(p)
        bx, by = a[0] + dx, a[1] + dy
        self.ax.plot([a[0], bx], [a[1], by], "k", lw=0.6, zorder=6)
        ang = math.atan2(by - a[1], bx - a[0])
        nx, ny = -math.sin(ang), math.cos(ang)
        tri = [(a[0] + nx * 0.07, a[1] + ny * 0.07), (a[0] - nx * 0.07, a[1] - ny * 0.07),
               (a[0] + math.cos(ang) * 0.12, a[1] + math.sin(ang) * 0.12)]
        self.ax.add_patch(Polygon(tri, closed=True, fc="k", ec="k", zorder=7))
        self.ax.add_patch(Rectangle((bx - 0.13, by - 0.13), 0.26, 0.26, fc="white", ec="k", lw=0.8, zorder=8))
        self.ax.text(bx, by, letter, ha="center", va="center", fontsize=TXT * 1.1, weight="bold", zorder=9)

    def finish(self, v, p, ra, dx=0.35, dy=0.35):
        a = v.m(p)
        x, y = a[0] + dx, a[1] + dy
        self.ax.plot([a[0], x], [a[1], y], "k", lw=0.5)
        self.ax.plot([x - 0.08, x, x + 0.18, x + 0.5], [y + 0.1, y - 0.0, y + 0.3, y + 0.3], "k", lw=0.7, zorder=7)
        self.ax.text(x + 0.05, y + 0.33, ra, fontsize=6.8, va="bottom", zorder=8)

    def centerline(self, v, p1, p2, ext=0.15):
        a, b = v.m(p1), v.m(p2)
        d = (b - a) / (np.linalg.norm(b - a) + 1e-12)
        a, b = a - d * ext, b + d * ext
        self.ax.plot([a[0], b[0]], [a[1], b[1]], color="k", lw=0.4, ls=(0, (12, 3, 2, 3)), zorder=4)

    def cutting_plane(self, v, p1, p2, letter, arrow_dir):
        a, b = v.m(p1), v.m(p2)
        self.ax.plot([a[0], b[0]], [a[1], b[1]], "k", lw=1.0, ls=(0, (14, 3, 3, 3, 3, 3)), zorder=6)
        for q in (a, b):
            self._arrow(q[0], q[1], q[0] + arrow_dir[0] * 0.35, q[1] + arrow_dir[1] * 0.35)
            self.ax.text(q[0] + arrow_dir[0] * 0.5, q[1] + arrow_dir[1] * 0.5, letter, fontsize=TXT * 1.3,
                         weight="bold", ha="center", va="center")

    def text(self, x, y, s, **kw):
        kw.setdefault("fontsize", TXT)
        self.ax.text(x, y, s, zorder=8, **kw)

    def save(self, pdf, png_path=None):
        pdf.savefig(self.fig)
        if png_path:
            self.fig.savefig(png_path, dpi=110)
        plt.close(self.fig)
