'''
__author__: Jiaming Shen, Peifeng Jing
__description__: Clean the CS full text paper. The utility function used in cleaner.py
__latest_update__: 08/14/2017
'''
import re
import random
import sys
#import enchant

def getStructureLevel(content):
    '''
    level of structured:
        5. if the content contains 'abstract', 'introduction' and 'references', the content is highest structured
        4. if the content contains 'abstract' and 'references' (4.1); or 'introduction' and 'references' (4.2), the content is second highest structured
        3. if the content contains 'abstract' (3.1) or 'introduction' (3.2), but not 'references', the content is structured with no references
        2. if the content contains 'references', but not 'abstract' or 'introduction', the content is structured at the end, but not in the front
        1. if the content does not contain 'abstract', 'introduction' and 'references', the content is worst structured
    '''
    
    hasAbstract = len(re.findall('\n\w?\d*\W*' + 'abstract' + '[^a-zA-Z]', content.lower())) > 0
    hasIntroduction = len(re.findall('\n\w?\d*\W*'+ 'introduction' +'[^a-zA-Z]', content.lower())) > 0
    hasReferences = len(re.findall('\n\w?\d*\W*'+ 'references' +'[^a-zA-Z]', content.lower())) > 0

    if hasAbstract and hasIntroduction and hasReferences:
        return 5
    elif (hasAbstract or hasIntroduction) and hasReferences:
        if hasAbstract and hasReferences:
            return 4.1
        else:
            return 4.2
    elif (hasAbstract or hasIntroduction) and not hasReferences:
        if hasAbstract:
            return 3.1
        else:
            return 3.2
    elif not (hasAbstract or hasIntroduction) and hasReferences:
        return 2
    else:
        return 1

def deleteSectionSymbol(content):
    '''
    remove "========"
    '''
    result = sorted(re.finditer('====\W+\n', content), key = lambda x : -x.span()[0])
    for res in result:
        ind1 = res.span()[0]
        ind2 = res.span()[1]
        if content[ind2:].find('\n') == -1:
            content = content[:ind1]
            continue
        tempRes = re.search('\n', content[ind2:]).span()
        ind3 = tempRes[0]
        ind4 = tempRes[1]
        try:
            float(content[ind2:ind2+ind3])
            content = content[:ind1] + '\n' + content[ind2+ind4:]
        except ValueError:
            content = content[:ind1] + '\n' + content[ind2:]
    return content

def countLevels(filesList):
    count = dict()
    # initialize
    for i in [5, 4.1, 4.2, 3.1, 3.2, 2, 1]:
        count[str(i)] = 0
    # count
    for filename in filesList:
        f = open(filename, 'r')
        content = f.read()
        count[str(getStructureLevel(content))] += 1
    print(count)

def validEnglishWord(word, context, specialWordMap):
    '''
    check if a word is valid English word.

    Current rules are:
        1) if a word contains only capital letters:
            if its length >= 3, return true
            else, return flase
        2) if a word contains only one characther:
            return false
        3) all the other cases, return false ???
    '''

    if word.upper() == word:
        if len(word) >= 3:
            return True
        else:
            return False

    if len(word) == 1:
        return False

    return False

    ''' THIS IS VERY SLOW; MAY NEED 60 HOURS IF VALIDATE WITH ENGLISH DICTIONARY
    # in case it contains multiple words separated by capital letters
    # The dictionary could be revised by adding specific domain words
    subWord = re.findall('[A-Z][^A-Z]*', word)
    d_US = enchant.Dict("en_US")    # US English
    d_GB = enchant.Dict("en_GB")    # GB English
    for each in subWord:
        if not d_US.check(word) and not d_GB.check(word):
            # check whether this word is specially appears multiple times in the context
            if word in specialWordMap:
                return specialWordMap[word]
            wordCount = len(re.findall('\s+' + word + '\s+', context))
            if wordCount > 3:
                specialWordMap[word] = True
                return True
            specialWordMap[word] = False
            return False
    return True
    '''

def insertSlash(word):
    '''
    insert slash in front of every character
    '''
    new = ''
    for c in word:
        new += "\\" + c
    return new

def clean_str(string):
    '''
    Tokenization/string cleaning for all datasets except for SST.
    Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
    Given by Yuming Mao
    :param string:
    :return:
    '''

    string = re.sub(r"[^A-Za-z0-9(),!?\'\`\.]", " ", string)

    string = re.sub(r"\'s", " \'s", string)

    string = re.sub(r"\'ve", " \'ve", string)

    string = re.sub(r"n\'t", " n\'t", string)

    string = re.sub(r"\'re", " \'re", string)

    string = re.sub(r"\'d", " \'d", string)

    string = re.sub(r"\'ll", " \'ll", string)

    string = re.sub(r",", " , ", string)

    string = re.sub(r"!", " ! ", string)

    string = re.sub(r"\(", " \( ", string)

    string = re.sub(r"\)", " \) ", string)

    string = re.sub(r"\?", " \? ", string)

    string = re.sub(r"\s{2,}", " ", string)

    return string.strip()

def sample_corpus(inputFile, outputFile, prob):
    """ Random sample inputFile corpus and save in outputFile with probability prob

    Usage: python sample.py text_in text_out 0.25
    """
    prob = float(prob)
    with open(inputFile, "r") as fin, open(outputFile, "w") as fout:
        for line in fin:
            if random.random() < prob:
                fout.write(line)
    print("[INFO] Sample file success")







