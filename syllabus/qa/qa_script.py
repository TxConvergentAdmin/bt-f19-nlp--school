
from cdqa.utils.converters import pdf_converter
from cdqa.utils.download import download_model
from cdqa.pipeline.cdqa_sklearn import QAPipeline
from cdqa.utils.converters import df2squad
from remove_noise import clean
import re

filepath = "../qa/syllabus_run_files"

def get_data(filepath):
    # Loading data and filtering / preprocessing the documents
    df = pdf_converter(directory_path=filepath)
    # print(df.dtypes)
    df = clean(df)

    # Download if model not already downloaded
    download_model(model='bert-squad_1.1', dir='./models')

    # Loading QAPipeline with CPU version of BERT Reader pretrained on SQuAD 1.1
    cdqa_pipeline = QAPipeline(reader='models/bert_qa_vCPU-sklearn.joblib')
    #cdqa_pipeline.cuda()

    # Fitting the retriever to the list of documents in the dataframe
    cdqa_pipeline.fit_retriever(df=df)
    #cdqa_pipeline.fit_reader("/mnt/c/Users/amerj/Documents/python_atom/nlp_syllabus/trained_sets/10_26_2019.json")

    return cdqa_pipeline

# store keys with colons following string, data in next string is value? then default to predict?
def run_queries(cdqa_pipeline):
    qa_txt = """Who is the professor?^Who is the TA?
    ^What materials are required?^When is the last midterm?"""
    queries = qa_txt.split("^")

    # Sending a question to the pipeline and getting prediction
    i = 1
    answer = {}
    answer['number'] = []
    answer['query'] = []
    answer['answer'] =  []
    answer['paragraph'] = []
    for query in queries:
        found = False
        # for section in df['paragraphs']:
        #     for paragraph in section:
        #         for word in query.lower().split():
        #             if word[-1:] == "?":
        #                 wordCheck = word[:-1].lower()
        #             else:
        #                 wordCheck = word.lower()
        #             #colonIndex = -1
        #             #if ":" in paragraph:
        #                 #for str in paragraph.split():
        #                     #if ":" in str:
        #
        #             if (wordCheck + ":") in paragraph.lower().split(): # re.search("\W+" + wordCheck + "\W+.*:$", paragraph.lower()) or re.search(wordCheck + ":$", paragraph.lower()) or
        #                 print("Query Number: " + str(i))
        #                 print('Query: {}'.format(query))
        #                 print('Answer: {}\n'.format(paragraph))
        #                 found = True
        #                 break

        if not found:
            prediction = cdqa_pipeline.predict(query=query, n_predictions=5)
            print(prediction)
            index = -1
            for t in range(0,4):
                if len(prediction[t][0]) > 6:
                    index = t
                    break

            if index == -1:
                index = 0

            answer['number'].append(str(i))
            answer['query'].append(query)
            answer['answer'].append(prediction[index][0])
            answer['paragraph'].append(prediction[index][2])

            # print("Query Number: " + str(i))
            # print('Query: {}'.format(query))
            # print('Answer: {}'.format(prediction[index][0]))
            # print('Title: {}'.format(prediction[index][1]))
            # print('Paragraph: {}\n'.format(prediction[index][2]))

        i+=1

    return answer


def query(cdqa_pipeline):
    query = input("Enter a question for your syllabus: ")

    prediction = cdqa_pipeline.predict(query=query, n_predictions=5)
    index = -1
    for t in range(0,4):
        if len(prediction[t][0]) > 6:
            index = t
            break

    if index == -1:
        index = 0

    print('Query: {}'.format(query))
    print('Answer: {}'.format(prediction[index][0]))
    print('Title: {}'.format(prediction[index][1]))
    print('Paragraph: {}\n'.format(prediction[index][2]))


if __name__ == '__main__':
     cdqa_pipeline = get_data(filepath)
     #print(run_queries(cdqa_pipeline))
     query(cdqa_pipeline)
