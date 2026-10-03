import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { LogOut } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const PAGE_TITLES = {
  '/app/dashboard': 'Executive Dashboard',
  '/app/market': 'Labour Market Intelligence',
  '/app/drilldown': 'District & Trade Drill-down',
  '/app/forecast': 'Forecasting Engine',
  '/app/skill-gaps': 'Skill Gap Intelligence',
  '/app/early-warning': 'Early Warning System',
  '/app/simulator': 'What-If Simulator',
  '/app/model-evaluation': 'AI Model Evaluation',
  '/app/data-sources': 'Data Sources & Export',
};

export const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const pageTitle = PAGE_TITLES[location.pathname] || 'Analytics';

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="topbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 11, color: 'var(--text-tertiary)', fontWeight: 500 }}>SkillSetu AI</span>
        <span style={{ color: 'var(--text-tertiary)', fontSize: 13 }}>/</span>
        <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text)' }}>{pageTitle}</span>
      </div>

      <div className="topbar-right">
        {user ? (
          <>
            <div className="user-profile-badge">
              <div className="user-avatar">
                {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
              </div>
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text)' }}>
                  {user.full_name || user.email}
                </div>
                <div style={{ fontSize: 10.5, color: 'var(--text-secondary)' }}>
                  {user.organization || 'Government of Odisha'}
                </div>
              </div>
              <span className="user-role-pill">{user.role || 'Analyst'}</span>
            </div>

            <button
              onClick={handleLogout}
              style={{
                display: 'flex', alignItems: 'center', gap: 6,
                padding: '6px 12px', borderRadius: 8,
                border: '1px solid var(--border)',
                background: 'transparent', color: 'var(--text-secondary)',
                fontSize: 12.5, fontWeight: 500, cursor: 'pointer',
                transition: 'all 0.18s', fontFamily: 'inherit',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = '#f3f4f6'; e.currentTarget.style.color = 'var(--text)'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-secondary)'; }}
            >
              <LogOut size={13} /> Logout
            </button>
          </>
        ) : (
          <button
            onClick={() => navigate('/login')}
            style={{
              background: 'var(--primary)', color: 'white',
              border: 'none', borderRadius: 8,
              padding: '7px 16px', fontSize: 13, fontWeight: 600,
              cursor: 'pointer', fontFamily: 'inherit',
            }}
          >
            Sign In
          </button>
        )}
      </div>
    </header>
  );
};

export default Navbar;
