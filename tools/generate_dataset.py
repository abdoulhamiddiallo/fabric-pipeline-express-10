"""Génère la production horaire du 21 octobre 2026 de quatre centrales solaires marocaines (données fictives).

Un CSV par centrale dans data/landing : ts, ghi_wm2 (irradiance globale, W/m²), mwh (énergie produite dans l'heure).
Le nom de la centrale n'est que dans le nom du fichier : c'est la colonne supplémentaire de la copie qui le retrouve.
"""
import csv, math, random
from pathlib import Path

random.seed(1021)
OUT = Path(__file__).resolve().parent.parent / "data" / "landing"
OUT.mkdir(parents=True, exist_ok=True)
DAY = "2026-10-21"

PLANTS = [
    # code, capacité retenue (MW), irradiance de crête (W/m²), rendement de référence, lever, coucher
    ("noor_ouarzazate", 72, 890, 0.82, 7.4, 18.9),
    ("noor_midelt", 600, 840, 0.80, 7.3, 18.8),
    ("noor_laayoune", 85, 820, 0.81, 7.9, 19.3),
    ("noor_boujdour", 20, 760, 0.61, 8.0, 19.4),   # vent de sable : panneaux encrassés
]

for code, cap, peak, pr, rise, sset in PLANTS:
    rows = []
    for h in range(24):
        t = h + 0.5
        if rise < t < sset:
            ghi = peak * math.sin(math.pi * (t - rise) / (sset - rise)) ** 1.3
            ghi *= random.uniform(0.93, 1.0)
        else:
            ghi = 0.0
        ghi = int(round(ghi))
        mwh = round(cap * ghi / 1000 * pr * random.uniform(0.97, 1.03), 1)
        rows.append({"ts": f"{DAY} {h:02d}:00:00", "ghi_wm2": ghi, "mwh": mwh})
    with open(OUT / f"{code}_{DAY}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["ts", "ghi_wm2", "mwh"])
        w.writeheader(); w.writerows(rows)
print("4 fichiers écrits dans", OUT)
