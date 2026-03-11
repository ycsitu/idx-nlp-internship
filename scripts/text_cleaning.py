import re

class TextCleaner:
    def __init__(self):
        self.abbrev_map = {
            'br': 'bedroom', 'ba': 'bathroom', 'sqft': 'square feet',
            'w/': 'with', 'w/o': 'without', 'mbr': 'master bedroom'
            }
        
    def clean_text(self, text):
        text = self.normalize_unicode(text)
        text = self.normalize_prices(text)
        text = self.normalize_measurements(text)
        text = self.expand_abbreviations(text)
        return text.strip()
    
    def normalize_prices(self, text):
        # 450k → 450000
        text = re.sub(r'(\d+)k', lambda m: str(int(m.group(1))*1000), text, flags=re.I)
        
        # 1.2m → 1200000
        text = re.sub(r'(\d+\.?\d*)m', lambda m: str(int(float(m.group(1))*1000000)), text, flags=re.I)
        
        return text
    
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
    
# Use this to guide your cleaning strategy:
profile = cleaner.profile_column(df, 'remarks')
print(f"HTML tags found in {profile['has_html']} listings")
print(f"Common abbreviations: {profile['common_abbreviations']}")