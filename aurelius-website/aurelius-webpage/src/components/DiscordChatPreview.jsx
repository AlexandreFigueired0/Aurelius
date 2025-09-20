import React from 'react';
import '../styles/DiscordChatPreview.css';

const DiscordChatPreview = () => {
  return (
    <div className="hero-visual">
      <div className="bot-preview">
        <div className="chat-header">
          <div className="server-info">
            <span className="server-name"># 💹 market-discussion</span>
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
              <h3>📈 AAPL - $175.43 <span className="change positive">+2.34 (+1.35%)</span></h3>
              <div className="stock-details">
                <span>Volume: 45.2M</span>
                <span>Market Cap: $2.73T</span>
              </div>
              <div className="mini-chart">📊 ▲ ▲ ▲ ▲ ▲</div>
            </div>
          </div>
        </div>

        <div className="discord-message">
          <div className="message-header">
            <div className="avatar">🤖</div>
            <span className="bot-name">Aurelius</span>
            <span className="bot-tag">BOT</span>
            <span className="timestamp">Today at 2:16 PM</span>
          </div>
          <div className="message-content">
            <div className="stock-card negative">
              <h3>📉 TSLA - $198.52 <span className="change negative">-5.23 (-2.56%)</span></h3>
              <div className="stock-details">
                <span>Volume: 62.1M</span>
                <span>P/E Ratio: 23.45</span>
              </div>
              <div className="mini-chart">📊 ▼ ▼ ▼ ▼ ▼</div>
            </div>
          </div>
        </div>

        <div className="discord-message">
          <div className="message-header">
            <div className="avatar">👤</div>
            <span className="username">TraderJoe</span>
            <span className="timestamp">Today at 2:17 PM</span>
          </div>
          <div className="message-content">
            <p>Amazing bot! Just saved me so much time 🚀</p>
          </div>
        </div>

        <div className="typing-indicator">
          <div className="avatar">🤖</div>
          <span>Aurelius is typing...</span>
          <div className="dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiscordChatPreview;