# NSL-KDD: notes

**Sources:**
- Kaggle [`dhoogla/nslkdd`](https://www.kaggle.com/datasets/dhoogla/nslkdd) (parquet): downloaded first, **not used** (see below)
- Kaggle [`hassan06/nslkdd`](https://www.kaggle.com/datasets/hassan06/nslkdd): the original UNB text/ARFF files, **used**

Both were downloaded 2026-10-03. Official source to cite: Tavallaee, Bagheri, Lu & Ghorbani, "A Detailed Analysis of the KDD CUP 99 Data Set", CISDA 2009 (UNB CIC).

**Cleaning script:** `scripts/clean_nslkdd.py`. Run it from the `datasets` folder.

## Why the dhoogla parquet was replaced

`KDDTrain.parquet` / `KDDTest.parquet` have only **36 of the standard 41 features**. They are missing `logged_in`, `srv_count`, `rerror_rate`, `srv_diff_host_rate` and `dst_host_srv_count`. Without those columns the data appears to contain 5,843 (train) and 646 (test) duplicate rows that are not duplicates in the real dataset. Results from this copy would not be comparable with the literature, so the original `KDDTrain+.txt` / `KDDTest+.txt` were downloaded and converted instead. The dhoogla files are left in `nslkdd/` untouched for reference only.

## Files

| File | What it is |
|---|---|
| `KDDTrain.parquet`, `KDDTest.parquet` | dhoogla copy, **not used** |
| `original/*.txt`, `original/*.arff` | Original NSL-KDD files: KDDTrain+, KDDTrain+_20Percent, KDDTest+, KDDTest-21. **Not modified.** |
| `clean/nslkdd_train.parquet` | KDDTrain+: 125,973 rows |
| `clean/nslkdd_train_20pct.parquet` | KDDTrain+_20Percent: 25,192 rows |
| `clean/nslkdd_test.parquet` | KDDTest+: 22,544 rows |
| `clean/nslkdd_test_21.parquet` | KDDTest-21 (the harder subset): 11,850 rows |

The Kaggle zip also unpacked every file a second time into `original/nsl-kdd/`. I checked that the copies were byte-identical (SHA-256) and deleted the second set, along with the `.jpg` and `index.html` extras.

## What was done

1. Added the 43 column names (the `.txt` files have no header): the standard 41 features, then `attack` (the label) and `difficulty` (0–21, how many of 21 classifiers got the record right).
2. Stripped whitespace from the attack names.
3. Added `attack_cat` using the standard 4-category mapping, including the attacks that only appear in the test set:
   - **DoS:** back, land, neptune, pod, smurf, teardrop, apache2, mailbomb, processtable, udpstorm
   - **Probe:** ipsweep, nmap, portsweep, satan, mscan, saint
   - **R2L:** ftp_write, guess_passwd, imap, multihop, phf, spy, warezclient, warezmaster, named, sendmail, snmpgetattack, snmpguess, worm, xlock, xsnoop, httptunnel
   - **U2R:** buffer_overflow, loadmodule, perl, rootkit, ps, sqlattack, xterm
4. Added `label`: 0 = normal, 1 = attack.
5. Stored `protocol_type`, `service`, `flag`, `attack` and `attack_cat` as categories.

The script asserts that the data has no NaNs and that every attack name is in the mapping.

## Checks

- Row counts match the official figures exactly (125,973 / 22,544).
- There are no NaNs and no duplicates in any of the four files.

| attack_cat | train | test |
|---|---:|---:|
| normal | 67,343 | 9,711 |
| DoS | 45,927 | 7,458 |
| Probe | 11,656 | 2,421 |
| R2L | 995 | 2,887 |
| U2R | 52 | 67 |

## Facts worth knowing

- `num_outbound_cmds` is always 0, so drop it before training. That leaves 40 features.
- The test set contains **17 attack types that never appear in training** (mscan, apache2, snmpgetattack, …). This is intentional. It's why R2L/U2R scores on KDDTest+ are low and why train/test accuracy differ so much.
- `difficulty` is metadata, not a feature. Leave it out of the model inputs.
- `service` has 70 values, so one-hot encoding gives 122 dimensions in total.
