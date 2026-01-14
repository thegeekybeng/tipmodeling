"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Globe2,
  TrendingDown,
  ArrowRight,
  RefreshCw,
  Info,
  ShieldAlert,
} from "lucide-react";
import {
  simulateShock,
  fetchEconomies,
  fetchAvailableIndustries,
  SimulationResult,
  EconomicRole,
  EconomyProfile,
  IndustryProfile,
  refreshData,
} from "@/lib/api";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ReferenceDot,
} from "recharts";

export const dynamic = "force-dynamic";

export default function Home() {
  const [economies, setEconomies] = useState<EconomyProfile[]>([]);
  const [industries, setIndustries] = useState<IndustryProfile[]>([]);
  const [importingId, setImportingId] = useState("USA");
  const [exportingId, setExportingId] = useState("CHN");
  const [industryId, setIndustryId] = useState("D26");
  const [tariff, setTariff] = useState(25);
  const [simulationResult, setSimulationResult] =
    useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  const formatUSD = (val_mn: number) => {
    const absVal = Math.abs(val_mn);
    const sign = val_mn < 0 ? "-" : "";
    if (absVal >= 1000000) {
      return `${sign}$${(absVal / 1000000).toFixed(2)}T`;
    }
    if (absVal >= 1000) {
      return `${sign}$${(absVal / 1000).toFixed(2)}B`;
    }
    return `${sign}$${absVal.toLocaleString()}M`;
  };

  const loadData = useCallback(async () => {
    try {
      const econData = await fetchEconomies();
      setEconomies(econData);

      // Initialize industries for the default selection
      const availableInd = await fetchAvailableIndustries(
        importingId,
        exportingId
      );
      setIndustries(availableInd);
    } catch (err: any) {
      console.error("INITIAL_LOAD_ERROR:", err);
    }
  }, [importingId, exportingId]);

  useEffect(() => {
    setMounted(true);
    // Load initial economy data
    fetchEconomies().then(setEconomies).catch(console.error);
  }, []);

  // Update available industries when economies change
  useEffect(() => {
    if (mounted) {
      fetchAvailableIndustries(importingId, exportingId)
        .then((indData) => {
          setIndustries(indData);
          // If current industry is no longer available, select the first one
          if (indData.length > 0 && !indData.find((i) => i.id === industryId)) {
            setIndustryId(indData[0].id);
          }
        })
        .catch(console.error);
    }
  }, [importingId, exportingId, mounted]);

  const handleRunSimulation = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await simulateShock({
        source_id: importingId,
        target_id: exportingId,
        industry_id: industryId,
        tariff_delta: tariff,
      });
      setSimulationResult({ ...data });
    } catch (err: any) {
      console.error("SIMULATION_FAILURE:", err);
      setError(
        err.message || "An unexpected error occurred during simulation."
      );
    } finally {
      setLoading(false);
    }
  }, [importingId, exportingId, industryId, tariff]);

  const handleRefreshData = async () => {
    setLoading(true);
    try {
      await refreshData();
      await loadData();
      await handleRunSimulation();
    } catch (err: any) {
      setError(err.message || "Failed to refresh data");
    } finally {
      setLoading(false);
    }
  };

  const currentSensitivityPoint =
    simulationResult?.sensitivity?.data_points.find(
      (p) => Math.round(p.tariff_pct) === tariff
    );

  const resourceImpacts = simulationResult?.impacts.filter(
    (i) => i.role === EconomicRole.EXPORTING_RESOURCE
  );

  return (
    <main className="min-h-screen bg-[#020617] text-slate-50 p-4 md:p-8 lg:p-12 font-sans selection:bg-blue-500/30">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-600/10 blur-[120px] rounded-full" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        <header className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12 border-b border-slate-800 pb-8">
          <div>
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-blue-600/20 rounded-lg border border-blue-500/30">
                <Globe2 className="w-6 h-6 text-blue-400" />
              </div>
              <h1 className="text-3xl font-extrabold tracking-tighter sm:text-4xl text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-500">
                Trade & Industrial Impact Propagation Model
              </h1>
            </div>
            <p className="text-slate-400 text-lg max-w-xl leading-relaxed">
              Visualising how each nation's industrial policy creates shockwave
              across the global economies. Propogation model includes
              interactive economic tipping points with insights.
            </p>
          </div>
          <div className="flex items-center gap-4 bg-slate-900/50 p-4 rounded-xl border border-slate-800">
            <div className="text-right">
              <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest leading-none mb-1">
                Engine Status
              </p>
              <p className="text-emerald-400 font-mono text-xs flex items-center gap-1.5 justify-end">
                <span
                  className={`w-1.5 h-1.5 rounded-full bg-emerald-500 ${
                    loading ? "animate-ping" : "animate-pulse"
                  }`}
                />
                {loading ? "CALCULATING..." : "LIVE V6.0 (MACRO)"}
              </p>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <aside className="lg:col-span-4 space-y-6">
            <div className="bg-slate-950/50 backdrop-blur-xl border border-white/10 p-8 rounded-3xl shadow-2xl sticky top-8">
              <h2 className="text-xl font-bold mb-8 flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-blue-400" />
                Simulation Config
              </h2>
              <div className="space-y-6">
                <div className="space-y-2">
                  <label className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">
                    Importer
                  </label>
                  <select
                    value={importingId}
                    onChange={(e) => setImportingId(e.target.value)}
                    className="w-full bg-slate-950/50 border-none shadow-inner p-3 rounded-xl focus:ring-2 focus:ring-blue-500/50 outline-none appearance-none cursor-pointer text-sm font-mono"
                  >
                    {economies.map((e) => (
                      <option key={e.id} value={e.id}>
                        {e.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">
                    Exporter (Target)
                  </label>
                  <select
                    value={exportingId}
                    onChange={(e) => setExportingId(e.target.value)}
                    className="w-full bg-slate-950/50 border-none shadow-inner p-3 rounded-xl focus:ring-2 focus:ring-blue-500/50 outline-none appearance-none cursor-pointer text-sm font-mono"
                  >
                    {economies
                      .filter((e) => e.id !== importingId)
                      .map((e) => (
                        <option key={e.id} value={e.id}>
                          {e.name}
                        </option>
                      ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">
                    Target Sector
                  </label>
                  <select
                    value={industryId}
                    onChange={(e) => setIndustryId(e.target.value)}
                    className="w-full bg-slate-950/50 border-none shadow-inner p-3 rounded-xl focus:ring-2 focus:ring-blue-500/50 outline-none appearance-none cursor-pointer text-sm font-mono"
                  >
                    {industries.map((i) => (
                      <option key={i.id} value={i.id}>
                        {i.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-6 pt-6 border-t border-slate-800">
                  <div className="flex justify-between items-center bg-slate-950/50 p-3 rounded-xl border border-slate-800/50">
                    <label className="text-[10px] font-mono text-slate-500 uppercase tracking-widest leading-none">
                      Applied Baseline
                    </label>
                    <span className="text-slate-300 font-mono text-sm font-bold">
                      {simulationResult?.baseline_tariff_pct ?? 0}%
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <label className="text-xs font-mono text-red-500 uppercase tracking-widest font-bold">
                      Tariff Shock (Δ)
                    </label>
                    <span className="text-red-500 font-mono font-black text-2xl">
                      +{tariff}%
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    step="1"
                    value={tariff}
                    onChange={(e) => setTariff(parseInt(e.target.value))}
                    className="w-full h-3 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-red-500 hover:accent-red-400 transition-all"
                  />
                  <div className="flex justify-between items-center border-t border-white/5 pt-4">
                    <label className="text-[10px] font-mono text-slate-400 uppercase tracking-widest leading-none">
                      Total Applied
                    </label>
                    <span className="text-white font-mono text-lg font-black tabular-nums">
                      {(simulationResult?.baseline_tariff_pct ?? 0) + tariff}%
                    </span>
                  </div>
                </div>

                <div className="pt-4 space-y-3">
                  <button
                    onClick={() => handleRunSimulation()}
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-900/20 transition-all flex items-center justify-center gap-2 group"
                  >
                    <ArrowRight
                      className={`w-5 h-5 group-hover:translate-x-1 transition-transform ${
                        loading ? "animate-pulse" : ""
                      }`}
                    />
                    {loading ? "ANALYZING..." : "Run Causality Analysis"}
                  </button>

                  <button
                    onClick={handleRefreshData}
                    disabled={loading}
                    className="w-full bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-300 py-3 rounded-xl border border-slate-700/50 transition-all flex items-center justify-center gap-2 text-xs font-mono tracking-widest uppercase"
                  >
                    <RefreshCw
                      className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`}
                    />
                    Refresh Intelligence
                  </button>
                </div>
              </div>
            </div>
          </aside>

          <section className="lg:col-span-8 space-y-8">
            {error && (
              <div className="bg-red-500/10 border border-red-500/30 p-6 rounded-2xl flex items-start gap-4">
                <ShieldAlert className="w-6 h-6 text-red-500 shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-red-500 font-bold mb-1">
                    Simulation Error
                  </h3>
                  <p className="text-red-400/80 text-sm">{error}</p>
                </div>
              </div>
            )}

            {simulationResult ? (
              <div
                className={
                  loading
                    ? "opacity-50 transition-opacity"
                    : "opacity-100 transition-opacity"
                }
              >
                <div className="bg-slate-950/50 border border-white/10 rounded-[2.5rem] overflow-hidden flex flex-col shadow-2xl backdrop-blur-xl">
                  <div className="p-8 md:p-12 border-b border-slate-800/50">
                    <div className="flex flex-col md:flex-row justify-between items-start gap-8 mb-12">
                      <div className="flex-1">
                        <h3 className="text-sm font-mono text-blue-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                          <Info className="w-5 h-5" />
                          Strategic Impact Insight
                        </h3>
                        <p className="text-2xl md:text-3xl font-bold text-slate-100 leading-tight tracking-tight font-sans">
                          {simulationResult.executive_summary}
                        </p>
                      </div>
                      <div className="w-full md:w-auto p-8 bg-red-600/10 rounded-3xl border border-red-500/20 text-center min-w-[200px] shadow-[0_0_20px_rgba(239,68,68,0.1)]">
                        <p className="text-[10px] font-mono text-red-400/70 uppercase tracking-widest mb-1">
                          Current Economic Drain
                        </p>
                        <p className="text-5xl font-black tabular-nums text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-orange-500">
                          {currentSensitivityPoint
                            ? formatUSD(currentSensitivityPoint.global_loss_mn)
                            : formatUSD(
                                Math.abs(
                                  simulationResult.global_gdp_loss_usd_mn
                                )
                              )}
                        </p>
                        <p className="text-[10px] font-mono text-red-500/50 mt-2">
                          AT {tariff}% TARIFF
                        </p>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="flex justify-between items-end">
                        <div>
                          <p className="text-xs text-blue-400/70 font-mono uppercase tracking-widest mb-1">
                            Crashing Point Analysis
                          </p>
                          <div className="flex items-center gap-3">
                            <span className="text-3xl font-black text-red-500 font-mono tabular-nums">
                              {
                                simulationResult.sensitivity
                                  ?.crashing_point_tariff
                              }
                              %
                            </span>
                            <span className="px-3 py-1 bg-red-500/10 border border-red-500/50 rounded-full text-[10px] font-black text-red-500 uppercase tracking-tighter shadow-[0_0_10px_rgba(239,68,68,0.3)]">
                              Systemic Tipping Point
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="h-[280px] w-full mt-6 -ml-4">
                        {mounted && (
                          <ResponsiveContainer width="100%" height="100%">
                            <AreaChart
                              data={simulationResult.sensitivity?.data_points}
                            >
                              <defs>
                                <linearGradient
                                  id="colorLoss"
                                  x1="0"
                                  y1="0"
                                  x2="0"
                                  y2="1"
                                >
                                  <stop
                                    offset="5%"
                                    stopColor="#ef4444"
                                    stopOpacity={0.2}
                                  />
                                  <stop
                                    offset="95%"
                                    stopColor="#ef4444"
                                    stopOpacity={0}
                                  />
                                </linearGradient>
                              </defs>
                              <CartesianGrid
                                strokeDasharray="3 3"
                                stroke="#1e293b"
                                vertical={false}
                              />
                              <XAxis
                                dataKey="tariff_pct"
                                stroke="#475569"
                                fontSize={10}
                                tickFormatter={(v) => `${v}%`}
                              />
                              <YAxis hide />
                              <Tooltip
                                contentStyle={{
                                  backgroundColor: "#0f172a",
                                  border: "1px solid #334155",
                                  borderRadius: "12px",
                                }}
                                itemStyle={{
                                  color: "#ef4444",
                                  fontWeight: "bold",
                                }}
                                labelFormatter={(t) =>
                                  `Tariff Intensity: ${t}%`
                                }
                                formatter={(val: number) => [
                                  formatUSD(val),
                                  "Global Drain",
                                ]}
                              />
                              <Area
                                type="monotone"
                                dataKey="global_loss_mn"
                                stroke="#ef4444"
                                strokeWidth={3}
                                fillOpacity={1}
                                fill="url(#colorLoss)"
                              />
                              {simulationResult.sensitivity && (
                                <ReferenceLine
                                  x={
                                    simulationResult.sensitivity
                                      .crashing_point_tariff
                                  }
                                  stroke="#ef4444"
                                  strokeWidth={2}
                                  className="drop-shadow-[0_0_8px_rgba(239,68,68,0.8)]"
                                  label={{
                                    value: "TIPPING POINT",
                                    position: "insideTopRight",
                                    fill: "#ef4444",
                                    fontSize: 10,
                                    fontWeight: "bold",
                                    fontFamily: "monospace",
                                  }}
                                />
                              )}
                              <ReferenceLine
                                x={tariff}
                                stroke="#3b82f6"
                                strokeWidth={2}
                              />
                              {currentSensitivityPoint && (
                                <ReferenceDot
                                  x={tariff}
                                  y={currentSensitivityPoint.global_loss_mn}
                                  r={6}
                                  fill="#3b82f6"
                                  stroke="#fff"
                                  strokeWidth={2}
                                />
                              )}
                            </AreaChart>
                          </ResponsiveContainer>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 bg-slate-950/20">
                    <div className="p-8 border-b md:border-b-0 md:border-r border-slate-800/50">
                      <h4 className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                        <TrendingDown className="w-4 h-4" /> Shock Propagation
                      </h4>
                      <div className="space-y-4">
                        {simulationResult.visuals?.timeline.map(
                          (event, idx) => (
                            <div
                              key={idx}
                              className="flex items-start gap-4 p-4 rounded-2xl bg-slate-950/50 border border-white/5 shadow-inner"
                            >
                              <div className="text-xs font-black text-slate-700 mt-0.5">
                                0{idx + 1}
                              </div>
                              <div>
                                <p className="text-[10px] font-mono text-blue-400 uppercase tracking-tighter">
                                  {event.period}
                                </p>
                                <p className="text-sm font-bold text-slate-200 font-mono tabular-nums">
                                  {formatUSD(event.global_loss_mn)}
                                </p>
                                <p className="text-[10px] text-slate-500 italic mt-1 leading-tight">
                                  "{event.description}"
                                </p>
                              </div>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                    <div className="p-8">
                      <h4 className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                        <ShieldAlert className="w-4 h-4 text-indigo-400" />{" "}
                        Supply Chain Contrition
                      </h4>
                      <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                        {resourceImpacts?.map((imp) => (
                          <div key={imp.country_id} className="space-y-2 mb-4">
                            <div className="flex justify-between items-center p-3 rounded-xl bg-slate-950/50 border border-white/5 shadow-inner">
                              <div className="flex items-center gap-3">
                                <p className="text-[10px] font-mono text-slate-600">
                                  {imp.country_id}
                                </p>
                                <span className="text-xs font-medium text-slate-300">
                                  {imp.country_name}
                                </span>
                              </div>
                              <p className="text-xs font-black text-red-500 font-mono tabular-nums">
                                -{imp.total_gdp_impact_pct.toFixed(3)}%
                              </p>
                            </div>
                            <div className="pl-6 space-y-1">
                              {imp.sectoral_impacts.map((sect, sIdx) => (
                                <div
                                  key={sIdx}
                                  className="flex justify-between items-center text-[10px]"
                                >
                                  <span className="text-slate-500 font-mono">
                                    {sect.industry_name}
                                  </span>
                                  <span className="text-red-400 font-bold font-mono tabular-nums">
                                    {sect.impact_pct.toFixed(4)}%
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-[600px] flex flex-col items-center justify-center border-2 border-dashed border-slate-800 rounded-[3rem] bg-slate-900/10 p-12 text-center backdrop-blur-sm">
                <Globe2 className="w-20 h-20 text-slate-800 mb-8 animate-pulse" />
                <h3 className="text-2xl font-bold text-slate-400 mb-3">
                  Awaiting Strategic Configuration
                </h3>
                <p className="text-slate-500 max-w-sm text-lg leading-relaxed">
                  Configure a policy shock in the sidebar to activate the
                  interactive casualty trace engine.
                </p>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
