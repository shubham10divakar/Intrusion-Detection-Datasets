# CIC-IDS-2017: notes

**Source:** Kaggle [`dhoogla/cicids2017`](https://www.kaggle.com/datasets/dhoogla/cicids2017) (CC BY-NC-SA 4.0), downloaded 2026-10-03 with the Kaggle CLI.
Official source to cite: Sharafaldin, Lashkari & Ghorbani, "Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization", ICISSP 2018 (UNB CIC).

**Cleaning script:** `scripts/clean_cicids2017.py`. Run it from the `datasets` folder.

## What this Kaggle copy already did (before the cleaning script)

The dhoogla copy is **not** the raw `MachineLearningCSV` release. The uploader had already:
- converted the files to parquet, one file per day/attack and 8 files in total, with compact dtypes;
- removed metadata columns (Flow ID, IPs, ports, timestamp) and the duplicated `Fwd Header Length.1` column. 77 features remain, plus `Label`;
- removed NaN/inf rows and duplicates **within each file**.

That's why the copy has 2,313,810 rows instead of the ~2.83M in the original CSVs. If you need to match papers that used the raw CSVs, get `MachineLearningCSV.zip` from the UNB CIC site.

## Files

| File | What it is |
|---|---|
| `*-no-metadata.parquet` (8 files) | Kaggle copy, one file per capture day/attack. **Not modified.** |
| `clean/cicids2017_clean.parquet` | **All days combined and cleaned: 2,228,430 rows, 69 features + 4 label/meta columns** |

## Problems found and how they were fixed (in order)

| # | Problem | Fix | Rows affected |
|---|---|---|---:|
| 1 | Web Attack labels are mojibake (`Web Attack � Brute Force`; the original had an en-dash) | Replaced with `-`, e.g. `Web Attack - Brute Force` | 2,143 labels |
| 2 | 8 columns are constant (always 0) across the whole dataset: `Bwd PSH Flags`, `Bwd URG Flags`, `Fwd/Bwd Avg Bytes/Bulk`, `Fwd/Bwd Avg Packets/Bulk`, `Fwd/Bwd Avg Bulk Rate` | Dropped, leaving **69 features** | – |
| 3 | NaN / inf values | Checked; none in this copy | 0 |
| 4 | Impossible negative values from CICFlowMeter bugs: negative `Flow Duration` / IAT (clock skew), and huge negative `Fwd/Bwd Header Length`, `Fwd Seg Size Min` (integer overflow) | Rows dropped. **Exception:** `Init Fwd/Bwd Win Bytes = -1` is a valid "no window seen" marker and was kept | 2,843 |
| 5 | Exact duplicates **across** day files (the uploader only deduplicated within a file) | Dropped, keeping the first occurrence | 81,997 |
| 6 | Identical feature vectors with **different** labels (ambiguous) | All copies dropped | 540 |

There are no NaN, inf or invalid negative values left.

## Added columns

- `Label`: the original fine-grained label (15 classes, including Benign)
- `Attack Family`: Benign, DoS (Hulk, GoldenEye, slowloris, Slowhttptest, Heartbleed), DDoS, PortScan, BruteForce (FTP-/SSH-Patator), WebAttack (Brute Force, XSS, SQL Injection), Botnet, Infiltration
- `Label Binary`: 0 = Benign, 1 = attack
- `Day`: which source file the row came from (e.g. `DoS-Wednesday`)

## Final class counts

| Label | Rows |
|---|---:|
| Benign | 1,892,401 |
| DoS Hulk | 172,554 |
| DDoS | 127,992 |
| DoS GoldenEye | 10,281 |
| FTP-Patator | 5,927 |
| DoS slowloris | 5,383 |
| DoS Slowhttptest | 5,228 |
| SSH-Patator | 3,217 |
| PortScan | 1,850 |
| Web Attack - Brute Force | 1,470 |
| Bot | 1,412 |
| Web Attack - XSS | 652 |
| Infiltration | 35 |
| Web Attack - Sql Injection | 21 |
| Heartbleed | 7 |

## Facts worth knowing

- **Extreme imbalance:** Heartbleed (7), SQL Injection (21) and Infiltration (35) are too small for a meaningful per-class test score. Most papers merge them into families (use `Attack Family`) or leave them out of multi-class results. Heartbleed lost 4 of its 11 rows in step 4 because of overflowed header lengths.
- Web Attack Brute Force and XSS are known to be nearly indistinguishable by flow features.
- The features are on very different scales (bytes/s goes up to ~2e9), so scale them, e.g. log1p + standardisation, before training a neural model.
- No official train/test split exists. Use a stratified split, and fit any scaler on the training part only.
