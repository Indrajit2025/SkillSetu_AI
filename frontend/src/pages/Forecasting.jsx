import React, { useEffect, useState } from 'react';
import api from '../api/client';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  Area,
  ComposedChart,
} from 'recharts';
import { Sparkles, Award, TrendingUp, Info } from 'lucide-react';

export const Forecasting = () => {
  const [districts, setDistricts] = useState([]);
  const [sectors, setSectors] = useState([]);
  const [trades, setTrades] = useState([]);

  const [selectedDistrict, setSelectedDistrict] = useState(1);
  const [selectedSector, setSelectedSector] = useState(1);
  const [selectedTrade, setSelectedTrade] = useState(1);

  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadFilters();
  }, []);

  useEffect(() => {
    if (selectedDistrict && selectedSector && selectedTrade) {
      fetchForecast();
    }
  }, [selectedDistrict, selectedSector, selectedTrade]);

  const loadFilters = async () => {
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
      if (res.data.length > 0) {
        setSelectedTrade(res.data[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchForecast = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await api.get(
        `/forecast?district_id=${selectedDistrict}&sector_id=${selectedSector}&trade_id=${selectedTrade}`
      );
      setForecastData(res.data);
    } catch (err) {
      setError('Unable to load forecast data for this selection.');
    } finally {
      setLoading(false);
    }
  };

  // Prepare chart timeline points: combine actual and forecast
  const chartData = (forecastData?.timeline || []).map((pt) => ({
    year: pt.year,
    actual_demand: pt.is_forecast ? null : pt.actual_demand,
    actual_supply: pt.is_forecast ? null : pt.actual_supply,
    forecast_demand: pt.is_forecast ? pt.forecasted_demand : null,
    forecast_supply: pt.is_forecast ? pt.forecasted_supply : null,
    demand_upper: pt.is_forecast ? pt.demand_upper_bound : null,
    demand_lower: pt.is_forecast ? pt.demand_lower_bound : null,
  }));

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Skill Demand-Supply Forecasting Engine</h1>
        <p className="page-subtitle">
          Time-aware multi-model forecasting (2025–2028 horizon) with confidence bounds and empirical cross-validation
        </p>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="filter-group">
          <label className="filter-label">District</label>
          <select
            className="filter-select"
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

        <div className="filter-group">
          <label className="filter-label">Sector</label>
          <select
            className="filter-select"
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

        <div className="filter-group">
          <label className="filter-label">Trade / Qualification</label>
          <select
            className="filter-select"
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
      </div>

      {loading ? (
        <div className="loading-box">Executing time-aware forecast models...</div>
      ) : error ? (
        <div className="error-box">{error}</div>
      ) : forecastData ? (
        <>
          {/* AI Narrative Insight Banner */}
          <div
            style={{
              background: 'linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%)',
              color: '#ffffff',
              padding: '18px 24px',
              borderRadius: '12px',
              marginBottom: '24px',
              display: 'flex',
              alignItems: 'center',
              gap: '16px',
            }}
          >
            <Sparkles size={28} style={{ flexShrink: 0 }} />
            <div>
              <div style={{ fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.8px', color: '#93c5fd', fontWeight: 700 }}>
                AI Model Forecast Insight ({forecastData.primary_model})
              </div>
              <div style={{ fontSize: '14.5px', marginTop: '4px', lineHeight: '1.5' }}>
                {forecastData.summary_insight}
              </div>
            </div>
          </div>

          {/* Unified Historical + Forecast Chart */}
          <div className="card" style={{ marginBottom: '24px' }}>
            <div className="card-title">
              <span>
                Historical (2019–2024) vs Projected (2025–2028) Trajectory: {forecastData.district_name} • {forecastData.trade_name}
              </span>
              <span className="badge" style={{ background: '#dbeafe', color: '#1d4ed8' }}>
                95% Confidence Interval
              </span>
            </div>

            <div style={{ height: '360px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData} margin={{ top: 10, right: 30, bottom: 0, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="year" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip
                    formatter={(val) => (val !== null ? Number(val).toLocaleString() : '—')}
                    contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
                  />
                  <Legend />
                  {/* Historical Solid Lines */}
                  <Line type="monotone" dataKey="actual_demand" name="Actual Demand (2019–2024)" stroke="#2563eb" strokeWidth={3} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="actual_supply" name="Actual Supply (2019–2024)" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} />

                  {/* Forecast Dashed Lines */}
                  <Line type="monotone" dataKey="forecast_demand" name="Forecast Demand (2025–2028)" stroke="#f97316" strokeWidth={3} strokeDasharray="5 5" dot={{ r: 5 }} />
                  <Line type="monotone" dataKey="forecast_supply" name="Forecast Supply (2025–2028)" stroke="#06b6d4" strokeWidth={3} strokeDasharray="5 5" dot={{ r: 5 }} />

                  {/* Confidence Bounds */}
                  <Line type="monotone" dataKey="demand_upper" name="Upper Demand Bound (+12%)" stroke="#fed7aa" strokeDasharray="2 2" dot={false} />
                  <Line type="monotone" dataKey="demand_lower" name="Lower Demand Bound (-12%)" stroke="#fed7aa" strokeDasharray="2 2" dot={false} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Model Comparison Benchmark Leaderboard */}
          <div className="card">
            <div className="card-title">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Award size={18} color="#2563eb" />
                <span>Model Evaluation & Validation Benchmark (Tested on Held-out 2024 Split)</span>
              </div>
              <span style={{ fontSize: '11px', color: '#64748b' }}>Time-aware split: No future leak</span>
            </div>

            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Model Architecture</th>
                    <th>Status</th>
                    <th>Mean Abs Error (MAE)</th>
                    <th>Root Mean Sq Error (RMSE)</th>
                    <th>Mean Abs % Error (MAPE)</th>
                    <th>R² Goodness of Fit</th>
                    <th>Split Strategy</th>
                  </tr>
                </thead>
                <tbody>
                  {forecastData.model_comparisons.map((m, idx) => (
                    <tr key={idx} style={{ background: m.is_primary ? '#eff6ff' : 'transparent' }}>
                      <td>
                        <strong>{m.model_name}</strong>
                        {m.is_primary && (
                          <span style={{ marginLeft: '8px', fontSize: '10px', background: '#2563eb', color: 'white', padding: '2px 6px', borderRadius: '4px' }}>
                            PRIMARY
                          </span>
                        )}
                      </td>
                      <td>
                        {m.is_primary ? (
                          <span style={{ color: '#16a34a', fontWeight: 700, fontSize: '12px' }}>Selected for Engine</span>
                        ) : (
                          <span style={{ color: '#64748b', fontSize: '12px' }}>Baseline Comparison</span>
                        )}
                      </td>
                      <td><strong>{m.mae}</strong></td>
                      <td style={{ color: m.is_primary ? '#1d4ed8' : '#334155', fontWeight: 700 }}>
                        {m.rmse}
                      </td>
                      <td>{m.mape !== null ? `${m.mape}%` : 'N/A'}</td>
                      <td>
                        <span style={{ fontWeight: 700, color: m.r2_score > 0.85 ? '#16a34a' : '#d97706' }}>
                          {m.r2_score}
                        </span>
                      </td>
                      <td style={{ fontSize: '11.5px', color: '#64748b' }}>
                        Train: {m.train_years} | Test: {m.test_year}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
};

export default Forecasting;
