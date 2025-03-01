import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const CTA = () => {
  return (
    <section style={{ 
      padding: '100px 0', 
      backgroundColor: 'white',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div style={{
        position: 'absolute',
        width: '100%',
        height: '100%',
        background: 'linear-gradient(135deg, rgba(74, 108, 247, 0.03) 0%, rgba(249, 115, 22, 0.03) 100%)',
        top: 0,
        left: 0,
        zIndex: 0
      }} />
      
      <div className="container" style={{ 
        maxWidth: '1280px', 
        margin: '0 auto', 
        padding: '0 1rem',
        position: 'relative',
        zIndex: 1
      }}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          style={{
            backgroundColor: 'var(--primary-color)',
            padding: '60px',
            borderRadius: '20px',
            boxShadow: '0 20px 40px rgba(74, 108, 247, 0.2)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center'
          }}
        >
          <h2 style={{
            fontSize: '36px',
            fontWeight: '700',
            color: 'white',
            marginBottom: '24px',
            maxWidth: '700px'
          }}>
            Ready to Transform Your Email Experience?
          </h2>
          
          <p style={{
            fontSize: '18px',
            lineHeight: '1.6',
            color: 'rgba(255, 255, 255, 0.9)',
            marginBottom: '40px',
            maxWidth: '700px'
          }}>
            Join thousands of professionals who have reclaimed their productivity with Sentient Inbox.
            Get started today and experience the power of AI-driven email management.
          </p>
          
          <div style={{
            display: 'flex',
            gap: '16px',
            flexWrap: 'wrap',
            justifyContent: 'center'
          }}>
            <Link
              to="/login"
              style={{
                backgroundColor: 'white',
                color: 'var(--primary-color)',
                padding: '16px 32px',
                borderRadius: '6px',
                fontWeight: '600',
                fontSize: '16px',
                transition: 'all 0.3s ease',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              Get Started
            </Link>
            
            <Link
              to="#features"
              style={{
                backgroundColor: 'transparent',
                color: 'white',
                padding: '16px 32px',
                borderRadius: '6px',
                fontWeight: '600',
                fontSize: '16px',
                border: '1.5px solid white',
                transition: 'all 0.3s ease',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              Learn More
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default CTA;