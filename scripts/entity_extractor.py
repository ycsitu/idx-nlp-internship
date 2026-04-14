import re
import pandas as pd
import json

class EntityExtractor:
    def extract_bedrooms(self, text):
        patterns = [
            r'(\d+)\s*?\w*?(?:bed|br|bedroom|bd)s?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return int(match.group(1))
        return None
    
    def extract_bathrooms(self, text):
        patterns = [
            r'(\d+)\s*?\w*?(?:bath|ba|bathroom|bth)s?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return int(match.group(1))
        return None

    def extract_sqft(self, text):
        patterns = [
            r'(\d+)\s?(?:\w+\s+)?((?:square|sq)\s(?:feet|foot|ft))\b',
            r'(\d+)\s?(?:\w+\s+)?(?:sqft)\b',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return int(match.group(1))
        return None
    
    def extract_price(self, text):
        patterns = [r'\$?(\d{5,})', r'\$(\d+)']
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return int(match.group(1))
        return None
    
    def extract_amenities(self, text):
        amenities = []
        for bigram in taxonomy_data:
            if bigram.get('category') == "Amenities":
                amenities.append(bigram.get('term')) 
        
        found = []
        for a in amenities:
            if re.search(rf'\b{re.escape(a)}\b', text, re.I):
                found.append(a)
        if(len(found) == 0):
            return None
        return len(found)
    
    def extract_all(self, text):
        return {
            'bedrooms': self.extract_bedrooms(text),
            'bathrooms': self.extract_bathrooms(text),
            'price': self.extract_price(text),
            'sqft': self.extract_sqft(text),
            'amenities': self.extract_amenities(text)
            } 
    
# assume df is cleaned
df = pd.read_csv('data/processed/cleaned_listing.csv', encoding="unicode_escape")

with open('data/processed/taxonomy.json', 'r', encoding='utf-8') as f:
    taxonomy_data = json.load(f)["terms"]

extractor = EntityExtractor()
df['amenities_res'] = df['remarks'].apply(lambda x: extractor.extract_amenities(x))
df['price_res'] = df['remarks'].apply(lambda x: extractor.extract_price(x))
df['beds_res'] = df['remarks'].apply(lambda x: extractor.extract_bedrooms(x))
df['baths_res'] = df['remarks'].apply(lambda x: extractor.extract_bathrooms(x))
df['sqft_res'] = df['remarks'].apply(lambda x: extractor.extract_sqft(x))

categories = ["price", "beds", "baths"]
results = ["price_res", "beds_res", "baths_res"]
final_result = []

for i in range(len(results)):
    extracted = df[df[results[i]].notna()].copy()
    total_correct = sum(extracted[categories[i]] == extracted[results[i]])
    total_predicted = len(extracted)
    precision = total_correct / total_predicted
    
    recall = df[df[categories[i]].notna()].copy()
    total_expected = len(recall)
    correct_recall = sum(recall[categories[i]] == recall[results[i]])
    recall_result = correct_recall / total_expected
    
    if (precision + recall_result) == 0:
        f1 = 0
    else:
        f1 = (2 * precision * recall_result) / (precision + recall_result)
    
    final_result.append({
        "Category": results[i],
        "Precision": precision,
        "Recall": recall_result,
        "F1-Score": f1,
        "Total Expected": total_expected,
        "Total Predicted": total_predicted,
        "Total Correct": total_correct
    })

for cat in final_result:
    print(cat)