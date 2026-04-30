import { useState } from 'react';
import { Share2, Copy, Check, Clock, ShieldCheck, Mail } from 'lucide-react';
import { generateAccessToken } from '../utils/api';

const C = { blue: '#1e40af', teal: '#10b981', border: '#e5e7eb', muted: '#6b7280', text: '#111827' };

export default function ShareAccess({ patientId }) {
  const [email, setEmail] = useState('dr.sharma@cityhospital.in');
  const [token, setToken] = useState(null);
  const [expiresAt, setExpiresAt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const generate = async (e) => {
    e.preventDefault();
    if (!email) return;
    setLoading(true); setError(''); setToken(null); setCopied(false);
    try {
      const r = await generateAccessToken(patientId, email);
      setToken(r.access_token);
      setExpiresAt(r.expires_at || '');
    } catch (e) { setError(e.message || 'Failed to generate token'); }
    finally { setLoading(false); }
  };

  const copy = () => { navigator.clipboard.writeText(token); setCopied(true); setTimeout(() => setCopied(false), 2000); };

  const formatExpiry = () => {
    if (!expiresAt) {
      const d = new Date(); d.setMinutes(d.getMinutes() + 30);
      return `${d.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})} on ${d.toLocaleDateString('en-GB',{day:'2-digit',month:'short',year:'numeric'})}`;
    }
    const d = new Date(expiresAt);
    return `${d.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})} on ${d.toLocaleDateString('en-GB',{day:'2-digit',month:'short',year:'numeric'})}`;
  };

  return (
    <div style={{ maxWidth: 540, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
        <div style={{ width: 56, height: 56, background: '#dbeafe', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 0.85rem', color: C.blue }}><Share2 size={28} /></div>
        <h3 style={{ fontSize: '1.35rem', fontWeight: 700, color: C.text, marginBottom: '0.35rem' }}>Share with Doctor</h3>
        <p style={{ color: C.muted }}>Generate a secure access token to share your complete medical history with your healthcare provider. Valid for 30 minutes.</p>
      </div>

      {error && <div style={{ background: '#fef2f2', color: '#991b1b', padding: '0.6rem 0.85rem', borderRadius: 8, marginBottom: '1rem', borderLeft: '4px solid #ef4444', fontSize: '0.875rem' }}>{error}</div>}

      <div style={{ background: '#fff', border: `1px solid ${C.border}`, borderRadius: 8, padding: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.04)' }}>
        <form onSubmit={generate}>
          {/* Doctor Email */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 600, color: '#374151', marginBottom: '0.35rem', textTransform: 'uppercase', letterSpacing: '0.03em' }}>Doctor Email</label>
            <div style={{ position: 'relative' }}>
              <Mail size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="e.g. dr.amit@hospital.com" style={{ width: '100%', padding: '0.65rem 0.75rem 0.65rem 2.25rem', borderRadius: 8, border: '1.5px solid #d1d5db', fontSize: '0.95rem' }} />
            </div>
          </div>

          <button type="submit" disabled={loading} style={{ width: '100%', padding: '0.8rem', background: C.blue, color: '#fff', border: 'none', borderRadius: 8, fontSize: '1rem', fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer' }}>
            {loading ? 'Generating…' : 'Generate Access Link'}
          </button>
        </form>

        {token && (
          <div style={{ marginTop: '1.5rem', padding: '1.15rem', background: '#ecfdf5', border: '1px solid #a7f3d0', borderRadius: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#065f46', fontWeight: 600, marginBottom: '0.85rem', fontSize: '0.95rem' }}>
              <Check size={18} /> Access Token Generated
            </div>

            <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '0.85rem' }}>
              <input type="text" readOnly value={token} style={{ flex: 1, padding: '0.55rem 0.75rem', borderRadius: 6, border: '1px solid #86efac', background: '#fff', fontFamily: 'monospace', fontWeight: 500, fontSize: '0.85rem' }} />
              <button onClick={copy} style={{ padding: '0.55rem', background: '#fff', border: '1px solid #86efac', borderRadius: 6, color: copied ? '#059669' : C.text, cursor: 'pointer' }}>
                {copied ? <Check size={18} /> : <Copy size={18} />}
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#047857', fontSize: '0.85rem', marginBottom: '0.85rem' }}>
              <Clock size={15} /> Expires in 30 minutes | {formatExpiry()}
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.4rem', color: '#065f46', fontSize: '0.85rem', background: '#d1fae5', padding: '0.65rem', borderRadius: 6 }}>
              <ShieldCheck size={16} style={{ flexShrink: 0, marginTop: 2 }} />
              <span>Share this token with your doctor via WhatsApp, Email, or SMS. They will need to enter it in their portal to access the records.</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
