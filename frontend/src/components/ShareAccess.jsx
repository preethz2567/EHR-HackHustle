import { useState } from 'react';
import { Share2, Copy, Check, Clock, ShieldCheck, Mail } from 'lucide-react';
import { generateAccessToken } from '../utils/api';

export default function ShareAccess({ patientId }) {
  const [doctorEmail, setDoctorEmail] = useState('dr.amit@hospital.com');
  const [duration, setDuration] = useState(30);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!doctorEmail) return;

    setLoading(true);
    setError('');
    setToken(null);
    setCopied(false);

    try {
      const res = await generateAccessToken(patientId, doctorEmail, duration);
      setToken(res.access_token);
    } catch (err) {
      setError(err.message || 'Failed to generate access token');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (!token) return;
    navigator.clipboard.writeText(token);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getExpiryTime = () => {
    const d = new Date();
    d.setMinutes(d.getMinutes() + duration);
    return `${d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} on ${d.toLocaleDateString('en-GB', {day: '2-digit', month: 'short', year: 'numeric'})}`;
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <div style={{ width: '64px', height: '64px', backgroundColor: '#e0f2fe', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem', color: '#0284c7' }}>
          <Share2 size={32} />
        </div>
        <h3 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#083344', marginBottom: '0.5rem' }}>Share with Doctor</h3>
        <p style={{ color: '#64748b' }}>Generate a secure, time-bound access link to share your complete medical history with your healthcare provider.</p>
      </div>

      {error && <div style={{ backgroundColor: '#fef2f2', color: '#b91c1c', padding: '0.75rem 1rem', borderRadius: '6px', marginBottom: '1.5rem', borderLeft: '4px solid #ef4444' }}>{error}</div>}

      <div style={{ backgroundColor: 'white', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '2rem', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
        <form onSubmit={handleGenerate}>
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: '#334155', marginBottom: '0.5rem' }}>Doctor Email</label>
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
              <Mail size={18} style={{ position: 'absolute', left: '1rem', color: '#94a3b8' }} />
              <input 
                type="email" 
                value={doctorEmail} 
                onChange={(e) => setDoctorEmail(e.target.value)}
                placeholder="e.g. dr.amit@hospital.com"
                style={{ width: '100%', padding: '0.75rem 1rem 0.75rem 2.5rem', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '1rem', outline: 'none' }}
              />
            </div>
          </div>

          <div style={{ marginBottom: '2rem' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: '#334155', marginBottom: '0.75rem' }}>Access Duration</label>
            <div style={{ display: 'flex', gap: '1rem' }}>
              {[15, 30, 60].map(val => (
                <label key={val} style={{ 
                  flex: 1, textAlign: 'center', padding: '0.75rem', borderRadius: '8px', 
                  border: `2px solid ${duration === val ? '#0284c7' : '#e2e8f0'}`, 
                  backgroundColor: duration === val ? '#f0f9ff' : 'white',
                  color: duration === val ? '#0284c7' : '#64748b',
                  fontWeight: '600', cursor: 'pointer', transition: 'all 0.2s'
                }}>
                  <input 
                    type="radio" 
                    name="duration" 
                    value={val} 
                    checked={duration === val} 
                    onChange={() => setDuration(val)} 
                    style={{ display: 'none' }}
                  />
                  {val === 60 ? '1 hour' : `${val} min`}
                </label>
              ))}
            </div>
          </div>

          <button 
            type="submit" 
            disabled={loading} 
            style={{ 
              width: '100%', padding: '1rem', backgroundColor: '#0284c7', color: 'white', 
              border: 'none', borderRadius: '8px', fontSize: '1.125rem', fontWeight: '600', 
              cursor: loading ? 'not-allowed' : 'pointer', transition: 'background-color 0.2s' 
            }}
          >
            {loading ? 'Generating...' : 'Generate Access Link'}
          </button>
        </form>

        {token && (
          <div style={{ marginTop: '2rem', padding: '1.5rem', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#166534', fontWeight: '600', marginBottom: '1rem' }}>
              <Check size={20} /> Access Link Generated
            </div>
            
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
              <input 
                type="text" 
                readOnly 
                value={token} 
                style={{ flex: 1, padding: '0.75rem 1rem', borderRadius: '6px', border: '1px solid #86efac', backgroundColor: 'white', color: '#0f172a', fontWeight: '500', fontFamily: 'monospace' }} 
              />
              <button 
                onClick={copyToClipboard} 
                title="Copy to clipboard"
                style={{ padding: '0.75rem', backgroundColor: 'white', border: '1px solid #86efac', borderRadius: '6px', color: copied ? '#16a34a' : '#0f172a', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
              >
                {copied ? <Check size={20} /> : <Copy size={20} />}
              </button>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#15803d', fontSize: '0.875rem', marginBottom: '1rem' }}>
              <Clock size={16} /> Expires in {duration} minutes | {getExpiryTime()}
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', color: '#166534', fontSize: '0.875rem', backgroundColor: '#dcfce7', padding: '0.75rem', borderRadius: '6px' }}>
              <ShieldCheck size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
              <span>Share this link with your doctor via WhatsApp, Email, or SMS. They will need to verify their identity to access the records.</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
