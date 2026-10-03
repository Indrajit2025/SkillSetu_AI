import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/client';
import {
  ArrowRight, ShieldCheck, Cpu, LineChart, Sliders, MapPin, Scale, AlertTriangle, ChevronRight, HelpCircle, Layers, Award, Sparkles, CheckCircle2
} from 'lucide-react';

export const PublicLanding = () => {
  const [stats, setStats] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/overview')
      .then((r) => setStats(r.data))
      .catch(() => {});
  }, []);

  return (
    <div className="public-landing-container" style={{ background: '#fafafa', color: '#0f172a', minHeight: '100vh', fontFamily: "'Inter', sans-serif" }}>
      
      {/* ── STICKY TOPBAR ────────────────────────────────── */}
      <nav style={{
        position: 'sticky', top: 0, zIndex: 100, backdropFilter: 'blur(20px)', background: 'rgba(255, 255, 255, 0.85)',
        borderBottom: '1px solid #ea632422', padding: '0 32px', height: '64px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        boxShadow: '0 2px 10px rgba(0,0,0,0.03)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '34px', height: '34px', borderRadius: '10px', background: 'linear-gradient(135deg, #f97316 0%, #2563eb 100%)',
            display: 'flex', alignItems: 'center', justify: 'center', fontWeight: '800', fontSize: '17px', color: '#fff',
            boxShadow: '0 3px 10px rgba(249, 115, 22, 0.3)'
          }}>S</div>
          <span style={{ fontSize: '19px', fontWeight: '800', letterSpacing: '-0.5px', color: '#0f172a' }}>SkillSetu <span style={{ color: '#ea580c' }}>AI</span></span>
          <span style={{ background: '#fff7ed', color: '#c2410c', fontSize: '11px', fontWeight: '700', padding: '2px 9px', borderRadius: '12px', border: '1px solid #ffedd5' }}>SIH PS 26246</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '28px', fontSize: '14px', fontWeight: '500', color: '#475569' }}>
          <a href="#about" style={{ color: 'inherit', textDecoration: 'none', transition: 'color 0.2s' }}>About Platform</a>
          <a href="#architecture" style={{ color: 'inherit', textDecoration: 'none', transition: 'color 0.2s' }}>Architecture</a>
          <a href="#guide" style={{ color: 'inherit', textDecoration: 'none', transition: 'color 0.2s' }}>User Guide</a>
          <button 
            onClick={() => navigate('/login')}
            style={{
              background: 'linear-gradient(135deg, #ea580c 0%, #f97316 100%)', color: '#fff', border: 'none',
              padding: '9px 22px', borderRadius: '20px', fontWeight: '600', fontSize: '13.5px', cursor: 'pointer',
              boxShadow: '0 4px 14px rgba(234, 88, 12, 0.35)', transition: 'transform 0.2s, box-shadow 0.2s'
            }}
            onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-1px)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.transform = 'none'; }}
          >
            Access Portal
          </button>
        </div>
      </nav>

      {/* ── HERO SECTION ────────────────────────────────────────────── */}
      <section style={{ padding: '90px 24px 70px', textAlign: 'center', maxWidth: '1040px', margin: '0 auto' }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 16px', borderRadius: '30px',
          background: '#fff7ed', border: '1px solid #ffedd5', color: '#ea580c',
          fontSize: '12.5px', fontWeight: '600', marginBottom: '28px'
        }}>
          <Sparkles size={15} color="#ea580c" />
          <span>Empowering State-Level Labour Market Governance</span>
        </div>

        <h1 style={{
          fontSize: '60px', fontWeight: '900', letterSpacing: '-1.8px', lineHeight: '1.1',
          color: '#0f172a', marginBottom: '24px'
        }}>
          AI-Driven Labour Intelligence &amp; <span style={{ color: '#2563eb' }}>Skill Gap</span> <span style={{ color: '#ea580c' }}>Forecasting</span>
        </h1>

        <p style={{ fontSize: '19px', color: '#475569', lineHeight: '1.6', maxWidth: '780px', margin: '0 auto 40px', fontWeight: '400' }}>
          SkillSetu AI bridges the mismatch between industry labour demand signals and ITI/vocational supply capacities across 30 Odisha pilot districts through machine learning econometric modelling.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px' }}>
          <button 
            onClick={() => navigate('/login')}
            style={{
              background: '#2563eb', color: '#ffffff', border: 'none', padding: '14px 34px', borderRadius: '30px',
              fontWeight: '700', fontSize: '15px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px',
              boxShadow: '0 6px 20px rgba(37, 99, 235, 0.35)', transition: 'transform 0.2s'
            }}
          >
            Launch System Dashboard <ArrowRight size={16} />
          </button>
          <a 
            href="#guide"
            style={{
              background: '#ffffff', color: '#0f172a', border: '1px solid #cbd5e1',
              padding: '14px 30px', borderRadius: '30px', fontWeight: '600', fontSize: '15px', textDecoration: 'none',
              boxShadow: '0 2px 5px rgba(0,0,0,0.04)'
            }}
          >
            Explore User Guide
          </a>
        </div>

        {/* Live Empirical Stats Bar */}
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1px', background: '#e2e8f0',
          border: '1px solid #e2e8f0', borderRadius: '20px', marginTop: '64px', overflow: 'hidden',
          boxShadow: '0 10px 30px rgba(0,0,0,0.05)'
        }}>
          <div style={{ padding: '28px 24px', background: '#ffffff' }}>
            <div style={{ fontSize: '38px', fontWeight: '900', color: '#2563eb', letterSpacing: '-1px' }}>{stats?.total_districts || 30}</div>
            <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px', marginTop: '4px' }}>Districts Monitored</div>
          </div>
          <div style={{ padding: '28px 24px', background: '#ffffff' }}>
            <div style={{ fontSize: '38px', fontWeight: '900', color: '#ea580c', letterSpacing: '-1px' }}>{stats?.monitored_sectors || 8}</div>
            <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px', marginTop: '4px' }}>Priority Sectors</div>
          </div>
          <div style={{ padding: '28px 24px', background: '#ffffff' }}>
            <div style={{ fontSize: '38px', fontWeight: '900', color: '#d97706', letterSpacing: '-1px' }}>{stats?.monitored_trades || 25}</div>
            <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px', marginTop: '4px' }}>NSQF Trades</div>
          </div>
          <div style={{ padding: '28px 24px', background: '#ffffff' }}>
            <div style={{ fontSize: '38px', fontWeight: '900', color: '#059669', letterSpacing: '-1px' }}>{stats ? stats.total_annual_demand.toLocaleString() : '160,952'}</div>
            <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px', marginTop: '4px' }}>Total Labour Demand</div>
          </div>
        </div>
      </section>

      {/* ── ABOUT PLATFORM SECTION ───────────────────────────────────── */}
      <section id="about" style={{ padding: '80px 24px', maxWidth: '1100px', margin: '0 auto', borderTop: '1px solid #e2e8f0' }}>
        <div style={{ textAlign: 'center', marginBottom: '56px' }}>
          <span style={{ color: '#ea580c', fontSize: '12px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px' }}>Core Objective</span>
          <h2 style={{ fontSize: '36px', fontWeight: '800', color: '#0f172a', marginTop: '8px' }}>Designed for Evidence-Based Policy Action</h2>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
          <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '16px', padding: '32px', boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: '#eff6ff', color: '#2563eb', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
              <Cpu size={22} />
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#0f172a', marginBottom: '12px' }}>Demand-Supply Mapping</h3>
            <p style={{ fontSize: '14px', color: '#64748b', lineHeight: '1.6' }}>
              Aggregates heterogeneous industrial job posting signals (NCS, Portal) alongside physical NCVT-MIS training intake data.
            </p>
          </div>

          <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '16px', padding: '32px', boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: '#fff7ed', color: '#ea580c', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
              <LineChart size={22} />
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#0f172a', marginBottom: '12px' }}>ML Forecasting (2025–2028)</h3>
            <p style={{ fontSize: '14px', color: '#64748b', lineHeight: '1.6' }}>
              Uses Gradient Boosting Regressors with feature lag inputs to project future skill deficits with confidence bounds.
            </p>
          </div>

          <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '16px', padding: '32px', boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: '#f0fdf4', color: '#059669', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
              <Sliders size={22} />
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#0f172a', marginBottom: '12px' }}>What-If Policy Simulator</h3>
            <p style={{ fontSize: '14px', color: '#64748b', lineHeight: '1.6' }}>
              Interactive knob controls allowing state planners to test seat additions, intake expansion, and retention boosts.
            </p>
          </div>
        </div>
      </section>

      {/* ── ARCHITECTURE SECTION ────────────────────────────────────── */}
      <section id="architecture" style={{ padding: '80px 24px', maxWidth: '1100px', margin: '0 auto', borderTop: '1px solid #e2e8f0' }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <span style={{ color: '#2563eb', fontSize: '12px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px' }}>Technical Foundation</span>
          <h2 style={{ fontSize: '36px', fontWeight: '800', color: '#0f172a', marginTop: '8px' }}>System Architecture &amp; Data Pipeline</h2>
        </div>

        <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '20px', padding: '40px', boxShadow: '0 8px 24px rgba(0,0,0,0.04)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', textAlign: 'center' }}>
            <div style={{ padding: '20px 16px', background: '#f8fafc', borderRadius: '14px', border: '1px solid #e2e8f0' }}>
              <div style={{ fontSize: '12px', color: '#2563eb', fontWeight: '700' }}>INPUT LAYER</div>
              <div style={{ fontSize: '15px', fontWeight: '700', color: '#0f172a', marginTop: '8px' }}>Data Sources</div>
              <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>NCVT-MIS · NCS Job Postings · PLFS Microdata</div>
            </div>

            <div style={{ padding: '20px 16px', background: '#f8fafc', borderRadius: '14px', border: '1px solid #e2e8f0' }}>
              <div style={{ fontSize: '12px', color: '#ea580c', fontWeight: '700' }}>PROCESSING</div>
              <div style={{ fontSize: '15px', fontWeight: '700', color: '#0f172a', marginTop: '8px' }}>FastAPI Backend</div>
              <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>SQLAlchemy · Pydantic v2 · SQLite Engine</div>
            </div>

            <div style={{ padding: '20px 16px', background: '#f8fafc', borderRadius: '14px', border: '1px solid #e2e8f0' }}>
              <div style={{ fontSize: '12px', color: '#d97706', fontWeight: '700' }}>INTELLIGENCE</div>
              <div style={{ fontSize: '15px', fontWeight: '700', color: '#0f172a', marginTop: '8px' }}>ML Engine</div>
              <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>GBR Models · Linear Extrapolation · Gap Classifier</div>
            </div>

            <div style={{ padding: '20px 16px', background: '#f8fafc', borderRadius: '14px', border: '1px solid #e2e8f0' }}>
              <div style={{ fontSize: '12px', color: '#059669', fontWeight: '700' }}>PRESENTATION</div>
              <div style={{ fontSize: '15px', fontWeight: '700', color: '#0f172a', marginTop: '8px' }}>React Dashboard</div>
              <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>Vite · Recharts · Lucide UI Components</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── USER GUIDE SECTION ──────────────────────────────────────── */}
      <section id="guide" style={{ padding: '80px 24px', maxWidth: '1000px', margin: '0 auto', borderTop: '1px solid #e2e8f0' }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <span style={{ color: '#059669', fontSize: '12px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px' }}>Platform Navigation</span>
          <h2 style={{ fontSize: '36px', fontWeight: '800', color: '#0f172a', marginTop: '8px' }}>How to Use SkillSetu AI</h2>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
          <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '16px', padding: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.03)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <span style={{ width: '28px', height: '28px', borderRadius: '50%', background: '#2563eb', color: '#fff', fontWeight: '800', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px' }}>1</span>
              <h4 style={{ fontSize: '16px', fontWeight: '700', color: '#0f172a' }}>Executive Overview</h4>
            </div>
            <p style={{ fontSize: '13.5px', color: '#64748b', lineHeight: '1.5' }}>
              Inspect high-level KPI cards and multi-year trend charts to grasp state-level labour market equilibrium.
            </p>
          </div>

          <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '16px', padding: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.03)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <span style={{ width: '28px', height: '28px', borderRadius: '50%', background: '#ea580c', color: '#fff', fontWeight: '800', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px' }}>2</span>
              <h4 style={{ fontSize: '16px', fontWeight: '700', color: '#0f172a' }}>District Drill-Down</h4>
            </div>
            <p style={{ fontSize: '13.5px', color: '#64748b', lineHeight: '1.5' }}>
              Filter by Odisha's 30 districts, sectors, and trades to identify micro-level deficits and economic tiering.
            </p>
          </div>

          <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '16px', padding: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.03)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <span style={{ width: '28px', height: '28px', borderRadius: '50%', background: '#d97706', color: '#fff', fontWeight: '800', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px' }}>3</span>
              <h4 style={{ fontSize: '16px', fontWeight: '700', color: '#0f172a' }}>Forecast Inspection</h4>
            </div>
            <p style={{ fontSize: '13.5px', color: '#64748b', lineHeight: '1.5' }}>
              Review 2025–2028 ML projections alongside confidence intervals to anticipate bottleneck trade years.
            </p>
          </div>

          <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '16px', padding: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.03)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <span style={{ width: '28px', height: '28px', borderRadius: '50%', background: '#059669', color: '#fff', fontWeight: '800', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px' }}>4</span>
              <h4 style={{ fontSize: '16px', fontWeight: '700', color: '#0f172a' }}>Simulate Interventions</h4>
            </div>
            <p style={{ fontSize: '13.5px', color: '#64748b', lineHeight: '1.5' }}>
              Adjust policy sliders to simulate seat expansions and observe real-time gap reduction metrics.
            </p>
          </div>
        </div>
      </section>

      {/* ── FOOTER ─────────────────────────────────────────────────── */}
      <footer style={{ borderTop: '1px solid #e2e8f0', padding: '40px 24px', textAlign: 'center', color: '#64748b', fontSize: '13px', background: '#ffffff' }}>
        <p style={{ fontWeight: '600', color: '#0f172a' }}>SkillSetu AI — Smart India Hackathon PS 26246 Solution</p>
        <p style={{ marginTop: '4px', fontSize: '12px', color: '#64748b' }}>Pilot Geography: Odisha (30 Districts) · Powered by FastAPI &amp; React</p>
      </footer>
    </div>
  );
};

export default PublicLanding;
