import { useState, useEffect } from 'react';
import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import { Fingerprint, ScanFace, ScanLine, Loader, ShieldAlert } from 'lucide-react';
import { authenticatePatient } from '../utils/api';

export default function BiometricAuth() {
  const location = useLocation();
  const navigate = useNavigate();
  const [type, setType] = useState('fingerprint');
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState('');

  // Protect this route from direct access
  if (!location.state || !location.state.patientId || !location.state.otp) {
    return <Navigate to="/login" replace />;
  }

  const { patientId, otp } = location.state;

  const handleScan = async () => {
    setScanning(true);
    setError('');

    // Simulate 2 second scanning process
    setTimeout(async () => {
      try {
        const mockBiometricData = `${patientId}-${type}-template`;
        const res = await authenticatePatient(patientId, type, mockBiometricData, otp);
        
        if (res.success && res.token) {
          localStorage.setItem('patientToken', res.token);
          navigate('/dashboard');
        } else {
          setError(res.message || 'Authentication failed');
          setScanning(false);
        }
      } catch (err) {
        setError(err.message || 'Server error occurred');
        setScanning(false);
      }
    }, 2000);
  };

  const getIcon = () => {
    if (type === 'fingerprint') return <Fingerprint size={64} className="scanner-icon" />;
    if (type === 'facial') return <ScanFace size={64} className="scanner-icon" />;
    return <ScanLine size={64} className="scanner-icon" />;
  };

  const getInstructions = () => {
    if (type === 'fingerprint') return 'Place your finger on the scanner';
    if (type === 'facial') return 'Look directly at the camera';
    return 'Position your eyes within the frame';
  };

  return (
    <div className="auth-layout">
      <div className="auth-card" style={{ textAlign: 'center' }}>
        <h2>Biometric Verification</h2>
        <p className="text-muted mt-2 mb-6">Confirm your identity securely</p>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-md text-sm text-left">
            <ShieldAlert size={16} className="inline mr-2" />
            {error}
          </div>
        )}

        <div className="form-group" style={{ textAlign: 'left' }}>
          <label>Select Verification Method</label>
          <select 
            value={type} 
            onChange={(e) => setType(e.target.value)}
            disabled={scanning}
          >
            <option value="fingerprint">Fingerprint Scan</option>
            <option value="facial">Facial Recognition</option>
            <option value="iris">Iris Scan</option>
          </select>
        </div>

        <div className="scanner-container">
          {getIcon()}
          {scanning && <div className="scanner-line"></div>}
          <h3 className="mt-4">{getInstructions()}</h3>
          <p className="text-muted text-sm mt-2">
            {scanning ? 'Verifying biometrics...' : 'Ready to scan'}
          </p>
        </div>

        <button 
          className="w-full mt-4" 
          onClick={handleScan}
          disabled={scanning}
        >
          {scanning ? (
            <><Loader size={18} className="spinner" /> Scanning...</>
          ) : (
            'Start Scan'
          )}
        </button>
        
        <button 
          className="w-full mt-4 outline" 
          onClick={() => navigate('/login')}
          disabled={scanning}
        >
          Back
        </button>
      </div>
    </div>
  );
}
