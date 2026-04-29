import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, ArrowRight, ShieldCheck } from 'lucide-react';

export default function Login() {
  const [patientId, setPatientId] = useState('P001');
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleNext = (e) => {
    e.preventDefault();
    if (!patientId || !otp) {
      setError('Please enter both Patient ID and OTP.');
      return;
    }
    // Proceed to biometric step
    navigate('/biometric-auth', { state: { patientId, otp } });
  };

  return (
    <div className="auth-layout">
      <div className="auth-card">
        <div className="auth-header">
          <Activity size={40} className="scanner-icon" style={{ margin: '0 auto' }} />
          <h1 className="mt-4">Patient Portal</h1>
          <p className="text-muted">Enter your details to access your medical records</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-md text-sm flex items-center gap-2">
            <span className="badge danger">Error</span> {error}
          </div>
        )}

        <form onSubmit={handleNext}>
          <div className="form-group">
            <label>Patient ID / Email</label>
            <input 
              type="text" 
              placeholder="e.g. P001"
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
            />
          </div>
          
          <div className="form-group">
            <label>OTP Verification</label>
            <input 
              type="text" 
              placeholder="Enter 6-digit OTP (e.g. 123456)"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              maxLength={6}
            />
            <p className="text-sm text-muted mt-2">
              <ShieldCheck size={14} className="inline mr-1" />
              For demo purposes, use OTP: 123456
            </p>
          </div>

          <button type="submit" className="w-full mt-4">
            Proceed to Biometric Verification <ArrowRight size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
