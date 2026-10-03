import React, { useEffect, useState } from 'react';
import api from '../api/client';
import StatusBadge from '../components/common/StatusBadge';
import UrgencyBadge from '../components/common/UrgencyBadge';
import { AlertCircle, TrendingDown, TrendingUp, RefreshCw } from 'lucide-react';

export const SkillGaps = () => {
  const [activeTab, setActiveTab] = useState('rankings'); // 'rankings' or 'matrix'
  const [rankings, setRankings] = useState(null);
  const [gaps, setGaps] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
  }, [statusFilter]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      const [rankRes, gapRes] = await Promise.all([
        api.get('/rankings?year=2024&top_n=10'),
        api.get(`/skill-gaps?year=2024${statusFilter ? `&status=${statusFilter}` : ''}&limit=100`),
      ]);
      setRankings(rankRes.data || { top_shortages: [], top_oversupply: [] });
      setGaps(gapRes.data?.items || []);
    } catch (err) {
      console.error('Failed to load skill gaps data:', err);
      setError('Failed to load skill gap analytics from the backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Skill Gap Intelligence &amp; Severity Ranking</h1>
        <p className="page-subtitle">
          District-level demand-supply mismatch indexing, severity scoring (0–100), and policy urgency tiers
        </p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid #e2e8f0', marginBottom: '20px' }}>
        <button
          onClick={() => setActiveTab('rankings')}
          style={{
            padding: '10px 18px',
            border: 'none',
            background: 'transparent',
            borderBottom: activeTab === 'rankings' ? '3px solid #2563eb' : '3px solid transparent',
            color: activeTab === 'rankings' ? '#2563eb' : '#64748b',
            fontWeight: 700,
            fontSize: '13.5px',
            cursor: 'pointer',
          }}
        >
          Priority Shortage &amp; Oversupply Rankings
        </button>

        <button
          onClick={() => setActiveTab('matrix')}
          style={{
            padding: '10px 18px',
            border: 'none',
            background: 'transparent',
            borderBottom: activeTab === 'matrix' ? '3px solid #2563eb' : '3px solid transparent',
            color: activeTab === 'matrix' ? '#2563eb' : '#64748b',
            fontWeight: 700,
            fontSize: '13.5px',
            cursor: 'pointer',
          }}
        >
          Full Skill Gap Matrix ({gaps.length} Records)
        </button>
      </div>

      {loading ? (
        <div className="loading-box">
          <div className="loading-spinner" />
          <p>Calculating skill gap rankings and severity matrices...</p>
        </div>
      ) : error ? (
        <div className="error-box">
          <AlertCircle size={16} />
          <span>{error}</span>
          <button onClick={fetchData} className="btn btn-secondary" style={{ marginLeft: 'auto', padding: '4px 10px', fontSize: 12 }}>
            <RefreshCw size={12} /> Retry
          </button>
        </div>
      ) : activeTab === 'rankings' && rankings ? (
        <>
          {/* Top Shortages Ranking Table */}
          <div className="card" style={{ marginBottom: '24px' }}>
            <div className="card-title">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <TrendingUp size={18} color="#dc2626" />
                <span style={{ color: '#dc2626' }}>Top 10 Acute Shortage Occupations (Severe Under-Supply)</span>
              </div>
              <span className="badge" style={{ background: '#fee2e2', color: '#b91c1c' }}>
                Capacity Deficit
              </span>
            </div>

            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Trade / Occupation</th>
                    <th>Sector</th>
                    <th>District</th>
                    <th>Net Shortage</th>
                    <th>Gap Ratio</th>
                    <th>Severity (0-100)</th>
                    <th>Urgency Tier</th>
                    <th>Diagnostic Factor</th>
                  </tr>
                </thead>
                <tbody>
                  {(rankings.top_shortages || []).map((item) => (
                    <tr key={item.rank}>
                      <td><span style={{ fontWeight: 800, color: '#64748b' }}>#{item.rank}</span></td>
                      <td><strong>{item.trade_name}</strong></td>
                      <td>{item.sector_name}</td>
                      <td>{item.district_name}</td>
                      <td style={{ color: '#dc2626', fontWeight: 800 }}>+{(item.net_gap ?? 0).toLocaleString()}</td>
                      <td><strong>{item.gap_ratio_pct ?? 0}%</strong></td>
                      <td style={{ minWidth: '110px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 700 }}>{item.severity_score ?? 0} / 100</div>
                        <div className="severity-bar-bg">
                          <div className="severity-bar-fill" style={{ width: `${Math.min(item.severity_score ?? 0, 100)}%`, backgroundColor: '#ef4444' }} />
                        </div>
                      </td>
                      <td><UrgencyBadge tier={item.urgency_tier || 'Critical'} /></td>
                      <td style={{ fontSize: '12px', color: '#475569', maxWidth: '340px' }}>
                        {item.diagnostic_explanation || 'Supply significantly lags estimated industry demand.'}
                      </td>
                    </tr>
                  ))}
                  {(!rankings.top_shortages || rankings.top_shortages.length === 0) && (
                    <tr>
                      <td colSpan={9} style={{ textAlign: 'center', padding: '24px', color: '#94a3b8' }}>
                        No shortage trades recorded.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Top Oversupply Ranking Table */}
          <div className="card">
            <div className="card-title">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <TrendingDown size={18} color="#d97706" />
                <span style={{ color: '#d97706' }}>Top Oversupply Occupations (Sub-Optimal Absorption)</span>
              </div>
              <span className="badge" style={{ background: '#fef3c7', color: '#92400e' }}>
                Excess Capacity
              </span>
            </div>

            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Trade / Occupation</th>
                    <th>Sector</th>
                    <th>District</th>
                    <th>Net Surplus</th>
                    <th>Gap Ratio</th>
                    <th>Severity (0-100)</th>
                    <th>Diagnostic Factor</th>
                  </tr>
                </thead>
                <tbody>
                  {(rankings.top_oversupply || []).map((item) => (
                    <tr key={item.rank}>
                      <td><span style={{ fontWeight: 800, color: '#64748b' }}>#{item.rank}</span></td>
                      <td><strong>{item.trade_name}</strong></td>
                      <td>{item.sector_name}</td>
                      <td>{item.district_name}</td>
                      <td style={{ color: '#d97706', fontWeight: 800 }}>{(item.net_gap ?? 0).toLocaleString()}</td>
                      <td><strong>{item.gap_ratio_pct ?? 0}%</strong></td>
                      <td style={{ minWidth: '110px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 700 }}>{item.severity_score ?? 0} / 100</div>
                        <div className="severity-bar-bg">
                          <div className="severity-bar-fill" style={{ width: `${Math.min(item.severity_score ?? 0, 100)}%`, backgroundColor: '#f59e0b' }} />
                        </div>
                      </td>
                      <td style={{ fontSize: '12px', color: '#475569', maxWidth: '340px' }}>
                        {item.diagnostic_explanation || 'Training capacity exceeds local industrial absorption.'}
                      </td>
                    </tr>
                  ))}
                  {(!rankings.top_oversupply || rankings.top_oversupply.length === 0) && (
                    <tr>
                      <td colSpan={8} style={{ textAlign: 'center', padding: '24px', color: '#94a3b8' }}>
                        No significant oversupply occupations identified for this cycle.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : activeTab === 'matrix' ? (
        /* Full Skill Gap Matrix */
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
            <div className="card-title" style={{ margin: 0 }}>
              Comprehensive Gap Matrix (District × Sector × Trade)
            </div>

            {/* Status Filter */}
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={() => setStatusFilter('')}
                className="btn btn-secondary"
                style={{
                  background: statusFilter === '' ? '#2563eb' : '#ffffff',
                  color: statusFilter === '' ? '#ffffff' : '#2563eb',
                  border: '1px solid #2563eb',
                  fontSize: 12,
                  padding: '5px 12px',
                }}
              >
                All Statuses
              </button>
              <button
                onClick={() => setStatusFilter('SHORTAGE')}
                className="btn btn-secondary"
                style={{
                  background: statusFilter === 'SHORTAGE' ? '#dc2626' : '#ffffff',
                  color: statusFilter === 'SHORTAGE' ? '#ffffff' : '#dc2626',
                  border: '1px solid #dc2626',
                  fontSize: 12,
                  padding: '5px 12px',
                }}
              >
                Shortages Only
              </button>
              <button
                onClick={() => setStatusFilter('OVERSUPPLY')}
                className="btn btn-secondary"
                style={{
                  background: statusFilter === 'OVERSUPPLY' ? '#d97706' : '#ffffff',
                  color: statusFilter === 'OVERSUPPLY' ? '#ffffff' : '#d97706',
                  border: '1px solid #d97706',
                  fontSize: 12,
                  padding: '5px 12px',
                }}
              >
                Oversupply Only
              </button>
              <button
                onClick={() => setStatusFilter('BALANCED')}
                className="btn btn-secondary"
                style={{
                  background: statusFilter === 'BALANCED' ? '#059669' : '#ffffff',
                  color: statusFilter === 'BALANCED' ? '#ffffff' : '#059669',
                  border: '1px solid #059669',
                  fontSize: 12,
                  padding: '5px 12px',
                }}
              >
                Balanced
              </button>
            </div>
          </div>

          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>District</th>
                  <th>Sector</th>
                  <th>Trade</th>
                  <th>Year</th>
                  <th>Demand</th>
                  <th>Supply</th>
                  <th>Net Gap</th>
                  <th>Gap Ratio</th>
                  <th>Status</th>
                  <th>Severity</th>
                  <th>Urgency</th>
                </tr>
              </thead>
              <tbody>
                {(gaps || []).map((g) => (
                  <tr key={g.id}>
                    <td><strong>{g.district_name}</strong></td>
                    <td>{g.sector_name}</td>
                    <td>{g.trade_name}</td>
                    <td>{g.year}</td>
                    <td>{(g.demand_value ?? 0).toLocaleString()}</td>
                    <td>{(g.supply_value ?? 0).toLocaleString()}</td>
                    <td
                      style={{
                        fontWeight: 700,
                        color: (g.net_gap ?? 0) > 0 ? '#dc2626' : (g.net_gap ?? 0) < 0 ? '#d97706' : '#059669',
                      }}
                    >
                      {(g.net_gap ?? 0) > 0 ? `+${(g.net_gap ?? 0).toLocaleString()}` : (g.net_gap ?? 0).toLocaleString()}
                    </td>
                    <td>{g.gap_ratio_pct ?? 0}%</td>
                    <td><StatusBadge status={g.status || 'BALANCED'} /></td>
                    <td>{g.severity_score ?? 0}</td>
                    <td><UrgencyBadge tier={g.urgency_tier || 'None'} /></td>
                  </tr>
                ))}
                {(!gaps || gaps.length === 0) && (
                  <tr>
                    <td colSpan={11} style={{ textAlign: 'center', padding: '24px', color: '#94a3b8' }}>
                      No gap records found for this filter.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default SkillGaps;
