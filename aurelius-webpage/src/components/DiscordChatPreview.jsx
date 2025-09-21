import React from 'react';
import '../styles/DiscordChatPreview.css';

const DiscordChatPreview = () => {
  return (
    <div className="hero-visual">
      <div className="bot-preview">
        <div className="chat-header">
          <div className="server-info">
            <span className="server-name"># 📈 stock-alerts</span>
            <span className="member-count">1,247 members online</span>
          </div>
        </div>
        
        <div className="discord-message">
          <div className="message-header">
            <div className="avatar">🤖</div>
            <span className="bot-name">Aurelius</span>
            <span className="bot-tag">BOT</span>
            <span className="timestamp">Today at 2:15 PM</span>
          </div>
          <div className="message-content">
            <div className="stock-card">
              <h3>🚨 NVDA Price alert! </h3>
              <div className="stock-details">
                <div>Price: $170.60</div>
                <div>
                  <span>Change:</span> <span className="change positive">(+10.35%)</span>
                </div>
              </div>
            </div>
          </div>
        </div>

              <div className="discord-message">
          <div className="message-header">
            <div className="avatar">👤</div>
            <span className="username">User</span>
            <span className="timestamp">Today at 2:17 PM</span>
          </div>
          <div className="message-content">
            <p>!stock Amazon</p>
          </div>
        </div>

        <div className="discord-message">
          <div className="message-header">
            <div className="avatar">🤖</div>
            <span className="bot-name">Aurelius</span>
            <span className="bot-tag">BOT</span>
            <span className="timestamp">Today at 2:17 PM</span>
          </div>
          <div className="message-content">
            <div className="stock-card dashboard">
              <h3>📊 AMZN Stock Dashboard</h3>
              <div className="stock-info">
                <div className="stock-header">
                </div>
                <div className="stock-metrics">
                  <span className="metric">
                    <span className="metric-label">💰 Price: </span>
                    <span className="metric-value">$231.48 USD</span>
                  </span>
                  <span className="metric">
                    <span className="metric-label">📈 Change: </span>
                    <span className="metric-value change negative">-0.03%</span>
                  </span>
                  <span className="metric">
                    <span className="metric-label">🏢 Market Cap: </span>
                    <span className="metric-value">$2.4T</span>
                  </span>
                </div>
                <div className="chart-section">
                  <img src="src/assets/chart.png" alt="AMZN Stock Chart - Last 1 Month" className="stock-chart" />
                </div>
                <div className="data-source">
                  <small>Data provided by Yahoo Finance (yfinance)</small>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default DiscordChatPreview;