import React, { useEffect, useState } from 'react';
import api from '../api/client';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';
import { Award, CheckCircle, Info, BrainCircuit, Activity } from 'lucide-react';

export const ModelEvaluation = () => {
  const [evalData, setEvalData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchEvaluation();
  }, []);

  const fetchEvaluation = async () => {
    try {
      setLoading(true);
      const res = await api.get('/model-evaluation');
      setEvalData(res.data);
    } catch (err) {
      setError('Failed to load model evaluation metrics from backend.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading-box">Loading model evaluation telemetry and feature importances...</div>;
  }

  if (error) {
    return <div className="error-box">{error}</div>;
  }

  if (!evalData) return null;

  // Extract primary model's feature importances for charting
  const primaryModel = evalData.models.find((m) => m.is_primary_model) || evalData.models[0];
  const featureChartData = (primaryModel?.feature_importances || []).map((f) => ({
    feature: f.feature,
    importance_pct: Math.round(f.importance * 100),
  }));

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">AI / Model Intelligence & Audit</h1>
        <p className="page-subtitle">
          Empirical evaluation metrics, time-aware backtesting validation, and transparent feature attribution
        </p>
      </div>

      {/* Model Split Strategy Banner */}
      <div
        style={{
          background: '#ffffff',
          border: '1px solid #e2e8f0',
          borderRadius: '12px',
          padding: '16px 20px',
          marginBottom: '24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <BrainCircuit size={22} color="#2563eb" />
          <div>
            <div style={{ fontSize: '12px', color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>
              Validation Strategy
            </div>
            <div style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a' }}>
              {evalData.data_split_strategy}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '12px', color: '#64748b' }}>Primary Production Model:</span>
          <span className="badge" style={{ background: '#dbeafe', color: '#1e40af', fontSize: '13px', padding: '4px 10px' }}>
            ★ {evalData.primary_model_name}
          </span>
        </div>
      </div>

      {/* Model Benchmark Leaderboard Card */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-title">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Award size={18} color="#2563eb" />
            <span>Forecasting Model Performance Leaderboard</span>
          </div>
          <span style={{ fontSize: '11.5px', color: '#64748b' }}>Held-out Test Split: Year 2024</span>
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Model Architecture</th>
                <th>Role</th>
                <th>MAE (Mean Abs Error)</th>
                <th>RMSE (Root Mean Sq Error)</th>
                <th>MAPE (%)</th>
                <th>R² Score</th>
                <th>Training / Test Split</th>
                <th>Operational Notes</th>
              </tr>
            </thead>
            <tbody>
              {evalData.models.map((m, i) => (
                <tr key={i} style={{ background: m.is_primary_model ? '#eff6ff' : 'transparent' }}>
                  <td>
                    <strong>{m.model_name}</strong>
                  </td>
                  <td>
                    {m.is_primary_model ? (
                      <span className="badge" style={{ background: '#2563eb', color: 'white' }}>
                        Primary Engine
                      </span>
                    ) : (
                      <span style={{ fontSize: '12px', color: '#64748b' }}>Benchmark Baseline</span>
                    )}
                  </td>
                  <td><strong>{m.mae}</strong></td>
                  <td style={{ fontWeight: 800, color: m.is_primary_model ? '#1d4ed8' : '#334155' }}>
                    {m.rmse}
                  </td>
                  <td>{m.mape !== null ? `${m.mape}%` : 'N/A'}</td>
                  <td>
                    <span style={{ fontWeight: 800, color: m.r2_score > 0.85 ? '#16a34a' : '#d97706' }}>
                      {m.r2_score}
                    </span>
                  </td>
                  <td style={{ fontSize: '12px', color: '#64748b' }}>
                    Train: {m.train_years} | Test: {m.test_year}
                  </td>
                  <td style={{ fontSize: '12px', color: '#475569', maxWidth: '300px' }}>
                    {m.notes}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Feature Importance & Methodology Row */}
      <div className="grid-cols-2">
        {/* Feature Importance Chart */}
        <div className="card">
          <div className="card-title">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={18} color="#2563eb" />
              <span>Feature Importance ({primaryModel?.model_name})</span>
            </div>
            <span style={{ fontSize: '11.5px', color: '#64748b' }}>Gini / Impurity Contribution</span>
          </div>

          <div style={{ height: '280px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={featureChartData}
                layout="vertical"
                margin={{ top: 10, right: 30, bottom: 10, left: 40 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" unit="%" stroke="#94a3b8" />
                <YAxis dataKey="feature" type="category" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val) => `${val}% contribution`}
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
                />
                <Bar dataKey="importance_pct" name="Importance" fill="#2563eb" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Methodology & Data Honesty Protocol */}
        <div className="card">
          <div className="card-title">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle size={18} color="#10b981" />
              <span>Methodology & Audit Protocol</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {evalData.methodology_notes.map((note, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '12.5px', color: '#334155' }}>
                <span style={{ color: '#2563eb', fontWeight: 800 }}>•</span>
                <span>{note}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelEvaluation;
