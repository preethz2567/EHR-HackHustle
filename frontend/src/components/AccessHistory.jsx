import { useState, useEffect } from 'react';
import { Clock, Loader, AlertCircle } from 'lucide-react';
import { getAuditLog } from '../utils/api';

export default function AccessHistory({ patientId }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await getAuditLog(patientId);
        setLogs(res.entries || []);
      } catch (err) {
        setError(err.message || 'Failed to fetch audit logs');
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, [patientId]);

  if (loading) {
    return (
      <div className="empty-state">
        <Loader size={32} className="spinner primary mx-auto" style={{ margin: '0 auto' }} />
        <p className="mt-4">Loading access history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="empty-state text-red-600">
        <AlertCircle size={48} style={{ margin: '0 auto' }} />
        <p className="mt-4">{error}</p>
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <div className="empty-state">
        <Clock size={48} style={{ margin: '0 auto' }} />
        <h3 className="mt-4">No Access History</h3>
        <p className="text-muted mt-2">There are no recorded access events for your account yet.</p>
      </div>
    );
  }

  const formatDate = (isoString) => {
    const d = new Date(isoString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    }).format(d);
  };

  return (
    <div>
      <div className="flex items-center gap-2 mb-6">
        <Clock size={24} className="text-muted" />
        <h3 style={{ margin: 0 }}>Security Audit Log</h3>
      </div>
      <p className="text-muted mb-6">A transparent record of who accessed your medical data and when.</p>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Event Type</th>
              <th>Actor</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, index) => (
              <tr key={index}>
                <td style={{ whiteSpace: 'nowrap' }} className="text-sm">
                  {formatDate(log.timestamp)}
                </td>
                <td>
                  <span className={`badge ${log.event_type.includes('AUTH') ? 'success' : 'primary'}`}>
                    {log.event_type.replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="font-semibold text-sm">
                  {log.actor_id} <span className="text-muted font-normal">({log.actor_role})</span>
                </td>
                <td className="text-sm text-muted">
                  {log.details}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
