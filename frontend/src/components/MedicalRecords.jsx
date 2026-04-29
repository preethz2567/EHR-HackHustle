import { useState, useEffect } from 'react';
import { FileText, Loader, Download } from 'lucide-react';
import { getCachedData } from '../utils/api';

export default function MedicalRecords({ patientId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await getCachedData(patientId);
      setData(res.data);
    } catch (err) {
      if (err.message.includes('404') || err.message.includes('No cached data')) {
        setError('No historical data found. Please fetch from providers using the button above.');
      } else {
        setError(err.message || 'Failed to load medical records');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();

    // Listen for refresh event
    window.addEventListener('refreshData', loadData);
    return () => window.removeEventListener('refreshData', loadData);
  }, [patientId]);

  if (loading) {
    return (
      <div className="empty-state">
        <Loader size={32} className="spinner primary mx-auto" style={{ margin: '0 auto' }} />
        <p className="mt-4">Loading medical records...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="empty-state">
        <FileText size={48} style={{ margin: '0 auto' }} />
        <h3 className="mt-4">No Records Found</h3>
        <p className="text-muted mt-2">{error}</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h3>EHR Summary</h3>
        <button className="outline text-sm">
          <Download size={16} /> View as PDF
        </button>
      </div>

      <div className="data-grid">
        <div className="card data-card">
          <div className="data-card-header">
            <h4 className="data-card-title">Diagnoses</h4>
            <span className="badge primary">{data.diagnoses?.length || 0}</span>
          </div>
          {data.diagnoses?.length > 0 ? (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {data.diagnoses.map((d, i) => (
                <li key={i} className="mb-2 pb-2" style={{ borderBottom: '1px solid var(--border)' }}>
                  <div className="font-semibold">{d.name}</div>
                  <div className="text-sm text-muted">Code: {d.code} • Date: {d.date_of_diagnosis}</div>
                </li>
              ))}
            </ul>
          ) : <p className="text-muted text-sm">No active diagnoses</p>}
        </div>

        <div className="card data-card">
          <div className="data-card-header">
            <h4 className="data-card-title">Medications</h4>
            <span className="badge warning">{data.medications?.length || 0}</span>
          </div>
          {data.medications?.length > 0 ? (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {data.medications.map((m, i) => (
                <li key={i} className="mb-2 pb-2" style={{ borderBottom: '1px solid var(--border)' }}>
                  <div className="font-semibold">{m.name} {m.dosage}</div>
                  <div className="text-sm text-muted">Indication: {m.indication}</div>
                </li>
              ))}
            </ul>
          ) : <p className="text-muted text-sm">No active medications</p>}
        </div>

        <div className="card data-card">
          <div className="data-card-header">
            <h4 className="data-card-title">Lab Results</h4>
            <span className="badge success">{data.labs?.length || 0}</span>
          </div>
          {data.labs?.length > 0 ? (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {data.labs.map((l, i) => (
                <li key={i} className="mb-2 pb-2" style={{ borderBottom: '1px solid var(--border)' }}>
                  <div className="font-semibold">{l.test_name}: {l.value}</div>
                  <div className="text-sm text-muted">Ref: {l.reference_range} • Date: {l.date}</div>
                </li>
              ))}
            </ul>
          ) : <p className="text-muted text-sm">No recent labs</p>}
        </div>

        <div className="card data-card">
          <div className="data-card-header">
            <h4 className="data-card-title">Clinical Episodes</h4>
            <span className="badge neutral">{data.episodes?.length || 0}</span>
          </div>
          {data.episodes?.length > 0 ? (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {data.episodes.map((e, i) => (
                <li key={i} className="mb-2 pb-2" style={{ borderBottom: '1px solid var(--border)' }}>
                  <div className="font-semibold capitalize">{e.type}</div>
                  <div className="text-sm text-muted">Reason: {e.reason}</div>
                  <div className="text-sm text-muted">Date: {e.date} • Duration: {e.duration_days} days</div>
                </li>
              ))}
            </ul>
          ) : <p className="text-muted text-sm">No recent episodes</p>}
        </div>
      </div>
    </div>
  );
}
