import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, TrendingUp, MapPin,
  LineChart, Scale, AlertTriangle, Sliders, Award, Database,
} from 'lucide-react';

const NAV_SECTIONS = [
  {
    label: 'Labour Analytics',
    items: [
      { to: '/app/dashboard', label: 'Executive Dashboard', icon: LayoutDashboard },
      { to: '/app/market', label: 'Market Intelligence', icon: TrendingUp },
    ],
  },
  {
    label: 'Decision Intelligence',
    items: [
      { to: '/app/drilldown', label: 'District Drill-down', icon: MapPin },
      { to: '/app/forecast', label: 'Forecasting Engine', icon: LineChart },
      { to: '/app/skill-gaps', label: 'Skill Gap Matrix', icon: Scale },
      { to: '/app/early-warning', label: 'Early Warning', icon: AlertTriangle },
    ],
  },
  {
    label: 'Governance & Audit',
    items: [
      { to: '/app/simulator', label: 'What-If Simulator', icon: Sliders },
      { to: '/app/model-evaluation', label: 'AI Model Eval', icon: Award },
      { to: '/app/data-sources', label: 'Data Sources', icon: Database },
    ],
  },
];

export const Sidebar = () => (
  <aside className="sidebar">
    <div className="sidebar-brand">
      <div className="emblem">S</div>
      <div>
        <div className="brand-name">SkillSetu AI</div>
        <div className="brand-sub">SIH PS 26246</div>
      </div>
    </div>

    <nav className="sidebar-nav">
      {NAV_SECTIONS.map((section) => (
        <div key={section.label} style={{ marginBottom: 4 }}>
          <div className="sidebar-section-title">{section.label}</div>
          {section.items.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
              >
                <Icon size={16} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </div>
      ))}
    </nav>

    <div className="sidebar-footer">
      <div style={{ fontSize: 10.5, color: '#475569' }}>Pilot Geography</div>
      <div className="pilot-tag">Odisha · 30 Districts</div>
      <div style={{ fontSize: 10, color: '#334155', marginTop: 6 }}>v1.0.0 · AI-Driven Forecasting</div>
    </div>
  </aside>
);

export default Sidebar;
