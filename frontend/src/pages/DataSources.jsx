import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { Database, Download, ExternalLink, ShieldCheck, FileSpreadsheet, FileJson, AlertCircle } from 'lucide-react';

export const DataSources = () => {
  const [sourcesData, setSourcesData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    fetchDataSources();
  }, []);

  const fetchDataSources = async () => {
    try {
      setLoading(true);
      const res = await api.get('/data-sources');
      setSourcesData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (format) => {
    setExporting(true);
    // Direct link trigger for file download
    window.open(`/api/export?format=${format}`, '_blank');
    setExporting(false);
  };

  if (loading) {
    return <div className="loading-box">Loading dataset coverage inventory...</div>;
  }

  if (!sourcesData) return null;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Data Sources, Coverage & Export</h1>
        <p className="page-subtitle">
          Complete attribution of open government portals, synthetic pilot calibrations, and policy data export tools
        </p>
      </div>

      {/* Prominent Data Honesty Statement Banner */}
      <div
        style={{
          background: '#fffbeb',
          border: '1px solid #fef3c7',
          borderLeft: '5px solid #f59e0b',
          borderRadius: '10px',
          padding: '18px 22px',
          marginBottom: '24px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#b45309', fontWeight: 800, fontSize: '13px', textTransform: 'uppercase', marginBottom: '6px' }}>
          <AlertCircle size={18} />
          <span>SIH 26246 Mandatory Data Honesty Declaration</span>
        </div>
        <div style={{ fontSize: '13.5px', color: '#78350f', lineHeight: '1.6' }}>
          {sourcesData.data_honesty_statement}
        </div>
      </div>

      {/* Dataset Summary Cards */}
      <div className="grid-cols-3">
        <div className="card">
          <div className="card-title">Covered Data Sources</div>
          <div style={{ fontSize: '32px', fontWeight: 900, color: '#0f172a' }}>
            {sourcesData.sources.length} Portals
          </div>
          <div style={{ fontSize: '12px', color: '#64748b' }}>
            {sourcesData.synthetic_sources_count} Calibrated Pilot • {sourcesData.real_sources_count} Official Taxonomy
          </div>
        </div>

        <div className="card">
          <div className="card-title">Total Records in Pilot DB</div>
          <div style={{ fontSize: '32px', fontWeight: 900, color: '#2563eb' }}>
            {sourcesData.total_records_in_db.toLocaleString()}
          </div>
          <div style={{ fontSize: '12px', color: '#64748b' }}>
            2018–2024 Multi-Year Historical Baseline
          </div>
        </div>

        <div className="card">
          <div className="card-title">Direct Policy Data Export</div>
          <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
            <button
              onClick={() => handleExport('json')}
              className="auth-btn-primary"
              style={{ padding: '8px 14px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px', margin: 0 }}
            >
              <FileJson size={16} /> JSON Export
            </button>
            <button
              onClick={() => handleExport('csv')}
              style={{
                background: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                padding: '8px 14px',
                fontSize: '12px',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <FileSpreadsheet size={16} /> CSV Export
            </button>
          </div>
          <div style={{ fontSize: '11px', color: '#64748b', marginTop: '8px' }}>
            One-click download of skill gaps & forecast vectors
          </div>
        </div>
      </div>

      {/* Data Source Inventory Table */}
      <div className="card">
        <div className="card-title">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Database size={18} color="#2563eb" />
            <span>Official Government Data Sources & Pilot Calibration Attribution</span>
          </div>
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Data Source Portal</th>
                <th>Category</th>
                <th>Years Covered</th>
                <th>Geographic Scope</th>
                <th>Coverage Scope</th>
                <th>Record Volume</th>
                <th>Data Type</th>
                <th>Attribution / Documentation Notes</th>
              </tr>
            </thead>
            <tbody>
              {sourcesData.sources.map((s) => (
                <tr key={s.id}>
                  <td>
                    <div style={{ fontWeight: 700, color: '#0f172a' }}>{s.source_name}</div>
                    {s.source_url && (
                      <a
                        href={s.source_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{ fontSize: '11px', color: '#2563eb', display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                      >
                        {s.source_url} <ExternalLink size={10} />
                      </a>
                    )}
                  </td>
                  <td>
                    <span className="badge" style={{ background: '#f1f5f9', color: '#334155' }}>
                      {s.category}
                    </span>
                  </td>
                  <td><strong>{s.years_covered}</strong></td>
                  <td>{s.states_covered}</td>
                  <td style={{ fontSize: '12px', color: '#475569' }}>
                    {s.districts_covered > 0 ? `${s.districts_covered} Districts • ` : ''}
                    {s.sectors_covered > 0 ? `${s.sectors_covered} Sectors` : 'National'}
                  </td>
                  <td><strong>{s.record_count.toLocaleString()}</strong></td>
                  <td>
                    {s.is_synthetic ? (
                      <span className="badge-shortage" style={{ background: '#fee2e2', color: '#991b1b', border: '1px solid #fecaca' }}>
                        Calibrated Pilot
                      </span>
                    ) : (
                      <span className="badge-balanced">Official Open Data</span>
                    )}
                  </td>
                  <td style={{ fontSize: '12px', color: '#475569', maxWidth: '340px' }}>
                    {s.notes}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DataSources;
