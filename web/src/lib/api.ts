export enum EconomicRole {
  IMPORTING = "IMPORTING",
  EXPORTING_GOODS = "EXPORTING_GOODS",
  EXPORTING_RESOURCE = "EXPORTING_RESOURCE",
}

export interface IndustryProfile {
  id: string;
  name: string;
  category?: string;
}

export interface EconomyProfile {
  id: string;
  name: string;
  gdp_usd_bn: number;
}

export interface SectoralImpact {
  industry_id: string;
  industry_name: string;
  impact_usd_mn: number;
  impact_pct: number;
}

export interface PolicyShock {
  source_id: string;
  target_id: string;
  industry_id: string;
  tariff_delta: number;
}

export interface SunburstNode {
  name: string;
  value: number;
  role: EconomicRole;
  children?: SunburstNode[];
}

export interface RadarMetrics {
  axis: string;
  value: number;
}

export interface TimelineEvent {
  period: string;
  global_loss_mn: number;
  description: string;
}

export interface AdvancedVisuals {
  heatmap: Record<string, number>;
  sunburst: SunburstNode;
  radar: RadarMetrics[];
  timeline: TimelineEvent[];
}

export interface SensitivityPoint {
  tariff_pct: number;
  global_loss_mn: number;
  is_crashing_point: boolean;
}

export interface SensitivityAnalysis {
  shock_context: PolicyShock;
  crashing_point_tariff: number;
  data_points: SensitivityPoint[];
}

export interface SimulationImpact {
  country_id: string;
  country_name: string;
  role: EconomicRole;
  direct_impact_usd_mn: number;
  total_gdp_impact_pct: number;
  domestic_gain_usd_mn?: number;
  deadweight_loss_usd_mn?: number;
  impact_narrative: string;
  impact_reasons: string[];
  trend: "DOWN" | "STABLE" | "UP";
  sectoral_impacts: SectoralImpact[];
  baseline_tariff_pct: number;
}

export interface SimulationResult {
  shock: PolicyShock;
  impacts: SimulationImpact[];
  global_gdp_loss_usd_mn: number;
  executive_summary: string;
  baseline_tariff_pct: number;
  sensitivity?: SensitivityAnalysis;
  visuals?: AdvancedVisuals;
}

export async function fetchEconomies(): Promise<EconomyProfile[]> {
  const response = await fetch("/api/economies", { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch economies");
  return response.json();
}

export async function fetchIndustries(): Promise<IndustryProfile[]> {
  const response = await fetch("/api/industries", { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch industries");
  return response.json();
}

export async function fetchAvailableIndustries(
  source_id: string,
  target_id: string
): Promise<IndustryProfile[]> {
  const response = await fetch(
    `/api/industries/available?source_id=${source_id}&target_id=${target_id}`,
    { cache: "no-store" }
  );
  if (!response.ok) throw new Error("Failed to fetch available industries");
  return response.json();
}

export async function simulateShock(
  shock: PolicyShock
): Promise<SimulationResult> {
  const response = await fetch("/api/simulate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(shock),
    cache: "no-store",
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Simulation failed (${response.status})`
    );
  }

  const result = await response.json();
  return result;
}

export async function refreshData(): Promise<{
  status: string;
  message: string;
}> {
  const response = await fetch("/api/data/refresh", {
    method: "POST",
    cache: "no-store",
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Refresh failed (${response.status})`);
  }

  return response.json();
}
