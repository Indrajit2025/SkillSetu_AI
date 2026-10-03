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
} from 'recharts';
import { Info, Sliders, Briefcase, GraduationCap } from 'lucide-react';

export const MarketIntelligence = () => {
  const [districts, setDistricts] = useState([]);
  const [sectors, setSectors] = useState([]);
  const [trades, setTrades] = useState([]);

  const [selectedDistrict, setSelectedDistrict] = useState(1);
  const [selectedSector, setSelectedSector] = useState(1);
  const [selectedTrade, setSelectedTrade] = useState(1);

  const [marketDetails, setMarketDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadTaxonomy();
  }, []);

  useEffect(() => {
    if (selectedDistrict && selectedSector && selectedTrade) {
      fetchMarketDetails();
    }
  }, [selectedDistrict, selectedSector, selectedTrade]);

  const loadTaxonomy = async () => {
    try {
      // 1 is Odisha
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
      console.error('Failed to load taxonomy', err);
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

  const fetchMarketDetails = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await api.get(
        `/market-details?district_id=${selectedDistrict}&sector_id=${selectedSector}&trade_id=${selectedTrade}`
      );
      setMarketDetails(res.data);
    } catch (err) {
      setError('No demand/supply records found for this combination.');
    } finally {
      setLoading(false);
    }
  };

  // Merge demand and supply series into single timeline table for charts
  const combinedTimeline = (marketDetails?.demand_series || []).map((d) => {
    const s = (marketDetails?.supply_series || []).find((x) => x.year === d.year);
    return {
      year: d.year,
      estimated_demand: d.estimated_total_demand,
      effective_supply: s?.effective_local_supply || 0,
      demand_index: d.normalized_demand_index,
      supply_index: s?.normalized_supply_index || 0,
      job_postings: d.job_postings_count,
      sanctioned_seats: s?.sanctioned_seats || 0,
      passouts: s?.passouts || 0,
      local_absorption_rate_pct: s?.local_absorption_rate_pct || 0,
    };
  });

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Labour Market Intelligence</h1>
        <p className="page-subtitle">
          Decomposed demand signals (NCS, Job Postings, GVA) vs Supply Capacity (NCVT-MIS seats, enrolments, absorption)
        </p>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="filter-group">
          <label className="filter-label">1. District</label>
          <select
            className="filter-select"
            value={selectedDistrict}
            onChange={(e) => setSelectedDistrict(Number(e.target.value))}
          >
            {districts.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name} ({d.economic_tier || 'Tier-2'})
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">2. Sector</label>
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
          <label className="filter-label">3. Trade / Occupation</label>
          <select
            className="filter-select"
            value={selectedTrade}
            onChange={(e) => setSelectedTrade(Number(e.target.value))}
          >
            {trades.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name} (NSQF L{t.nsqf_level || 4})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading-box">Retrieving market intelligence metrics...</div>
      ) : error ? (
        <div className="error-box">{error}</div>
      ) : marketDetails ? (
        <>
          {/* Signal Decomposition Cards */}
          <div className="grid-cols-2">
            {/* Demand Signals */}
            <div className="card">
              <div className="card-title">
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Briefcase size={18} color="#2563eb" />
                  <span>Demand Signal Decomposition (2024 Latest)</span>
                </div>
                <span className="badge" style={{ background: '#dbeafe', color: '#1d4ed8' }}>
                  Weighted Index Engine
                </span>
              </div>

              {marketDetails.demand_series.length > 0 && (
                <div>
                  {(() => {
                    const latest = marketDetails.demand_series[marketDetails.demand_series.length - 1];
                    return (
                      <>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '16px' }}>
                          <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px' }}>
                            <div style={{ fontSize: '11px', color: '#64748b' }}>Active Job Postings</div>
                            <div style={{ fontSize: '20px', fontWeight: 800 }}>{latest.job_postings_count.toLocaleString()}</div>
                            <div style={{ fontSize: '10.5px', color: '#16a34a' }}>+ Weight: 35%</div>
                          </div>
                          <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px' }}>
                            <div style={{ fontSize: '11px', color: '#64748b' }}>Hiring Growth Rate (YoY)</div>
                            <div style={{ fontSize: '20px', fontWeight: 800 }}>{latest.hiring_growth_rate_pct}%</div>
                            <div style={{ fontSize: '10.5px', color: '#16a34a' }}>+ Weight: 25%</div>
                          </div>
                          <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px' }}>
                            <div style={{ fontSize: '11px', color: '#64748b' }}>Sector GVA Growth</div>
                            <div style={{ fontSize: '20px', fontWeight: 800 }}>{latest.gva_growth_pct}%</div>
                            <div style={{ fontSize: '10.5px', color: '#16a34a' }}>+ Weight: 20%</div>
                          </div>
                          <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px' }}>
                            <div style={{ fontSize: '11px', color: '#64748b' }}>Industrial Inflows</div>
                            <div style={{ fontSize: '20px', fontWeight: 800 }}>₹{latest.investment_inflow_crores} Cr</div>
                            <div style={{ fontSize: '10.5px', color: '#16a34a' }}>+ Weight: 20%</div>
                          </div>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', background: '#eff6ff', borderRadius: '8px' }}>
                          <div>
                            <div style={{ fontSize: '12px', fontWeight: 700, color: '#1e40af' }}>Normalized Demand Index</div>
                            <div style={{ fontSize: '11px', color: '#3b82f6' }}>Composite Min-Max Normalized (0–100 Scale)</div>
                          </div>
                          <div style={{ fontSize: '24px', fontWeight: 900, color: '#1d4ed8' }}>
                            {latest.normalized_demand_index} / 100
                          </div>
                        </div>
                      </>
                    );
                  })()}
                </div>
              )}
            </div>

            {/* Supply Signals */}
            <div className="card">
              <div className="card-title">
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <GraduationCap size={18} color="#10b981" />
                  <span>Supply Capacity & Absorption (2024 Latest)</span>
                </div>
                <span className="badge" style={{ background: '#d1fae5', color: '#047857' }}>
                  NCVT-MIS Aligned
                </span>
              </div>

              {marketDetails.supply_series.length > 0 && (
                <div>
                  {(() => {
                    const latest = marketDetails.supply_series[marketDetails.supply_series.length - 1];
                    return (
                      <>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '16px' }}>
                          <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px' }}>
                            <div style={{ fontSize: '11px', color: '#64748b' }}>Sanctioned Seats</div>
                            <div style={{ fontSize: '20px', fontWeight: 800 }}>{latest.sanctioned_seats.toLocaleString()}</div>
                            <div style={{ fontSize: '10.5px', color: '#059669' }}>Seat Weight: 30%</div>
                          </div>
                          <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px' }}>
                            <div style={{ fontSize: '11px', color: '#64748b' }}>Actual Enrolments</div>
                            <div style={{ fontSize: '20px', fontWeight: 800 }}>{latest.actual_enrolments.toLocaleString()}</div>
                            <div style={{ fontSize: '10.5px', color: '#059669' }}>Enrolment Weight: 35%</div>
                          </div>
                          <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px' }}>
                            <div style={{ fontSize: '11px', color: '#64748b' }}>Certified Passouts</div>
                            <div style={{ fontSize: '20px', fontWeight: 800 }}>{latest.passouts.toLocaleString()}</div>
                            <div style={{ fontSize: '10.5px', color: '#059669' }}>Completion Weight: 35%</div>
                          </div>
                          <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px' }}>
                            <div style={{ fontSize: '11px', color: '#64748b' }}>Local Absorption Rate</div>
                            <div style={{ fontSize: '20px', fontWeight: 800 }}>{latest.local_absorption_rate_pct}%</div>
                            <div style={{ fontSize: '10.5px', color: '#0284c7' }}>Effective: {latest.effective_local_supply}</div>
                          </div>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', background: '#ecfdf5', borderRadius: '8px' }}>
                          <div>
                            <div style={{ fontSize: '12px', fontWeight: 700, color: '#065f46' }}>Normalized Supply Index</div>
                            <div style={{ fontSize: '11px', color: '#059669' }}>Composite Capacity & Completion Metric</div>
                          </div>
                          <div style={{ fontSize: '24px', fontWeight: 900, color: '#047857' }}>
                            {latest.normalized_supply_index} / 100
                          </div>
                        </div>
                      </>
                    );
                  })()}
                </div>
              )}
            </div>
          </div>

          {/* Historical Demand vs Supply Trend Chart */}
          <div className="card">
            <div className="card-title">
              <span>Demand vs Effective Supply Trend ({marketDetails.district_name} • {marketDetails.trade_name})</span>
              <span style={{ fontSize: '12px', color: '#64748b' }}>2019 – 2024 Empirical & Calibrated Records</span>
            </div>
            <div style={{ height: '320px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={combinedTimeline} margin={{ top: 10, right: 30, bottom: 0, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="year" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip
                    formatter={(val) => Number(val).toLocaleString()}
                    contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="estimated_demand" name="Estimated Labour Demand" stroke="#2563eb" strokeWidth={3} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="effective_supply" name="Effective Local Supply" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="job_postings" name="Job Postings" stroke="#f59e0b" strokeWidth={2} strokeDasharray="4 4" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
};

export default MarketIntelligence;
