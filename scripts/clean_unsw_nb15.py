"""Clean the raw UNSW-NB15 CSVs (UNSW-NB15_1..4.csv) into parquet.

Run from the datasets folder:  python scripts/clean_unsw_nb15.py
See unsw-nb15/NOTES.md for what each step fixes and why.
"""
import glob
from pathlib import Path

import pandas as pd

SRC = Path("unsw-nb15")
OUT = SRC / "clean"
OUT.mkdir(exist_ok=True)

# 1. Column names come from the features file (raw CSVs have no header).
#    Normalise: lowercase, remove stray spaces ("ct_src_ ltm" -> "ct_src_ltm").
feat = pd.read_csv(SRC / "NUSW-NB15_features.csv", encoding="latin-1")
names = [n.strip().replace(" ", "").lower() for n in feat["Name"]]

# 2. Read everything as text first; utf-8-sig strips the BOM on file 1.
#    (Files are ASCII apart from the BOM, so this is equivalent to latin-1.)
files = sorted(glob.glob(str(SRC / "UNSW-NB15_[1-4].csv")))
df = pd.concat(
    [pd.read_csv(f, header=None, names=names, dtype=str, keep_default_na=False,
                 encoding="utf-8-sig") for f in files],
    ignore_index=True,
)
n_raw = len(df)


# 3. Ports: a few are hex strings ("0x000b") or "-". Hex -> int, "-" -> -1.
def parse_port(s):
    s = s.strip()
    if s in ("", "-"):
        return -1
    return int(s, 16) if s.lower().startswith("0x") else int(s)


for c in ("sport", "dsport"):
    df[c] = df[c].map(parse_port).astype("int64")

# 4. Blank counters (empty / single space) mean "not an HTTP/FTP flow" -> 0.
for c in ("ct_flw_http_mthd", "is_ftp_login", "ct_ftp_cmd"):
    df[c] = df[c].str.strip().replace("", "0")

# 5. is_ftp_login is documented as binary but contains 2 and 4 -> clip to 0/1.
df["is_ftp_login"] = (df["is_ftp_login"].astype(int) > 0).astype("int8")

# 6. attack_cat: strip whitespace, merge "Backdoors" into "Backdoor",
#    blank -> "Normal" (blank rows are exactly the label==0 rows).
df["attack_cat"] = (df["attack_cat"].str.strip()
                    .replace({"Backdoors": "Backdoor", "": "Normal"}))

# 7. Cast numerics using the types listed in the features file.
nominal = {"srcip", "dstip", "proto", "state", "service", "attack_cat"}
for c in df.columns:
    if c in nominal or c in ("sport", "dsport", "is_ftp_login"):
        continue
    df[c] = pd.to_numeric(df[c])  # raises if anything unexpected is left
for c in nominal:
    df[c] = df[c].astype("category")
df["label"] = df["label"].astype("int8")

assert df.isna().sum().sum() == 0
assert ((df["attack_cat"] == "Normal") == (df["label"] == 0)).all()

df.to_parquet(OUT / "unsw_nb15_full.parquet", index=False)

# 8. Deduplicated copy (exact duplicates over all 49 columns).
dedup = df.drop_duplicates(ignore_index=True)
dedup.to_parquet(OUT / "unsw_nb15_full_dedup.parquet", index=False)

# 9. Official train/test split files: already clean; just re-save as parquet.
for split in ("training", "testing"):
    t = pd.read_csv(SRC / f"UNSW_NB15_{split}-set.csv")
    assert t.isna().sum().sum() == 0
    t.to_parquet(OUT / f"unsw_nb15_{split}_set.parquet", index=False)

print(f"raw rows            : {n_raw:,}")
print(f"full (cleaned)      : {len(df):,}")
print(f"full dedup          : {len(dedup):,}  (removed {len(df) - len(dedup):,})")
print("attack_cat (full):\n", df["attack_cat"].value_counts().to_string())
print("attack_cat (dedup):\n", dedup["attack_cat"].value_counts().to_string())
