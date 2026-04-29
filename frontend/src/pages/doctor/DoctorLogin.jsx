import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stethoscope, Mail, Lock, Loader } from 'lucide-react';
import { authenticateDoctor } from '../../utils/doctorApi';
import './DoctorPortal.css';

export default function DoctorLogin() {
  const [email, setEmail] = useState('dr.amit@hospital.com');
  const [password, setPassword] = useState('doctor123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }
    
    setLoading(true);
    setError('');

    try {
      const res = await authenticateDoctor(email, password);
      if (res.token) {
        localStorage.setItem('doctorToken', res.token);
        localStorage.setItem('doctorEmail', email);
        navigate('/doctor/access');
      } else {
        setError('Authentication failed. Please check your credentials.');
      }
    } catch (err) {
      setError(err.message || 'Connection failed. Please check your network and retry.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="doctor-auth-container">
      {/* Left Hero */}
      <div className="doctor-hero">
        <div className="doctor-hero-overlay" />
        <img
          src="https://images.unsplash.com/photo-1551076805-e1869033e561?auto=format&fit=crop&w=1000&q=80"
          alt="Doctor and Patient"
          className="doctor-hero-img"
        />
        <div className="doctor-hero-content">
          <h2>Precision Care, Powered by Data</h2>
          <p>
            Access comprehensive patient histories, AI-driven risk assessments, and 
            longitudinal health trends to make informed clinical decisions.
          </p>
        </div>
      </div>

      {/* Right Panel */}
      <div className="doctor-form-section">
        <div className="brand-header">
          <Stethoscope className="brand-icon" size={28} />
          <span>
            HealthBridge <span style={{ color: '#0d9488' }}>India</span>
          </span>
        </div>

        <div className="form-wrapper">
          <div className="fade-in">
            <h3>Doctor Login</h3>
            <p className="subtitle">
              Secure access for authorized healthcare providers.
            </p>

            {error && <div className="error-box">{error}</div>}

            <form onSubmit={handleLogin}>
              <div className="input-group">
                <label>Email Address</label>
                <div className="input-with-icon">
                  <Mail size={18} className="input-icon" />
                  <input
                    type="email"
                    className="input-field"
                    placeholder="dr.amit@hospital.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>

              <div className="input-group" style={{ marginTop: '1rem' }}>
                <label>Password</label>
                <div className="input-with-icon">
                  <Lock size={18} className="input-icon" />
                  <input
                    type="password"
                    className="input-field"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
                <div className="forgot-password">
                  <a href="#">Forgot Password?</a>
                </div>
              </div>

              <button
                type="submit"
                className="btn-primary"
                style={{ marginTop: '1.5rem' }}
                disabled={loading}
              >
                {loading ? (
                  <><Loader size={18} className="spinner" /> Authenticating...</>
                ) : (
                  'Login to Portal'
                )}
              </button>

              <div className="auth-footer-link">
                <p>
                  Don't have an account? <a href="#">Register your practice</a>
                </p>
              </div>
            </form>
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
