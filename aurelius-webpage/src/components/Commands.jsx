import React from 'react';
import '../styles/Commands.css';

const Commands = () => {
  const commandCategories = [
    {
      title: 'Stock Information',
      commands: [
        {
          command: '/stock AAPL',
          description: 'Get current stock price and basic info'
        },
        {
          command: '/chart TSLA 1d',
          description: 'Display price chart for specified timeframe'
        },
        {
          command: '/info MSFT',
          description: 'Get information about a specific company'
        },
        {
          command: '/metrics AMZN',
          description: 'Get key financial metrics for a stock'
        }
      ]
    },
    {
      title: 'News & Alerts',
      commands: [
        {
          command: '/news AAPL',
          description: 'Get latest news for specific stock'
        },
        {
          command: '/watch TSLA 8',
          description: 'Set an alert for percentage price changes of a stock'
        },
        {
          command: '/unwatch TSLA',
          description: 'Remove an alert for a specific stock'
        },
        {
          command: '/list',
          description: 'View your watchlist'
        }
      ]
    },
    {
      title: 'Comparsions',
      commands: [
        {
          command: '/compare TSLA NVDA',
          description: 'Compare two stocks side by side'
        },
        {
          command: '/compare_sp500 GOOGL',
          description: 'Compare a stock against the S&P 500 index'
        },

      ]
    }
  ];

  return (
    <section id="commands" className="commands">
      <div className="container">
        <h2 className="section-title">Bot Commands</h2>
        <div className="commands-container">
          {commandCategories.map((category, index) => (
            <div key={index} className="command-category">
              <h3>{category.title}</h3>
              <div className="command-list">
                {category.commands.map((cmd, cmdIndex) => (
                  <div key={cmdIndex} className="command-item">
                    <code>{cmd.command}</code>
                    <p>{cmd.description}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Commands;