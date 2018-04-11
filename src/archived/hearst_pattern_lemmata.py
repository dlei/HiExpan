'''
__author__: Jiaming Shen
__description__: Extract hypernym using hearst pattern. Based on NP
__lastest_updated__: Deprecated
'''
import re
import os
import sys
from multiprocessing import Pool
from pattern.en import parsetree
from pattern.search import search
from collections import Counter

def NP_filter(chunk):

    NP = [str(w.string) for w in chunk.words]
    if len(NP) < 2:
        return ([],[])

    NP_lemma = [w.lemma for w in chunk.words]
    if NP[0] in ["other", "such"]:
        NP = NP[1:]
        NP_lemma = NP_lemma[1:]

    if len(NP) == 1 and NP[0] == "NP":
        return ([],[])

    return (NP,NP_lemma)


def NP_chunking(document, Debug = False):
    '''
    :param document: input raw document, string
    :param Debug: output debug info or not, boolean
    :return: a tuple of (parsed_document:string, number_of_NP:int, number2NP:list)
    '''

    parsed_sentences = []
    count = 0
    count2NP = []
    count2NP_lemma = []


    s = parsetree(document, lemmata=True)  # s is a Text Object, which is a list of Sentence Object.
    for sentence in s:
        sentence_string = sentence.string

        if Debug:
            print(sentence.id, "\t", "Raw sentence: ", sentence_string)

        for chunk in sentence.chunks:
            if chunk.type == "NP":
                NP, NP_lemma = NP_filter(chunk) # leave only good NP

                if NP:
                    p_string = "\s+".join([str(np) for np in NP])

                    try: # filter those bad quality NP with RE metacharacter
                        p = re.compile(p_string)
                    except:
                        continue

                    p_new = "NP" + str(count)
                    sentence_string, numReplacements = re.subn(p, p_new, sentence_string)
                    if numReplacements:  # did match
                        count2NP.append(" ".join(NP))
                        count2NP_lemma.append(" ".join(NP_lemma))
                        count += 1

        if Debug:
            print("Parsed sentence: ", sentence_string)
        parsed_sentences.append(sentence_string)

    parsed_document = "\n".join(parsed_sentences)
    tokenized_sentences = [sent.string for sent in s]

    return (parsed_document, count, count2NP, count2NP_lemma, tokenized_sentences)

def hearst_pattern_extracting(parsed_document, Debug = False):
    '''
    :param parsed_document: document in which all noun phrases are
    :param Debug: output debug info or not, boolean
    :return: a list of matched pattern with its heading.
             Each element is also a list in the form [pattern_string, head].
             The head is the hypernymy in the relationship
    '''

    hp_all = re.compile(r"""
        ((NP\d+)[\s,]*such[\s]+as[\s,]*[NP\d+\s,]*(?:and|or)*[\s,]*NP\d+)| # Pattern 1: NP0 such as {NP, (and|or)} NP
        (such[\s]+(NP\d+)[\s,]*as[\s,]*[NP\d+\s,]*(?:and|or)*[\s,]*NP\d+)| # Pattern 2: such NP0 as {NP, }* {(and|or)} NP
        (NP\d+[NP\d+\s,]*(?:and|or)*\s+other\s+(NP\d+))| # Pattern 3: NP {, NP}* {(and|or)} other NP
        ((NP\d+)[\s,]+(?:including|especially)[NP\d+\s,]*(?:and|or)*\s+NP\d+) # Pattern 4: NP {,} {(including|especially)} {NP, }* {(and|or)} NP
    """, re.VERBOSE)
    m = re.findall(hp_all, parsed_document)

    pattern_match = []
    for match in m:  # each match is one of the hearst pattern
        head = False
        pattern_pair = []
        for group in match:
            if group and not head:  # the whole matched pattern
                pattern_pair.append(str(group))
                head = True  # wait for appending the head of this pattern
                continue

            if group and head:  # the head of a previous matched pattern
                pattern_pair.append(str(group))
                pattern_match.append(pattern_pair)  # append the whole pattern tuple
                head = False
                pattern_pair = []

    return pattern_match

def hyponym_extracting(pattern_list):
    '''
    :param pattern_list: a list of matched pattern with its heading.
             Each element is also a list in the form [pattern_string, head].
             The head is the hypernymy in the relationship.
    :return: a list of hyponyms,
                in which the first element is hyponymy_id, the second element is hypernymy_id
    '''

    hyponyms = []

    for pattern in pattern_list:
        head = pattern[1]
        pattern_string = pattern[0]

        NPs = re.findall(r"NP\d+", pattern_string)
        for NP in NPs:
            if NP != head:
                hyponyms.append([NP, head])

    return hyponyms

def hyponym_name_mapping(hyponyms_list, count2name):
    '''
    :param hyponyms_list: a list of hyponym ids,
                in which the first element is hyponymy_id, the second element is hypernymy_id
    :param count2name: mapping from NP_id to NP_name
    :return: hyponyms: a list of hyponym ids,
                in which the first element is hyponymy_name, the second element is hypernymy_name
    '''

    hyponyms = []
    for pair in hyponyms_list:
        hyponym_id = re.search(r"\d+",pair[0]).group()
        try:
            hyponym = count2name[int(hyponym_id)]
        except:
            print(hyponyms_list, count2name)
        hypernym_id = re.search(r"\d+",pair[1]).group()
        hypernym = count2name[int(hypernym_id)]

        hyponyms.append([hyponym,hypernym])

    return hyponyms

def saving_ranked_hyponyms(hyponyms, outpath = "./"):
    hyponyms_tuple = [tuple(pair) for pair in hyponyms]
    c = Counter(hyponyms_tuple)

    try:
        with open(outpath+"DBLP_500k_tokenized_hyponym_lemma.txt","w") as fout:
            for ele in sorted(c.items(), key=lambda x: -x[1]):
                fout.write("::".join(ele[0]))
                fout.write("\t")
                fout.write(str(ele[1]))
                fout.write("\n")

        hyponym_mentions = []
        for pair in c.keys():
            hyponym_mentions.append(pair[0])
            hyponym_mentions.append(pair[1])

        entity_mention_counter = Counter(hyponym_mentions)

        with open(outpath+"DBLP_500k_tokenized_entity.txt","w") as fout:
            for pair in sorted(entity_mention_counter.items(), key=lambda x: -x[1]):
                fout.write(pair[0])
                fout.write("\t")
                fout.write(str(pair[1]))
                fout.write("\n")
        return True

    except:
        return False


if __name__ == "__main__":
    # Loading data
    # docs = []
    # failed_docs = []
    # print("=== Start loading files ===")
    # # with open("./data/raw_DBLP_500k_tokenized.txt", "r") as fin:
    # with open("../data/signal_processing_expert.txt", "r") as fin:
    #     docs = fin.readlines()
    #
    # hyponyms_all = []
    # count = 0
    # failed_count = 0
    # tokenized_corpus = []
    #
    # print("=== Finish loading files, start processing ===")
    # for doc in docs:
    #
    #     if count % 100 == 0 and count != 0:
    #         print(count)
    #
    #     if count == 100:
    #         break
    #
    #     if doc and (not re.match(r'None\s+', doc, re.IGNORECASE)):
    #         doc = re.sub(r'[^\x00-\x7F]+', ' ', doc)
    #         doc = re.sub(r"\s[$^|{}\\\(\)\[\]]", " ", doc)
    #         doc = re.sub(r"\s+", " ", doc)
    #         try:
    #             print "=== A new doc ==="
    #             parsed_doc, np_count, count2name, count2NP_lemma, tokenized_sentences = NP_chunking(doc, Debug=False)
    #             tokenized_corpus.append(tokenized_sentences)
    #             # print parsed_doc
    #             pattern_list = hearst_pattern_extracting(parsed_doc)
    #             print pattern_list
    #             hyponyms_id = hyponym_extracting(pattern_list)
    #             print hypnomys
    #             hyponyms = hyponym_name_mapping(hyponyms_id, count2NP_lemma)
    #             if hyponyms:
    #                 print hyponyms
    #                 hyponyms_all.extend(hyponyms)
    #             count += 1
    #
    #         except:
    #             failed_docs.append(doc)
    #             failed_count += 1
    #             print("A document failed, totally failed = ", failed_count)
    #             continue

    # print("=== Saving detected hyponyms ===")
    # saving_ranked_hyponyms(hyponyms_all,"./data/")
    #
    # print("=== Saving failed documents ===")
    # with open("./data/failed_docs.txt","w") as fout:
    #     for ele in failed_docs:
    #         fout.write(ele)
    #         fout.write("\n")
    #
    # print("=== Saving tokenized sentences ===")
    # with open("./data/signal_processing_tokenized_sentences.txt", "w") as fout:
    #     for doc_id in xrange(len(tokenized_corpus)):
    #         tokenized_doc = tokenized_corpus[doc_id]
    #         for sent_id in xrange(len(tokenized_doc)):
    #             fout.write(str(doc_id)+"-"+str(sent_id)+"\t")
    #             fout.write(tokenized_doc[sent_id])
    #             fout.write("\n")
    #
    # print(" === All done === ")
    ###########################

    ###########################
    ## Testing one file
    ###########################
    doc = "On Finding Critical Independent and Vertex Sets . An independent set $ I_ { c } $ of a undirected graph $ G $ is called critical if \ [ | I_ { c } | - | N ( I_ { c } ) | = \ max \ { | I | - | N ( I ) | : \ mbox { \ rm $ I $ is an independent set of $ G $ } \ } , \ ] where $ N ( I ) $ is the set of all vertices of $ G $ adjacent to some vertex of $ I $ . It has been proved by Cun - Quan Zhang [ SIAM J . Discrete Math . , 3 ( 1990 ) , pp . 431 - - 438 ] that the problem of finding a critical independent set is polynomially solvable . This paper shows that the problem can be solved in $ O ( | V ( G ) | ^ { 1 / 2 } | E ( G ) | ) $ time and its weighted version in $ O ( | V ( G ) | ^ { 2 } | E ( G ) | ^ { 1 / 2 } ) $ time ."
    doc = re.sub(r"\s[$^|{}\\\(\)\[\]]", " ", doc)
    doc = re.sub(r"\s+", " ", doc)

    print doc
    #
    hyponyms_all = []
    parsed_doc, np_count, count2name, count2NP_lemma, tokenized_sentences = NP_chunking(doc, Debug=True)
    print "Parsed_doc = ", parsed_doc
    pattern_list = hearst_pattern_extracting(parsed_doc, Debug=True)
    print "!!! Pattern_list = ", pattern_list
    hyponyms_id = hyponym_extracting(pattern_list)
    print "!!! Hyponym id = ", hyponyms_id
    hyponyms = hyponym_name_mapping(hyponyms_id, count2NP_lemma)
    print "!!! Hyponyms = ", hyponyms
    # if hyponyms:
    #     # print hyponyms
    #     hyponyms_all.extend(hyponyms)
    # print hyponyms_all
    # print count2NP_lemma