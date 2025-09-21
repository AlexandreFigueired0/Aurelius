import React from 'react';
import Navigation from './components/Navigation';
import Hero from './components/Hero';
import StockTicker from './components/StockTicker';
import Features from './components/Features';
import Pricing from './components/Pricing';
import Commands from './components/Commands';
import Invite from './components/Invite';
import Footer from './components/Footer';
import './App.css';

function App() {
  return (
    <div className="App">
      <Navigation />
      <Hero />
      <StockTicker />
      <Features />
      <Pricing />
      <Commands />
      <Invite />
      <Footer />
    </div>
  );
}

export default App;
