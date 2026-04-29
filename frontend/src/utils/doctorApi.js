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

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    localStorage.removeItem(tokenType);
    window.location.href = '/doctor/login';
    throw new Error('Unauthorized');
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
 * Doctor Dashboard functions
 * Uses the sessionToken stored during PatientAccess phase
 */
export async function getPatientData(patientId, sessionToken) {
  return fetchDoctorApi(`/doctor/patient-data`, {
    method: 'GET',
    headers: {
      'Patient-Id': patientId,
      'Access-Token': sessionToken
    }
  }, 'doctorToken'); 
}
