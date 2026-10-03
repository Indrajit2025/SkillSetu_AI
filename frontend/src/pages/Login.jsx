import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/elevatr-auth.css';
import { ShieldCheck, UserCheck, Briefcase } from 'lucide-react';

export const Login = () => {
  const [isSignUp, setIsSignUp] = useState(false);
  const { login, register, loading } = useAuth();
  const navigate = useNavigate();

  // Login form state
  const [loginEmail, setLoginEmail] = useState('analyst@odisha.gov.in');
  const [loginPassword, setLoginPassword] = useState('Analyst@123');
  const [loginError, setLoginError] = useState('');

  // Register form state
  const [regName, setRegName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regRole, setRegRole] = useState('analyst');
  const [regOrg, setRegOrg] = useState('');
  const [regDept, setRegDept] = useState('');
  const [regError, setRegError] = useState('');

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoginError('');
    const res = await login(loginEmail, loginPassword);
    if (res.success) {
      navigate('/app/dashboard');
    } else {
      setLoginError(res.error);
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setRegError('');
    const res = await register({
      full_name: regName,
      email: regEmail,
      password: regPassword,
      role: regRole,
      organization: regOrg || 'Skill Development Department',
      department: regDept || 'Labour Analytics Wing',
    });
    if (res.success) {
      navigate('/app/dashboard');
    } else {
      setRegError(res.error);
    }
  };

  const fillDemoCredentials = (email, pass) => {
    setLoginEmail(email);
    setLoginPassword(pass);
    setLoginError('');
  };

  return (
    <div className="elevatr-auth-wrapper">
      <div className="elevatr-auth-header">
        <h2>SkillSetu AI Portal</h2>
        <p>AI-Enabled Labour Market Intelligence & Skill Demand-Supply Forecasting Engine</p>
      </div>

      <div className={`auth-container ${isSignUp ? 'right-panel-active' : ''}`} id="authContainer">
        {/* Sign Up Panel (Sliding in) */}
        <div className="auth-form-container sign-up-container">
          <form className="auth-form" onSubmit={handleRegisterSubmit}>
            <h1>Create Account</h1>
            <span className="sub-text">Join the Odisha Skill Intelligence Network</span>

            {regError && <div className="error-banner">{regError}</div>}

            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Dr. Rajesh Mohanty"
                value={regName}
                onChange={(e) => setRegName(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Official Email</label>
              <input
                type="email"
                className="form-input"
                placeholder="name@odisha.gov.in"
                value={regEmail}
                onChange={(e) => setRegEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Stakeholder Role</label>
              <select
                className="form-input"
                value={regRole}
                onChange={(e) => setRegRole(e.target.value)}
              >
                <option value="analyst">Labour Market Analyst</option>
                <option value="policy_maker">Policy Maker / Govt Officer</option>
                <option value="training_institute">Training Institute / ITI Head</option>
              </select>
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                className="form-input"
                placeholder="Minimum 6 characters"
                value={regPassword}
                onChange={(e) => setRegPassword(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="auth-btn-primary" disabled={loading}>
              {loading ? 'Registering...' : 'Register Account'}
            </button>
          </form>
        </div>

        {/* Sign In Panel */}
        <div className="auth-form-container sign-in-container">
          <form className="auth-form" onSubmit={handleLoginSubmit}>
            <h1>Sign In</h1>
            <span className="sub-text">Use your government authorized credentials</span>

            {loginError && <div className="error-banner">{loginError}</div>}

            <div className="form-group">
              <label>Email Address</label>
              <input
                type="email"
                className="form-input"
                placeholder="analyst@odisha.gov.in"
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                className="form-input"
                placeholder="••••••••"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="auth-btn-primary" disabled={loading}>
              {loading ? 'Authenticating...' : 'Sign In to Dashboard'}
            </button>

            {/* Quick Demo Access Chips */}
            <div className="demo-credentials-box">
              <div className="title">⚡ Quick Demo Login (One-Click)</div>
              <div className="demo-chips">
                <button
                  type="button"
                  className="demo-chip"
                  onClick={() => fillDemoCredentials('analyst@odisha.gov.in', 'Analyst@123')}
                >
                  Analyst (Odisha)
                </button>
                <button
                  type="button"
                  className="demo-chip"
                  onClick={() => fillDemoCredentials('policy@sdteodiasha.gov.in', 'Policy@123')}
                >
                  Policy Maker
                </button>
                <button
                  type="button"
                  className="demo-chip"
                  onClick={() => fillDemoCredentials('admin@skillsetu.gov.in', 'Admin@123')}
                >
                  Platform Admin
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* ElevatR Sliding Gradient Overlay Container */}
        <div className="auth-overlay-container">
          <div className="auth-overlay">
            {/* Left Overlay (shown when Register is active) */}
            <div className="auth-overlay-panel auth-overlay-left">
              <h1>Welcome Back!</h1>
              <p>Already have an authorized access ID? Sign in to access real-time district forecasts and gap matrices.</p>
              <button
                type="button"
                className="auth-btn-ghost"
                onClick={() => {
                  setIsSignUp(false);
                  setRegError('');
                }}
              >
                Sign In
              </button>
            </div>

            {/* Right Overlay (shown when Login is active) */}
            <div className="auth-overlay-panel auth-overlay-right">
              <h1>Hello, Officer!</h1>
              <p>Join the national labour intelligence dashboard to simulate policy interventions and plan skill infrastructure.</p>
              <button
                type="button"
                className="auth-btn-ghost"
                onClick={() => {
                  setIsSignUp(true);
                  setLoginError('');
                }}
              >
                Register
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
