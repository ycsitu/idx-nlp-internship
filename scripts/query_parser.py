import re
import json
import pandas as pd

class QueryParser:
    def parse(self, query):
        filters = {}

        # Price patterns
        if match := re.search(r'under\s+\$?(\d+)([km]?)', query, re.I):
            filters['price_max'] = int(match.group(1))*1000 #assume K, bad fix

        # Bedroom patterns
        if match := re.search(r'(\d+)\+?\s*(?:bed|br)', query, re.I):
            filters['bedrooms_min' if '+' in match.group(0) else 'bedrooms'] = int(match.group(1))

        # Bathroom patterns
        if match := re.search(r'(\d+)\+?\s*(?:bath|ba)', query, re.I):
            filters['bathrooms_min' if '+' in match.group(0) else 'bathrooms'] = int(match.group(1))

        # TODO: city patterns
        '''if match := re.search(r'in\s', query, re.I):
            filters['city'] = match.group(1)'''

        return filters

    def to_sql(self, filters):
        conditions = []
        params = []

        if 'price' in filters:
            conditions.append('L_SystemPrice >= %s')
            params.append(filters['price'])
        if 'price_max' in filters:
            conditions.append('L_SystemPrice <= %s')
            params.append(filters['price_max'])
        if 'price_min' in filters:
            conditions.append('L_SystemPrice >= %s')
            params.append(filters['price_min'])

        if 'bedrooms' in filters:
            conditions.append('L_Keyword2 = %s')
            params.append(filters['bedrooms'])
        if 'bedrooms_min' in filters:
            conditions.append('L_Keyword2 >= %s')
            params.append(filters['bedrooms_min'])
        if 'bedrooms_max' in filters:
            conditions.append('L_Keyword2 <= %s')
            params.append(filters['bedrooms_max'])

        if 'bathrooms' in filters:
            conditions.append('L_Keyword2 = %s')
            params.append(filters['bathrooms'])
        if 'bathrooms_min' in filters:
            conditions.append('L_Keyword3 >= %s')
            params.append(filters['bathrooms_min'])
        if 'bathrooms_max' in filters:
            conditions.append('L_Keyword3 >= %s')
            params.append(filters['bathrooms_max'])

        if 'city' in filters:
            conditions.append('L_City = %s')
            params.append(filters['city'])

        #TODO: add amenity filters

        if len(conditions) == 0:
            return "SELECT * FROM rets_property", params

        where_clause = ' AND '.join(conditions)
        return f"SELECT * FROM rets_property WHERE {where_clause}", params
    
class SchemaValidator:
    def __init__(self, schema_path='../data/processed/schema.json'):
        with open(schema_path) as f:
            self.schema = json.load(f)
        self.valid_cities = self.schema.get('valid_cities', []) 

    def validate_query(self, filters):
        errors = []

        # Check city exists in database
        if 'city' in filters:
            if filters['city'] not in self.valid_cities:
                errors.append(f"City '{filters['city']}' not found in database")

        # Check price range
        for key in ['price_max', 'price_min', 'price']:
            if key in filters:
                if filters[key] < 100000 or filters[key] > 10000000:
                    errors.append(f"Price {filters[key]} outside typical range")

        # Check bedroom count
        for key in ['bedrooms_max', 'bedrooms_min', 'bedrooms']:
            if key in filters:
                if filters[key] < 1 or filters[key] > 10:
                    errors.append(f"Price {filters[key]} outside typical range")

        # Check bathroom count
        for key in ['bathrooms_max', 'bathrooms_min', 'bathrooms']:
            if key in filters:
                if filters[key] < 1 or filters[key] > 10:
                    errors.append(f"Price {filters[key]} outside typical range")

        return len(errors) == 0, errors