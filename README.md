# IDS datasets

Downloaded and cleaned on 2026-10-03. The raw files were never modified. Every cleaned file lives in a `clean/` subfolder and can be rebuilt with the scripts in `scripts/`. Each dataset folder has a `NOTES.md` with the full details.

| Dataset | Use this file | Rows | Features | Labels | Notes |
|---|---|---:|---:|---|---|
| UNSW-NB15 | `unsw-nb15/clean/unsw_nb15_full_dedup.parquet` | 2,059,414 | 47 (incl. IPs/ports/times) | `attack_cat` (10), `label` | [NOTES](unsw-nb15/NOTES.md) |
| UNSW-NB15 (official split) | `unsw-nb15/clean/unsw_nb15_{training,testing}_set.parquet` | 82,332 / 175,341 | 42 | `attack_cat`, `label` | |
| CIC-IDS-2017 | `cicids2017/clean/cicids2017_clean.parquet` | 2,228,430 | 69 | `Label` (15), `Attack Family` (8), `Label Binary` | [NOTES](cicids2017/NOTES.md) |
| NSL-KDD | `nslkdd/clean/nslkdd_{train,test}.parquet` | 125,973 / 22,544 | 41 | `attack`, `attack_cat` (5), `label` | [NOTES](nslkdd/NOTES.md) |

`unsw-nb15/clean/unsw_nb15_full.parquet` (2,540,047 rows) is the cleaned UNSW-NB15 data **with** its duplicates, if you need the raw row count.

## Getting the data

All data files (raw and cleaned, about 1.5 GB) are stored in this repo with **Git LFS**. Install Git LFS before cloning:

```powershell
git lfs install
git clone https://github.com/shubham10divakar/Intrusion-Detection-Datasets.git
```

## Quick load

```python
import pandas as pd
unsw = pd.read_parquet("unsw-nb15/clean/unsw_nb15_full_dedup.parquet")
cic  = pd.read_parquet("cicids2017/clean/cicids2017_clean.parquet")
kdd_tr = pd.read_parquet("nslkdd/clean/nslkdd_train.parquet")
kdd_te = pd.read_parquet("nslkdd/clean/nslkdd_test.parquet")
```

Install the requirements with `pip install -r requirements.txt` (pandas, pyarrow and the Kaggle CLI).

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

## Licences and citations

The data in this repo is a **mirror** of third-party datasets. It is redistributed under each owner's terms, as summarised below. The data is **for academic research only**, and anyone using it must cite the original papers. The cleaning scripts and notes are this repo's own work and are released under the [MIT License](LICENSE). The MIT licence does not apply to the dataset files.

| Dataset | Owner | Terms | Cite |
|---|---|---|---|
| UNSW-NB15 | UNSW Canberra Cyber (N. Moustafa, J. Slay) | Free use for academic research purposes; **commercial use strictly prohibited** ([terms](https://research.unsw.edu.au/projects/unsw-nb15-dataset)) | [1], [2] |
| CIC-IDS-2017 | Canadian Institute for Cybersecurity, UNB | Redistribution and mirroring allowed in any form, but any use or redistribution must cite the paper ([terms](https://www.unb.ca/cic/datasets/ids-2017.html)). The Kaggle copy used here (`dhoogla/cicids2017`) is CC BY-NC-SA 4.0 | [3] |
| NSL-KDD | Canadian Institute for Cybersecurity, UNB | Same CIC terms: redistribution allowed with citation ([terms](https://www.unb.ca/cic/datasets/nsl.html)) | [4] |

1. N. Moustafa and J. Slay, "UNSW-NB15: a comprehensive data set for network intrusion detection systems (UNSW-NB15 network data set)," *Military Communications and Information Systems Conference (MilCIS)*, IEEE, 2015.
2. N. Moustafa and J. Slay, "The evaluation of Network Anomaly Detection Systems: Statistical analysis of the UNSW-NB15 data set and the comparison with the KDD99 data set," *Information Security Journal: A Global Perspective*, 25(1-3), 2016.
3. I. Sharafaldin, A. H. Lashkari and A. A. Ghorbani, "Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization," *4th Int. Conf. on Information Systems Security and Privacy (ICISSP)*, 2018.
4. M. Tavallaee, E. Bagheri, W. Lu and A. A. Ghorbani, "A Detailed Analysis of the KDD CUP 99 Data Set," *IEEE Symposium on Computational Intelligence for Security and Defense Applications (CISDA)*, 2009.

If you are a dataset owner and want a copy removed from this mirror, please open an issue.

## Main decisions (summary)

- **UNSW-NB15:** fixed the header, BOM, hex/`-` ports, blank FTP/HTTP counters (set to 0), `is_ftp_login` values above 1, and messy `attack_cat` values (whitespace, Backdoors→Backdoor, blank→Normal). 480,633 exact duplicate rows were removed in the dedup file.
- **CIC-IDS-2017:** fixed the Web Attack label encoding and dropped 8 constant columns. Removed 2,843 rows with impossible negative values (CICFlowMeter bugs), 81,997 duplicates across day files, and 540 rows with conflicting labels.
- **NSL-KDD:** the Kaggle parquet copy was missing 5 of the 41 features, so the original `KDDTrain+` / `KDDTest+` text files were used instead. Added names, a 4-category attack mapping and a binary label.
