import pandas as pd
from ast import literal_eval

from cdqa.utils.filters import filter_paragraphs
from cdqa.utils.download import download_model, download_bnpp_data
from cdqa.pipeline.cdqa_sklearn import QAPipeline
from cdqa.utils.converters import df2squad
from cdqa.utils.converters import pdf_converter

# Download data and models
download_model(model='bert-squad_1.1', dir='./models')

# Loading data and filtering / preprocessing the documents
df = pdf_converter(directory_path='/mnt/c/Users/amerj/Documents/python_atom/syllabus_files')

# Loading QAPipeline with CPU version of BERT Reader pretrained on SQuAD 1.1
cdqa_pipeline = QAPipeline(reader='models/bert_qa_vGPU-sklearn.joblib')

# Fitting the retriever to the list of documents in the dataframe
cdqa_pipeline.fit_retriever(df)

# Sending a question to the pipeline and getting prediction
query = 'Where are quizzes and exams?'
prediction = cdqa_pipeline.predict(query)

print('query: {}\n'.format(query))
print('answer: {}\n'.format(prediction[0]))
print('title: {}\n'.format(prediction[1]))
print('paragraph: {}\n'.format(prediction[2]))
