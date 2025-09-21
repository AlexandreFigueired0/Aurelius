import React from 'react';
import '../styles/Invite.css';

const Invite = () => {
  const stats = [
    { value: '10,000+', label: 'Servers' },
    { value: '500,000+', label: 'Users' },
    { value: '99.9%', label: 'Uptime' }
  ];

  return (
    <section id="invite" className="invite">
      <div className="container">
        <div className="invite-content">
          <h2>Ready to Get Started?</h2>
          <p>Add Aurelius to your Discord server and start tracking the stock market with your community.</p>
          <div className="invite-buttons">
            <a href="#" className="btn btn-primary btn-large">
              🤖 Add to Discord
            </a>
            <a href="#" className="btn btn-outline">
              📖 Documentation
            </a>
          </div>
          <div className="invite-stats">
            {stats.map((stat, index) => (
              <div key={index} className="stat">
                <h3>{stat.value}</h3>
                <p>{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Invite;