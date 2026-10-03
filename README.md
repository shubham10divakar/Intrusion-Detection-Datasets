# IDS datasets

Downloaded and cleaned on 2026-10-03. The raw files were never modified. Every cleaned file lives in a `clean/` subfolder and can be rebuilt with the scripts in `scripts/`. Each dataset folder has a `NOTES.md` with the full details.

| Dataset | Use this file | Rows | Features | Labels | Notes |
|---|---|---:|---:|---|---|
| UNSW-NB15 | `unsw-nb15/clean/unsw_nb15_full_dedup.parquet` | 2,059,414 | 47 (incl. IPs/ports/times) | `attack_cat` (10), `label` | [NOTES](unsw-nb15/NOTES.md) |
| UNSW-NB15 (official split) | `unsw-nb15/clean/unsw_nb15_{training,testing}_set.parquet` | 82,332 / 175,341 | 42 | `attack_cat`, `label` | |
| CIC-IDS-2017 | `cicids2017/clean/cicids2017_clean.parquet` | 2,228,430 | 69 | `Label` (15), `Attack Family` (8), `Label Binary` | [NOTES](cicids2017/NOTES.md) |
| NSL-KDD | `nslkdd/clean/nslkdd_{train,test}.parquet` | 125,973 / 22,544 | 41 | `attack`, `attack_cat` (5), `label` | [NOTES](nslkdd/NOTES.md) |

`unsw-nb15/clean/unsw_nb15_full.parquet` (2,540,047 rows) is the cleaned UNSW-NB15 data **with** its duplicates, if you need the raw row count.

## Quick load

```python
import pandas as pd
unsw = pd.read_parquet("unsw-nb15/clean/unsw_nb15_full_dedup.parquet")
cic  = pd.read_parquet("cicids2017/clean/cicids2017_clean.parquet")
kdd_tr = pd.read_parquet("nslkdd/clean/nslkdd_train.parquet")
kdd_te = pd.read_parquet("nslkdd/clean/nslkdd_test.parquet")
```

Reading these files needs `pandas` and `pyarrow`.

## Rebuild

```powershell
python scripts/clean_unsw_nb15.py
python scripts/clean_cicids2017.py
python scripts/clean_nslkdd.py
```

## Re-download (Kaggle CLI, run once `kaggle auth login` is done)

```powershell
python -m kaggle datasets download -d mrwellsdavid/unsw-nb15 -p unsw-nb15 --unzip
python -m kaggle datasets download -d dhoogla/cicids2017   -p cicids2017 --unzip
python -m kaggle datasets download -d hassan06/nslkdd      -p nslkdd/original --unzip   # then delete the duplicate nsl-kdd/ subfolder
```

## Main decisions (summary)

- **UNSW-NB15:** fixed the header, BOM, hex/`-` ports, blank FTP/HTTP counters (set to 0), `is_ftp_login` values above 1, and messy `attack_cat` values (whitespace, Backdoors→Backdoor, blank→Normal). 480,633 exact duplicate rows were removed in the dedup file.
- **CIC-IDS-2017:** fixed the Web Attack label encoding and dropped 8 constant columns. Removed 2,843 rows with impossible negative values (CICFlowMeter bugs), 81,997 duplicates across day files, and 540 rows with conflicting labels.
- **NSL-KDD:** the Kaggle parquet copy was missing 5 of the 41 features, so the original `KDDTrain+` / `KDDTest+` text files were used instead. Added names, a 4-category attack mapping and a binary label.
