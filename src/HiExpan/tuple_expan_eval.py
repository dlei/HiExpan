'''
__author__: Jiaming Shen
__description__: Evaluate the performance of depth expansion using relational skipgrams, embedding offset
__latest_update__: 09/04/2017
'''
import sys
import util
import tuple_expan
import edge_expan
from collections import defaultdict

FLAGS_VERBOSE = False
FLAGS_TOPK = 10

if __name__ == "__main__":
  corpusName = sys.argv[1]
  methodName = sys.argv[2]

  folderPath = '../../data/' + corpusName + '/intermediate/'
  print('loading eidToEntityMap...')
  eid2ename, ename2eid = util.loadEidToEntityMap(folderPath+'entity2id.txt') #entity2id.txt

  print("loading ground truth relation")
  # evalFilePath = "../../data/" + corpusName + "/evaluation/is-state-of_full.tsv"
  evalFilePath = "../../data/" + corpusName + "/evaluation/isA_relations.tsv"
  gt_relations = util.loadGroundTruthRelations(evalFilePath, header=True)
  print("Number of ground truth relations = %s" % len(gt_relations))

  if methodName == "embedding":
    print('loading embedding files')
    inputEntityEmbeddingFile = "../../data/" + corpusName + "/intermediate/entity_word2vec.emb"
    (eid2embed, embed_matrix, eid2rank, rank2eid, embed_matrix_array) = \
      edge_expan.load_entity_embedding(inputEntityEmbeddingFile)
  elif methodName == "relational_skipgram":
    print('loading skipgramsByEidMap, eidsBySkipgramMap...')
    skipgramsByEidPairMap, eidPairsBySkipgramMap = util.loadFeaturesAndEidPairMap(
      folderPath+'eidPairRelationalSkipgramsCounts.txt') #eidPairRelationalSkipgramsCounts.txt

    print('loading weightByEidAndSkipgramMap...')
    weightByEidPairAndSkipgramMap = util.loadWeightByEidPairAndFeatureMap(
      folderPath+'eidPairRelationalSkipgrams2TFIDFStrength.txt' ) #(eid1, eid2, feature, weight) file
  elif methodName == "mix_intersection":
    print('loading embedding files')
    inputEntityEmbeddingFile = "../../data/" + corpusName + "/intermediate/entity_word2vec.emb"
    (eid2embed, embed_matrix, eid2rank, rank2eid, embed_matrix_array) = edge_expan.load_entity_embedding(
      inputEntityEmbeddingFile)

    print('loading skipgramsByEidMap, eidsBySkipgramMap...')
    skipgramsByEidPairMap, eidPairsBySkipgramMap = util.loadFeaturesAndEidPairMap(
      folderPath + 'eidPairRelationalSkipgramsCounts.txt')  # eidPairRelationalSkipgramsCounts.txt

    print('loading weightByEidAndSkipgramMap...')
    weightByEidPairAndSkipgramMap = util.loadWeightByEidPairAndFeatureMap(
      folderPath + 'eidPairRelationalSkipgrams2TFIDFStrength.txt')  # (eid1, eid2, feature, weight) file
  else:
    print("[ERROR] Unsupported method: %s" % methodName)
    exit(-1)


  USA_states_ids = [290971, 656628, 293014, 411194, 341991, 112564, 604241, 449086, 456059, 476415]
  USA_id = 644125

  Canada_id = 114450
  Japan_id = 309528
  China_id = 132050
  Germany_id = 240965
  # England_id = 200192
  Russia_id = 531974
  India_id = 292563
  Australia_id = 64527
  France_id = 222703
  Spain_id = 574965
  Italy_id = 288516
  # Switzerland_id = 594159
  # Belgium_id = 80983
  Scotland_id = 548525
  # Denmark_id = 170137
  # New_Zealand_id = 441974
  Poland_id = 487833
  Sweden_id = 593507
  # Austria_id = 65110
  Romania_id = 525397
  Norway_id = 451161
  # Finland_id = 216697
  # Hungary_id = 285145
  # Portugal_id = 490894
  South_Africa_id = 572164
  Mexico_id = 408545
  Brazil_id = 99925
  # Turkey_id = 636042
  Ireland_id = 297492
  # Estonia_id = 204669
  # Bulgaria_id = 106876
  # Greece_id = 253902
  # Ukraine_id = 641844
  # Great_Britain_id = 253035
  # United_Kingdom_id = 643778
  # Slovenia_id = 567541
  # Croatia_id = 153539
  # Serbia_id = 553311
  # Slovakia_id = 567503
  # Lithuania_id = 370946
  # The_Netherlands_id = 613621
  # Netherlands_id = 439239
  # Israel_id = 299639
  # Iceland_id = 289535
  # Holland_id = 279382
  # Luxembourg_id = 381615
  Argentina_id = 55823
  # Thailand_id = 604663
  # Malta_id = 388820
  # Bosnia_and_Herzegovina_id = 97358
  # Albania_id = 34131
  # Singapore_id = 563302
  # Latvia_id = 360492
  # Macedonia_id = 384805
  # Montenegro_id = 421466
  # Moldova_id = 419869
  # Czech_Republic_id = 156568


  # country_ids = [USA_id, Canada_id, Japan_id, China_id, Germany_id, England_id, Russia_id, India_id]
  # country_ids = [Australia_id,France_id, Spain_id, Italy_id, Switzerland_id, Belgium_id, Scotland_id,
  #                Denmark_id, New_Zealand_id, Poland_id, Sweden_id, Austria_id, Romania_id, Norway_id,
  #                Finland_id, Hungary_id, Portugal_id, South_Africa_id, Mexico_id, Brazil_id, Turkey_id,
  #                Ireland_id, Estonia_id, Bulgaria_id, Greece_id, Ukraine_id, Great_Britain_id,
  #                United_Kingdom_id, Slovenia_id, Croatia_id, Serbia_id, Slovakia_id, Lithuania_id,
  #                The_Netherlands_id, Netherlands_id, Israel_id, Iceland_id, Holland_id, Luxembourg_id,
  #                Argentina_id, Thailand_id, Malta_id, Bosnia_and_Herzegovina_id, Albania_id, Singapore_id,
  #                Latvia_id, Macedonia_id, Montenegro_id, Moldova_id, Czech_Republic_id]
  country_ids = [Canada_id, Japan_id, China_id, India_id, Germany_id, Russia_id, Australia_id, France_id,
                 Spain_id, Italy_id]
  country_ids_difficult = [Scotland_id, Poland_id, Sweden_id, Romania_id, Norway_id, South_Africa_id, Mexico_id,
                           Brazil_id, Argentina_id, Ireland_id]

  two_seeds_queries = [[290971, 656628], [293014, 411194], [341991, 112564], [604241, 449086], [456059, 476415]]
  three_seeds_queries = [[290971, 656628, 293014], [411194, 341991, 112564], [604241, 449086, 456059],
                         [476415, 290971, 656628], [293014, 411194, 341991]]
  four_seeds_queries = [[290971, 656628, 293014, 411194], [341991, 112564, 604241, 449086],
                        [456059, 476415, 290971, 656628], [293014, 411194, 341991, 112564],
                        [604241, 449086, 456059, 476415]]
  five_seeds_queries = [[290971, 656628, 293014, 411194, 341991], [112564, 604241, 449086, 456059, 476415],
                        [656628, 293014, 411194, 341991, 112564], [290971, 604241, 449086, 456059, 476415],
                        [293014, 411194, 341991, 112564, 604241]]
  six_seeds_queries =[[290971, 656628, 293014, 411194, 341991, 112564],[604241, 449086, 456059, 476415, 290971, 656628],
                      [293014, 411194, 341991, 112564, 604241, 449086],[456059, 476415, 290971, 656628, 293014, 411194],
                      [341991, 112564, 604241, 449086, 456059, 476415]]

  reference_edges = [(USA_id, state_id) for state_id in USA_states_ids]
  all_queries = [two_seeds_queries, three_seeds_queries, four_seeds_queries, five_seeds_queries, six_seeds_queries]

  # change the input reference children, we generate a "query"
  for queries in all_queries:
    print("="*80)
    print("=== Test queries with %s number of seed entities ===" % len(queries[0]))
    ## each query type has an aggregated precision at each position
    rank2precision_list = defaultdict(list) # key: rank (one-indexed), value: a list of precision, each element for one query
    for query in queries:
      reference_edges = [(USA_id, state_id) for state_id in query]
      ## each query has its precision at each position
      # precisions = [0.0, 0.0, 0.0, 0.0, 0.0]
      precisions = [0.0] * FLAGS_TOPK
      ## each query is tested on multiple countries
      for country_id in country_ids_difficult:
        if methodName == "relational_skipgram":
          expanded_provinces = tuple_expan.tuple_expan(country_id, reference_edges, eid2ename, skipgramsByEidPairMap,
                                                       eidPairsBySkipgramMap, weightByEidPairAndSkipgramMap,
                                                       topK=FLAGS_TOPK, FLAGS_DEBUG=False)
        elif methodName == "embedding":
          expanded_provinces = edge_expan.edge_expan_using_edges(reference_edges, country_id, eid2embed,
                                                                 embed_matrix_array, rank2eid, eid2ename, embed_dim=100,
                                                                 topK=FLAGS_TOPK)
        elif methodName == "mix_intersection":
          ### First extract topK * 3 entities using relational_skipgram
          expanded_provinces_relational_skipgram = tuple_expan.tuple_expan(country_id, reference_edges, eid2ename, skipgramsByEidPairMap,
                                                       eidPairsBySkipgramMap, weightByEidPairAndSkipgramMap,
                                                       topK=FLAGS_TOPK*3, FLAGS_DEBUG=False)
          ### Then extract topK * 3 entities using embedding
          expanded_provinces_embedding = edge_expan.edge_expan_using_edges(reference_edges, country_id, eid2embed,
                                                                 embed_matrix_array, rank2eid, eid2ename, embed_dim=100,
                                                                 topK=FLAGS_TOPK*3)
          expanded_provinces = []
          tmp_candidate = []
          rank = 0
          for candidate in expanded_provinces_relational_skipgram:
            rank += 1
            if candidate in expanded_provinces_embedding:
              expanded_provinces.append(candidate)
            else:
              tmp_candidate.append(candidate)
              # if rank <= FLAGS_TOPK :
              #   print("Top candidates by relational skipgram that is not in embeddings topK",
              #         candidate[0], eid2ename[candidate[0]], country_id, eid2ename[country_id])
          if len(expanded_provinces) >= FLAGS_TOPK:
            expanded_provinces = expanded_provinces[:FLAGS_TOPK]
          else:
            num_add_in = FLAGS_TOPK - len(expanded_provinces)
            expanded_provinces.extend(tmp_candidate[:num_add_in])
        else:
          print("[ERROR] Unsupported method")

        expanded_province_correctness = [0.0] * FLAGS_TOPK
        for i in range(len(expanded_provinces)):
          province_id = expanded_provinces[i][0]
          if (province_id, country_id) in gt_relations:
            expanded_province_correctness[i] = 1.0
          else:
            if FLAGS_VERBOSE:
              print("Wrong relation:", (province_id, eid2ename[province_id], country_id, eid2ename[country_id]))
        for i in range(FLAGS_TOPK):
          precision_at_i = sum(expanded_province_correctness[:(i+1)]) / (i+1)
          precisions[i] += precision_at_i

      avg_precisions = [ele/len(country_ids) for ele in precisions]

      for rank in range(FLAGS_TOPK):
        rank2precision_list[rank+1].append(avg_precisions[rank])

    print("[Results]")
    for rank in range(FLAGS_TOPK):
      precisions_list = rank2precision_list[rank+1]
      print("Precision@%s" % (rank+1), precisions_list, sum(precisions_list) / len(precisions_list))
