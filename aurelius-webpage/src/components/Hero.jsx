import React from 'react';
import DiscordChatPreview from './DiscordChatPreview';
import '../styles/Hero.css';

const Hero = () => {
  return (
    <section className="hero">
      <div className="hero-container">
        <div className="hero-content">
          <h1 className="hero-title">
            Aurelius
            <span className="hero-subtitle">Financial Discord Bot</span>
          </h1>
          <p className="hero-description">
            Access real-time stock market info, charts, and financial news directly in your Discord server. 
            Discuss investments with your community and make informed decisions.
          </p>
          <div className="hero-buttons">
            <a target="_blank" href="https://discord.com/oauth2/authorize?client_id=1415287898760286303&permissions=292058082304&integration_type=0&scope=bot" className="btn btn-primary">Add to Discord</a>
            <a href="#features" className="btn btn-secondary">Learn More</a>
          </div>
        </div>
        <DiscordChatPreview />
      </div>
    </section>
  );
};

export default Hero;