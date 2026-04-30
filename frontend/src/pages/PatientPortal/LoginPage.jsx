import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { HeartPulse, ArrowRight, ShieldCheck, Mail, Lock, Loader } from 'lucide-react';
import './PatientAuth.css';

export default function Login() {
  const [step, setStep] = useState(1);
  const [patientId, setPatientId] = useState('P001');
  const [email, setEmail] = useState('patient@healthbridge.in');
  const [password, setPassword] = useState('password123');
  const [otp, setOtp] = useState(['', '', '', '']);
  const [error, setError] = useState('');
  const [timer, setTimer] = useState(45);
  const navigate = useNavigate();
  const otpRefs = [useRef(), useRef(), useRef(), useRef()];

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let interval;
    if (step === 2 && timer > 0) {
      interval = setInterval(() => setTimer(t => t - 1), 1000);
    }
    return () => clearInterval(interval);
  }, [step, timer]);

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter your email/phone and password.');
      return;
    }
    setError('');
    setLoading(true);
    // Simulate brief server validation
    setTimeout(() => {
      setLoading(false);
      setStep(2);
    }, 600);
  };

  const handleOtpChange = (index, value) => {
    if (!/^[0-9]*$/.test(value)) return;
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);
    if (value !== '' && index < 3) {
      otpRefs[index + 1].current.focus();
    }
  };

  const handleOtpKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      otpRefs[index - 1].current.focus();
    }
  };

  const handleOtpSubmit = (e) => {
    e.preventDefault();
    const fullOtp = otp.join('');
    if (fullOtp.length < 4) {
      setError('Please enter the complete 4-digit OTP.');
      return;
    }
    navigate('/biometric-auth', { state: { patientId, otp: '123456' } });
  };

  const resendOtp = () => {
    setTimer(45);
    setOtp(['', '', '', '']);
    otpRefs[0].current.focus();
  };

  return (
    <div className="auth-page-container">
      {/* Left — Hero Image */}
      <div className="auth-hero-section">
        <div className="auth-hero-overlay" />
        <img
          src="https://images.unsplash.com/photo-1576091160550-2173ff9e5eb3?auto=format&fit=crop&w=1000&q=80"
          alt="Doctor and Patient"
          className="auth-hero-image"
        />
        <div className="auth-hero-content">
          <h2>Empowering Your Healthcare Journey</h2>
          <p>
            Access your medical records securely, manage your health data, and
            connect seamlessly with your care team.
          </p>
        </div>
      </div>

      {/* Right — Form */}
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
          {step === 1 ? (
            /* -------- PAGE 1: LOGIN -------- */
            <div className="auth-step-1 fade-in">
              <h3>Patient Login</h3>
              <p className="subtitle">
                Welcome back! Please login to your account.
              </p>

              {error && <div className="error-alert">{error}</div>}

              <form onSubmit={handleLoginSubmit}>
                <div className="input-group">
                  <label>Email / Phone</label>
                  <div className="input-with-icon">
                    <Mail size={18} className="input-icon" />
                    <input
                      type="text"
                      placeholder="Enter your registered email or phone"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                  </div>
                </div>

                <div className="input-group mt-3">
                  <label>Password</label>
                  <div className="input-with-icon">
                    <Lock size={18} className="input-icon" />
                    <input
                      type="password"
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </div>
                  <div className="forgot-password">
                    <a href="#">Forgot Password?</a>
                  </div>
                </div>

                <button type="submit" className="btn-solid-blue w-full mt-6" disabled={loading}>
                  {loading ? (
                    <><Loader size={17} className="spinner" /> Authenticating...</>
                  ) : (
                    'Login Securely'
                  )}
                </button>
              </form>

              <div className="auth-footer-link">
                <p>
                  New user? <a href="#">Register here</a>
                </p>
              </div>
            </div>
          ) : (
            /* -------- PAGE 2: OTP -------- */
            <div className="auth-step-2 fade-in">
              <button className="back-button" onClick={() => setStep(1)}>
                ← Back
              </button>

              <h3>Verify Your Identity</h3>
              <p className="subtitle">
                We've sent an OTP to your registered email/phone.
              </p>

              {error && <div className="error-alert">{error}</div>}

              <form onSubmit={handleOtpSubmit}>
                <div className="otp-container">
                  {otp.map((digit, i) => (
                    <input
                      key={i}
                      ref={otpRefs[i]}
                      type="text"
                      maxLength={1}
                      value={digit}
                      onChange={(e) => handleOtpChange(i, e.target.value)}
                      onKeyDown={(e) => handleOtpKeyDown(i, e)}
                      className="otp-input"
                    />
                  ))}
                </div>

                <div className="resend-container">
                  <span className="text-muted text-sm">
                    Didn't receive code?{' '}
                  </span>
                  {timer > 0 ? (
                    <span className="text-sm font-semibold text-blue">
                      Resend in {timer}s
                    </span>
                  ) : (
                    <button
                      type="button"
                      onClick={resendOtp}
                      className="resend-btn"
                    >
                      Resend OTP
                    </button>
                  )}
                </div>

                <button type="submit" className="btn-solid-blue w-full mt-6">
                  Verify &amp; Proceed <ArrowRight size={18} />
                </button>
              </form>
            </div>
          )}
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
