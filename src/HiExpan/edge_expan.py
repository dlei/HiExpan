'''
__author__: Jiaming Shen
__description__: Given a collection of (A,B) edges and a source node C, find the most suitable D such that
    A:B = C:D using embedding
__latest_update__: 09/06/2017
'''
import numpy as np
import time
import sys
from collections import defaultdict
from scipy.spatial import distance

def load_entity_embedding(inputFileName, dim=100):
    '''
    Load the entity embedding with word as context
    '''
    M = dim # dimensionality of embedding
    eid2embed = {}
    embed_matrix = []
    cnt = 0
    eid2rank = {}
    rank2eid = {}
    with open(inputFileName,"r") as fin:
        start = time.time()
        for line in fin:
            if cnt % 100000 == 0 and cnt != 0:
                print("Finish loading %s entity-word embeddings" % cnt)
            # if cnt == 0: # skip-first line
            #     cnt += 1
            #     continue

            # Assume no header
            seg = line.strip().split()        
            eid2rank[int(seg[0])] = cnt
            rank2eid[cnt] = int(seg[0])
            
            embed = np.array([float(ele) for ele in seg[1:]])
            embed_matrix.append(embed)
            eid2embed[int(seg[0])] = embed.reshape(1,M)
            
            cnt += 1
        end = time.time()
        
        embed_matrix_array = np.array(embed_matrix)
        print("Finish load entity embedding files, using time %s (seconds)" % (end-start))

    return (eid2embed, embed_matrix, eid2rank, rank2eid, embed_matrix_array)

def load_entity2id_map(inputFileName):
    ename2eid = defaultdict()
    eid2ename = defaultdict()

    start = time.time()
    with open(inputFileName,"r") as fin:
        for line in fin:
            line = line.strip()
            seg = line.split("\t")
            ename2eid[seg[0]] = int(seg[1])
            eid2ename[int(seg[1])] = seg[0]
        end = time.time()
        print("Finish load ename and eid mapping file, using time %s (seconds)" % (end-start))  

    return (ename2eid, eid2ename)

def find_most_similar_fast(target_embed, embed_matrix_array, rank2eid, eid2ename, topK = 1):
    '''
    target_eid
    eid2embed: key = eid (int), value is the embedding of eid ( array of dimension (1, M))
    usage: find_most_similar_fast(eid2embed[114450], embed_matrix_array, rank2eid, eid2ename, topK = 3)
    '''
    dist_matrix = distance.cdist(target_embed, embed_matrix_array, 'cosine')          
    sorted_rank = np.argpartition(dist_matrix,topK) # ascending order

    results = []
    for i in range(topK):
        rank = sorted_rank[0][i] 
        similarity = 1.0 - dist_matrix[0][rank]
        eid = rank2eid[rank]
        results.append([eid, eid2ename[eid], similarity])
    
    results = sorted(results, key = lambda x:-x[2])
    ## max_normalization
    max_similarity = results[0][2]
    for ele in results:
      ele[2] /= max_similarity
    return results

def find_target_embedding(seed_parent_id, seed_children_id, target_id, eid2embed, embed_dim=100):
    '''
    :param seed_parent_id:
    :param seed_children_id:
    :param target_id:
    :param eid2embed:
    :param embed_dim:
    :return:
    '''
    offset = np.zeros([1,embed_dim])
    for children_id in seed_children_id:
        offset += (eid2embed[seed_parent_id] - eid2embed[children_id])
    offset /= (len(seed_children_id))
    target_embed = eid2embed[target_id] - offset
    return target_embed

def edge_expan(seed_parent_id, seed_children_ids, target_parent_id, eid2embed,
               embed_matrix_array, rank2eid, eid2ename, embed_dim=100, topK=5):
    target_embedding = find_target_embedding(seed_parent_id, seed_children_ids, target_parent_id, eid2embed, embed_dim)
    expanded_eids = find_most_similar_fast(target_embedding, embed_matrix_array, rank2eid, eid2ename, topK)
    return expanded_eids

def find_target_embedding_using_edges(reference_edges, target_id, eid2embed, embed_dim=100):
    '''

    :param reference_edges: a list of (parent, child) eids
    :param target_id:
    :param eid2emed:
    :param embed_dim:
    :return:
    '''
    offset = np.zeros([1, embed_dim])
    for edge in reference_edges:
        offset += (eid2embed[edge[0]] - eid2embed[edge[1]])
    offset /= (len(reference_edges))
    target_embed = eid2embed[target_id] - offset
    return target_embed

def edge_expan_using_edges(reference_edges, target_parent_id, eid2embed,
               embed_matrix_array, rank2eid, eid2ename, embed_dim=100, topK=5):
    target_embedding = find_target_embedding_using_edges(reference_edges, target_parent_id, eid2embed, embed_dim)
    ## extract topK+1 entities in case one of the most similar entity is the target_parent node itself
    expanded_eids = find_most_similar_fast(target_embedding, embed_matrix_array, rank2eid, eid2ename, topK+1)
    res = []
    for ele in expanded_eids:
        if ele[0] != target_parent_id:
            res.append(ele)
    ## in case none of the expanded node is target_parent_id, select only the topK ones
    if len(res) > topK:
        res = res[:topK]
    return res

if __name__ == '__main__':
    data = sys.argv[1] # wiki
    inputEntityEmbeddingFile = "../../data/"+data+"/intermediate/entity_word2vec.emb"
    inputEidMapFile = "../../data/"+data+"/intermediate/entity2id.txt"
    (eid2embed, embed_matrix, eid2rank, rank2eid, embed_matrix_array) = load_entity_embedding(inputEntityEmbeddingFile)
    (ename2eid, eid2ename) = load_entity2id_map(inputEidMapFile)

    ## Following are US States ids
    two_seeds_queries = [[290971, 656628], [293014, 411194], [341991, 112564], [604241, 449086], [456059, 476415]]
    three_seeds_queries = [[290971, 656628, 293014], [411194, 341991, 112564], [604241, 449086, 456059],
                           [476415, 290971, 656628], [293014, 411194, 341991]]
    four_seeds_queries = [[290971, 656628, 293014, 411194], [341991, 112564, 604241, 449086],
                          [456059, 476415, 290971, 656628], [293014, 411194, 341991, 112564],
                          [604241, 449086, 456059, 476415]]
    five_seeds_queries = [[290971, 656628, 293014, 411194, 341991], [112564, 604241, 449086, 456059, 476415],
                          [656628, 293014, 411194, 341991, 112564], [290971, 604241, 449086, 456059, 476415],
                          [293014, 411194, 341991, 112564, 604241]]
    six_seeds_queries = [[290971, 656628, 293014, 411194, 341991, 112564],
                         [604241, 449086, 456059, 476415, 290971, 656628],
                         [293014, 411194, 341991, 112564, 604241, 449086],
                         [456059, 476415, 290971, 656628, 293014, 411194],
                         [341991, 112564, 604241, 449086, 456059, 476415]]

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


    reference_edges = [(USA_id, state_id) for state_id in six_seeds_queries[0]]
    country_ids = [Canada_id, Japan_id, China_id, India_id, Germany_id, Russia_id, Australia_id, France_id, Spain_id,
                   Italy_id]
    for country_id in country_ids:
        print(country_id, eid2ename[country_id])
        
        # target_embedding = find_target_embedding(USA_id, USA_states_ids, country_id, eid2embed, embed_dim = 100)
        # expanded_provinces = find_most_similar_fast(target_embedding, embed_matrix_array, rank2eid, eid2ename, topK = 10)
        # expanded_provinces = edge_expan(USA_id, USA_states_ids, country_id, eid2embed,
        #                                embed_matrix_array, rank2eid, eid2ename)
        expanded_provinces = edge_expan_using_edges(reference_edges, country_id, eid2embed, embed_matrix_array,
                                                    rank2eid, eid2ename, embed_dim=100, topK = 10)
        for expanded_province in expanded_provinces:
            print(expanded_province)

        print("="*80)

