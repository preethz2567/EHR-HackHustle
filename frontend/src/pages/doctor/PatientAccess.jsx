import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserSearch, KeyRound, Loader, LogOut } from 'lucide-react';
import { startDoctorSession } from '../../utils/doctorApi';

export default function PatientAccess() {
  const [patientId, setPatientId] = useState('P001');
  const [accessToken, setAccessToken] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleAccess = async (e) => {
    e.preventDefault();
    if (!patientId || !accessToken) {
      setError('Please enter both Patient ID and Access Token.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      // Step 1: Start a 30-min session with the access token
      const res = await startDoctorSession(patientId, accessToken);
      
      // Step 2: Store session data for subsequent requests
      localStorage.setItem('doctorSessionId', res.session_id);
      localStorage.setItem('doctorSessionToken', accessToken);
      localStorage.setItem('currentPatientId', patientId);
      
      // Step 3: Navigate to the dashboard
      navigate('/doctor/dashboard');
    } catch (err) {
      setError(err.message || 'Access denied or token expired');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('doctorToken');
    localStorage.removeItem('doctorSessionToken');
    localStorage.removeItem('doctorSessionId');
    localStorage.removeItem('currentPatientId');
    navigate('/doctor/login');
  };

  return (
    <div className="app-layout" style={{ background: '#f1f5f9' }}>
      <header className="topbar">
        <div className="topbar-brand" style={{ color: '#334155' }}>
          <span>Clinical Portal</span>
        </div>
        <div className="topbar-actions">
          <button className="outline text-sm" onClick={handleLogout} style={{ color: '#475569', borderColor: '#cbd5e1' }}>
            <LogOut size={16} /> Logout
          </button>
        </div>
      </header>

      <div className="flex items-center justify-center" style={{ minHeight: 'calc(100vh - 70px)' }}>
        <div className="card" style={{ width: '100%', maxWidth: '500px', padding: '2.5rem' }}>
          <div className="text-center mb-8">
            <div style={{ background: '#e2e8f0', padding: '1rem', borderRadius: '50%', display: 'inline-block', marginBottom: '1rem' }}>
              <UserSearch size={32} style={{ color: '#475569' }} />
            </div>
            <h2 style={{ color: '#334155' }}>Patient Access Request</h2>
            <p className="text-muted mt-2">Enter the session token provided by the patient.</p>
          </div>

          {error && (
            <div className="mb-6 p-3 bg-red-50 border border-red-200 text-red-600 rounded-md text-sm text-center font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleAccess}>
            <div className="form-group">
              <label>Patient ID or ABHA</label>
              <input 
                type="text" 
                placeholder="e.g. P001"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
              />
            </div>
            
            <div className="form-group mb-8">
              <label className="flex items-center gap-2">
                <KeyRound size={16} /> Access Token
              </label>
              <input 
                type="text" 
                placeholder="Paste the access token here"
                value={accessToken}
                onChange={(e) => setAccessToken(e.target.value)}
                style={{ fontFamily: 'monospace' }}
              />
            </div>

            <button type="submit" className="w-full" style={{ backgroundColor: '#334155', borderColor: '#334155', padding: '0.75rem' }} disabled={loading}>
              {loading ? <><Loader size={18} className="spinner" /> Validating...</> : 'Access Medical Records'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
