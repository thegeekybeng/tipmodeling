import sys
import os

# Add the current directory to sys.path so we can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import PolicyShock
from logic import calculate_simulation

def run_remediation_audit():
    print("--- 🚀 TIPM v3.0 Logic Remediation Audit ---")

    # 1. GOVERNANCE CHECK: Zero Tariff = Zero Drain
    print("\n[CHECK 1] Governance: Tariff Delta = 0%")
    shock_zero = PolicyShock(source_id='USA', target_id='CHN', industry_id='D26', tariff_delta=0.0)
    result_zero = calculate_simulation(shock_zero)
    print(f"Global Loss: ${result_zero.global_gdp_loss_usd_mn:.2f}M")
    print(f"Summary: {result_zero.executive_summary}")
    assert result_zero.global_gdp_loss_usd_mn == 0, "Governance Fail: Tariff 0% must result in $0 drain."

    # 2. AXIOM 1: Trade-Driven Impact (USA taxes China Electronics)
    print("\n[CHECK 2] Axiom 1: Trade-Driven Impact (CHN D26 -> USA)")
    shock_axiom = PolicyShock(source_id='USA', target_id='CHN', industry_id='D26', tariff_delta=10.0)
    result_axiom = calculate_simulation(shock_axiom)
    
    # In seed_db.sql: CHN -> USA, D26 is 80,000M. 10% tariff = 8,000M direct loss.
    # Plus Bullwhip for SGP (5000/80000 * 8000 * 1.5) = 750M.
    # Plus Blowback for USA (8000 * 0.15) = 1200M.
    # Total Global Loss = 8000 (CHN) + 750 (SGP) + 1800 (MYS) + 1200 (USA) = 11750M.
    
    print(f"Global Loss: ${-result_axiom.global_gdp_loss_usd_mn:.2f}M")
    print(f"Target (CHN) Impact: ${result_axiom.impacts[0].direct_impact_usd_mn:.2f}M")
    print(f"Summary: {result_axiom.executive_summary}")
    
    assert "Bullwhip Effect Multiplier (x1.5)" in result_axiom.executive_summary, "Narrative Fail: Missing characterization."
    assert abs(result_axiom.impacts[0].direct_impact_usd_mn) == 8000.0, "Axiom 1 Fail: Direct loss mismatch."
    assert any(i.country_id == 'SGP' for i in result_axiom.impacts), "Causality Fail: Missing SG upstream link."
    assert any(i.country_id == 'MYS' for i in result_axiom.impacts), "Causality Fail: Missing MY upstream link (Multi-Node Summation)."
    assert abs(result_axiom.global_gdp_loss_usd_mn) == 11750.0, f"Summation Fail: Expected 11750M, got {-result_axiom.global_gdp_loss_usd_mn}M."

    print("\n--- ✅ AUDIT COMPLETED: MULTI-NODE LOGIC RECTIFIED ---")

if __name__ == "__main__":
    run_remediation_audit()
