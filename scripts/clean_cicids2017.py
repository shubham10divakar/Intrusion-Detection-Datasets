"""Clean the CIC-IDS-2017 day parquet files (Kaggle dhoogla/cicids2017).

Run from the datasets folder:  python scripts/clean_cicids2017.py
See cicids2017/NOTES.md for what each step fixes and why.
"""
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path("cicids2017")
OUT = SRC / "clean"
OUT.mkdir(exist_ok=True)

# 1. Load all days; keep the source day as a column.
parts = []
for f in sorted(SRC.glob("*-no-metadata.parquet")):
    d = pd.read_parquet(f)
    d["Label"] = d["Label"].astype(str)
    d["Day"] = f.stem.replace("-no-metadata", "")
    parts.append(d)
df = pd.concat(parts, ignore_index=True)
n_raw = len(df)
log = {}

# 2. Fix mojibake in Web Attack labels ("Web Attack � Brute Force").
df["Label"] = df["Label"].str.replace("�", "-", regex=False).str.strip()

# 3. Drop columns that are constant across the whole dataset.
const = [c for c in df.columns if df[c].nunique() <= 1]
df = df.drop(columns=const)
log["constant columns dropped"] = const

feats = [c for c in df.columns if c not in ("Label", "Day")]

# 4. Remove NaN / inf (none in this copy, kept as a safety net).
num = df[feats].select_dtypes("number")
bad = num.isna().any(axis=1) | np.isinf(num).any(axis=1)
log["rows with NaN/inf"] = int(bad.sum())
df = df[~bad]

# 5. Negative values are CICFlowMeter artefacts (clock skew, int overflow),
#    except Init Fwd/Bwd Win Bytes where -1 means "no window seen" -> keep.
allowed_neg = {"Init Fwd Win Bytes", "Init Bwd Win Bytes"}
chk = [c for c in feats if c not in allowed_neg and pd.api.types.is_numeric_dtype(df[c])]
neg = (df[chk] < 0).any(axis=1)
log["rows with invalid negative values"] = int(neg.sum())
df = df[~neg]

# 6. Exact duplicates across days (source was only deduplicated per day).
before = len(df)
df = df.drop_duplicates(subset=feats + ["Label"])
log["cross-day duplicate rows"] = before - len(df)

# 7. Identical feature vectors with different labels are ambiguous -> drop all.
amb = df.duplicated(subset=feats, keep=False)
log["rows with conflicting labels"] = int(amb.sum())
df = df[~amb].reset_index(drop=True)

# 8. Label columns: binary + attack family (common grouping in the literature).
family = {
    "Benign": "Benign",
    "DoS Hulk": "DoS", "DoS GoldenEye": "DoS", "DoS slowloris": "DoS",
    "DoS Slowhttptest": "DoS", "Heartbleed": "DoS",
    "DDoS": "DDoS",
    "PortScan": "PortScan",
    "FTP-Patator": "BruteForce", "SSH-Patator": "BruteForce",
    "Web Attack - Brute Force": "WebAttack", "Web Attack - XSS": "WebAttack",
    "Web Attack - Sql Injection": "WebAttack",
    "Bot": "Botnet",
    "Infiltration": "Infiltration",
}
assert set(df["Label"]) <= set(family), set(df["Label"]) - set(family)
df["Attack Family"] = df["Label"].map(family).astype("category")
df["Label Binary"] = (df["Label"] != "Benign").astype("int8")
df["Label"] = df["Label"].astype("category")
df["Day"] = df["Day"].astype("category")

df.to_parquet(OUT / "cicids2017_clean.parquet", index=False)

print(f"raw rows   : {n_raw:,}")
for k, v in log.items():
    print(f"{k:35s}: {v if isinstance(v, list) else f'{v:,}'}")
print(f"clean rows : {len(df):,}   features: {len(feats)}")
print(df["Label"].value_counts().to_string())
