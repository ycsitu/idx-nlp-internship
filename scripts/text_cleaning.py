import re
import pandas as pd
import nltk
from collections import Counter
import unicodedata

class TextCleaner:
    def __init__(self):
        self.abbrev_map = {

            'br': 'bedroom',
            'bed': 'bedroom',
            'ba': 'bathroom',
            'bath': 'bathroom',
            'bth': 'bathroom',
            'mbr': 'master bedroom',
            'kit': 'kitchen',
            'kitn': 'kitchen',

            'a/c': 'air conditioning',
            'ac': 'air conditioning',
            'hwy': 'highway',
            'apt': 'apartment',

            'w/': 'with',
            'w': 'with',
            'w/o': 'without',

            # units
            'sqft': 'square feet',
            'sf': 'square feet',

            # single digit numbers (technically not abbrevs :))
            'one': '1',
            'two': '2',
            'three': '3',
            'four': '4',
            'five': '5',
            'six': '6',
            'seven': '7',
            'eight': '8',
            'nine': '9',
            'ten': '10',

            }
        
    def clean_text(self, text):
        text = self.normalize_unicode(text)
        text = self.normalize_prices(text)
        text = self.normalize_measurements(text)
        text = self.expand_abbreviations(text)
        return text.strip()
    
    def normalize_unicode(self, text):
        return unicodedata.normalize("NFKD", text)

    def normalize_prices(self, text):
        # 450k → 450000
        text = re.sub(r'(\d+)k', lambda m: str(int(m.group(1))*1000), text, flags=re.I)
        
        # 1.2m → 1200000
        text = re.sub(r'(\d+\.?\d*)m', lambda m: str(int(float(m.group(1))*1000000)), text, flags=re.I)
        
        return text
    
    def normalize_measurements(self, text):
        # 12,000 -> 12000
        text = re.sub(r'(\d),(\d)', r'\1\2', text)

        # 12 000 -> 12000
        text = re.sub(r'(\d) (\d)', r'\1\2', text)
        
        # sq ft, sq.ft., sqft, sf, sq feet - > square feet    
        text = re.sub(r'(\d+)\s*sqft', r'\1 square feet', text, flags=re.I) # check against init
        
        return text
    
    def expand_abbreviations(self, text):
        for abbrev, full in self.abbrev_map.items():
            text = re.sub(r'\b' + re.escape(abbrev) + r'\b', full, text, flags=re.I)
        return text
    
    def _extract_top_ngrams(self, df):
        n = 20

        all_text = ' '.join(df.dropna().str.lower())
        tokens = nltk.word_tokenize(all_text)
        bigrams = list(nltk.ngrams(tokens, 2))
        freq = Counter(bigrams)

        return freq.most_common(n)

    def _detect_abbreviations(self, df):
        counts = {}

        for text in df.dropna():
            words = text.split()

            for word in words:
                if word in self.abbrev_map:
                    counts[word] = counts.get(word, 0) + 1
        return counts.items()

    def profile_column(self, df, column_name):
        """Analyze what's actually in L_Remarks"""
        return {
            'null_rate': df[column_name].isnull().mean(),
            'avg_length': df[column_name].str.len().mean(),
            'common_terms': self._extract_top_ngrams(df[column_name]),
            'price_mentions': df[column_name].str.contains(r'\$\d').sum(),
            'has_html': df[column_name].str.contains('<').sum(),
            'common_abbreviations': self._detect_abbreviations(df[column_name])
        }
    
cleaner = TextCleaner()
df = pd.read_csv('data/processed/listing_sample.csv', encoding="unicode_escape")
df['remarks'].apply(cleaner.clean_text)
df.to_csv('data/processed/cleaned_listing.csv', index=False)

# Use this to guide your cleaning strategy:
profile = cleaner.profile_column(df, 'remarks')
print(f"HTML tags found in {profile['has_html']} listings")
print(f"Common abbreviations: {profile['common_abbreviations']}")