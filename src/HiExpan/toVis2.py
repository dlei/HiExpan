import pickle
from collections import defaultdict

# taxonomy_pickle_path = "/Users/shenjiaming/Google Drive/2018 HiExpan/experiments/taxonomy-results/" \
#                        "dblpv2-nnse-1-4-he-5/taxonomy_nnse-1-5-he-5_final.pickle"
# with open(taxonomy_pickle_path, "rb") as fin:
#   rootNode = pickle.load(fin)
#
# q = []
# def iterPath(node, path="*"):
#   if node.ename == "ROOT":
#     for child in node.children:
#       iterPath(child, path)
#   else:
#     q.append(path + "/" + "_".join(node.ename.split()))
#     # print(path + "/" + "_".join(node.ename.split()))
#     for child in node.children:
#       iterPath(child, path + "/" + "_".join(node.ename.split()))
#
# iterPath(rootNode)

taxonomy_txt_path = "/Users/shenjiaming/Google Drive/2018 HiExpan/experiments/taxonomy-results/" \
                       "wiki-best-l2/taxonomy_l2-best_final_adjusted.txt"
q = []
level2entity = defaultdict(list)
entity2directparent = {}
entity2level = {}
entity2path = {}
entity2finalpath = {}
with open(taxonomy_txt_path, "r") as fin:
  prev_level = 0
  prev_entity = ""
  for i, line in enumerate(fin):
    line = line.strip("\n")
    segs = line.split("\t")
    cur_level = len(segs)
    entity = segs[-1].split(" (eid=")[0]
    cur_entity = "_".join(entity.split())
    if i == 0:  # root
      cur_entity = "*"
      level2entity[cur_level].append(cur_entity)
      prev_entity = cur_entity
      prev_level = cur_level
      entity2finalpath[cur_entity] = "*"

    if cur_level == prev_level:
      cur_path = "/".join(entity2finalpath[prev_entity].split("/")[:-1])+"/"+cur_entity
    elif cur_level > prev_level:
      cur_path = entity2finalpath[prev_entity]+"/"+cur_entity
    elif cur_level < prev_level:
      level_diff = prev_level-cur_level
      cur_path = "/".join(entity2finalpath[prev_entity].split("/")[:-(1+level_diff)])+"/"+cur_entity
    else:
      print("Error")

    entity2finalpath[cur_entity] = cur_path
    q.append(cur_path[1:])
    # print("cur_level:", cur_level, "cur_entity:", cur_entity, "prev_level:", prev_level, "prev_entity:", prev_entity)
    print("cur_path:", cur_path[1:])
    prev_level = cur_level
    prev_entity = cur_entity



q = q[1:]
outFile = "../wordnet-vis-master/hiexpan_trees/wiki_final.txt"
with open(outFile, "w") as fout:
  for i,ele in enumerate(q):
    fout.write(str(i)+"\t"+ele+"\t"+"NA"+"\n")

