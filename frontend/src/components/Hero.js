import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const Hero = () => {
  return (
    <section
      style={{
        position: 'relative',
        padding: '180px 0 120px',
        overflow: 'hidden',
        backgroundImage: 'linear-gradient(180deg, rgba(249, 250, 255, 0.7) 0%, rgba(249, 250, 255, 1) 100%)',
      }}
    >
      {/* Abstract Background Elements */}
      <div style={{ position: 'absolute', top: '0', right: '0', zIndex: '-1', opacity: '0.7', width: '50%', height: '100%' }}>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.7 }}
          transition={{ duration: 1.5 }}
          style={{
            position: 'absolute',
            top: '20%',
            right: '-5%',
            width: '350px',
            height: '350px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(74, 108, 247, 0.15) 0%, rgba(74, 108, 247, 0) 70%)',
          }}
        />
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.7 }}
          transition={{ duration: 1.5, delay: 0.3 }}
          style={{
            position: 'absolute',
            top: '40%',
            right: '15%',
            width: '250px',
            height: '250px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(249, 115, 22, 0.15) 0%, rgba(249, 115, 22, 0) 70%)',
          }}
        />
      </div>

      <div className="container" style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 1rem' }}>
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
            maxWidth: '800px',
            margin: '0 auto',
          }}
        >
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
          >
            <h1
              style={{
                fontSize: '48px',
                fontWeight: '700',
                marginBottom: '24px',
                lineHeight: '1.2',
                color: 'var(--text-color)',
              }}
            >
              Intelligent Email Management with{' '}
              <span className="text-gradient" style={{ 
                backgroundImage: 'linear-gradient(to right, var(--primary-color), var(--secondary-color))',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                color: 'transparent',
               }}>
                AI-Powered
              </span>{' '}
              Automation
            </h1>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            <p
              style={{
                fontSize: '18px',
                lineHeight: '1.6',
                marginBottom: '40px',
                color: 'var(--body-color)',
                maxWidth: '700px',
              }}
            >
              Sentient Inbox intelligently analyzes your emails, classifies meeting requests, and 
              generates appropriate responses, saving you hours of manual email management.
              Focus on what matters while AI handles your inbox.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.4 }}
            style={{
              display: 'flex',
              gap: '16px',
              flexWrap: 'wrap',
              justifyContent: 'center',
            }}
          >
            <Link
              to="/login"
              style={{
                backgroundColor: 'var(--primary-color)',
                color: 'white',
                padding: '14px 32px',
                borderRadius: '6px',
                fontWeight: '500',
                fontSize: '16px',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.3s ease',
              }}
              className="btn btn-primary"
            >
              Get Started
            </Link>
            <Link
              to="#how-it-works"
              style={{
                backgroundColor: 'transparent',
                color: 'var(--primary-color)',
                padding: '14px 32px',
                borderRadius: '6px',
                fontWeight: '500',
                fontSize: '16px',
                border: '1.5px solid var(--primary-color)',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.3s ease',
              }}
              className="btn btn-secondary"
            >
              How It Works
            </Link>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.6 }}
            style={{
              display: 'flex',
              justifyContent: 'center',
              gap: '40px',
              marginTop: '80px',
              flexWrap: 'wrap',
            }}
          >
            <div style={{ textAlign: 'center' }}>
              <h3 style={{ fontSize: '36px', fontWeight: '700', color: 'var(--primary-color)', marginBottom: '8px' }}>85%</h3>
              <p style={{ fontSize: '16px', color: 'var(--body-color)' }}>Time Saved</p>
            </div>
            <div style={{ textAlign: 'center' }}>
              <h3 style={{ fontSize: '36px', fontWeight: '700', color: 'var(--primary-color)', marginBottom: '8px' }}>95%</h3>
              <p style={{ fontSize: '16px', color: 'var(--body-color)' }}>Accuracy</p>
            </div>
            <div style={{ textAlign: 'center' }}>
              <h3 style={{ fontSize: '36px', fontWeight: '700', color: 'var(--primary-color)', marginBottom: '8px' }}>24/7</h3>
              <p style={{ fontSize: '16px', color: 'var(--body-color)' }}>Processing</p>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default Hero;