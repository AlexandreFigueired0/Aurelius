import React from 'react';
import '../styles/Pricing.css';

const Pricing = () => {
  const pricingPlans = [
    {
      name: 'Starter',
      price: 'Free',
      period: 'Forever',
      popular: false,
      features: [
        '✅ Basic stock quotes',
        '✅ 10 stock lookups per day',
        '✅ Simple price alerts',
        '✅ Market indices',
        '✅ Community support',
        '❌ Real-time data',
        '❌ Advanced charts',
        '❌ Portfolio tracking'
      ],
      buttonText: 'Get Started',
      buttonLink: '#invite',
      note: 'Perfect for small communities'
    },
    {
      name: 'Professional',
      price: '$9.99',
      period: 'per month',
      popular: true,
      features: [
        '✅ Real-time stock data',
        '✅ Unlimited stock lookups',
        '✅ Advanced price alerts',
        '✅ Interactive charts',
        '✅ Portfolio tracking',
        '✅ Financial news',
        '✅ Technical indicators',
        '✅ Priority support',
        '✅ Custom watchlists'
      ],
      buttonText: 'Subscribe Now',
      buttonLink: '#subscribe-pro',
      note: '14-day free trial'
    },
    {
      name: 'Enterprise',
      price: '$29.99',
      period: 'per month',
      popular: false,
      features: [
        '✅ Everything in Professional',
        '✅ Multi-server support',
        '✅ Custom branding',
        '✅ Advanced analytics',
        '✅ API access',
        '✅ Dedicated support',
        '✅ Custom integrations',
        '✅ White-label options',
        '✅ SLA guarantee'
      ],
      buttonText: 'Contact Sales',
      buttonLink: '#contact-sales',
      note: 'Custom solutions available'
    }
  ];

  const subscriptionSteps = [
    {
      number: '1',
      title: 'Choose Your Plan',
      description: 'Select the subscription tier that fits your community\'s needs'
    },
    {
      number: '2',
      title: 'Secure Payment',
      description: 'Pay securely through our payment portal with Stripe integration'
    },
    {
      number: '3',
      title: 'Instant Access',
      description: 'Your bot gets upgraded immediately with premium features'
    }
  ];

  const subscriptionFeatures = [
    {
      icon: '🔒',
      title: 'Secure & Reliable',
      description: 'All payments processed securely through Stripe. Cancel anytime.'
    },
    {
      icon: '💎',
      title: 'Premium Support',
      description: 'Get priority support and feature requests with paid plans.'
    },
    {
      icon: '📈',
      title: 'Regular Updates',
      description: 'Continuous feature updates and improvements included.'
    }
  ];

  return (
    <section id="pricing" className="pricing">
      <div className="container">
        <h2 className="section-title">Choose Your Plan</h2>
        <p className="pricing-subtitle">Get the financial insights your Discord community needs</p>
        <div className="pricing-grid">
          
          {pricingPlans.map((plan, index) => (
            <div key={index} className={`pricing-card ${plan.popular ? 'pricing-card-popular' : ''}`}>
              {plan.popular && <div className="popular-badge">Most Popular</div>}
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
                <a href={plan.buttonLink} className={`btn ${plan.popular ? 'btn-primary' : 'btn-outline'}`}>
                  {plan.buttonText}
                </a>
                <p className="pricing-note">{plan.note}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Subscription Management */}
        <div className="subscription-info">
          <h3>How It Works</h3>
          <div className="subscription-steps">
            {subscriptionSteps.map((step, index) => (
              <div key={index} className="step">
                <div className="step-number">{step.number}</div>
                <h4>{step.title}</h4>
                <p>{step.description}</p>
              </div>
            ))}
          </div>
          <div className="subscription-features">
            {subscriptionFeatures.map((feature, index) => (
              <div key={index} className="feature-highlight">
                <h4>{feature.icon} {feature.title}</h4>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Pricing;