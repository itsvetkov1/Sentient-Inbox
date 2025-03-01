import React from 'react';
import { motion } from 'framer-motion';

const steps = [
  {
    number: '01',
    title: 'Connect Your Email',
    description: 'Securely connect your email account to Sentient Inbox. We support all major email providers including Gmail, Outlook, and more.',
    color: '#4A6CF7',
  },
  {
    number: '02',
    title: 'AI Analyzes Your Messages',
    description: 'Our advanced AI analyzes your incoming emails, identifying meeting requests and categorizing them by priority and action required.',
    color: '#F97316',
  },
  {
    number: '03',
    title: 'Extract Meeting Details',
    description: 'The system automatically extracts key meeting information like date, time, location, and participants, even from unstructured text.',
    color: '#8A9EF9',
  },
  {
    number: '04',
    title: 'Generate Smart Responses',
    description: 'Sentient Inbox crafts appropriate responses based on your calendar availability and meeting preferences.',
    color: '#4A6CF7',
  },
];

const HowItWorks = () => {
  return (
    <section id="how-it-works" style={{ 
      padding: '100px 0', 
      backgroundColor: 'var(--background-color)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Background decorative elements */}
      <div style={{ 
        position: 'absolute',
        width: '500px',
        height: '500px',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(74, 108, 247, 0.05) 0%, rgba(74, 108, 247, 0) 70%)',
        top: '-250px',
        left: '-100px',
        zIndex: '0'
      }} />
      
      <div style={{ 
        position: 'absolute',
        width: '300px',
        height: '300px',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(249, 115, 22, 0.05) 0%, rgba(249, 115, 22, 0) 70%)',
        bottom: '-150px',
        right: '-50px',
        zIndex: '0'
      }} />
      
      <div className="container" style={{ 
        maxWidth: '1280px', 
        margin: '0 auto', 
        padding: '0 1rem',
        position: 'relative',
        zIndex: '1'
      }}>
        {/* Section Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          style={{ 
            textAlign: 'center', 
            maxWidth: '600px', 
            margin: '0 auto', 
            marginBottom: '60px' 
          }}
        >
          <h2 style={{ 
            fontSize: '36px', 
            fontWeight: '700', 
            color: 'var(--text-color)', 
            marginBottom: '16px' 
          }}>
            How It Works
          </h2>
          <p style={{ 
            fontSize: '16px', 
            color: 'var(--body-color)', 
            lineHeight: '1.6' 
          }}>
            Our intelligent system works seamlessly in the background to manage your email communications
          </p>
        </motion.div>

        {/* Steps */}
        <div style={{ 
          display: 'flex',
          flexDirection: 'column',
          gap: '40px',
          maxWidth: '800px',
          margin: '0 auto'
        }}>
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: index % 2 === 0 ? -30 : 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.15 }}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '24px',
                backgroundColor: 'white',
                padding: '30px',
                borderRadius: '12px',
                boxShadow: '0 5px 15px rgba(0, 0, 0, 0.05)',
              }}
            >
              <div style={{ 
                minWidth: '50px',
                height: '50px',
                borderRadius: '50%',
                backgroundColor: step.color,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: '700',
                fontSize: '18px'
              }}>
                {step.number}
              </div>
              <div>
                <h3 style={{ 
                  fontSize: '22px', 
                  fontWeight: '600', 
                  marginBottom: '10px', 
                  color: 'var(--text-color)' 
                }}>
                  {step.title}
                </h3>
                <p style={{ 
                  fontSize: '15px', 
                  color: 'var(--body-color)', 
                  lineHeight: '1.6' 
                }}>
                  {step.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;