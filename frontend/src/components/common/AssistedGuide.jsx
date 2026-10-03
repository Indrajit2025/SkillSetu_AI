import React, { useState } from 'react';
import { Compass, ChevronDown, ChevronUp, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

/**
 * A collapsible guidance ribbon that shows at the top of analytical pages.
 * Props: title, purpose, steps=[{bold, desc}], nextActionLabel, nextActionTo
 */
export const AssistedGuide = ({ title, purpose, steps = [], nextActionLabel, nextActionTo }) => {
  const [open, setOpen] = useState(false);

  return (
    <div className="assisted-guide" onClick={() => setOpen(!open)}>
      <Compass size={16} style={{ flexShrink: 0, marginTop: 1 }} />
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <span style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, color: '#4f46e5' }}>
              How to use this page
            </span>
            <div style={{ fontSize: 13.5, fontWeight: 700, color: '#1e40af', marginTop: 1 }}>{title}</div>
          </div>
          {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </div>

        {open && (
          <div onClick={(e) => e.stopPropagation()} style={{ marginTop: 10 }}>
            {purpose && (
              <p style={{ fontSize: 12.5, color: '#334155', lineHeight: 1.5, marginBottom: 10 }}>{purpose}</p>
            )}
            {steps.length > 0 && (
              <div className="guided-steps">
                {steps.map((s, i) => (
                  <div key={i} className="guided-step">
                    <span className="step-num">{i + 1}</span>
                    <span><strong>{s.bold}</strong>{s.desc ? ` — ${s.desc}` : ''}</span>
                  </div>
                ))}
              </div>
            )}
            {nextActionTo && (
              <div style={{ marginTop: 12, textAlign: 'right' }}>
                <Link
                  to={nextActionTo}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 5, fontSize: 13, fontWeight: 600, color: '#3730a3' }}
                >
                  {nextActionLabel || 'Next Step'} <ArrowRight size={13} />
                </Link>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AssistedGuide;
