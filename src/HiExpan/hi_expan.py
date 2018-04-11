'''
__author__: Jiaming Shen, Ellen Wu, Dongming Lei
__description__: A python implementation of HiExpan v0.2 algorithm
__latest_update__: 02/06/2018
'''
import sys
import util
import math
import edge_expan
import tuple_expan
import argparse
import pickle
import params
import user_seeds
from tree_node import TreeNode
from set_expan import setExpan
from collections import defaultdict

# define global variables
MAX_ITER_TREE = 5
FLAGS_USE_TYPE = True
FLAGS_DEBUG = True
# during depth expansion, the number of reference edges under each siblings
FLAGS_INITIAL_EDGE = 1
# during depth expansion, the number of initial seeds that will be extracted
FLAGS_INITIAL_NODE = 3
# the method for depth expansion, allow: "embedding", "relational_skipgram"

# FLAGS_DEPTH_EXPANSION_METHOD = "relational_skipgram"
FLAGS_DEPTH_EXPANSION_METHOD = "embedding"
# relative weights used for setExpan
source_weights = {"sg":5.0, "tp":1.0, "eb":0.0}
# maximum children under each level, root level is -1, first level is 0, second level is 1, ......
level2max_children = {-1:10, 0:20, 1:40, 2:1e9, 3:1e9, 4:1e9, 5:1e9}
# the feature relative weights used for expanding a level x node's childrens
level2source_weights = {
  -1: {"sg":5.0, "tp":0.0, "eb":0.0},
  0: {"sg":5.0, "tp":0.0, "eb":0.0},
  1: {"sg":5.0, "tp":0.0, "eb":0.0},
  2: {"sg":5.0, "tp":0.0, "eb":0.0},
}
# the maximum expanded entity number
level2max_expand_eids = {-1: 3, 0:5, 1:5, 2:5}
# the global level-wise reference_edges between each two levels
level2reference_edges = defaultdict(list)
# use global level-wise reference edges or not
FLAGS_USE_GLOBAL_REFERENCE_ENDGES = True
# iteratively add level-wise reference edges during expansion or not
FLAGS_ITERATIVELY_ADD_REFERENCE_EDGES = True

def obtainReferenceEdges(targetNode, useGlobal=False):
  if useGlobal:
    reference_edges = level2reference_edges[targetNode.level]
  else:
    reference_edges = []
    ## Add 1) edges in user guidance and 2) first FLAGS_INITIAL_EDGE edge under each sibling nodes as
    # reference edges
    for sibling in targetNode.parent.children:
      cnt = 0
      for cousin in sibling.children:
        if cousin.isUserProvided and sibling.isUserProvided:
          reference_edges.append((sibling.eid, cousin.eid))
        else:
          reference_edges.append((sibling.eid, cousin.eid))
          cnt += 1
          if cnt >= FLAGS_INITIAL_EDGE:
            break
  return reference_edges

def isSynonym(eid1, eid2):
  eidpair = frozenset([eid1, eid2])
  for synset in synonyms_KB:
    if eidpair.issubset(synset):
      return True
  return False

def save_conflict_nodes(eidsWithConflicts, eid2nodes, conflict_nodes_file_path):
  with open(conflict_nodes_file_path, "w") as fout:
    fout.write("Number of conflict eids = %s\n" % len(eidsWithConflicts))
    fout.write("="*80+"\n")
    for eid in eidsWithConflicts:
      fout.write("Deal with conflict nodes with ename = %s, eid = %s\n" % (eid2ename[eid], eid))
      conflictNodes = eid2nodes[eid]
      for conflictNode in conflictNodes:
        fout.write("    "+str(conflictNode)+"\n")
      mostProbableNodeIdx = util.getMostProbableNodeIdx(conflictNodes, eid2patterns, eidAndPattern2strength)
      fout.write("!!!Most probable node:" + str(conflictNodes[mostProbableNodeIdx])+"\n")
      fout.write("="*80+"\n")

def updateParams(params):
  MAX_ITER_TREE = params['MAX_ITER_TREE']
  FLAGS_USE_TYPE = params['FLAGS_USE_TYPE']
  FLAGS_DEBUG = params['FLAGS_DEBUG']
  FLAGS_INITIAL_EDGE = params['FLAGS_INITIAL_EDGE']
  FLAGS_INITIAL_NODE = params['FLAGS_INITIAL_NODE']
  FLAGS_DEPTH_EXPANSION_METHOD = params['FLAGS_DEPTH_EXPANSION_METHOD']
  level2max_children = params['level2max_children']
  level2source_weights = params['level2source_weights']
  level2max_expand_eids = params['level2max_expand_eids']
  level2reference_edges = params['level2reference_edges']
  FLAGS_USE_GLOBAL_REFERENCE_ENDGES = params['FLAGS_USE_GLOBAL_REFERENCE_ENDGES']
  FLAGS_ITERATIVELY_ADD_REFERENCE_EDGES = params['FLAGS_ITERATIVELY_ADD_REFERENCE_EDGES']

# read all command line parameters
parser = argparse.ArgumentParser(prog='hi_expan.py', description='Run HiExpan algorithm on input data')
parser.add_argument('-data', required=True, help='CorpusName.')
parser.add_argument('-taxonPrefix', required=True, help='Output Taxonomy Prefix')
parser.add_argument('-loadPickle', required=False, default=0, help='load prestored data from pickle or not')

args = parser.parse_args()
data = str(args.data)
load_pickle_flag = (int(args.loadPickle) == 1)
taxonPrefix = str(args.taxonPrefix)

# Update all model parameters
if data == 'wiki':
  pm = params.load_wiki_params()
elif data == 'dblpv2':
  pm = params.load_dblp_params()
elif data == 'cvd':
  pm = params.load_cvd_params()
elif data == 'ql':
  pm = params.load_ql_params()
else:
  print("[ERROR] Unsupported Dataset: %s" % data)
  exit(-1)
updateParams(pm)

'''
Load all data files
'''
if load_pickle_flag:
  ## load from pickle
  print("=== Start loading all files ...... ===")
  print("load_from_pickle")
  pickle_file = '../../data/' + data + '/intermediate/all_data.pickle'
  with open(pickle_file, "rb") as fin:
    [eid2ename, ename2eid, eid2patterns, pattern2eids, eidAndPattern2strength, eid2types, type2eids,
     eidAndType2strength, eid2embed, embed_matrix, eid2rank, rank2eid, embed_matrix_array, skipgramsByEidPairMap,
     eidPairsBySkipgramMap, weightByEidPairAndSkipgramMap] = pickle.load(fin)
  print("=== Finish loading all files. HaHaHa ===")
else:
  print("=== Start loading all files ...... ===")
  folder = '../../data/'+data+'/intermediate/'
  print('loading eid and name maps')
  eid2ename, ename2eid = util.loadEidToEntityMap(folder+'entity2id.txt') #entity2Eid.txt

  ## TODO: Later, we can merge the loadFeaturesAndEidMap and loadWeightByEidAndFeatureMap into one function
  print('loading eid and skipgram maps')
  eid2patterns, pattern2eids = util.loadFeaturesAndEidMap(folder+'eidSkipgramCounts.txt') #eidSkipgramCount.txt
  print('loading skipgram strength map')
  eidAndPattern2strength = util.loadWeightByEidAndFeatureMap(folder+'eidSkipgram2TFIDFStrength.txt', idx=-1) #(eid, feature, weight) file

  # print('loading eid pair document-level PPMI score')
  # eidpair2PPMI = util.loadEidDocPairPPMI(folder+'eidDocPairPPMI.txt')

  if (FLAGS_USE_TYPE):
    print('loading eid and type maps')
    eid2types, type2eids = util.loadFeaturesAndEidMap(folder+'eidTypeCounts.txt') #eidTypeCount.txt
    print('loading type strength map')
    eidAndType2strength = util.loadWeightByEidAndFeatureMap(folder+'eidType2TFIDFStrength.txt', idx=-1) #(eid, feature, weight) file
  else:
    eid2types = {}
    type2eids = {}
    eidAndType2strength = {}


  print("loading entity embedding files")
  # inputEntityEmbeddingFile="../../data/"+data+"/intermediate/entity.emb"
  inputEntityEmbeddingFile="../../data/"+data+"/intermediate/entity_word2vec.emb"
  # inputEntityEmbeddingFile="../../data/"+data+"/intermediate/entity_repel.emb"
  (eid2embed, embed_matrix, eid2rank, rank2eid, embed_matrix_array) = edge_expan.load_entity_embedding(inputEntityEmbeddingFile)

  print('loading skipgramsByEidMap, eidsBySkipgramMap...')
  skipgramsByEidPairMap, eidPairsBySkipgramMap = util.loadFeaturesAndEidPairMap(
    folder + 'eidPairRelationalSkipgramsCounts.txt')  # eidPairRelationalSkipgramsCounts.txt

  print('loading weightByEidAndSkipgramMap...')
  weightByEidPairAndSkipgramMap = util.loadWeightByEidPairAndFeatureMap(
    folder + 'eidPairRelationalSkipgrams2TFIDFStrength.txt')  # (eid1, eid2, feature, weight) file

  print("=== Finish loading all files. HaHaHa ===")

  pickle_file = folder + "all_data.pickle"
  with open(pickle_file, "wb") as fout:
    pickle.dump([eid2ename, ename2eid, eid2patterns, pattern2eids, eidAndPattern2strength, eid2types, type2eids,
                 eidAndType2strength, eid2embed, embed_matrix, eid2rank, rank2eid, embed_matrix_array,
                 skipgramsByEidPairMap, eidPairsBySkipgramMap, weightByEidPairAndSkipgramMap],
                fout, protocol=pickle.HIGHEST_PROTOCOL)
  print("[INFO] save to pickle")

'''
Initialize the seed taxonomy
'''
if data == "wiki":
  userInput = user_seeds.load_wiki_seeds()
elif data == "dblpv2":
  userInput = user_seeds.load_dblp_seeds()
elif data == "cvd":
  userInput = user_seeds.load_cvd_seeds()
elif data == "ql":
  userInput = user_seeds.load_ql_seeds()
else:
  print("[ERROR] Unsupported Dataset: %s" % data)
  exit(-1)

stopLevel = max([ele[1] for ele in userInput]) + 1
print("stopLevel:", stopLevel)
print("Tree Depth:", stopLevel+1)

if data == "wiki":
  ## Use Case 1: Wiki-location
  synonyms_KB = set([ frozenset([640449, 644125, 637887]), frozenset([686224, 686220]) ])
elif data == "dblpv2":
  ## Use Case 2: DBLP-CS
  synonyms_KB = set([
    frozenset([16878, 16877]), # wireless network
    frozenset([15716, 15721, 15718, 15712]), # training examples
    frozenset([6928, 6851]), # human-computer interaction
  ])
elif data == "cvd":
  ## Use Case 3: CVD
  synonyms_KB = set([
      frozenset([8555, 5297]), # cv disease, cardiovascular diseases
      frozenset([14515, 7984, 5146]), #coronary heart diseases, heart-disease
      frozenset([32371,5297]), #TRICKY
  ])
else:
  synonyms_KB = set([])


'''
Add user supervision
'''
rootNode = None
ename2treeNode = {}
for i, node in enumerate(userInput):
  if i == 0: ## ROOT
    rootNode = TreeNode(parent=None, level=-1, eid=-1, ename="ROOT", isUserProvided=True, confidence_score=0.0,
                        max_children=level2max_children[-1])
    ename2treeNode["ROOT"] = rootNode
    for children in node[2]:
      newNode = TreeNode(parent=rootNode, level=0, eid=ename2eid[children], ename=children, isUserProvided=True,
                         confidence_score=0.0, max_children=level2max_children[0])
      ename2treeNode[children] = newNode
      rootNode.addChildren([newNode])
  else:
    ename = node[0]
    eid = ename2eid[ename]  # assume user supervision is an entity mention in entity2id.txt
    level = node[1]
    childrens = node[2]
    if ename in ename2treeNode: # existing node
      parent_treeNode = ename2treeNode[ename]
      for children in childrens:
        newNode = TreeNode(parent=parent_treeNode, level=parent_treeNode.level+1, eid=ename2eid[children],
                           ename=children, isUserProvided=True, confidence_score=0.0,
                           max_children=level2max_children[parent_treeNode.level+1])
        ename2treeNode[children] = newNode
        parent_treeNode.addChildren([newNode])
        level2reference_edges[parent_treeNode.level].append((parent_treeNode.eid, newNode.eid))
    else: # not existing node
      print("[ERROR] disconnected tree node: %s" % node)

print("level2reference_edges:", level2reference_edges)

### Previous user guidance input
# rootNode = TreeNode(parent=None, level=-1, eid=-1, ename="ROOT", isUserProvided=True, confidence_score=0.0)
# rootNode = TreeNode(parent=None, level=-1, eid=11301, ename="Computer Science", isUserProvided=True, confidence_score=0.0)
# nextParent = rootNode
# for i in range(len(userInput)):
#   levelList = userInput[i]
#   level = i
#   parent = nextParent
#   for j in range(len(levelList)):
#     ename = levelList[j]
#     newNode = TreeNode(parent, level, ename2eid[ename.lower()], ename, True, confidence_score=0.0)
#     if j == 0:
#       nextParent = newNode
#     parent.addChildren([newNode])

rootNode.printSubtree(0)
seed_taxonomy_file_path = "../../data/"+data+"/results/taxonomy_%s_init.txt" % taxonPrefix
rootNode.saveToFile(seed_taxonomy_file_path)

'''
Start HiExpan: iteratively grow the taxonomy tree
'''
update = True
iters = 0
while update:
  # expand the whole tree (expand node by node) and record node(s) of eid
  eid2nodes = {}
  eidsWithConflicts = set()
  targetNodes = [rootNode] # targetNodes includes all parent nodes to expand
  while len(targetNodes) > 0:
    # expand childrens under current targetnode
    targetNode = targetNodes[0]
    targetNodes = targetNodes[1:]
    if targetNode.eid >= 0:
      eid = targetNode.eid

      # detect conflicts
      if eid in eid2nodes:
        eid2nodes[eid].append(targetNode)
        eidsWithConflicts.add(eid)
      else:
        eid2nodes[eid] = [targetNode]

    # targetNode is already leaf node, stop expanding
    if targetNode.level >= stopLevel:
      continue

    # targetNode has enough children, just add children to be consider, stop expanding
    if len(targetNode.children) > targetNode.max_children:
      targetNodes += targetNode.children
      print("[INFO: Reach maximum children at node]:", targetNode)
      continue

    # Depth expansion: expand target node
    if len(targetNode.children) == 0:

      # Depth expansion: get seed entities if no children is provided by user
      ## TODO: change other ways to obtain the reference edges
      if FLAGS_DEBUG:
        print("[Depth Expansion] ", end = "")
        print(targetNode)

      reference_edges = obtainReferenceEdges(targetNode, useGlobal=FLAGS_USE_GLOBAL_REFERENCE_ENDGES)
      if FLAGS_DEBUG:
        print("\t\tNumber of reference edges = %s" % len(reference_edges))

      if FLAGS_DEPTH_EXPANSION_METHOD == "embedding":
        seedChildrenInfo = edge_expan.edge_expan_using_edges(reference_edges, targetNode.eid, eid2embed,
                                                             embed_matrix_array, rank2eid, eid2ename,
                                                             embed_dim=100, topK=FLAGS_INITIAL_NODE)
      elif FLAGS_DEPTH_EXPANSION_METHOD == "relational_skipgram":
        seedChildrenInfo = tuple_expan.tuple_expan(targetNode.eid, reference_edges, eid2ename, skipgramsByEidPairMap,
                                                   eidPairsBySkipgramMap, weightByEidPairAndSkipgramMap,
                                                   topK=FLAGS_INITIAL_NODE, FLAGS_DEBUG=False)
      else:
        print("[ERROR] Unsupported depth expansion method: %s" % FLAGS_DEPTH_EXPANSION_METHOD)

      ## If relational skipgram cannot extract candidates, using embedding
      if len(seedChildrenInfo) == 0:
        print("[INFO] Use relational skipgram unable to obtain initial seeds, switch to embedding method")
        print(targetNode)
        seedChildrenInfo = edge_expan.edge_expan_using_edges(reference_edges, targetNode.eid, eid2embed,
                                                             embed_matrix_array, rank2eid, eid2ename, embed_dim=100,
                                                             topK=FLAGS_INITIAL_NODE)

      if FLAGS_DEBUG:
        for ele in seedChildrenInfo:
          print("\t\tObtain node with ename=%s, eid=%s" % (ele[1], ele[0]))

      seedOrderedChildren = []
      for seedChildren in seedChildrenInfo:
        seedChildEid = seedChildren[0]
        seedChildEname = seedChildren[1]
        confidence_score = (targetNode.confidence_score + math.log(seedChildren[2]))
        if seedChildEid != targetNode.eid:
          seedOrderedChildren.append(TreeNode(parent=targetNode, level=targetNode.level+1, eid=seedChildEid,
                                              ename=seedChildEname, isUserProvided=False,
                                              confidence_score=confidence_score,
                                              max_children=level2max_children[targetNode.level+1]))
          if FLAGS_ITERATIVELY_ADD_REFERENCE_EDGES:
            level2reference_edges[targetNode.level].append((targetNode.eid, seedChildEid))
      targetNode.addChildren(seedOrderedChildren)

    # Wide expansion: obtain ordered new childrenEids
    seedEidsWithConfidence = [(child.eid, child.confidence_score) for child in targetNode.children]
    negativeSeedEids = targetNode.restrictions
    negativeSeedEids.add(targetNode.eid) # add parent eid as negative example into SetExpan
    if FLAGS_DEBUG:
      print("[Width Expansion] Expand: ", targetNode, "restrictions:", negativeSeedEids)
    ## at least grow one node
    max_expand_eids = max(len(negativeSeedEids)+1, level2max_expand_eids[targetNode.level])
    # max_expand_eids = level2max_expand_eids[targetNode.level] + len(negativeSeedEids)
    newOrderedChildrenEidsWithConfidence = setExpan(seedEidsWithConfidence, negativeSeedEids, eid2patterns,
                                                    pattern2eids,eidAndPattern2strength, eid2types, type2eids,
                                                    eidAndType2strength, eid2ename, eid2embed,
                                                    source_weights=level2source_weights[targetNode.level],
                                                    max_expand_eids=max_expand_eids,
                                                    use_embed=True,
                                                    use_type=True)
    newOrderedChildren = []
    for ele in newOrderedChildrenEidsWithConfidence:
      ## Check synonmy
      newChildEid = ele[0]
      confidence_score = ele[1]
      confidence_score += targetNode.confidence_score
      synonym_FLAG = False
      for sibling in targetNode.children:
        if isSynonym(newChildEid, sibling.eid):
          sibling.addSynonym(newChildEid)
          synonym_FLAG = True
          if FLAGS_DEBUG:
            print("\t\t[Synonym] Find a pair of synonyms: <%s (%s), %s (%s)>" % (sibling.ename, sibling.eid,
                                                                          eid2ename[newChildEid], newChildEid))
          break
      if synonym_FLAG: ## bypass those synonym nodes
        continue

      newChild = TreeNode(parent=targetNode, level=targetNode.level+1, eid=newChildEid, ename=eid2ename[newChildEid],
                          isUserProvided=False, confidence_score=confidence_score,
                          max_children=level2max_children[targetNode.level+1])
      if FLAGS_DEBUG:
        print("        Obtain node with ename=%s, eid=%s" % (eid2ename[newChildEid], newChildEid))
      newOrderedChildren.append(newChild)
    targetNode.addChildren(newOrderedChildren)

    # Add its children as in the queue
    targetNodes += targetNode.children


  # tree is expanded in this iter
  iters += 1
  taxonomy_file_path = "../../data/" + data + "/results/taxonomy_%s_iter_%s_preprune.txt" % (taxonPrefix, iters)
  rootNode.saveToFile(taxonomy_file_path)
  taxonomy_pickle_path = "../../data/" + data + "/results/taxonomy_%s_iter_%s_preprune.pickle" % (taxonPrefix, iters)
  with open(taxonomy_pickle_path, "wb") as fout:
    pickle.dump(rootNode, fout, protocol=pickle.HIGHEST_PROTOCOL)
  print("=== Starting Taxonomy Pruning at iteration %s ===" % iters)
  if FLAGS_DEBUG:
    print("level2reference_edges:", level2reference_edges)
    rootNode.printSubtree(0)
    print("[INFO] Number of conflict eids at iteration %s = %s" % (iters, len(eidsWithConflicts)))
    conflict_nodes_file_path = "../../data/" + data + "/results/taxonomy_%s_iter_%s_conflict_nodes.txt" % (taxonPrefix, iters)
    save_conflict_nodes(eidsWithConflicts, eid2nodes, conflict_nodes_file_path)

  # check conflicts
  nodesToDelete = []
  for eid in eidsWithConflicts:
    if FLAGS_DEBUG:
      print("Deal with conflict nodes with ename = %s, eid = %s" % (eid2ename[eid], eid))
    # select most probable one
    conflictNodes = eid2nodes[eid]
    if FLAGS_DEBUG:
      print("\tConflict nodes:")
      for conflictNode in conflictNodes:
        print("\t", conflictNode)
    mostProbableNodeIdx = util.getMostProbableNodeIdx(conflictNodes, eid2patterns, eidAndPattern2strength)
    if FLAGS_DEBUG:
      print("    [Pruning] Most probable Node = ", end="")
      print(conflictNodes[mostProbableNodeIdx])
    # 1) delete others and 2) for their parents: updateFromChild
    for i in range(len(conflictNodes)):
      if i == mostProbableNodeIdx:
        continue
      nodesToDelete.append(conflictNodes[i])

  if FLAGS_DEBUG:
    print("[Pruning] Start deleting all the following nodes")
  for node in nodesToDelete:
    if FLAGS_DEBUG:
      print(node)
    node.parent.cutFromChild(node)
    node.delete()

  print("=== Taxonomy Tree at iteration %s ===" % iters)
  rootNode.printSubtree(0)
  taxonomy_file_path = "../../data/" + data + "/results/taxonomy_%s_iter_%s_postprune.txt" % (taxonPrefix, iters)
  rootNode.saveToFile(taxonomy_file_path)
  taxonomy_pickle_path = "../../data/" + data + "/results/taxonomy_%s_iter_%s_postprune.pickle" % (taxonPrefix, iters)
  with open(taxonomy_pickle_path, "wb") as fout:
    pickle.dump(rootNode, fout, protocol=pickle.HIGHEST_PROTOCOL)
  print("Finish saving post-pruning Taxonomy Tree at iteration %s" % iters)

  if iters >= MAX_ITER_TREE:
    break
  ## TODO: remove it after testing
  # update = False
  # break

print("Final Taxonomy Tree")
rootNode.printSubtree(0)
taxonomy_file_path = "../../data/" + data + "/results/taxonomy_%s_final.txt" % taxonPrefix
taxonomy_pickle_path = "../../data/" + data + "/results/taxonomy_%s_final.pickle" % taxonPrefix
with open(taxonomy_pickle_path, "wb") as fout:
  pickle.dump(rootNode, fout, protocol=pickle.HIGHEST_PROTOCOL)
rootNode.saveToFile(taxonomy_file_path)


