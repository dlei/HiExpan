import re
import sys

fname = sys.argv[1]
fname_out = sys.argv[2]
# fname = "/Users/shenjiaming/Desktop/wiki.emb.txt"
# fname_out = "/Users/shenjiaming/Desktop/entity_repel.emb"
with open(fname, 'r') as fin, open(fname_out, 'w') as fout:
  ct = -1
  for line in fin:
    if ct == -1:
      ct += 1
      continue
    seg = line.strip('\r\n').split(' ')
    if re.match(r"^\|\|(\d)+\|\|", seg[0]):
      eid = seg[0][2:-2]
      fout.write(" ".join([eid] + seg[1:]) + "\n")
      ct += 1

print("Number of entities:", ct)

