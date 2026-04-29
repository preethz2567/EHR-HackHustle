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
    if (!endpoint.includes('access-patient-data') && !endpoint.includes('start-session')) {
      localStorage.removeItem('doctorSessionId');
      localStorage.removeItem('doctorSessionToken');
      localStorage.removeItem('currentPatientId');
      window.location.href = '/doctor/login';
      throw new Error('Unauthorized');
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
 * Returns { status, patient_id, patient_data }.
 */
export async function accessPatientData(accessToken) {
  const response = await fetch(`${API_URL}/doctor/access-patient-data`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ access_token: accessToken })
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Access denied');
  }
  return data;
}

/**
 * Start a session by validating the patient's access token.
 * Kept for backward compatibility with the PatientAccess → ChiefComplaint flow.
 */
export async function startDoctorSession(patientId, accessToken) {
  // Use the simplified access endpoint directly
  const data = await accessPatientData(accessToken);
  return { session_id: 'simplified_session', patient_id: data.patient_id, patient_data: data.patient_data };
}

/**
 * Fetch patient data using the stored access token
 */
export async function getPatientData() {
  const accessToken = localStorage.getItem('doctorSessionToken');
  if (!accessToken) throw new Error("No access token found");
  
  const data = await accessPatientData(accessToken);
  return { patient_data: data.patient_data, patient_id: data.patient_id };
}

/**
 * Fetch dashboard-formatted data (including AI analysis)
 */
export async function getDashboardData() {
  const accessToken = localStorage.getItem('doctorSessionToken');
  if (!accessToken) throw new Error("No access token found");
  
  const response = await fetch(`${API_URL}/doctor/dashboard-data`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ access_token: accessToken })
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Access denied');
  }
  return data;
}

/**
 * Export PDF report via backend
 */
export async function exportReportPdf(accessToken, exportType = 'full') {
  const response = await fetch(`${API_URL}/doctor/export-report-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ access_token: accessToken, export_type: exportType }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Export failed');
  }
  return data;
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
  const response = await fetch(`${API_URL}/doctor/export-report-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ access_token: accessToken, export_type: 'full' }),
  });

  if (!response.ok) {
    throw new Error('Failed to export report');
  }

  return response.json();
}
