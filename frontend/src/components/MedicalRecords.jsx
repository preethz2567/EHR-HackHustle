import { useState, useEffect } from 'react';
import { FileText, Loader, Download, ChevronDown, ChevronUp, Pill, Activity, Syringe, PlusSquare } from 'lucide-react';
import { getCachedData } from '../utils/api';

export default function MedicalRecords({ patientId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openSection, setOpenSection] = useState('diagnoses');

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
    window.addEventListener('refreshData', loadData);
    return () => window.removeEventListener('refreshData', loadData);
  }, [patientId]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <Loader size={32} className="spinner" style={{ margin: '0 auto', color: '#0284c7' }} />
        <p style={{ marginTop: '1rem', color: '#64748b' }}>Loading medical records...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
        <FileText size={48} style={{ margin: '0 auto', color: '#cbd5e1' }} />
        <h3 style={{ marginTop: '1rem', color: '#334155' }}>No Records Found</h3>
        <p style={{ color: '#64748b', marginTop: '0.5rem' }}>{error}</p>
      </div>
    );
  }

  const toggleSection = (section) => {
    setOpenSection(openSection === section ? '' : section);
  };

  const AccordionHeader = ({ id, title, icon: Icon, count }) => (
    <div 
      style={{ 
        display: 'flex', justifyContent: 'space-between', alignItems: 'center', 
        padding: '1rem 1.5rem', cursor: 'pointer', backgroundColor: openSection === id ? '#f0f9ff' : 'white',
        borderBottom: '1px solid #e2e8f0', transition: 'background-color 0.2s'
      }}
      onClick={() => toggleSection(id)}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#0f172a', fontWeight: '600' }}>
        <Icon size={20} style={{ color: '#0284c7' }} />
        {title}
        <span style={{ backgroundColor: '#e2e8f0', color: '#475569', fontSize: '0.75rem', padding: '0.1rem 0.5rem', borderRadius: '99px' }}>
          {count}
        </span>
      </div>
      <div>
        {openSection === id ? <ChevronUp size={20} color="#64748b"/> : <ChevronDown size={20} color="#64748b"/>}
      </div>
    </div>
  );

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#083344' }}>Comprehensive Record</h3>
        <button style={{ 
          display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem', 
          backgroundColor: 'white', border: '1px solid #cbd5e1', borderRadius: '6px', 
          color: '#334155', fontWeight: '500', cursor: 'pointer' 
        }}>
          <Download size={16} /> Download as PDF
        </button>
      </div>

      <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden' }}>
        
        {/* Diagnoses Accordion */}
        <AccordionHeader id="diagnoses" title="Diagnoses" icon={Activity} count={data.diagnoses?.length || 0} />
        {openSection === 'diagnoses' && (
          <div style={{ padding: '1.5rem', backgroundColor: 'white', borderBottom: '1px solid #e2e8f0' }}>
            {data.diagnoses?.length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1rem' }}>
                {data.diagnoses.map((d, i) => (
                  <div key={i} style={{ padding: '1rem', border: '1px solid #e2e8f0', borderRadius: '6px', backgroundColor: '#f8fafc' }}>
                    <div style={{ fontWeight: '600', color: '#0f172a', marginBottom: '0.25rem' }}>{d.name}</div>
                    <div style={{ fontSize: '0.875rem', color: '#64748b' }}>Diagnosed: {d.date_of_diagnosis}</div>
                    <div style={{ fontSize: '0.875rem', color: '#64748b' }}>ICD-10: {d.code}</div>
                  </div>
                ))}
              </div>
            ) : <p style={{ color: '#64748b' }}>No active diagnoses</p>}
          </div>
        )}

        {/* Medications Accordion */}
        <AccordionHeader id="medications" title="Medications" icon={Pill} count={data.medications?.length || 0} />
        {openSection === 'medications' && (
          <div style={{ padding: '1.5rem', backgroundColor: 'white', borderBottom: '1px solid #e2e8f0' }}>
            {data.medications?.length > 0 ? (
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #e2e8f0', color: '#475569' }}>
                    <th style={{ padding: '0.75rem' }}>Name</th>
                    <th style={{ padding: '0.75rem' }}>Dosage</th>
                    <th style={{ padding: '0.75rem' }}>Indication</th>
                    <th style={{ padding: '0.75rem' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.medications.map((m, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid #e2e8f0' }}>
                      <td style={{ padding: '1rem 0.75rem', fontWeight: '500', color: '#0f172a' }}>{m.name}</td>
                      <td style={{ padding: '1rem 0.75rem', color: '#334155' }}>{m.dosage}</td>
                      <td style={{ padding: '1rem 0.75rem', color: '#64748b' }}>{m.indication}</td>
                      <td style={{ padding: '1rem 0.75rem' }}>
                        <span style={{ backgroundColor: '#dcfce7', color: '#166534', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: '600' }}>Active</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : <p style={{ color: '#64748b' }}>No active medications</p>}
          </div>
        )}

        {/* Labs Accordion */}
        <AccordionHeader id="labs" title="Lab Results" icon={Syringe} count={data.labs?.length || 0} />
        {openSection === 'labs' && (
          <div style={{ padding: '1.5rem', backgroundColor: 'white', borderBottom: '1px solid #e2e8f0' }}>
            {data.labs?.length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
                {data.labs.map((l, i) => (
                  <div key={i} style={{ padding: '1rem', border: '1px solid #e2e8f0', borderRadius: '6px', borderLeft: '4px solid #0d9488' }}>
                    <div style={{ fontWeight: '600', color: '#0f172a' }}>{l.test_name}</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#0d9488', margin: '0.25rem 0' }}>{l.value}</div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Ref: {l.reference_range}</div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.5rem' }}>{l.date}</div>
                  </div>
                ))}
              </div>
            ) : <p style={{ color: '#64748b' }}>No recent labs</p>}
          </div>
        )}

        {/* Episodes Accordion */}
        <AccordionHeader id="episodes" title="Clinical Episodes" icon={PlusSquare} count={data.episodes?.length || 0} />
        {openSection === 'episodes' && (
          <div style={{ padding: '1.5rem', backgroundColor: 'white' }}>
            {data.episodes?.length > 0 ? (
              <div style={{ position: 'relative', borderLeft: '2px solid #e2e8f0', marginLeft: '1rem', paddingLeft: '1.5rem' }}>
                {data.episodes.map((e, i) => (
                  <div key={i} style={{ position: 'relative', marginBottom: '1.5rem' }}>
                    <div style={{ position: 'absolute', width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#0284c7', left: '-1.85rem', top: '0.25rem', border: '2px solid white' }}></div>
                    <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#0284c7', textTransform: 'capitalize' }}>{e.type}</div>
                    <div style={{ fontWeight: '600', color: '#0f172a', margin: '0.25rem 0' }}>{e.reason}</div>
                    <div style={{ fontSize: '0.875rem', color: '#64748b' }}>{e.date} • Duration: {e.duration_days} days</div>
                    <div style={{ fontSize: '0.875rem', color: '#475569', marginTop: '0.25rem' }}>Outcome: {e.outcome}</div>
                  </div>
                ))}
              </div>
            ) : <p style={{ color: '#64748b' }}>No recent episodes</p>}
          </div>
        )}

      </div>
    </div>
  );
}
