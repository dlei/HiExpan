#!/bin/bash
# Author: Dongming Lei

DATA=$1

cd corpusProcessing_hiexpan
./corpusProcess.sh $DATA
cd ../dataProcessing_hiexpan
./dataProcess.sh $DATA
