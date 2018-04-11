'''
__author__: Ellen Wu
__description__: extract the corpus extracted from WikiData for later use of segmentation
                 make sure to use python3
    input: 1)json_corpus_file: corpus json file, extracted from WikiData
    output: 1)corpus files: per text per line
'''

import sys
import json
import re

corpusName = sys.argv[1]
inputFileName = '../../data/'+corpusName+'/source/corpus.txt'
outputFileName = '../../data/'+corpusName+'/source/corpus.clean.txt'

with open(inputFileName) as fin, open(outputFileName, 'w') as f_corpus:
    for doc in fin:
        doc = doc.strip()
        # remove non-ascii character
        doc = re.sub(r"[^\x00-\x7F]+", "", doc)
        # replace multiple continuous punctations
        doc = re.sub(r"\!+", "!", doc)
        doc = re.sub(r"\,+", ",", doc)
        doc = re.sub(r"\?+", "?", doc)
        # add whitespace between/after some punctations
        doc = re.sub(r"([.,!:?()])", r" \1 ", doc)
        # replace multiple continuous whitespace with a single whitespace
        doc = re.sub(r"\s{2,}", "", doc)
        if not doc:
            doc = "EMPTY_DOC_PLACEHOLDER"
        f_corpus.write(doc+'\n')
