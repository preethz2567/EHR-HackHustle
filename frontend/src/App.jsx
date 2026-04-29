import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthGuard from './components/AuthGuard';
import DoctorAuthGuard from './components/DoctorAuthGuard';
import Login from './pages/Login';
import BiometricAuth from './pages/BiometricAuth';
import Dashboard from './pages/Dashboard';
import LandingPage from './pages/LandingPage';

import DoctorLogin from './pages/doctor/DoctorLogin';
import PatientAccess from './pages/doctor/PatientAccess';
import ChiefComplaint from './pages/doctor/ChiefComplaint';
import DoctorDashboard from './pages/doctor/DoctorDashboard';

import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/biometric-auth" element={<BiometricAuth />} />
        
        <Route 
          path="/dashboard/*" 
          element={
            <AuthGuard>
              <Dashboard />
            </AuthGuard>
          } 
        />

        {/* Doctor Routes */}
        <Route path="/doctor/login" element={<DoctorLogin />} />
        
        <Route 
          path="/doctor/access" 
          element={
            <DoctorAuthGuard>
              <PatientAccess />
            </DoctorAuthGuard>
          } 
        />
        
        <Route 
          path="/doctor/chief-complaint" 
          element={
            <DoctorAuthGuard>
              <ChiefComplaint />
            </DoctorAuthGuard>
          } 
        />
        
        <Route 
          path="/doctor/dashboard" 
          element={
            <DoctorAuthGuard>
              <DoctorDashboard />
            </DoctorAuthGuard>
          } 
        />
        
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
