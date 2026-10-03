import React from 'react';

export const StatusBadge = ({ status }) => {
  if (!status) return null;
  const s = status.toUpperCase();

  if (s === 'SHORTAGE') {
    return <span className="badge-shortage">Shortage</span>;
  }
  if (s === 'OVERSUPPLY') {
    return <span className="badge-oversupply">Oversupply</span>;
  }
  return <span className="badge-balanced">Balanced</span>;
};

export default StatusBadge;
