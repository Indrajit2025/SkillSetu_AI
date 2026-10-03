import React, { useEffect, useState } from 'react';
import api from '../api/client';
import StatusBadge from '../components/common/StatusBadge';
import UrgencyBadge from '../components/common/UrgencyBadge';
import AssistedGuide from '../components/common/AssistedGuide';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  LineChart,
  Line,
} from 'recharts';
import { Sliders, Play, RotateCcw, CheckCircle2, TrendingDown, ArrowRight, Sparkles } from 'lucide-react';

export const Simulator = () => {
  const [districts, setDistricts] = useState([]);
  const [sectors, setSectors] = useState([]);
  const [trades, setTrades] = useState([]);

  // Selections
  const [selectedDistrict, setSelectedDistrict] = useState(1);
  const [selectedSector, setSelectedSector] = useState(1);
  const [selectedTrade, setSelectedTrade] = useState(1);
  const [targetYear, setTargetYear] = useState(2026);

  // Intervention Knobs
  const [additionalSeats, setAdditionalSeats] = useState(500);
  const [intakeExpansionPct, setIntakeExpansionPct] = useState(15.0);
  const [demandSurgePct, setDemandSurgePct] = useState(5.0);
  const [placementBoostPct, setPlacementBoostPct] = useState(10.0);

  // Simulation State
  const [simulationResult, setSimulationResult] = useState(null);
  const [simulating, setSimulating] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadTaxonomy();
  }, []);

  const loadTaxonomy = async () => {
    try {
      const [distRes, secRes, trRes] = await Promise.all([
        api.get('/states/1/districts'),
        api.get('/sectors'),
        api.get('/trades?sector_id=1'),
      ]);
      setDistricts(distRes.data);
      setSectors(secRes.data);
      setTrades(trRes.data);
      if (distRes.data.length > 0) setSelectedDistrict(distRes.data[0].id);
      if (secRes.data.length > 0) setSelectedSector(secRes.data[0].id);
      if (trRes.data.length > 0) setSelectedTrade(trRes.data[0].id);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSectorChange = async (secId) => {
    setSelectedSector(secId);
    try {
      const res = await api.get(`/trades?sector_id=${secId}`);
      setTrades(res.data);
      if (res.data.length > 0) setSelectedTrade(res.data[0].id);
    } catch (err) {
      console.error(err);
    }
  };

  const runSimulation = async () => {
    setSimulating(true);
    setError('');
    try {
      const payload = {
        scenario_name: 'Policy Intervention Simulation',
        district_id: selectedDistrict,
        sector_id: selectedSector,
        trade_id: selectedTrade,
        target_year: targetYear,
        additional_seats: Number(additionalSeats),
        intake_expansion_pct: Number(intakeExpansionPct),
        demand_surge_pct: Number(demandSurgePct),
        placement_boost_pct: Number(placementBoostPct),
      };
      const res = await api.post('/scenarios', payload);
      setSimulationResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Simulation execution failed.');
    } finally {
      setSimulating(false);
    }
  };

  // Run automatically on first load once taxonomy is loaded
  useEffect(() => {
    if (selectedDistrict && selectedSector && selectedTrade) {
      runSimulation();
    }
  }, [selectedDistrict, selectedSector, selectedTrade]);

  return (
    <div>
      <AssistedGuide
        title="What-If Policy Simulation Guide"
        purpose="Model and test policy interventions in training seats, institutional intake, or local placement retention before committing state funds."
        steps={[
          { bold: 'Select Target', desc: 'Choose a district, sector, trade, and target budget horizon year (2025–2028).' },
          { bold: 'Adjust Policy Knobs', desc: 'Move the sliders for +Seats, +Intake %, +Demand Shock %, and +Placement Retention %.' },
          { bold: 'Review Real-time Impact', desc: 'Observe how the Net Gap reduces and how Severity Score shifts (e.g. Critical to Medium).' },
        ]}
        nextActionLabel="Review Model Evaluation"
        nextActionTo="/app/model-evaluation"
      />
      <div className="page-header">
        <h1 className="page-title">What-If Policy Scenario Simulator</h1>
        <p className="page-subtitle">
          Test training seat expansions, intake boosts, and placement improvements to assess gap mitigation before funding commitment
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: '24px' }}>
        {/* Left Column: Intervention Control Knobs */}
        <div className="card">
          <div className="card-title">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sliders size={18} color="#2563eb" />
              <span>Intervention Knobs</span>
            </div>
            <button
              onClick={() => {
                setAdditionalSeats(500);
                setIntakeExpansionPct(15.0);
                setDemandSurgePct(5.0);
                setPlacementBoostPct(10.0);
              }}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#64748b',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '11px',
              }}
            >
              <RotateCcw size={12} /> Reset
            </button>
          </div>

          {/* Geography & Trade Selection */}
          <div className="form-group">
            <label>Target District</label>
            <select
              className="form-input"
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(Number(e.target.value))}
            >
              {districts.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Sector</label>
            <select
              className="form-input"
              value={selectedSector}
              onChange={(e) => handleSectorChange(Number(e.target.value))}
            >
              {sectors.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Trade / Qualification</label>
            <select
              className="form-input"
              value={selectedTrade}
              onChange={(e) => setSelectedTrade(Number(e.target.value))}
            >
              {trades.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Target Horizon Year</label>
            <select
              className="form-input"
              value={targetYear}
              onChange={(e) => setTargetYear(Number(e.target.value))}
            >
              <option value={2025}>2025 (Immediate Cycle)</option>
              <option value={2026}>2026 (Medium Horizon)</option>
              <option value={2027}>2027 (Long Horizon)</option>
              <option value={2028}>2028 (Strategic Vision)</option>
            </select>
          </div>

          <hr style={{ border: 'none', borderTop: '1px solid #e2e8f0', margin: '20px 0' }} />

          {/* Slider 1: Additional Seats */}
          <div className="slider-group">
            <div className="slider-header">
              <span>Additional Training Seats</span>
              <strong style={{ color: '#2563eb' }}>+{additionalSeats} Seats</strong>
            </div>
            <input
              type="range"
              min="0"
              max="2000"
              step="50"
              className="slider-input"
              value={additionalSeats}
              onChange={(e) => setAdditionalSeats(Number(e.target.value))}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10.5px', color: '#94a3b8' }}>
              <span>0 (Status Quo)</span>
              <span>+1,000</span>
              <span>+2,000 Seats</span>
            </div>
          </div>

          {/* Slider 2: Intake Expansion % */}
          <div className="slider-group">
            <div className="slider-header">
              <span>Institutional Intake Boost</span>
              <strong style={{ color: '#2563eb' }}>+{intakeExpansionPct}%</strong>
            </div>
            <input
              type="range"
              min="0"
              max="50"
              step="5"
              className="slider-input"
              value={intakeExpansionPct}
              onChange={(e) => setIntakeExpansionPct(Number(e.target.value))}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10.5px', color: '#94a3b8' }}>
              <span>0%</span>
              <span>+25%</span>
              <span>+50% Expansion</span>
            </div>
          </div>

          {/* Slider 3: Demand Surge % */}
          <div className="slider-group">
            <div className="slider-header">
              <span>Simulated Demand Shock / Surge</span>
              <strong style={{ color: demandSurgePct >= 0 ? '#ea580c' : '#16a34a' }}>
                {demandSurgePct >= 0 ? `+${demandSurgePct}%` : `${demandSurgePct}%`}
              </strong>
            </div>
            <input
              type="range"
              min="-20"
              max="40"
              step="5"
              className="slider-input"
              value={demandSurgePct}
              onChange={(e) => setDemandSurgePct(Number(e.target.value))}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10.5px', color: '#94a3b8' }}>
              <span>-20% (Decline)</span>
              <span>0%</span>
              <span>+40% (Surge)</span>
            </div>
          </div>

          {/* Slider 4: Placement Boost % */}
          <div className="slider-group">
            <div className="slider-header">
              <span>Local Placement / Absorption Boost</span>
              <strong style={{ color: '#10b981' }}>+{placementBoostPct}%</strong>
            </div>
            <input
              type="range"
              min="0"
              max="30"
              step="2"
              className="slider-input"
              value={placementBoostPct}
              onChange={(e) => setPlacementBoostPct(Number(e.target.value))}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10.5px', color: '#94a3b8' }}>
              <span>0% (Historical)</span>
              <span>+15%</span>
              <span>+30% Retention</span>
            </div>
          </div>

          <button
            onClick={runSimulation}
            disabled={simulating}
            className="auth-btn-primary"
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginTop: '16px' }}
          >
            <Play size={16} />
            <span>{simulating ? 'Simulating...' : 'Recalculate Scenario'}</span>
          </button>
        </div>

        {/* Right Column: Simulation Output & Impact Analysis */}
        <div>
          {error && <div className="error-box">{error}</div>}

          {simulationResult && (
            <>
              {/* Policy Impact Summary Card */}
              <div
                style={{
                  background: '#f0fdf4',
                  border: '1px solid #bbf7d0',
                  borderRadius: '12px',
                  padding: '18px 24px',
                  marginBottom: '20px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#166534', fontWeight: 800, fontSize: '13px', textTransform: 'uppercase', marginBottom: '6px' }}>
                  <Sparkles size={18} />
                  <span>AI Policy Impact Assessment</span>
                </div>
                <div style={{ fontSize: '14.5px', color: '#14532d', lineHeight: '1.6' }}>
                  {simulationResult.policy_impact_summary}
                </div>
              </div>

              {/* Baseline vs Scenario 4-Card Comparison Grid */}
              <div className="grid-cols-4" style={{ marginBottom: '20px' }}>
                {/* 1. Demand Comparison */}
                <div className="metric-card">
                  <div className="label">Labour Demand</div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                    <span style={{ fontSize: '16px', color: '#64748b', textDecoration: 'line-through' }}>
                      {Math.round(simulationResult.baseline_demand).toLocaleString()}
                    </span>
                    <span style={{ fontSize: '22px', fontWeight: 800, color: '#1e293b' }}>
                      {Math.round(simulationResult.scenario_demand).toLocaleString()}
                    </span>
                  </div>
                  <div className="meta" style={{ color: '#ea580c' }}>
                    {demandSurgePct > 0 ? `+${demandSurgePct}% Demand Surge` : 'Status Quo Demand'}
                  </div>
                </div>

                {/* 2. Supply Comparison */}
                <div className="metric-card">
                  <div className="label">Effective Supply</div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                    <span style={{ fontSize: '16px', color: '#64748b' }}>
                      {Math.round(simulationResult.baseline_supply).toLocaleString()}
                    </span>
                    <ArrowRight size={14} color="#94a3b8" />
                    <span style={{ fontSize: '22px', fontWeight: 800, color: '#10b981' }}>
                      {Math.round(simulationResult.effective_scenario_supply).toLocaleString()}
                    </span>
                  </div>
                  <div className="meta" style={{ color: '#16a34a' }}>
                    +{Math.round(simulationResult.effective_scenario_supply - simulationResult.baseline_supply).toLocaleString()} New Skilled Workers
                  </div>
                </div>

                {/* 3. Net Gap Delta */}
                <div className="metric-card">
                  <div className="label">Net Labour Gap</div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                    <span style={{ fontSize: '16px', color: '#64748b' }}>
                      {Math.round(simulationResult.baseline_net_gap).toLocaleString()}
                    </span>
                    <ArrowRight size={14} color="#94a3b8" />
                    <span style={{ fontSize: '22px', fontWeight: 800, color: '#dc2626' }}>
                      {Math.round(simulationResult.scenario_net_gap).toLocaleString()}
                    </span>
                  </div>
                  <div className="meta" style={{ color: '#2563eb', fontWeight: 600 }}>
                    Delta: {simulationResult.delta_net_gap > 0 ? `+${simulationResult.delta_net_gap}` : simulationResult.delta_net_gap}
                  </div>
                </div>

                {/* 4. Severity Score Shift */}
                <div className="metric-card">
                  <div className="label">Severity Score Shift</div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                    <span style={{ fontSize: '16px', color: '#64748b' }}>
                      {simulationResult.baseline_severity_score}
                    </span>
                    <ArrowRight size={14} color="#94a3b8" />
                    <span style={{ fontSize: '22px', fontWeight: 800, color: simulationResult.delta_severity_score < 0 ? '#10b981' : '#ef4444' }}>
                      {simulationResult.scenario_severity_score}
                    </span>
                  </div>
                  <div className="meta">
                    Shift: {simulationResult.baseline_urgency_tier} → <strong>{simulationResult.scenario_urgency_tier}</strong>
                  </div>
                </div>
              </div>

              {/* Multi-Year Timeline Comparison Chart */}
              <div className="card">
                <div className="card-title">
                  <span>Baseline vs Scenario Trajectory (2024–2028 Timeline)</span>
                  <span style={{ fontSize: '12px', color: '#64748b' }}>Year-by-year impact simulation</span>
                </div>

                <div style={{ height: '320px', width: '100%' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={simulationResult.comparison_timeline} margin={{ top: 10, right: 20, bottom: 0, left: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="year" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip
                        formatter={(val) => Number(val).toLocaleString()}
                        contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
                      />
                      <Legend />
                      <Bar dataKey="baseline_demand" name="Baseline Demand" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="baseline_supply" name="Baseline Supply" fill="#cbd5e1" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="scenario_demand" name="Scenario Demand" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="effective_scenario_supply" name="Scenario Effective Supply" fill="#10b981" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Simulator;
