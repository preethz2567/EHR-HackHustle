import { BrowserRouter, Routes, Route } from 'react-router-dom';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<div>Landing page</div>} />
        <Route path='/patient/login' element={<div>Patient login</div>} />
        <Route path='/patient/otp' element={<div>OTP verification</div>} />
        <Route path='/patient/biometric' element={<div>Biometric auth</div>} />
        <Route path='/patient/dashboard' element={<div>Patient dashboard</div>} />
        <Route path='/doctor/login' element={<div>Doctor login</div>} />
        <Route path='/doctor/patient-access' element={<div>Patient access page</div>} />
        <Route path='/doctor/chief-complaint' element={<div>Chief complaint page</div>} />
        <Route path='/doctor/dashboard' element={<div>Doctor dashboard</div>} />
      </Routes>
    </BrowserRouter>
  );
}
