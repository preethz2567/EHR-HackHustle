import { Navigate, useLocation } from 'react-router-dom';

export default function AuthGuard({ children }) {
  const token = localStorage.getItem('patientToken');
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}
