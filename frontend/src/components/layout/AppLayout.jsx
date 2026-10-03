import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';

export const AppLayout = () => (
  <div className="app-container">
    <Sidebar />
    <div className="main-content">
      <Navbar />
      <main className="page-container">
        <div className="data-honesty-banner">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>
              <strong>PILOT DEPLOYMENT · ODISHA</strong>: Calibrated dataset across 30 districts &amp; 8 sectors.
              All figures are from traceable empirical models or labelled synthetic pilot baselines (is_synthetic=1).
            </span>
          </div>
          <span className="badge">SIH PS 26246</span>
        </div>
        <Outlet />
      </main>
    </div>
  </div>
);

export default AppLayout;
