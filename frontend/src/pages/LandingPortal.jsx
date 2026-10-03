import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/client';
import {
  LayoutDashboard, MapPin, LineChart, Scale, AlertTriangle,
  Sliders, Award, Database, ArrowRight, TrendingUp,
  Building, GraduationCap, Cpu, Zap, ChevronRight,
} from 'lucide-react';

const MODULES = [
  {
    to: '/dashboard', icon: LayoutDashboard, iconBg: '#eff6ff', iconColor: '#2563eb',
    tag: 'Macro Overview', title: 'Executive Dashboard',
    desc: 'High-level command center with aggregate demand/supply metrics and critical shortage lists.',
    features: ['Real-time KPI cards from API', 'Sector distribution charts', 'Top 5 critical urgency trades'],
  },
  {
    to: '/drilldown', icon: MapPin, iconBg: '#ecfdf5', iconColor: '#059669',
    tag: 'Granular Explorer', title: 'District & Trade Drill-down',
    desc: 'Navigate the full hierarchy: National → State → 30 Districts → 8 Sectors → 25 Trades.',
    features: ['30 Odisha districts live', 'Trade activity matrix', 'Economic tier classification'],
  },
  {
    to: '/forecast', icon: LineChart, iconBg: '#fffbeb', iconColor: '#d97706',
    tag: 'ML Projections', title: 'Forecasting Engine',
    desc: '2025–2028 projections powered by GradientBoostingRegressor with empirical confidence bounds.',
    features: ['4-year demand & supply forecast', '±12% confidence intervals', 'GBR vs Ridge model comparison'],
  },
  {
    to: '/skill-gaps', icon: Scale, iconBg: '#fef2f2', iconColor: '#dc2626',
    tag: 'Deficit Indexing', title: 'Skill Gap Intelligence',
    desc: 'Normalized gap classification (Shortage · Oversupply · Balanced) with 0–100 severity scores.',
    features: ['Top 10 acute shortages', 'Oversupply re-balancing list', 'Feature-driven diagnostics'],
  },
  {
    to: '/early-warning', icon: AlertTriangle, iconBg: '#fdf2f8', iconColor: '#db2777',
    tag: 'Proactive Alerts', title: 'Early Warning System',
    desc: 'Identifies upcoming bottleneck years before market dislocations occur.',
    features: ['Emerging shortage & oversupply', 'Critical year calculation', '6–12 month lead-time alerts'],
  },
  {
    to: '/simulator', icon: Sliders, iconBg: '#e0e7ff', iconColor: '#4338ca',
    tag: 'Key Innovation', title: 'What-If Simulator',
    desc: 'Test policy interventions with interactive sliders. Real-time gap recalculation from the API.',
    features: ['+Seats / +Intake / +Retention knobs', 'Multi-year comparison timeline', 'AI policy narrative summary'],
    featured: true,
  },
];

const JOURNEY = [
  {
    to: '/dashboard', step: 'Step 1', icon: LayoutDashboard, iconBg: '#eff6ff', iconColor: '#2563eb',
    title: 'Check Executive Health',
    desc: 'Review state-level shortages, surplus counts, and multi-year macro trends.',
  },
  {
    to: '/drilldown', step: 'Step 2', icon: MapPin, iconBg: '#ecfdf5', iconColor: '#059669',
    title: 'Drill Into Districts',
    desc: 'Select any of 30 Odisha districts and filter by sector and trade.',
  },
  {
    to: '/forecast', step: 'Step 3', icon: LineChart, iconBg: '#fffbeb', iconColor: '#d97706',
    title: 'Inspect AI Forecasts',
    desc: 'See 2025–2028 projections with 95% confidence bands and model metrics.',
  },
  {
    to: '/simulator', step: 'Step 4 ✦', icon: Sliders, iconBg: '#e0e7ff', iconColor: '#4338ca',
    title: 'Simulate Interventions',
    desc: 'Use sliders (+seats, +intake, +retention) to test gap reduction policies.',
  },
];

const ROLES = [
  {
    icon: Building, iconBg: '#eff6ff', iconColor: '#2563eb',
    role: 'Policy Maker / Govt Officer',
    desc: 'Approves vocational budgets, sanctions ITI seats, plans multi-year skill missions.',
    steps: [
      { label: 'Early Warning', note: 'for upcoming shortages' },
      { label: 'What-If Simulator', note: 'to test adding seats' },
      { label: 'Data Sources', note: 'to export sanitized reports' },
    ],
    to: '/simulator', linkLabel: 'Go to Simulator',
  },
  {
    icon: TrendingUp, iconBg: '#ecfdf5', iconColor: '#059669',
    role: 'Labour Market Analyst',
    desc: 'Evaluates demand-supply elasticities, validates ML backtesting results.',
    steps: [
      { label: 'Market Intelligence', note: 'for decomposed signal weights' },
      { label: 'AI Model Evaluation', note: 'for MAE/RMSE benchmarks' },
      { label: 'Forecast Engine', note: 'for confidence interval review' },
    ],
    to: '/market', linkLabel: 'Go to Market Intel',
  },
  {
    icon: GraduationCap, iconBg: '#fffbeb', iconColor: '#d97706',
    role: 'Training Institute / ITI Head',
    desc: 'Manages curriculum, enrolment capacity, passouts, and local placement absorption.',
    steps: [
      { label: 'District Drill-down', note: 'to locate your district' },
      { label: 'Skill Gaps', note: 'to avoid oversupplied trades' },
      { label: 'Critical Shortages', note: 'to target curriculum' },
    ],
    to: '/drilldown', linkLabel: 'Go to District Explorer',
  },
];

export const LandingPortal = () => {
  const [stats, setStats] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/overview')
      .then((r) => setStats(r.data))
      .catch(() => {});
  }, []);

  return (
    <div className="landing-wrapper">

      {/* ── HERO ─────────────────────────────────────── */}
      <div className="landing-hero">
        <div className="hero-badge">
          <span className="dot" />
          PILOT DEPLOYMENT: ODISHA (30 DISTRICTS) · SIH PS 26246
        </div>

        <h1 className="hero-title">
          AI-Enabled <span className="highlight">Labour Market</span><br />
          Intelligence &amp; Skill Forecasting
        </h1>

        <p className="hero-desc">
          A decision intelligence platform that aggregates industrial demand signals,
          cross-references training capacities, forecasts 2025–2028 skill gaps, and
          enables evidence-based policy interventions.
        </p>

        <div className="hero-cta-row">
          <Link to="/dashboard" className="hero-cta-primary">
            Open Executive Dashboard <ArrowRight size={16} />
          </Link>
          <Link to="/simulator" className="hero-cta-secondary">
            <Sliders size={15} /> Launch What-If Simulator
          </Link>
        </div>

        {/* Live stats strip */}
        <div className="hero-stats-strip">
          <div className="hero-stat">
            <div className="hs-value">{stats?.total_districts ?? 30}</div>
            <div className="hs-label">Districts Monitored</div>
          </div>
          <div className="hero-stat">
            <div className="hs-value">{stats?.monitored_sectors ?? 8}</div>
            <div className="hs-label">Industry Sectors</div>
          </div>
          <div className="hero-stat">
            <div className="hs-value">{stats?.monitored_trades ?? 25}</div>
            <div className="hs-label">NSQF Trades</div>
          </div>
          <div className="hero-stat">
            <div className="hs-value primary">
              {stats ? stats.total_annual_demand.toLocaleString() : '160,952'}
            </div>
            <div className="hs-label">Total Labour Demand</div>
          </div>
          <div className="hero-stat">
            <div className="hs-value danger">
              {stats?.total_shortage_zones ?? '—'}
            </div>
            <div className="hs-label">Shortage Zones</div>
          </div>
        </div>
      </div>

      {/* ── 4-STEP GUIDED JOURNEY ─────────────────── */}
      <div className="journey-section">
        <div className="section-header-block" style={{ marginBottom: 20 }}>
          <span className="section-eyebrow">Assisted Workflow</span>
          <h2 className="section-title">How to navigate this platform</h2>
          <p className="section-subtitle">Follow this 4-step path to analyse deficits and simulate policies</p>
        </div>

        <div className="journey-grid">
          {JOURNEY.map((s) => {
            const Icon = s.icon;
            return (
              <Link key={s.to} to={s.to} className="journey-step">
                <div className="step-number">{s.step}</div>
                <div className="step-icon" style={{ background: s.iconBg, color: s.iconColor }}>
                  <Icon size={18} />
                </div>
                <h3>{s.title}</h3>
                <p>{s.desc}</p>
                <div className="step-go">
                  Explore <ChevronRight size={13} />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* ── MODULE CATALOG ────────────────────────── */}
      <div className="modules-section">
        <div className="section-header-block" style={{ marginBottom: 20 }}>
          <span className="section-eyebrow">Module Catalog</span>
          <h2 className="section-title">Dedicated analytics &amp; decision modules</h2>
          <p className="section-subtitle">Each module is self-contained with clear filters and evidence-based metrics</p>
        </div>

        <div className="modules-grid">
          {MODULES.map((m) => {
            const Icon = m.icon;
            return (
              <Link key={m.to} to={m.to} className={`module-card${m.featured ? ' featured' : ''}`}>
                <div className="module-card-top">
                  <div className="module-icon" style={{ background: m.iconBg, color: m.iconColor }}>
                    <Icon size={20} />
                  </div>
                  <span className={`module-tag${m.featured ? ' featured-tag' : ''}`}>{m.tag}</span>
                </div>
                <h3>{m.title}</h3>
                <p>{m.desc}</p>
                <ul className="module-features">
                  {m.features.map((f, i) => <li key={i}>{f}</li>)}
                </ul>
                <div className="module-footer">
                  <span>Open Module</span>
                  <ArrowRight size={14} />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* ── ROLE-BASED GUIDANCE ───────────────────── */}
      <div>
        <div className="section-header-block" style={{ marginBottom: 20 }}>
          <span className="section-eyebrow">Persona-Based Guides</span>
          <h2 className="section-title">Assisted guidance by user role</h2>
          <p className="section-subtitle">Select your role to see a tailored navigation workflow</p>
        </div>

        <div className="roles-grid">
          {ROLES.map((r) => {
            const Icon = r.icon;
            return (
              <div key={r.role} className="role-card">
                <div className="role-header">
                  <div className="role-icon" style={{ background: r.iconBg, color: r.iconColor }}>
                    <Icon size={18} />
                  </div>
                  <h4>{r.role}</h4>
                </div>
                <p>{r.desc}</p>
                <div className="role-steps">
                  {r.steps.map((s, i) => (
                    <div key={i} className="role-step">
                      {i + 1}. <strong>{s.label}</strong> — {s.note}
                    </div>
                  ))}
                </div>
                <Link to={r.to} className="role-link">
                  {r.linkLabel} <ChevronRight size={13} />
                </Link>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
};

export default LandingPortal;
