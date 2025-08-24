import React, { createContext, useState, useContext, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Limpiar errores al cambiar de ruta
  useEffect(() => {
    if (error) setError(null);
  }, [location.pathname]);

  useEffect(() => {
    const tokenInStorage = localStorage.getItem('token');
    if (tokenInStorage) {
      setToken(tokenInStorage);
      api.setAuthToken(tokenInStorage);
      setUser({ token: tokenInStorage });
    }
    setLoading(false);
  }, []);

  const login = async (credentials) => {
    try {
      const { data } = await api.login(credentials);
      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
      api.setAuthToken(data.access_token);
      setUser({ token: data.access_token });
      navigate('/dashboard');
    } catch (err) {
      const errorMessage = err.response?.data?.msg || "Error al iniciar sesión. Revisa tus credenciales.";
      setError(errorMessage);
    }
  };

  const register = async (userData) => {
    try {
      await api.register(userData);
      sessionStorage.setItem('authSuccessMessage', '¡Registro completado con éxito! Ahora puedes iniciar sesión.');
      navigate('/login');
    } catch (err) {
      const errorMessage = err.response?.data?.msg || "Error en el registro. Inténtalo de nuevo.";
      setError(errorMessage);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    api.setAuthToken(null);
    navigate('/login');
  };

  const value = { user, token, login, logout, register, loading, error };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  return useContext(AuthContext);
};