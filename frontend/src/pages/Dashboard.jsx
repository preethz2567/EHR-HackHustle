import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Activity, LogOut, CloudDownload, Loader, CheckCircle, 
  Home, FileText, UploadCloud, Share2, History, Settings,
  Bell, User, HeartPulse
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
  const [patientId] = useState('P001'); // In real app, decode from JWT
  
  // Mock quick stats
  const [stats, setStats] = useState({
    diagnoses: 3,
    medications: 4,
    labs: 15,
    lastUpdated: '29-Apr-2026 14:30',
    activeAuths: 1
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
        setFetchSuccess(`Data cached successfully! ${res.records_count || 45} records fetched.`);
        setStats(prev => ({ ...prev, lastUpdated: new Date().toLocaleString() }));
        // Dispatch an event to notify sub-components (MedicalRecords) to refresh
        window.dispatchEvent(new Event('refreshData'));
      }
    } catch (err) {
      alert(err.message || 'Failed to fetch historical data');
    } finally {
      setFetching(false);
      // Clear success message after 5 seconds
      setTimeout(() => setFetchSuccess(null), 5000);
    }
  };

  const sidebarLinks = [
    { id: 'home', icon: Home, label: 'Dashboard' },
    { id: 'records', icon: FileText, label: 'Medical Records' },
    { id: 'upload', icon: UploadCloud, label: 'Upload Reports' },
    { id: 'share', icon: Share2, label: 'Share Access' },
    { id: 'history', icon: History, label: 'Access History' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ];

  const handleNavigation = (id) => {
    if (['records', 'upload', 'share', 'history'].includes(id)) {
      setActiveTab(id);
    } else {
      setActiveTab('records'); // Fallback or implement views
    }
  };

  return (
    <div className="patient-dashboard">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <HeartPulse size={28} className="text-teal" />
          <span className="brand-text">HealthBridge</span>
        </div>

        <nav className="sidebar-nav">
          {sidebarLinks.map(link => (
            <button 
              key={link.id} 
              className={`nav-item ${activeTab === link.id || (link.id === 'home' && activeTab === 'records') ? 'active' : ''}`}
              onClick={() => handleNavigation(link.id)}
            >
              <link.icon size={20} />
              <span>{link.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button className="nav-item text-danger" onClick={handleLogout}>
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="main-wrapper">
        {/* Topbar */}
        <header className="topbar">
          <div className="topbar-search">
            {/* Can add search here later */}
          </div>
          <div className="topbar-actions">
            <button className="icon-btn">
              <Bell size={20} />
              <span className="notification-dot"></span>
            </button>
            <div className="user-profile">
              <div className="avatar">
                <User size={18} />
              </div>
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
            <p className="text-muted">Manage your complete medical history securely.</p>
          </div>

          {/* Section A: Quick Stats */}
          <section className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon-wrapper bg-blue-100 text-blue">
                <FileText size={24} />
              </div>
              <div className="stat-info">
                <h3>Records Cached</h3>
                <p>{stats.diagnoses} Diagnoses • {stats.medications} Meds • {stats.labs} Labs</p>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon-wrapper bg-teal-100 text-teal">
                <History size={24} />
              </div>
              <div className="stat-info">
                <h3>Last Updated</h3>
                <p>{stats.lastUpdated}</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon-wrapper bg-purple-100 text-purple">
                <ShieldCheck size={24} />
              </div>
              <div className="stat-info">
                <h3>Active Authorizations</h3>
                <p>{stats.activeAuths} Doctors currently have access</p>
              </div>
            </div>
          </section>

          {/* Section B: Action Buttons */}
          <section className="actions-grid">
            <div className="action-card primary" onClick={handleFetchData}>
              <CloudDownload size={32} className="action-icon" />
              <h3>Fetch Historical Data</h3>
              <p>Pull recent records from all your connected hospitals</p>
              {fetching && <div className="action-status fetching"><Loader size={16} className="spinner"/> Fetching from hospitals...</div>}
              {fetchSuccess && <div className="action-status success"><CheckCircle size={16}/> {fetchSuccess}</div>}
            </div>

            <div className="action-card secondary" onClick={() => setActiveTab('upload')}>
              <UploadCloud size={32} className="action-icon" />
              <h3>Upload New Report</h3>
              <p>Add vaccine cards, external lab reports, or discharge summaries</p>
            </div>

            <div className="action-card tertiary" onClick={() => setActiveTab('share')}>
              <Share2 size={32} className="action-icon" />
              <h3>Share with Doctor</h3>
              <p>Generate a secure, time-limited access token for your physician</p>
            </div>
          </section>

          {/* Section C: Tab Content */}
          <section className="tabs-section">
            <div className="content-card">
              <div className="tabs-header">
                <button className={`tab-link ${activeTab === 'records' ? 'active' : ''}`} onClick={() => setActiveTab('records')}>
                  My Medical Records
                </button>
                <button className={`tab-link ${activeTab === 'upload' ? 'active' : ''}`} onClick={() => setActiveTab('upload')}>
                  Upload Reports
                </button>
                <button className={`tab-link ${activeTab === 'share' ? 'active' : ''}`} onClick={() => setActiveTab('share')}>
                  Share Access
                </button>
                <button className={`tab-link ${activeTab === 'history' ? 'active' : ''}`} onClick={() => setActiveTab('history')}>
                  Access History
                </button>
              </div>

              <div className="tab-body">
                {activeTab === 'records' && <MedicalRecords patientId={patientId} />}
                {activeTab === 'upload' && <UploadRecords patientId={patientId} />}
                {activeTab === 'share' && <ShareAccess patientId={patientId} />}
                {activeTab === 'history' && <AccessHistory patientId={patientId} />}
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}


