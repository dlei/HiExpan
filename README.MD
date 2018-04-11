# HiExpan
To start, create a data folder with dataset name `$DATA` at the project root. 
```
data/$DATA
└── source
    └── corpus.txt
```
    
## Preprocessing
In `src/`, run

```./preprocess_master.sh $DATA```

## HiExpan
In `src/`, run

```python3 hi_expan.py -data cvd -taxonPrefix cvd_emb_13_3_555_seed -loadPickle 0```

Parameters to be fill in later. 
