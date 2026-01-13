import sys
import os

# Add the current directory to sys.path so we can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import PolicyShock
from logic import calculate_simulation

def run_mechanism_audit():
    print("--- 📉 TIPM v4.0 Market Mechanism & Crashing Point Audit ---")

    # 1. LOW TARIFF: Protectionist Gain (Expected positive for Importer)
    print("\n[CHECK 1] Low Tariff (5%): Estimating Protectionist Gain")
    shock_low = PolicyShock(source_id='USA', target_id='CHN', industry_id='D26', tariff_delta=5.0)
    result_low = calculate_simulation(shock_low)
    usa_low = next(i for i in result_low.impacts if i.country_id == 'USA')
    print(f"USA Net Impact @ 5%: ${usa_low.direct_impact_usd_mn:,.2f}M")
    print(f"USA Wealth Transfer: +${usa_low.domestic_gain_usd_mn:,.2f}M")
    print(f"USA Deadweight Loss: -${usa_low.deadweight_loss_usd_mn:,.2f}M")
    
    # 2. HIGH TARIFF: Systemic Drag (Expected negative for Importer)
    print("\n[CHECK 2] High Tariff (60%): Estimating Systemic Drag")
    shock_high = PolicyShock(source_id='USA', target_id='CHN', industry_id='D26', tariff_delta=60.0)
    result_high = calculate_simulation(shock_high)
    usa_high = next(i for i in result_high.impacts if i.country_id == 'USA')
    print(f"USA Net Impact @ 60%: ${usa_high.direct_impact_usd_mn:,.2f}M")
    print(f"USA Wealth Transfer: +${usa_high.domestic_gain_usd_mn:,.2f}M")
    print(f"USA Deadweight Loss: -${usa_high.deadweight_loss_usd_mn:,.2f}M")

    # 3. CRASHING POINT DISCOVERY
    print("\n[CHECK 3] Crashing Point Discovery")
    print(f"Discovery Result: {result_high.executive_summary}")
    
    # Validation logic
    assert usa_low.direct_impact_usd_mn > -500, "Low tariff should have minimal or positive impact due to wealth transfer."
    assert usa_high.direct_impact_usd_mn < -5000, "High tariff must result in significant net loss due to quadratic deadweight and retaliation."
    assert result_high.sensitivity is not None, "Sensitivity analysis must be populated."
    assert result_high.sensitivity.crashing_point_tariff > 0, "Crashing point must be a positive tariff %."

    print("\n--- ✅ AUDIT COMPLETED: MARKET MECHANISMS VALIDATED ---")

if __name__ == "__main__":
    run_mechanism_audit()
