# @dlei5
# generate the canonical form
# input: 
#  1) /intermediate/entitylist.txt
#  2) /intermediate/entity2id.txt
# output:
#  1) /intermediate/canonicalMapping.txt
#  2) /intermediate/entity2idUnique.txt

from collections import defaultdict
import numpy as np
import sys

data = sys.argv[1]

entityCountFileName = '../../data/'+data+'/intermediate/entitylist.txt'
entityCount = {}
with open(entityCountFileName) as fin:
    for line in fin:
        segs = line.strip().split("\t")
        if len(segs) < 2:
            print("DEFECT LINE", line, segs)
            continue
        entityCount[segs[0]] = int(segs[1])

inputFileName = '../../data/'+data+'/intermediate/entity2id.txt'
id2entities = defaultdict(set)
with open(inputFileName) as fin:
    for line in fin:
        segs = line.strip().split("\t")
        id2entities[segs[1]].add(segs[0])

canonicalFormOutputFile = '../../data/'+data+'/intermediate/canonicalMapping.txt'
canonicalFormMap = {}
with open(canonicalFormOutputFile, 'w') as fout:
    for key, vals in id2entities.items():
        vals = list(vals)
        counts = [entityCount[ele] for ele in vals]
        canonical_form = vals[np.argmax(counts)]
        canonicalFormMap[canonical_form] = vals
        fout.write(canonical_form + '\t' + ','.join(vals) + '\n')

uniqueE2IdOutputFile = '../../data/'+data+'/intermediate/entity2idUnique.txt'
with open(inputFileName) as fin, open(uniqueE2IdOutputFile, 'w') as fout:
    for line in fin:
        segs = line.strip().split("\t")
        if segs[0] in canonicalFormMap:
            fout.write(line)
