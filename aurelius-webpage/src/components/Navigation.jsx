import React from 'react';
import '../styles/Navigation.css';

const Navigation = () => {
  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-logo">
          <h2>Aurelius</h2>
        </div>
        <div className="nav-links">
          <a href="#features">Features</a>
          <a href="#pricing">Pricing</a>
          <a href="#commands">Commands</a>
          <a href="#invite">Invite Bot</a>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;