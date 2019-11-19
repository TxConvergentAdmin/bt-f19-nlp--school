from nltk.tokenize import RegexpTokenizer
import spacy

def tokenize(self, str):
    tokenizer = RegexpTokenizer(r'\w+')
    tokenizer.tokenize(str)

def main():
    file_name = "wics_bull_session.txt"
    with open(file_name, 'r') as data:
        f = data.read()
    
        nlp = spacy.load("en_core_web_sm")     
        doc = nlp(f)
        for token in doc:
            print(token.text, token.pos_, token.dep_)
            
main()
