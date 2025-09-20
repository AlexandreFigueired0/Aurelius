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
          command: '/company MSFT',
          description: 'Get detailed company information'
        }
      ]
    },
    {
      title: 'Market Data',
      commands: [
        {
          command: '/market',
          description: 'View overall market status and indices'
        },
        {
          command: '/gainers',
          description: 'Show today\'s top gaining stocks'
        },
        {
          command: '/losers',
          description: 'Show today\'s top losing stocks'
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
          command: '/alert TSLA 200',
          description: 'Set price alert for stock'
        },
        {
          command: '/watchlist',
          description: 'Manage your stock watchlist'
        }
      ]
    }
  ];

  return (
    <section id="commands" className="commands">
      <div className="container">
        <h2 className="section-title">Bot Commands</h2>
        <div className="commands-grid">
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