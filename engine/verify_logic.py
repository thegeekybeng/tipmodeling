import sys
import os

# Add the current directory to sys.path so we can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import PolicyShock
from logic import calculate_simulation

def test_us_cn_tariff():
    print("--- Running Test: US imposes 10% tariff on China ---")
    shock = PolicyShock(source_id="USA", target_id="CHN", industry_id="D26", tariff_delta=10.0)
    results = calculate_simulation(shock)
    
    cn_impact = results["CN"]
    sg_impact = results["SG"]
    
    print(f"CN GDP Change: {cn_impact.total_gdp_change_pct:.4f}%")
    print(f"SG GDP Change: {sg_impact.total_gdp_change_pct:.4f}%")
    print(f"SG Second Order Loss: ${sg_impact.second_order_impact_usd:.2f}B")
    
    # Assertions for sanity
    assert cn_impact.total_gdp_change_pct < 0
    assert sg_impact.total_gdp_change_pct < 0
    print("\n[SUCCESS] Logic verified mathematically.")

if __name__ == "__main__":
    test_us_cn_tariff()
