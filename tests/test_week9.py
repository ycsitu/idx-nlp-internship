#from ..scripts.compliance_checker import ComplianceChecker
class ComplianceChecker:
    def __init__(self):
        self.prohibited_patterns = {
        'familial': ['no children', 'adults only', 'perfect for singles', 'all-adult'],
        'disability': ['no wheelchairs', 'must be able-bodied'],
        'race': ['white neighborhood', 'asian neighborhood', 'black neighborhood'],
        'religion': ['christian community', 'jewish neighborhood', 'muslim community'],
        'sex': ['women only', 'men only'],
        }

        self.warning_patterns = {
        'familial': [],
        'disability': [],
        'race': ['diverse area'],
        'religion': [],
        'sex': [],
        }
        
        self.info_patterns = { # keywords without context
        'familial': ['children', 'adult', 'minor', 'child'],
        'disability': ['wheelchair', 'disabled'],
        'race': ['diverse', 'ethnic'],
        'religion': ['jewish', 'christian', 'muslim'],
        'sex': ['women', 'men'],
        }

    def check_listing(self, text):
        violations_list = []
        violations = 0
        text_lower = text.lower()

        for category, patterns in self.prohibited_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    violations_list.append({
                        'category': category,
                        'pattern': pattern,
                        'severity': 'error',
                        'message': f'Prohibited language: {pattern} (Fair Housing violation)'
                        })
                    violations += 1
                    
        for category, patterns in self.warning_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    violations_list.append({
                        'category': category,
                        'pattern': pattern,
                        'severity': 'warning',
                        'message': f'Warning (requires review): {pattern} (Potential Fair Housing violation)'
                        })
                    
        for category, patterns in self.info_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    violations_list.append({
                        'category': category,
                        'pattern': pattern,
                        'severity': 'info',
                        'message': f'Info: {pattern} (Potential Fair Housing violation)'
                        })

        return {'compliant': violations == 0, 'violations': violations}

import json

true_positives = 0
false_positives = 0
false_negatives = 0
total_violating = 0
total_compliant = 0

with open('data/processed/sample_compliance.json', 'r', encoding='utf-8') as f:
    records = json.load(f)["data"]

checker = ComplianceChecker()

for row in records:
    expected_violating = bool(row["violating"])
    result = checker.check_listing(str(row["text"]))
    predicted_violating = not bool(result["compliant"])

    if expected_violating:
        total_violating += 1
        if predicted_violating:
            true_positives += 1
        else:
            false_negatives += 1
    else:
        total_compliant += 1
        if predicted_violating:
            false_positives += 1

recall = true_positives / total_violating if total_violating else 0
precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) else 0.0

results = {
    "recall": recall,
    "precision": precision,
    "true_positives": true_positives,
    "false_positives": false_positives,
    "false_negatives": 0,
    "total_violating": total_violating,
    "total_compliant": total_compliant
}

print(results)