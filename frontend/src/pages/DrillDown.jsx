import React, { useEffect, useState } from 'react';
import api from '../api/client';
import StatusBadge from '../components/common/StatusBadge';
import UrgencyBadge from '../components/common/UrgencyBadge';
import AssistedGuide from '../components/common/AssistedGuide';
import { MapPin, Search, ChevronRight, Layers, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DrillDown = () => {
  const [districts, setDistricts] = useState([]);
  const [selectedDistrictId, setSelectedDistrictId] = useState(1);
  const [activeTrades, setActiveTrades] = useState([]);
  const [districtGaps, setDistrictGaps] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDistricts();
  }, []);

  useEffect(() => {
    if (selectedDistrictId) {
      loadDistrictData(selectedDistrictId);
    }
  }, [selectedDistrictId]);

  const loadDistricts = async () => {
    try {
      const res = await api.get('/states/1/districts');
      setDistricts(res.data);
      if (res.data.length > 0) {
        setSelectedDistrictId(res.data[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const loadDistrictData = async (distId) => {
    try {
      setLoading(true);
      const [tradesRes, gapsRes] = await Promise.all([
        api.get(`/districts/${distId}/trades`),
        api.get(`/skill-gaps?district_id=${distId}&year=2024&limit=50`),
      ]);
      setActiveTrades(tradesRes.data);
      setDistrictGaps(gapsRes.data.items);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectedDistrict = districts.find((d) => d.id === selectedDistrictId);

  const filteredGaps = districtGaps.filter((g) =>
    g.trade_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    g.sector_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      <AssistedGuide
        title="District & Trade Drill-down Guide"
        purpose="Explore localized skill balances across all 30 districts in Odisha down to specific NSQF trade qualifications."
        steps={[
          { bold: 'Select District', desc: 'Click any district in the left menu (e.g. Khordha, Cuttack, Ganjam).' },
          { bold: 'Inspect Trade Balances', desc: 'Check the Net Gap (+ for shortage, - for surplus) and Severity Score.' },
          { bold: 'Forecast Trajectory', desc: 'Click the "Forecast" link in any row to see ML projections for 2025–2028.' },
        ]}
        nextActionLabel="View Forecasting Engine"
        nextActionTo="/forecast"
      />
      <div className="page-header">
        <h1 className="page-title">District & Trade Drill-down</h1>
        <p className="page-subtitle">
          Granular intelligence down to district, sector, and individual qualification trades
        </p>
      </div>

      {/* Hierarchy Breadcrumb Banner */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: '#ffffff',
          border: '1px solid #e2e8f0',
          padding: '12px 18px',
          borderRadius: '10px',
          marginBottom: '20px',
          fontSize: '13px',
          fontWeight: 600,
        }}
      >
        <span style={{ color: '#64748b' }}>India (National)</span>
        <ChevronRight size={14} color="#94a3b8" />
        <span style={{ color: '#64748b' }}>Odisha (State)</span>
        <ChevronRight size={14} color="#94a3b8" />
        <span style={{ color: '#2563eb' }}>{selectedDistrict?.name || 'District'}</span>
        <span className="badge" style={{ marginLeft: 'auto', background: '#f1f5f9', color: '#475569' }}>
          Tier: {selectedDistrict?.economic_tier || 'Tier-2'}
        </span>
      </div>

      {/* Main Grid: District Selector Sidebar + Trade Table */}
      <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: '20px' }}>
        {/* District List Sidebar */}
        <div className="card" style={{ padding: '16px', maxHeight: '720px', overflowY: 'auto' }}>
          <div style={{ fontSize: '13px', fontWeight: 700, color: '#334155', marginBottom: '12px' }}>
            Odisha Districts (30 Monitored)
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {districts.map((d) => {
              const isSelected = d.id === selectedDistrictId;
              return (
                <button
                  key={d.id}
                  onClick={() => setSelectedDistrictId(d.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '9px 12px',
                    borderRadius: '8px',
                    border: isSelected ? '1px solid #2563eb' : '1px solid transparent',
                    background: isSelected ? '#eff6ff' : 'transparent',
                    color: isSelected ? '#1d4ed8' : '#334155',
                    fontWeight: isSelected ? 700 : 500,
                    fontSize: '13px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.15s',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <MapPin size={14} color={isSelected ? '#2563eb' : '#94a3b8'} />
                    <span>{d.name}</span>
                  </div>
                  <span style={{ fontSize: '10.5px', color: '#94a3b8' }}>{d.economic_tier}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected District Trade Dossier */}
        <div>
          {/* District Summary Card */}
          <div className="card" style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <h2 style={{ fontSize: '20px', fontWeight: 800, color: '#0f172a' }}>
                  {selectedDistrict?.name} District Intelligence Profile
                </h2>
                <div style={{ fontSize: '13px', color: '#64748b', marginTop: '2px' }}>
                  Lat: {selectedDistrict?.latitude}° N • Lon: {selectedDistrict?.longitude}° E • Population: {selectedDistrict?.population_lakhs || '—'} Lakhs
                </div>
              </div>

              {/* Search Box */}
              <div style={{ position: 'relative', minWidth: '240px' }}>
                <Search size={14} style={{ position: 'absolute', left: '10px', top: '10px', color: '#94a3b8' }} />
                <input
                  type="text"
                  placeholder="Filter trades or sectors..."
                  className="form-input"
                  style={{ paddingLeft: '32px', fontSize: '12.5px' }}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Trade Gap Table */}
          <div className="card">
            <div className="card-title">
              <span>Monitored Trades in {selectedDistrict?.name} (2024 Reference)</span>
              <span style={{ fontSize: '12px', color: '#64748b' }}>{filteredGaps.length} Active Profiles</span>
            </div>

            {loading ? (
              <div className="loading-box">Loading district trades...</div>
            ) : filteredGaps.length === 0 ? (
              <div style={{ padding: '30px', textAlign: 'center', color: '#94a3b8' }}>
                No trades match the current filter in this district.
              </div>
            ) : (
              <div className="table-responsive">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Trade / Occupation</th>
                      <th>Sector</th>
                      <th>Demand</th>
                      <th>Supply</th>
                      <th>Net Gap</th>
                      <th>Status</th>
                      <th>Severity</th>
                      <th>Urgency</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredGaps.map((item) => (
                      <tr key={item.id}>
                        <td>
                          <strong>{item.trade_name}</strong>
                        </td>
                        <td>{item.sector_name}</td>
                        <td>{item.demand_value.toLocaleString()}</td>
                        <td>{item.supply_value.toLocaleString()}</td>
                        <td
                          style={{
                            fontWeight: 700,
                            color: item.net_gap > 0 ? '#dc2626' : item.net_gap < 0 ? '#d97706' : '#16a34a',
                          }}
                        >
                          {item.net_gap > 0 ? `+${item.net_gap.toLocaleString()}` : item.net_gap.toLocaleString()}
                        </td>
                        <td><StatusBadge status={item.status} /></td>
                        <td style={{ minWidth: '100px' }}>
                          <span style={{ fontWeight: 700, fontSize: '12px' }}>{item.severity_score}</span>
                          <div className="severity-bar-bg">
                            <div
                              className="severity-bar-fill"
                              style={{
                                width: `${item.severity_score}%`,
                                backgroundColor: item.severity_score > 70 ? '#ef4444' : item.severity_score > 40 ? '#f59e0b' : '#10b981',
                              }}
                            />
                          </div>
                        </td>
                        <td><UrgencyBadge tier={item.urgency_tier} /></td>
                        <td>
                          <Link
                            to={`/app/forecast`}
                            style={{
                              fontSize: '11px',
                              fontWeight: 700,
                              color: '#2563eb',
                              textDecoration: 'none',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '2px',
                            }}
                          >
                            Forecast <ArrowRight size={12} />
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DrillDown;
