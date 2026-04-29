import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, Activity, Network, ChevronDown, CheckCircle2, User, UserPlus, HeartPulse, Stethoscope, Mail, Phone, MapPin } from 'lucide-react';
import './LandingPage.css';

export default function LandingPage() {
  const navigate = useNavigate();
  const [isScrolled, setIsScrolled] = useState(false);
  const [showLoginMenu, setShowLoginMenu] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="landing-page">
      {/* Navigation */}
      <nav className={`navbar ${isScrolled ? 'scrolled' : ''}`}>
        <div className="container nav-content">
          <div className="logo-container">
            <HeartPulse className="logo-icon" size={28} />
            <span className="logo-text">HealthBridge <span className="text-teal">India</span></span>
          </div>
          
          <div className="nav-links">
            <button onClick={() => scrollToSection('about')} className="nav-link">About</button>
            <button onClick={() => scrollToSection('features')} className="nav-link">Features</button>
            <button onClick={() => scrollToSection('contact')} className="nav-link">Contact</button>
            
            <div className="dropdown-container" 
                 onMouseEnter={() => setShowLoginMenu(true)}
                 onMouseLeave={() => setShowLoginMenu(false)}>
              <button className="nav-link login-btn">
                Login <ChevronDown size={16} />
              </button>
              {showLoginMenu && (
                <div className="dropdown-menu">
                  <Link to="/login" className="dropdown-item">
                    <User size={16} /> Patient Login
                  </Link>
                  <Link to="/doctor/login" className="dropdown-item">
                    <Stethoscope size={16} /> Doctor Login
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-bg-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
        </div>
        <div className="container hero-content">
          <div className="hero-text animate-fade-in-up">
            <div className="badge-pill">India's Leading Health Information Network</div>
            <h1 className="hero-title">
              Unified Patient Records <br/>
              <span className="text-gradient">Across Providers</span>
            </h1>
            <p className="hero-subtitle">
              Access your complete medical history anytime, anywhere. We connect fragmented health data securely using the ABHA framework, giving you control and doctors the insights they need.
            </p>
            <div className="hero-cta">
              <Link to="/login" className="btn btn-primary">
                I'm a Patient
              </Link>
              <Link to="/doctor/login" className="btn btn-outline-white">
                I'm a Doctor
              </Link>
            </div>
            <p className="hero-hint" onClick={() => scrollToSection('features')}>
              Learn more below <ChevronDown size={16} />
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <div className="container">
          <div className="section-header text-center">
            <h2 className="section-title">A New Era of Healthcare Interoperability</h2>
            <p className="section-subtitle">Seamlessly integrating data from hospitals, clinics, and labs into one secure ecosystem.</p>
          </div>

          <div className="features-grid">
            {/* Feature 1 */}
            <div className="feature-card">
              <div className="feature-icon-wrapper bg-blue-100">
                <Network className="feature-icon text-blue" size={32} />
              </div>
              <h3>Federated Data</h3>
              <p>Access and merge records from multiple hospitals instantly. No more carrying paper files or missing critical history during emergencies.</p>
            </div>

            {/* Feature 2 */}
            <div className="feature-card">
              <div className="feature-icon-wrapper bg-teal-100">
                <Shield className="feature-icon text-teal" size={32} />
              </div>
              <h3>Patient Control</h3>
              <p>You own your data. Use ABHA and biometric consent to dynamically control exactly who sees what, maintaining complete privacy.</p>
            </div>

            {/* Feature 3 */}
            <div className="feature-card">
              <div className="feature-icon-wrapper bg-purple-100">
                <Activity className="feature-icon text-purple" size={32} />
              </div>
              <h3>AI-Powered Insights</h3>
              <p>Intelligent agent networks analyze medications, labs, and history in seconds to provide doctors with critical alerts and recommendations.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="testimonials-section bg-light-gray">
        <div className="container">
          <div className="section-header text-center">
            <h2 className="section-title">Trusted by Healthcare Leaders</h2>
            <p className="section-subtitle">See how HealthBridge is transforming clinical outcomes and patient experiences.</p>
          </div>

          <div className="testimonials-grid">
            <div className="testimonial-card">
              <div className="stars">★★★★★</div>
              <p className="quote">"The federated query system is a game-changer. I no longer have to guess what medications a patient was prescribed at another facility. The AI insights highlight critical interactions instantly."</p>
              <div className="author">
                <div className="avatar bg-blue">DR</div>
                <div className="author-info">
                  <h4>Dr. Rajesh Kumar</h4>
                  <span>Chief Cardiologist, Apollo Hospitals</span>
                </div>
              </div>
            </div>

            <div className="testimonial-card">
              <div className="stars">★★★★★</div>
              <p className="quote">"I manage chronic conditions for my elderly parents. With HealthBridge, I just link their ABHA IDs, and every doctor visit is synced. Giving consent via fingerprint is so secure and easy."</p>
              <div className="author">
                <div className="avatar bg-teal">PS</div>
                <div className="author-info">
                  <h4>Priya Sharma</h4>
                  <span>Patient Caregiver, Bengaluru</span>
                </div>
              </div>
            </div>

            <div className="testimonial-card">
              <div className="stars">★★★★★</div>
              <p className="quote">"Before HealthBridge, consolidating scattered PDF reports took 20 minutes per patient. Now, the Orchestrator agent summarizes their entire 10-year history in 3 seconds. Incredible."</p>
              <div className="author">
                <div className="avatar bg-purple">AM</div>
                <div className="author-info">
                  <h4>Dr. Anjali Menon</h4>
                  <span>Internal Medicine, Manipal Hospitals</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bottom-cta">
        <div className="container">
          <div className="cta-content">
            <h2>Ready to transform your healthcare experience?</h2>
            <p>Join thousands of doctors and patients already on HealthBridge India.</p>
            <div className="cta-buttons">
              <Link to="/login" className="btn btn-white text-blue font-bold">Register as Patient</Link>
              <Link to="/doctor/login" className="btn btn-outline-white">Register as Provider</Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer id="contact" className="footer">
        <div className="container">
          <div className="footer-grid">
            <div className="footer-brand">
              <div className="logo-container">
                <HeartPulse size={24} />
                <span className="logo-text">HealthBridge <span className="text-teal">India</span></span>
              </div>
              <p>Building the secure, interoperable backbone for India's digital health infrastructure.</p>
            </div>
            
            <div className="footer-links">
              <h4>Platform</h4>
              <ul>
                <li><a href="#">Patient Portal</a></li>
                <li><a href="#">Doctor Dashboard</a></li>
                <li><a href="#">Hospital Integration</a></li>
                <li><a href="#">ABHA Verification</a></li>
              </ul>
            </div>
            
            <div className="footer-links">
              <h4>Legal</h4>
              <ul>
                <li><a href="#">Privacy Policy</a></li>
                <li><a href="#">Terms of Service</a></li>
                <li><a href="#">HIPAA Compliance</a></li>
                <li><a href="#">NDHM Guidelines</a></li>
              </ul>
            </div>
            
            <div className="footer-contact">
              <h4>Contact Us</h4>
              <ul>
                <li><Mail size={16} /> support@healthbridge.in</li>
                <li><Phone size={16} /> +91 800 123 4567</li>
                <li><MapPin size={16} /> HealthTech Park, Bengaluru, 560100</li>
              </ul>
            </div>
          </div>
          
          <div className="footer-bottom">
            <p>&copy; {new Date().getFullYear()} HealthBridge India. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
