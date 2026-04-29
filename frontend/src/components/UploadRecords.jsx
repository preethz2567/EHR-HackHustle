import { useState, useRef } from 'react';
import { UploadCloud, FileText, X, CheckCircle, Trash2 } from 'lucide-react';
import { uploadManualRecord } from '../utils/api';

export default function UploadRecords({ patientId }) {
  const [file, setFile] = useState(null);
  const [docType, setDocType] = useState('vaccine_card');
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  // Mock list of uploaded files
  const [uploadedFiles, setUploadedFiles] = useState([
    { id: 1, name: 'COVID_Vaccine_Certificate.pdf', date: '28-Apr-2024 10:30', type: 'Vaccine Card', status: 'Merged' },
    { id: 2, name: 'Blood_Test_Report_Apollo.jpg', date: '29-Apr-2024 09:15', type: 'Lab Report', status: 'Pending' }
  ]);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDelete = (id) => {
    setUploadedFiles(uploadedFiles.filter(f => f.id !== id));
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first.');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');

    try {
      await uploadManualRecord(patientId, docType, file);
      setSuccess('File uploaded successfully!');
      
      // Add to list
      const newFile = {
        id: Date.now(),
        name: file.name,
        date: new Date().toLocaleString(),
        type: docType === 'vaccine_card' ? 'Vaccine Card' : docType === 'lab_report' ? 'Lab Report' : 'Prescription',
        status: 'Pending'
      };
      setUploadedFiles([newFile, ...uploadedFiles]);
      setFile(null);
      
      window.dispatchEvent(new Event('refreshData'));
    } catch (err) {
      setError(err.message || 'Failed to upload document');
    } finally {
      setUploading(false);
      setTimeout(() => setSuccess(''), 4000);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#083344', marginBottom: '0.5rem' }}>Upload Reports</h3>
        <p style={{ color: '#64748b' }}>Upload external records to consolidate your medical history.</p>
      </div>

      {error && <div style={{ backgroundColor: '#fef2f2', color: '#b91c1c', padding: '0.75rem 1rem', borderRadius: '6px', marginBottom: '1rem', borderLeft: '4px solid #ef4444' }}>{error}</div>}
      {success && <div style={{ backgroundColor: '#f0fdf4', color: '#15803d', padding: '0.75rem 1rem', borderRadius: '6px', marginBottom: '1rem', borderLeft: '4px solid #22c55e', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><CheckCircle size={18} /> {success}</div>}

      <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
        {/* Upload Form */}
        <div style={{ flex: '1', minWidth: '300px' }}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: '#334155', marginBottom: '0.5rem' }}>Document Type</label>
            <select 
              value={docType} 
              onChange={(e) => setDocType(e.target.value)}
              style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid #cbd5e1', backgroundColor: 'white' }}
            >
              <option value="vaccine_card">Vaccine Card</option>
              <option value="lab_report">Lab Report</option>
              <option value="prescription">Prescription</option>
              <option value="discharge_summary">Discharge Summary</option>
            </select>
          </div>

          <div 
            style={{
              border: `2px dashed ${isDragOver ? '#0284c7' : '#cbd5e1'}`,
              backgroundColor: isDragOver ? '#f0f9ff' : '#f8fafc',
              borderRadius: '8px', padding: '3rem 2rem', textAlign: 'center',
              cursor: 'pointer', transition: 'all 0.2s', marginBottom: '1.5rem'
            }}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              onChange={handleFileSelect}
            />
            
            {file ? (
              <div>
                <FileText size={48} style={{ margin: '0 auto', color: '#0284c7' }} />
                <h4 style={{ marginTop: '1rem', color: '#0f172a' }}>{file.name}</h4>
                <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '0.25rem' }}>{(file.size / 1024).toFixed(1)} KB</p>
                <button 
                  onClick={(e) => { e.stopPropagation(); setFile(null); }}
                  style={{ marginTop: '1rem', padding: '0.25rem 0.75rem', backgroundColor: 'transparent', border: '1px solid #ef4444', color: '#ef4444', borderRadius: '4px', cursor: 'pointer', fontSize: '0.875rem' }}
                >
                  Clear Selection
                </button>
              </div>
            ) : (
              <div>
                <UploadCloud size={48} style={{ margin: '0 auto', color: '#94a3b8' }} />
                <h4 style={{ marginTop: '1rem', color: '#0f172a', fontWeight: '600' }}>Drag vaccine cards, lab reports, discharge summaries here</h4>
                <p style={{ color: '#0284c7', fontSize: '0.875rem', marginTop: '0.5rem', fontWeight: '500' }}>OR Click to browse</p>
                <p style={{ color: '#94a3b8', fontSize: '0.75rem', marginTop: '1rem' }}>Supported formats: PDF, JPG, PNG (Max 5MB)</p>
              </div>
            )}
          </div>

          <button 
            onClick={handleUpload} 
            disabled={!file || uploading}
            style={{ 
              width: '100%', padding: '0.875rem', backgroundColor: (!file || uploading) ? '#cbd5e1' : '#0d9488', 
              color: 'white', border: 'none', borderRadius: '6px', fontWeight: '600', cursor: (!file || uploading) ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.2s'
            }}
          >
            {uploading ? 'Uploading...' : 'Upload Document'}
          </button>
        </div>

        {/* Uploaded Files List */}
        <div style={{ flex: '1', minWidth: '300px' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: '600', color: '#083344', marginBottom: '1rem' }}>Previously Uploaded</h4>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {uploadedFiles.map(f => (
              <div key={f.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', backgroundColor: 'white', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                  <FileText size={20} style={{ color: '#64748b', marginTop: '0.1rem' }} />
                  <div>
                    <div style={{ fontWeight: '500', color: '#0f172a', fontSize: '0.875rem', wordBreak: 'break-all' }}>{f.name}</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.25rem' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>{f.date}</span>
                      <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>•</span>
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>{f.type}</span>
                    </div>
                    {f.status === 'Merged' ? (
                      <div style={{ fontSize: '0.75rem', color: '#16a34a', fontWeight: '600', marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        <CheckCircle size={12} /> Merged into your records
                      </div>
                    ) : (
                      <div style={{ fontSize: '0.75rem', color: '#ca8a04', fontWeight: '600', marginTop: '0.5rem' }}>
                        Pending verification
                      </div>
                    )}
                  </div>
                </div>
                <button 
                  onClick={() => handleDelete(f.id)}
                  style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', padding: '0.5rem' }}
                  title="Delete File"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
