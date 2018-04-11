import sys
import json
from collections import defaultdict

def loadMap(filename):
  map = {}
  with open(filename, 'r') as fin:
    for line in fin:
      seg = line.strip('\r\n').split('\t')
      map[seg[0]] = int(seg[1])
  return map

def writeMapToFile(map, outFilename):
  with open(outFilename, 'w') as fout:
    for key in map:
      lkey = list(key)
      fout.write(str(lkey[0])+'\t'+str(lkey[1])+'\t'+str(map[key])+'\n')

if __name__ == "__main__":
  data = sys.argv[1]
  eidMapFilename = '../../data/'+data+'/intermediate/entity2id.txt'
  probaseLinkedFile = '../../data/'+data+'/intermediate/linked_results.txt'
  jsonFile = '../../data/'+data+'/intermediate/sentences.json'
  outFile = '../../data/'+data+'/intermediate/eidTypeCounts.txt'

  entity2type2weight = defaultdict(lambda: defaultdict(float))
  with open(probaseLinkedFile) as fin:
    for line in fin:
      seg = line.strip('\r\n').split('\t')
      if len(seg) <= 1:
        continue
      entity = seg[0].lower()
      for tup in seg[1:]:
        if len(tup.split()) < 1:
          continue
        t = ' '.join(tup.split()[0:-1])
        wei = tup.split()[-1]
        entity2type2weight[entity][t] += float(wei)
  ent2eidMap = loadMap(eidMapFilename)
  eidType2count = defaultdict(float)

  with open(jsonFile) as fin:
    for line in fin:
      for em in json.loads(line.strip('\r\n'))['entityMentions']:
        ent = em['text'].lower()
        eid = ent2eidMap[ent]
        for t in entity2type2weight[ent]:
          eidType2count[(eid, t)] += entity2type2weight[ent][t]

  writeMapToFile(eidType2count, outFile)

