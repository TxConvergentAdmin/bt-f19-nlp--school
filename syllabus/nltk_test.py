article = '''
o.walker@utexas.edu
January 10th'''


import nltk
from nltk.tag import StanfordNERTagger
import os
java_path = "C:/Program Files/Java/jdk-10.0.1/bin/java.exe"
os.environ['JAVAHOME'] = java_path


stanford_ner_tagger = StanfordNERTagger(
    'stanford-ner/' + 'classifiers/english.muc.7class.distsim.crf.ser.gz',
    'stanford-ner/' + 'stanford-ner-3.9.2.jar'
)

article = article.split()

regex = [
    (r'.*@.*\..*','EML')
]
regexp_tagger = nltk.RegexpTagger(regex)


results = stanford_ner_tagger.tag(article)
results.extend(regexp_tagger.tag(article))

#print(results)

print('Original Sentence: %s' % (article))
for result in results:
    tag_value = result[0]
    tag_type = result[1]
    if tag_type not in ['O', None]:
        print('Type: %s, Value: %s' % (tag_type, tag_value))
