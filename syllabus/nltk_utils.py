import nltk
from nltk.tag import StanfordNERTagger
import os
import tika
from tika import parser
import re
from enum import Enum, auto

# regex expressions and classification objects used to extract information from a syllabus


class Tag_Type(Enum):
    NER = auto()
    TOKEN_RE = auto()
    LINE_RE = auto()

# type of information (i.e. name, date, time)
class Field:
    def __init__(self,name,tag_type,reg=None,re_map=None):
        self.name = name
        self.tag_type = tag_type
        if reg is not None:
            self.reg = reg
        if re_map is not None:
            self.re_map = re_map

# example-- name: professor; keys: professor, instructor; fields: PERSON; optional_fields: EML, NBR
class Category:
    def __init__(self,name,keys,fields,optional_fields=None):
        self.name = name
        self.keys = keys
        self.fields = fields
        if optional_fields is not None:
            self.opt_fields = optional_fields

    def new_item(self):
        return Item(self.name,[f.name for f in self.fields],[o.name for o in self.opt_fields])

# reresents specific instance of a category (i.e. Professor Calvin Lin)
class Item:
    def __init__(self,name,fields,opt_fields):
        self.name = name
        self.vals = {}
        for f in fields:
            self.vals[f] = None
        self.opt_vals = {}
        for o in opt_fields:
            self.opt_vals[o] = None
        self.line = None

    def complete(self):
        for k in self.vals.keys():
            if not self.vals[k]:
                return False
        return True

    def __str__(self):
        return self.name + ' ' + str(self.vals) + ' ' + str(self.opt_vals)

    def __repr__(self):
        return self.__str__()

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
        'NUM' : r'^(?:30|31|[0-2]?\d)(?:\w\w)?$'
    },
    'FULL': {
        'F' : r'\d{1,2}[/\-]\d{1,2}'
    }
}
date_reg = r'((?:)^'
for k in date:
    for j in date[k]:
        date_reg+= (date[k][j]+'(?:$|:)|^')
date_reg = date_reg[:-9]+')'

person = Field('PERSON',Tag_Type.NER)
email = Field('EML',Tag_Type.TOKEN_RE,reg=r'[\w\.]*@.*\.[\w\.]*')
number = Field('NBR',Tag_Type.LINE_RE,reg=r'\(?\d{3}\)?[\-\s]\d{3}[\-\s]\d{4}')
time = Field('TME',Tag_Type.LINE_RE,reg=r'(?:[12]?\d(?::\d{2})?[^\w\s\.:][12]?\d(?::\d{2})?(?:\s?[aApP]\.?[mM]\.?)?|\d{1,2}\s?[aApP]\.?[mM]\.?|[12]?\d:\d{2}(?:\s?[aApP]\.?[mM]\.?)?)')
date = Field('DTE',Tag_Type.TOKEN_RE,reg=date_reg,re_map=date)
location = Field('LOC',Tag_Type.LINE_RE,reg=r'(?:(?:[A-Z][a-z]+|[A-Z]{3})\s\d\.\d{3}[A-Z]?|[iI]n [cC]lass)')

fields = [person,email,number,time,date,location]
field_map = {'PERSON':person,'EML':email,'NBR':number,'TME':time,'DTE':date,'LOC':location }

professor = Category('professor',['professor', 'instructor'],[person],optional_fields=[email,number])
TA = Category('TA',['TA','teaching assistant'],[person],optional_fields=[email,number])
final = Category('final exam',['final'],[date],optional_fields=[time,location])
midterm = Category('midterm',['midterm','exam','test'],[date],optional_fields=[time,location])
assignment = Category('assignment',['reading','read','paper','essay','homework','problem set'],[date],optional_fields=[time])

categories = [professor,TA,final,midterm,assignment]

# regex for the course ID (i.e. M 408M)
course_name_re = r'[a-zA-Z]{1,4}\s?\d{3}[a-zA-Z]?'
time_range_reg = r'[12]?\d(?::\d{2})?([^\w\s])[12]?\d(?::\d{2})?(?:\s?[aApP]\.?[mM]\.?)?'
