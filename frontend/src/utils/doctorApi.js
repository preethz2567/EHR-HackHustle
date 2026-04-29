// src/utils/doctorApi.js
const API_URL = 'http://localhost:5000/api';

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

  // Attach session ID if available
  const sessionId = localStorage.getItem('doctorSessionId');
  if (sessionId) {
    headers['Session-Id'] = sessionId;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Only clear session data, don't redirect if we're starting a session
    if (!endpoint.includes('start-session')) {
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

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || 'Something went wrong');
  }

  return data;
}

/**
 * Auth functions
 */
export async function authenticateDoctor(email, password) {
  return fetchDoctorApi('/doctor/auth', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }, null); // No token required for login
}

/**
 * Start a 30-minute session with the patient's access token.
 * Returns { session_id, expires_at_timestamp, expires_in_minutes }
 */
export async function startDoctorSession(patientId, accessToken) {
  const res = await fetchDoctorApi('/doctor/start-session', {
    method: 'POST',
    body: JSON.stringify({ patient_id: patientId, access_token: accessToken }),
  }, 'doctorToken');

  return res;
}

/**
 * Fetch patient data using the active session (Session-Id header auto-attached)
 */
export async function getPatientData() {
  return fetchDoctorApi('/doctor/patient-data', {
    method: 'GET',
  }, 'doctorToken');
}

/**
 * Fetch dashboard-formatted data using the active session
 */
export async function getDashboardData() {
  return fetchDoctorApi('/doctor/dashboard-data', {
    method: 'GET',
  }, 'doctorToken');
}

/**
 * Export PDF report using the active session
 */
export async function exportReport() {
  const token = localStorage.getItem('doctorToken');
  const sessionId = localStorage.getItem('doctorSessionId');

  const response = await fetch(`${API_URL}/doctor/export-report`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Session-Id': sessionId,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to export report');
  }

  return response.blob();
}
