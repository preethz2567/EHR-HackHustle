import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  HeartPulse, LogOut, CloudDownload, Loader, CheckCircle,
  Home, FileText, UploadCloud, Share2, History, Settings,
  Bell, User, ShieldCheck
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
  const [patientId] = useState('P001');

  const [stats] = useState({
    diagnoses: 3, medications: 4, labs: 15,
    lastUpdated: '29-Apr-2026 14:30',
    activeAuths: 0,
  });

  const handleLogout = () => {
    localStorage.removeItem('patientToken');
    navigate('/login');
  };

  const handleFetchData = async () => {
    setFetching(true);
    setFetchSuccess(null);
    try {
      const res = await fetchHistoricalData(patientId);
      if (res.success) {
        setFetchSuccess(
          `Data cached successfully! ${res.records_count || 45} records fetched.`
        );
        window.dispatchEvent(new Event('refreshData'));
      }
    } catch (err) {
      alert(err.message || 'Failed to fetch historical data');
    } finally {
      setFetching(false);
      setTimeout(() => setFetchSuccess(null), 5000);
    }
  };

  const sidebarLinks = [
    { id: 'home',     icon: Home,        label: 'Dashboard' },
    { id: 'records',  icon: FileText,    label: 'Medical Records' },
    { id: 'upload',   icon: UploadCloud, label: 'Upload Reports' },
    { id: 'share',    icon: Share2,      label: 'Share Access' },
    { id: 'history',  icon: History,     label: 'Access History' },
    { id: 'settings', icon: Settings,    label: 'Settings' },
  ];

  const go = (id) => {
    if (['records', 'upload', 'share', 'history'].includes(id)) setActiveTab(id);
    else setActiveTab('records');
  };

  return (
    <div className="patient-dashboard">
      {/* ======== Sidebar ======== */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <HeartPulse size={26} style={{ color: '#10b981' }} />
          <span className="brand-text">HealthBridge</span>
        </div>

        <nav className="sidebar-nav">
          {sidebarLinks.map((l) => (
            <button
              key={l.id}
              className={`nav-item ${
                activeTab === l.id || (l.id === 'home' && activeTab === 'records')
                  ? 'active'
                  : ''
              }`}
              onClick={() => go(l.id)}
            >
              <l.icon size={19} />
              <span>{l.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button className="nav-item text-danger" onClick={handleLogout}>
            <LogOut size={19} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* ======== Main Area ======== */}
      <div className="main-wrapper">
        {/* Top bar */}
        <header className="topbar">
          <div className="topbar-actions">
            <button className="icon-btn">
              <Bell size={19} />
              <span className="notification-dot" />
            </button>
            <div className="user-profile">
              <div className="avatar"><User size={17} /></div>
              <div className="user-info">
                <span className="user-name">Rajesh Patel ({patientId})</span>
                <span className="user-role">Patient</span>
              </div>
            </div>
          </div>
        </header>

        <main className="dashboard-content">
          <div className="page-header">
            <h1>Patient Dashboard</h1>
            <p className="text-muted">
              Manage your complete medical history securely.
            </p>
          </div>

          {/* Section A — Quick Stats */}
          <section className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon-wrapper bg-blue-100 text-blue">
                <FileText size={22} />
              </div>
              <div className="stat-info">
                <h3>Records Cached</h3>
                <p>
                  {stats.diagnoses} Diagnoses · {stats.medications} Meds ·{' '}
                  {stats.labs} Labs
                </p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon-wrapper bg-teal-100 text-teal">
                <History size={22} />
              </div>
              <div className="stat-info">
                <h3>Last Updated</h3>
                <p>{stats.lastUpdated}</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon-wrapper bg-purple-100 text-purple">
                <ShieldCheck size={22} />
              </div>
              <div className="stat-info">
                <h3>Active Authorizations</h3>
                <p>{stats.activeAuths} doctors</p>
              </div>
            </div>
          </section>

          {/* Section B — Action Buttons */}
          <section className="actions-grid">
            <div className="action-card primary" onClick={handleFetchData}>
              <CloudDownload size={28} className="action-icon" />
              <h3>Fetch Historical Data</h3>
              <p>Pull recent records from all your connected hospitals</p>
              {fetching && (
                <div className="action-status fetching">
                  <Loader size={15} className="spinner" /> Fetching from
                  Hospital A, B, C…
                </div>
              )}
              {fetchSuccess && (
                <div className="action-status success">
                  <CheckCircle size={15} /> {fetchSuccess}
                </div>
              )}
            </div>

            <div
              className="action-card secondary"
              onClick={() => setActiveTab('upload')}
            >
              <UploadCloud size={28} className="action-icon" />
              <h3>Upload New Report</h3>
              <p>Add vaccine cards, external lab reports, or discharge summaries</p>
            </div>

            <div
              className="action-card tertiary"
              onClick={() => setActiveTab('share')}
            >
              <Share2 size={28} className="action-icon" />
              <h3>Share with Doctor</h3>
              <p>Generate a secure, time-limited access token for your physician</p>
            </div>
          </section>

          {/* Section C — Tabs */}
          <section className="tabs-section">
            <div className="content-card">
              <div className="tabs-header">
                {[
                  { id: 'records', label: 'My Medical Records' },
                  { id: 'upload',  label: 'Upload Reports' },
                  { id: 'share',   label: 'Share Access' },
                  { id: 'history', label: 'Access History' },
                ].map((t) => (
                  <button
                    key={t.id}
                    className={`tab-link ${activeTab === t.id ? 'active' : ''}`}
                    onClick={() => setActiveTab(t.id)}
                  >
                    {t.label}
                  </button>
                ))}
              </div>

              <div className="tab-body">
                {activeTab === 'records' && (
                  <MedicalRecords patientId={patientId} />
                )}
                {activeTab === 'upload' && (
                  <UploadRecords patientId={patientId} />
                )}
                {activeTab === 'share' && (
                  <ShareAccess patientId={patientId} />
                )}
                {activeTab === 'history' && (
                  <AccessHistory patientId={patientId} />
                )}
              </div>
            </div>
          </section>
        </main>

        {/* Dashboard Footer */}
        <footer className="dashboard-footer">
          <span>Last login: 29-Apr-2026 14:32 · Session: Active</span>
          <a href="#">Help &amp; Support</a>
        </footer>
      </div>
    </div>
  );
}
