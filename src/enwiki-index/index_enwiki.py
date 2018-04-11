'''
__author__: Jiaming Shen
__description__: Index enwiki files from yuning's output using Elasticsearch
'''
import os
import sys
import re
import time
import json
from collections import defaultdict
from elasticsearch import Elasticsearch


def parse_one_file(inputPath):
  documents = []
  with open(inputPath, "r") as fin:
    IN_DOC_MIDDLE = False
    for line in fin:
      m = re.findall("<doc id=\"(.*?)\" url=\"(.*?)\" title=\"(.*?)\">\n", line)
      if m: # start of doc
        doc_info = m[0] # example: ('24842957', 'https://en.wikipedia.org/wiki?curid=24842957', 'Reinaldo Alagoano')
        doc_string = ""
        IN_DOC_MIDDLE = True
      else:
        if line == "</doc>\n":
          doc_string = " ".join(doc_string.split())
          documents.append( (doc_info, doc_string) )
          IN_DOC_MIDDLE = False
        else: # middle of doc
          doc_string += line

  if IN_DOC_MIDDLE:
    print("[Warning] Mismatch of <doc> tag in file: %s" % inputPath)
  return documents

rootdir = "/shared/data/yuningm2/wikiextractor/enwiki/"
filePaths = []
for subdir, dirs, files in os.walk(rootdir):
  for file in files:
    filepath = subdir + os.sep + file
    filePaths.append(filepath)
print("Total number of files to index = %s" % len(filePaths))


logFilePath = "./log_20171229.txt"

INDEX_NAME = "enwiki_20171201"
TYPE_NAME = "enwiki_20171201_doc"

es = Elasticsearch()

with open(logFilePath, "w") as fout:
  start = time.time()
  doc_cnt = 0 # number of total enwiki articles
  file_cnt = 0
  for filepath in filePaths:
    file_cnt += 1
    documents = parse_one_file(filepath)
    doc_cnt += len(documents)
    bulk_data = []
    for document in documents:
      data_dict = {}
      if len(document) != 2 or len(document[0]) != 3:
        print(len(document))
        print(len(document[0]))
        print(document[0])
        continue
      data_dict["docid"] = document[0][0]
      data_dict["url"] = document[0][1]
      data_dict["title"] = document[0][2]
      data_dict["article"] = document[1]
      op_dict = {"index": {"_index": INDEX_NAME, "_type": TYPE_NAME, "_id": data_dict["docid"]}}
      bulk_data.append(op_dict)
      bulk_data.append(data_dict)

    tmp = time.time()
    es.bulk(index=INDEX_NAME, body=bulk_data, request_timeout=180)
    fout.write("[%s] bulk indexing... %s, escaped time %s (seconds) \n" % (file_cnt, filepath, tmp - start))
    print("[%s] bulk indexing... %s, escaped time %s (seconds) " % (file_cnt, filepath, tmp - start))

  end = time.time()
  fout.write("Finish indexing. Total escaped time %s (seconds) \n" % (end - start))
  print("Finish indexing. Total escaped time %s (seconds) " % (end - start))
  fout.write("Total number of enwiki articles = %s \n" % doc_cnt)
  print("Total number of enwiki articles = %s " % doc_cnt)
