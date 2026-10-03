r"""
Collect the STEP files of every custom METAL part (no assemblies, no bought-part envelopes, no printed parts, no
superseded designs) into Quote-Part-Step-Files/ for quoting (e.g. JLCCNC), named <drawing no>_<part>.step, plus a
manifest (quantity, material, finish, drawing, notes). Parts that only exist inside a drawing script or as part of a
bought component are exported here (STEP in mm, like all project STEP files).

Run from the project root:  .venv\Scripts\python tools\collect_quote_step_files.py
"""
import csv
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad"
OUT = ROOT / "Quote-Part-Step-Files"
DWG = CAD / "drawings"
IN = 25.4

# (drawing, name, source STEP (relative to cad/) or None if exported below, qty, material, finish, notes)
PARTS = [
    ("WT-6C-001", "balance_6c", "six_component_balance/balance_6c_7075.step", 1, "7075-T651", "none (no anodize)",
     "Wire EDM necks/flexures; +-.0005 in sections; CMM report requested. Tighter than JLCCNC standard +-0.05 mm: upload the PDF drawing."),
    ("WT-6C-002", "puck_model_interface", "six_component_balance/model_puck_6061.step", 1, "6061-T6",
     "clear anodize II", "Dowel holes +.0005; face flat .0005 - upload drawing."),
    ("WT-6C-003", "sting", "six_component_balance/sting_4140.step", 1, "4140 pre-hard 28-32 HRC (ask for 42CrMo; 45# steel is the JLCCNC fallback)",
     "black oxide", "0.300 in bore x 17 in (gun drill); OD ground .8740-.8750, straightness .002."),
    ("WT-6C-004", "pod_reference_2.25in_printed", "six_component_balance/pod_reference_2.25in_printed.step", 1,
     "PC-ABS, 3D PRINTED (JLC3DP); NOT CNC", "as printed",
     "3D-PRINTED PART: internal 0.060 in pressure channels and a nose ring cannot be machined. Choose a 3D-printing "
     "process; clear all channels before use. JLC3DP quoted $112.96 in PC-ABS (2026-10-03)."),
    ("WT-6C-201", "spindle_roll", "roll_spindle/spindle_4140.step", 1, "4140 pre-hard (ask for 42CrMo)",
     "black oxide except seats", "35 k5 bearing seats ground; D-D bore by wire EDM; M35x1.5 thread; keyway."),
    ("WT-6C-202", "housing_roll_spindle", "roll_spindle/housing_6061.step", 1, "6061-T6",
     "clear anodize II, mask bores", "2x 55 H7 bores line-bored, runout .0005."),
    ("WT-6C-203-1", "cap_front", "roll_spindle/front_cap_6061.step", 1, "6061-T6", "clear anodize II",
     "Pilot lip 2.1640-2.1645 in."),
    ("WT-6C-203-2", "cap_rear", "roll_spindle/rear_cap_6061.step", 1, "6061-T6", "clear anodize II",
     "Pilot lip 2.1640-2.1645 in."),
    ("WT-6C-204", "adapter_gearbox", "roll_spindle/gearbox_adapter_6061.step", 1, "6061-T6", "clear anodize II",
     "Gearbox hole pattern per NMRV030 vendor drawing (confirm)."),
    ("WT-6C-205", "bracket_roll_encoder", "roll_spindle/encoder_bracket.step", 1, "6061-T6 (.125 plate)",
     "clear anodize II", ""),
    ("WT-6C-301", "sleeve_calibration", "calibration_6c/sleeve_6c_6061.step", 1, "6061-T6",
     "clear anodize II, mask load holes", "20 reamed load holes .2510-.2520, position .001."),
    ("WT-6C-302", "arm_roll_calibration", "calibration_6c/roll_arm_6061.step", 1, "6061-T6 (.500 plate)",
     "clear anodize II", "Knife-edge V-notches, no burrs."),
    ("WT-6C-303", "stirrup_45deg", "calibration_6c/stirrup_45_6061.step", 1, "6061-T6 (.300 plate)",
     "clear anodize II", ""),
    ("WT-6C-304", "yoke_calibration", "calibration_6c/yoke_6c_6061.step", 1, "6061-T6", "clear anodize II", ""),
    ("WT-6C-305", "plate_head_cal_stand", "calibration_6c/head_plate_v2_6061.step", 2, "6061-T6 (.500 plate)",
     "clear anodize II", "Qty 2, identical."),
    ("WT-6C-306-1", "bridge_jack", "calibration_6c/jack_bridge_v2_6061.step", 1, "6061-T6", "clear anodize II", ""),
    ("WT-6C-306-2", "spacer_cross", "calibration_6c/cross_spacer_6061.step", 2, "6061-T6", "clear anodize II",
     "Qty 2."),
    ("WT-6C-307", "tube_base_cal_stand", "calibration_6c/base_tube_v2.step", 1,
     "6061-T6 rect. tube 3 x 1.5 x .125", "none", "Cut to 31 in and drill (hole table on the drawing)."),
    ("WT-6C-308", "upright_pulley", "calibration_stand/drag_upright.step", 4, "6061-T6 (.375 plate)",
     "clear anodize II", "Qty 4, identical (2 drag + 2 thrust; drag_upright.step = thrust_upright.step)."),
    ("WT-6C-309", "axle_pulley", "calibration_stand/thrust_axle.step", 2, "416 stainless or 4140, 5/16 ground rod",
     "none", "Qty 2 (drag + thrust axle)."),
    ("WT-6C-310", "pulley_cable_2in", "calibration_stand/pulley_2in.step", 3, "6061-T6", "clear anodize II, mask bore",
     "Qty 3 (2 drag + 1 thrust); bore for one R5-2Z bearing each."),
    ("WT-6C-401", "cheek_pitch_sector", "pitch_sector_motorized/cheek_plus_y.step", 2, "6061-T6 (.500 plate)",
     "clear anodize II", "Qty 2, identical (+y and -y). Arc slots profile .002 - upload drawing."),
    ("WT-6C-402", "rack_plate_pitch", "pitch_sector_motorized/rack_plate.step", 1, "6061-T6 (.500 plate)",
     "clear anodize II", "Internal arc rack m1.25 by wire EDM; CAD teeth are simplified - use the drawing gear data."),
    ("WT-6C-403", "plate_base_pitch", "pitch_sector_motorized/base_plate.step", 1, "6061-T6 (.750 plate)",
     "clear anodize II", ""),
    ("WT-6C-404-1", "tie_top_pitch", "pitch_sector_motorized/top_tie.step", 1, "6061-T6", "clear anodize II", ""),
    ("WT-6C-404-2", "spacer_pitch_fwd", "pitch_sector_motorized/spacer0.step", 1, "6061-T6", "clear anodize II", ""),
    ("WT-6C-404-3", "spacer_pitch_aft", "pitch_sector_motorized/spacer1.step", 1, "6061-T6", "clear anodize II", ""),
    ("WT-6C-405", "bracket_pitch_drive", "pitch_sector_motorized/drive_bracket_6061.step", 1, "6061-T6",
     "clear anodize II, mask bore", "22 H7 bearing bore; M6 pattern to confirm with the NMRV030 vendor drawing."),
    ("WT-6C-406", "shaft_pitch_pinion", None, 1, "4140 or 416 stainless", "none",
     "Shaft only (8 h6); the m1.25 20T gear is bought and pinned on."),
    ("WT-6C-501", "rail_yaw_inner", "yaw_carriage/rail_inner.step", 1, "6061-T6 (.500 plate)",
     "hard anodize III preferred", "PRELIMINARY - bay dims TO CONFIRM. CAD edges square: 90 deg V-edges per drawing."),
    ("WT-6C-502", "rail_yaw_outer", "yaw_carriage/rail_outer.step", 1, "6061-T6 (.500 plate)",
     "hard anodize III preferred", "PRELIMINARY - TO CONFIRM. V-edges per drawing."),
    ("WT-6C-503", "rack_yaw_floor", "yaw_carriage/floor_rack.step", 1, "6061-T6", "clear anodize II",
     "PRELIMINARY - TO CONFIRM. External arc rack m1.25 by wire EDM; CAD teeth simplified."),
    ("WT-6C-504", "plate_yaw_carriage", "yaw_carriage/carriage_plate_6061.step", 1, "6061-T6 (.500 plate)",
     "clear anodize II", "PRELIMINARY - front edge R12.400 and wheel-stud radii TO CONFIRM."),
    ("WT-6C-506-1", "spacer_wheel_plain", None, 4, "6061-T6 (or 303 stainless)", "clear anodize II",
     "PRELIMINARY."),
    ("WT-6C-506-2", "spacer_wheel_eccentric", None, 4, "6061-T6 (or 303 stainless)", "clear anodize II",
     "PRELIMINARY. Eccentric preload spacer."),
]
GEN_CAD_COPY = {"WT-6C-406": "pitch_sector_motorized/pinion_shaft_8mm.step",
                "WT-6C-506-1": "yaw_carriage/wheel_spacer_plain.step",
                "WT-6C-506-2": "yaw_carriage/wheel_spacer_eccentric.step"}
EXCLUDED = [
    ("WT-6C-505", "yaw pinion: a bought stock m1.25 20T gear, modified (rebore/keyway) - buy the gear with the right bore"),
    ("WT-6C-406 gear", "bought stock m1.25 20T spur gear"),
    ("bought parts", "bearings, KM7 locknut, NMRV030 + gearmotors, NEMA motors, cam followers, V-wheels, encoders, fasteners"),
    ("assemblies", "assembly_*.step files"),
    ("superseded", "aluminum_balance/, printed_pps_balance/, creep_test_coupon/, aoa_mechanism/ and the 3-component stand head/foot/jack bridge/yoke/base tube"),
]


def export_generated():
    """Parts that exist only inside a script or a bought-part model."""
    import cadquery as cq
    sys.path.insert(0, str(DWG))
    sys.path.insert(0, str(CAD / "pitch_sector_motorized"))
    out = {}
    import build_pitch_sector_cad as P
    shaft = (cq.Workplane("XZ").center(P.R_PIN_C, 0).circle(0.157).extrude(1.2)
             .translate((0, -2.55 + 0.6, 0)))
    out["WT-6C-406"] = shaft
    import sheets_yaw as SY
    out["WT-6C-506-1"] = SY.make_spacer(False)
    out["WT-6C-506-2"] = SY.make_spacer(True)
    return out


def main():
    OUT.mkdir(exist_ok=True)
    gen = export_generated()
    import cadquery as cq
    rows = []
    for dwg, name, src, qty, mat, fin, note in PARTS:
        fname = f"{dwg}_{name}.step"
        if src:
            shutil.copy2(CAD / src, OUT / fname)
        else:
            cq.exporters.export(cq.Workplane().add(gen[dwg].val().scale(IN)), str(OUT / fname))
            shutil.copy2(OUT / fname, CAD / GEN_CAD_COPY[dwg])
        pdf = dwg.rsplit("-", 1)[0] if dwg.count("-") == 3 else dwg
        pdf_path = DWG / f"{pdf}.pdf"
        rows.append(dict(file=fname, drawing=dwg, part=name, qty=qty, material=mat, finish=fin,
                         drawing_pdf=f"cad/drawings/{pdf}.pdf" if pdf_path.exists() else "(none yet)", notes=note))
    with open(OUT / "parts_manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    n_pcs = sum(r["qty"] for r in rows)
    lines = ["# Quote package - custom metal parts", "",
             f"{len(rows)} STEP files ({n_pcs} pieces for one set). STEP units are **millimetres**. Generated by "
             "`tools/collect_quote_step_files.py`; quantities, materials and finishes are in `parts_manifest.csv`.", "",
             "Quoting notes (JLCCNC):",
             "- JLCCNC's standard tolerance is +-0.05 mm (+-.002 in). For the precision parts (balance, puck, sting, "
             "spindle, housing, caps, sleeve, cheeks, racks, drive bracket) upload the PDF drawing from `cad/drawings/` "
             "with the STEP and ask them to quote to the drawing tolerances.",
             "- JLCCNC's steel options are 45# and SUS304; the sting and spindle are 4140 pre-hard - ask for 42CrMo "
             "(the Chinese equivalent), or quote them elsewhere.",
             "- The 5xx yaw-carriage parts are PRELIMINARY (bay dimensions TO CONFIRM): quote for budget only.",
             "- The racks' CAD teeth are simplified; the drawings give the gear data.",
             "- US duty on Chinese aluminium/steel parts is pre-collected by JLCCNC (about 90 % aluminium, 80 % steel), "
             "shipped DDP.", "", "| File | Qty | Material | Finish | Notes |", "|---|---|---|---|---|"]
    lines += [f"| {r['file']} | {r['qty']} | {r['material']} | {r['finish']} | {r['notes']} |" for r in rows]
    lines += ["", "Not included:"] + [f"- {a}: {b}" for a, b in EXCLUDED]
    (OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(rows)} STEP files, {n_pcs} pieces -> {OUT}")


if __name__ == "__main__":
    main()
