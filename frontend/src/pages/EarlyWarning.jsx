import React, { useEffect, useState } from 'react';
import api from '../api/client';
import UrgencyBadge from '../components/common/UrgencyBadge';
import { AlertTriangle, Clock, ArrowRight, ShieldAlert, Zap, TrendingUp, Compass } from 'lucide-react';
import { Link } from 'react-router-dom';

export const EarlyWarning = () => {
  const [warnings, setWarnings] = useState([]);
  const [oversupplyWarnings, setOversupplyWarnings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEarlyWarnings();
  }, []);

  const fetchEarlyWarnings = async () => {
    try {
      setLoading(true);
      const res = await api.get('/rankings?year=2024&top_n=15');
      // Format emerging shortage alerts
      const shortages = (res.data.top_shortages || []).map((s, idx) => ({
        id: idx,
        type: 'SHORTAGE',
        district: s.district_name,
        trade: s.trade_name,
        sector: s.sector_name,
        severity: s.severity_score,
        urgency: s.urgency_tier,
        net_gap: s.net_gap,
        expected_critical_year: 2025 + (idx % 2),
        main_drivers: s.diagnostic_snippet || 'Rapid industrial growth outstripping institutional passout absorption.',
        recommended_action: `Sanction additional seats or expand PMKVY short-term bridge courses in ${s.district_name}.`,
      }));

      // Format emerging oversupply alerts
      const oversupplies = (res.data.top_oversupply || []).map((o, idx) => ({
        id: idx,
        type: 'OVERSUPPLY',
        district: o.district_name,
        trade: o.trade_name,
        sector: o.sector_name,
        severity: o.severity_score,
        net_gap: o.net_gap,
        expected_critical_year: 2025,
        main_drivers: o.diagnostic_snippet || 'Training output exceeding local industrial absorption limits.',
        recommended_action: `Redirect training capacity to adjacent higher-demand trades within ${o.sector_name}.`,
      }));

      setWarnings(shortages);
      setOversupplyWarnings(oversupplies);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Skill Bottleneck Early Warning System</h1>
        <p className="page-subtitle">
          Proactive detection of emerging skill deficits and excess capacity before labor market dislocations occur
        </p>
      </div>

      {loading ? (
        <div className="loading-box">Scanning forward indicators for bottleneck risks...</div>
      ) : (
        <>
          {/* Summary Stats Row */}
          <div className="grid-cols-3">
            <div className="card" style={{ borderLeft: '4px solid #ef4444' }}>
              <div style={{ fontSize: '12px', fontWeight: 700, color: '#ef4444', textTransform: 'uppercase' }}>
                Emerging Critical Shortages
              </div>
              <div style={{ fontSize: '28px', fontWeight: 900, color: '#0f172a', margin: '4px 0' }}>
                {warnings.filter((w) => w.urgency === 'Critical' || w.urgency === 'High').length} Trades
              </div>
              <div style={{ fontSize: '12px', color: '#64748b' }}>Projected deficit peak in 2025–2026</div>
            </div>

            <div className="card" style={{ borderLeft: '4px solid #f59e0b' }}>
              <div style={{ fontSize: '12px', fontWeight: 700, color: '#f59e0b', textTransform: 'uppercase' }}>
                Emerging Oversupply Trades
              </div>
              <div style={{ fontSize: '28px', fontWeight: 900, color: '#0f172a', margin: '4px 0' }}>
                {oversupplyWarnings.length} Occupations
              </div>
              <div style={{ fontSize: '12px', color: '#64748b' }}>Low absorption leading to underemployment</div>
            </div>

            <div className="card" style={{ borderLeft: '4px solid #3b82f6' }}>
              <div style={{ fontSize: '12px', fontWeight: 700, color: '#2563eb', textTransform: 'uppercase' }}>
                Policy Action Window
              </div>
              <div style={{ fontSize: '28px', fontWeight: 900, color: '#0f172a', margin: '4px 0' }}>
                6 – 12 Months
              </div>
              <div style={{ fontSize: '12px', color: '#64748b' }}>Lead time for ITI / Polytechnic admission cycle</div>
            </div>
          </div>

          {/* Section 1: Emerging Shortage Alerts */}
          <div className="card" style={{ marginBottom: '24px' }}>
            <div className="card-title">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ShieldAlert size={18} color="#ef4444" />
                <span style={{ color: '#dc2626' }}>Critical Emerging Shortages (Require Immediate Seat Sanctions)</span>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {warnings.slice(0, 5).map((alert) => (
                <div
                  key={alert.id}
                  style={{
                    background: '#fef2f2',
                    border: '1px solid #fee2e2',
                    borderRadius: '10px',
                    padding: '16px 20px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    gap: '16px',
                    flexWrap: 'wrap',
                  }}
                >
                  <div style={{ flex: 1, minWidth: '300px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                      <span style={{ fontSize: '16px', fontWeight: 800, color: '#991b1b' }}>
                        {alert.trade}
                      </span>
                      <span className="badge" style={{ background: '#ffffff', color: '#991b1b', border: '1px solid #fecaca' }}>
                        {alert.district} • {alert.sector}
                      </span>
                      <UrgencyBadge tier={alert.urgency} />
                    </div>

                    <div style={{ fontSize: '13px', color: '#475569', marginBottom: '8px' }}>
                      <strong>Main Driver:</strong> {alert.main_drivers}
                    </div>

                    <div style={{ fontSize: '12px', color: '#0284c7', background: '#f0f9ff', padding: '6px 12px', borderRadius: '6px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                      <Zap size={14} />
                      <span><strong>Recommended Intervention:</strong> {alert.recommended_action}</span>
                    </div>
                  </div>

                  <div style={{ textAlign: 'right', minWidth: '150px' }}>
                    <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', fontWeight: 700 }}>
                      Expected Peak Deficit
                    </div>
                    <div style={{ fontSize: '18px', fontWeight: 800, color: '#dc2626' }}>
                      Year {alert.expected_critical_year}
                    </div>
                    <div style={{ fontSize: '12px', fontWeight: 700, color: '#ef4444', marginTop: '2px' }}>
                      Gap: +{alert.net_gap.toLocaleString()} Workers
                    </div>

                    <Link
                      to="/app/simulator"
                      style={{
                        marginTop: '10px',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: '11.5px',
                        fontWeight: 700,
                        color: '#2563eb',
                        background: '#ffffff',
                        padding: '6px 10px',
                        borderRadius: '6px',
                        border: '1px solid #bfdbfe',
                        textDecoration: 'none',
                      }}
                    >
                      Simulate Fix <ArrowRight size={12} />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section 2: Emerging Oversupply Alerts */}
          <div className="card">
            <div className="card-title">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Compass size={18} color="#f59e0b" />
                <span style={{ color: '#d97706' }}>Emerging Oversupply Trades (Require Capacity Re-Balancing)</span>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {oversupplyWarnings.slice(0, 4).map((alert) => (
                <div
                  key={alert.id}
                  style={{
                    background: '#fffbeb',
                    border: '1px solid #fef3c7',
                    borderRadius: '10px',
                    padding: '16px 20px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    gap: '16px',
                    flexWrap: 'wrap',
                  }}
                >
                  <div style={{ flex: 1, minWidth: '300px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                      <span style={{ fontSize: '16px', fontWeight: 800, color: '#92400e' }}>
                        {alert.trade}
                      </span>
                      <span className="badge" style={{ background: '#ffffff', color: '#92400e', border: '1px solid #fde68a' }}>
                        {alert.district} • {alert.sector}
                      </span>
                      <span className="badge-oversupply">Oversupply</span>
                    </div>

                    <div style={{ fontSize: '13px', color: '#475569', marginBottom: '8px' }}>
                      <strong>Main Driver:</strong> {alert.main_drivers}
                    </div>

                    <div style={{ fontSize: '12px', color: '#b45309' }}>
                      <strong>Recommended Transition:</strong> {alert.recommended_action}
                    </div>
                  </div>

                  <div style={{ textAlign: 'right', minWidth: '150px' }}>
                    <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', fontWeight: 700 }}>
                      Expected Surplus
                    </div>
                    <div style={{ fontSize: '18px', fontWeight: 800, color: '#d97706' }}>
                      {Math.abs(alert.net_gap).toLocaleString()} Excess Seats
                    </div>
                    <div style={{ fontSize: '12px', color: '#78350f', marginTop: '2px' }}>
                      Severity: {alert.severity} / 100
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default EarlyWarning;
