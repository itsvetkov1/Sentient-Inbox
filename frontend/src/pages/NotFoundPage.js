import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const NotFoundPage = () => {
  return (
    <div style={{ 
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: 'var(--background-color)',
      padding: '20px',
    }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          textAlign: 'center',
          maxWidth: '500px',
        }}
      >
        <div style={{ 
          fontSize: '120px', 
          fontWeight: '700',
          color: 'var(--primary-color)',
          lineHeight: '1',
          marginBottom: '24px',
        }}>
          404
        </div>
        
        <h1 style={{ 
          fontSize: '28px',
          fontWeight: '700',
          color: 'var(--text-color)',
          marginBottom: '16px',
        }}>
          Page Not Found
        </h1>
        
        <p style={{ 
          fontSize: '16px',
          color: 'var(--body-color)',
          marginBottom: '32px',
          lineHeight: '1.6',
        }}>
          The page you're looking for doesn't exist or has been moved.
        </p>
        
        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px' }}>
          <Link
            to="/"
            style={{
              backgroundColor: 'transparent',
              color: 'var(--primary-color)',
              border: '1.5px solid var(--primary-color)',
              borderRadius: '6px',
              padding: '12px 24px',
              fontWeight: '500',
              textDecoration: 'none',
              transition: 'all 0.3s ease',
            }}
          >
            Go Home
          </Link>
          
          <Link
            to="/dashboard"
            style={{
              backgroundColor: 'var(--primary-color)',
              color: 'white',
              borderRadius: '6px',
              padding: '12px 24px',
              fontWeight: '500',
              textDecoration: 'none',
              transition: 'all 0.3s ease',
            }}
          >
            Go to Dashboard
          </Link>
        </div>
      </motion.div>
    </div>
  );
};

export default NotFoundPage;