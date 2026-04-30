// src/utils/api.js
const API_URL = 'http://127.0.0.1:5000/api';

/**
 * Standard fetch wrapper that automatically includes the Authorization header
 * and handles 401 Unauthorized responses by clearing the token and redirecting.
 */
export async function fetchApi(endpoint, options = {}) {
  const token = localStorage.getItem('patientToken');
  
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Remove Content-Type if we are sending FormData (browser sets it automatically with boundary)
  if (options.body instanceof FormData) {
    delete headers['Content-Type'];
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
    localStorage.removeItem('patientToken');
    window.location.href = '/login';
    throw new Error('Unauthorized');
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
 * Auth functions
 */
export async function authenticatePatient(patientId, biometricType, biometricData, otp, email, password) {
  return fetchApi('/patient/login', {
    method: 'POST',
    body: JSON.stringify({
      patient_id: patientId,
      biometric_type: biometricType,
      biometric_data: biometricData,
      otp: otp,
      email: email,
      password: password
    }),
  });
}

/**
 * Patient Portal functions
 */
export async function fetchHistoricalData(patientId) {
  return fetchApi(`/patient/${patientId}/fetch-historical`, {
    method: 'POST',
  });
}

export async function getCachedData(patientId) {
  return fetchApi(`/patient/${patientId}/my-records`, {
    method: 'GET',
  });
}

export async function uploadManualRecord(patientId, file) {
  const formData = new FormData();
  formData.append('file', file);

  return fetchApi(`/patient/${patientId}/upload-manual`, {
    method: 'POST',
    body: formData,
  });
}

export async function generateAccessToken(patientId, doctorEmail) {
  return fetchApi(`/patient/${patientId}/generate-access-token`, {
    method: 'POST',
    body: JSON.stringify({
      doctor_email: doctorEmail,
    }),
  });
}

export async function getActiveTokens(patientId) {
  return fetchApi(`/patient/${patientId}/active-tokens`, {
    method: 'GET',
  });
}

export async function revokeToken(patientId, accessToken) {
  return fetchApi(`/patient/${patientId}/revoke-token/${accessToken}`, {
    method: 'DELETE',
  });
}

export async function getAuditLog(patientId) {
  return fetchApi(`/patient/${patientId}/audit-log`, {
    method: 'GET',
  });
}

export async function exportMedicalRecordsPdf(patientId) {
  return fetchApi(`/patient/${patientId}/export-medical-records-pdf`, {
    method: 'POST',
  });
}
