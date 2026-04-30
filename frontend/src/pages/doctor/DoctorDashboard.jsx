import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Timer, Download, LogOut, ShieldAlert, Loader, Activity, Pill, 
  AlertTriangle, History, X, Check, FileEdit, Clock, Stethoscope
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceArea } from 'recharts';
import { getPatientData, getDashboardData, exportReportPdf, getDownloadUrl } from '../../utils/doctorApi';
import './DoctorPortal.css';

export default function DoctorDashboard() {
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('summary');
  const [timeLeft, setTimeLeft] = useState(30 * 60); // 30 min session
  const [showExportModal, setShowExportModal] = useState(false);
  const [sessionWarning, setSessionWarning] = useState(false);
  const [patientData, setPatientData] = useState(null);
  const [isExporting, setIsExporting] = useState(false);
  const [exportOptions, setExportOptions] = useState({
    summary: true, risk: true, meds: true, trends: true, recs: true, log: false
  });

  const patientId = localStorage.getItem('currentPatientId');
  const sessionId = localStorage.getItem('doctorSessionId');
  const patientName = localStorage.getItem('currentPatientName') || 'Patient';
  const patientAge = localStorage.getItem('currentPatientAge') || 'N/A';
  const chiefComplaint = localStorage.getItem('chiefComplaint') || 'Chest pain with shortness of breath';
  const complaintContext = localStorage.getItem('complaintContext') || 'Past 3 hours';

  // Mock patient details based on dynamic data
  const patient = {
    name: patientName,
    age: patientAge,
    gender: "Unknown",
    id: patientId,
    lastVisit: "Recent",
    bloodGroup: "N/A"
  };

  useEffect(() => {
    if (!patientId || !sessionId) {
      navigate('/doctor/access');
      return;
    }

    // Fetch actual dashboard data from backend
    const loadData = async () => {
      try {
        const res = await getDashboardData();
        setPatientData(res);
      } catch (err) {
        setError(err.message || 'Failed to load patient data');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [patientId, sessionId, navigate]);

  useEffect(() => {
    if (timeLeft <= 0) {
      handleLogout('Session expired. Logging out automatically.');
      return;
    }

    if (timeLeft === 5 * 60 && !sessionWarning) {
      setSessionWarning(true);
    }

    const timer = setInterval(() => setTimeLeft((prev) => prev - 1), 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  const handleLogout = (message = 'Session ended successfully') => {
    localStorage.removeItem('doctorSessionToken');
    localStorage.removeItem('doctorSessionId');
    localStorage.removeItem('currentPatientId');
    localStorage.removeItem('chiefComplaint');
    localStorage.removeItem('complaintContext');
    // We keep doctorToken
    navigate('/doctor/access');
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const extendSession = () => {
    setTimeLeft(prev => prev + 15 * 60);
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const accessToken = localStorage.getItem('doctorSessionToken');
      // Determine export type from selected options
      let exportType = 'full';
      const selected = Object.entries(exportOptions).filter(([k, v]) => v).map(([k]) => k);
      if (selected.length === 1) {
        const mapping = { summary: 'summary', risk: 'risk', meds: 'medications', trends: 'trends', recs: 'recommendations' };
        exportType = mapping[selected[0]] || 'full';
      }
      
      const res = await exportReportPdf(accessToken, exportType);
      
      if (res.download_url) {
        const a = document.createElement('a');
        a.href = `http://127.0.0.1:5000${res.download_url}`;
        a.download = res.filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
      }
    } catch (err) {
      setError(err.message || 'Export failed. Please try again.');
    } finally {
      setIsExporting(false);
      setShowExportModal(false);
    }
  };

  // Content rendering based on active tab
  const renderTabContent = () => {
    switch(activeTab) {
      case 'summary':
        const summary_data = patientData?.patient_summary || {};
        const diags = summary_data.diagnoses || [];
        const meds = summary_data.medications || [];
        const labs = summary_data.recent_labs || [];
        return (
          <div className="three-col-grid">
            <div className="section-card">
              <div className="section-title"><Activity size={18} className="text-teal" /> Active Diagnoses</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {diags.length > 0 ? diags.map((d, i) => (
                  <div key={i} style={{ border: '1px solid #e2e8f0', borderRadius: '6px', padding: '0.75rem', background: '#fafbfc' }}>
                    <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600, marginBottom: '0.25rem' }}>{d.code || 'CODE-N/A'}</div>
                    <div style={{ fontWeight: 600, color: '#0f172a', textTransform: 'capitalize', marginBottom: '0.25rem' }}>{d.name}</div>
                    <div style={{ fontSize: '0.85rem', color: '#334155' }}>Diagnosed: {d.date_of_diagnosis}</div>
                    <div style={{ fontSize: '0.85rem', color: '#10b981', fontWeight: 600, marginTop: '0.25rem' }}>Status: {d.status} ✓</div>
                  </div>
                )) : <p>No diagnoses found</p>}
              </div>
            </div>
            
            <div className="section-card">
              <div className="section-title"><Pill size={18} className="text-teal" /> Current Medications</div>
              <div style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '1rem' }}>{summary_data.medications_count} active medications</div>
              <table className="data-table" style={{ fontSize: '0.8rem' }}>
                <thead><tr><th>Name</th><th>Dosage</th><th>Indication</th><th>Status</th><th>Adherence</th></tr></thead>
                <tbody>
                  {meds.length > 0 ? meds.map((m, i) => (
                    <tr key={i}>
                      <td style={{ textTransform: 'capitalize', fontWeight: 600 }}>{m.name}</td>
                      <td>{m.dosage || 'N/A'}</td>
                      <td>{m.indication || 'N/A'}</td>
                      <td><span className={m.is_active !== false ? "badge badge-green" : "badge badge-gray"}>{m.is_active !== false ? 'Active' : 'Inactive'}</span></td>
                      <td style={{ color: '#10b981', fontWeight: 600 }}>{m.adherence_percent ? m.adherence_percent + '%' : 'N/A'}</td>
                    </tr>
                  )) : <tr><td colSpan="5">No medications found</td></tr>}
                </tbody>
              </table>
            </div>

            <div className="section-card">
              <div className="section-title"><Activity size={18} className="text-teal" /> Recent Vitals & Labs</div>
              <div style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '1rem' }}>Latest test results</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {labs.slice(0, 5).map((l, i) => (
                  <div key={i} style={{ borderLeft: `4px solid ${l.status !== 'Normal' ? '#ef4444' : '#10b981'}`, borderRadius: '6px', padding: '0.75rem', background: '#fafbfc', borderTop: '1px solid #e2e8f0', borderRight: '1px solid #e2e8f0', borderBottom: '1px solid #e2e8f0' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                      <span style={{ fontWeight: 600 }}>{l.test_name}: {l.value} {l.unit}</span>
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>{l.date}</span>
                    </div>
                    <div style={{ fontSize: '0.85rem', color: '#334155' }}>Ref: {l.reference_range}</div>
                    <div style={{ fontSize: '0.85rem', color: l.status !== 'Normal' ? '#ef4444' : '#10b981', fontWeight: 600, marginTop: '0.25rem' }}>Status: {l.status}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case 'risk':
        const risks = patientData?.risk_assessment?.immediate_risks || [];
        const interactions = patientData?.risk_assessment?.drug_interactions || [];
        const contra = patientData?.risk_assessment?.contraindications || [];
        return (
          <div className="fade-in">
            {risks.some(r => r.severity === 'CRITICAL') && (
              <div className="alert-box alert-high" style={{ padding: '1.25rem', fontSize: '1.1rem', fontWeight: 700, justifyContent: 'center' }}>
                <AlertTriangle size={24} /> HIGH RISK PROFILE
              </div>
            )}

            <h3 style={{ margin: '1.5rem 0 1rem', color: '#0c1e3c', fontSize: '1.15rem' }}>Section A: Immediate Risks</h3>
            <div className="three-col-grid" style={{ marginBottom: '2rem' }}>
              {risks.length > 0 ? risks.map((r, i) => (
                <div key={i} className="section-card" style={{ borderTop: `4px solid ${r.severity === 'CRITICAL' ? '#ef4444' : r.severity === 'HIGH' ? '#f97316' : '#eab308'}` }}>
                  <div style={{ display: 'inline-block', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, marginBottom: '0.75rem', background: r.severity === 'CRITICAL' ? '#fee2e2' : r.severity === 'HIGH' ? '#ffedd5' : '#fef3c7', color: r.severity === 'CRITICAL' ? '#991b1b' : r.severity === 'HIGH' ? '#9a3412' : '#854d0e' }}>
                    {r.severity}
                  </div>
                  <div style={{ fontWeight: 600, color: '#0f172a', marginBottom: '0.5rem' }}>{r.risk}</div>
                  <p style={{ fontSize: '0.85rem', color: '#334155', margin: 0 }}><span style={{ fontWeight: 600 }}>Mitigation:</span> {r.mitigation}</p>
                </div>
              )) : <p>No immediate risks identified.</p>}
            </div>

            <div className="three-col-grid">
              <div>
                <h3 style={{ margin: '0 0 1rem', color: '#0c1e3c', fontSize: '1.15rem' }}>Section B: Drug Interactions</h3>
                {interactions.length > 0 ? interactions.map((inter, i) => (
                  <div key={i} className="section-card" style={{ borderTop: '4px solid #f97316', marginBottom: '1rem', background: '#fffaf5' }}>
                    <div style={{ fontWeight: 600, color: '#9a3412', marginBottom: '0.25rem' }}>{inter.interaction}</div>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#ea580c', marginBottom: '0.5rem' }}>Severity: {inter.severity}</div>
                    <p style={{ fontSize: '0.85rem', color: '#334155', margin: 0 }}><span style={{ fontWeight: 600 }}>Mitigation:</span> {inter.mitigation}</p>
                  </div>
                )) : <div className="section-card"><p>No known interactions detected.</p></div>}
              </div>
              
              <div>
                <h3 style={{ margin: '0 0 1rem', color: '#0c1e3c', fontSize: '1.15rem' }}>Section C: Contraindications</h3>
                {contra.length > 0 ? contra.map((c, i) => (
                  <div key={i} className="section-card" style={{ borderTop: '4px solid #eab308', marginBottom: '1rem', background: '#fefce8' }}>
                    <div style={{ fontWeight: 600, color: '#854d0e', marginBottom: '0.25rem' }}>{c.contraindication}</div>
                    <p style={{ fontSize: '0.85rem', color: '#334155', margin: 0 }}><span style={{ fontWeight: 600 }}>Why:</span> {c.why}</p>
                  </div>
                )) : <div className="section-card"><p>No contraindications detected.</p></div>}
              </div>
            </div>
          </div>
        );

      case 'meds':
        const med_analysis = patientData?.medication_analysis || {};
        const regimen = med_analysis.current_regimen || [];
        const gaps = med_analysis.therapy_gaps || [];
        return (
          <div className="fade-in">
            <h3 style={{ margin: '0 0 1.25rem', color: '#0c1e3c' }}>Medication Reconciliation</h3>
            <div className="section-card" style={{ padding: 0, overflow: 'hidden', marginBottom: '2rem' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Med Name</th>
                    <th>Dosage</th>
                    <th>Indication</th>
                    <th>Status</th>
                    <th>Adherence</th>
                  </tr>
                </thead>
                <tbody>
                  {regimen.length > 0 ? regimen.map((m, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600, textTransform: 'capitalize' }}>{m.name}</td>
                      <td>{m.dosage || 'N/A'}</td>
                      <td>{m.indication || 'N/A'}</td>
                      <td><span className={m.is_active !== false ? "badge badge-green" : "badge badge-gray"}>{m.is_active !== false ? 'Active' : 'Inactive'}</span></td>
                      <td style={{ color: '#10b981', fontWeight: 600 }}>{m.adherence_percent ? m.adherence_percent + '%' : 'N/A'}</td>
                    </tr>
                  )) : <tr><td colSpan="5">No current medications found.</td></tr>}
                </tbody>
              </table>
            </div>

            <h3 style={{ margin: '0 0 1rem', color: '#0c1e3c' }}>Therapy Gaps & Recommendations</h3>
            <div className="three-col-grid">
              {gaps.length > 0 ? gaps.map((gap, i) => (
                <div key={i} className="section-card" style={{ borderLeft: `4px solid ${gap.priority === 'RECOMMENDED' ? '#3b82f6' : '#94a3b8'}` }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: gap.priority === 'RECOMMENDED' ? '#2563eb' : '#64748b', marginBottom: '0.5rem' }}>
                    {gap.priority || 'OPTIONAL'}
                  </div>
                  <div style={{ fontWeight: 600, color: '#0f172a', marginBottom: '0.5rem' }}>Gap: {gap.gap_description || gap.gap || 'N/A'}</div>
                  <p style={{ fontSize: '0.85rem', color: '#334155', marginBottom: '0.5rem' }}><span style={{ fontWeight: 600 }}>Recommendation:</span> {gap.recommendation || 'N/A'}</p>
                  <p style={{ fontSize: '0.8rem', color: '#64748b', margin: 0 }}><span style={{ fontWeight: 600 }}>Evidence:</span> {gap.evidence || 'Clinical Guidelines'}</p>
                </div>
              )) : <div className="section-card"><p>No therapy gaps identified.</p></div>}
            </div>
          </div>
        );

      case 'trends':
        const trends = patientData?.health_trends || {};
        
        // Map data for Recharts
        const hba1cData = (trends.hba1c || []).map(d => ({ date: d.date?.split('-').slice(1).join('/') || '', val: d.value }));
        const egfrData = (trends.egfr || []).map(d => ({ date: d.date?.split('-').slice(1).join('/') || '', val: d.value }));
        
        // Merge BP systolic and diastolic by date
        const bpMap = {};
        (trends.bp_systolic || []).forEach(d => { bpMap[d.date] = { ...bpMap[d.date], date: d.date?.split('-').slice(1).join('/') || '', sys: d.value } });
        (trends.bp_diastolic || []).forEach(d => { bpMap[d.date] = { ...bpMap[d.date], date: d.date?.split('-').slice(1).join('/') || '', dia: d.value } });
        const bpData = Object.values(bpMap).sort((a, b) => a.date.localeCompare(b.date));

        return (
          <div className="fade-in">
            <h3 style={{ margin: '0 0 1.25rem', color: '#0c1e3c' }}>Historical Health Metrics</h3>
            <div className="three-col-grid">
              
              {/* HbA1c */}
              <div className="section-card">
                <div style={{ fontWeight: 600, color: '#0f172a', marginBottom: '0.25rem' }}>HbA1c Trend</div>
                <div style={{ fontSize: '0.8rem', color: trends.hba1c_trend?.includes('worsening') ? '#ef4444' : '#10b981', fontWeight: 600, marginBottom: '1rem' }}>
                  {trends.hba1c_trend?.toUpperCase() || 'STABLE'}
                </div>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={hba1cData} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                      <YAxis domain={['auto', 'auto']} tick={{ fontSize: 12 }} />
                      <Tooltip />
                      <ReferenceArea y1={6.5} y2={10} fill="#fee2e2" fillOpacity={0.5} />
                      <ReferenceArea y1={5.7} y2={6.5} fill="#ffedd5" fillOpacity={0.5} />
                      <ReferenceArea y1={0} y2={5.7} fill="#dcfce7" fillOpacity={0.5} />
                      <Line type="monotone" dataKey="val" stroke="#2563eb" strokeWidth={3} dot={{ r: 4 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Blood Pressure */}
              <div className="section-card">
                <div style={{ fontWeight: 600, color: '#0f172a', marginBottom: '0.25rem' }}>Blood Pressure Trend</div>
                <div style={{ fontSize: '0.8rem', color: trends.bp_trend?.includes('worsening') || trends.bp_trend?.includes('uncontrolled') ? '#ef4444' : '#10b981', fontWeight: 600, marginBottom: '1rem' }}>
                  {trends.bp_trend?.toUpperCase() || 'STABLE'}
                </div>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={bpData} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                      <YAxis domain={['auto', 'auto']} tick={{ fontSize: 12 }} />
                      <Tooltip />
                      <Line type="monotone" dataKey="sys" stroke="#ef4444" strokeWidth={3} dot={{ r: 4 }} name="Systolic" />
                      <Line type="monotone" dataKey="dia" stroke="#f97316" strokeWidth={3} dot={{ r: 4 }} name="Diastolic" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* eGFR */}
              <div className="section-card">
                <div style={{ fontWeight: 600, color: '#0f172a', marginBottom: '0.25rem' }}>eGFR Trend</div>
                <div style={{ fontSize: '0.8rem', color: trends.egfr_trend?.includes('worsening') || trends.egfr_trend?.includes('declining') ? '#ef4444' : '#10b981', fontWeight: 600, marginBottom: '1rem' }}>
                  {trends.egfr_trend?.toUpperCase() || 'STABLE'}
                </div>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={egfrData} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                      <YAxis domain={['auto', 'auto']} tick={{ fontSize: 12 }} />
                      <Tooltip />
                      <ReferenceArea y1={0} y2={30} fill="#fee2e2" fillOpacity={0.5} />
                      <ReferenceArea y1={30} y2={45} fill="#ffedd5" fillOpacity={0.5} />
                      <ReferenceArea y1={45} y2={60} fill="#fef08a" fillOpacity={0.3} />
                      <ReferenceArea y1={60} y2={120} fill="#dcfce7" fillOpacity={0.5} />
                      <Line type="monotone" dataKey="val" stroke="#f97316" strokeWidth={3} dot={{ r: 4 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

            </div>
          </div>
        );

      case 'timeline':
        const timelineEvents = patientData?.disease_timeline || [];
        return (
          <div className="fade-in">
            <h3 style={{ margin: '0 0 1.25rem', color: '#0c1e3c' }}>Disease Progression Timeline</h3>
            <div className="section-card" style={{ padding: '2rem' }}>
              <div style={{ borderLeft: '3px solid #e2e8f0', marginLeft: '1rem', paddingLeft: '2rem', position: 'relative' }}>
                {timelineEvents.length > 0 ? timelineEvents.map((evt, i) => (
                  <div key={i} style={{ marginBottom: i === timelineEvents.length - 1 ? 0 : '2rem', position: 'relative' }}>
                    <div style={{
                      position: 'absolute',
                      left: '-2.4rem',
                      width: '1.25rem',
                      height: '1.25rem',
                      borderRadius: '50%',
                      background: evt.severity_code === 'severe' ? '#ef4444' : evt.severity_code === 'moderate' ? '#f59e0b' : '#3b82f6',
                      border: '3px solid #fff',
                      boxShadow: '0 0 0 1px #e2e8f0'
                    }} />
                    <div style={{ color: '#64748b', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.25rem' }}>{evt.date}</div>
                    <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #f1f5f9' }}>
                      <h4 style={{ margin: '0 0 0.5rem', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {evt.event}
                        <span style={{ 
                          fontSize: '0.7rem', 
                          padding: '0.1rem 0.4rem', 
                          borderRadius: '4px',
                          background: evt.severity_code === 'severe' ? '#fee2e2' : evt.severity_code === 'moderate' ? '#fef3c7' : '#dbeafe',
                          color: evt.severity_code === 'severe' ? '#991b1b' : evt.severity_code === 'moderate' ? '#92400e' : '#1e40af'
                        }}>
                          {evt.severity}
                        </span>
                      </h4>
                      <p style={{ margin: '0 0 0.5rem', color: '#334155', fontSize: '0.9rem' }}>{evt.description}</p>
                      {evt.details && <p style={{ margin: 0, color: '#64748b', fontSize: '0.8rem' }}>{evt.details}</p>}
                    </div>
                  </div>
                )) : <p>No progression data available.</p>}
              </div>
            </div>
          </div>
        );

      case 'recs':
        const recs = patientData?.clinical_recommendations || {};
        const summary = recs.clinical_summary || "No summary available.";
        const priorities = recs.immediate_priorities || [];
        const riskSignals = recs.key_risk_signals || [];
        
        return (
          <div className="fade-in">
            <h3 style={{ margin: '0 0 1.25rem', color: '#0c1e3c' }}>AI-Synthesized Clinical Summary</h3>
            
            <div className="ai-summary-box">
              <p>{summary}</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
              <div className="section-card">
                <h4 style={{ color: '#0c1e3c', marginBottom: '1rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.5rem' }}>Immediate Priorities</h4>
                <ul className="numbered-list">
                  {priorities.length > 0 ? priorities.map((p, i) => (
                    <li key={i} className="numbered-item" style={{ borderBottom: i === priorities.length - 1 ? 'none' : '1px solid #f1f5f9', paddingBottom: i === priorities.length - 1 ? 0 : '1rem' }}>
                      <div className="number-circle" style={{ background: i === 0 ? '#ef4444' : i === 1 ? '#f97316' : '#eab308' }}>{i + 1}</div>
                      <div className="numbered-content">
                        <h4 style={{ color: '#0f172a' }}>{p.action}</h4>
                        <p><span style={{ fontWeight: 600, color: '#334155' }}>Rationale:</span> {p.rationale}</p>
                        <p><span style={{ fontWeight: 600, color: '#334155' }}>Timeline:</span> {p.timeline}</p>
                      </div>
                    </li>
                  )) : <p>No immediate priorities identified.</p>}
                </ul>
              </div>

              <div className="section-card" style={{ background: '#fafbfc' }}>
                <h4 style={{ color: '#0c1e3c', marginBottom: '1rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.5rem' }}>Key Risk Signals</h4>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                  {riskSignals.length > 0 ? riskSignals.map((signal, i) => (
                    <li key={i} style={{ display: 'flex', gap: '0.5rem', fontSize: '0.9rem', color: '#334155', lineHeight: 1.5 }}>
                      <span style={{ fontSize: '1.1rem' }}>⚠️</span> 
                      <span>{signal}</span>
                    </li>
                  )) : <li>No key risk signals.</li>}
                </ul>
              </div>
            </div>
          </div>
        );

      case 'log':
        return (
          <div className="fade-in section-card" style={{ padding: 0, overflow: 'hidden' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Action</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>29-Apr-2024 14:32</td>
                  <td>Patient data accessed</td>
                  <td>Token verified</td>
                </tr>
                <tr>
                  <td>29-Apr-2024 14:32</td>
                  <td>AI analysis triggered</td>
                  <td>Risk, Meds, Trends, Lab agents ran</td>
                </tr>
              </tbody>
            </table>
          </div>
        );

      default: return null;
    }
  };

  const doctorName = localStorage.getItem('doctorName') || 'Dr. Amit Kumar';
  const doctorHospital = localStorage.getItem('doctorHospital') || 'Cardiologist';

  if (loading) {
    return (
      <div className="doctor-auth-container" style={{ background: '#f1f5f9', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <Loader size={40} className="spinner text-teal" style={{ margin: '0 auto 1rem' }} />
          <p style={{ color: '#0c1e3c', fontWeight: 600 }}>Loading patient records...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="doctor-auth-container" style={{ background: '#f1f5f9', alignItems: 'center', justifyContent: 'center' }}>
        <div className="section-card" style={{ textAlign: 'center', maxWidth: '400px' }}>
          <AlertTriangle size={48} style={{ color: '#ef4444', margin: '0 auto 1rem' }} />
          <h2 style={{ color: '#0c1e3c', fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>Access Error</h2>
          <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>{error}</p>
          <button className="btn-primary" onClick={() => navigate('/doctor/access')}>Back to Access Page</button>
        </div>
      </div>
    );
  }

  return (
    <div className="doctor-portal">
      <header className="doctor-topbar">
        <div className="doctor-brand">
          <Stethoscope size={24} style={{ color: '#0d9488' }} />
          <span>HealthBridge India</span>
          <span style={{ fontSize: '0.9rem', fontWeight: 400, marginLeft: '1rem', borderLeft: '1px solid rgba(255,255,255,0.2)', paddingLeft: '1rem' }}>
            {doctorName} <span style={{ color: '#94a3b8', fontSize: '0.8rem' }}>({doctorHospital})</span>
          </span>
        </div>
        <div className="doctor-actions">
          <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>Patient: {patient.name}</span>
          <div className={`session-timer ${timeLeft < 300 ? 'warning' : ''}`}>
            <Timer size={16} />
            <span>{formatTime(timeLeft)}</span>
          </div>
          <button className="btn-logout" onClick={() => handleLogout()}>
            <LogOut size={16} /> Logout
          </button>
        </div>
      </header>

      <main className="main-container fade-in">

        {/* 5-minute session warning */}
        {sessionWarning && timeLeft > 0 && timeLeft <= 300 && (
          <div style={{ background: '#fef3c7', border: '1px solid #f59e0b', borderRadius: 8, padding: '0.75rem 1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#92400e', fontWeight: 600, fontSize: '0.9rem' }}>
              <AlertTriangle size={18} /> Session ending in {formatTime(timeLeft)} — save your work!
            </div>
            <button onClick={() => { extendSession(); setSessionWarning(false); }} style={{ background: '#f59e0b', color: '#fff', border: 'none', borderRadius: 6, padding: '0.35rem 0.75rem', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer' }}>Extend 15 min</button>
          </div>
        )}
        
        {/* Header Section */}
        <div className="patient-header-card">
          <div className="patient-info-grid">
            <div className="info-item">
              <div className="label">Patient Name</div>
              <div className="value">{patient.name}</div>
            </div>
            <div className="info-item">
              <div className="label">Age / Gender</div>
              <div className="value">{patient.age} Y, {patient.gender}</div>
            </div>
            <div className="info-item">
              <div className="label">Patient ID</div>
              <div className="value">{patient.id}</div>
            </div>
            <div className="info-item">
              <div className="label">Last Visit</div>
              <div className="value">{patient.lastVisit}</div>
            </div>
            <div className="info-item">
              <div className="label">Blood Group</div>
              <div className="value" style={{ color: '#ef4444' }}>{patient.bloodGroup}</div>
            </div>
          </div>
          
          <div className="chief-complaint-box">
            <div>
              <div className="cc-title">Chief Complaint</div>
              <div className="cc-text">{chiefComplaint}</div>
              <div className="cc-duration">Duration/Context: {complaintContext}</div>
            </div>
            <button className="btn-secondary" style={{ width: 'auto', padding: '0.4rem 0.8rem', fontSize: '0.8rem' }} onClick={() => navigate('/doctor/chief-complaint')}>
              <FileEdit size={14} /> Edit
            </button>
          </div>
        </div>

        {/* Tabs Area */}
        <div className="portal-tabs">
          <button className={`portal-tab ${activeTab === 'summary' ? 'active' : ''}`} onClick={() => setActiveTab('summary')}>Patient Summary</button>
          <button className={`portal-tab ${activeTab === 'risk' ? 'active' : ''}`} onClick={() => setActiveTab('risk')}>Risk Assessment</button>
          <button className={`portal-tab ${activeTab === 'meds' ? 'active' : ''}`} onClick={() => setActiveTab('meds')}>Medication Analysis</button>
          <button className={`portal-tab ${activeTab === 'trends' ? 'active' : ''}`} onClick={() => setActiveTab('trends')}>Health Trends</button>
          <button className={`portal-tab ${activeTab === 'timeline' ? 'active' : ''}`} onClick={() => setActiveTab('timeline')}>Disease Timeline</button>
          <button className={`portal-tab ${activeTab === 'recs' ? 'active' : ''}`} onClick={() => setActiveTab('recs')}>Clinical Recommendations</button>
          <button className={`portal-tab ${activeTab === 'log' ? 'active' : ''}`} onClick={() => setActiveTab('log')}>Audit Log</button>
        </div>

        <div style={{ minHeight: '400px', marginBottom: '2rem' }}>
          {renderTabContent()}
        </div>

        {/* Bottom Actions */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#fff', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 1px 2px rgba(0,0,0,0.03)' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#ef4444', fontWeight: 600, fontSize: '0.9rem' }}>
              <Clock size={16} /> Session expires in: {formatTime(timeLeft)}
            </div>
            <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.2rem' }}>Session will auto-logout when timer reaches 0. Save your work.</div>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button className="btn-secondary" style={{ width: 'auto' }} onClick={extendSession}>Extend Session (+15m)</button>
            <button className="btn-primary" style={{ width: 'auto' }} onClick={() => setShowExportModal(true)}><Download size={16} /> Export Report</button>
          </div>
        </div>
      </main>

      {/* Export Modal */}
      {showExportModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="section-card" style={{ width: '100%', maxWidth: '400px', padding: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0c1e3c', margin: 0 }}>Export Patient Report</h3>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }} onClick={() => setShowExportModal(false)}><X size={20} /></button>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', marginBottom: '2rem' }}>
              {Object.entries({
                summary: 'Include patient summary',
                risk: 'Include risk assessment',
                meds: 'Include medication analysis',
                trends: 'Include health trends',
                recs: 'Include recommendations',
                log: 'Include audit log'
              }).map(([key, label]) => (
                <label key={key} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.9rem', color: '#334155', cursor: 'pointer' }}>
                  <input 
                    type="checkbox" 
                    checked={exportOptions[key]} 
                    onChange={(e) => setExportOptions({...exportOptions, [key]: e.target.checked})}
                    style={{ width: '16px', height: '16px', accentColor: '#2563eb' }}
                  />
                  {label}
                </label>
              ))}
            </div>

            <button className="btn-primary" onClick={handleExport} disabled={isExporting}>
              {isExporting ? <><Loader size={16} className="spinner" /> Generating... Please wait...</> : 'Generate & Download PDF'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
