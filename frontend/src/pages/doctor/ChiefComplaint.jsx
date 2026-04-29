import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileEdit, ArrowRight, User } from 'lucide-react';
import './DoctorPortal.css';

export default function ChiefComplaint() {
  const [complaint, setComplaint] = useState('');
  const [context, setContext] = useState('');
  const [suggestions] = useState([
    'Chest pain', 'Shortness of breath', 'Dizziness', 
    'Abdominal pain', 'High fever', 'Routine checkup'
  ]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  const navigate = useNavigate();
  const patientId = localStorage.getItem('currentPatientId');

  useEffect(() => {
    if (!patientId) {
      navigate('/doctor/access');
    }
  }, [patientId, navigate]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!complaint.trim()) return;

    // Store the chief complaint in local storage to be passed to the dashboard
    localStorage.setItem('chiefComplaint', complaint);
    localStorage.setItem('complaintContext', context);
    
    navigate('/doctor/dashboard');
  };

  const handleCancel = () => {
    navigate('/doctor/access');
  };

  return (
    <div className="doctor-portal" style={{ background: '#f1f5f9' }}>
      <header className="doctor-topbar" style={{ justifyContent: 'center' }}>
        <div className="doctor-brand">
          HealthBridge <span style={{ color: '#0d9488' }}>India</span> — Clinical Entry
        </div>
      </header>

      <div className="main-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 'calc(100vh - 64px)' }}>
        <div className="section-card" style={{ width: '100%', maxWidth: '600px', padding: '2.5rem' }}>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '2rem' }}>
            <div style={{ background: '#e0e7ff', color: '#2563eb', padding: '0.5rem', borderRadius: '50%' }}>
              <User size={20} />
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Patient Auto-populated</div>
              <div style={{ fontWeight: 600, color: '#0f172a' }}>Rajesh Patel <span style={{ color: '#94a3b8', fontWeight: 400 }}>| Age: 68 | ID: {patientId}</span></div>
            </div>
          </div>

          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <div style={{ background: '#ccfbf1', color: '#0d9488', padding: '1rem', borderRadius: '50%', display: 'inline-block', marginBottom: '1rem' }}>
              <FileEdit size={32} />
            </div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a' }}>Why is the patient visiting today?</h2>
            <p style={{ color: '#64748b', marginTop: '0.5rem' }}>Please enter the primary reason for this consultation</p>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="input-group" style={{ position: 'relative' }}>
              <label>Chief Complaint <span style={{ color: '#ef4444' }}>*</span></label>
              <input 
                type="text" 
                className="input-field"
                style={{ paddingLeft: '0.8rem' }}
                placeholder="e.g., Chest pain, Shortness of breath, High fever, etc."
                value={complaint}
                onChange={(e) => {
                  setComplaint(e.target.value);
                  setShowSuggestions(true);
                }}
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                required
              />
              
              {showSuggestions && !complaint && (
                <div style={{ position: 'absolute', top: '100%', left: 0, right: 0, background: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', marginTop: '0.25rem', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', zIndex: 10 }}>
                  <div style={{ padding: '0.5rem 0.75rem', fontSize: '0.75rem', color: '#64748b', background: '#f8fafc', borderBottom: '1px solid #e2e8f0', fontWeight: 600 }}>SUGGESTIONS</div>
                  {suggestions.map(s => (
                    <div 
                      key={s} 
                      style={{ padding: '0.75rem', cursor: 'pointer', fontSize: '0.9rem', color: '#334155', borderBottom: '1px solid #f1f5f9' }}
                      onMouseDown={() => {
                        setComplaint(s);
                        setShowSuggestions(false);
                      }}
                      onMouseEnter={(e) => e.target.style.background = '#f0f4ff'}
                      onMouseLeave={(e) => e.target.style.background = '#fff'}
                    >
                      {s}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="input-group" style={{ marginTop: '1.5rem' }}>
              <label>Additional Context <span style={{ color: '#94a3b8', fontWeight: 400, textTransform: 'none' }}>(Optional)</span></label>
              <textarea 
                className="text-area"
                placeholder="Duration, severity, associated symptoms, etc."
                value={context}
                onChange={(e) => setContext(e.target.value)}
                style={{ minHeight: '80px' }}
              />
            </div>

            <div style={{ display: 'flex', gap: '1rem', marginTop: '2.5rem' }}>
              <button type="button" className="btn-secondary" onClick={handleCancel}>
                Cancel
              </button>
              <button type="submit" className="btn-primary" disabled={!complaint.trim()}>
                Proceed to Analysis <ArrowRight size={18} />
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
