'''
__author__: Jiaming Shen
__description__: Given a collection of (A,B) edges and a source node C where A,B,C are eids,
  find the most suitable D such that A:B = C:D using relational skipgrams
__latest_update__: 08/31/2017
'''
import sys
import util
from collections import defaultdict

# Relational skipgrams that can cover [FLAGS_RSG_POPULARITY_LOWER, FLAGS_RSG_POPULARITY_UPPER] numbers of
# entities will be retained
FLAGS_RSG_POPULARITY_LOWER = 0
FLAGS_RSG_POPULARITY_UPPER = 1000000
# FLAGS_TOP_K_RSG is the maximum number of relational skipgrams that wil be selected to calculate the
# distributional similarity.
FLAGS_TOP_K_RSG = 1000000
# FLAGS_TOP_K_EID is the number of candidate entity pairs that we will return
FLAGS_TOP_K_EID = 5

# TODO: later we should move this function and the similar function in set_expan.py into util.py
def getFeatureSim(candidatePair, seedPair, weightByEidPairAndSkipgramMap, coreFeatures):
  simWithSeed = [0.0, 0.0]
  for f in coreFeatures:
    if (candidatePair, f) in weightByEidPairAndSkipgramMap:
      weight_eid = weightByEidPairAndSkipgramMap[(candidatePair, f)]
    else:
      weight_eid = 0.0
    if (seedPair, f) in weightByEidPairAndSkipgramMap:
      weight_seed = weightByEidPairAndSkipgramMap[(seedPair, f)]
    else:
      weight_seed = 0.0
    # Weighted Jaccard similarity
    simWithSeed[0] += min(weight_eid, weight_seed)
    simWithSeed[1] += max(weight_eid, weight_seed)
  if simWithSeed[1] == 0:
    res = 0.0
  else:
    res = simWithSeed[0]*1.0/simWithSeed[1]
  return res

def tuple_expan(target_eid, seedEidPairs, eidToEntityMap, skipgramsByEidPairMap, eidPairsBySkipgramMap,
                weightByEidPairAndSkipgramMap, topK=5, FLAGS_DEBUG=False):
  '''

  :param target_eid:
  :param seedEidPairs: a list of eid pairs (a list of int tuple)
  :param eidToEntityMap: dict(int) -> string
  :param skipgramsByEidPairMap: defaultdict((int, int)) -> set(string)
  :param eidPairsBySkipgramMap: defaultdict(string) -> set((int, int))
  :param weightByEidPairAndSkipgramMap: dict((int, int), string) -> float

  :return: a list of triplet, each of it is (eid, ename, strength)
  '''
  relationalSkipgram2score = defaultdict(float)
  for eidpair in seedEidPairs:
    for relational_sg in skipgramsByEidPairMap[eidpair]:
      relational_sg_popularity = len(eidPairsBySkipgramMap[relational_sg])
      ## include only the relational skipgram that matches suitable number of entity pairs
      if relational_sg_popularity < FLAGS_RSG_POPULARITY_LOWER or relational_sg_popularity > FLAGS_RSG_POPULARITY_UPPER:
        continue
      else:
        relationalSkipgram2score[relational_sg] += weightByEidPairAndSkipgramMap[(eidpair, relational_sg)]
  if FLAGS_DEBUG:
    print("Number of candidate relational skipgrams = %s" % len(relationalSkipgram2score))
    # for k,v in relationalSkipgram2score.items():
    #   print(k,v)


  max_num_of_relational_sg = len(relationalSkipgram2score)
  coreRelationalSkipgrams = [ele[0] for ele in sorted(relationalSkipgram2score.items(),
                                   key = lambda x:-x[1])[:max(max_num_of_relational_sg, FLAGS_TOP_K_RSG)]]

  candidate_pairs = set()
  for coreRelationalSkipgram in coreRelationalSkipgrams:
    for eidPair in eidPairsBySkipgramMap[coreRelationalSkipgram]:
      if eidPair[0] == target_eid:
        candidate_pairs.add(eidPair)
  if FLAGS_DEBUG:
    print("Number of candidate pairs = %s" % len(candidate_pairs))

  candidatePair2score = defaultdict(float)
  for candidatePair in candidate_pairs:
    for seedPair in seedEidPairs:
      candidatePair2score[candidatePair] += getFeatureSim(candidatePair, seedPair, weightByEidPairAndSkipgramMap,
                                                         coreRelationalSkipgrams)
  res = []
  if (len(candidatePair2score) == 0):
    return res

  cnt = 0
  max_strength = max(candidatePair2score.values())
  for candidatePair in sorted(candidatePair2score.items(), key = lambda x:-x[1]):
    eid = candidatePair[0][1]
    ename = eidToEntityMap[eid]
    strength = candidatePair[1]
    res.append([eid, ename, 1.0*strength/max_strength])
    cnt += 1
    if cnt >= topK:
      break

  return res



if __name__ == "__main__":
  # corpusName = sys.argv[1]
  corpusName = "wiki"
  folderPath = '../../data/' + corpusName + '/intermediate/'

  print('loading eidToEntityMap...')
  eid2ename, ename2eid = util.loadEidToEntityMap(folderPath+'entity2id.txt') #entity2id.txt

  print('loading skipgramsByEidMap, eidsBySkipgramMap...')
  skipgramsByEidPairMap, eidPairsBySkipgramMap = util.loadFeaturesAndEidPairMap(
    folderPath+'eidPairRelationalSkipgramsCounts.txt'
  ) #eidPairRelationalSkipgramsCounts.txt

  print('loading weightByEidAndSkipgramMap...')
  weightByEidPairAndSkipgramMap = util.loadWeightByEidPairAndFeatureMap(
    folderPath+'eidPairRelationalSkipgrams2TFIDFStrength.txt'
  ) #(eid1, eid2, feature, weight) file

  USA_states_ids = [290971, 656628, 293014, 411194, 341991, 112564, 604241, 449086, 456059, 476415]
  USA_id = 644125
  # Canada_id = 114450
  # Japan_id = 309528
  # China_id = 132050
  # Germany_id = 240965
  # England_id = 200192
  # Russia_id = 531974
  # India_id = 292563

  Australia_id = 64527
  France_id = 222703
  Spain_id = 574965
  Italy_id = 288516
  Switzerland_id = 594159
  Belgium_id = 80983
  Scotland_id = 548525
  Denmark_id = 170137
  New_Zealand_id = 441974
  Poland_id = 487833
  Sweden_id = 593507
  Austria_id = 65110
  Romania_id = 525397
  Norway_id = 451161
  Finland_id = 216697
  Hungary_id = 285145
  Portugal_id = 490894
  South_Africa_id = 572164
  Mexico_id = 408545
  Brazil_id = 99925
  Turkey_id = 636042
  Ireland_id = 297492
  Estonia_id = 204669
  Bulgaria_id = 106876
  Greece_id = 253902
  Ukraine_id = 641844
  Great_Britain_id = 253035
  United_Kingdom_id = 643778
  Slovenia_id = 567541
  Croatia_id = 153539
  Serbia_id = 553311
  Slovakia_id = 567503
  Lithuania_id = 370946
  The_Netherlands_id = 613621
  Netherlands_id = 439239
  Israel_id = 299639
  Iceland_id = 289535
  Holland_id = 279382
  Luxembourg_id = 381615
  Argentina_id = 55823
  Thailand_id = 604663
  Malta_id = 388820
  Bosnia_and_Herzegovina_id = 97358
  Albania_id = 34131
  Singapore_id = 563302
  Latvia_id = 360492
  Macedonia_id = 384805
  Montenegro_id = 421466
  Moldova_id = 419869
  Czech_Republic_id = 156568

  reference_edges = [(USA_id, state_id) for state_id in USA_states_ids]
  # country_ids = [USA_id, Canada_id, Japan_id, China_id, Germany_id, England_id, Russia_id, India_id]
  country_ids = [Australia_id,France_id, Spain_id, Italy_id, Switzerland_id, Belgium_id, Scotland_id,
                 Denmark_id, New_Zealand_id, Poland_id, Sweden_id, Austria_id, Romania_id, Norway_id,
                 Finland_id, Hungary_id, Portugal_id, South_Africa_id, Mexico_id, Brazil_id, Turkey_id,
                 Ireland_id, Estonia_id, Bulgaria_id, Greece_id, Ukraine_id, Great_Britain_id,
                 United_Kingdom_id, Slovenia_id, Croatia_id, Serbia_id, Slovakia_id, Lithuania_id,
                 The_Netherlands_id, Netherlands_id, Israel_id, Iceland_id, Holland_id, Luxembourg_id,
                 Argentina_id, Thailand_id, Malta_id, Bosnia_and_Herzegovina_id, Albania_id, Singapore_id,
                 Latvia_id, Macedonia_id, Montenegro_id, Moldova_id, Czech_Republic_id]

  outputFilePath = '../../data/' + corpusName + '/intermediate/relation-is-state-of.txt'
  with open(outputFilePath, "w") as fout:
    for country_id in country_ids:
      print(country_id, eid2ename[country_id])

      expanded_provinces = tuple_expan(country_id, reference_edges, eid2ename, skipgramsByEidPairMap,
                                       eidPairsBySkipgramMap, weightByEidPairAndSkipgramMap,
                                       topK=5, FLAGS_DEBUG=True)
      for expanded_province in expanded_provinces:
        print(expanded_province)
        fout.write(expanded_province[1] + "\t" + str(expanded_province[0])+"\t" + eid2ename[country_id] +
                   "\t" + str(country_id)+"\n")
    print("=" * 80)

