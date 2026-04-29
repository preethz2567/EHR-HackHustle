import { useState, useEffect } from 'react';
import { History, Loader, AlertCircle, ShieldOff, Clock, Mail } from 'lucide-react';
import { getActiveTokens, revokeToken, getAuditLog } from '../utils/api';

const C = { blue: '#1e40af', teal: '#10b981', border: '#e5e7eb', muted: '#6b7280', text: '#111827' };

export default function AccessHistory({ patientId }) {
  const [tokens, setTokens] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [revoking, setRevoking] = useState(null);

  const fetchData = async () => {
    try {
      const [tokenRes, logRes] = await Promise.all([
        getActiveTokens(patientId).catch(() => ({ active_tokens: [] })),
        getAuditLog(patientId).catch(() => ({ entries: [] }))
      ]);
      setTokens(tokenRes.active_tokens || []);
      
      const entries = (logRes.audit_log || [])
        .slice(0, 20)
        .map((l, i) => ({
          id: i,
          actor: l.user_id || l.doctor_id || 'Unknown',
          event: l.action,
          time: l.timestamp,
          details: l.details || {}
        }));
      setLogs(entries);
    } catch (e) { setError(e.message || 'Failed to load data'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, [patientId]);

  const handleRevoke = async (fullToken) => {
    setRevoking(fullToken);
    try {
      await revokeToken(patientId, fullToken);
      setTokens(tokens.filter(t => t.token !== fullToken));
    } catch (e) {
      setError(e.message || 'Failed to revoke');
    } finally {
      setRevoking(null);
    }
  };

  const fmt = (iso) => {
    try {
      const d = new Date(iso);
      return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }).format(d);
    } catch { return iso; }
  };

  if (loading)
    return <div style={{ textAlign: 'center', padding: '3rem' }}><Loader size={28} className="spinner" style={{ margin: '0 auto', color: C.blue }} /><p style={{ marginTop: '0.85rem', color: C.muted }}>Loading access history…</p></div>;

  if (error)
    return <div style={{ textAlign: 'center', padding: '3rem', background: '#fef2f2', borderRadius: 8 }}><AlertCircle size={40} style={{ margin: '0 auto', color: '#ef4444' }} /><p style={{ color: '#991b1b', marginTop: '0.85rem' }}>{error}</p><button onClick={() => { setError(''); setLoading(true); fetchData(); }} style={{ marginTop: '1rem', padding: '0.5rem 1rem', background: '#ef4444', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer' }}>Retry</button></div>;

  return (
    <div>
      <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: C.blue, marginBottom: '0.35rem' }}>Access History & Active Tokens</h3>
      <p style={{ color: C.muted, marginBottom: '1.25rem' }}>Monitor active access tokens and view a transparent record of who has accessed your data.</p>

      {/* Active Tokens Section */}
      {tokens.length > 0 && (
        <div style={{ marginBottom: '2rem' }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#059669', marginBottom: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Clock size={16} /> Active Tokens ({tokens.length})
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {tokens.map((t, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', background: '#ecfdf5', border: '1px solid #a7f3d0', borderRadius: 8 }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', color: '#065f46', fontWeight: 600 }}>
                    <Mail size={14} /> {t.doctor_email}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#047857', marginTop: '0.25rem' }}>
                    Token: {t.masked_token || t.token} · Expires in {t.expires_in_minutes} min
                  </div>
                  <div style={{ fontSize: '0.7rem', color: '#6b7280', marginTop: '0.15rem' }}>
                    Expires at: {fmt(t.expires_at)}
                  </div>
                </div>
                <button 
                  onClick={() => handleRevoke(t.token)} 
                  disabled={revoking === t.token}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '0.2rem', padding: '0.4rem 0.7rem', background: '#fef2f2', color: '#ef4444', border: '1px solid #fca5a5', borderRadius: 6, fontSize: '0.825rem', fontWeight: 500, cursor: 'pointer' }}
                >
                  <ShieldOff size={13} /> {revoking === t.token ? 'Revoking...' : 'Revoke'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Audit Log Section */}
      {logs.length > 0 ? (
        <div style={{ background: '#fff', borderRadius: 8, border: `1px solid ${C.border}`, overflow: 'hidden', boxShadow: '0 1px 2px rgba(0,0,0,0.04)' }}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead style={{ background: '#fafafa', borderBottom: `1px solid ${C.border}` }}>
                <tr>
                  {['Actor', 'Event', 'Time'].map(h => (
                    <th key={h} style={{ padding: '0.75rem 1.15rem', fontSize: '0.825rem', fontWeight: 600, color: '#4b5563' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {logs.map(l => (
                  <tr key={l.id} style={{ borderBottom: `1px solid #f3f4f6` }}>
                    <td style={{ padding: '0.85rem 1.15rem', fontWeight: 500, fontSize: '0.85rem' }}>{l.actor}</td>
                    <td style={{ padding: '0.85rem 1.15rem', fontSize: '0.85rem' }}>
                      <span style={{ background: (l.event || '').toUpperCase().includes('GENERATE') ? '#dbeafe' : (l.event || '').toUpperCase().includes('ACCESS') ? '#d1fae5' : '#f3f4f6', color: (l.event || '').toUpperCase().includes('GENERATE') ? '#1e40af' : (l.event || '').toUpperCase().includes('ACCESS') ? '#065f46' : '#4b5563', padding: '0.15rem 0.45rem', borderRadius: 4, fontSize: '0.7rem', fontWeight: 600 }}>
                        {l.event}
                      </span>
                    </td>
                    <td style={{ padding: '0.85rem 1.15rem', fontSize: '0.85rem', color: C.muted }}>{fmt(l.time)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : tokens.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3.5rem 1.5rem', background: '#f3f4f6', borderRadius: 8, border: `1px solid ${C.border}` }}>
          <History size={44} style={{ margin: '0 auto', color: '#9ca3af' }} />
          <h3 style={{ marginTop: '0.85rem', color: '#374151', fontSize: '1.15rem', fontWeight: 600 }}>No Access History</h3>
          <p style={{ color: C.muted, marginTop: '0.35rem' }}>No doctors have accessed your data yet.</p>
        </div>
      ) : null}
    </div>
  );
}
