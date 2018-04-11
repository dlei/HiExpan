'''
__author__: Keqian Li
__description__: Used to parse text fields from the original singal processing XML file. 
'''

from lxml import etree
import re

file = '/local/home/klee/workspace/data/pdf/Signal Processing (2002-2016).xml'
file_output = file+'_processed.txt'

def listget(list, index, default=None):
    try:
        return list[index]
    except IndexError:
        return default

newline = re.compile(r'[\r\n]+')
headerSeparater = ':::::'
fieldSeparater = ';;;;;'

def removeNewLineToken(s):
    try:
        return re.sub(newline, lineSeparater, s)
    except Exception, e:
        return ''

def processStreaming(file):
  coords = etree.parse(file).getroot()
  with open(file_output, 'w') as f_out:
    for record in coords.xpath('record'):
      docid, title, abstract = [removeNewLineToken(listget(record.xpath('%s//text()'%name), 0)) for name in ['docid', 'title', 'abstract']]
      # record.xpath('title//text()')[0], record.xpath('abstract//text()')[0]
      f_out.write(docid+headerSeparater+title+fieldSeparater+abstract+'\n') 

processStreaming(file)