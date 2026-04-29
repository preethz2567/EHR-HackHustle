import { Navigate, useLocation } from 'react-router-dom';

export default function DoctorAuthGuard({ children }) {
  const token = localStorage.getItem('doctorToken');
  const location = useLocation();

  if (!token) {
    return <Navigate to="/doctor/login" state={{ from: location }} replace />;
  }

  return children;
}
