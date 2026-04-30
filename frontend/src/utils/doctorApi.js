// src/utils/doctorApi.js
const API_URL = 'http://127.0.0.1:5000/api';

/**
 * Standard fetch wrapper for doctor endpoints
 */
export async function fetchDoctorApi(endpoint, options = {}, tokenType = 'doctorToken') {
  const token = localStorage.getItem(tokenType);
  
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  let response;
  try {
    response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });
  } catch (err) {
    throw new Error('Connection failed. Please check your network and retry.');
  }

  if (response.status === 401) {
    const isAuthEndpoint = endpoint.includes('auth') || endpoint.includes('login');
    const isAccessEndpoint = endpoint.includes('access-patient-data') || endpoint.includes('verify-access-token');
    
    if (!isAuthEndpoint && !isAccessEndpoint) {
      // Only redirect if it's a critical auth failure on a data endpoint
      console.error('Session expired or unauthorized access');
    }
  }
  
  if (response.status === 403) {
    throw new Error('Access denied or token expired');
  }

  if (response.status === 404) {
    throw new Error('Patient not found');
  }

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || 'Something went wrong');
  }

  return data;
}

/**
 * Auth: Doctor login via backend
 */
export async function authenticateDoctor(email, password) {
  return fetchDoctorApi('/doctor/auth', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }, null);
}

/**
 * Simplified token access — doctor provides the patient's 32-char access token.
 * Returns { status, patient_id, doctor_email }.
 */
export async function accessPatientData(accessToken) {
  const data = await fetchDoctorApi('/doctor/verify-access-token', {
    method: 'POST',
    body: JSON.stringify({ access_token: accessToken })
  });

  // Store patient ID for subsequent calls
  localStorage.setItem('currentPatientId', data.patient_id);
  
  // Fetch actual data using the ID
  const patientData = await getPatientData(data.patient_id, accessToken);
  return { status: 'success', patient_id: data.patient_id, patient_data: patientData.patient_data };
}

/**
 * Start a session by validating the patient's access token.
 */
export async function startDoctorSession(patientId, accessToken) {
  const data = await accessPatientData(accessToken);
  return { session_id: 'simplified_session', patient_id: data.patient_id, patient_data: data.patient_data };
}

/**
 * Fetch patient data using the stored access token and dynamic ID
 */
export async function getPatientData(patientId, accessTokenOverride) {
  const accessToken = accessTokenOverride || localStorage.getItem('doctorSessionToken');
  const id = patientId || localStorage.getItem('currentPatientId');
  if (!accessToken) throw new Error("No access token found");
  if (!id) throw new Error("No patient ID found");
  
  const data = await fetchDoctorApi(`/doctor/patient-data/${id}?access_token=${accessToken}`, {
    method: 'GET'
  });

  return { patient_data: data.patient_data, patient_id: id };
}

/**
 * Trigger AI analysis for the patient
 */
export async function analyzePatient(chiefComplaint, context) {
  const accessToken = localStorage.getItem('doctorSessionToken');
  const patientId = localStorage.getItem('currentPatientId');
  
  if (!accessToken) throw new Error("No access token found");
  if (!patientId) throw new Error("No patient ID found");

  return fetchDoctorApi(`/doctor/analyze-patient/${patientId}?access_token=${accessToken}`, {
    method: 'POST',
    body: JSON.stringify({
      chief_complaint: chiefComplaint,
      context: context
    })
  });
}

/**
 * Fetch dashboard-formatted data (including AI analysis)
 */
export async function getDashboardData(patientId) {
  const accessToken = localStorage.getItem('doctorSessionToken');
  const id = patientId || localStorage.getItem('currentPatientId');
  if (!accessToken) throw new Error("No access token found");
  if (!id) throw new Error("No patient ID found");
  
  return fetchDoctorApi(`/doctor/dashboard-data/${id}?access_token=${accessToken}`, {
    method: 'GET'
  });
}

/**
 * Export PDF report via backend
 */
export async function exportReportPdf(accessToken, exportType = 'full', patientId) {
  const id = patientId || localStorage.getItem('currentPatientId');
  if (!id) throw new Error("No patient ID found");

  return fetchDoctorApi(`/doctor/export-report-pdf/${id}`, {
    method: 'POST',
    body: JSON.stringify({ access_token: accessToken, export_type: exportType }),
  });
}

/**
 * Download a generated PDF
 */
export function getDownloadUrl(filename) {
  return `${API_URL.replace('/api', '')}/api/download/${filename}`;
}

/**
 * Legacy export (blob download)
 */
export async function exportReport() {
  const accessToken = localStorage.getItem('doctorSessionToken');
  const patientId = localStorage.getItem('currentPatientId');
  return exportReportPdf(accessToken, 'full', patientId);
}
