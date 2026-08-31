import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.entity_extractor import EntityExtractor
import pandas as pd
import json

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