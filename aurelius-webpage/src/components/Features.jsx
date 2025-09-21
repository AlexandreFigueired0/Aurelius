import React from 'react';
import '../styles/Features.css';

const Features = () => {
  const features = [
    {
      icon: '📈',
      title: 'Real-Time Stock Data',
      description: 'Get instant access to live stock prices, market caps, and trading volumes for thousands of stocks worldwide.'
    },
    {
      icon: '📰',
      title: 'Financial News',
      description: 'Stay updated with the latest market news, earnings reports, and financial analysis from trusted sources.'
    },
    {
      icon: '🔍',
      title: 'Stock Analysis',
      description: 'Access detailed stock information, financial ratios, and fundamental analysis data.'
    },
    {
      icon: '⚡',
      title: 'Market Alerts',
      description: 'Set up custom alerts for price targets, volume spikes, and breaking financial news.'
    }
  ];

  return (
    <section id="features" className="features">
      <div className="container">
        <h2 className="section-title">Powerful Financial Tools</h2>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;