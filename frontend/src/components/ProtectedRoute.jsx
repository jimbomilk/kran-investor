import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { token, loading } = useAuth();

  if (loading) {
    // Optional: show a loading spinner
    return <div>Loading...</div>;
  }

  if (!token) {
    // Redirige al usuario a la página de login si no está autenticado.
    // `replace` evita que la ruta protegida se guarde en el historial de navegación.
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;