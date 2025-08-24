import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, error } = useAuth();
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    const msg = sessionStorage.getItem('authSuccessMessage');
    if (msg) {
      setSuccessMessage(msg);
      sessionStorage.removeItem('authSuccessMessage');
    }
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    login({ email, password });
  };

  return (
    <div className="flex items-center justify-center h-screen bg-gray-900">
      <div className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold text-center text-white">Iniciar Sesión</h1>
        
        {successMessage && <div className="bg-green-500 text-white p-2 rounded">{successMessage}</div>}
        {error && <div className="bg-red-500 text-white p-2 rounded">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block mb-2 text-sm font-bold text-gray-400">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 text-white bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block mb-2 text-sm font-bold text-gray-400">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 text-white bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <button type="submit" className="w-full px-4 py-2 font-bold text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-500 focus:ring-opacity-50">
            Entrar
          </button>
        </form>
        <p className="text-sm text-center text-gray-400">
          ¿No tienes una cuenta? <Link to="/register" className="font-medium text-blue-500 hover:underline">Regístrate</Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;