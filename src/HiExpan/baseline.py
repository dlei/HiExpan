# @dlei5

# import libs
import numpy as np
from scipy.spatial import distance
import math

import util
import set_expan
import time
import pickle

from tree_node import TreeNode
from collections import defaultdict



# set up global vars

level2max_children = {-1:10, 0:15, 1:5, 2:1e9, 3:1e9, 4:1e9, 5:1e9}
level2reference_edges = defaultdict(list)
negativeSeedEids = set()
load_pickle_flag = True
FLAGS_USE_TYPE = True



data = "dblpv2"
folder = '../../data/'+data+'/intermediate/'

userInput = [
  ["ROOT", -1, ["machine learning", "data mining", "information retrieval"]],

  ["machine learning", 0, ["supervised machine learning", "unsupervised learning", "reinforcement learning"]],
  ["data mining", 0, ["pattern mining", "graph mining", "web mining", "text mining"]],
  ["information retrieval", 0, ["document retrieval", "query processing", "relevance feedback"]],
    
  ["supervised machine learning", 1, ["support vector machines"]]
]

# load pickle data 

print("=== Start loading all files ...... ===")
print("load_from_pickle")
pickle_file = '../../data/' + data + '/intermediate/all_data.pickle'
with open(pickle_file, "rb") as fin:
    [eid2ename, ename2eid, eid2patterns, pattern2eids, eidAndPattern2strength, eid2types, type2eids,
     eidAndType2strength, eid2embed, embed_matrix, eid2rank, rank2eid, embed_matrix_array, skipgramsByEidPairMap,
     eidPairsBySkipgramMap, weightByEidPairAndSkipgramMap] = pickle.load(fin)
print("=== Finish loading all files. HaHaHa ===")


# load PPMI
print('loading eid pair document-level PPMI score')
eidpair2PPMI = util.loadEidDocPairPPMI(folder + 'eidDocPairPPMI.txt')


# define functions 
def sim_par_new(p_eid, c_eid, reference_edges, embed_alpha, eid2embed, eidpair2PPMI, embed_dim=100, DEBUG=False):
  '''
  reference_edges: a list of (parent, child) eids
  embed_alpha: relative weight of embedding, set 1.0 to use only embedding, set 0.0 to use only document-co-occurrence
  '''

  ## embedding offest similarity
  target_offset = np.zeros([1, embed_dim])
  for edge in reference_edges:
    target_offset += (eid2embed[edge[0]] - eid2embed[edge[1]])
  target_offset /= (len(reference_edges))

  current_relation_offset = eid2embed[p_eid] - eid2embed[c_eid]
  embedding_sim = float(1.0 - distance.cdist(current_relation_offset, target_offset, 'cosine'))
  if embedding_sim < 0:
    embedding_sim = 0.0

  ## docPPMI similarity
  if frozenset([c_eid, p_eid]) in eidpair2PPMI:
    cooccur_sim = eidpair2PPMI[frozenset([c_eid, p_eid])]
  else:
    cooccur_sim = 0.0

  # overall_sim = ( embedding_sim ** embed_alpha ) * (cooccur_sim ** (1-embed_alpha))
  overall_sim = embedding_sim * math.sqrt(1 + cooccur_sim)
  if DEBUG:
    print("Embedding_sim:", embedding_sim)
    print("Co-occurrence_sim:", cooccur_sim)
    print("Scaled_embedding_sim:", (embedding_sim ** (1 - embed_alpha)))
    print("Overall_sim:", overall_sim)
    print("%.6f" % embedding_sim, "%.6f" % cooccur_sim, "%.6f" % overall_sim)
  return overall_sim


def runSetExpan(seedEidsWithConfidence, numToExpand):
    expandedEidsWithConfidence = set_expan.setExpan(
        seedEidsWithConfidence=seedEidsWithConfidence,
        negativeSeedEids=negativeSeedEids,
        eid2patterns=eid2patterns,
        pattern2eids=pattern2eids,
        eidAndPattern2strength=eidAndPattern2strength,
        eid2types=eid2types,
        type2eids=type2eids,
        eidAndType2strength=eidAndType2strength,
        eid2ename=eid2ename,
        eid2embed=eid2embed,
        source_weights={"sg":1.0, "tp":5.0, "eb":5.0},
        max_expand_eids=numToExpand,
        use_embed=True,
        use_type=True,
        FLAGS_VERBOSE=False,
        FLAGS_DEBUG=False
    )
    print(expandedEidsWithConfidence)
    for ele in expandedEidsWithConfidence:
      print("eid=", ele[0], "ename=", eid2ename[ele[0]], "confidence_score=", ele[1])

    
    return expandedEidsWithConfidence


def obtainReferenceEdges(targetNode):
  return level2reference_edges[targetNode.level]
  reference_edges = []
  ## Add 1) edges in user guidance and 2) first FLAGS_INITIAL_EDGE edge under each sibling nodes as
  # reference edges
  for sibling in targetNode.parent.children:
    print(sibling)
    cnt = 0
    for cousin in sibling.children:
      print(cousin)
      if cousin.isUserProvided and sibling.isUserProvided:
        reference_edges.append((sibling.eid, cousin.eid))
      else:
        reference_edges.append((sibling.eid, cousin.eid))
        cnt += 1
        if cnt >= FLAGS_INITIAL_EDGE:
          break
  return reference_edges


def init():
    # generate reference edges
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
        
    return rootNode


def getNodesByLevel(node, level):
    if node.level == level:
        return [node]
    
    res = []
    for child in node.children:
        res = res + getNodesByLevel(child, level)
        
    return res


rootNode = init()
rootNode.printSubtree(0)
reference_edges = obtainReferenceEdges(rootNode.children[0])


level = -1 # start from root
MAX_LEVEL = 2
targetNode = rootNode
while level < MAX_LEVEL:
    
    level += 1
    print(level)
    
    seedEidsWithConfidence = [(child.eid, child.confidence_score) for child in getNodesByLevel(rootNode, level)]
    newOrderedChildrenEidsWithConfidence = runSetExpan(seedEidsWithConfidence, 5 ** level)
    
    print(newOrderedChildrenEidsWithConfidence)
    for ele in newOrderedChildrenEidsWithConfidence:
        newChildEid = ele[0]
        confidence_score = ele[1]
            
        if level == 0: # first level, just append them to root

            newChild = TreeNode(parent=rootNode, level=level, eid=newChildEid, ename=eid2ename[newChildEid],
                                  isUserProvided=False, confidence_score=confidence_score,
                                  max_children=level2max_children[targetNode.level+1])
            rootNode.addChildren([newChild])


        else:
            # calculate best parent to attach to 
            max_sim = 0
            best_parent = None
            for p in getNodesByLevel(rootNode, level-1): # find all parents for this child 
#                 obtainReferenceEdges(rootNode.children[0])
                sim = sim_par_new(p.eid, ele[0], reference_edges, 0.5, eid2embed, eidpair2PPMI, embed_dim=100, DEBUG=False)
#                 sim = sim_par_new(p.eid, ele[0], obtainReferenceEdges(), 0.5, eid2embed, eidpair2PPMI, embed_dim=100,
#                                     DEBUG=False)

                print(p.ename, ":", eid2ename[newChildEid], sim)

                if sim >  max_sim:
                    max_sim = sim
                    best_parent = p

            print("=== attaching", eid2ename[ele[0]], " to ", best_parent.ename)
            if best_parent is not None:
                newChild = TreeNode(parent=best_parent, level=level, eid=newChildEid, ename=eid2ename[newChildEid],
                                  isUserProvided=False, confidence_score=confidence_score,
                                  max_children=level2max_children[p.level+1]) 
                best_parent.addChildren([newChild])
                
                
rootNode.printSubtree(0)
rootNode.saveToFile(folder + "../results/baseline.txt" )

