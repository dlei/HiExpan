#!/bin/bash
data=$1
path=$(pwd)
# USE_CLEAN_PHRASE_LIST should be set to 0 in most cases
USE_CLEAN_PHRASE_LIST=${USE_CLEAN_PHRASE_LIST:- 0}
if [ $USE_CLEAN_PHRASE_LIST -eq 1 ]; then
	ENTITY_MIN_SUP=-1
else
	ENTITY_MIN_SUP=10
fi
## If use the script under corpusProcessing to generate the corpus, set DRY_RUN=0, otherwise, set it to be 1
DRY_RUN=${DRY_RUN:- 0}
## Whether extract relational skipgrams
EXTRACT_RELATIONAL_SKIPGRAMS=${EXTRACT_RELATIONAL_SKIPGRAMS:- 1}
## The embedding method used, can be PTE or word2vec
EMBEDDING_METHOD=word2vec

echo 'Corpus Name:' $data
echo 'Current Path:' $path

if [ ! -d ../../data/n$data/intermediate ]; then
	mkdir ../../data/$data/intermediate
fi

if [ ! -d ../../data/$data/results ]; then
	mkdir ../../data/$data/results
fi

echo 'start'

## If DRY_RUN is 0, run from the begging
if [ $DRY_RUN -eq 1 ]; then
	echo 'generating sentences.json and entity2id.txt'
	python3 probase3.py $data
	python3 obtainEntityAndTypeList.py $data
	python3 entityResolutionAndFilterv2.py $data $ENTITY_MIN_SUP
	python3 replaceEid.py $data
	python3 genCanonicalMap.py $data
else
	echo 'loading exist sentences.json and entity2id.txt'
fi

echo 'generating entityCounts.txt'
python3 entityCounts.py $data

echo 'generating eid-feature counts & strength files'
python3 extractTypeInfo.py $data
python3 extractFeatures.py $data
if [ $EXTRACT_RELATIONAL_SKIPGRAMS -eq 1 ]; then
	echo 'generating eid pair relational skipgrams files'
	python3 extractRelationalSkipgrams.py $data
fi

echo 'skipgram features'
python3 TFIDFSelection.py $data Skipgram
echo 'type feature'
python3 TFIDFSelection.py $data Type
if [ $EXTRACT_RELATIONAL_SKIPGRAMS -eq 1 ]; then
	echo 'relational skipgrams feature'
	python3 TFIDFSelection.py $data PairRelationalSkipgrams
fi

### I don't think the following is necessary
# echo 'pair-wise co-occurance feature'
# python3 TFIDFSelection.py $data Pair

if [ "$EMBEDDING_METHOD" == "PTE" ]; then
	echo 'generating embedding files using PTE'
	python3 prepareFormatForEmbed.py $data
	cd ../tools/PTE/
	make
	chmod +x ./run.sh
	./run.sh $data
	cd $path
	python3 getEmbFile.py $data PTE
elif [ "$EMBEDDING_METHOD" == "word2vec" ]; then
	echo 'generating embedding files using word2vec'
	python3 prepareFormatForEmbed_word2vec.py $data
	cd ../tools/word2vec/src
	make
	cd ../
	chmod +x ./run.sh
	./run.sh $data
	cd $path
	python3 getEmbFile.py $data word2vec
fi

### I don't think the following is necessary
# python prepareFormatForEmbed_type.py $data
# cd /shared/data/jiaming/entity-embed/
# ./run.sh $data
# cd $path
# python getEmbFile.py $data 1

# find eidPairDocumentLevelPPMI
python3 extractEidDocPairs.py

echo 'done'
