import { useState } from 'react';
import { Share2, Copy, Check } from 'lucide-react';
import { generateAccessToken } from '../utils/api';

export default function ShareAccess({ patientId }) {
  const [doctorEmail, setDoctorEmail] = useState('dr.sharma@cityhospital.in');
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

  return (
    <div className="card p-6" style={{ padding: '2rem', maxWidth: '600px' }}>
      <div className="flex items-center gap-3 mb-6">
        <div style={{ background: 'var(--primary-light)', padding: '0.75rem', borderRadius: '50%', color: 'var(--primary)' }}>
          <Share2 size={24} />
        </div>
        <div>
          <h3 style={{ margin: 0 }}>Grant Medical Access</h3>
          <p className="text-muted text-sm mt-1">Generate a secure, time-bound access link for your healthcare provider.</p>
        </div>
      </div>

      {error && <div className="mb-4 text-red-600 font-semibold">{error}</div>}

      <form onSubmit={handleGenerate}>
        <div className="form-group">
          <label>Doctor ID / Email</label>
          <input 
            type="text" 
            value={doctorEmail} 
            onChange={(e) => setDoctorEmail(e.target.value)}
            placeholder="e.g. dr.sharma@cityhospital.in"
          />
        </div>

        <div className="form-group mb-6">
          <label>Access Duration</label>
          <select value={duration} onChange={(e) => setDuration(Number(e.target.value))}>
            <option value={15}>15 Minutes</option>
            <option value={30}>30 Minutes</option>
            <option value={60}>1 Hour</option>
          </select>
        </div>

        <button type="submit" disabled={loading} className="w-full">
          {loading ? 'Generating...' : 'Generate Access Token'}
        </button>
      </form>

      {token && (
        <div className="mt-8 p-4 bg-gray-50 border border-gray-200 rounded-md" style={{ background: 'var(--bg-color)', border: '1px solid var(--border)' }}>
          <label className="font-semibold block mb-2 text-sm text-muted">Session Token Generated</label>
          <div className="flex gap-2">
            <input 
              type="text" 
              readOnly 
              value={token} 
              style={{ fontFamily: 'monospace', fontSize: '0.875rem' }} 
            />
            <button className="outline" onClick={copyToClipboard} title="Copy to clipboard">
              {copied ? <Check size={18} className="text-green-600" /> : <Copy size={18} />}
            </button>
          </div>
          <p className="text-sm mt-2 text-muted">
            Provide this token to <strong>{doctorEmail}</strong>. It will expire in {duration} minutes.
          </p>
        </div>
      )}
    </div>
  );
}
