import React from 'react';

export const UrgencyBadge = ({ tier }) => {
  if (!tier) return null;
  const t = tier.toLowerCase();

  if (t === 'critical') {
    return <span className="badge-tier-critical">Critical</span>;
  }
  if (t === 'high') {
    return <span className="badge-tier-high">High</span>;
  }
  if (t === 'medium') {
    return <span className="badge-tier-medium">Medium</span>;
  }
  return <span style={{ fontSize: '11px', color: '#64748b' }}>Low / Normal</span>;
};

export default UrgencyBadge;
