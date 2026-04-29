import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Timer, Download, LogOut, ShieldAlert, Loader } from 'lucide-react';
import { getPatientData, exportReport } from '../../utils/doctorApi';

import PatientSummary from '../../components/doctor/PatientSummary';
import RiskAssessment from '../../components/doctor/RiskAssessment';
import HealthTrends from '../../components/doctor/HealthTrends';
import Recommendations from '../../components/doctor/Recommendations';

export default function DoctorDashboard() {
  const navigate = useNavigate();
  const dashboardRef = useRef(null);
  
  const [patientData, setPatientData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('summary');
  
  // Timer state
  const [timeLeft, setTimeLeft] = useState(30 * 60); // 30 minutes in seconds

  const patientId = localStorage.getItem('currentPatientId');
  const sessionId = localStorage.getItem('doctorSessionId');

  useEffect(() => {
    if (!patientId || !sessionId) {
      navigate('/doctor/access');
      return;
    }

    const fetchData = async () => {
      try {
        const res = await getPatientData();
        setPatientData(res.patient_data);
      } catch (err) {
        setError(err.message || 'Failed to load patient data');
        if (err.message.includes('expired') || err.message.includes('denied')) {
          handleLogout('Session expired or access denied');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [patientId, sessionId, navigate]);

  useEffect(() => {
    if (timeLeft <= 0) {
      handleLogout('Session expired');
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft]);

  const handleLogout = (message = 'Session ended') => {
    localStorage.removeItem('doctorSessionToken');
    localStorage.removeItem('doctorSessionId');
    localStorage.removeItem('currentPatientId');
    // We keep doctorToken so they are still logged in as doctor, just need to request new patient access
    alert(message);
    navigate('/doctor/access');
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handleExportPDF = async () => {
    try {
      const blob = await exportReport();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${patientId}_Report_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Failed to generate PDF: ' + err.message);
    }
  };

  const tabs = [
    { id: 'summary', label: 'Patient Summary' },
    { id: 'risk', label: 'Risk Assessment' },
    { id: 'trends', label: 'Health Trends' },
    { id: 'recommendations', label: 'Recommendations' },
  ];

  if (loading) {
    return (
      <div className="auth-layout" style={{ background: '#f1f5f9' }}>
        <div className="empty-state" style={{ width: '100%', maxWidth: '400px' }}>
          <Loader size={32} className="spinner mx-auto" style={{ borderTopColor: '#334155' }} />
          <p className="mt-4">Loading patient profile...</p>
        </div>
      </div>
    );
  }

  if (error || !patientData) {
    return (
      <div className="auth-layout" style={{ background: '#f1f5f9' }}>
        <div className="empty-state" style={{ width: '100%', maxWidth: '400px' }}>
          <ShieldAlert size={48} className="mx-auto text-red-500" />
          <p className="mt-4 text-red-600 font-semibold">{error}</p>
          <button onClick={() => navigate('/doctor/access')} className="mt-4 outline">Back to Access</button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-layout" style={{ background: '#f8fafc' }}>
      <header className="topbar" style={{ background: '#1e293b', color: 'white' }}>
        <div className="flex items-center gap-4">
          <div className="font-semibold text-lg">Dr. Sharma</div>
          <div className="text-sm px-3 py-1 bg-slate-700 rounded-full flex items-center gap-2">
            <Timer size={14} className={timeLeft < 300 ? 'text-red-400' : 'text-slate-300'} />
            <span className={timeLeft < 300 ? 'text-red-400 font-bold' : ''}>
              {formatTime(timeLeft)}
            </span>
          </div>
        </div>
        <button className="outline text-sm" onClick={() => handleLogout()} style={{ color: 'white', borderColor: 'white' }}>
          <LogOut size={16} /> Exit Patient
        </button>
      </header>

      <main className="main-content container" ref={dashboardRef}>
        <div className="dashboard-header bg-white p-6 rounded-lg shadow-sm border border-slate-200 mb-6 flex justify-between items-center">
          <div>
            <h1 style={{ color: '#0f172a' }}>Patient: {patientId}</h1>
            <div className="flex gap-4 mt-2 text-sm text-slate-500 font-medium">
              <span>Age: {patientData.age || 68}</span>
              <span>Last Visit: {patientData.episodes?.[0]?.date || 'Unknown'}</span>
            </div>
          </div>
          
          <button onClick={handleExportPDF} style={{ backgroundColor: '#0f172a' }}>
            <Download size={16} /> Export Report
          </button>
        </div>

        <div className="tabs-container">
          <div className="tabs-list">
            {tabs.map(tab => (
              <button
                key={tab.id}
                className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
                style={activeTab === tab.id ? { color: '#0f172a', borderBottomColor: '#0f172a' } : {}}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="tab-content">
          {activeTab === 'summary' && <PatientSummary data={patientData} />}
          {activeTab === 'risk' && <RiskAssessment />}
          {activeTab === 'trends' && <HealthTrends data={patientData} />}
          {activeTab === 'recommendations' && <Recommendations />}
        </div>
      </main>
    </div>
  );
}
