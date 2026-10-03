"""
Budgetary machining-cost estimate for every custom metal part (balance, roll spindle, pitch sector, yaw carriage,
calibration hardware), quantity 1 set, for four kinds of supplier:

  CN   - China online platforms (JLCCNC at the low end, RapidDirect at the high end)
  SCS  - SendCutSend CNC (6061-T6 only, parts within 7 x 7 x 12 in, +-.005 in): only the parts it can make
  US   - US online marketplaces (Xometry, Protolabs Network/Hubs US)
  SHOP - local / university machine shop at a shop rate (no marketplace margin)

Method (per part): stock from the CAD bounding box (plate rounded up to a stock thickness, bar to a stock diameter)
-> material cost; roughing time = removed volume / metal-removal rate; plus feature time, setups, programming,
special operations (wire EDM, grinding, gun drilling, gear teeth) and inspection hours set from the drawing
tolerances; then hours x rate + material + finishing (+ shipping/duties for CN). Each result is a LOW..HIGH range.

THIS IS NOT A QUOTE. Accuracy is roughly +-40 %. Get real quotes by uploading the STEP + PDF drawing of each part
(see the RFQ notes printed at the end). Rates and prices are 2026 assumptions stated below.

Run (from analysis/):  ..\\.venv\\Scripts\\python machining_cost_estimate.py      -> machining_cost_estimate.csv / .json
"""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad"
HERE = Path(__file__).resolve().parent

# ------------------------------------------------------------------ assumptions (USD, 2026)
MAT = {  # density lb/in^3, $/lb for small cut pieces (low, high), metal-removal rate in^3/min (job-shop average)
    "6061-T6": dict(rho=0.0975, usd=(8, 14), mrr=2.5),
    "7075-T651": dict(rho=0.101, usd=(15, 26), mrr=2.5),
    "4140 PH": dict(rho=0.284, usd=(6, 12), mrr=0.5),
    "steel": dict(rho=0.284, usd=(4, 8), mrr=0.6),
}
RATE = {  # $/h (low, high) for milling / turning / wire EDM / grinding; programming at the milling rate
    # CN calibrated 2026-10-03 to the real JLCCNC instant quote (34 lines, analysis/jlccnc_quote_2026-10-03.json):
    # with these values the quote falls inside the low..high range for 16 of the 22 comparable 6061 parts.
    "CN": dict(mill=(10, 20), turn=(10, 20), edm=(20, 40), grind=(30, 55)),
    "SCS": dict(mill=(40, 70), turn=None, edm=None, grind=None),
    "US": dict(mill=(95, 150), turn=(85, 130), edm=(100, 150), grind=(100, 150)),
    "SHOP": dict(mill=(65, 105), turn=(60, 95), edm=(80, 120), grind=(80, 120)),
}
MAT_FACTOR = {"CN": 0.45, "SCS": 1.0, "US": 1.15, "SHOP": 1.0}      # material price relative to US small-lot price
PROG_FACTOR = {"CN": 0.2, "SCS": 0.25, "US": 1.0, "SHOP": 1.0}     # SCS: automated quoting / CAM for simple parts
FINISH = {  # per part number (lot charge) + per piece, (low, high)
    "anodize": {"CN": ((0, 0), (4, 15)), "SCS": ((0, 0), (6, 20)), "US": ((45, 90), (4, 12)), "SHOP": ((60, 120), (3, 8))},
    "black oxide": {"CN": ((0, 0), (3, 10)), "SCS": None, "US": ((40, 80), (3, 10)), "SHOP": ((50, 100), (3, 8))},
    "none": {k: ((0, 0), (0, 0)) for k in RATE},
}
# Shipping (to a US address), researched 2026-10:
#  CN: DDP express (DHL/UPS/FedEx) $8-15 per chargeable kg (max of actual and volumetric = L*W*H cm / 5000);
#      US duty pre-collected by JLCCNC on the goods value: aluminium CNC 90 %, steel 80 % (10 % provisional + 25 %
#      Sec. 301 + 50 % Sec. 232 + 0-7.5 % HS), not refunded in the 55-110 % band. Plus ~$25 formal-entry fees.
#  SCS: free US shipping over $39.   US: Xometry free standard US shipping; Protolabs Network price includes shipping.
#  SHOP: local pickup.
CN_SHIP_PER_KG = (8, 15)
CN_DUTY = {"6061-T6": 0.90, "7075-T651": 0.90, "4140 PH": 0.80, "steel": 0.80}
CN_ENTRY = 25
PACK = 1.25                  # packaging weight factor; box = envelope + 2 in each way
STOCK_T = [0.125, 0.188, 0.25, 0.375, 0.5, 0.625, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0]


# ------------------------------------------------------------------ parts
# step: CAD path; qty; mat; form: plate | bar | tube | none; tol: std | prec | ultra;
# feat: holes/taps/slots count; setups; prog: CAM hours (qty 1); extra: {"edm": h, "grind": h, "turn": h, "insp": h,
# "gundrill": h, "mill": h}; fin: finish; scs: SendCutSend eligible (6061, <= 7x7x12, tolerances >= +-.005)
P = [
    # --- balance and model interface
    dict(dwg="WT-6C-001", name="Balance, 6-component", step="six_component_balance/balance_6c_7075.step", qty=1,
         mat="7075-T651", form="bar", tol="ultra", feat=14, setups=4, prog=4.0, fin="none", scs=False,
         extra=dict(edm=6.0, insp=2.0, mill=1.0),
         note="wire EDM necks/flexures (rough + 2 skims), +-.0005 sections, CMM report; the cost driver"),
    dict(dwg="WT-6C-002", name="Puck, model interface", step="six_component_balance/model_puck_6061.step", qty=1,
         mat="6061-T6", form="bar", tol="prec", feat=8, setups=2, prog=1.0, fin="anodize", scs=False,
         extra=dict(turn=0.4), note="dowel holes +.0005; flatness .0005 is beyond SendCutSend"),
    dict(dwg="WT-6C-003", name="Sting", step="six_component_balance/sting_4140.step", qty=1,
         mat="4140 PH", form="bar", tol="ultra", feat=6, setups=3, prog=2.0, fin="black oxide", scs=False,
         extra=dict(turn=1.2, gundrill=2.0, grind=1.5, insp=0.75),
         note="0.300 bore x 17 in = gun drilling (or start from DOM/honed tube); OD ground, straightness .002"),
    # --- roll spindle
    dict(dwg="WT-6C-201", name="Spindle, roll", step="roll_spindle/spindle_4140.step", qty=1, mat="4140 PH",
         form="bar", tol="ultra", feat=10, setups=4, prog=3.0, fin="black oxide", scs=False,
         extra=dict(turn=1.8, grind=1.5, edm=1.0, insp=0.75),
         note="35 k5 seats ground; D-D bore by wire EDM; M35x1.5 thread; keyway"),
    dict(dwg="WT-6C-202", name="Housing, roll spindle", step="roll_spindle/housing_6061.step", qty=1, mat="6061-T6",
         form="bar", tol="prec", feat=22, setups=4, prog=2.5, fin="anodize", scs=False,
         extra=dict(insp=0.75), note="55 H7 bores line-bored in one setup (runout .0005)"),
    dict(dwg="WT-6C-203-1", name="Cap, front", step="roll_spindle/front_cap_6061.step", qty=1, mat="6061-T6",
         form="plate", tol="prec", feat=5, setups=2, prog=0.75, fin="anodize", scs=False, extra=dict(turn=0.3)),
    dict(dwg="WT-6C-203-2", name="Cap, rear", step="roll_spindle/rear_cap_6061.step", qty=1, mat="6061-T6",
         form="plate", tol="prec", feat=5, setups=2, prog=0.5, fin="anodize", scs=False, extra=dict(turn=0.3)),
    dict(dwg="WT-6C-204", name="Adapter, gearbox", step="roll_spindle/gearbox_adapter_6061.step", qty=1,
         mat="6061-T6", form="plate", tol="std", feat=8, setups=2, prog=0.75, fin="anodize", scs=True),
    dict(dwg="WT-6C-205", name="Bracket, roll encoder", step="roll_spindle/encoder_bracket.step", qty=1,
         mat="6061-T6", form="plate", tol="std", feat=7, setups=1, prog=0.5, fin="anodize", scs=True),
    # --- calibration hardware
    dict(dwg="WT-6C-301", name="Sleeve, calibration", step="calibration_6c/sleeve_6c_6061.step", qty=1,
         mat="6061-T6", form="bar", tol="prec", feat=45, setups=5, prog=2.0, fin="anodize", scs=False,
         extra=dict(insp=0.5), note="20 reamed load holes (pos .001) + 20 corner grooves"),
    dict(dwg="WT-6C-302", name="Arm, roll calibration", step="calibration_6c/roll_arm_6061.step", qty=1,
         mat="6061-T6", form="plate", tol="std", feat=10, setups=2, prog=0.75, fin="anodize", scs=True),
    dict(dwg="WT-6C-303", name="Stirrup, 45 deg", step="calibration_6c/stirrup_45_6061.step", qty=1,
         mat="6061-T6", form="plate", tol="std", feat=4, setups=2, prog=0.75, fin="anodize", scs=True),
    dict(dwg="WT-6C-304", name="Yoke, calibration", step="calibration_6c/yoke_6c_6061.step", qty=1, mat="6061-T6",
         form="bar", tol="std", feat=5, setups=3, prog=0.75, fin="anodize", scs=True),
    dict(dwg="WT-6C-305", name="Plate, head, cal. stand", step="calibration_6c/head_plate_v2_6061.step", qty=2,
         mat="6061-T6", form="plate", tol="std", feat=12, setups=1, prog=0.75, fin="anodize", scs=False,
         note="16.15 in long: over the SendCutSend 12 in limit"),
    dict(dwg="WT-6C-306-1", name="Bridge, jack", step="calibration_6c/jack_bridge_v2_6061.step", qty=1,
         mat="6061-T6", form="bar", tol="std", feat=5, setups=2, prog=0.4, fin="anodize", scs=True),
    dict(dwg="WT-6C-306-2", name="Spacer, cross", step="calibration_6c/cross_spacer_6061.step", qty=2,
         mat="6061-T6", form="bar", tol="std", feat=3, setups=2, prog=0.3, fin="anodize", scs=True),
    dict(dwg="WT-6C-307", name="Tube, base, cal. stand", step="calibration_6c/base_tube_v2.step", qty=1,
         mat="6061-T6", form="tube", tol="std", feat=18, setups=2, prog=0.5, fin="none", scs=False,
         note="cut + drill purchased 3x1.5x.125 tube (31 in)"),
    dict(dwg="WT-6C-308/309/310", name="Uprights (4), axles (2), pulleys (3)", step=None, qty=1, mat="6061-T6",
         form="none", tol="std", feat=24, setups=6, prog=1.5, fin="anodize", scs=True, stock_lb=2.4, rough_h=1.1,
         note="pulley uprights, axles (5/16 ground rod) and 2 in pulleys with R5-2Z bearings"),
    # --- pitch sector
    dict(dwg="WT-6C-401", name="Cheek, pitch sector", step="pitch_sector_motorized/cheek_plus_y.step", qty=2,
         mat="6061-T6", form="plate", tol="prec", feat=8, setups=2, prog=1.5, fin="anodize", scs=False,
         extra=dict(insp=0.5), note="arc track slots profile .002; machine both stacked"),
    dict(dwg="WT-6C-402", name="Rack plate, pitch", step="pitch_sector_motorized/rack_plate.step", qty=1,
         mat="6061-T6", form="plate", tol="prec", feat=3, setups=2, prog=1.5, fin="anodize", scs=False,
         extra=dict(edm=2.5, insp=0.5), note="~87 internal teeth m1.25 by wire EDM"),
    dict(dwg="WT-6C-403", name="Plate, base, pitch", step="pitch_sector_motorized/base_plate.step", qty=1,
         mat="6061-T6", form="plate", tol="std", feat=12, setups=2, prog=0.75, fin="anodize", scs=False,
         note="0.75 in plate, 9.2 x 5.7 in; flat .002 is tighter than SCS"),
    dict(dwg="WT-6C-404-1", name="Tie, top", step="pitch_sector_motorized/top_tie.step", qty=1, mat="6061-T6",
         form="bar", tol="std", feat=4, setups=2, prog=0.5, fin="anodize", scs=True),
    dict(dwg="WT-6C-404-2/3", name="Spacers, pitch", step="pitch_sector_motorized/spacer0.step", qty=2,
         mat="6061-T6", form="bar", tol="std", feat=2, setups=2, prog=0.3, fin="anodize", scs=True),
    dict(dwg="WT-6C-405", name="Bracket, pitch drive", step="pitch_sector_motorized/drive_bracket_6061.step", qty=1,
         mat="6061-T6", form="bar", tol="prec", feat=6, setups=2, prog=0.75, fin="anodize", scs=False,
         note="22 H7 bearing bore"),
    dict(dwg="WT-6C-406", name="Pinion shaft (gear bought)", step=None, qty=1, mat="4140 PH", form="none",
         tol="prec", feat=3, setups=2, prog=0.5, fin="none", scs=False, stock_lb=0.3, rough_h=0.2,
         extra=dict(turn=0.6, grind=0.3), note="8 h6 ground shaft + rebore/pin the stock m1.25 20T gear"),
    # --- yaw carriage (preliminary: bay dimensions to confirm)
    dict(dwg="WT-6C-501", name="Rail, yaw, inner", step="yaw_carriage/rail_inner.step", qty=1, mat="6061-T6",
         form="plate", tol="prec", feat=11, setups=3, prog=1.5, fin="anodize", scs=False,
         extra=dict(mill=0.75), note="V-edges on both arcs (hard anodize preferred)"),
    dict(dwg="WT-6C-502", name="Rail, yaw, outer", step="yaw_carriage/rail_outer.step", qty=1, mat="6061-T6",
         form="plate", tol="prec", feat=12, setups=3, prog=1.5, fin="anodize", scs=False, extra=dict(mill=1.0)),
    dict(dwg="WT-6C-503", name="Rack, yaw, floor", step="yaw_carriage/floor_rack.step", qty=1, mat="6061-T6",
         form="plate", tol="prec", feat=3, setups=2, prog=1.5, fin="anodize", scs=False,
         extra=dict(edm=2.5, insp=0.5), note="~80 external teeth m1.25 by wire EDM"),
    dict(dwg="WT-6C-504", name="Plate, yaw carriage", step="yaw_carriage/carriage_plate_6061.step", qty=1,
         mat="6061-T6", form="plate", tol="std", feat=17, setups=2, prog=1.25, fin="anodize", scs=False,
         note="~11 x 18 in sector plate"),
    dict(dwg="WT-6C-505", name="Pinion mods, yaw (gear bought)", step=None, qty=1, mat="steel", form="none",
         tol="prec", feat=2, setups=1, prog=0.3, fin="none", scs=False, stock_lb=0.0, rough_h=0.0,
         extra=dict(turn=0.5), note="rebore + keyway/set screw on a stock m1.25 20T gear"),
    dict(dwg="WT-6C-506", name="Spacers, wheel (plain + eccentric)", step=None, qty=8, mat="6061-T6", form="none",
         tol="std", feat=1, setups=1, prog=0.3, fin="anodize", scs=True, stock_lb=0.04, rough_h=0.0,
         extra=dict(turn=0.15)),
]


# ------------------------------------------------------------------ geometry
def geom(step):
    import cadquery as cq
    s = cq.importers.importStep(str(CAD / step)).val()
    k = 1 / 25.4
    bb = s.BoundingBox()
    dims = sorted([bb.xlen * k, bb.ylen * k, bb.zlen * k])
    return dims, s.Volume() * k ** 3


def stock(form, dims):
    t, w, l = dims
    if form == "plate":
        tt = next((x for x in STOCK_T if x >= t - 1e-3), t)
        return tt * (w + 0.25) * (l + 0.25)
    if form == "bar":
        return (t + 0.125) * (w + 0.125) * (l + 0.25)
    return t * w * l * 0.25   # tube: material is the tube itself (approximate as 25 % of the envelope)


def rng(a, b):
    return [round(a), round(b)]


def estimate():
    rows = []
    tot = {k: [0.0, 0.0] for k in RATE}
    finish_lots = {k: set() for k in RATE}
    for p in P:
        q = p["qty"]
        m = MAT[p["mat"]]
        if p["step"]:
            dims, vol = geom(p["step"])
            vs = stock(p["form"], dims)
            removal = max(vs - vol, 0.0) if p["form"] != "tube" else 0.2
            stock_lb = vs * m["rho"]
            rough_h = removal / m["mrr"] / 60
        else:
            dims, vol = [0, 0, 0], 0
            stock_lb, rough_h = p.get("stock_lb", 0.2), p.get("rough_h", 0.2)
        ex = p.get("extra", {})
        tolf = {"std": 1.0, "prec": 1.3, "ultra": 1.6}[p["tol"]]
        setup_h = 0.4 * p["setups"]                       # per batch
        run_mill = (rough_h + p["feat"] * 1.5 / 60 + 0.15 + ex.get("mill", 0)) * tolf   # per piece
        per_piece = dict(mill=run_mill, turn=ex.get("turn", 0), edm=ex.get("edm", 0),
                         grind=ex.get("grind", 0) + ex.get("gundrill", 0))
        insp = ex.get("insp", 0) + (0.25 if p["tol"] == "prec" else 0)
        out = dict(dwg=p["dwg"], name=p["name"], qty=q, material=p["mat"], tol=p["tol"],
                   envelope_in=" x ".join(f"{d:.2f}" for d in dims), part_lb=round(vol * m["rho"], 2),
                   stock_lb=round(stock_lb, 2), note=p.get("note", ""), scs_ok=p["scs"])
        hrs = setup_h + p["prog"] + insp + q * sum(per_piece.values())
        lb = (vol * m["rho"] if p["step"] else max(p.get("stock_lb", 0.1) * 0.6, 0.05)) * q
        box = [d + 2 for d in dims] if p["step"] else [4, 4, 3]
        vol_kg = q * box[0] * box[1] * box[2] * 16.387 / 5000 if p["step"] else 0.2 * q
        out["ship_kg"] = round(max(lb * 0.4536 * PACK, vol_kg if max(box) < 30 else vol_kg * 1.0), 2)
        out["hours"] = round(hrs, 1)
        for v, rate in RATE.items():
            if v == "SCS" and not p["scs"]:
                out[v] = None
                continue
            lo = hi = 0.0
            for i, (a) in enumerate((0, 1)):
                r = rate
                c = (setup_h + p["prog"] * PROG_FACTOR[v] + insp) * r["mill"][a]
                for op, h in per_piece.items():
                    if h:
                        rr = r[op] if r.get(op) else r["mill"]
                        c += q * h * rr[a]
                c += q * stock_lb * m["usd"][a] * MAT_FACTOR[v]
                fin = FINISH[p["fin"]][v] if FINISH[p["fin"]].get(v) else ((0, 0), (0, 0))
                c += q * fin[1][a]
                if fin[0][a]:
                    finish_lots[v].add((p["fin"], fin[0][0], fin[0][1]))
                if a == 0:
                    lo = c
                else:
                    hi = c
            out[v] = rng(lo, hi)
            tot[v][0] += lo
            tot[v][1] += hi
        rows.append(out)
    # finish lot charges: US/SHOP anodizers batch all parts in one lot per finish type
    for v in ("US", "SHOP"):
        for fin in {f[0] for f in finish_lots[v]}:
            lot = FINISH[fin][v][0]
            tot[v][0] += lot[0]
            tot[v][1] += lot[1]
    # CN: duty on each part's goods value + DDP express freight on the chargeable weight of the order
    tot["CN"] = [0.0, 0.0]
    for r in rows:
        d = CN_DUTY[r["material"]]
        r["CN_landed"] = rng(r["CN"][0] * (1 + d), r["CN"][1] * (1 + d))
        tot["CN"][0] += r["CN_landed"][0]
        tot["CN"][1] += r["CN_landed"][1]
    kg = cn_kg(rows)
    ship = [kg * CN_SHIP_PER_KG[0] + CN_ENTRY, kg * CN_SHIP_PER_KG[1] + CN_ENTRY]
    tot["CN"] = [tot["CN"][0] + ship[0], tot["CN"][1] + ship[1]]
    totals = {k: rng(*v) for k, v in tot.items()}
    totals["CN_ship"] = rng(*ship)
    totals["CN_kg"] = round(kg, 1)
    return rows, totals


def cn_kg(rows):
    return sum(r["ship_kg"] for r in rows)


def mixed(rows):
    """Recommended split: precision/EDM/steel parts at a US supplier (or a local shop), 6061 parts that fit at
    SendCutSend, the remaining 6061 parts at the cheapest of CN (with duties) or US."""
    lo = hi = 0.0
    plan = []
    cn_rows = []
    for r in rows:
        if r["tol"] == "ultra" or r["material"] != "6061-T6" or r["dwg"] in BEARING_FITS:
            v = "US"            # wire EDM / grinding / bearing fits: US marketplace (or a local shop)
        elif r["scs_ok"]:
            v = "SCS"           # simple 6061 that fits 7 x 7 x 12 in, free shipping
        else:
            v = "CN"            # large or medium-precision 6061 plates: RapidDirect / JLCCNC (+-.001-.002)
        c = r["CN_landed"] if v == "CN" else r[v]
        if v == "CN":
            cn_rows.append(r)
        lo += c[0]
        hi += c[1]
        plan.append((r["dwg"], r["name"], v))
    kg = cn_kg(cn_rows)
    ship = (kg * CN_SHIP_PER_KG[0] + CN_ENTRY, kg * CN_SHIP_PER_KG[1] + CN_ENTRY) if cn_rows else (0, 0)
    return plan, rng(lo + ship[0], hi + ship[1]), rng(*ship)


BEARING_FITS = ("WT-6C-202", "WT-6C-203-1", "WT-6C-203-2", "WT-6C-405", "WT-6C-002")


if __name__ == "__main__":
    rows, tot = estimate()
    with open(HERE / "machining_cost_estimate.csv", "w", newline="") as f:
        cols = ["dwg", "name", "qty", "material", "tol", "envelope_in", "part_lb", "stock_lb", "ship_kg", "hours", "CN",
                "CN_landed", "SCS",
                "US", "SHOP", "scs_ok", "note"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{r[k][0]}-{r[k][1]}" if isinstance(r.get(k), list) else r.get(k)) for k in cols})
    plan, mix, mix_ship = mixed(rows)
    json.dump(dict(rows=rows, totals=tot, mixed=mix, mixed_cn_ship=mix_ship, plan=plan,
                   assumptions=dict(rates=RATE, material=MAT, cn_ship_per_kg=CN_SHIP_PER_KG, cn_duty=CN_DUTY)),
              open(HERE / "machining_cost_estimate.json", "w"), indent=1)
    print(f"{'DWG':12s} {'PART':36s} {'QTY':>3s} {'HRS':>5s} {'CN $':>11s} {'SCS $':>11s} {'US $':>11s} {'SHOP $':>11s}")
    for r in rows:
        f = lambda v: f"{v[0]}-{v[1]}" if v else "-"   # noqa: E731
        print(f"{r['dwg']:12s} {r['name'][:36]:36s} {r['qty']:3d} {r['hours']:5.1f} {f(r['CN']):>11s} "
              f"{f(r['SCS']):>11s} {f(r['US']):>11s} {f(r['SHOP']):>11s}")
    print("\nTOTALS, one complete set (USD):")
    print(f"  CN (JLCCNC..RapidDirect), landed: 80-90 % duty + DDP express {tot['CN_kg']} kg chargeable "
          f"(${tot['CN_ship'][0]}-{tot['CN_ship'][1]}): {tot['CN'][0]:,}-{tot['CN'][1]:,}")
    print(f"  US marketplace (Xometry / Hubs US), shipping free/included: {tot['US'][0]:,}-{tot['US'][1]:,}")
    print(f"  Local / university shop at shop rate (pickup):         {tot['SHOP'][0]:,}-{tot['SHOP'][1]:,}")
    print(f"  SendCutSend can make only the {sum(r['scs_ok'] for r in rows)} simple 6061 parts: "
          f"{tot['SCS'][0]:,}-{tot['SCS'][1]:,}")
    print(f"  Recommended split (US: precision/EDM/steel/bearing fits; SCS: simple 6061; CN: large 6061), "
          f"incl. CN freight ${mix_ship[0]}-{mix_ship[1]} + duties: {mix[0]:,}-{mix[1]:,}")
    for d, n, v in plan:
        print(f"    {d:12s} {n[:40]:40s} -> {v}")
