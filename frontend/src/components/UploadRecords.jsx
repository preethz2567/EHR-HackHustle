import { useState, useRef } from 'react';
import { UploadCloud, File, X, CheckCircle } from 'lucide-react';
import { uploadManualRecord } from '../utils/api';

export default function UploadRecords({ patientId }) {
  const [file, setFile] = useState(null);
  const [docType, setDocType] = useState('vaccine_card');
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
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
      setFile(null);
      // Trigger refresh of data
      window.dispatchEvent(new Event('refreshData'));
    } catch (err) {
      setError(err.message || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card p-6" style={{ padding: '2rem' }}>
      <h3>Upload External Records</h3>
      <p className="text-muted mb-6">Add physical documents, prescriptions, or external lab reports to your EHR.</p>

      {error && <div className="mb-4 text-red-600 font-semibold">{error}</div>}
      {success && <div className="mb-4 text-green-600 font-semibold flex items-center gap-2"><CheckCircle size={16} /> {success}</div>}

      <div className="form-group mb-6" style={{ maxWidth: '400px' }}>
        <label>Document Type</label>
        <select value={docType} onChange={(e) => setDocType(e.target.value)}>
          <option value="vaccine_card">Vaccine Card</option>
          <option value="lab_report">Lab Report</option>
          <option value="prescription">Prescription</option>
        </select>
      </div>

      <div 
        className={`dropzone mb-6 ${file ? 'active' : ''}`}
        onDragOver={(e) => e.preventDefault()}
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
            <File size={48} className="dropzone-icon" style={{ margin: '0 auto' }} />
            <h4 className="mt-4">{file.name}</h4>
            <p className="text-muted text-sm mt-1">{(file.size / 1024).toFixed(1)} KB</p>
            <button 
              className="outline sm mt-4" 
              onClick={(e) => { e.stopPropagation(); setFile(null); }}
              style={{ padding: '0.25rem 0.75rem' }}
            >
              <X size={14} /> Remove
            </button>
          </div>
        ) : (
          <div>
            <UploadCloud size={48} className="dropzone-icon" style={{ margin: '0 auto' }} />
            <h4 className="mt-4">Click or drag file to this area to upload</h4>
            <p className="text-muted text-sm mt-2">Support for a single PDF or image upload.</p>
          </div>
        )}
      </div>

      <button 
        onClick={handleUpload} 
        disabled={!file || uploading}
        style={{ padding: '0.75rem 2rem' }}
      >
        {uploading ? 'Uploading...' : 'Upload Document'}
      </button>
    </div>
  );
}
