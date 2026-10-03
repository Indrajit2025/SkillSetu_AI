import React, { useEffect, useState } from 'react';
import api from '../api/client';
import StatusBadge from '../components/common/StatusBadge';
import UrgencyBadge from '../components/common/UrgencyBadge';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  Tooltip, Legend, BarChart, Bar, CartesianGrid,
} from 'recharts';
import {
  ArrowUpRight, TrendingUp, AlertTriangle, Users,
  MapPin, Sliders, X, ChevronDown, ChevronRight,
} from 'lucide-react';
import { Link } from 'react-router-dom';

/* ── Small sub-components ─────────────────────────── */

const LoadingScreen = () => (
  <div className="loading-box">
    <div className="loading-spinner" />
    <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>Loading intelligence overview…</p>
  </div>
);

const ExploreCard = ({ icon: Icon, iconBg, iconColor, pill, pillColor, title, value, sub, onClick, active }) => (
  <button
    onClick={onClick}
    style={{
      all: 'unset',
      display: 'flex',
      flexDirection: 'column',
      gap: 10,
      padding: '22px 22px 18px',
      background: active ? '#f0f5ff' : 'var(--bg-card)',
      border: `1px solid ${active ? '#93c5fd' : 'var(--border)'}`,
      borderRadius: 'var(--radius-lg)',
      cursor: 'pointer',
      transition: 'all 0.2s',
      boxShadow: active ? '0 0 0 3px rgba(37,99,235,0.1)' : 'var(--shadow-sm)',
      textAlign: 'left',
      width: '100%',
    }}
  >
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ width: 38, height: 38, borderRadius: 9, background: iconBg, color: iconColor, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Icon size={18} />
      </div>
      {pill && (
        <span style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.4, padding: '2px 8px', borderRadius: 10, background: pillColor || '#f3f4f6', color: pilColor || 'var(--text-secondary)' }}>
          {pill}
        </span>
      )}
    </div>
    <div>
      <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 0.4 }}>{title}</div>
      {value && <div style={{ fontSize: 28, fontWeight: 900, letterSpacing: -1, color: 'var(--text)', lineHeight: 1.1, marginTop: 2 }}>{value}</div>}
      {sub && <div style={{ fontSize: 12, color: 'var(--text-tertiary)', marginTop: 3 }}>{sub}</div>}
    </div>
    <div style={{ fontSize: 12.5, fontWeight: 600, color: active ? 'var(--primary)' : 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 4, marginTop: 2 }}>
      {active ? <><X size={12} /> Close details</> : <><ChevronDown size={12} /> See details</>}
    </div>
  </button>
);

/* ── Main Dashboard ───────────────────────────────── */
export const Dashboard = () => {
  const [overview, setOverview] = useState(null);
  const [states, setStates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activePanel, setActivePanel] = useState(null); // 'trend' | 'sectors' | 'shortages' | null

  useEffect(() => {
    Promise.all([api.get('/overview'), api.get('/states')])
      .then(([ovRes, stRes]) => {
        setOverview(ovRes.data);
        setStates(stRes.data);
      })
      .catch(() => setError('Failed to load overview data from FastAPI backend.'))
      .finally(() => setLoading(false));
  }, []);

  const togglePanel = (name) => setActivePanel(prev => prev === name ? null : name);

  if (loading) return <LoadingScreen />;
  if (error) return <div className="error-box">{error}</div>;
  if (!overview) return null;

  const shortage = overview.metric_cards?.find(c => c.label?.toLowerCase().includes('shortage'))?.value ?? '—';
  const demand = overview.total_annual_demand?.toLocaleString() ?? '—';
  const districts = overview.total_districts ?? 30;

  return (
    <div>

      {/* ── HERO BAND ─────────────────────────────── */}
      <div className="dash-hero-band">
        <div>
          <h1>Executive Labour Intelligence</h1>
          <p>National → State → District demand-supply matrix · Pilot: Odisha 30 districts, 8 sectors</p>
        </div>
        <div className="dash-hero-kpis">
          <div className="dash-kpi">
            <div className="kv">{demand}</div>
            <div className="kl">Total Demand</div>
          </div>
          <div className="dash-kpi">
            <div className="kv red">{shortage}</div>
            <div className="kl">Shortage Zones</div>
          </div>
          <div className="dash-kpi">
            <div className="kv green">{districts}</div>
            <div className="kl">Districts</div>
          </div>
        </div>
      </div>

      {/* ── EXPLORE CARDS ROW ─────────────────────── */}
      <div className="explore-row">
        <ExploreCard
          icon={TrendingUp} iconBg="#eff6ff" iconColor="#2563eb"
          title="Historical Trend"
          value="2019–2024"
          sub="Demand vs supply over 6 years"
          active={activePanel === 'trend'}
          onClick={() => togglePanel('trend')}
        />
        <ExploreCard
          icon={Users} iconBg="#ecfdf5" iconColor="#059669"
          title="Sector Breakdown"
          value="8 Sectors"
          sub="Demand/supply by industry"
          active={activePanel === 'sectors'}
          onClick={() => togglePanel('sectors')}
        />
        <ExploreCard
          icon={AlertTriangle} iconBg="#fef2f2" iconColor="#dc2626"
          title="Critical Shortages"
          value="Top 5"
          sub="Highest severity trade gaps"
          active={activePanel === 'shortages'}
          onClick={() => togglePanel('shortages')}
        />
      </div>

      {/* ── DETAIL PANEL: TREND ───────────────────── */}
      {activePanel === 'trend' && (
        <div className="detail-panel">
          <div className="detail-panel-header">
            <div className="detail-panel-title">Historical Labour Demand vs Supply Trend (2019–2024)</div>
            <button className="close-btn" onClick={() => setActivePanel(null)}><X size={14} /></button>
          </div>
          <div style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={overview.time_series_trend} margin={{ top: 8, right: 20, bottom: 0, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="year" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <Tooltip
                  formatter={(v) => Number(v).toLocaleString()}
                  contentStyle={{ borderRadius: 8, border: '1px solid #e5e7eb', fontSize: 13 }}
                />
                <Legend />
                <Line type="monotone" dataKey="total_demand" name="Total Demand" stroke="#2563eb" strokeWidth={3} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="total_supply" name="Effective Supply" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="insight-box blue" style={{ marginTop: 16 }}>
            <strong>Insight:</strong> Demand outpaces supply across most years — the gap is widening, indicating a structural shortage that intensifies without policy intervention.
          </div>
          <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
            <Link to="/app/market" className="btn btn-primary" style={{ fontSize: 13 }}>
              Market Intelligence <ArrowUpRight size={13} />
            </Link>
            <Link to="/app/forecast" className="btn btn-secondary" style={{ fontSize: 13 }}>
              View 2025–2028 Forecasts
            </Link>
          </div>
        </div>
      )}

      {/* ── DETAIL PANEL: SECTORS ─────────────────── */}
      {activePanel === 'sectors' && (
        <div className="detail-panel">
          <div className="detail-panel-header">
            <div className="detail-panel-title">Sectoral Demand-Supply Distribution — 8 Priority Sectors</div>
            <button className="close-btn" onClick={() => setActivePanel(null)}><X size={14} /></button>
          </div>
          <div style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={overview.sector_breakdown} margin={{ top: 8, right: 20, bottom: 28, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="sector_name" stroke="#94a3b8" tick={{ fontSize: 10 }} interval={0} angle={-15} textAnchor="end" />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <Tooltip
                  formatter={(v) => Number(v).toLocaleString()}
                  contentStyle={{ borderRadius: 8, border: '1px solid #e5e7eb', fontSize: 13 }}
                />
                <Legend />
                <Bar dataKey="demand_volume" name="Demand" fill="#3b82f6" radius={[4,4,0,0]} />
                <Bar dataKey="supply_volume" name="Supply" fill="#34d399" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
            <Link to="/app/drilldown" className="btn btn-primary" style={{ fontSize: 13 }}>
              District Explorer <ArrowUpRight size={13} />
            </Link>
            <Link to="/app/skill-gaps" className="btn btn-secondary" style={{ fontSize: 13 }}>
              Skill Gap Matrix
            </Link>
          </div>
        </div>
      )}

      {/* ── DETAIL PANEL: SHORTAGES ───────────────── */}
      {activePanel === 'shortages' && (
        <div className="detail-panel">
          <div className="detail-panel-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <AlertTriangle size={16} color="#ef4444" />
              <div className="detail-panel-title">Top Critical Shortage Trades — Policy Priority Window</div>
            </div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <Link to="/app/skill-gaps" style={{ fontSize: 12.5, color: 'var(--primary)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}>
                Full Matrix <ArrowUpRight size={13} />
              </Link>
              <button className="close-btn" onClick={() => setActivePanel(null)}><X size={14} /></button>
            </div>
          </div>

          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>District</th>
                  <th>Sector</th>
                  <th>Trade</th>
                  <th>Demand</th>
                  <th>Supply</th>
                  <th>Net Gap</th>
                  <th>Severity</th>
                  <th>Urgency</th>
                </tr>
              </thead>
              <tbody>
                {overview.top_critical_trades.map((item, i) => (
                  <tr key={i}>
                    <td><strong>{item.district_name}</strong></td>
                    <td style={{ fontSize: 12.5, color: 'var(--text-secondary)' }}>{item.sector_name}</td>
                    <td><span style={{ fontWeight: 600 }}>{item.trade_name}</span></td>
                    <td>{item.demand.toLocaleString()}</td>
                    <td>{item.supply.toLocaleString()}</td>
                    <td style={{ color: '#dc2626', fontWeight: 700 }}>+{item.net_gap.toLocaleString()}</td>
                    <td style={{ minWidth: 100 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, fontWeight: 700 }}>
                        <span>{item.severity_score}</span><span style={{ color: 'var(--text-tertiary)' }}>/100</span>
                      </div>
                      <div className="severity-bar-bg">
                        <div className="severity-bar-fill" style={{ width: `${item.severity_score}%`, backgroundColor: item.severity_score > 70 ? '#ef4444' : '#f59e0b' }} />
                      </div>
                    </td>
                    <td><UrgencyBadge tier={item.urgency_tier} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
            <Link to="/app/skill-gaps" className="btn btn-primary" style={{ fontSize: 13 }}>
              Full Skill Gap Analysis <ArrowUpRight size={13} />
            </Link>
            <Link to="/app/simulator" className="btn btn-secondary" style={{ fontSize: 13 }}>
              Simulate Interventions
            </Link>
          </div>
        </div>
      )}

      {/* ── SECONDARY KPI CARDS ───────────────────── */}
      {overview.metric_cards && overview.metric_cards.length > 0 && (
        <>
          <div style={{ marginBottom: 16 }}>
            <span className="section-eyebrow">Key Performance Indicators</span>
            <h2 className="section-title">Aggregate Metrics</h2>
          </div>
          <div className="grid-cols-4">
            {overview.metric_cards.slice(0, 8).map((card, idx) => (
              <div key={idx} className="metric-card">
                <div className="label">{card.label}</div>
                <div className="value">{card.value}</div>
                <div className="meta">
                  <span style={{
                    display: 'inline-block', width: 7, height: 7, borderRadius: '50%',
                    background: card.badge_variant === 'danger' ? '#ef4444' : card.badge_variant === 'warning' ? '#f59e0b' : card.badge_variant === 'success' ? '#10b981' : '#3b82f6',
                    flexShrink: 0,
                  }} />
                  <span>{card.description}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* ── NAVIGATION NUDGES ─────────────────────── */}
      <div className="grid-cols-3" style={{ marginTop: 8 }}>
        {[
          { to: '/app/forecast', icon: TrendingUp, label: 'View 2025–2028 Forecast', color: '#d97706', bg: '#fffbeb', desc: 'AI projections with confidence bounds' },
          { to: '/app/early-warning', icon: AlertTriangle, label: 'Early Warning System', color: '#db2777', bg: '#fdf2f8', desc: 'Upcoming shortage & oversupply alerts' },
          { to: '/app/simulator', icon: Sliders, label: 'Launch What-If Simulator', color: '#4338ca', bg: '#eef2ff', desc: 'Test policy interventions interactively' },
        ].map(({ to, icon: Icon, label, color, bg, desc }) => (
          <Link key={to} to={to} style={{
            display: 'flex', alignItems: 'center', gap: 14, padding: '16px 18px',
            background: 'var(--bg-card)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius)', textDecoration: 'none', color: 'inherit',
            transition: 'all 0.18s', boxShadow: 'var(--shadow-sm)',
          }}
            onMouseEnter={e => { e.currentTarget.style.boxShadow = 'var(--shadow-md)'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
            onMouseLeave={e => { e.currentTarget.style.boxShadow = 'var(--shadow-sm)'; e.currentTarget.style.transform = ''; }}
          >
            <div style={{ width: 38, height: 38, borderRadius: 9, background: bg, color, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <Icon size={18} />
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 13.5, fontWeight: 700, color: 'var(--text)' }}>{label}</div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>{desc}</div>
            </div>
            <ChevronRight size={16} color="var(--text-tertiary)" />
          </Link>
        ))}
      </div>

    </div>
  );
};

export default Dashboard;
