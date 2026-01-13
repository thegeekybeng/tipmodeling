import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import PolicyShock
from logic import calculate_simulation

def test_agri_tariff():
    print("--- 📉 Agriculture Crashing Point Test (D01T03) ---")
    # USA imposes tariff on IDN (target for D01T03 in seed_db)
    shock = PolicyShock(source_id='USA', target_id='IDN', industry_id='D01T03', tariff_delta=13.0)
    result = calculate_simulation(shock)
    
    print(f"Crashing Point Detected: {result.sensitivity.crashing_point_tariff}%")
    
    # Check importer impact at 1, 2, 3, 4, 5%
    for t in range(1, 6):
        s = PolicyShock(source_id='USA', target_id='IDN', industry_id='D01T03', tariff_delta=float(t))
        res = calculate_simulation(s, include_sensitivity=False)
        usa = next(i for i in res.impacts if i.country_id == 'USA')
        print(f"USA Net Impact @ {t}%: ${usa.direct_impact_usd_mn:,.2f}M")

if __name__ == "__main__":
    test_agri_tariff()
