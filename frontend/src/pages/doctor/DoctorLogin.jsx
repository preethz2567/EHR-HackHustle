import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stethoscope, ArrowRight, ShieldCheck } from 'lucide-react';
import { authenticateDoctor } from '../../utils/doctorApi';

export default function DoctorLogin() {
  const [email, setEmail] = useState('dr.sharma@cityhospital.in');
  const [password, setPassword] = useState('doctor123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both Email and Password.');
      return;
    }
    
    setLoading(true);
    setError('');
    try {
      const res = await authenticateDoctor(email, password);
      if (res.success && res.token) {
        localStorage.setItem('doctorToken', res.token);
        navigate('/doctor/access');
      } else {
        setError(res.message || 'Authentication failed');
      }
    } catch (err) {
      setError(err.message || 'Server error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-layout" style={{ background: 'linear-gradient(135deg, var(--bg-color) 0%, #cbd5e1 100%)' }}>
      <div className="auth-card">
        <div className="auth-header">
          <div style={{ background: 'var(--surface)', padding: '1rem', borderRadius: '50%', display: 'inline-block', boxShadow: 'var(--shadow-sm)' }}>
            <Stethoscope size={40} className="scanner-icon" style={{ margin: '0', color: '#334155' }} />
          </div>
          <h1 className="mt-4" style={{ color: '#334155' }}>Doctor Portal</h1>
          <p className="text-muted">Clinical Access Gateway</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-md text-sm flex items-center gap-2">
            <span className="badge danger">Error</span> {error}
          </div>
        )}

        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label>Email Address</label>
            <input 
              type="email" 
              placeholder="e.g. dr.sharma@cityhospital.in"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input 
              type="password" 
              placeholder="Enter password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <p className="text-sm text-muted mt-2">
              <ShieldCheck size={14} className="inline mr-1" />
              For demo purposes, use password: doctor123
            </p>
          </div>

          <button type="submit" className="w-full mt-4" style={{ backgroundColor: '#334155', borderColor: '#334155' }} disabled={loading}>
            {loading ? 'Authenticating...' : <><ArrowRight size={18} /> Login to Clinic</>}
          </button>
        </form>
      </div>
    </div>
  );
}
