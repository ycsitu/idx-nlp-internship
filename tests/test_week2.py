import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.text_cleaning import TextCleaner
import pandas as pd

def test_price_normalization():
    cleaner = TextCleaner()
    assert '450000' in cleaner.normalize_prices('priced at 450k')
    assert '1200000' in cleaner.normalize_prices('$1.2m home')
    
def test_profiling():
    cleaner = TextCleaner()
    df = pd.read_csv('data/processed/listing_sample.csv', encoding="unicode_escape")
    profile = cleaner.profile_column(df, 'remarks')
    assert 'null_rate' in profile
    assert 'avg_length' in profile 

test_price_normalization()
test_profiling()
print("done")