import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, LogOut, CloudDownload, Loader, CheckCircle } from 'lucide-react';
import { fetchHistoricalData } from '../utils/api';
import MedicalRecords from '../components/MedicalRecords';
import UploadRecords from '../components/UploadRecords';
import ShareAccess from '../components/ShareAccess';
import AccessHistory from '../components/AccessHistory';

export default function Dashboard() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('records');
  const [fetching, setFetching] = useState(false);
  const [fetchSuccess, setFetchSuccess] = useState(null);
  const [patientId] = useState('P001'); // In real app, decode from JWT

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
        setFetchSuccess(`Data cached! You have ${res.records_count} records.`);
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

  const tabs = [
    { id: 'records', label: 'My Medical Records' },
    { id: 'upload', label: 'Upload Records' },
    { id: 'share', label: 'Share Access' },
    { id: 'history', label: 'Access History' },
  ];

  return (
    <div className="app-layout">
      <header className="topbar">
        <div className="topbar-brand">
          <Activity size={24} />
          <span>Patient Portal</span>
        </div>
        <div className="topbar-actions">
          <span className="text-sm font-semibold text-muted">Patient: {patientId}</span>
          <button className="outline" onClick={handleLogout}>
            <LogOut size={16} /> Logout
          </button>
        </div>
      </header>

      <main className="main-content container">
        <div className="dashboard-header">
          <div>
            <h1>Unified Health Record</h1>
            <p className="text-muted mt-1">Manage your complete medical history securely.</p>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <button onClick={handleFetchData} disabled={fetching}>
              {fetching ? (
                <><Loader size={16} className="spinner" /> Fetching...</>
              ) : (
                <><CloudDownload size={16} /> Fetch Historical Data</>
              )}
            </button>
            {fetchSuccess && (
              <span className="text-sm text-green-600 mt-2 flex items-center gap-1 font-semibold">
                <CheckCircle size={14} /> {fetchSuccess}
              </span>
            )}
          </div>
        </div>

        <div className="tabs-container">
          <div className="tabs-list">
            {tabs.map(tab => (
              <button
                key={tab.id}
                className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="tab-content">
          {activeTab === 'records' && <MedicalRecords patientId={patientId} />}
          {activeTab === 'upload' && <UploadRecords patientId={patientId} />}
          {activeTab === 'share' && <ShareAccess patientId={patientId} />}
          {activeTab === 'history' && <AccessHistory patientId={patientId} />}
        </div>
      </main>
    </div>
  );
}
