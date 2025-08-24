import React, { useState, useEffect, useContext } from 'react';
import PortfolioTable from '../components/PortfolioTable';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';

const DashboardPage = () => {
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { logout } = useContext(AuthContext);

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        const response = await api.getPortfolio();
        setPortfolio(response.data);
      } catch (err) {
        setError('Error al cargar la cartera. Por favor, inténtalo de nuevo más tarde.');
        if (err.response && err.response.status === 401) {
          logout();
        }
      }
      setLoading(false);
    };

    fetchPortfolio();
  }, [logout]);

  if (loading) {
    return <div className="p-8 text-center">Cargando...</div>;
  }

  if (error) {
    return <div className="p-8 text-center text-red-500">{error}</div>;
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <p className="mt-2 text-gray-400">Bienvenido a tu cartera virtual.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <div className="bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-300">Saldo Disponible</h2>
          <p className="text-3xl font-bold text-green-500 mt-2">
            ${portfolio.cash_balance ? portfolio.cash_balance.toFixed(2) : '0.00'}
          </p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-300">Valor Total de la Cartera</h2>
          <p className="text-3xl font-bold text-blue-500 mt-2">
            ${portfolio.total_portfolio_value ? portfolio.total_portfolio_value.toFixed(2) : '0.00'}
          </p>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Activos en Cartera</h2>
        <PortfolioTable holdings={portfolio.holdings} />
      </div>
    </div>
  );
};

export default DashboardPage;