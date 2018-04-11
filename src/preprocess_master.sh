#!/bin/bash
# Author: Dongming Lei

DATA=$1

cd corpusProcessing_hiexpan
./corpusProcess.sh $DATA
cd ../dataProcessing_hiexpan
export DRY_RUN=1
./dataProcess.sh $DATA
