import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Aquí podrías verificar si ya existe un token en localStorage al cargar la app
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Aquí podrías validar el token contra el backend y obtener datos del usuario
      // Por ahora, lo dejamos como placeholder
      // setUser({ token });
    }
    setLoading(false);
  }, []);

  const login = async (credentials) => {
    const { data } = await api.login(credentials);
    localStorage.setItem('token', data.access_token);
    setUser({ token: data.access_token });
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const value = { user, login, logout, loading };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  return useContext(AuthContext);
};