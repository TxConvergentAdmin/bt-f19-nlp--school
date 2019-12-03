import re

def clean(df):
    concatenated = ""
    # just edit df directly and remove columns not needed!?
    # try to combine paragraphs into decent sizes so they're more understandable
    # if colon create new one?
    section = 0
    #print(df['paragraphs'][0]) # debugging: show all paragraphs before processing
    while section < len(df['paragraphs']):
        i = 0
        while i < len(df['paragraphs'][section]):
            #df['paragraphs'][section][i] = re.sub('\s+', ' ', df['paragraphs'][section][i])
            paragraph = df['paragraphs'][section][i]
            split = paragraph.split()
            if re.search("^.*:\s*$", paragraph) or len(split) <= 5:
                j = i
                concatenated += paragraph
                while i < len(df["paragraphs"][section]) and len(concatenated) < 120:
                    #df['paragraphs'][section][i] = re.sub('\s+', ' ', df['paragraphs'][section][i])
                    paragraph = df['paragraphs'][section][i]
                    concatenated +=  " " + paragraph
                    df['paragraphs'][section][i] = ""
                    # if re.search("^.*:\s*$", paragraph) and i+1 < len(df["paragraphs"][section]):
                    #     i += 1
                    #     #df['paragraphs'][section][i] = re.sub('\s+', ' ', df['paragraphs'][section][i])
                    #     paragraph = df['paragraphs'][section][i]
                    #     concatenated += " " + paragraph
                    if len(concatenated) < 120:
                        i += 1
                df['paragraphs'][section][j] = concatenated
                #print(df['paragraphs'][section][j]) # debugging: check concatentation
                concatenated = "";
            elif len(paragraph) <= 3 or not re.search(".*[a-zA-Z]{1,}.*", paragraph):
                df['paragraphs'][section][j] = ""
            i+=1
        section += 1
    #print(df['paragraphs'][0]) # debugging: show all paragraphs post processing
    return df
