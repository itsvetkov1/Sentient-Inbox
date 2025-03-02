import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';

const Header = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  return (
    <header
      className={`fixed top-0 left-0 w-full z-50 transition-all duration-300 ${
        scrolled ? 'bg-white shadow-md py-3' : 'bg-transparent py-5'
      }`}
      style={{
        backgroundColor: scrolled ? 'white' : 'transparent',
        boxShadow: scrolled ? '0 2px 10px rgba(0, 0, 0, 0.08)' : 'none',
        padding: scrolled ? '12px 0' : '20px 0',
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        zIndex: 50,
        transition: 'all 0.3s ease'
      }}
    >
      <div className="container" style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        maxWidth: '1280px',
        margin: '0 auto',
        padding: '0 1rem'
      }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center' }}>
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            style={{ fontSize: '24px', fontWeight: 700, color: 'var(--text-color)' }}
          >
            Sentient<span style={{ color: 'var(--primary-color)' }}>Inbox</span>
          </motion.div>
        </Link>

        {/* Desktop Navigation */}
        <nav style={{ 
          display: 'flex',
          alignItems: 'center',
          gap: '40px',
          '@media (max-width: 1024px)': {
            display: 'none'
          }
        }} className="hidden lg:flex items-center gap-10">
          <ul style={{ 
            display: 'flex',
            alignItems: 'center',
            gap: '32px',
            listStyle: 'none'
          }}>
            <li>
              <Link to="/" style={{ 
                color: 'var(--text-color)',
                fontWeight: 500,
                fontSize: '16px',
                transition: 'all 0.3s ease'
              }}>
                Home
              </Link>
            </li>
            <li>
              <Link to="#features" style={{ 
                color: 'var(--text-color)',
                fontWeight: 500,
                fontSize: '16px',
                transition: 'all 0.3s ease'
              }}>
                Features
              </Link>
            </li>
            <li>
              <Link to="#how-it-works" style={{ 
                color: 'var(--text-color)',
                fontWeight: 500,
                fontSize: '16px',
                transition: 'all 0.3s ease'
              }}>
                How It Works
              </Link>
            </li>
          </ul>

          <Link to="/login" style={{
            backgroundColor: 'var(--primary-color)',
            color: 'white',
            padding: '12px 24px',
            borderRadius: '6px',
            fontWeight: 500,
            transition: 'all 0.3s ease'
          }} className="btn btn-primary">
            Sign In
          </Link>
        </nav>

        {/* Mobile Menu Button */}
        <button
          onClick={toggleMobileMenu}
          style={{ 
            display: 'none',
            cursor: 'pointer',
            backgroundColor: 'transparent',
            border: 'none',
            padding: '8px',
            '@media (max-width: 1023px)': {
              display: 'block'
            }
          }}
          className="lg:hidden"
        >
          {mobileMenuOpen ? (
            <CloseIcon style={{ color: 'var(--text-color)' }} />
          ) : (
            <MenuIcon style={{ color: 'var(--text-color)' }} />
          )}
        </button>
      </div>

      {/* Mobile Navigation */}
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{
          opacity: mobileMenuOpen ? 1 : 0,
          height: mobileMenuOpen ? 'auto' : 0,
        }}
        transition={{ duration: 0.3 }}
        style={{ 
          overflow: 'hidden',
          backgroundColor: 'white',
          '@media (min-width: 1024px)': {
            display: 'none'
          }
        }}
        className="lg:hidden"
      >
        <div style={{ padding: '20px' }}>
          <ul style={{ listStyle: 'none' }}>
            <li style={{ marginBottom: '15px' }}>
              <Link 
                to="/" 
                style={{ 
                  color: 'var(--text-color)',
                  fontWeight: 500,
                  fontSize: '16px',
                  display: 'block',
                  padding: '8px 0'
                }}
                onClick={() => setMobileMenuOpen(false)}
              >
                Home
              </Link>
            </li>
            <li style={{ marginBottom: '15px' }}>
              <Link 
                to="#features" 
                style={{ 
                  color: 'var(--text-color)',
                  fontWeight: 500,
                  fontSize: '16px',
                  display: 'block',
                  padding: '8px 0'
                }}
                onClick={() => setMobileMenuOpen(false)}
              >
                Features
              </Link>
            </li>
            <li style={{ marginBottom: '15px' }}>
              <Link 
                to="#how-it-works" 
                style={{ 
                  color: 'var(--text-color)',
                  fontWeight: 500,
                  fontSize: '16px',
                  display: 'block',
                  padding: '8px 0'
                }}
                onClick={() => setMobileMenuOpen(false)}
              >
                How It Works
              </Link>
            </li>
            <li>
              <Link 
                to="/login" 
                style={{
                  backgroundColor: 'var(--primary-color)',
                  color: 'white',
                  padding: '12px 24px',
                  borderRadius: '6px',
                  fontWeight: 500,
                  display: 'inline-block',
                  marginTop: '10px'
                }}
                onClick={() => setMobileMenuOpen(false)}
              >
                Sign In
              </Link>
            </li>
          </ul>
        </div>
      </motion.div>
    </header>
  );
};

export default Header;