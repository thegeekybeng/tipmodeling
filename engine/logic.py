import os
import sqlite3
import yaml
from models import PolicyShock, SimulationResult, SimulationImpact, EconomicRole, EconomyProfile, IndustryProfile, SensitivityAnalysis, SensitivityPoint, SunburstNode, RadarMetrics, TimelineEvent, AdvancedVisuals, SectoralImpact
from typing import Dict, List, Any

# --- CONFIGURATION LOADING ---
def load_config() -> Dict[str, Any]:
    config_path = os.getenv("CONFIG_PATH", "config/config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}

CONFIG = load_config()

# --- DATABASE CONNECTION ---
def get_db_connection():
    # Use the local SQLite file as requested
    db_path = CONFIG.get("caching", {}).get("db_path", "data/phishing.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_economies() -> List[EconomyProfile]:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, gdp_usd_bn FROM economies ORDER BY name ASC")
        rows = cur.fetchall()
        return [EconomyProfile(id=row['id'], name=row['name'], gdp_usd_bn=row['gdp_usd_bn']) for row in rows]
    finally:
        cur.close()
        conn.close()

def get_industries() -> List[IndustryProfile]:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, category FROM industries ORDER BY name ASC")
        rows = cur.fetchall()
        return [IndustryProfile(id=row['id'], name=row['name'], category=row['category']) for row in rows]
    finally:
        cur.close()
        conn.close()

def get_available_industries(source_id: str, target_id: str) -> List[IndustryProfile]:
    """Returns industries that actually have trade volume between source and target."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT DISTINCT i.id, i.name, i.category
            FROM industries i
            JOIN trade_matrix tm ON i.id = tm.industry_id
            WHERE tm.source_econ_id = ? AND tm.target_econ_id = ?
            AND tm.value_added_usd_mn > 0
            ORDER BY i.name ASC
        """, (target_id, source_id)) # Note: target_id is the exporter, source_id is the importer in trade_matrix terms
        rows = cur.fetchall()
        return [IndustryProfile(id=row['id'], name=row['name'], category=row['category']) for row in rows]
    finally:
        cur.close()
        conn.close()

# --- CONFIGURATION & GOVERNANCE ---
REPRODUCIBILITY_SEED = 42
SENSITIVITY_FACTOR = 0.4      # Bullwhip Effect Multiplier (Reduced from 1.5 to 0.4)
IMPORT_BLOWBACK_BASE = 0.05   # Base 5% inflationary blowback (Reduced from 10%)
WEALTH_TRANSFER_RATE = 0.45   # 45% of tariff value transferred to local producers (Increased from 25%)
EFFICIENCY_GAP_COEFF = 0.002  # Quadratic drag coefficient for deadweight loss

def discover_crashing_point(shock: PolicyShock) -> SensitivityAnalysis:
    """Finds the tariff threshold where net benefit for the importer turns negative."""
    points = []
    crashing_point = 100.0
    found_crash = False

    # Simulate from 0% to 100% in 1% increments for higher precision
    for t in range(0, 101, 1):
        temp_shock = shock.copy(update={"tariff_delta": float(t)})
        # We run a partial simulation to check the Importer's balance
        res = calculate_simulation(temp_shock, include_sensitivity=False)
        
        # Find the importer impact
        importer_impact = next((i for i in res.impacts if i.role == EconomicRole.IMPORTING), None)
        total_loss = res.global_gdp_loss_usd_mn
        
        is_crash = False
        if importer_impact and importer_impact.direct_impact_usd_mn < 0 and not found_crash and t > 0:
            crashing_point = float(t)
            found_crash = True
            is_crash = True
            
        points.append(SensitivityPoint(
            tariff_pct=float(t),
            global_loss_mn=abs(total_loss),
            is_crashing_point=is_crash
        ))
        
    return SensitivityAnalysis(
        shock_context=shock,
        crashing_point_tariff=crashing_point,
        data_points=points
    )

def calculate_simulation(shock: PolicyShock, include_sensitivity: bool = True) -> SimulationResult:
    # --- 0. GOVERNANCE CHECK: ZERO TARIFF ---
    if shock.tariff_delta == 0:
        return SimulationResult(
            shock=shock,
            impacts=[],
            global_gdp_loss_usd_mn=0.0,
            executive_summary="Policy Neutral: No tariff adjustment detected. Global economic drain is $0.00."
        )

    conn = get_db_connection()
    cur = conn.cursor()
    
    impacts = []
    global_loss_mn = 0.0
    
    try:
        # --- 1. BASELINE DATA (Exporter -> Importer) ---
        cur.execute("""
            SELECT e.id, e.name, e.gdp_usd_bn, tm.value_added_usd_mn, tm.baseline_tariff_pct, i.category
            FROM economies e
            JOIN trade_matrix tm ON tm.source_econ_id = e.id
            JOIN industries i ON i.id = tm.industry_id
            WHERE tm.source_econ_id = ? AND tm.target_econ_id = ? AND tm.industry_id = ?
        """, (shock.target_id, shock.source_id, shock.industry_id))
        
        target_data = cur.fetchone()
        if not target_data:
            return SimulationResult(
                shock=shock, impacts=[], global_gdp_loss_usd_mn=0.0,
                executive_summary="Data Null: No trade volume found."
            )

        sector_export_vol_mn = float(target_data['value_added_usd_mn'])
        baseline_tariff = float(target_data['baseline_tariff_pct'])
        
        # Shock impact is based on delta from baseline
        # Total Applied Tariff = Baseline + Delta
        tariff_factor = (baseline_tariff + shock.tariff_delta) / 100.0
        industry_category = target_data['category'] or "Manufacturing"
        
        # --- 1.1 REACTIVE PARAMETERS ---
        # Adjust coefficients based on industry sector
        wealth_transfer = WEALTH_TRANSFER_RATE
        blowback_base = IMPORT_BLOWBACK_BASE
        drag_coeff = EFFICIENCY_GAP_COEFF
        
        if industry_category == "Primary":
            wealth_transfer = 0.45  # Balanced domestic scale-up for primary goods
            blowback_base = 0.06     # Moderate base inflationary impact
            drag_coeff = 0.003       # Moderate scale-up drag
        elif industry_category == "Services":
            wealth_transfer = 0.40  # Services are easier to relocate/substitute
            blowback_base = 0.05     # Lower immediate inflation
            drag_coeff = 0.001       # Efficient relocation
        
        # --- 2. IMPACT: EXPORTER (Revenue Contraction) ---
        direct_loss_exporter = sector_export_vol_mn * tariff_factor
        target_gdp_mn = float(target_data['gdp_usd_bn']) * 1000.0
        
        impacts.append(SimulationImpact(
            country_id=shock.target_id,
            country_name=target_data['name'],
            role=EconomicRole.EXPORTING_GOODS,
            direct_impact_usd_mn=-direct_loss_exporter,
            total_gdp_impact_pct=-(direct_loss_exporter / target_gdp_mn) * 100.0,
            impact_narrative=f"Sectoral revenue contraction in {shock.industry_id}.",
            impact_reasons=[
                f"Revenue loss from ${sector_export_vol_mn:,.0f}M targeted exports",
                f"Applied Tariff: {baseline_tariff + shock.tariff_delta}% (Baseline: {baseline_tariff}%)"
            ],
            trend="DOWN",
            sectoral_impacts=[
                SectoralImpact(
                    industry_id=shock.industry_id,
                    industry_name=next((i.name for i in get_industries() if i.id == shock.industry_id), shock.industry_id),
                    impact_usd_mn=-direct_loss_exporter,
                    impact_pct=-(direct_loss_exporter / target_gdp_mn) * 100.0
                )
            ],
            baseline_tariff_pct=baseline_tariff
        ))
        global_loss_mn += direct_loss_exporter

        # --- 3. UPSTREAM CONTAGION (Bullwhip) ---
        cur.execute("""
            SELECT e.id, e.name, e.gdp_usd_bn, tm.value_added_usd_mn
            FROM trade_matrix tm JOIN economies e ON tm.source_econ_id = e.id
            WHERE tm.target_econ_id = ? AND tm.industry_id = ?
        """, (shock.target_id, shock.industry_id))
        
        for supplier in cur.fetchall():
            if supplier['id'] == shock.target_id: continue
            supplier_va_mn = float(supplier['value_added_usd_mn'])
            upstream_loss = (direct_loss_exporter * (supplier_va_mn / sector_export_vol_mn)) * SENSITIVITY_FACTOR
            impacts.append(SimulationImpact(
                country_id=supplier['id'], country_name=supplier['name'],
                role=EconomicRole.EXPORTING_RESOURCE,
                direct_impact_usd_mn=-upstream_loss,
                total_gdp_impact_pct=-(upstream_loss / (float(supplier['gdp_usd_bn']) * 1000.0)) * 100.0,
                impact_narrative="Upstream volatility contagion.",
                impact_reasons=[f"Bullwhip shock on intermediate demand (x{SENSITIVITY_FACTOR})"],
                trend="DOWN",
                sectoral_impacts=[
                    SectoralImpact(
                        industry_id=shock.industry_id,
                        industry_name=next((i.name for i in get_industries() if i.id == shock.industry_id), shock.industry_id),
                        impact_usd_mn=-upstream_loss,
                        impact_pct=-(upstream_loss / (float(supplier['gdp_usd_bn']) * 1000.0)) * 100.0
                    )
                ]
            ))
            global_loss_mn += upstream_loss

        # --- 4. THE MARKET MECHANISM: IMPORTER BALANCING ---
        cur.execute("SELECT name, gdp_usd_bn FROM economies WHERE id = ?", (shock.source_id,))
        source_data = cur.fetchone()
        if source_data:
            # A: Wealth Transfer (Gains for local producers)
            # Efficiency Gap: gains decrease as tariff increases (quadratic drag)
            efficiency_gap_factor = max(0, 1 - (shock.tariff_delta * drag_coeff))
            domestic_gain = (direct_loss_exporter * wealth_transfer) * efficiency_gap_factor
            
            # B: Deadweight Loss (Value destroyed - Quadratic)
            deadweight_loss = (direct_loss_exporter * (tariff_factor / 2))
            
            # C: Inflationary Blowback
            cost_spike = direct_loss_exporter * (blowback_base + (tariff_factor * 0.1))
            
            # D: Retaliation Hit (Feedback Loop)
            # Retaliation scales with the size of the target economy relative to global baseline
            retaliation_multiplier = min(1.0, float(target_data['gdp_usd_bn']) / 5000.0) # Cap at 1.0 (5T GDP)
            retaliation_damage = direct_loss_exporter * 0.20 * retaliation_multiplier
            
            # Net Result for Importer
            net_importer_impact = domestic_gain - (deadweight_loss + cost_spike + retaliation_damage)
            source_gdp_mn = float(source_data['gdp_usd_bn']) * 1000.0
            
            impacts.append(SimulationImpact(
                country_id=shock.source_id, country_name=source_data['name'],
                role=EconomicRole.IMPORTING,
                direct_impact_usd_mn=net_importer_impact,
                total_gdp_impact_pct=(net_importer_impact / source_gdp_mn) * 100.0,
                domestic_gain_usd_mn=domestic_gain,
                deadweight_loss_usd_mn=deadweight_loss,
                impact_narrative="Net fiscal result of internal mechanisms.",
                impact_reasons=[
                    f"Wealth Transfer: +${domestic_gain:,.0f}M to local {shock.industry_id} producers",
                    f"Efficiency Gap/Deadweight: -${deadweight_loss:,.0f}M destroyed",
                    f"Inflation Blowback: -${cost_spike:,.0f}M consumer drag",
                    f"Retaliation: -${retaliation_damage:,.0f}M loss in unrelated sectors"
                ],
                trend="UP" if net_importer_impact > 0 else "DOWN"
            ))

        # --- 5. SYNCHRONIZE GLOBAL OUTPUT ---
        # Global Drain is the sum of ALL negative direct impacts (wealth destruction)
        # Note: We only count the losses to avoid double counting transfers.
        # However, to match user request "sum of all direct/second-order losses reported",
        # we sum the direct_impact_usd_mn of all entities that suffered a loss.
        global_loss_mn = sum(abs(i.direct_impact_usd_mn) for i in impacts if i.direct_impact_usd_mn < 0)

    except Exception as e:
        print(f"SIMULATION_ERROR: {str(e)}"); raise e
    finally:
        cur.close(); conn.close()

    sensitivity = discover_crashing_point(shock) if include_sensitivity else None
    
    # --- 5. ADVANCED VISUALS (Roadmap v5.0) ---
    heatmap = {imp.country_id: abs(imp.total_gdp_impact_pct) for imp in impacts}
    
    # Sunburst: Root is Target -> Children are Upstream
    target_imp = next((i for i in impacts if i.role == EconomicRole.EXPORTING_GOODS), None)
    sunburst = SunburstNode(
        name=target_imp.country_name if target_imp else shock.target_id,
        value=abs(target_imp.direct_impact_usd_mn) if target_imp else 0.0,
        role=EconomicRole.EXPORTING_GOODS,
        children=[
            SunburstNode(name=i.country_name, value=abs(i.direct_impact_usd_mn), role=i.role)
            for i in impacts if i.role == EconomicRole.EXPORTING_RESOURCE
        ]
    )
    
    # Radar: Normalized scores (0-100)
    radar = [
        RadarMetrics(axis="Global Drain", value=min(100, (global_loss_mn / 50000) * 100)),
        RadarMetrics(axis="Inflation Severity", value=min(100, tariff_factor * 100)),
        RadarMetrics(axis="Retaliation Risk", value=50.0 if shock.tariff_delta > 10 else 10.0),
        RadarMetrics(axis="Supply Chain Volatility", value=SENSITIVITY_FACTOR * 40), # 1.5x -> 60
        RadarMetrics(axis="Protectionist Gain", value=min(100, (next((i.domestic_gain_usd_mn for i in impacts if i.role == EconomicRole.IMPORTING), 0) / 5000) * 100))
    ]
    
    # Timeline: Shock Propagation
    timeline = [
        TimelineEvent(period="Day 0", global_loss_mn=global_loss_mn * 0.4, description="Immediate revenue contraction & export cessation."),
        TimelineEvent(period="Month 3", global_loss_mn=global_loss_mn * 0.8, description="Upstream demand pullback & supply chain volatility peaks."),
        TimelineEvent(period="Year 1+", global_loss_mn=global_loss_mn, description="Full inflationary blowback & systemic efficiency gap realized.")
    ]

    summary = (
        f"A {shock.tariff_delta}% tariff on {shock.industry_id} triggers a ${global_loss_mn:,.0f}M global drain. "
        f"Importer ({shock.source_id}) {'already exceeded' if shock.tariff_delta > sensitivity.crashing_point_tariff else 'reaches'} a 'Crashing Point' at {sensitivity.crashing_point_tariff}% tariff "
        f"where accumulation of deadweight loss and retaliation overrides local production gains."
    ) if sensitivity else "Simulation result generated."

    return SimulationResult(
        shock=shock, impacts=impacts,
        global_gdp_loss_usd_mn=-global_loss_mn,
        executive_summary=summary,
        sensitivity=sensitivity,
        visuals=AdvancedVisuals(
            heatmap=heatmap,
            sunburst=sunburst,
            radar=radar,
            timeline=timeline
        )
    )
