import re
import json
import pandas as pd
from .entity_extractor import EntityExtractor
from .taxonomy_builder import taxonomy_data

class SignalExtractor:

    def __init__(self, taxonomy, entity_extractor):
        self.taxonomy = taxonomy
        self.extractor = entity_extractor

        self.amenity_terms = self._flatten_taxonomy_terms(taxonomy)

        self.condition_patterns = {
            'move-in ready': [r'move\s*-?in\s+ready', r'turn\s*-?key', r'ready\s+to\s+move\s+in'],
            'new construction': [r'new\s+construction', r'brand\s+new', r'newly\s+built'],
            'renovated': [r'fully\s+renovated', r'recently\s+renovated', r'remodeled', r'updated'],
            'fixer': [r'fixer', r'fixer\s*upper', r'tlc\s+needed', r'handyman\s+special'],
            'as-is': [r'as\s*-?is'],
            'original condition': [r'original\s+condition'],
            'well maintained': [r'well\s+maintained', r'pride\s+of\s+ownership', r'immaculate']
        }

        self.financing_patterns = {
            'cash': [r'cash\s+only', r'cash\s+buyer'],
            'conventional': [r'conventional\s+loan', r'conv\s+loan', r'conventional\s+financing'],
            'fha': [r'\bfha\b', r'fha\s+financing'],
            'va': [r'\bva\b', r'va\s+loan', r'va\s+financing'],
            'usda': [r'\busda\b'],
            'seller financing': [r'seller\s+financing', r'owner\s+financing', r'owner\s+carry'],
            'assumable': [r'assumable\s+(?:loan|mortgage)'],
            '1031 exchange': [r'1031\s+exchange'],
            'lease option': [r'lease\s+option', r'rent\s+to\s+own']
        }

        self.location_patterns = {
            'near schools': [r'near\s+schools?', r'close\s+to\s+schools?'],
            'walking distance': [r'walking\s+distance\s+to', r'walk\s+to'],
            'close to shopping': [r'close\s+to\s+shopping', r'near\s+shopping', r'shopping\s+and\s+dining'],
            'close to freeway': [r'easy\s+access\s+to\s+freeway', r'freeway\s+access', r'highway\s+access'],
            'quiet neighborhood': [r'quiet\s+neighborhood'],
            'cul-de-sac': [r'cul\s*-?de\s*-?sac'],
            'corner lot': [r'corner\s+lot'],
            'waterfront': [r'waterfront', r'lakefront', r'river\s+access'],
            'views': [r'ocean\s+view', r'mountain\s+view', r'city\s+view', r'panoramic\s+views?', r'scenic\s+views?'],
            'downtown': [r'near\s+downtown', r'close\s+to\s+downtown', r'\bdowntown\b']
        }

    def extract_signals(self, listing_record):
        remarks = self._normalize_text(
            listing_record.get('L_Remarks', listing_record.get('remarks', ''))
        )

        return {
            'listing_id': listing_record.get('L_ListingID', listing_record.get('listing_id')),
            'bedrooms': self.extractor.extract_bedrooms(remarks),
            'bathrooms': self.extractor.extract_bathrooms(remarks),
            'price': self.extractor.extract_price(remarks),
            'sqft': self.extractor.extract_sqft(remarks),
            'amenities': self._match_amenities(remarks),
            'condition': self._extract_category(remarks, self.condition_patterns),
            'financing': self._extract_category(remarks, self.financing_patterns),
            'location': self._extract_category(remarks, self.location_patterns)
        }

    def _normalize_text(self, text):
        return ' '.join(str(text).split()) if text else ''

    def _flatten_taxonomy_terms(self, taxonomy):
        if not taxonomy:
            return []

        terms = []
        if isinstance(taxonomy, dict) and 'terms' in taxonomy:
            for item in taxonomy.get('terms', []):
                term = item.get('term') if isinstance(item, dict) else None
                if term:
                    terms.append(term)
        elif isinstance(taxonomy, dict):
            for value in taxonomy.values():
                if isinstance(value, list):
                    terms.extend(value)

        terms = list(set([str(term).strip().lower() for term in terms]))
        terms.sort(key=len, reverse=True)
        return terms

    def _match_amenities(self, remarks):
        text = remarks.lower()
        found = []
        for term in self.amenity_terms:
            pattern = rf'(?<!\w){re.escape(term)}(?!\w)'
            if re.search(pattern, text, flags=re.I):
                found.append(term)
        return sorted(set(found))

    def _extract_category(self, text, pattern_map):
        hits = []
        for canonical, patterns in pattern_map.items():
            for pattern in patterns:
                if re.search(pattern, text, flags=re.I):
                    hits.append(canonical)
                    break
        return sorted(set(hits))

def fetch_from_local_csv(csv_path='../data/processed/listing_sample.csv'):
    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        remarks = row.get('remarks')
        if isinstance(remarks, str) and remarks.strip():
            yield {
                'L_ListingID': row.get('L_ListingID'),
                'L_Remarks': remarks
            }


extractor = EntityExtractor()
signal_extractor = SignalExtractor(taxonomy_data, extractor)

count = 0

with open('../data/processed/signal_extraction_full.json', 'w', encoding='utf-8') as f:
    f.write('[\n')
    first = True

    data_source = '../data/processed/listing_sample.csv'
    records = fetch_from_local_csv()

    for record in records:
        result = signal_extractor.extract_signals(record)
        if not first:
            f.write(',\n')
        f.write(json.dumps(result, ensure_ascii=False))
        first = False
        count += 1

    f.write('\n]\n')

    print("Processing complete")