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
    items = info(filename)
    d = infoJSON(items)
    print(d)

def info(file):
    print('NER: running...')
    text = pdf_to_text(file)
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

    for lns in tag_map['TME']:
        if lns != []:
            items['time'] = lns[0]
            break

    for lns in tag_map['LOC']:
        if lns != []:
            items['place'] = lns[0]
            break

    for line in lines:
        for days in util.days.keys():
            if re.search(days,line,re.IGNORECASE):
                items['days'] = util.days[days]
                break


    # identify midterm names i.e. Exam 2 and check for in class times
    for mid in items['midterm']:
        s = re.search('(?P<name>(?:midterm|exam|test))\s*(?P<num>\d+)?',mid.line,re.IGNORECASE)
        if s is not None:
            if s.group('num') is not None:
                mid.name = s.group('name') + ' ' + s.group('num')
            else:
                mid.name = s.group('name')

        if mid.opt_vals['LOC'] is not None and mid.opt_vals['LOC'].lower() == 'in class':
            if 'time' in items.keys():
                mid.opt_vals['TME'] = items['time']
            if 'place' in items.keys():
                mid.opt_vals['LOC'] = items['place']

    # clean up the date field
    for cat in ['midterm','final exam','assignment','office hours']:
        itms = items[cat]
        for it in itms:
            date = it.vals['DTE']
            if date is None:
                continue
            weekday = ''
            day = ''
            month = ''
            # get the weekday
            for wkd in util.dates['WEEKDAY'].keys():
                if re.search(util.dates['WEEKDAY'][wkd],date):
                    weekday = wkd.capitalize()
                    break
            # get the month
            for mnth in util.dates['MONTH'].keys():
                if re.search(util.dates['MONTH'][mnth],date):
                    month = mnth.capitalize()
            # get the day
            if month is not '':
                s = re.search(month+r'\W+(?P<d>\d{1,2})',date,re.IGNORECASE)
                if s:
                    day = s.group('d')
                else:
                    s = re.search(r'(?P<d>\d{1,2})',date)
                    if s:
                        day = s.group('d')
            # mm/dd format
            if month is '':
                s = re.search(r'(?P<m>\d{1,2})[/\-](?P<d>\d{1,2})',date)
                if s:
                    day = s.group('d')
                    month = util.months[s.group('m')-1] if s.group('m') < 13 else ''

            if weekday is '':
                if day is '' or month is '':
                    it.vals['DTE'] = None
                    continue
            else:
                it.vals['DTE'] = (weekday + ' ' + month + ' ' + day).strip()

    # remove non-complete items
    for cat in items.keys():
        i = 0
        while (i < len(items[cat])):
            itm = items[cat][i]
            if type(itm) is util.Item and not itm.complete():
                print(items[cat][i])
                del items[cat][i]
            else:
                i+=1


    # look for a course ID (i.e. M 408M)
    courseID = None
    for line in lines:
        m = re.search(util.course_name_re,line)
        if m:
            courseID = m.group(0)
            break
    if courseID is not None:
        items['course'] = courseID

    # assign professor to be one professor item
    prof = None
    if items['professor'] != []:
        prof = items['professor'][0]
    else:
        names = tag_map['PERSON']  # if we didn't find a professor, just use the first name found
        for i in range(len(names)):
            if names[i] != []:
                prof = item('professor',['PERSON'],['EML','NBR'])
                prof.vals['PERSON'] = names[i][0]
                break
    if prof is not None:
        items['professor'] = prof
        if prof.opt_vals['EML'] is None: # look for the profs name in all the emails
            name = prof.vals['PERSON'].split()
            for emls in tag_map['EML']:
                for eml in emls:
                    for n in name:
                        if re.search(n,eml,re.IGNORECASE):
                            prof.opt_vals['EML'] = eml

    # remove extra items
    for cat in ['final exam','office hours']:
        if items[cat] != []:
            items[cat] = items[cat][0]

    print('NER: DONE')
    return items

def infoJSON(info):
    info_dict = {}
    for key in info.keys():
        items = info[key]
        if type(items) == util.Item:
            d = items.to_dict()
            info_dict[key] = d
        elif type(items) == list:
            info_dict[key] = []
            for itm in items:
                d = itm.to_dict()
                info_dict[key].append(d)
        else:
            info_dict[key] = items

    return info_dict


if __name__ == '__main__':
    main()
