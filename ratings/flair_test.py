import flair

sentence = "Hasn’t taught undergrad before"
flair_sentiment = flair.models.TextClassifier.load('en-sentiment')
s = flair.data.Sentence(sentence)
flair_sentiment.predict(s)
total_sentiment = s.labels
print(total_sentiment)


