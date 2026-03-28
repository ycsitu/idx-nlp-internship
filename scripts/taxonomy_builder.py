import nltk
from collections import Counter
from nltk.util import ngrams
import pandas as pd
import json

path = "data/processed/listing_sample.csv"
df = pd.read_csv(path, encoding= 'unicode_escape')
nltk.download('punkt')


# Extract bigrams from remarks
all_text = ' '.join(df['remarks'].dropna().str.lower())
tokens = nltk.word_tokenize(all_text)
bigrams = list(ngrams(tokens, 2))
freq = Counter(bigrams)

# Top 200 bigrams become taxonomy seed
taxonomy_data = {"terms": []}
index = 0

for bigram, count in freq.most_common(200):
    index += 1
    term = ' '.join(bigram)
    taxonomy_data["terms"].append({
            "id": index,
            "term": term,
            "count": count
        })
    print(f"{term}: {count}")


with open("data/processed/taxonomy.json", 'w', encoding='utf-8') as f:
        json.dump(taxonomy_data, f, indent=4)