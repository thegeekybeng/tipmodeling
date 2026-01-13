import sys
import os

# Add the current directory to sys.path so we can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import PolicyShock
from logic import calculate_simulation

def run_visualization_audit():
    print("--- 🎨 TIPM v5.0 Visualization Data Audit ---")

    # Simulate China Electronics @ 10%
    shock = PolicyShock(source_id='USA', target_id='CHN', industry_id='D26', tariff_delta=10.0)
    result = calculate_simulation(shock)
    
    vis = result.visuals
    assert vis is not None, "Error: Visuals data missing."

    # 1. Heatmap Check
    print("\n[CHECK 1] Heatmap Data")
    print(f"Heatmap Entries: {list(vis.heatmap.keys())}")
    assert 'CHN' in vis.heatmap and 'USA' in vis.heatmap, "Heatmap missing core countries."

    # 2. Sunburst Check
    print("\n[CHECK 2] Sunburst Hierarchy")
    print(f"Root: {vis.sunburst.name} (${vis.sunburst.value}M)")
    print(f"Suppliers: {[c.name for c in vis.sunburst.children]}")
    assert len(vis.sunburst.children) >= 2, "Sunburst missing multi-node suppliers (SGP/MYS)."

    # 3. Radar Check
    print("\n[CHECK 3] Strategic Radar Metrics")
    for m in vis.radar:
        print(f" - {m.axis}: {m.value:.1f}")
    assert any(m.axis == "Global Drain" for m in vis.radar), "Radar missing key axes."

    # 4. Timeline Check
    print("\n[CHECK 4] Propagation Timeline")
    for e in vis.timeline:
        print(f" - {e.period}: ${e.global_loss_mn:,.0f}M - {e.description}")
    assert len(vis.timeline) == 3, "Timeline missing propagation phases."

    print("\n--- ✅ AUDIT COMPLETED: VISUALIZATION DATA VALIDATED ---")

if __name__ == "__main__":
    run_visualization_audit()
