# NB_Noor : classe les centrales solaires du jour et renvoie un verdict au pipeline

# ===== Cellule 1 : cellule de paramètres (le pipeline remplace cette valeur) =====
day = "2026-10-21"

# ===== Cellule 2 : le calcul =====
import json, re
from pyspark.sql import functions as F

if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
    raise ValueError(f"Date invalide reçue du pipeline : {day}")

# capacité retenue pour l'exercice, en MW
PLANTS = {"noor_ouarzazate": ("Noor Ouarzazate", 72), "noor_midelt": ("Noor Midelt", 600),
          "noor_laayoune": ("Noor Laâyoune", 85), "noor_boujdour": ("Noor Boujdour", 20)}
ref = spark.createDataFrame([(k, n, float(c)) for k, (n, c) in PLANTS.items()], "code string, plant string, capacity_mw double")

raw = (spark.read.table("production_raw")
       .filter(F.col("load_day") == day)
       .withColumn("code", F.regexp_extract("source_file", r"(noor_[a-z]+)", 1))
       .withColumn("mwh", F.col("mwh").cast("double"))
       .withColumn("ghi", F.col("ghi_wm2").cast("double")))

scores = (raw.groupBy("code")
          .agg(F.round(F.sum("mwh"), 1).alias("mwh"), F.sum("ghi").alias("ghi_wh"))
          .join(ref, "code")
          .withColumn("capacity_factor_pct", F.round(100 * F.col("mwh") / (F.col("capacity_mw") * 24), 1))
          .withColumn("performance_ratio", F.round(F.col("mwh") / (F.col("capacity_mw") * F.col("ghi_wh") / 1000), 2))
          .withColumn("status", F.when(F.col("performance_ratio") < 0.75, "alerte").otherwise("ok"))
          .withColumn("day", F.lit(day))
          .select("day", "plant", "capacity_mw", "mwh", "capacity_factor_pct", "performance_ratio", "status"))
scores.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("plant_scores")

rows = scores.orderBy(F.desc("capacity_factor_pct")).collect()
alerts = [r["plant"] for r in rows if r["status"] == "alerte"]
verdict = {
    "day": day,
    "plants": len(rows),
    "total_mwh": round(sum(r["mwh"] for r in rows), 1),
    "best": rows[0]["plant"],
    "best_cf": rows[0]["capacity_factor_pct"],
    "alerts": len(alerts),
    "alert_plants": ", ".join(alerts) if alerts else "aucune",
}
print(verdict)
notebookutils.notebook.exit(json.dumps(verdict, ensure_ascii=False))
