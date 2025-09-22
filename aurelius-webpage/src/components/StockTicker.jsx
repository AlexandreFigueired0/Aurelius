import React from 'react';
import '../styles/StockTicker.css';

// Import all stock images
import aaplImg from '../assets/aapl.png';
import googlImg from '../assets/googl.png';
import tslaImg from '../assets/tsla.png';
import msftImg from '../assets/msft.png';
import amznImg from '../assets/amzn.png';
import nvdaImg from '../assets/nvda.png';
import metaImg from '../assets/meta.png';
import nflxImg from '../assets/nflx.png';
import pltrImg from '../assets/pltr.png';
import intcImg from '../assets/intc.png';

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
    { img: aaplImg, ticker: 'AAPL', price: '$175.43', change: '+1.35%', positive: true },
    { img: googlImg, ticker: 'GOOGL', price: '$284.52', change: '+0.85%', positive: true },
    { img: tslaImg, ticker: 'TSLA', price: '$470.60', change: '-2.56%', positive: false },
    { img: msftImg, ticker: 'MSFT', price: '$462.89', change: '+2.11%', positive: true },
    { img: amznImg, ticker: 'AMZN', price: '$233.69', change: '+1.74%', positive: true },
    { img: nvdaImg, ticker: 'NVDA', price: '$170.60', change: '+10.35%', positive: true },
    { img: metaImg, ticker: 'META', price: '$487.32', change: '-0.94%', positive: false },
    { img: nflxImg, ticker: 'NFLX', price: '$1,222.45', change: '+1.12%', positive: true },
    { img: pltrImg, ticker: 'PLTR', price: '$182.37', change: '-0.01%', positive: false },
    { img: intcImg, ticker: 'INTC', price: '$29.14', change: '-0.27%', positive: false }
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