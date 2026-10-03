"""Convert the original NSL-KDD text files to labelled parquet.

Run from the datasets folder:  python scripts/clean_nslkdd.py
See nslkdd/NOTES.md for what each step fixes and why.
"""
from pathlib import Path

import pandas as pd

SRC = Path("nslkdd/original")
OUT = Path("nslkdd/clean")
OUT.mkdir(exist_ok=True)

# Standard 41 features, then the label and the difficulty level (0-21).
COLS = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in",
    "num_compromised", "root_shell", "su_attempted", "num_root",
    "num_file_creations", "num_shells", "num_access_files", "num_outbound_cmds",
    "is_host_login", "is_guest_login", "count", "srv_count", "serror_rate",
    "srv_serror_rate", "rerror_rate", "srv_rerror_rate", "same_srv_rate",
    "diff_srv_rate", "srv_diff_host_rate", "dst_host_count",
    "dst_host_srv_count", "dst_host_same_srv_rate", "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate", "dst_host_srv_serror_rate", "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate", "attack", "difficulty",
]

# Standard 4-category mapping (Tavallaee et al. 2009 + test-only attacks).
CATEGORY = {
    "normal": "normal",
    **dict.fromkeys(["back", "land", "neptune", "pod", "smurf", "teardrop",
                     "apache2", "mailbomb", "processtable", "udpstorm"], "DoS"),
    **dict.fromkeys(["ipsweep", "nmap", "portsweep", "satan", "mscan",
                     "saint"], "Probe"),
    **dict.fromkeys(["ftp_write", "guess_passwd", "imap", "multihop", "phf",
                     "spy", "warezclient", "warezmaster", "named", "sendmail",
                     "snmpgetattack", "snmpguess", "worm", "xlock", "xsnoop",
                     "httptunnel"], "R2L"),
    **dict.fromkeys(["buffer_overflow", "loadmodule", "perl", "rootkit",
                     "ps", "sqlattack", "xterm"], "U2R"),
}

FILES = {
    "KDDTrain+.txt": "nslkdd_train.parquet",
    "KDDTrain+_20Percent.txt": "nslkdd_train_20pct.parquet",
    "KDDTest+.txt": "nslkdd_test.parquet",
    "KDDTest-21.txt": "nslkdd_test_21.parquet",
}

for src, dst in FILES.items():
    d = pd.read_csv(SRC / src, header=None, names=COLS)
    assert d.isna().sum().sum() == 0
    d["attack"] = d["attack"].str.strip()
    unknown = set(d["attack"]) - set(CATEGORY)
    assert not unknown, unknown
    d["attack_cat"] = d["attack"].map(CATEGORY)
    d["label"] = (d["attack"] != "normal").astype("int8")
    for c in ("protocol_type", "service", "flag", "attack", "attack_cat"):
        d[c] = d[c].astype("category")
    d.to_parquet(OUT / dst, index=False)
    print(f"{src:26s} rows={len(d):7,}  dups={d.duplicated().sum():4}  "
          f"{d['attack_cat'].value_counts().to_dict()}")

const = [c for c in COLS[:41] if pd.read_parquet(OUT / "nslkdd_train.parquet")[c].nunique() <= 1]
print("constant in train:", const)
