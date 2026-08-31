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
        'disability': ['wheelchair'],
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

        return {'compliant': violations == 0, 'num_violations': violations, 'violations_list': violations_list}