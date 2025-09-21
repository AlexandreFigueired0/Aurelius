import React from 'react';
import '../styles/StockTicker.css';

const TickerItem = ({ img, ticker, price, change, positive }) => (
  <div className="ticker-item">
    <img src={img} alt={`${ticker} logo`} className="ticker-logo" />
    <span className="ticker">{ticker}</span>
    <span className="price-info">
      <span className={`change ${positive ? 'positive' : 'negative'}`}>{change}</span>
      <span className={`price ${positive ? 'positive' : 'negative'}`}>{price}</span>
    </span>
  </div>
);

const StockTicker = () => {
  const stockData = [
    { img: 'src/assets/aapl.png', ticker: 'AAPL', price: '$175.43', change: '+1.35%', positive: true },
    { img: 'src/assets/googl.png', ticker: 'GOOGL', price: '$284.52', change: '+0.85%', positive: true },
    { img: 'src/assets/tsla.png', ticker: 'TSLA', price: '$470.60', change: '-2.56%', positive: false },
    { img: 'src/assets/msft.png', ticker: 'MSFT', price: '$462.89', change: '+2.11%', positive: true },
    { img: 'src/assets/amzn.png', ticker: 'AMZN', price: '$233.69', change: '+1.74%', positive: true },
    { img: 'src/assets/nvda.png', ticker: 'NVDA', price: '$170.60', change: '+10.35%', positive: true },
    { img: 'src/assets/meta.png', ticker: 'META', price: '$487.32', change: '-0.94%', positive: false },
    { img: 'src/assets/nflx.png', ticker: 'NFLX', price: '$1,222.45', change: '+1.12%', positive: true },
    { img: 'src/assets/pltr.png', ticker: 'PLTR', price: '$182.37', change: '-0.01%', positive: false },
    { img: 'src/assets/intc.png', ticker: 'INTC', price: '$29.14', change: '-0.27%', positive: false }
  ];

  return (
    <section className="stock-ticker">
      <div className="ticker-container">
        <div className="ticker-content">
          {stockData.map((stock, index) => (
            <TickerItem
              key={index}
              img={stock.img}
              ticker={stock.ticker}
              price={stock.price}
              change={stock.change}
              positive={stock.positive}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default StockTicker;