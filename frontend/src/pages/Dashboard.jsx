import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  HeartPulse, LogOut, CloudDownload, Loader, CheckCircle,
  Bell, User, ShieldCheck, HelpCircle, FileText,
  UploadCloud, Share2, History, Activity
} from 'lucide-react';
import { fetchHistoricalData } from '../utils/api';
import MedicalRecords from '../components/MedicalRecords';
import UploadRecords from '../components/UploadRecords';
import ShareAccess from '../components/ShareAccess';
import AccessHistory from '../components/AccessHistory';
import './PatientDashboard.css';

export default function Dashboard() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('records');
  const [fetching, setFetching] = useState(false);
  const [fetchSuccess, setFetchSuccess] = useState(null);
  const [patientId] = useState(localStorage.getItem('patient_id') || 'P001');
  const patientName = localStorage.getItem('patient_name') || 'Rajesh Kumar';

  const [stats] = useState({
    diagnoses: 3, medications: 4, labs: 15,
    lastUpdated: '29-Apr-2026 14:30',
    activeAuths: 0,
  });

  const handleLogout = () => {
    localStorage.removeItem('patientToken');
    localStorage.removeItem('patient_id');
    localStorage.removeItem('patient_name');
    navigate('/login');
  };

  const handleFetchData = async () => {
    setFetching(true);
    setFetchSuccess(null);
    try {
      const res = await fetchHistoricalData(patientId);
      if (res.success) {
        setFetchSuccess(`Synced! ${res.records_count || 45} records found.`);
        window.dispatchEvent(new Event('refreshData'));
      }
    } catch (err) {
      alert(err.message || 'Sync failed');
    } finally {
      setFetching(false);
      setTimeout(() => setFetchSuccess(null), 5000);
    }
  };

  return (
    <div className="patient-dashboard">
      {/* ══════ Horizontal Top Navbar ══════ */}
      <header className="topbar">
        <div className="navbar-brand" onClick={() => navigate('/')}>
          <HeartPulse size={28} className="text-blue" />
          <span>HealthBridge</span>
        </div>

        <nav className="navbar-nav">
          <button 
            className={`nav-link-item ${activeTab === 'home' ? 'active' : ''}`}
            onClick={() => setActiveTab('home')}
          >
            Overview
          </button>
          <button 
            className={`nav-link-item ${activeTab === 'records' ? 'active' : ''}`}
            onClick={() => setActiveTab('records')}
          >
            Medical Records
          </button>
          <button 
            className={`nav-link-item ${activeTab === 'share' ? 'active' : ''}`}
            onClick={() => setActiveTab('share')}
          >
            Share Access
          </button>
          <button 
            className={`nav-link-item ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            Access History
          </button>
        </nav>

        <div className="topbar-right">
          <button className="icon-btn">
            <Bell size={20} />
          </button>
          <div className="user-profile">
            <div className="avatar">{patientName.charAt(0)}</div>
            <div className="user-info">
              <span className="user-name">{patientName}</span>
              <span className="user-role">ID: {patientId}</span>
            </div>
            <button className="icon-btn" onClick={handleLogout} title="Logout" style={{ marginLeft: '1rem' }}>
              <LogOut size={18} className="text-danger" />
            </button>
          </div>
        </div>
      </header>

      {/* ══════ Main Wrapper ══════ */}
      <main className="main-wrapper fade-in">
        <div className="page-header">
          <h1>Welcome back, {patientName.split(' ')[0]}</h1>
          <p>Your comprehensive health profile and record management.</p>
        </div>

        {/* Section A — Quick Stats (KPIs) */}
        <section className="stats-grid">
          <div className="stat-card">
            <div className="stat-header">
              <div className="stat-info">
                <h3>Unified Records</h3>
                <div className="stat-value">{stats.diagnoses + stats.medications + stats.labs}</div>
              </div>
              <div className="stat-icon-wrapper" style={{ background: '#eff6ff' }}>
                <FileText size={24} color="#3b82f6" />
              </div>
            </div>
            <div className="stat-footer">
              {stats.diagnoses} Diagnoses · {stats.medications} Meds · {stats.labs} Labs
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <div className="stat-info">
                <h3>Last Synced</h3>
                <div className="stat-value" style={{ fontSize: '1.25rem' }}>{stats.lastUpdated.split(' ')[0]}</div>
              </div>
              <div className="stat-icon-wrapper" style={{ background: '#f0fdf4' }}>
                <History size={24} color="#22c55e" />
              </div>
            </div>
            <div className="stat-footer">
              Updated at {stats.lastUpdated.split(' ')[1]}
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <div className="stat-info">
                <h3>Active Consent</h3>
                <div className="stat-value">{stats.activeAuths} <span style={{ fontSize: '1rem' }}>Doctors</span></div>
              </div>
              <div className="stat-icon-wrapper" style={{ background: '#fef3c7' }}>
                <ShieldCheck size={24} color="#f59e0b" />
              </div>
            </div>
            <div className="stat-footer">
              Valid permissions in network
            </div>
          </div>
        </section>

        {/* Section B — Action Grid */}
        <section className="actions-grid">
          <div className="action-card" onClick={handleFetchData}>
            <div className="action-icon">
              <CloudDownload size={28} />
            </div>
            <h3>Sync Data</h3>
            <p>Pull latest records from connected hospital nodes.</p>
            {fetching && (
              <div className="action-status fetching">
                <Loader size={16} className="spinner" /> Syncing...
              </div>
            )}
            {fetchSuccess && (
              <div className="action-status success">
                <CheckCircle size={16} /> {fetchSuccess}
              </div>
            )}
          </div>

          <div className="action-card" onClick={() => setActiveTab('upload')}>
            <div className="action-icon" style={{ background: '#f0fdfa', color: '#0d9488' }}>
              <UploadCloud size={28} />
            </div>
            <h3>Upload</h3>
            <p>Add external reports or prescriptions manually.</p>
          </div>

          <div className="action-card" onClick={() => setActiveTab('share')}>
            <div className="action-icon" style={{ background: '#f5f3ff', color: '#7c3aed' }}>
              <Share2 size={28} />
            </div>
            <h3>Authorize</h3>
            <p>Grant secure, time-bound access to providers.</p>
          </div>
        </section>

        {/* Section C — Content Area */}
        <div className="content-card">
          <div className="tabs-header">
            <button className={`tab-link ${activeTab === 'records' ? 'active' : ''}`} onClick={() => setActiveTab('records')}>Timeline</button>
            <button className={`tab-link ${activeTab === 'share' ? 'active' : ''}`} onClick={() => setActiveTab('share')}>Consent</button>
            <button className={`tab-link ${activeTab === 'history' ? 'active' : ''}`} onClick={() => setActiveTab('history')}>Log</button>
          </div>

          <div className="tab-body fade-in">
            {activeTab === 'records' && <MedicalRecords />}
            {activeTab === 'upload' && <UploadRecords />}
            {activeTab === 'share' && <ShareAccess />}
            {activeTab === 'history' && <AccessHistory />}
            {activeTab === 'home' && (
              <div style={{ textAlign: 'center', padding: '3rem 0' }}>
                <Activity size={48} color="#3b82f6" style={{ margin: '0 auto 1rem' }} />
                <h3>Health Activity</h3>
                <p>No recent critical alerts detected in your network.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
