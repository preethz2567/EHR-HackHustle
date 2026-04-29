import { useState, useEffect } from 'react';
import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import { Fingerprint, CheckCircle2, ShieldCheck, HeartPulse } from 'lucide-react';
import { authenticatePatient } from '../utils/api';
import './PatientAuth.css';

export default function BiometricAuth() {
  const location = useLocation();
  const navigate = useNavigate();
  const [scanning, setScanning] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  // Protect this route from direct access
  if (!location.state || !location.state.patientId || !location.state.otp) {
    return <Navigate to="/login" replace />;
  }

  const { patientId, otp } = location.state;

  useEffect(() => {
    // Auto-start scanning when component mounts
    startScan();
  }, []);

  const startScan = () => {
    setScanning(true);
    setError('');

    // Simulate 2 second scanning process
    setTimeout(async () => {
      try {
        const mockBiometricData = `${patientId}-fingerprint-template`;
        const res = await authenticatePatient(patientId, 'fingerprint', mockBiometricData, otp);
        
        if (res.success && res.token) {
          localStorage.setItem('patientToken', res.token);
          setScanning(false);
          setSuccess(true);
          
          // Wait 1.5s on success screen before redirecting
          setTimeout(() => {
            navigate('/dashboard');
          }, 1500);
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

  return (
    <div className="auth-page-container">
      {/* Left Side - Hero Image */}
      <div className="auth-hero-section">
        <div className="auth-hero-overlay"></div>
        <img 
          src="https://images.unsplash.com/photo-1576091160550-2173ff9e5eb3?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80" 
          alt="Healthcare Security" 
          className="auth-hero-image"
        />
        <div className="auth-hero-content">
          <h2>Empowering Your Healthcare Journey</h2>
          <p>Access your medical records securely, manage your health data, and connect seamlessly with your care team.</p>
        </div>
      </div>

      {/* Right Side - Biometric Form */}
      <div className="auth-form-section">
        <div className="auth-form-header">
          <div className="logo-container">
            <HeartPulse className="text-blue" size={32} />
            <span className="logo-text">HealthBridge <span className="text-teal">India</span></span>
          </div>
          <p className="tagline">Your Health, Your Control</p>
        </div>

        <div className="auth-form-container text-center">
          <div className="fade-in">
            <h3>Two-Factor Authentication</h3>
            <p className="subtitle">Complete your identity verification</p>

            {error && <div className="error-alert text-left">{error}</div>}

            <div className="auth-method-selector">
              <label className="method-radio selected">
                <input type="radio" checked readOnly />
                <Fingerprint size={18} />
                <span>Fingerprint Scanner</span>
              </label>
            </div>

            <div className={`biometric-scanner-box ${scanning ? 'scanning' : ''} ${success ? 'success' : ''}`}>
              {success ? (
                <div className="success-state fade-in">
                  <CheckCircle2 size={64} className="text-teal mb-4" />
                  <h4>Fingerprint Verified ✓</h4>
                  <p>Redirecting securely...</p>
                </div>
              ) : (
                <div className="scan-state">
                  <div className="fingerprint-wrapper">
                    <Fingerprint size={80} className={`text-blue ${scanning ? 'pulse' : ''}`} />
                    {scanning && <div className="scan-line"></div>}
                  </div>
                  <h4 className="mt-6 mb-2">
                    {scanning ? 'Scanning biometrics...' : 'Place your registered finger on scanner...'}
                  </h4>
                  {scanning && (
                    <div className="progress-bar mt-4">
                      <div className="progress-fill"></div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {!success && !scanning && error && (
              <button onClick={startScan} className="btn-solid-blue w-full mt-6">
                Try Again
              </button>
            )}
            
            {!success && !scanning && !error && (
              <p className="text-muted text-sm mt-6 flex items-center justify-center gap-2">
                <ShieldCheck size={16} /> Secured by ABHA Framework
              </p>
            )}
          </div>
        </div>

        <div className="auth-legal-footer">
          <a href="#">Privacy Policy</a>
          <span className="separator">•</span>
          <a href="#">Terms of Service</a>
        </div>
      </div>
    </div>
  );
}
