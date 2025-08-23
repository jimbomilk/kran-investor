import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children }) => {
  // const { user } = useAuth(); // Descomentar cuando AuthContext esté implementado

  // Placeholder para simulación. En la app real, se usará el `user` del contexto.
  const isAuthenticated = false; // Cambiar a `true` para acceder a /dashboard

  if (!isAuthenticated) {
    // Redirige al usuario a la página de login si no está autenticado.
    // `replace` evita que la ruta protegida se guarde en el historial de navegación.
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;