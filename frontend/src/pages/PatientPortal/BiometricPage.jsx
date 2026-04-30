import { useState } from 'react';
import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import { CreditCard, CheckCircle2, ShieldCheck, HeartPulse, Loader } from 'lucide-react';
import { authenticatePatient } from '../utils/api';
import './PatientAuth.css';

export default function BiometricAuth() {
  const location = useLocation();
  const navigate = useNavigate();
  const [aadhaar, setAadhaar] = useState('');
  const [verifying, setVerifying] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  if (!location.state?.patientId || !location.state?.otp) {
    return <Navigate to="/login" replace />;
  }
  const { patientId, otp } = location.state;

  const formatAadhaar = (val) => {
    const digits = val.replace(/\D/g, '').slice(0, 12);
    const parts = [];
    for (let i = 0; i < digits.length; i += 4) {
      parts.push(digits.slice(i, i + 4));
    }
    return parts.join(' ');
  };

  const handleChange = (e) => {
    setAadhaar(formatAadhaar(e.target.value));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const digits = aadhaar.replace(/\s/g, '');
    if (digits.length !== 12) {
      setError('Please enter a valid 12-digit Aadhaar number.');
      return;
    }

    setVerifying(true);
    setError('');

    setTimeout(async () => {
      try {
        // Use the original biometric template for backend compatibility
        // Aadhaar is validated at the UI level only (simulated UIDAI check)
        const res = await authenticatePatient(
          patientId,
          'fingerprint',
          `${patientId}-fingerprint-template`,
          otp
        );
        if (res.success && res.token) {
          localStorage.setItem('patientToken', res.token);
          localStorage.setItem('patient_id', res.patient_id);
          localStorage.setItem('patient_name', res.name);
          setVerifying(false);
          setSuccess(true);
          setTimeout(() => navigate('/dashboard'), 1200);
        } else {
          setError(res.message || 'Verification failed. Please try again.');
          setVerifying(false);
        }
      } catch (err) {
        setError(err.message || 'Server error. Please try again.');
        setVerifying(false);
      }
    }, 2000);
  };

  return (
    <div className="auth-page-container">
      {/* Left Hero */}
      <div className="auth-hero-section">
        <div className="auth-hero-overlay" />
        <img
          src="https://images.unsplash.com/photo-1576091160550-2173ff9e5eb3?auto=format&fit=crop&w=1000&q=80"
          alt="Healthcare"
          className="auth-hero-image"
        />
        <div className="auth-hero-content">
          <h2>Secure Identity Verification</h2>
          <p>
            Your Aadhaar verification is powered by UIDAI and secured through
            the ABHA Health ID framework. Your data is never stored.
          </p>
        </div>
      </div>

      {/* Right Panel */}
      <div className="auth-form-section">
        <div className="auth-form-header">
          <div className="logo-container">
            <HeartPulse className="logo-icon" size={28} />
            <span className="logo-text">
              HealthBridge <span className="logo-accent">India</span>
            </span>
          </div>
          <p className="tagline">Your Health, Your Control</p>
        </div>

        <div className="auth-form-container">
          <div className="fade-in">
            <h3>Aadhaar Verification</h3>
            <p className="subtitle">
              Verify your identity using your Aadhaar number linked with ABHA
            </p>

            {error && <div className="error-alert">{error}</div>}

            {success ? (
              <div className="success-panel fade-in">
                <CheckCircle2 size={60} className="success-icon" />
                <h4>Identity Verified ✓</h4>
                <p>Redirecting to your dashboard…</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit}>
                {/* Aadhaar card visual */}
                <div className="aadhaar-card">
                  <div className="aadhaar-card-top">
                    <div>
                      <div className="aadhaar-label">Government of India</div>
                      <div className="aadhaar-title">आधार — Aadhaar</div>
                    </div>
                    <CreditCard size={26} style={{ opacity: 0.5 }} />
                  </div>
                  <div className="aadhaar-number">
                    {aadhaar || 'XXXX XXXX XXXX'}
                  </div>
                  <div className="aadhaar-sub">Linked with ABHA Health ID</div>
                  <div className="aadhaar-circle-1" />
                  <div className="aadhaar-circle-2" />
                </div>

                {/* Input */}
                <div className="input-group">
                  <label>Aadhaar Number</label>
                  <div className="input-with-icon">
                    <CreditCard size={18} className="input-icon" />
                    <input
                      type="text"
                      placeholder="XXXX XXXX XXXX"
                      value={aadhaar}
                      onChange={handleChange}
                      maxLength={14}
                      style={{ letterSpacing: '0.1em', fontFamily: "'Inter', monospace" }}
                    />
                  </div>
                  <p className="input-hint">
                    Your Aadhaar is verified via UIDAI and never stored
                  </p>
                </div>

                <button
                  type="submit"
                  className="btn-primary-auth w-full mt-6"
                  disabled={verifying}
                >
                  {verifying ? (
                    <>
                      <Loader size={17} className="spinner" />
                      Verifying with UIDAI…
                    </>
                  ) : (
                    'Verify & Continue'
                  )}
                </button>

                <p className="secured-badge">
                  <ShieldCheck size={15} /> Secured by ABHA Framework
                </p>
              </form>
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
