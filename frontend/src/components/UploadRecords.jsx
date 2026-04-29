import { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle, Trash2, X } from 'lucide-react';
import { uploadManualRecord } from '../utils/api';

const C = { blue: '#1e40af', teal: '#10b981', border: '#e5e7eb', muted: '#6b7280', text: '#111827', gray: '#f3f4f6' };

export default function UploadRecords({ patientId }) {
  const [file, setFile] = useState(null);
  const [docType, setDocType] = useState('vaccine_card');
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [drag, setDrag] = useState(false);
  const ref = useRef(null);

  const [files, setFiles] = useState([
    { id: 1, name: 'COVID_Vaccine_Certificate.pdf', date: '28-Apr-2024', type: 'Vaccine Card', status: 'Merged' },
    { id: 2, name: 'Blood_Test_Apollo.jpg', date: '29-Apr-2024', type: 'Lab Report', status: 'Pending' },
  ]);

  const upload = async () => {
    if (!file) { setError('Please select a file first.'); return; }
    setUploading(true); setError(''); setSuccess('');
    try {
      const res = await uploadManualRecord(patientId, file);
      const fileType = res.file_type || 'other';
      const typeLabel = fileType === 'vaccine_card' ? 'Vaccine Card' : fileType === 'lab_report' ? 'Lab Report' : fileType === 'discharge_summary' ? 'Discharge Summary' : 'Document';
      setSuccess(`File uploaded successfully! Detected as: ${typeLabel}`);
      setFiles([{ id: Date.now(), name: res.filename || file.name, date: new Date().toLocaleDateString('en-GB',{day:'2-digit',month:'short',year:'numeric'}), type: typeLabel, status: res.merged ? 'Merged' : 'Pending' }, ...files]);
      setFile(null);
      window.dispatchEvent(new Event('refreshData'));
    } catch (e) { setError(e.message || 'Upload failed. Please try again.'); }
    finally { setUploading(false); setTimeout(() => setSuccess(''), 4000); }
  };

  return (
    <div>
      <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: C.blue, marginBottom: '0.35rem' }}>Upload Reports</h3>
      <p style={{ color: C.muted, marginBottom: '1.25rem' }}>Upload external records to consolidate your medical history.</p>

      {error && <div style={{ background: '#fef2f2', color: '#991b1b', padding: '0.6rem 0.85rem', borderRadius: 8, marginBottom: '0.85rem', borderLeft: '4px solid #ef4444', fontSize: '0.875rem' }}>{error}</div>}
      {success && <div style={{ background: '#ecfdf5', color: '#065f46', padding: '0.6rem 0.85rem', borderRadius: 8, marginBottom: '0.85rem', borderLeft: `4px solid ${C.teal}`, display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.875rem' }}><CheckCircle size={16} /> {success}</div>}

      <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
        {/* Upload form */}
        <div style={{ flex: 1, minWidth: 280 }}>
          <div style={{ marginBottom: '0.85rem' }}>
            <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 600, color: '#374151', marginBottom: '0.35rem', textTransform: 'uppercase', letterSpacing: '0.03em' }}>Document Type</label>
            <select value={docType} onChange={e => setDocType(e.target.value)} style={{ width: '100%', padding: '0.6rem', borderRadius: 6, border: `1.5px solid #d1d5db`, background: '#fff' }}>
              <option value="vaccine_card">Vaccine Card</option>
              <option value="lab_report">Lab Report</option>
              <option value="prescription">Prescription</option>
              <option value="discharge_summary">Discharge Summary</option>
            </select>
          </div>

          <div
            onDragOver={e => { e.preventDefault(); setDrag(true); }}
            onDragLeave={() => setDrag(false)}
            onDrop={e => { e.preventDefault(); setDrag(false); if (e.dataTransfer.files?.[0]) setFile(e.dataTransfer.files[0]); }}
            onClick={() => ref.current?.click()}
            style={{ border: `2px dashed ${drag ? C.blue : '#d1d5db'}`, background: drag ? '#eff6ff' : C.gray, borderRadius: 8, padding: '2.5rem 1.5rem', textAlign: 'center', cursor: 'pointer', transition: 'all 0.15s', marginBottom: '1rem' }}
          >
            <input type="file" ref={ref} style={{ display: 'none' }} onChange={e => { if (e.target.files?.[0]) setFile(e.target.files[0]); }} />
            {file ? (
              <>
                <FileText size={40} style={{ margin: '0 auto', color: C.blue }} />
                <h4 style={{ marginTop: '0.75rem' }}>{file.name}</h4>
                <p style={{ color: C.muted, fontSize: '0.825rem' }}>{(file.size/1024).toFixed(1)} KB</p>
                <button onClick={e => { e.stopPropagation(); setFile(null); }} style={{ marginTop: '0.6rem', padding: '0.2rem 0.6rem', background: 'transparent', border: `1px solid #ef4444`, color: '#ef4444', borderRadius: 4, cursor: 'pointer', fontSize: '0.825rem' }}>Clear</button>
              </>
            ) : (
              <>
                <UploadCloud size={40} style={{ margin: '0 auto', color: '#9ca3af' }} />
                <h4 style={{ marginTop: '0.75rem', fontWeight: 600 }}>Drag vaccine cards, lab reports, discharge summaries here</h4>
                <p style={{ color: C.blue, fontSize: '0.85rem', fontWeight: 500, marginTop: '0.35rem' }}>OR Click to browse</p>
                <p style={{ color: '#9ca3af', fontSize: '0.75rem', marginTop: '0.85rem' }}>Supported: PDF, JPG, PNG (Max 5 MB)</p>
              </>
            )}
          </div>

          <button onClick={upload} disabled={!file || uploading} style={{ width: '100%', padding: '0.75rem', background: (!file || uploading) ? '#d1d5db' : C.teal, color: '#fff', border: 'none', borderRadius: 6, fontWeight: 600, cursor: (!file||uploading) ? 'not-allowed' : 'pointer' }}>
            {uploading ? 'Uploading…' : 'Upload Document'}
          </button>
        </div>

        {/* Uploaded files list */}
        <div style={{ flex: 1, minWidth: 280 }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: C.text, marginBottom: '0.85rem' }}>Previously Uploaded</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {files.map(f => (
              <div key={f.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.85rem', background: '#fff', border: `1px solid ${C.border}`, borderRadius: 8 }}>
                <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'flex-start' }}>
                  <FileText size={18} style={{ color: C.muted, marginTop: 2 }} />
                  <div>
                    <div style={{ fontWeight: 500, fontSize: '0.85rem', wordBreak: 'break-all' }}>{f.name}</div>
                    <div style={{ fontSize: '0.75rem', color: C.muted }}>{f.date} · {f.type}</div>
                    {f.status === 'Merged' ? (
                      <div style={{ fontSize: '0.75rem', color: '#059669', fontWeight: 600, marginTop: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                        <CheckCircle size={11} /> Merged into your records
                      </div>
                    ) : (
                      <div style={{ fontSize: '0.75rem', color: '#d97706', fontWeight: 600, marginTop: '0.25rem' }}>Pending verification</div>
                    )}
                  </div>
                </div>
                <button onClick={() => setFiles(files.filter(x => x.id !== f.id))} style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', padding: '0.35rem' }}><Trash2 size={15} /></button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
