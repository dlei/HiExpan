'''
__author__: Peifeng Jing
__description__: Clean the CS full text paper. To run the code, uncommented 
                 the demo mode and put this code along with "utility.py" in 
                 the same path of full_text_papers.
'''
import os, re
import random
import utility

# collect all paper's paths in an list
# directoryPath = 'full_text_papers/'
directoryPath = "../data/full_text_papers/"
conferenceFolder = os.listdir(directoryPath)
conferenceFolder.remove('.DS_Store')    # avoid auto generated .DS_Store on mac osx
filesList = []     # full path with paper names
for eachFolder in conferenceFolder:
    files= os.listdir(directoryPath + eachFolder)
    for filename in files:
        filesList.append(directoryPath + eachFolder + '/' + filename)

#utility.countLevels(filesList)    # print counts of each structured level {'1': 398, '2': 252, '3.1': 652, '3.2': 107, '4.1': 2451, '4.2': 255, '5': 16210}

##========================================
# Demo Mode (comment if not neccessary)
#
# mode 1: select top n papers
# mode 2: select random n papers
# mode 3: select certain level of structures
##========================================
# select specific files (# of files/file structure level)
# mode = 2
# top = 5
# levelRange = (1,3)
# if mode == 1:
#     filesList = filesList[:top]
# elif mode == 2:
#     filesList = random.sample(filesList, top)
# elif mode == 3:
#     temp = random.sample(filesList, 1)[0]
#     tempContent = open(temp, 'r').read()
#     tempLevel = utility.getStructureLevel(tempContent)
#     while tempLevel < levelRange[0] or tempLevel > levelRange[1]:
#         temp = random.sample(filesList, 1)[0]
#         tempContent = open(temp, 'r').read()
#         tempLevel = utility.getStructureLevel(tempContent)
#     filesList = [temp]
# # filesList = ['full_text_papers/CIKM_papers/416d9a3f3ef054a4ba33b7fc0852b08a3c548b7a.pdf.txt.txt.txt']
# # write to a file for original text comparison
# file = '../data/original_full_text_(demo).txt'
# open(file, 'w').close() # clear original file
# toFile = open(file, 'a')
# for filename in filesList:
#     fromFile = open(filename, 'r')
#     content = fromFile.read()
#     toFile.write(content)
#     fromFile.close()
# toFile.close()
##===========================================
# Demo End Here
##===========================================


# read all text and append to the text file
file = '../data/full_text.txt'
open(file, 'w').close() # clear original file
toFile = open(file, 'a')

countDash = 0   # RULE 2, # of lines end with a dash

count = 0
for filename in filesList:
    print(str(count) + '/' + str(len(filesList)))
    count += 1

    fromFile = open(filename, 'r')
    text = fromFile.read()
    
    ### ALL PROCESS COME HERE
    # print('filename: ' + filename)

    ### RULE 1
    # CLEAN BASED ON WHETHER THE TEXT IS WELL STRUCTURED
    #   level of structured:
    #       5. if the content contains 'abstract', 'introduction' and 'references', the content is highest structured
    #       4. if the content contains 'abstract' and 'references' (4.1); or 'introduction' and 'references' (4.2), the content is second highest structured
    #       3. if the content contains 'abstract' (3.1) or 'introduction' (3.2), but not 'references', the content is structured with no references
    #       2. if the content contains 'references', but not 'abstract' or 'introduction', the content is structured at the end, but not in the front
    #       1. if the content does not contain 'abstract', 'introduction' and 'references', the content is worst structured
    structureLevel = utility.getStructureLevel(text)
    # print("RULE 1 structure level: " + str(structureLevel))
    
    ## level 5 structured
    if structureLevel == 5:
        # remove all "========="
        text = utility.deleteSectionSymbol(text)
        # full text start from first "\nabstract[^a-zA-Z]" and end at the last "\nreferences[^a-zA-Z]"
        front_index = re.search('\n\w?\d*\W*abstract[^a-zA-Z]', text.lower()).start()
        end_index = re.search('\n\w?\d*\W*references[^a-zA-Z]', text.lower()).start()
        content = text[front_index : end_index]
        # the first line is the title
        content = text.split('\n', 1)[0] + content
    ## level 4.1 structured
    if structureLevel == 4.1:
        # remove all "========="
        text = utility.deleteSectionSymbol(text)
        # full text start from first "\nabstract[^a-zA-Z]" and end at the last "\nreferences[^a-zA-Z]"
        front_index = re.search('\n\w?\d*\W*abstract[^a-zA-Z]', text.lower()).start()
        end_index = re.search('\n\w?\d*\W*references[^a-zA-Z]', text.lower()).start()
        content = text[front_index : end_index]
        # the first line is the title
        content = text.split('\n', 1)[0] + content
    ## level 4.2 structured
    if structureLevel == 4.2:
        # remove all "========="
        text = utility.deleteSectionSymbol(text)
        # full text start from first "\nintroduction[^a-zA-Z]" and end at the last "\nreferences[^a-zA-Z]"
        front_index = re.search('\n\w?\d*\W*introduction[^a-zA-Z]', text.lower()).start()
        end_index = re.search('\n\w?\d*\W*references[^a-zA-Z]', text.lower()).start()
        content = text[front_index : end_index]
        # the first line is the title
        content = text.split('\n', 1)[0] + content
    ## level 3.1 structured
    if structureLevel == 3.1:
        # remove all "========="
        text = utility.deleteSectionSymbol(text)
        # full text start from first "\nabstract[^a-zA-Z]" and end at the last "\nreferences[^a-zA-Z]"
        front_index = re.search('\n\w?\d*\W*abstract[^a-zA-Z]', text.lower()).start()
        content = text[front_index : ]
        # the first line is the title
        content = text.split('\n', 1)[0] + content
    ## level 3.2 structured
    if structureLevel == 3.2:
        # remove all "========="
        text = utility.deleteSectionSymbol(text)
        # full text start from first "\nabstract[^a-zA-Z]" and end at the last "\nreferences[^a-zA-Z]"
        front_index = re.search('\n\w?\d*\W*introduction[^a-zA-Z]', text.lower()).start()
        content = text[front_index : ]
        # the first line is the title (THIS MAY NOT BE TRUE)
        content = text.split('\n', 1)[0] + content
    ## level 2 structured
    if structureLevel == 2:
        # remove all "========="
        text = utility.deleteSectionSymbol(text)
        # full text end at the last "references"
        end_index = re.search('\n\w?\d*\W*references[^a-zA-Z]', text.lower()).start()
        content = text[: end_index]
    ## level 1 structured
    if structureLevel == 1:
        # remove all "========="
        text = utility.deleteSectionSymbol(text)
        content = text



    ### RULE 2 there should be no dash at the end of a line
    # count of cases
    # print('RULE 2 dash at end of lines: ' +
    #     str(len(re.findall('-\n', content)) + len(re.findall('-\W+\n', content))))
    # DELETE DASHS AT THE END OF ALL LINES
    content = re.sub('-\n', '', content)
    content = re.sub('-\W+\n', '', content)


    ### RULE 3: in content, if a single line contains 1-3 words, all these words must be valid English words
    # temp = ''
    # lines = content.strip().split('\n')
    # countInvalid = 0
    # specialWordMap = dict()
    # for line in lines:
    #     validLine = True
    #     groups = re.findall(r'\S+', line)
    #     if len(groups) <= 3:     # the line has 1-3 groups
    #         words = re.findall(r"[\w']+|[\W+]", line)    # split content into words and punctuations
    #         for word in words:
    #             if re.search('\W+', word) is None:  # non-punctuation
    #                 if not utility.validEnglishWord(word, content, specialWordMap):  # not valid word
    #                     countInvalid += 1
    #                     validLine = False
    #                     #print(line + ' False')     # for demo only
    #                     break    # this line is not meaningful, go to next line
    #     if validLine:
    #         temp += line + '\n'
    # content = temp
    # print('RULE 3 invalid lines based on English words: ' + str(countInvalid))

    ### RULE 4: longest English word in major dictionary has 45 letters
    # remove all words longer than 45 letters
    # words = re.finditer(r'\w+', text)
    # countLongWord = 0
    # for word in words:
    #     ind0 = word.span()[0]
    #     ind1 = word.span()[1]
    #     if ind1 - ind0 >= 45:
    #         content = content[:ind0] + content[ind1:]
    #         countLongWord += 1
    # print('RULE 4 long words: ' + str(countLongWord))

    ### RULE 5: Most a single word should not be a multi-punctuation combination, except "--"
    # words = re.findall('\W+', re.sub('\s+', '', content))    # split content into words and punctuations
    # countMultiPunc = 0
    # for word in words:
    #     if len(word) <= 1 or len(re.findall('[^\-]+', word)) == 0:
    #         continue
    #     if word in content:
    #         word = utility.insertSlash(word)
    #         content = re.sub(word, '', content)
    #     countMultiPunc += 1
    # print('RULE 5 meaningless multi punc: ' + str(countMultiPunc))


    ### RULE 6: Regular word should not have !@#$%^&* in the middle of the word
    # specialChar = ['@','#','$','%','^','&','*','+','=']
    # words = re.findall('\S+', re.sub('\n', ' ', content))
    # countNonRegChar = 0
    # for word in words:
    #     for schar in specialChar:
    #         if schar in word:
    #             if word in content:
    #                 print(word)
    #                 word = utility.insertSlash(word)
    #                 content = re.sub(schar, '', content)
    #                 print(word in content)
    #                 countNonRegChar += 1
    #                 break
    # print('RULE 6 non regular character in the word: ' + str(countNonRegChar))
    #

    ### RULE 7: replace all non-ascii character with a single whitespace
    content = re.sub(r'[^\x00-\x7F]+', ' ', content)

    ### RULE 8: replace all citation markers e.g. "[1, 2]" with "TYPE_CITATION"
    content = re.sub(r'\[[\d,\s]+\]', "TYPE_CITATION", content)

    ### RULE 9: replace all digits with "TYPE_DIGIT"
    content = re.sub(r'\s\d+\s', " TYPE_DIGIT ", content)

    # multiline to single line; replace tab by whitespace; remove trailing space
    content = re.sub('\s+', ' ', content).strip()

    ### END ALL PROCESS
    # add filename in the front
    content = filename.split('/')[-1] + '\t' + content + '\n'   
    toFile.write(content)
    fromFile.close()
toFile.close()


