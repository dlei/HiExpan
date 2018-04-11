'''
__author__: Jiaming Shen
__description__: User input seed taxonomy used in HiExpan
__latest_update__: 02/09/2018

Format of user supervision:
  [ParentEntityName, ParentLevel, ListOfChildrenEntityName]
Note:
  1. Except the ROOT name, all the other "ParentEntityName" must appear after its parent node appears
  (For example, "machine learning" must appear after "ROOT" (its parent)
  2. Don't add the leaf nodes in userInput
  (For example, "decision trees" is a leaf node, no need to include it in userInput)

'''

def load_wiki_seeds():
  # Case 1: three level taxonomy
  # userInput = [
  #   ["ROOT", -1, ["north america", "europe"]],
  #   ["north america", 0, ["united states", "canada"]],
  #   ["europe", 0, ["frances", "germany"]],
  #   ["united states", 1, ["california", "illinois"]],
  # ]
  # userInput = [
  #   ["ROOT", -1, ["north america", "europe", "asia"]],
  #   ["north america", 0, ["united states", "canada", "mexico"]],
  #   ["europe", 0, ["frances", "germany"]],
  #   ["asia", 0, ["china", "japan"]],
  #   ["united states", 1, ["california", "illinois"]],
  # ]

  # Case 2: two level taxonomy
  userInput = [
    ["ROOT", -1, ["united states", "china", "canada"]],
    ["united states", 0, ["california", "illinois", "florida"]],
    ["china", 0, ["shandong", "zhejiang", "sichuan"]],
  ]

  return userInput

def load_dblp_seeds():
  # Case 1: three level taxonomy
  # userInput = [
  #   ["ROOT", -1, ["machine learning", "data mining", "information retrieval"]],
  #   ["machine learning", 0, ["supervised machine learning", "unsupervised learning", "reinforcement learning"]],
  #   ["data mining", 0, ["pattern mining", "graph mining", "web mining", "text mining"]],
  #   ["information retrieval", 0, ["document retrieval", "query processing", "relevance feedback"]],
  #
  #   ["supervised machine learning", 1, ["support vector machines", "decision trees", "random forests"]],
  #   ["unsupervised learning", 1, ["agglomerative clustering", "principle component analysis", "latent dirichlet allocation"]],
  #   ["reinforcement learning", 1, ["markov decision processes", "policy gradient"]]
  #   # ["supervised machine learning", 0, ["named entity recognition", "information extraction", "machine translation"]],
  #   # ["neural networks", 1, ["convolutional neural network", "recurrent neural networks"]],
  # ]

  # Case 2: two level taxonomy
  userInput = [
    # ["ROOT", -1, ["machine learning", "data mining", "natural language processing", "information retrieval", "wireless networks"]],
    ["ROOT", -1,
     ["machine learning", "data mining", "natural language processing", "information retrieval", "wireless networks"]],
    ["data mining", 0, ["association rule mining", "text mining", "outlier detection"]],
    ["machine learning", 0, ["support vector machines", "decision trees", "neural networks"]],
    ["natural language processing", 0, ["named entity recognition", "information extraction", "machine translation"]],
  ]
  return userInput

def load_cvd_seeds():
  # Case 1: two level taxonomy
  # userInput = [
  #   ["ROOT", -1, ["cardiovascular diseases", "cardiovascular abnormalities", "vascular diseases", "heart-disease"]],
  #   ["cardiovascular diseases", -1, ["cardiovascular abnormalities", "vascular diseases", "heart-disease"]],
  #   ["cardiovascular abnormalities", 0, ["turner syndrome", "tetralogy of fallot",
  #                                        "noonan syndrome", "congenital heart defects"]],
  #   ["vascular diseases", 0, ["arteriovenous malformations", "high-blood pressure",
  #                             "arterial occlusions", "splenic infarction", "coronary aneurysms"]],
  #   ["heart-disease", 0, ["aortic-valve stenosis", "cardiac arrests", "carcinoid heart disease"]],
  # ]

  userInput = [
    ["ROOT", -1, ["cardiovascular abnormalities", "vascular diseases", "heart-disease"]],
    ["cardiovascular abnormalities", 0, ["turner syndrome", "tetralogy of fallot", "noonan syndrome"]],
    ["vascular diseases", 0, ["arteriovenous malformations", "high-blood pressure", "arterial occlusions"]],
    ["heart-disease", 0, ["aortic-valve stenosis", "cardiac arrests", "carcinoid heart disease"]],
  ]

  return userInput

def load_ql_seeds():
  # Case 1: two level taxonomy
  # userInput = [
  #   ["ROOT", -1, ["cardiovascular diseases", "cardiovascular abnormalities", "vascular diseases", "heart-disease"]],
  #   ["cardiovascular diseases", -1, ["cardiovascular abnormalities", "vascular diseases", "heart-disease"]],
  #   ["cardiovascular abnormalities", 0, ["turner syndrome", "tetralogy of fallot",
  #                                        "noonan syndrome", "congenital heart defects"]],
  #   ["vascular diseases", 0, ["arteriovenous malformations", "high-blood pressure",
  #                             "arterial occlusions", "splenic infarction", "coronary aneurysms"]],
  #   ["heart-disease", 0, ["aortic-valve stenosis", "cardiac arrests", "carcinoid heart disease"]],
  # ]

  userInput = [
    ["ROOT", -1, ["quantum algorithms", "quantum systems", "quantum theory"]],
    ["quantum algorithms", 0, ["quantum annealing", "quantum machine learning"]],
    ["quantum systems", 0, ["quantum computers", "quantum circuits"]],
    ["quantum theory", 0, ["quantum states", "hilbert-space"]],
  ]

  return userInput