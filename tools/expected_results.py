"""Recalcule ce que NB_Noor doit écrire dans plant_scores et renvoyer au pipeline."""
import csv, json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

LANDING = Path(__file__).resolve().parent.parent / "data" / "landing"
PLANTS = {"noor_ouarzazate": ("Noor Ouarzazate", 72), "noor_midelt": ("Noor Midelt", 600),
          "noor_laayoune": ("Noor Laâyoune", 85), "noor_boujdour": ("Noor Boujdour", 20)}
r = lambda x, n: float(Decimal(repr(x)).quantize(Decimal(1).scaleb(-n), rounding=ROUND_HALF_UP))
rows = []
for code, (name, cap) in PLANTS.items():
    data = list(csv.DictReader(open(LANDING / f"{code}_2026-10-21.csv", encoding="utf-8")))
    mwh = r(sum(float(d["mwh"]) for d in data), 1)
    ghi = sum(float(d["ghi_wm2"]) for d in data)
    peak = max(float(d["mwh"]) for d in data)
    rows.append((name, cap, mwh, r(100 * mwh / (cap * 24), 1), r(mwh / (cap * ghi / 1000), 2), ghi, peak))
rows.sort(key=lambda x: -x[3])
for x in rows:
    print(f"{x[0]:16} {x[1]:4} MW  {x[2]:8} MWh  CF {x[3]:5} %  PR {x[4]:.2f}  {'alerte' if x[4] < 0.75 else 'ok'}  GHI {x[5]:.0f} Wh/m²  pointe {x[6]} MWh")
alerts = [x[0] for x in rows if x[4] < 0.75]
print(json.dumps({"day": "2026-10-21", "plants": 4, "total_mwh": round(sum(x[2] for x in rows), 1), "best": rows[0][0],
                  "best_cf": rows[0][3], "alerts": len(alerts), "alert_plants": ", ".join(alerts) or "aucune"}, ensure_ascii=False))
