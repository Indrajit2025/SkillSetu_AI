import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import AppLayout from './components/layout/AppLayout';

// Public pages (no sidebar)
import PublicLanding from './pages/PublicLanding';
import Login from './pages/Login';

// App pages (inside sidebar layout)
import Dashboard from './pages/Dashboard';
import MarketIntelligence from './pages/MarketIntelligence';
import DrillDown from './pages/DrillDown';
import Forecasting from './pages/Forecasting';
import SkillGaps from './pages/SkillGaps';
import EarlyWarning from './pages/EarlyWarning';
import Simulator from './pages/Simulator';
import ModelEvaluation from './pages/ModelEvaluation';
import DataSources from './pages/DataSources';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('App ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '40px', maxWidth: '600px', margin: '40px auto', background: '#fff', borderRadius: '12px', border: '1px solid #fee2e2', boxShadow: '0 4px 12px rgba(0,0,0,0.05)', textAlign: 'center' }}>
          <h2 style={{ color: '#dc2626', marginBottom: '12px' }}>Something went wrong</h2>
          <p style={{ color: '#64748b', fontSize: '14px', marginBottom: '20px' }}>
            {this.state.error?.message || 'An unexpected rendering error occurred.'}
          </p>
          <button
            onClick={() => { this.setState({ hasError: false }); window.location.href = '/app/dashboard'; }}
            style={{ background: '#2563eb', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer', fontWeight: 600 }}
          >
            Return to Dashboard
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export const App = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* ── PUBLIC ROUTES (no sidebar) ── */}
            <Route path="/" element={<PublicLanding />} />
            <Route path="/login" element={<Login />} />

            {/* ── AUTHENTICATED APP ROUTES (with sidebar) ── */}
            <Route path="/app" element={<AppLayout />}>
              <Route index element={<Navigate to="/app/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="market" element={<MarketIntelligence />} />
              <Route path="drilldown" element={<DrillDown />} />
              <Route path="forecast" element={<Forecasting />} />
              <Route path="skill-gaps" element={<SkillGaps />} />
              <Route path="early-warning" element={<EarlyWarning />} />
              <Route path="simulator" element={<Simulator />} />
              <Route path="model-evaluation" element={<ModelEvaluation />} />
              <Route path="data-sources" element={<DataSources />} />
            </Route>

            {/* Catch-all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
