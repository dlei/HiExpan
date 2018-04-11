# generate edges
# @dlei5

import sys
from collections import defaultdict

# extract edges from trees
def _recurse_tree(parent, depth, pool_map, source, fout):
    last_line = source.readline().rstrip()
    while last_line:
        tabs = last_line.count('\t')
        if tabs < depth:
            break
        node = last_line.strip()
        if tabs >= depth:
            if parent is not None:
                parent = parent.split(" (")[0]
                node = node.split(" (")[0]
                
                fout.write("%s\t%s\n" % (parent, node))
                
            last_line = _recurse_tree(node, tabs+1, pool_map, source, fout)
    return last_line


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("usage: python generateEdges.py $DATANAME $TAXONOMY_TREE_FILE")
        print("example: python generateEdges.py dblpv2 dblpv2-l3/taxonomy_test_new_hiexpan_iter_1_postprune.txt")

    data = sys.argv[1]
    variant = sys.argv[2]

    dataDir = '../../data/' + data + '/results/'
    resultFile = dataDir + variant
    outputFile = dataDir + variant.split(".")[0] + '_edges.txt'


    with open(resultFile) as fin, open(outputFile, 'w') as fout:
        pool_map = defaultdict(dict)
        _recurse_tree(None, 0, pool_map, fin, fout)

    print("Output: ", outputFile)

# sort {file-name} | uniq -u
