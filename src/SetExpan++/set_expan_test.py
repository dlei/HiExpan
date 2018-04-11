'''
__author__: Jiaming Shen
__description__: The testing function for running SetExpan algorithm
__latest_update__: 10/12/2017
'''
import util
import set_expan

## Setting global versions
FLAGS_USE_TYPE=True

## Loading Corpus
data = "wiki"
print('dataset:%s' % data)
# data = "wiki_ellen" # test the original old dataset
folder = '../../data/'+data+'/intermediate/'
print('loading eid and name maps')
eid2ename, ename2eid = util.loadEidToEntityMap(folder+'entity2id.txt') #entity2id.txt
print('loading eid and skipgram maps')
eid2patterns, pattern2eids = util.loadFeaturesAndEidMap(folder+'eidSkipgramCounts.txt') #eidSkipgramCount.txt
print('loading skipgram strength map')
eidAndPattern2strength = util.loadWeightByEidAndFeatureMap(folder+'eidSkipgram2TFIDFStrength.txt', idx=-1) #(eid, feature, weight) file
if (FLAGS_USE_TYPE):
  print('loading eid and type maps')
  eid2types, type2eids = util.loadFeaturesAndEidMap(folder+'eidTypeCounts.txt') #eidTypeCount.txt
  print('loading type strength map')
  eidAndType2strength = util.loadWeightByEidAndFeatureMap(folder+'eidType2TFIDFStrength.txt', idx=-1) #(eid, feature, weight) file

## Start set expansion
userInput = ["United States", "China", "Japan", "germany", "England", "Russia", "India"]
seedEidsWithConfidence = [(ename2eid[ele.lower()], 0.0) for ele in userInput]

# seedEidsWithConfidence_dblp_method_single = [(7649, 0.0), (2299, 0.0), (9784, 0.0), (10554, 0.0), (7963, 0.0),
#                                             (6101, 0.0), (13857, 0.0), (2575, 0.0), (1959, 0.0), (4395, 0.0),
#                                             (11507, 0.0), (12794, 0.0), (8143, 0.0), (7237, 0.0), (2668, 0.0),
#                                             (4928, 0.0), (8070, 0.0), (9766, 0.0), (5911, 0.0), (11497, 0.0),
#                                             (5869, 0.0), (3690, 0.0), (9647, 0.0), (757, 0.0), (10587, 0.0),
#                                             (5713, 0.0), (1150, 0.0), (14105, 0.0), (3548, 0.0), (11533, 0.0),
#                                             (5479, 0.0), (4614, 0.0), (13030, 0.0), (14837, 0.0), (8232, 0.0)]

# seedEidsWithConfidence_dblp_method_class = [(9012, 0.0), (652, 0.0), (13169, 0.0), (15819, 0.0), (14650, 0.0),
#                                             (15554, 0.0), (3334, 0.0), (14542, 0.0), (3044, 0.0), (9847, 0.0),
#                                             (9826, 0.0), (9619, 0.0), (11985, 0.0), (6825, 0.0), (2767, 0.0),
#                                             (9152, 0.0), (12024, 0.0), (10105, 0.0), (3848, 0.0), (4810, 0.0),
#                                             (11944, 0.0), (6319, 0.0), (126, 0.0)]
negativeSeedEids = set()
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
    FLAGS_VERBOSE=True,
    FLAGS_DEBUG=True
)
print("=== In test case ===")
for ele in expandedEidsWithConfidence:
  print("eid=", ele[0], "ename=", eid2ename[ele[0]], "confidence_score=", ele[1])

with open("./test_setexpan.txt", "w") as fout:
  for ele in expandedEidsWithConfidence:
    fout.write("eid=" + str(ele[0]) + "\t" + "ename=" + eid2ename[ele[0]] + "\t" + "confidence_score=" + str(ele[1]))
    fout.write("\n")
