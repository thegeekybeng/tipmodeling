from pydantic import BaseModel
from typing import Dict, List, Optional

class SectorProfile(BaseModel):
    name: str
    export_volume_usd: float  # Total exports for this sector
    elasticity: float         # How sensitive is this sector to price? (Luxury = High, Food = Low)
    # Who feeds this sector? (e.g., Electronics needs Semiconductors)
    upstream_dependencies: Dict[str, float] = {} # { "SG_Semicon": 0.4 } means 40% of input comes from SG

class CountryProfile(BaseModel):
    name: str
    gdp: float
    # New: Detailed Sector Breakdown
    sectors: Dict[str, SectorProfile] 
    # Keep aggregate trading partners for baseline gravity
    trading_partners: Dict[str, float]

class SimulationResult(BaseModel):
    country_name: str
    direct_impact_usd: float
    second_order_impact_usd: float
    total_gdp_change_pct: float
    # New: Sector-level breakdown
    sector_impacts: Dict[str, float] = {} 
    impact_breakdown: Dict[str, float] = {}
