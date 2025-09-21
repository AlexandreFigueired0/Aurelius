import React from 'react';
import '../styles/Footer.css';

const Footer = () => {
  const footerSections = [
    {
      title: 'Aurelius',
      type: 'description',
      content: 'The ultimate Discord bot for financial market insights and real-time stock tracking.'
    },
    {
      title: 'Quick Links',
      type: 'links',
      links: [
        { label: 'Features', href: '#features' },
        { label: 'Pricing', href: '#pricing' },
        { label: 'Commands', href: '#commands' },
        { label: 'Invite Bot', href: '#invite' }
      ]
    },
    {
      title: 'Support',
      type: 'links',
      links: [
        { label: 'Documentation', href: '#' },
        { label: 'Support Server', href: '#' },
        { label: 'Status Page', href: '#' },
        { label: 'Manage Subscription', href: '#' }
      ]
    },
    {
      title: 'Legal',
      type: 'links',
      links: [
        { label: 'Privacy Policy', href: '#' },
        { label: 'Terms of Service', href: '#' }
      ]
    }
  ];

  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          {footerSections.map((section, index) => (
            <div key={index} className="footer-section">
              {section.type === 'description' ? (
                <>
                  <h3>{section.title}</h3>
                  <p>{section.content}</p>
                </>
              ) : (
                <>
                  <h4>{section.title}</h4>
                  <ul>
                    {section.links.map((link, linkIndex) => (
                      <li key={linkIndex}>
                        <a href={link.href}>{link.label}</a>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          ))}
        </div>
        <div className="footer-bottom">
          <p>&copy; 2025 Aurelius Bot. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;