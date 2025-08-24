import React from 'react';

const PortfolioTable = ({ holdings }) => {
  if (!holdings || holdings.length === 0) {
    return <p className="text-gray-400">No tienes activos en tu cartera.</p>;
  }

  return (
    <div className="overflow-x-auto mt-6">
      <table className="min-w-full bg-gray-800 rounded-lg shadow-md">
        <thead>
          <tr className="bg-gray-700 text-gray-300 uppercase text-sm leading-normal">
            <th className="py-3 px-6 text-left">Símbolo</th>
            <th className="py-3 px-6 text-left">Cantidad</th>
            <th className="py-3 px-6 text-left">Valor de Mercado</th>
          </tr>
        </thead>
        <tbody className="text-gray-200 text-sm font-light">
          {holdings.map((holding) => (
            <tr key={holding.ticker_symbol} className="border-b border-gray-700 hover:bg-gray-700">
              <td className="py-3 px-6 text-left whitespace-nowrap">{holding.ticker_symbol}</td>
              <td className="py-3 px-6 text-left">{holding.quantity}</td>
              <td className="py-3 px-6 text-left">${holding.current_market_value ? holding.current_market_value.toFixed(2) : 'N/A'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PortfolioTable;