'''
__author__: Jiaming Shen
__description__: Parameters used in HiExpan
__latest_update__: 02/09/2018
'''
from collections import defaultdict

def load_wiki_params():
  params = {}
  params['MAX_ITER_TREE'] = 5
  params['FLAGS_USE_TYPE'] = True
  params['FLAGS_DEBUG'] = True

  params['FLAGS_INITIAL_EDGE'] = 1
  params['FLAGS_INITIAL_NODE'] = 3
  params['FLAGS_DEPTH_EXPANSION_METHOD'] = "embedding"
  params['level2max_children'] = {-1: 15, 0:40, 1:25, 2:1e9, 3:1e9, 4:1e9, 5:1e9}
  params['level2source_weights'] = {
    -1: {"sg":5.0, "tp":0.0, "eb":0.0},
    0: {"sg":5.0, "tp":0.0, "eb":1.0},
    1: {"sg":5.0, "tp":0.0, "eb":1.0},
    2: {"sg":5.0, "tp":0.0, "eb":1.0},
  }
  params['level2max_expand_eids'] = {-1: 4, 0:5, 1:5, 2:5}
  params['level2reference_edges'] = defaultdict(list)
  params['FLAGS_USE_GLOBAL_REFERENCE_ENDGES'] = True
  params['FLAGS_ITERATIVELY_ADD_REFERENCE_EDGES'] = True
  return params

def load_dblp_params():
  params = {}
  params['MAX_ITER_TREE'] = 5
  params['FLAGS_USE_TYPE'] = True
  params['FLAGS_DEBUG'] = True

  params['FLAGS_INITIAL_EDGE'] = 1
  params['FLAGS_INITIAL_NODE'] = 3
  params['FLAGS_DEPTH_EXPANSION_METHOD'] = "embedding"
  params['level2max_children'] = {-1:10, 0:20, 1:40, 2:1e9, 3:1e9, 4:1e9, 5:1e9}
  params['level2source_weights'] = {
    -1: {"sg":5.0, "tp":5.0, "eb":1.0},
    0: {"sg":5.0, "tp":5.0, "eb":1.0},
    1: {"sg":5.0, "tp":5.0, "eb":1.0},
    2: {"sg":5.0, "tp":5.0, "eb":1.0},
  }
  params['level2max_expand_eids'] = {-1: 3, 0:5, 1:8, 2:5}
  params['level2reference_edges'] = defaultdict(list)
  params['FLAGS_USE_GLOBAL_REFERENCE_ENDGES'] = True
  params['FLAGS_ITERATIVELY_ADD_REFERENCE_EDGES'] = False
  return params

def load_cvd_params():
  params = {}
  params['MAX_ITER_TREE'] = 5
  params['FLAGS_USE_TYPE'] = True
  params['FLAGS_DEBUG'] = True

  params['FLAGS_INITIAL_EDGE'] = 1
  params['FLAGS_INITIAL_NODE'] = 3
  params['FLAGS_DEPTH_EXPANSION_METHOD'] = "embedding"
  params['level2max_children'] = {-1:10, 0:20, 1:40, 2:1e9, 3:1e9, 4:1e9, 5:1e9}
  params['level2source_weights'] = {
    -1: {"sg":5.0, "tp":1.0, "eb":1.0},
    0: {"sg":5.0, "tp":1.0, "eb":1.0},
    1: {"sg":5.0, "tp":1.0, "eb":1.0},
    2: {"sg":5.0, "tp":1.0, "eb":1.0},
  }
  params['level2max_expand_eids'] = {-1: 3, 0:5, 1:5, 2:5}
  params['level2reference_edges'] = defaultdict(list)
  params['FLAGS_USE_GLOBAL_REFERENCE_ENDGES'] = True
  params['FLAGS_ITERATIVELY_ADD_REFERENCE_EDGES'] = True
  return params


def load_ql_params():
  params = {}
  params['MAX_ITER_TREE'] = 5
  params['FLAGS_USE_TYPE'] = True
  params['FLAGS_DEBUG'] = True

  params['FLAGS_INITIAL_EDGE'] = 1
  params['FLAGS_INITIAL_NODE'] = 3
  params['FLAGS_DEPTH_EXPANSION_METHOD'] = "embedding"
  params['level2max_children'] = {-1:8, 0:15, 1:40, 2:1e9, 3:1e9, 4:1e9, 5:1e9}
  params['level2source_weights'] = {
    -1: {"sg":1.0, "tp":0.0, "eb":0.0},
    0: {"sg":1.0, "tp":0.0, "eb":0.0},
    1: {"sg":1.0, "tp":0.0, "eb":0.0},
    2: {"sg":1.0, "tp":0.0, "eb":0.0},
  }
  params['level2max_expand_eids'] = {-1: 3, 0:5, 1:8, 2:5}
  params['level2reference_edges'] = defaultdict(list)
  params['FLAGS_USE_GLOBAL_REFERENCE_ENDGES'] = True
  params['FLAGS_ITERATIVELY_ADD_REFERENCE_EDGES'] = False
  return params