import React from 'react';
import '../styles/Pricing.css';



const Pricing = () => {
  const pricingPlans = [
    {
      name: 'Starter',
      price: 'Free',
      period: 'Forever',
      best: false,
      features: [
        '✅ Centralized stock market info sharing in Discord',
        '✅ View basic real-time stock and company data',
        '✅ View historical stock performance',
        '✅ Set up alerts up to 5 stocks',
        '✅ View news about stocks',
        '❌ Complex stock analysis',
        '❌ Comparison between stocks',
        '❌ Comparison of stocks against S&P 500',
      ],
      buttonText: 'Get Started',
      buttonLink: 'https://discord.com/oauth2/authorize?client_id=1415287898760286303&permissions=292058082304&integration_type=0&scope=bot',
      note: 'Experiment before committing'
    },
    {
      name: 'PRO',
      price: '$2.99',
      period: 'per month',
      best: true,
      features: [
        '✅ All Free tier features',
        '✅ Complex metrics for deeper insights',
        '✅ Set up alerts for up to 50 stocks',
        '✅ Comparison between stocks',
        '✅ Comparison of stocks against S&P 500',
        '✅ Priority support',
      ],
      buttonText: 'Subscribe Now',
      buttonLink: "https://discord.com/discovery/applications/1415287898760286303/store",
      note: 'Start monitoring multiple stocks and analyzing complex metrics'
    },

  ];

  return (
    <section id="pricing" className="pricing">
      <div className="container">
        <h2 className="section-title">Choose Your Plan</h2>
        <p className="pricing-subtitle">Get the financial insights your Discord community needs</p>
        <div className="pricing-grid">
          
          {pricingPlans.map((plan, index) => (
            <div key={index} className={`pricing-card ${plan.best ? 'pricing-card-popular' : ''}`}>
              {plan.best && <div className="popular-badge">Best Value</div>}
              <div className="pricing-header">
                <h3>{plan.name}</h3>
                <div className="price">
                  <span className="price-amount">{plan.price}</span>
                  <span className="price-period">{plan.period}</span>
                </div>
              </div>
              <div className="pricing-features">
                <ul>
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex}>{feature}</li>
                  ))}
                </ul>
              </div>
              <div className="pricing-footer">
                <a href={plan.buttonLink} target="_blank" className={`btn ${plan.best ? 'btn-primary' : 'btn-outline'}`}>
                  {plan.buttonText}
                </a>
                <p className="pricing-note">{plan.note}</p>
              </div>
            </div>
          ))}
        </div>


      </div>
    </section>
  );
};

export default Pricing;