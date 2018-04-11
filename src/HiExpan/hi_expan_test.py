'''
__author__: Jiaming Shen
__description__: A simple test for hi_expan.py
__latest_update__: 08/27/2017
'''
import sys
import util
import edge_expan
from tree_node import TreeNode
from set_expan import setExpan

# define global variables
MAX_ITER_TREE = 5
FLAGS_USE_TYPE = True
FLAGS_DEBUG = True

## TODO: change the userInput representation to allow user to specify the seed node under "China".
# userInput = [("United States", "China", "Russia", "Canada"), ("Illinois", "California")]
userInput = [("machine LEarning", "computer Vision", "INFORMATION RETRIEVAL"), ("neural Network", "Support Vector Machine", "Decision tree")]
stopLevel = len(userInput) - 1

# readAllMaps
# data = sys.argv[1]
data = "wiki"
folder = '../../data/'+data+'/intermediate/'
print('loading eid and name maps')
eid2ename, ename2eid = util.loadEidToEntityMap(folder+'entity2id.txt') #entity2Eid.txt


# initialize tree
rootNode = TreeNode(parent=None, level=-1, eid=-1, ename="ROOT", isUserProvided=True)
nextParent = rootNode
for i in range(len(userInput)):
  levelList = userInput[i]
  level = i
  parent = nextParent
  for j in range(len(levelList)):
    ename = levelList[j]
    newNode = TreeNode(parent, level, ename2eid[ename.lower()], ename, True)
    if j == 0:
      nextParent = newNode
    parent.addChildren([newNode])

rootNode.printSubtree(0)
print(rootNode)

## Testing the taxonomy saving
outputFile = "../../data/"+data+"/results/taxonomy.txt"
with open(outputFile,"w") as fout:
  s = []
  s.append(rootNode)
  while (len(s) != 0):
    top = s[-1]
    s = s[:-1]
    tab_number = top.level + 1
    entity_name = top.ename
    fout.write(tab_number*"\t"+entity_name+"\n")
    for child in reversed(top.children):
      s.append(child)


