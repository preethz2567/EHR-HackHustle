import { useState, useEffect } from 'react';
import {
  FileText, Loader, Download, ChevronDown, ChevronUp,
  Pill, Activity, TestTube2, CalendarClock,
} from 'lucide-react';
import { getCachedData, exportMedicalRecordsPdf } from '../utils/api';

/* inline colour tokens so every sub-component stays consistent */
const C = {
  blue: '#1e40af', teal: '#10b981', gray: '#f3f4f6',
  border: '#e5e7eb', text: '#111827', muted: '#6b7280',
};

export default function MedicalRecords({ patientId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [open, setOpen] = useState('diagnoses');

  const load = async () => {
    setLoading(true); setError('');
    try { const r = await getCachedData(patientId); setData(r.data); }
    catch (e) {
      setError(
        e.message?.includes('404') || e.message?.includes('No cached')
          ? 'No historical data found. Please fetch from providers first.'
          : e.message || 'Failed to load records',
      );
    } finally { setLoading(false); }
  };

  useEffect(() => {
    load();
    window.addEventListener('refreshData', load);
    return () => window.removeEventListener('refreshData', load);
  }, [patientId]);

  if (loading)
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <Loader size={28} className="spinner" style={{ margin: '0 auto', color: C.blue }} />
        <p style={{ marginTop: '0.85rem', color: C.muted }}>Loading medical records…</p>
      </div>
    );

  if (error || !data)
    return (
      <div style={{ textAlign: 'center', padding: '3rem', background: C.gray, borderRadius: 8 }}>
        <FileText size={44} style={{ margin: '0 auto', color: '#d1d5db' }} />
        <h3 style={{ marginTop: '0.85rem', color: C.text }}>No Records Found</h3>
        <p style={{ color: C.muted, marginTop: '0.35rem' }}>{error}</p>
      </div>
    );

  const toggle = (id) => setOpen(open === id ? '' : id);

  const Header = ({ id, title, icon: Icon, count }) => (
    <div
      onClick={() => toggle(id)}
      style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '0.85rem 1.15rem', cursor: 'pointer',
        background: open === id ? '#eff6ff' : '#fff',
        borderBottom: `1px solid ${C.border}`, transition: 'background 0.15s',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', fontWeight: 600, color: C.text }}>
        <Icon size={18} style={{ color: C.blue }} />
        {title}
        <span style={{ background: '#e5e7eb', color: '#4b5563', fontSize: '0.7rem', padding: '0.1rem 0.45rem', borderRadius: 99 }}>
          {count}
        </span>
      </div>
      {open === id ? <ChevronUp size={18} color={C.muted} /> : <ChevronDown size={18} color={C.muted} />}
    </div>
  );

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.15rem' }}>
        <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: C.blue }}>Comprehensive EHR Summary</h3>
        <button 
          onClick={async () => {
            try {
              const res = await exportMedicalRecordsPdf(patientId);
              if (res.download_url) {
                const a = document.createElement('a');
                a.href = `http://127.0.0.1:5000${res.download_url}`;
                a.download = res.filename || 'report.pdf';
                document.body.appendChild(a);
                a.click();
                a.remove();
              }
            } catch (err) {
              alert(err.message || 'Failed to download PDF');
            }
          }}
          style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.4rem 0.85rem', background: '#fff', border: `1px solid ${C.border}`, borderRadius: 6, color: C.text, fontWeight: 500, cursor: 'pointer', fontSize: '0.85rem' }}
        >
          <Download size={15} /> Download as PDF
        </button>
      </div>

      <div style={{ border: `1px solid ${C.border}`, borderRadius: 8, overflow: 'hidden' }}>
        {/* Diagnoses */}
        <Header id="diagnoses" title="Diagnoses" icon={Activity} count={data.diagnoses?.length || 0} />
        {open === 'diagnoses' && (
          <div style={{ padding: '1.15rem', background: '#fff', borderBottom: `1px solid ${C.border}` }}>
            {data.diagnoses?.length ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(240px,1fr))', gap: '0.85rem' }}>
                {data.diagnoses.map((d, i) => (
                  <div key={i} style={{ padding: '0.85rem', border: `1px solid ${C.border}`, borderRadius: 6, background: C.gray }}>
                    <div style={{ fontWeight: 600, color: C.text, marginBottom: '0.2rem' }}>{d.name}</div>
                    <div style={{ fontSize: '0.825rem', color: C.muted }}>Diagnosed: {d.date_of_diagnosis}</div>
                    <div style={{ fontSize: '0.825rem', color: C.muted }}>ICD-10: {d.code}</div>
                  </div>
                ))}
              </div>
            ) : <p style={{ color: C.muted }}>No active diagnoses</p>}
          </div>
        )}

        {/* Medications */}
        <Header id="medications" title="Medications" icon={Pill} count={data.medications?.length || 0} />
        {open === 'medications' && (
          <div style={{ padding: '1.15rem', background: '#fff', borderBottom: `1px solid ${C.border}` }}>
            {data.medications?.length ? (
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: `2px solid ${C.border}`, color: '#4b5563' }}>
                    <th style={{ padding: '0.6rem' }}>Name</th>
                    <th style={{ padding: '0.6rem' }}>Dosage</th>
                    <th style={{ padding: '0.6rem' }}>Indication</th>
                    <th style={{ padding: '0.6rem' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.medications.map((m, i) => (
                    <tr key={i} style={{ borderBottom: `1px solid ${C.border}` }}>
                      <td style={{ padding: '0.75rem 0.6rem', fontWeight: 500 }}>{m.name}</td>
                      <td style={{ padding: '0.75rem 0.6rem', color: '#374151' }}>{m.dosage}</td>
                      <td style={{ padding: '0.75rem 0.6rem', color: C.muted }}>{m.indication}</td>
                      <td style={{ padding: '0.75rem 0.6rem' }}>
                        <span style={{ background: '#d1fae5', color: '#065f46', padding: '0.15rem 0.45rem', borderRadius: 4, fontSize: '0.7rem', fontWeight: 600 }}>Active</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : <p style={{ color: C.muted }}>No active medications</p>}
          </div>
        )}

        {/* Labs */}
        <Header id="labs" title="Lab Results" icon={TestTube2} count={data.labs?.length || 0} />
        {open === 'labs' && (
          <div style={{ padding: '1.15rem', background: '#fff', borderBottom: `1px solid ${C.border}` }}>
            {data.labs?.length ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(190px,1fr))', gap: '0.85rem' }}>
                {data.labs.map((l, i) => (
                  <div key={i} style={{ padding: '0.85rem', border: `1px solid ${C.border}`, borderRadius: 6, borderLeft: `4px solid ${C.teal}` }}>
                    <div style={{ fontWeight: 600 }}>{l.test_name}</div>
                    <div style={{ fontSize: '1.35rem', fontWeight: 700, color: C.teal, margin: '0.15rem 0' }}>{l.value}</div>
                    <div style={{ fontSize: '0.75rem', color: C.muted }}>Ref: {l.reference_range}</div>
                    <div style={{ fontSize: '0.75rem', color: C.muted, marginTop: '0.35rem' }}>{l.date}</div>
                  </div>
                ))}
              </div>
            ) : <p style={{ color: C.muted }}>No recent labs</p>}
          </div>
        )}

        {/* Episodes */}
        <Header id="episodes" title="Clinical Episodes" icon={CalendarClock} count={data.episodes?.length || 0} />
        {open === 'episodes' && (
          <div style={{ padding: '1.15rem', background: '#fff' }}>
            {data.episodes?.length ? (
              <div style={{ position: 'relative', borderLeft: `2px solid ${C.border}`, marginLeft: '0.85rem', paddingLeft: '1.25rem' }}>
                {data.episodes.map((e, i) => (
                  <div key={i} style={{ position: 'relative', marginBottom: '1.25rem' }}>
                    <div style={{ position: 'absolute', width: 10, height: 10, borderRadius: '50%', background: C.blue, left: '-1.6rem', top: '0.3rem', border: '2px solid #fff' }} />
                    <div style={{ fontSize: '0.825rem', fontWeight: 600, color: C.blue, textTransform: 'capitalize' }}>{e.type}</div>
                    <div style={{ fontWeight: 600, color: C.text, margin: '0.15rem 0' }}>{e.reason}</div>
                    <div style={{ fontSize: '0.825rem', color: C.muted }}>{e.date} · Duration: {e.duration_days} days</div>
                    <div style={{ fontSize: '0.825rem', color: '#374151', marginTop: '0.15rem' }}>Outcome: {e.outcome}</div>
                  </div>
                ))}
              </div>
            ) : <p style={{ color: C.muted }}>No recent episodes</p>}
          </div>
        )}
      </div>
    </div>
  );
}
