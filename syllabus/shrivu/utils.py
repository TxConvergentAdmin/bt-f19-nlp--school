from cdqa.utils.converters import pdf_converter
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag.stanford import StanfordNERTagger
from spacy.lang.en import English
import nltk
import json
#nltk.download()



def pdf_to_tokens(dir_name='.'):
    sents = []
    df = pdf_converter(directory_path=dir_name)
    for line in df["paragraphs"][0]:
        sents.extend(sent_tokenize(line))
    sent_tokens = []
    for sent in sents:
        sent_tokens.append(word_tokenize(sent))
    return sent_tokens


def tokens_to_labeling_csv(sent_tokens, filename):
    with open(filename, 'w') as f:
        f.write('sent,token,label\n')
        for i, tokens in enumerate(sent_tokens):
            f.write('{},--,--\n'.format(i))
            for token in tokens:
                f.write('{},{},\n'.format(i,token))

def csv_to_training_data_format(filename, outname):
    # java -cp "stanford-ner-3.9.2.jar:lib/*" -mx4g edu.stanford.nlp.ie.crf.CRFClassifier -prop train/prop.txt
    with open(outname, 'w') as of:
        with open(filename, 'r') as f:
            for line in f.readlines():
                sent_id, token, label = line.strip().split(',')
                if token == '--':
                    continue
                if len(label) == 0 and token != 'token':
                    of.write('{}\t{}\n'.format(token, 'O'))
                else:
                    of.write('{}\t{}\n'.format(token, label.upper()))

def create_tagger():
    jar = './stanford-ner-tagger/stanford-ner.jar'
    model = './stanford-ner-tagger/school-ner.ser.gz'
    ner_tagger = StanfordNERTagger(model, jar, encoding='utf8')
    def predict(sentence):
        words = nltk.word_tokenize(sentence)
        return ner_tagger.tag(words)
    return predict

# tokens_to_labeling_csv(pdf_to_tokens('.'), 'out.csv')
# csv_to_training_data_format('out1.csv', 'ner.tsv')

sentence = u"The Vocab worksheet is due on November 5th"
print(create_tagger()(sentence))
