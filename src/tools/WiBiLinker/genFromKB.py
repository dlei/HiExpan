DATA_PREFIX = '/shared/data/dlei5/fts/Maple/data/'

def pairs_from_wibi():
    pairs = set()
    # file = open('/home/dlei5/data/fts/Maple/data/wibi-ver1.0/taxonomies/WiBi.categorytaxonomy.ver1.0.txt')
    file = open(DATA_PREFIX + 'wibi-ver1.0/taxonomies/WiBi.pagetaxonomy.ver1.0.txt') 


    for line in file:
        if line.startswith('#'):
            continue
        splits = line.lower().strip('\n').split('\t')
        
        pairs.add((splits[0], splits[1]))

    return pairs

def pairs_from_word2vec():
    files = [open(DATA_PREFIX + 'questions-phrases.txt'), open(DATA_PREFIX + 'questions-words.txt')]

    pairs = set()
    for file in files:
        for line in file:
            if line.startswith(':'):
                continue
            splits = line.lower().strip('\n').split(' ')
            pairs.add((splits[0], splits[1]))
            pairs.add((splits[2], splits[3]))

    return pairs


def pairs_from_hype():
    file = open(DATA_PREFIX + 'datasets/all.tsv')
    pairs = set()
    for line in file:
        splits = line.lower().strip('\n').split('\t')
        if splits[2] == 'True':
            paris.add(splits[0], splits[1])

    return pairs

def generate_pairs(s):
    file = open('/shared/data/jiaming/FTS/Maple/data/wiki/intermediate/entity2id.txt')

    entities = []
    res = []
    for line in file:
        splits = line.lower().strip('\n').split('\t')
        entities.append( (splits[0], splits[1])) #entity_name id

    print("len: " , len(entities))
    
    for i in range(0, len(entities)):
        for j in range(i, len(entities)):
            pair = (entities[i][0], entities[j][0])
            if pair in s:
                res.append((entities[i][0], entities[i][1], entities[j][0], entities[j][1]))


    return res

def main():
    s = set()
    s |= pairs_from_wibi()
    s |= pairs_from_word2vec()
    s |= pairs_from_hype()

    res = generate_pairs(s)
    for r in res:
        print("%s,%s,%s,%s" % (r[0], r[1], r[2], r[3]))

main()
