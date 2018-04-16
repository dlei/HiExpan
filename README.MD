# HiExpan

To start, first create a data folder with dataset name `$DATA` at the project root, and then put your raw text corpus under the `$DATA/source/` folder. 

```
data/$DATA
└── source
    └── corpus.txt
```

## Requirments

Before running the following codes, you need to first install the required packages by typing following commands:

```
$ cd ./src/
$ pip3 install -r requirements.txt
```
	
## Preprocessing 
In `src/`, run

```
$ ./preprocess_master.sh $DATA
```

## HiExpan
In `src/HiExpan`, run

```
$ python3 hi_expan.py -data $DATA -taxonPrefix cvd_emb_13_3_555_seed -loadPickle 0
```