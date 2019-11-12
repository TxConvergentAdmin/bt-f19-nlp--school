import nltk
from nltk.tag import StanfordNERTagger
import os
import tika
from tika import parser
import re
import nltk_utils as util


# this needs to be where your java.exe file is
java_path = "C:/Program Files/Java/jdk-10.0.1/bin/java.exe"
os.environ['JAVAHOME'] = java_path
filename = 'nlp-school/syllabus/syllabus_files/M408M.pdf'


def pdf_to_text(filename):
    parsed = parser.from_file(filename)
    cont = parsed['content']
    return cont

# splits into paragraphs
def split_newline(text):
    return re.compile(r'\n+(?![a-z])').split(text)

# splits paragraphs into words
def tokenize(lines):
    return [re.compile(r'\.?,?:?(?:\s+|$)').split(ln) for ln in lines]

def re_format(str):
    return "(?:^|\W+)"+str+"(?:$|\W+)"

def tagger():
    stanford_ner_tagger = StanfordNERTagger(
        'stanford-ner/' + 'classifiers/english.muc.7class.distsim.crf.ser.gz',
        'stanford-ner/' + 'stanford-ner-3.9.2.jar'
    )
    return stanford_ner_tagger

# this should return a map where each key is a field and each value is a list of lists
# each item in the list is a list of the words that match the field regex in that line of the text
def tag_by_line(text):
    lines = split_newline(text)
    split = tokenize(lines)
    items = {}
    regex = []
    for f in util.fields:
        items[f.name] = []
        if f.tag_type == util.Tag_Type.TOKEN_RE:
            regex.append((f.reg,f.name))

    ner_tagger = tagger()
    reg_tagger = nltk.RegexpTagger(regex)

    tags = [ner_tagger.tag(words) for words in split]
    for t,s in zip(tags,split):
        t.extend(reg_tagger.tag(s))

    # for fields that are tagged by word, aggregate neighboring tags of the same type and add them to the map of items
    keys = [f.name for f in util.fields if (f.tag_type == util.Tag_Type.NER or f.tag_type == util.Tag_Type.TOKEN_RE)]
    current_string = ''
    current_type = None
    i = -1
    for line in tags:
        i+=1
        for key in keys:
            items[key].append([])
        for tag in line:
            val = tag[0]
            type = tag[1]
            if type != current_type:
                if len(current_string) > 0:
                    items[current_type][i].append(current_string[:-1])
                current_string = ''
                current_type = type
            if type in keys:
                current_string+= val + ' '

    # for fields that are matched by line, do regex and add them to the map of items
    for line in lines:
        for f in util.fields:
            if f.tag_type == util.Tag_Type.LINE_RE:
                matches = re.findall(f.reg,line)
                items[f.name].append([m for m in matches])

    return items


def main():
    text = pdf_to_text(filename)
    tag_map = tag_by_line(text)
    #print(tag_map)
    lines = split_newline(text)
    items = {}
    for cat in util.categories:
        items[cat.name] = []
    for i in range(len(lines)):
        for cat in util.categories:
            for key in cat.keys:
                if re.search(re_format(key),lines[i],re.IGNORECASE):
                    item = cat.new_item()
                    item.line = lines[i]
                    for field in item.vals.keys():
                        if tag_map[field][i]:
                            item.vals[field] = tag_map[field][i][0]
                    for field in item.opt_vals.keys():
                        if tag_map[field][i]:
                            item.opt_vals[field] = tag_map[field][i][0]
                    items[cat.name].append(item)

    # if the prof doesn't have an email, search the emails for their name
    prof = None
    if items['professor'] is not []:
        prof = items['professor'][0]
        if prof.opt_vals['EML'] is None:
            name = prof.vals['PERSON'].split()
            for eml in tag_map['EML']:
                for n in name:
                    if re.search(n,eml,re.IGNORECASE):
                        prof.opt_vals['EML'] = eml

    # look for a course ID (i.e. M 408M)
    courseID = None
    for line in lines:
        m = re.search(util.course_name_re,line)
        if m:
            courseID = m.group(0)
            break

    print(courseID)
    for key in items.keys():
        print(key,[i for i in items[key] if i.complete()])


if __name__ == '__main__':
    main()
