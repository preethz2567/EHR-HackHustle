import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { KeyRound, Loader, LogOut, Stethoscope, UserCheck, CheckCircle, ArrowRight } from 'lucide-react';
import { accessPatientData } from '../../utils/doctorApi';
import './DoctorPortal.css';

export default function PatientAccess() {
  const [accessToken, setAccessToken] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [verified, setVerified] = useState(false);
  const [patientInfo, setPatientInfo] = useState(null);
  const navigate = useNavigate();

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!accessToken.trim()) {
      setError('Please enter the Access Token.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const res = await accessPatientData(accessToken.trim());
      
      // Store the access token for subsequent API calls
      localStorage.setItem('doctorSessionId', 'simplified_session');
      localStorage.setItem('doctorSessionToken', accessToken.trim());
      localStorage.setItem('currentPatientId', res.patient_id);
      
      const pd = res.patient_data || {};
      localStorage.setItem('currentPatientName', pd.name || 'Patient');
      localStorage.setItem('currentPatientAge', pd.age || 'N/A');
      
      // Extract patient info from the response for display
      setPatientInfo({
        name: pd.name || 'Patient',
        age: pd.age || 'N/A',
        gender: pd.gender || 'N/A',
        id: res.patient_id,
        diagnoses: (pd.diagnoses || []).length,
        medications: (pd.medications || []).length,
        labs: (pd.labs || []).length,
      });
      setVerified(true);
    } catch (err) {
      if (err.message.includes('expired')) {
        setError('Token has expired. Please request a new token from the patient.');
      } else if (err.message.includes('revoked')) {
        setError('Token has been revoked by the patient.');
      } else if (err.message.includes('Invalid')) {
        setError('Invalid token. Please check and try again.');
      } else if (err.message.includes('Connection')) {
        setError('Connection failed. Please check your network and retry.');
      } else {
        setError(err.message || 'Access denied or token expired');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleProceed = () => {
    navigate('/doctor/chief-complaint');
  };

  const handleLogout = () => {
    localStorage.removeItem('doctorToken');
    localStorage.removeItem('doctorSessionToken');
    localStorage.removeItem('doctorSessionId');
    localStorage.removeItem('currentPatientId');
    localStorage.removeItem('doctorEmail');
    navigate('/doctor/login');
  };

  return (
    <div className="doctor-portal">
      <header className="doctor-topbar">
        <div className="doctor-brand">
          <Stethoscope size={24} style={{ color: '#0d9488' }} />
          <span>Clinical Portal</span>
        </div>
        <div className="doctor-actions">
          <button className="btn-logout" onClick={handleLogout}>
            <LogOut size={16} /> Logout
          </button>
        </div>
      </header>

      <div className="main-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 'calc(100vh - 64px)' }}>
        <div className="section-card" style={{ width: '100%', maxWidth: '540px', padding: '2.5rem' }}>
          
          {!verified ? (
            <>
              <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                <div style={{ background: '#f0f4ff', color: '#2563eb', padding: '1rem', borderRadius: '50%', display: 'inline-block', marginBottom: '1rem' }}>
                  <UserCheck size={36} />
                </div>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a' }}>Access Patient Records</h2>
                <p style={{ color: '#64748b', marginTop: '0.5rem' }}>Enter the patient's authorization token to securely access their clinical history.</p>
              </div>

              {error && <div className="error-box">{error}</div>}

              <form onSubmit={handleVerify}>
                <div className="input-group" style={{ marginBottom: '2rem' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <KeyRound size={14} /> Patient Authorization Token
                  </label>
                  <textarea 
                    className="text-area"
                    placeholder="Paste the 32-character token here..."
                    value={accessToken}
                    onChange={(e) => setAccessToken(e.target.value)}
                    style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}
                  />
                </div>

                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? (
                    <><Loader size={18} className="spinner" /> Verifying Token...</>
                  ) : (
                    'Verify Token'
                  )}
                </button>
              </form>
            </>
          ) : (
            <div className="fade-in">
              <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                <div style={{ background: '#d1fae5', color: '#059669', padding: '1rem', borderRadius: '50%', display: 'inline-block', marginBottom: '1rem' }}>
                  <CheckCircle size={36} />
                </div>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#059669' }}>Token Verified ✓</h2>
                <p style={{ color: '#64748b', marginTop: '0.5rem' }}>Patient records are ready for access.</p>
              </div>

              {/* Patient Info Card */}
              <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem', marginBottom: '2rem' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>Patient Information</div>
                <div style={{ fontWeight: 700, fontSize: '1.15rem', color: '#0f172a' }}>{patientInfo?.name}</div>
                <div style={{ color: '#475569', fontSize: '0.9rem', marginTop: '0.25rem' }}>
                  Age: {patientInfo?.age} | Gender: {patientInfo?.gender} | ID: {patientInfo?.id}
                </div>
                <div style={{ display: 'flex', gap: '1rem', marginTop: '0.75rem' }}>
                  <span style={{ background: '#dbeafe', color: '#1e40af', padding: '0.2rem 0.5rem', borderRadius: 4, fontSize: '0.75rem', fontWeight: 600 }}>{patientInfo?.diagnoses} Diagnoses</span>
                  <span style={{ background: '#d1fae5', color: '#065f46', padding: '0.2rem 0.5rem', borderRadius: 4, fontSize: '0.75rem', fontWeight: 600 }}>{patientInfo?.medications} Medications</span>
                  <span style={{ background: '#fef3c7', color: '#92400e', padding: '0.2rem 0.5rem', borderRadius: 4, fontSize: '0.75rem', fontWeight: 600 }}>{patientInfo?.labs} Lab Tests</span>
                </div>
              </div>

              <button className="btn-primary" onClick={handleProceed} style={{ width: '100%' }}>
                Proceed to Analysis <ArrowRight size={18} />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
