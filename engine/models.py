from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum

class EconomicRole(str, Enum):
    IMPORTING = "IMPORTING"               # Final consumer / Tariff source
    EXPORTING_GOODS = "EXPORTING_GOODS"   # Direct target of tariff
    EXPORTING_RESOURCE = "EXPORTING_RESOURCE" # Upstream supplier

class PolicyShock(BaseModel):
    source_id: str  # Importing Country ID (e.g., USA)
    target_id: str  # Exporting Goods Country ID (e.g., CHN)
    industry_id: str # Targeted Industry ID (e.g., D26)
    tariff_delta: float # Percentage (e.g., 25 for 25%)

class IndustryProfile(BaseModel):
    id: str
    name: str
    category: Optional[str] = None

class EconomyProfile(BaseModel):
    id: str
    name: str
    gdp_usd_bn: float

class SectoralImpact(BaseModel):
    industry_id: str
    industry_name: str
    impact_usd_mn: float
    impact_pct: float

class SimulationImpact(BaseModel):
    country_id: str
    country_name: str
    role: EconomicRole
    direct_impact_usd_mn: float
    total_gdp_impact_pct: float
    domestic_gain_usd_mn: float = 0.0 # Wealth transfer to local producers
    deadweight_loss_usd_mn: float = 0.0 # Value destroyed
    impact_narrative: str
    impact_reasons: List[str]  # Detailed qualitative reasons
    trend: str # "DOWN", "STABLE", or "UP"
    sectoral_impacts: List[SectoralImpact] = [] # Breakdown of impacts by sector

class SensitivityPoint(BaseModel):
    tariff_pct: float
    global_loss_mn: float
    is_crashing_point: bool = False

class SensitivityAnalysis(BaseModel):
    shock_context: PolicyShock
    crashing_point_tariff: float
    data_points: List[SensitivityPoint]

class SunburstNode(BaseModel):
    name: str
    value: float # USD Millions
    role: EconomicRole
    children: Optional[List['SunburstNode']] = None

class RadarMetrics(BaseModel):
    axis: str
    value: float # 0-100 score

class TimelineEvent(BaseModel):
    period: str # e.g., "Day 0", "Month 3"
    global_loss_mn: float
    description: str

class AdvancedVisuals(BaseModel):
    heatmap: Dict[str, float] # country_id -> impact_pct (for Choropleth)
    sunburst: SunburstNode
    radar: List[RadarMetrics]
    timeline: List[TimelineEvent]

class SimulationResult(BaseModel):
    shock: PolicyShock
    impacts: List[SimulationImpact]
    global_gdp_loss_usd_mn: float
    executive_summary: str
    sensitivity: Optional[SensitivityAnalysis] = None
    visuals: Optional[AdvancedVisuals] = None
    baseline_tariff_pct: float = 0.0 # Anchor for the specific shock pair

# Rebuild models for recursive SunburstNode
SunburstNode.model_rebuild()
