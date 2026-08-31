from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pandas as pd
import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class IntentClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=500)
        self.model = LogisticRegression()
        self.labels = ['browsing', 'researching', 'ready_to_buy']

    def train(self, queries, labels):
        X = self.vectorizer.fit_transform(queries)
        self.model.fit(X, labels)

    def predict(self, query):
        X = self.vectorizer.transform([query])
        probas = self.model.predict_proba(X)[0]
        intent = self.labels[probas.argmax()]
        confidence = probas.max()
        return intent, confidence
    
with open('../data/processed/sample_queries_buyerintent.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
classifier = IntentClassifier()

queries = [item for item in data['query']]
labels = [item for item in data['intent']]

X_train, X_test, y_train, y_test = train_test_split(
    queries, labels, test_size=0.25
)

classifier.train(X_train, y_train)

results = [classifier.predict(query) for query in X_test]

y_pred = [r[0] for r in results]
confidence = [r[1] for r in results]
accuracy = accuracy_score(y_test, y_pred)

df = pd.DataFrame({
    'query': X_test,
    'true_intent': y_test,
    'predicted_intent': y_pred,
    'correct': np.array(y_test) == np.array(y_pred),
    'confidence': confidence,
})

print(f"Test Accuracy: {accuracy * 100:.2f}%")