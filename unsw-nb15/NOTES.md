# UNSW-NB15: notes

**Source:** Kaggle [`mrwellsdavid/unsw-nb15`](https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15), downloaded 2026-10-03 with the Kaggle CLI.
Official source to cite: Moustafa & Slay, "UNSW-NB15: a comprehensive data set for network intrusion detection systems", MilCIS 2015 (UNSW Canberra Cyber).

**Cleaning script:** `scripts/clean_unsw_nb15.py`. Run it from the `datasets` folder.

## Files

| File | What it is |
|---|---|
| `UNSW-NB15_1.csv` … `_4.csv` | Raw full dataset (no header). **Not modified.** |
| `NUSW-NB15_features.csv` | Column names, types and descriptions (49 columns) |
| `UNSW-NB15_LIST_EVENTS.csv` | Event counts per attack category/subcategory |
| `UNSW_NB15_training-set.csv` / `_testing-set.csv` | Official pre-made split (82,332 / 175,341 rows, 45 columns) |
| `clean/unsw_nb15_full.parquet` | **Cleaned full dataset, all 2,540,047 rows** |
| `clean/unsw_nb15_full_dedup.parquet` | Cleaned full dataset with exact duplicates removed (2,059,414 rows) |
| `clean/unsw_nb15_training_set.parquet` / `_testing_set.parquet` | Official split, same content as the CSVs, saved as parquet |

## Problems found in the raw CSVs and how they were fixed

| # | Problem | Fix |
|---|---|---|
| 1 | No header row | Column names taken from `NUSW-NB15_features.csv` |
| 2 | Column names messy (`ct_src_ ltm` has a space, mixed case like `Sload`, `Label`) | Lowercased and spaces removed, e.g. `ct_src_ltm`, `sload`, `label` |
| 3 | UTF-8 BOM at the start of `UNSW-NB15_1.csv` (corrupts the first IP) | Read with `utf-8-sig` |
| 4 | `sport` / `dsport` contain hex strings (`0x000b`, `0xcc09`, …; 304 rows) and `-` (9 rows) | Hex converted to int; `-` set to **-1** |
| 5 | `ct_flw_http_mthd` blank in 1,348,145 rows; `is_ftp_login` blank and `ct_ftp_cmd` a single space in 1,429,879 rows | Set to **0** (blank means the flow is not HTTP/FTP) |
| 6 | `is_ftp_login` is documented as binary but has values 2 (30 rows) and 4 (156 rows) | Clipped to 0/1 (`> 0` becomes 1) |
| 7 | `attack_cat` has stray whitespace (`" Fuzzers "`, `" Fuzzers"`, `" Reconnaissance "`, `" Shellcode "`) | Stripped |
| 8 | `attack_cat` has both `Backdoor` and `Backdoors` | Merged into `Backdoor` |
| 9 | `attack_cat` blank for normal traffic | Set to `Normal`; checked that this matches exactly the `label == 0` rows |
| 10 | Everything was read as text | Cast to numeric, with `proto`, `state`, `service`, IPs and `attack_cat` as categories |

After cleaning there are no NaNs left. The script asserts this.

## Facts worth knowing

- **Row count:** the raw files hold **2,540,047** records. The paper reports 2,540,044, and this small mismatch is common to every copy of the dataset.
- **Duplicates:** **480,633** rows are exact duplicates over all 49 columns. Most of them are `Generic` / `Exploits` / `DoS` attack rows. Removing them changes the class balance a lot:

  | attack_cat | full | dedup |
  |---|---:|---:|
  | Normal | 2,218,764 | 1,959,771 |
  | Generic | 215,481 | 25,378 |
  | Exploits | 44,525 | 27,599 |
  | Fuzzers | 24,246 | 21,795 |
  | DoS | 16,353 | 5,665 |
  | Reconnaissance | 13,987 | 13,357 |
  | Analysis | 2,677 | 2,184 |
  | Backdoor | 2,329 | 1,983 |
  | Shellcode | 1,511 | 1,511 |
  | Worms | 174 | 171 |

  When you make your own train/test split, use the dedup file (or deduplicate before splitting). Otherwise identical rows end up on both sides and inflate the scores.
- **Identifier and leakage columns:** `srcip`, `sport`, `dstip`, `dsport`, `stime` and `ltime` identify hosts and time. They are normally dropped before training. `sttl`, `dttl` and `ct_state_ttl` are known to leak the label almost on their own, so report whether you used them.
- **Official split files:** these were already clean (no NaNs, `attack_cat` normalised, `Normal` filled in). They use 45 slightly different columns: they add `id` and `rate`, rename some columns (`smean`, `sinpkt`, `response_body_len`), and drop the IPs, ports and timestamps. They also contain duplicates (26,387 in train, 67,601 in test when `id` is ignored), which matters if you report results on this split.
