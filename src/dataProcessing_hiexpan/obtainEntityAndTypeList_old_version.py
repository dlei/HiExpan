'''
__author__: Ellen Wu, Jiaming Shen
__description__: Generate entity/type list from raw json input
    Input: 1) the sentence.json.raw
    Output: 1) a list of entity surface name, and 2) a list of type names
__latest_updates__: 08/23/2017
'''
import json
from collections import defaultdict
import sys

def main(corpusName):
    inputFile = '../../data/'+corpusName+'/intermediate/sentences.json.spacy'
    # probaseLinkedFile = '../../data/'+corpusName+'/intermediate/linked_results.txt'
    outputEntityListFile = '../../data/'+corpusName+'/intermediate/entitylist.txt'
    outputTypeListFile = '../../data/'+corpusName+'/intermediate/typelist.txt'

    mention2count = defaultdict(int)
    type2count = defaultdict(float)

    # entity2type2weight = defaultdict(lambda: defaultdict(float))
    # with open(probaseLinkedFile) as fin:
    #     for line in fin:
    #         seg = line.strip('\r\n').split('\t')
    #         if len(seg) <= 1:
    #             continue
    #         entity = seg[0].lower()
    #         for tup in seg[1:]:
    #             if len(tup.split()) < 1:
    #                 continue
    #             t = ' '.join(tup.split()[0:-1])
    #             wei = tup.split()[-1]
    #             entity2type2weight[entity][t] += float(wei)

    # ents = entity2type2weight.keys()
    with open(inputFile,"r") as fin:
        cnt = 0
        for line in fin:
            if cnt % 100000 == 0 and cnt != 0:
                print("Processed %d lines" % cnt)

            line = line.strip()
            sentence = json.loads(line)

            for mention in sentence["entityMentions"]:
                entity = mention["text"].lower()
                #if entity in ents:
                mention2count[entity] += 1
                ## TODO: deal with multiple types for each mention later
                # for t in entity2type2weight[entity]:
                #     type2count[t] += entity2type2weight[entity][t]
            cnt += 1


    with open(outputEntityListFile, "w") as fout:
        for ele in sorted(mention2count.items(), key = lambda x:(x[0],-x[1])):
            fout.write(ele[0]+"\t"+str(ele[1])+"\n")

    with open(outputTypeListFile, "w") as fout:
        for ele in sorted(type2count.items(), key = lambda x:(x[0],-x[1])):
            fout.write(ele[0]+"\t"+str(ele[1])+"\n")

if __name__ == '__main__':
    corpusName = sys.argv[1]
    main(corpusName)
