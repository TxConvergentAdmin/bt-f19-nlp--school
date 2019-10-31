import re

def clean(df):
    concat = False
    concatenated = ""
    # just edit df directly and remove columns not needed!?
    # try to combine paragraphs into decent sizes so they're more understandable
    # if colon create new one?
    section = 0
    while section < len(df['paragraphs']):
        i = 0
        while i < len(df['paragraphs'][section]):
            paragraph = df['paragraphs'][section][i]
            if re.search("^.*:\s*$", paragraph) or len(paragraph) <= 10:
                j = i
                concatenated += paragraph
                while i < len(df["paragraphs"][0]) and len(concatenated) < 50:
                    if not re.search("^.*:\\s*$", paragraph): # or (len(df['paragraphs'][section][i+1]) > 50 and df['paragraphs'][section][j] < 10)
                        concatenated += paragraph
                        print(1) # debugging: check concatenation
                    i += 1
                    paragraph = df['paragraphs'][section][i]
                df['paragraphs'][section][j] = concatenated
                print(concatenated) # debugging: check concatentation
                concatenated = "";
            elif len(paragraph) <= 3 or not re.search(".*[a-zA-Z]{2,}.*", paragraph):
                df['paragraphs'][section][j] = ""
            i+=1
        section += 1
    print(df['paragraphs'][0])
    return df
