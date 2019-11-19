
from cdqa.utils.converters import pdf_converter
from cdqa.utils.download import download_model
from cdqa.pipeline.cdqa_sklearn import QAPipeline
from cdqa.utils.converters import df2squad
from remove_noise import clean

def main():
    # Loading data and filtering / preprocessing the documents
    df = pdf_converter(directory_path='/mnt/c/Users/amerj/Documents/python_atom/nlp_syllabus/syllabus_run_files')
    # print(df.dtypes)
    df = clean(df)

    # Download if model not already downloaded
    # download_model(model='bert-squad_1.1', dir='./models')

    # Loading QAPipeline with CPU version of BERT Reader pretrained on SQuAD 1.1
    cdqa_pipeline = QAPipeline(reader='models/bert_qa_vGPU-sklearn.joblib')
    #cdqa_pipeline.cuda()

    # Fitting the retriever to the list of documents in the dataframe
    cdqa_pipeline.fit_retriever(df)
    #cdqa_pipeline.fit_reader("/mnt/c/Users/amerj/Documents/python_atom/nlp_syllabus/trained_sets/10_26_2019.json")

    print(df)
    return cdqa_pipeline, df

# store keys with colons following string, data in next string is value? then default to predict?
def run_queries(cdqa_pipeline, df):
    qa_txt = """Who is the professor?^Who is the TA?^What is the grading policy?^What is the grade distribution?^What materials are required?
    ^What is the professor’s email?^What is the textbook?^What is the homework for October 13th?^Where is class?^Where are lectures?^Where are discussions?
    ^Where is homework posted?^Where are the professor’s office hours?^Where are the TA’s office hours?^When are tests?^When are quizzes?
    ^When is the final?^When are the TA’s/professor’s office hours?^When is homework due?^Is attendance mandatory?^Is there a final?^Is the class hard?
    ^Is a midterm dropped?^Are there any homework assignments dropped?^Is homework dropped?^Are there any papers?^Is there a curve?
    ^Do I have to buy a textbook?^Does the professor take attendance?^How much is homework/midterms/the final worth?^How hard is this class?
    ^How good is the professor?^How many homework assignments are there?^How many midterms are there?"""
    queries = qa_txt.split("^")

    # Sending a question to the pipeline and getting prediction
    i = 1
    for query in queries:
        found = False
        for section in df['paragraphs']:
            for paragraph in section:
                for word in query.lower().split():
                    if word[-1:] == "?":
                        wordCheck = word[:-1].lower() + ":"
                    else:
                        wordCheck = word.lower() + ":"
                    if wordCheck in paragraph.lower().split():
                        print("Query Number: " + str(i))
                        print('Query: {}'.format(query))
                        print('Answer: {}\n'.format(paragraph))
                        found = True
                        break

        if not found:
            prediction = cdqa_pipeline.predict(query)

            print("Query Number: " + str(i))
            print('Query: {}'.format(query))
            print('Answer: {}'.format(prediction[0]))
            print('Title: {}'.format(prediction[1]))
            print('Paragraph: {}\n'.format(prediction[2]))

        i+=1

if __name__ == '__main__':
    cdqa_pipeline, df = main()
    run_queries(cdqa_pipeline, df)
