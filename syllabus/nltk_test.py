article = '''
o.walker@utexas.edu
January 10th'''

import nltk
from nltk.tag import StanfordNERTagger
import os
import tika
from tika import parser
import re


# this needs to be where your java.exe file is
java_path = "C:/Program Files/Java/jdk-10.0.1/bin/java.exe"
os.environ['JAVAHOME'] = java_path

file = open("nlp-school/syllabus/syllabus_files/M408M.pdf","rb")
parsed = parser.from_file('nlp-school/syllabus/syllabus_files/M408M.pdf')
cont = parsed['content']
#cont_lines = re.compile("(?:\n*\.\s+\n*|\n+)").split(cont)


stanford_ner_tagger = StanfordNERTagger(
    'stanford-ner/' + 'classifiers/english.muc.7class.distsim.crf.ser.gz',
    'stanford-ner/' + 'stanford-ner-3.9.2.jar'
)
article = re.compile('\.?,?[\s\n]+').split(cont)
#article = re.compile('\n+').split(cont)

date = {
    'MONTH': {
        'JANUARY' : r'(?:January|Jan\.?)',
        'FEBRUARY' : r'(?:February|Feb\.?)',
        'MARCH' : r'(?:March|Mar\.?)',
        'APRIL' : r'(?:April|Apr\.?)',
        'MAY' : r'(?:May|May\.?)',
        'JUNE' : r'(?:June|Jun\.?)',
        'JULY' : r'(?:July|Jul\.?)',
        'AUGUST' : r'(?:August|Aug\.?)',
        'SEPTEMBER' : r'(?:September|Sept\.?)',
        'OCTOBER' : r'(?:October|Oct\.?)',
        'NOVEMBER' : r'(?:November|Nov\.?)',
        'DECEMBER' : r'(?:December|December\.?)'
    },
    'WEEKDAY' : {
        'MONDAY' : r'(?:Monday|Mon\.?|M\.?)',
        'TUESDAY' : r'(?:Tuesday|Tues\.?|T\.?)',
        'WEDNESDAY' : r'(?:Wednesday|Wed\.?|W\.?)',
        'THURSDAY' : r'(?:Thursday|Thurs\.?|Th\.?)',
        'FRIDAY' : r'(?:Friday|Fri\.?|F\.?)',
        'SATURDAY' : r'(?:Saturday|Sat\.?|S\.?)',
        'SUNDAY' : r'(?:Sunday|Sun\.?)',
        'RANGE' : r'(?=.)(?:M?T?W?(?:Th)?F?S?)'
    },
    'NUMBER' : {
        'NUM' : r'(?:30|31|[0-2]?\d)(?:\w\w)?'
    },
    'FULL': {
        'F' : r'\d{1,2}[/\-]\d{1,2}'
    }
}


regex = [
    (r'[\w\.]*@.*\.[\w\.]*','EML'),
    (r'(?:\d{1,2}:\d\d(?:\s*\w{1,2})?|\d{1,2}\s?(?:a\.?m\.?|A\.?M\.?|a\.?|p\.?m\.?|P\.?M\.?|p\.?))','TME'),
]
date_reg = r'((?:)^'
for k in date:
    for j in date[k]:
        date_reg+= (date[k][j]+'(?:$|:)|^')
date_reg = date_reg[:-9]+')'
#print(date_reg)
regex.append((date_reg,'DTE'))


regexp_tagger = nltk.RegexpTagger(regex)



results = stanford_ner_tagger.tag(article)
results.extend(regexp_tagger.tag(article))
#results.extend(nltk.pos_tag(article))

#print(results)
items = {
    'EML':[],
    'TME':[],
    'DTE':[],
    'PERSON':[]
}

'''
print('Original Sentence: %s' % (article))
for result in results:
    tag_value = result[0]
    tag_type = result[1]
    if tag_type not in ['O', None,'ORGANIZATION']:
        print('Type: %s, Value: %s' % (tag_type, tag_value))
        '''

current = ""
currentType = None
for result in results:
    val = result[0]
    type = result[1]
    if type != currentType:
        if len(current) > 0:
            items[currentType].append(current[:-1])
        current = ''
        currentType = type
    if type in items.keys():
         current+=val + " "





print(items)
