# evaluation
# @dlei5
# calculate accuracy and recall

import sys
from collections import defaultdict
from collections import deque

def checkAncesterCorrect(child, ancestor):
    if child not in child2parent:
        return False
    
    if child2parent[child] == ancestor:
        return True
    
    return checkAncesterCorrect(child2parent[child], ancestor)
    
def permute(edges):
    permuted_edges = defaultdict(set)
    for c, pset in edges.items():
        permuted_edges[c].union(pset)
        
        stack = list(pset)
        while len(stack):
            pp = stack.pop()
            if pp in edges:
                stack += edges[pp]
            permuted_edges[c].add(pp)
        
    return permuted_edges


def readEdgesToSet(fileName):
    dic = defaultdict(set)
    with open(fileName) as fin:
        for line in fin:
            line = line.strip()
            segs = line.split("\t")

            parent = segs[0]
            child = segs[1]
            dic[child].add(parent)
            
    return dic

def calcTotal(values):
    total = 0
    for v in values:
        total += len(v)
    return total

def eval(pred, gold):
    correct = 0
    for c, p in pred.items():
        if c in gold:
            correct += len(p & gold[c]) #intersect(p, gold[c])
            
    print("correct:", correct / calcTotal(pred.values()))
    print("recall:", correct / calcTotal(gold.values()))

    
if __name__ == "__main__":

    if len(sys.argv) < 4:
        print("usage: python eval.py $DATANAME $GOLD_TAXONOMY_EDGE_FILE $PRED_TAXONOMY_EDGE_FILE")
        # print("example: python generateEdges.py dblpv2 dblpv2-l3/taxonomy_test_new_hiexpan_iter_1_postprune.txt")

    data = sys.argv[1]
    goldFile = sys.argv[2]
    predFile = sys.argv[3]
    
    dataDir = '../../data/' + data + '/results/'

    # readin correct edges
    pred = readEdgesToSet(dataDir + predFile)
    gold = readEdgesToSet(dataDir + goldFile)

    print('edge-based metris: ')
    eval(pred, gold)
    print('ancestor-based metris: ')
    eval(permute(pred), permute(gold))

