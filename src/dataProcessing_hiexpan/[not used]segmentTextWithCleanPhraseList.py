'''
__author__: Ellen Wu
__description__: segment a corpus file with provided clean phrase list
    input: 1)corpus_file: per sentence per line; 2)phrase_file: per phrase per line
    output: 1)segmented text in the same format as segphrase
'''
import sys
from collections import defaultdict

corpus_file = sys.argv[1]
phrase_file = sys.argv[2]
output = corpus_file + '.segmented'
length2phraselist = defaultdict(set)
with open(corpus_file) as f_text, open(phrase_file) as f_phrase, open(output, 'w') as fout:
  for line in f_phrase:
    phrase_tokens = line.strip('\r\n').split()
    length2phraselist[len(phrase_tokens)].add(line.strip('\r\n'))
  phrase_lengths = sorted(list(length2phraselist.keys()), reverse=True)

  for line in f_text:
    starts = []
    ends = []
    tokens = line.strip('\r\n').split()
    cursor = 0
    while cursor < len(tokens):
      for l in phrase_lengths:
        if (cursor+l) > len(tokens):
          continue
        if ' '.join(tokens[cursor:cursor+l]).lower() in length2phraselist[l]:
          starts.append(cursor)
          ends.append(cursor+l)
          cursor = cursor+l
          break
        if l == phrase_lengths[-1]:
          cursor = cursor+1

    for i in range(1, len(starts)+1):
      tokens = tokens[:starts[-i]] + ['<phrase>'] + tokens[starts[-i]:ends[-i]] + ['</phrase>'] + tokens[ends[-i]:]
    fout.write(' '.join(tokens)+'\n')

