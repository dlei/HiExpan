# generate new edges
# @dlei5

"""
taking in an existing edges
output newly added edges
"""

import sys
from collections import defaultdict


def getLineKey(line):
    segs = line.strip().split("\t")
    key = segs[0] + "^" + segs[1]
    return key    
    
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("usage: python generateEdges.py $DATANAME $TAXONOMY_TREE_FILE")

    data = sys.argv[1]
    old = sys.argv[2]
    new = sys.argv[3]

    dataDir = '../../data/' + data + '/results/'
    existingFile = dataDir + old
    newInputFile = dataDir + new
    
    existingMap = {}
    with open(existingFile) as fin:
        for line in fin:
            existingMap[getLineKey(line)] = True
            
        
    with open(newInputFile) as fin:
        for line in fin:
            if getLineKey(line) not in existingMap:
                segs = line.strip().split("\t")
                print(segs[0]+"\t"+segs[1])
                

