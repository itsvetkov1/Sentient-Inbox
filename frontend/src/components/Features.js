import React from 'react';
import { motion } from 'framer-motion';
import EmailIcon from '@mui/icons-material/Email';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import ScheduleIcon from '@mui/icons-material/Schedule';
import SecurityIcon from '@mui/icons-material/Security';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import AnalyticsIcon from '@mui/icons-material/Analytics';

const featureItems = [
  {
    icon: <EmailIcon style={{ fontSize: '32px', color: 'var(--primary-color)' }} />,
    title: 'Email Analysis',
    description: 'Advanced AI algorithms analyze your emails to identify meeting-related communications with high accuracy.',
  },
  {
    icon: <AssignmentTurnedInIcon style={{ fontSize: '32px', color: 'var(--primary-color)' }} />,
    title: 'Smart Categorization',
    description: 'Automatically categorize emails based on content, priority, and required actions.',
  },
  {
    icon: <ScheduleIcon style={{ fontSize: '32px', color: 'var(--primary-color)' }} />,
    title: 'Meeting Management',
    description: 'Extract meeting details, schedule conflicts, and automatically generate appropriate responses.',
  },
  {
    icon: <SecurityIcon style={{ fontSize: '32px', color: 'var(--primary-color)' }} />,
    title: 'Secure Processing',
    description: 'Enterprise-grade security ensures your email content is processed with the highest privacy standards.',
  },
  {
    icon: <AutorenewIcon style={{ fontSize: '32px', color: 'var(--primary-color)' }} />,
    title: 'Automated Responses',
    description: 'Generate context-aware responses for common meeting requests, saving you time and effort.',
  },
  {
    icon: <AnalyticsIcon style={{ fontSize: '32px', color: 'var(--primary-color)' }} />,
    title: 'Processing Insights',
    description: 'Gain valuable insights into your email traffic, response times, and communication patterns.',
  },
];

const Features = () => {
  return (
    <section id="features" style={{ padding: '100px 0', backgroundColor: 'white' }}>
      <div className="container" style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 1rem' }}>
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
            Powerful Features
          </h2>
          <p style={{ 
            fontSize: '16px', 
            color: 'var(--body-color)', 
            lineHeight: '1.6' 
          }}>
            Sentient Inbox combines advanced AI with intuitive design to revolutionize your email workflow
          </p>
        </motion.div>

        {/* Features Grid */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', 
          gap: '30px' 
        }}>
          {featureItems.map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              style={{
                backgroundColor: 'white',
                borderRadius: '8px',
                padding: '30px',
                boxShadow: '0 5px 15px rgba(0, 0, 0, 0.05)',
                transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                cursor: 'pointer',
              }}
              whileHover={{
                transform: 'translateY(-5px)',
                boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
              }}
            >
              <div style={{ marginBottom: '20px' }}>{item.icon}</div>
              <h3 style={{ 
                fontSize: '20px', 
                fontWeight: '600', 
                marginBottom: '10px', 
                color: 'var(--text-color)' 
              }}>
                {item.title}
              </h3>
              <p style={{ 
                fontSize: '15px', 
                color: 'var(--body-color)', 
                lineHeight: '1.6' 
              }}>
                {item.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;