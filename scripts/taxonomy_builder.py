import nltk
from collections import Counter
from nltk.util import ngrams
from nltk.corpus import stopwords
import pandas as pd
import json

df = pd.read_csv("../data/processed/listing_sample.csv", encoding= 'unicode_escape')
nltk.download('punkt')
nltk.download('stopwords')


# Extract bigrams from remarks
all_text = ' '.join(df['remarks'].dropna().str.lower())
stop_words = set(stopwords.words('english'))
custom_stop_words = [",", ".", "!"]
stop_words.update(custom_stop_words)
tokens = [word for word in nltk.word_tokenize(all_text) if word not in stop_words]
bigrams = list(ngrams(tokens, 2))
freq = Counter(bigrams)

# Top 200 bigrams become taxonomy seed
taxonomy_data = {"terms": []}
index = 0
categories = [ # not implemented yet
      "Location",
      "Rooms",
      "Amenities",
      "Condition",
      "Financing",
]

for bigram, count in freq.most_common(200):
    index += 1
    term = ' '.join(bigram)
    taxonomy_data["terms"].append({
            "id": index,
            "term": term,
            "count": count, 
            "category": "Uncategorized"
        })


with open("../data/processed/taxonomy.json", 'w', encoding='utf-8') as f:
        json.dump(taxonomy_data, f, indent=4)