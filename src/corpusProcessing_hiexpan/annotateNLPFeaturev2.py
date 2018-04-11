'''
__author__: Dongming Lei 
__description__: Run SpaCy tool on AutoPhrase output and filter non-NP quality phrases.
    Please have SpaCy Installed: https://spacy.io/usage/
        `pip install -U spacy`
        `python -m spacy download en`
    Input: 1) segmentation.txt
    Output: 1) a tmp sentences.json.spacy (without entity information), 2) a quality NP phrases list
__latest_updates__: 03/10/2018
'''

import sys
import time
import json
import re
import multiprocessing
import os
from multiprocessing import Lock
from collections import deque
import spacy
from spacy.symbols import ORTH, LEMMA, POS, TAG
from tqdm import tqdm

DEBUG = False


# INIT SpaCy
nlp = spacy.load('en')
start_phrase = [{ORTH: u'<phrase>', LEMMA: u'', POS: u'START_PHRASE', TAG: u'START_PHRASE'}]
end_phrase = [{ORTH: u'</phrase>', LEMMA: u'', POS: u'END_PHRASE', TAG: u'END_PHRASE'}]
nlp.tokenizer.add_special_case(u'<phrase>', start_phrase)
nlp.tokenizer.add_special_case(u'</phrase>', end_phrase)
    
def clean_text(text):
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    ## add space before and after <phrase> tags
    text = re.sub(r"<phrase>", " <phrase> ", text)
    text = re.sub(r"</phrase>", " </phrase> ", text)
    # text = re.sub(r"<phrase>", " ", text)
    # text = re.sub(r"</phrase>", " ", text)
    ## add space before and after special characters
    text = re.sub(r"([.,!:?()])", r" \1 ", text)
    ## replace multiple continuous whitespace with a single one
    text = re.sub(r"\s{2,}", " ", text)
    text = text.replace("-", " ")

    return text

def find(haystack, needle):
    """Return the index at which the sequence needle appears in the
    sequence haystack, or -1 if it is not found, using the Boyer-
    Moore-Horspool algorithm. The elements of needle and haystack must
    be hashable.

    >>> find([1, 1, 2], [1, 2])
    1

    """
    h = len(haystack)
    n = len(needle)
    skip = {needle[i]: n - i - 1 for i in range(n - 1)}
    i = n - 1
    while i < h:
        for j in range(n):
            if haystack[i - j] != needle[-j - 1]:
                i += skip.get(haystack[i], n)
                break
        else:
            return i - n + 1
    return -1


def process_one_doc(article, articleId):
    result = []
    phrases = []
    output_token_list = []
    
    # go over once 
    article = clean_text(article)
    q = deque()
    IN_PHRASE_FLAG = False
    for token in article.split(" "):
        if token == "<phrase>":
            IN_PHRASE_FLAG = True            
        elif token == "</phrase>":
            current_phrase_list = []
            while (len(q) != 0):
                current_phrase_list.append(q.popleft())
            phrases.append(" ".join(current_phrase_list).lower())
            IN_PHRASE_FLAG = False
        else:
            if IN_PHRASE_FLAG: # in the middle of a phrase, push the (word, pos) tuple
                q.append(token)

            ## put all the token information into the output fields
            output_token_list.append(token)
            
    text = " ".join(output_token_list)

    doc = nlp(text)
    
    sentId = 0
    for sent in doc.sents:
        NPs = []
        pos = []
        tokens = []
        for s in sent.noun_chunks:
            NPs.append(s)
            
        # get pos tag    
        for token in sent:
            tokens.append(token.text)
            pos.append(token.tag_)
        
        entityMentions = []
        # For each quality phrase, check if it's NP
        for p in phrases:
            for np in NPs:
                # find if p is a substring of np
                if np.text.find(p) != -1:
                    sent_offset = sent.start
                    
                    tmp = nlp(p)
                    p_tokens = [tok.text for tok in tmp]

                    offset = find(tokens[np.start - sent_offset:np.end - sent_offset], p_tokens)
                    if offset == -1:
                        # SKIP THIS AS THIS IS NOT EXACTLY MATCH
                        continue

                    start_offset = np.start + offset - sent_offset
                    ent = {
                        "text": " ".join(p_tokens),
                        "start": start_offset,
                        #"end": start_offset + len(p.split(" ")) - 1,
                        "end": start_offset + len(p_tokens) - 1,
                        "type": "phrase"
                    }

                    # sanity check 
                    if ent["text"] != " ".join(tokens[ent["start"]:ent["end"]+1]):
                        print("NOT MATCH", p, " ".join(tokens[ent["start"]:ent["end"]+1]))
                        print("SENT", " ".join(tokens))
                        print("SENT2", sent.text)
                    entityMentions.append(ent)
        
        res = {
            "articleId": articleId,
            "sentId": sentId,
            "tokens": tokens,
            "pos": pos,
            "entityMentions": entityMentions,
            "np_chunks": [{"text": t.text, "start": t.start-sent.start, "end": t.end-sent.start-1} for t in NPs]
        }
        result.append(res)
        sentId += 1
        
    return result

def endpos_in_tokens():
    '''
        calculate end position of nps    
    '''
    return

def preprocess(articles):
    phrases_by_article = []
    text_by_article = []

    for article in tqdm(articles):
        phrases = []
        output_token_list = []

        # go over once 
        article = clean_text(article)
        q = deque()
        IN_PHRASE_FLAG = False
        for token in article.split(" "):
            if token == "<phrase>":
                IN_PHRASE_FLAG = True            
            elif token == "</phrase>":
                current_phrase_list = []
                while (len(q) != 0):
                    current_phrase_list.append(q.popleft())
                phrases.append(" ".join(current_phrase_list).lower())
                IN_PHRASE_FLAG = False
            else:
                if IN_PHRASE_FLAG: # in the middle of a phrase, push the (word, pos) tuple
                    q.append(token)

                ## put all the token information into the output fields
                output_token_list.append(token)
                
        text = " ".join(output_token_list)
        text_by_article.append(text)
        phrases_by_article.append(phrases)

    return text_by_article, phrases_by_article

def analyse_text(articleId, doc, phrases):
    result = []

    sentId = 0
    for sent in doc.sents:
        NPs = []
        pos = []
        tokens = []
        for s in sent.noun_chunks:
            NPs.append(s)
            
        # get pos tag    
        for token in sent:
            tokens.append(token.text)
            pos.append(token.tag_)
        
        entityMentions = []
        # For each quality phrase, check if it's NP
        for p in phrases:
            for np in NPs:
                # find if p is a substring of np
                if np.text.find(p) != -1:
                    sent_offset = sent.start
                    
                    tmp = nlp(p)
                    p_tokens = [tok.text for tok in tmp]

                    offset = find(tokens[np.start - sent_offset:np.end - sent_offset], p_tokens)
                    if offset == -1:
                        # SKIP THIS AS THIS IS NOT EXACTLY MATCH
                        continue

                    start_offset = np.start + offset - sent_offset
                    ent = {
                        "text": " ".join(p_tokens),
                        "start": start_offset,
                        #"end": start_offset + len(p.split(" ")) - 1,
                        "end": start_offset + len(p_tokens) - 1,
                        "type": "phrase"
                    }

                    # sanity check 
                    if ent["text"] != " ".join(tokens[ent["start"]:ent["end"]+1]):
                        print("NOT MATCH", p, " ".join(tokens[ent["start"]:ent["end"]+1]))
                        print("SENT", " ".join(tokens))
                        print("SENT2", sent.text)
                    entityMentions.append(ent)
        
        res = {
            "articleId": articleId,
            "sentId": sentId,
            "tokens": tokens,
            "pos": pos,
            "entityMentions": entityMentions,
            "np_chunks": [{"text": t.text, "start": t.start-sent.start, "end": t.end-sent.start-1} for t in NPs]
        }
        result.append(res)
        sentId += 1
        
    return result

def process_batch(input_path, output_path, num_workers=1):
    with open(input_path, "r") as fin, open(output_path, "w") as fout:
        # Preprocess the text 
        # in format of [[text, phrases], ...]
        text_by_article, phrases_by_article = preprocess(fin.readlines())

        articleId = 0
        for doc in tqdm(lp.pipe(text_by_article, n_threads=40, batch_size=10000)):
            if articleId % 1000 == 0:
                print("Processed %s documents; current time: %s" % (articleId, time.time()))

            result = analyse_text(articleId, doc, phrases_by_article[articleId])

            for sent in result:
                json.dump(sent, fout)
                fout.write("\n")

            articleId += 1


def process_corpus_mp(input_path, output_path, num_workers=4):
    start = time.time()
    with open(input_path, "r") as fin, open(output_path, "w") as fout:
        pool = multiprocessing.Pool(processes=num_workers)
        
        # test if multiprocessing is working
        multiple_results = [pool.apply_async(os.getpid, ()) for i in range(4)]
        print([res.get(timeout=1) for res in multiple_results])

        results = [pool.apply_async(
            process_corpus_thread, 
            args=(line, cnt)) for cnt, line in enumerate(fin)]
        results = [p.get() for p in results]
        
        for cnt, sents in enumerate(results):
            for sent in sents:
                json.dump(sent, fout)
                fout.write("\n")

    end = time.time()
    print("Finish NLP processing, using time %s (second) " % (end-start))

def process_corpus_thread(line, cnt):    
    if DEBUG and cnt > 1000:
        return []

    if cnt % 1000 == 0:
        print("Processed %s documents; current time: %s" % (cnt, time.time()))
    line = line.strip()
    try:
        article_result = process_one_doc(line, cnt)
    except:
        print("exception")
        return []

    return article_result


if __name__ == "__main__":
    corpusName = sys.argv[1]  # e.g. dblpv2
    FLAGS_POS_TAGGING = sys.argv[2]
    num_workers = int(sys.argv[3])
    input_path = "../../data/" + corpusName + "/intermediate/segmentation.txt"
    output_path = "../../data/" + corpusName + "/intermediate/sentences.json.spacy"
    process_batch(input_path, output_path, num_workers=num_workers)
