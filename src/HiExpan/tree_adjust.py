'''
__author__: Jiaming Shen
__description__: Implement tree global adjustment algorithm
__latest_update__: 02/06/2017
'''
import sys
import util
import math
import edge_expan
import tuple_expan
import argparse
import pickle
import time
import numpy as np
from tqdm import tqdm
from itertools import chain
from itertools import combinations
from collections import defaultdict
from scipy.spatial import distance
from sklearn.preprocessing import normalize
from numpy.linalg import inv
from tree_node import TreeNode
from set_expan import setExpan, getCombinedWeightByFeatureMap, getFeatureSim

FLAGS_USE_TYPE = True
FLAGS_SG_POPULARITY_LOWER = 3
FLAGS_SG_POPULARITY_UPPER = 30
FLAGS_INITIAL_EDGE = 1
load_pickle = True

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

def sim_sib(eid1, eid2, alpha, featuresByEidMap, weightByEidAndFeatureMap, pattern2eids, eid2embed, eid2types,
            eidAndType2strength, topK_quality_sg=150, DEBUG=False):
  '''
  skipgram-similarity
  '''
  skipgram_features = getCombinedWeightByFeatureMap([eid1, eid2], featuresByEidMap, weightByEidAndFeatureMap)

  redundantSkipgrams = set()
  for i in skipgram_features:
    size = len(pattern2eids[i])
  if size < FLAGS_SG_POPULARITY_LOWER or size > FLAGS_SG_POPULARITY_UPPER:
    redundantSkipgrams.add(i)
  for sg in redundantSkipgrams:
    del skipgram_features[sg]

  if topK_quality_sg < 0:
    quality_skipgram_features = skipgram_features
  else:
    quality_skipgram_features = {}
    for ele in sorted(skipgram_features.items(), key=lambda x: -x[1])[0:topK_quality_sg]:
      quality_skipgram_features[ele[0]] = ele[1]

  skipgram_sim = getFeatureSim(eid1, eid2, weightByEidAndFeatureMap, quality_skipgram_features)
  if skipgram_sim < 0:
    skipgram_sim = 0

  '''
  embedding-similarity
  '''
  embedding_sim = float(1.0 - distance.cdist(eid2embed[eid1], eid2embed[eid2], 'cosine'))
  if embedding_sim < 0:
    embedding_sim = 0

  '''
  type-similarity
  '''
  type_features = getCombinedWeightByFeatureMap([eid1, eid2], eid2types, eidAndType2strength)
  type_sim = getFeatureSim(eid1, eid2, eidAndType2strength, type_features)
  if type_sim < 0:
    type_sim = 0

  overall_sim = (skipgram_sim ** alpha) * (embedding_sim ** (1 - alpha))
      # overall_sim = (embedding_sim ** alpha) * (type_sim ** (1-alpha))
  if DEBUG:
    print("%.6f" % skipgram_sim, "%.6f" % embedding_sim, "%.6f" % type_sim, "%.6f" % overall_sim)
  return overall_sim

def obtainReferenceEdges(targetNode):
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

def adjust_taxonomy_one_level(parent_eids, children_eids, alpha_Y_content=0.5, alpha_W = 0.5):
  ### Parent-children content similarity matrix
  Y_content = []
  for i in tqdm(range(len(children_eids))):
    child_eid = children_eids[i][0]
    original_parent = children_eids[i][1]
    Y_i = []
    best_parent_idx = None
    best_parent_sim = -1e-10
    for j in range(len(parent_eids)):
      parent_eid = parent_eids[j]
      sim = sim_par_new(parent_eid, child_eid, reference_edges, 0.5, eid2embed, eidpair2PPMI, embed_dim=100,
                        DEBUG=False)
      if sim > best_parent_sim:
        best_parent_sim = sim
        best_parent_idx = j
      Y_i.append(sim)
    Y_content.append(Y_i)

  Y_content = np.array(Y_content)
  Y_content = normalize(Y_content, norm="l1", axis=1)

  print("Finish Construct Child-Parent Content Similarity Matrix")
  with open("./Y_content.pickle", "wb") as fout:
    pickle.dump(Y_content, fout, protocol=pickle.HIGHEST_PROTOCOL)

  ### Parent-child previous structure similarity
  Y_structure = []
  for i in tqdm(range(len(children_eids))):
    child_eid = children_eids[i][0]
    original_parent_eid = children_eids[i][1]
    Y_i = []
    for j in range(len(parent_eids)):
      if parent_eids[j] == original_parent_eid:
        Y_i.append(1.0)
      else:
        Y_i.append(0.0)
    Y_structure.append(Y_i)
  Y_structure = np.array(Y_structure)
  Y_structure = normalize(Y_structure, norm="l1", axis=1)

  print("Finish Construct Child-Parent Similarity Matrix")
  with open("./Y_structure.pickle", "wb") as fout:
    pickle.dump(Y_structure, fout, protocol=pickle.HIGHEST_PROTOCOL)

  ### Child-child similarity
  W = []
  for i in tqdm(range(len(children_eids))):
      W_i = []
      for j in range(len(children_eids)):
          if j == i:
              W_i.append(0.0)
          elif j < i:
              W_i.append(W[j][i])
          else:
              eid1 = children_eids[i][0]
              eid2 = children_eids[j][0]
              W_i.append(sim_sib(eid1, eid2, alpha_W, eid2patterns, eidAndPattern2strength, pattern2eids,
                                 eid2embed, eid2types, eidAndType2strength, topK_quality_sg=150))
      W.append(W_i)
  W = np.array(W)
  W = normalize(W, norm="l1", axis=1)
  print("Finish Construct Child-Child Similarity Matrix")
  with open("./W.pickle", "wb") as fout:
    pickle.dump(W, fout, protocol=pickle.HIGHEST_PROTOCOL)

  return (Y_content, Y_structure, W)

def load_pre_saved_matrix():
  with open("./Y_content.pickle", "rb") as fin:
    Y_content = pickle.load(fin)

  with open("./Y_structure.pickle", "rb") as fin:
    Y_structure = pickle.load(fin)

  with open("./W.pickle", "rb") as fin:
    W = pickle.load(fin)

  return (Y_content, Y_structure, W)

def return_F_star(Y, W, mu, mode="raw", l1_row_normalize=True, DEBUG=False):
  row_norm = np.sum(W, axis=1)
  normalizer = np.diag(row_norm ** -0.5)
  D = np.diag(row_norm)
  S = np.matmul(np.matmul(normalizer, W), normalizer)
  P = np.matmul(np.diag(row_norm ** -1), W)

  if l1_row_normalize:
    Y = normalize(Y, norm="l1", axis=1)
  n = Y.shape[0]
  c = Y.shape[1]
  alpha = 1.0 / (1.0 + mu)
  beta = 1.0 - alpha

  if mode == "raw":
    I = np.diag(np.ones(n))
    diff_kernal = inv(np.matrix(I - alpha * S))
    F_star = beta * np.matmul(diff_kernal, Y)
  elif mode == "stochastic-1":
    I = np.diag(np.ones(n))
    diff_kernal = inv(np.matrix(I - alpha * P))
    F_star = beta * np.matmul(diff_kernal, Y)
  elif mode == "stochastic-2":
    diff_kernal = inv(np.matrix(D - alpha * W))
    F_star = beta * np.matmul(diff_kernal, Y)
  else:
    print("Unsupported mode: %s" % mode)
    print("Please input one of %s" % ["raw", "stochastic-1", "stochastic-2"])
    return None
  return F_star

def return_F_star_two_Y(Y1, Y2, W, mu1, mu2, mode="raw", l1_row_normalize=True, DEBUG=False):
  row_norm = np.sum(W, axis=1)
  normalizer = np.diag(row_norm ** -0.5)
  D = np.diag(row_norm)
  S = np.matmul(np.matmul(normalizer, W), normalizer)
  P = np.matmul(np.diag(row_norm ** -1), W)

  n = Y1.shape[0]
  c = Y1.shape[1]
  alpha = 1.0 / (1.0 + mu1 + mu2)
  beta1 = mu1 / (1.0 + mu1 + mu2)
  beta2 = mu2 / (1.0 + mu1 + mu2)
  Y = beta1 * Y1 + beta2 * Y2
  if l1_row_normalize:
    Y = normalize(Y, norm="l1", axis=1)
  print("=== Y in return_F_star_two_Y ===\n", Y)

  if mode == "raw":
    I = np.diag(np.ones(n))
    diff_kernal = inv(np.matrix(I - alpha * S))
    F_star = np.matmul(diff_kernal, Y)
  elif mode == "stochastic-1":
    I = np.diag(np.ones(n))
    diff_kernal = inv(np.matrix(I - alpha * P))
    F_star = np.matmul(diff_kernal, Y)
  elif mode == "stochastic-2":
    diff_kernal = inv(np.matrix(D - alpha * W))
    F_star = np.matmul(diff_kernal, Y)
  else:
    print("Unsupported mode: %s" % mode)
    print("Please input one of %s" % ["raw", "stochastic-1", "stochastic-2"])
    return None
  return F_star

'''
Start of main functions
'''
parser = argparse.ArgumentParser(prog='tree_adjust.py', description='Run Tree adjustment algorithm')
parser.add_argument('-data', required=True, help='CorpusName.')
parser.add_argument('-taxonPrefix', required=True, help='Output Taxonomy Prefix')
parser.add_argument('-inputTaxon', required=False, help='Input taxonomy (in txt) before global adjustment')
parser.add_argument('-outputTaxon', required=False, help='Output taxonomy (in txt) after global adjustment')
args = parser.parse_args()
data = str(args.data)
taxonPrefix = str(args.taxonPrefix)
if args.inputTaxon:
  inputTaxon = str(args.inputTaxon)
  outputTaxon_pickle = inputTaxon[:-4]+".pickle"
else:
  inputTaxon = "../../data/" + data + "/results/taxonomy_%s_final.txt" % taxonPrefix
  inputTaxon_pickle = "../../data/" + data + "/results/taxonomy_%s_final.pickle" % taxonPrefix
if args.outputTaxon:
  outputTaxon = str(args.outputTaxon)
  outputTaxon_pickle = outputTaxon[:-4]+".pickle"
else:
  outputTaxon = "../../data/" + data + "/results/taxonomy_%s_final_adjusted.txt" % taxonPrefix
  outputTaxon_pickle = "../../data/" + data + "/results/taxonomy_%s_final_adjusted.pickle" % taxonPrefix


folder = '../../data/'+data+'/intermediate/'

'''
Load all data files
'''
print("=== Start loading all files ...... ===")
start = time.time()
print('loading eid and name maps')
eid2ename, ename2eid = util.loadEidToEntityMap(folder+'entity2id.txt') #entity2Eid.txt

## TODO: Later, we can merge the loadFeaturesAndEidMap and loadWeightByEidAndFeatureMap into one function
print('loading eid and skipgram maps')
eid2patterns, pattern2eids = util.loadFeaturesAndEidMap(folder+'eidSkipgramCounts.txt') #eidSkipgramCount.txt
print('loading skipgram strength map')
eidAndPattern2strength = util.loadWeightByEidAndFeatureMap(folder+'eidSkipgram2TFIDFStrength.txt', idx=-1) #(eid, feature, weight) file

print('loading eid pair document-level PPMI score')
eidpair2PPMI = util.loadEidDocPairPPMI(folder + 'eidDocPairPPMI.txt')

if (FLAGS_USE_TYPE):
    print('loading eid and type maps')
    eid2types, type2eids = util.loadFeaturesAndEidMap(folder+'eidTypeCounts.txt') #eidTypeCount.txt
    print('loading type strength map')
    eidAndType2strength = util.loadWeightByEidAndFeatureMap(folder+'eidType2TFIDFStrength.txt', idx=-1) #(eid, feature, weight) file

print("loading entity embedding files")
# inputEntityEmbeddingFile="../../data/"+data+"/intermediate/entity.emb"
inputEntityEmbeddingFile="../../data/"+data+"/intermediate/entity_word2vec.emb"
# inputEntityEmbeddingFile="../../data/"+data+"/intermediate/entity.emb_word2vec"
(eid2embed, embed_matrix, eid2rank, rank2eid, embed_matrix_array) = edge_expan.load_entity_embedding(inputEntityEmbeddingFile)

print('loading skipgramsByEidMap, eidsBySkipgramMap...')
skipgramsByEidPairMap, eidPairsBySkipgramMap = util.loadFeaturesAndEidPairMap(
    folder + 'eidPairRelationalSkipgramsCounts.txt')    # eidPairRelationalSkipgramsCounts.txt

print('loading weightByEidAndSkipgramMap...')
weightByEidPairAndSkipgramMap = util.loadWeightByEidPairAndFeatureMap(
    folder + 'eidPairRelationalSkipgrams2TFIDFStrength.txt')    # (eid1, eid2, feature, weight) file

end = time.time()
print("=== Finish loading all files. HaHaHa ===")
print("using time %s" % (end-start))

'''
Load input taxonomy before adjustment
'''
with open(inputTaxon_pickle, "rb") as fin:
  rootNode = pickle.load(fin)

eid2Treenodes = {}
parent_eids = [ele.eid for ele in rootNode.children]
parent_enames = [ele.ename for ele in rootNode.children]
print("!!!Number of candidate parents = %s" % len(parent_enames))
print("!!!Candidate parents:", parent_enames)
children_eids = []
children_enames = []
for parent_node in rootNode.children:
  eid2Treenodes[parent_node.eid] = parent_node
  for child_node in parent_node.children:
    eid2Treenodes[child_node.eid] = child_node
    children_eids.append((child_node.eid, parent_node.eid))
    children_enames.append((child_node.ename))
  # children_eids.extend([(ele.eid, parent_node.eid) for ele in parent_node.children])
  # children_enames.extend([ele.ename for ele in parent_node.children])
print("!!!Number of children = %s" % len(children_eids))
reference_edges = obtainReferenceEdges(rootNode.children[-1])
print("!!!Number of reference edges = %s" % len(reference_edges))

eid2Treenodes = {}
parent_eids = [ele.eid for ele in rootNode.children]
parent_enames = [ele.ename for ele in rootNode.children]
print(parent_eids)
print(parent_enames)
print("Number of parents = %s" % len(parent_enames))
children_eids = []
children_enames = []
for parent_node in rootNode.children:
  eid2Treenodes[parent_node.eid] = parent_node
  for child_node in parent_node.children:
    eid2Treenodes[child_node.eid] = child_node
    children_eids.append((child_node.eid, parent_node.eid))
    children_enames.append((child_node.ename))
  # children_eids.extend([(ele.eid, parent_node.eid) for ele in parent_node.children])
  # children_enames.extend([ele.ename for ele in parent_node.children])
print("children_eids[0]", children_eids[0])
print("Number of children = %s" % len(children_eids))
print(children_eids[0:10])

if load_pickle:
  (Y_content, Y_structure, W) = load_pre_saved_matrix()
else:
  (Y_content, Y_structure, W) = adjust_taxonomy_one_level(parent_eids, children_eids, alpha_Y_content=0.5, alpha_W=0.5)

Y_sparstiy = np.sum(Y_content == 0) /  np.prod(Y_content.shape)
print("Sparsity of matrix Y_content: %s" % Y_sparstiy)

Y_colum_sum = np.sum(Y_structure, axis=0)
print("Class popularity from Y_structure: %s" % Y_colum_sum)

row_norm = Y_content.sum(axis=1)
Y_row_sparsity = np.sum(row_norm == 0) /  np.prod(row_norm.shape)
print("Number of node without parent assignment: %s" % np.sum(row_norm == 0))
print("Percentage of node without parent assignments: %s" % Y_row_sparsity)

W_sparstiy = np.sum(W == 0) /  np.prod(W.shape)
print("Sparsity of matrix W: %s" % W_sparstiy)

'''
Start taxonomy adjustment 
'''
print("=== Y_content ===\n", Y_content)
F_star = return_F_star_two_Y(Y_structure, Y_content, W, mu1=0.5, mu2=5.0, l1_row_normalize=True)
assignments = np.argmax(F_star, axis=1)
changed_node_cnt = 0
for i in range(len(children_eids)):
  child_eid = children_eids[i][0]
  original_parent_eid = children_eids[i][1]
  current_parent_eid = parent_eids[assignments[i,0]]
  if original_parent_eid != current_parent_eid:
    changed_node_cnt += 1
    print("Entity: %s" % eid2ename[child_eid])
    print("\tChange from parent: %s --> %s" % (eid2ename[original_parent_eid], eid2ename[current_parent_eid]))
print("Number of nodes changed parent:", changed_node_cnt)

parent_eid2childrens = defaultdict(list)
for i in range(assignments.shape[0]):
  child_eid = children_eids[i][0]
  current_parent_eid = parent_eids[assignments[i,0]]
  parent_eid2childrens[current_parent_eid].append(eid2Treenodes[child_eid])
for parent_eid in parent_eids:
  eid2Treenodes[parent_eid].children = sorted(parent_eid2childrens[parent_eid], key=lambda x:-x.confidence_score)

print("Final Adjusted Taxonomy Tree")
rootNode.printSubtree(0)
# taxonomy_file_path = "../../data/" + data + "/results/taxonomy_%s_final_adjusted.txt" % taxonPrefix
# taxonomy_pickle_path = "../../data/" + data + "/results/taxonomy_%s_final_adjusted.pickle" % taxonPrefix
with open(outputTaxon_pickle, "wb") as fout:
  pickle.dump(rootNode, fout, protocol=pickle.HIGHEST_PROTOCOL)
rootNode.saveToFile(outputTaxon)







