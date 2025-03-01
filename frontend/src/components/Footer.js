import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer style={{ 
      backgroundColor: 'var(--text-color)',
      padding: '80px 0 30px',
      color: 'white'
    }}>
      <div className="container" style={{ 
        maxWidth: '1280px', 
        margin: '0 auto', 
        padding: '0 1rem'
      }}>
        <div style={{ 
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '40px',
          marginBottom: '60px'
        }}>
          {/* Company Info */}
          <div>
            <Link to="/" style={{ display: 'inline-block', marginBottom: '20px' }}>
              <div style={{ fontSize: '24px', fontWeight: 700, color: 'white' }}>
                Sentient<span style={{ color: 'var(--primary-light)' }}>Inbox</span>
              </div>
            </Link>
            <p style={{ 
              fontSize: '15px',
              lineHeight: '1.6',
              color: 'rgba(255, 255, 255, 0.8)',
              marginBottom: '24px'
            }}>
              Intelligent email management for modern professionals. Powered by advanced AI to help you focus on what matters.
            </p>
          </div>
          
          {/* Quick Links */}
          <div>
            <h3 style={{ 
              fontSize: '18px', 
              fontWeight: '600', 
              marginBottom: '24px',
              color: 'white'
            }}>
              Quick Links
            </h3>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              <li style={{ marginBottom: '12px' }}>
                <Link to="/" style={{ 
                  color: 'rgba(255, 255, 255, 0.8)', 
                  fontSize: '15px',
                  transition: 'all 0.3s ease',
                  textDecoration: 'none'
                }}>
                  Home
                </Link>
              </li>
              <li style={{ marginBottom: '12px' }}>
                <Link to="#features" style={{ 
                  color: 'rgba(255, 255, 255, 0.8)', 
                  fontSize: '15px',
                  transition: 'all 0.3s ease',
                  textDecoration: 'none'
                }}>
                  Features
                </Link>
              </li>
              <li style={{ marginBottom: '12px' }}>
                <Link to="#how-it-works" style={{ 
                  color: 'rgba(255, 255, 255, 0.8)', 
                  fontSize: '15px',
                  transition: 'all 0.3s ease',
                  textDecoration: 'none'
                }}>
                  How It Works
                </Link>
              </li>
              <li style={{ marginBottom: '12px' }}>
                <Link to="/login" style={{ 
                  color: 'rgba(255, 255, 255, 0.8)', 
                  fontSize: '15px',
                  transition: 'all 0.3s ease',
                  textDecoration: 'none'
                }}>
                  Login
                </Link>
              </li>
            </ul>
          </div>
          
          {/* Resources */}
          <div>
            <h3 style={{ 
              fontSize: '18px', 
              fontWeight: '600', 
              marginBottom: '24px',
              color: 'white'
            }}>
              Resources
            </h3>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              <li style={{ marginBottom: '12px' }}>
                <Link to="#" style={{ 
                  color: 'rgba(255, 255, 255, 0.8)', 
                  fontSize: '15px',
                  transition: 'all 0.3s ease',
                  textDecoration: 'none'
                }}>
                  Documentation
                </Link>
              </li>
              <li style={{ marginBottom: '12px' }}>
                <Link to="#" style={{ 
                  color: 'rgba(255, 255, 255, 0.8)', 
                  fontSize: '15px',
                  transition: 'all 0.3s ease',
                  textDecoration: 'none'
                }}>
                  API Reference
                </Link>
              </li>
              <li style={{ marginBottom: '12px' }}>
                <Link to="#" style={{ 
                  color: 'rgba(255, 255, 255, 0.8)', 
                  fontSize: '15px',
                  transition: 'all 0.3s ease',
                  textDecoration: 'none'
                }}>
                  Privacy Policy
                </Link>
              </li>
              <li style={{ marginBottom: '12px' }}>
                <Link to="#" style={{ 
                  color: 'rgba(255, 255, 255, 0.8)', 
                  fontSize: '15px',
                  transition: 'all 0.3s ease',
                  textDecoration: 'none'
                }}>
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
          
          {/* Contact */}
          <div>
            <h3 style={{ 
              fontSize: '18px', 
              fontWeight: '600', 
              marginBottom: '24px',
              color: 'white'
            }}>
              Contact Us
            </h3>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              <li style={{ marginBottom: '16px' }}>
                <div style={{ 
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '10px',
                  color: 'rgba(255, 255, 255, 0.8)', 
                  fontSize: '15px',
                }}>
                  <span style={{ fontWeight: '500' }}>Email:</span>
                  <span>support@sentientinbox.com</span>
                </div>
              </li>
              <li style={{ marginBottom: '16px' }}>
                <div style={{ 
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '10px',
                  color: 'rgba(255, 255, 255, 0.8)', 
                  fontSize: '15px',
                }}>
                  <span style={{ fontWeight: '500' }}>Phone:</span>
                  <span>+1 (555) 123-4567</span>
                </div>
              </li>
              <li>
                <div style={{ 
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '10px',
                  color: 'rgba(255, 255, 255, 0.8)', 
                  fontSize: '15px',
                }}>
                  <span style={{ fontWeight: '500' }}>Address:</span>
                  <span>123 AI Avenue, Tech City, CA 94103</span>
                </div>
              </li>
            </ul>
          </div>
        </div>
        
        {/* Copyright */}
        <div style={{ 
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          paddingTop: '30px',
          textAlign: 'center',
          color: 'rgba(255, 255, 255, 0.6)',
          fontSize: '14px'
        }}>
          <p>© {currentYear} Sentient Inbox. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;