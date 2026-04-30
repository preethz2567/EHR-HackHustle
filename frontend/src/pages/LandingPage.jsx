import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  HeartPulse, Shield, Activity, Network, ChevronDown, 
  ArrowRight, ShieldCheck, Globe, Database, Star, 
  Zap, Lock, Users, Stethoscope, User, CheckCircle2
} from 'lucide-react';
import './LandingPage.css';

export default function LandingPage() {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) element.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="landing-page">
      {/* Navbar */}
      <nav className={`navbar ${isScrolled ? 'scrolled' : ''}`}>
        <div className="container nav-content">
          <Link to="/" className="logo-container">
            <HeartPulse className="logo-icon" size={32} />
            <span>HealthBridge</span>
          </Link>
          
          <div className="nav-links">
            <a href="#features" className="nav-link">Network</a>
            <a href="#security" className="nav-link">Security</a>
            <a href="#about" className="nav-link">About Us</a>
            <Link to="/login" className="nav-link">Patient Portal</Link>
            <Link to="/doctor/login" className="nav-link nav-cta">Provider Login</Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="container hero-content">
          <div className="hero-text animate-up">
            <span className="hero-tag">India's Unified Health Identity Network</span>
            <h1 className="hero-title">
              Your Medical History. <br />
              <span className="text-gradient">Fully Connected.</span>
            </h1>
            <p className="hero-subtitle">
              HealthBridge securely connects your health data across hospitals and clinics using the ABDM framework. Access your complete records anytime, anywhere.
            </p>
            <div className="hero-actions">
              <Link to="/login" className="btn btn-primary">
                Get Started <ArrowRight size={20} />
              </Link>
              <Link to="/doctor/login" className="btn btn-outline">
                Provider Portal
              </Link>
            </div>
            <p className="hero-hint" onClick={() => scrollToSection('features')}>
              Learn how it works <ChevronDown size={16} />
            </p>
          </div>
          
          <div className="hero-image-container">
            <img 
              src="https://images.unsplash.com/photo-1576091160550-2173ff9e5eb3?auto=format&fit=crop&w=1000&q=80" 
              alt="Connected Healthcare" 
              className="hero-main-img"
            />
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-strip">
        <div className="container stats-grid">
          <div className="stat-item">
            <div className="stat-num">1.2M+</div>
            <div className="stat-label">Linked ABHA IDs</div>
          </div>
          <div className="stat-item">
            <div className="stat-num">1,200+</div>
            <div className="stat-label">Hospitals Integrated</div>
          </div>
          <div className="stat-item">
            <div className="stat-num">100%</div>
            <div className="stat-label">Data Ownership</div>
          </div>
          <div className="stat-item">
            <div className="stat-num">24/7</div>
            <div className="stat-label">Emergency Access</div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features">
        <div className="container">
          <div className="section-head">
            <h2 className="section-title">A Secure, Interoperable Ecosystem</h2>
            <p className="section-subtitle">Bridging the gap between hospitals, clinics, and labs nation-wide.</p>
          </div>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon"><Network size={32} /></div>
              <h3>Federated Query</h3>
              <p>Search and merge your records from Apollo, Fortis, and Manipal hospitals instantly without carrying paper files.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon" style={{ color: '#0d9488' }}><ShieldCheck size={32} /></div>
              <h3>Consent-First</h3>
              <p>You decide who sees your records. Grant time-bound access via biometric or OTP verification for total privacy.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon" style={{ color: '#8b5cf6' }}><Zap size={32} /></div>
              <h3>Clinical Intel</h3>
              <p>Advanced agent networks analyze disparate records to provide doctors with critical alerts and health trends.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Security Section */}
      <section id="security" className="security-section">
        <div className="container security-grid">
          <div className="security-visual">
            <div className="shield-blob">
              <Lock size={80} color="white" />
            </div>
          </div>
          <div className="security-text">
            <span className="badge">Trust & Security</span>
            <h2>Military-Grade Data Protection</h2>
            <p>Your data is encrypted at rest and in transit. HealthBridge does not store your clinical data; we facilitate secure, encrypted peer-to-peer exchanges between providers upon your explicit consent.</p>
            <ul className="security-list">
              <li><CheckCircle2 size={20} className="check-icon" /> HIPAA & ABDM Compliant</li>
              <li><CheckCircle2 size={20} className="check-icon" /> SHA-256 Encryption</li>
              <li><CheckCircle2 size={20} className="check-icon" /> Blockchain Audit Logs</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-grid">
            <div className="footer-brand">
              <div className="logo-container">
                <HeartPulse className="logo-icon" size={28} />
                <span>HealthBridge</span>
              </div>
              <p>Pioneering the next generation of India's health information backbone.</p>
            </div>
            
            <div className="footer-col">
              <h4>Platform</h4>
              <ul>
                <li><Link to="/login">Patient Portal</Link></li>
                <li><Link to="/doctor/login">Provider Access</Link></li>
                <li><a href="#">Network Status</a></li>
              </ul>
            </div>

            <div className="footer-col">
              <h4>Resources</h4>
              <ul>
                <li><a href="#">Security Whitepaper</a></li>
                <li><a href="#">API Documentation</a></li>
                <li><a href="#">Privacy Policy</a></li>
              </ul>
            </div>

            <div className="footer-col">
              <h4>Connect</h4>
              <ul>
                <li><a href="#">LinkedIn</a></li>
                <li><a href="#">Twitter</a></li>
                <li><a href="#">Contact Us</a></li>
              </ul>
            </div>
          </div>
          
          <div className="footer-bottom">
            <p>&copy; {new Date().getFullYear()} HealthBridge India. Secure Digital Health Infrastructure. Powered by ABDM.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
