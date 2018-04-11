'''
__author__: Jiaming Shen
__description__: Check the metadata information in s2datasets, and extract text information
'''
import os
import re
import json
from collections import Counter
from collections import defaultdict

if __name__ == '__main__':
    rootdir = "../metadata/"

    filepaths = []
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            #print os.path.join(subdir, file)
            filepath = subdir + os.sep + file
            if filepath.endswith(".txt") :
                filepaths.append(filepath)

    keyphraselist = []
    abstractsWithId = []
    venue2count = defaultdict(int)
    cnt = 0
    for filepath in filepaths:
        with open(filepath, "r") as fin:
            for line in fin:
                cnt += 1
                line = line.strip()
                paperInfo = json.loads(line)

                venue = paperInfo["venue"]
                venue2count[venue] += 1
                keyPhrases = [ele.lower() for ele in paperInfo["keyPhrases"]]
                keyphraselist.extend(keyPhrases)

                paperID = paperInfo["id"]
                if not paperID:
                    print(paperInfo)
                abstract = paperInfo["paperAbstract"].replace("\n"," ")
                title = paperInfo["title"].replace("\n"," ")
                if not abstract:
                    abstract = ""
                    print("!!!Paper %s has no abstract" % paperID)
                if not title:
                    title = ""
                    print("!!!Paper %s has no title" % paperID)
                abstractsWithId.append([paperID, title, abstract])


    keyphraseCounter = Counter(keyphraselist)
    print(cnt)
    print(len(keyphraseCounter))
    for ele in keyphraseCounter.most_common(200):
        print(ele)

    for ele in venue2count.items():
        print(ele)

    with open("../keyPhrases.txt", "w") as fout:
        for ele in sorted(keyphraseCounter.items(), key = lambda x:-x[1]):
            if ele[1] >= 5:
                fout.write(ele[0]+"\t"+str(ele[1])+"\n")
            else:
                break

    with open("../title_abstracts.txt", "w") as fout:
        for ele in abstractsWithId:
            ## title three times
            fout.write(ele[1]+". ")
            fout.write(ele[1]+". ")
            fout.write(ele[1]+". ")
            fout.write(ele[2])
            fout.write("\n")
