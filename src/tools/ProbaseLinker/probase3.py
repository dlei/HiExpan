import sys,json,urllib.request,urllib.parse,time,os
import operator
import pickle
import time
import multiprocessing as mp
import math

class ProbaseReference:
    """A class for Probase"""
    _version = 1.0
    

    def __init__(self, key = 'm3XGOzAbxDxNTjJQQ1gxlFQhXVkiBKl3'):
        self.key = key
        self.api_url = 'https://concept.research.microsoft.com/api/Concept/ScoreByProb?instance=%s&topK=10&api_key=' + key
        if os.path.isfile('probase_local.p'):
            self.cache = self.load_from_file("probase_local.p")   
        else:
            self.cache = None     

    def get_probase_fusion(self, phrase):
        if phrase in self.cache:
            return self.cache[phrase]
        else:
            res = self.get_probase_online(phrase)
            self.cache[phrase] = res
            self.save_to_file(res, "probase_local.p")
            return res
    
    def get_probase_online(self, phrase):
        phrase = phrase.strip()
        if len(phrase) <=0:
            return None

        res = None
        for i in range(0,10):
            while True:
                try:
                    response = urllib.request.urlopen( self.api_url % urllib.parse.quote(phrase, safe='') ).read()
                    res = json.loads(str(response, 'utf-8'))
                    res = sorted(res.items(), key=operator.itemgetter(1), reverse=True)
                except Exception as e:
                    time.sleep(10)
                    print('Retrying: %s' % phrase)
                    print(e)
                    continue
                break

        if (res):
            print("[{}]Succeed in getting phrase: {}".format(
                mp.current_process().name,
                phrase,
                )
            )
        elif (res == []):
            print("[{}]Unlinkable phrase:{}".format(
                mp.current_process().name,
                phrase,
                )
            )
        else:
            print("[{}][ERROR] Failed to link:{}".format(
                mp.current_process().name,
                phrase,
                )
            )
        return res

    def get_probase_batch(self, phrases, save = False):
        if phrases is None:
            return {}

        linkable_cnt = 0
        res = {}
        for e in phrases:
            link_res = self.get_probase_online(e)
            if (link_res):
                linkable_cnt += 1
                if linkable_cnt % 1000 == 0:
                    print("=========== [%s][INFO] Linked %s phrases ==========" % (mp.current_process().name,linkable_cnt))
            res[e] = link_res

        if(save):
            self.save_to_file(res, "probase_local.p")

        return res

    def save_to_file(self, obj, file):
        pickle.dump( obj, open( file, "wb" ) )

    def load_from_file(self, file):
        return pickle.load( open( file, "rb" ) )

    def convert_to_txt_file(self, file):
        with open(file, "w") as fout:
            for ele in self.cache:
                fout.write(ele+"\t"+str(self.cache[ele]))
                fout.write("\n")


    def get_probase_parallel(
        self, 
        phrases, 
        num_workers = 1,
        save = False,
    ):
        num_workers+=1
        pool = mp.Pool(processes=num_workers)

        num_lines = len(phrases)
        batch_size = math.floor(num_lines/(num_workers-1))
        print("batch_size: %d" % batch_size)

        start_pos = [i*batch_size for i in range(0, num_workers)]
        phrases = list(phrases)
        results = [pool.apply_async(self.get_probase_batch, args=(phrases[start:start+batch_size], False)) for i, start in enumerate(start_pos)]
        results = [p.get() for p in results]
        
        res={}
        for r in results:
            res.update(r)
        
        if(save):
            self.save_to_file(res, "probase_local_parallel.p")
            self.cache = res
            self.convert_to_txt_file('linked_results_parallel.txt')

def get_phrases(phrase_file, first_nrow=0):  
    phrases = set()
    cnt=0
    with open(phrase_file) as f:
        for line in f:
            cnt+=1
            s = line.strip().split('\t')
            phrases.add(s[0])
            if first_nrow!=0 and cnt>first_nrow:
                break

    print('Done: get_phrases')
    return phrases


def get_phrases_new(phrase_file, first_nrow=0):
    phrases = set()
    cnt = 0
    with open(phrase_file) as f:
        for line in f:
            cnt += 1
            line = line.strip()
            phrases.add(" ".join(line.split("_")))
            if first_nrow != 0 and cnt > first_nrow:
                break

    print('Done: get_phrases')
    return phrases

if __name__ == "__main__":
    p = ProbaseReference()
    # outfile = "./linked_results.txt"
    # p.convert_to_txt_file(outfile)
    # res = p.get_probase_online("computer science")
    # print(res)
    phrase_files = "/shared/data/jiaming/FTS/Maple/data/wiki/intermediate/entity2id.txt"
    phrases = get_phrases(phrase_files, first_nrow=0)
    start = time.time()
    # p.get_probase_batch(phrases, save=True)
    p.get_probase_parallel(phrases, num_workers = 30, save=True)

    end = time.time()
    print("Linking %s phrases using time %s (seconds)" % (len(phrases), end-start))




