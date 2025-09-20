import React from 'react';
import '../styles/StockTicker.css';

const StockTicker = () => {
  const stockData = [
    { symbol: 'AAPL', price: '$175.43', change: '+1.35%', positive: true },
    { symbol: 'GOOGL', price: '$2,847.52', change: '+0.85%', positive: true },
    { symbol: 'TSLA', price: '$198.52', change: '-2.56%', positive: false },
    { symbol: 'MSFT', price: '$412.89', change: '+2.11%', positive: true },
    { symbol: 'AMZN', price: '$3,334.69', change: '+1.74%', positive: true },
    { symbol: 'NVDA', price: '$875.28', change: '+3.22%', positive: true },
    { symbol: 'META', price: '$487.32', change: '-0.94%', positive: false },
    { symbol: 'BTC', price: '$67,425.00', change: '+4.15%', positive: true },
  ];

  return (
    <section className="stock-ticker">
      <div className="ticker-container">
        <div className="ticker-content">
          {stockData.map((stock, index) => (
            <div key={index} className="ticker-item">
              <span className="symbol">{stock.symbol}</span>
              <span className={`price ${stock.positive ? 'positive' : 'negative'}`}>
                {stock.price}
              </span>
              <span className={`change ${stock.positive ? 'positive' : 'negative'}`}>
                {stock.change}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default StockTicker;