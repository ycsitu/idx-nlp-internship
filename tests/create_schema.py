# for week 4, query parser

import json
import pandas as pd

data_path = 'data/processed/listing_sample.csv'
schema_path = 'data/processed/schema.json'
df = pd.read_csv(data_path)

schema_data = {
        "price": { "min": 100000, "max": 10000000 },
        "bedrooms": { "min": 1, "max": 10 },
        "bathrooms": { "min": 1, "max": 10 },
        "valid_cities": df['L_City'].unique().tolist()
    }

with open(schema_path, 'w', encoding='utf-8') as f:
    json.dump(schema_data, f, indent=4)