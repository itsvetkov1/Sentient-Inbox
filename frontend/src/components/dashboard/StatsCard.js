import React from 'react';
import { motion } from 'framer-motion';

// Icons for different stats
import EmailIcon from '@mui/icons-material/Email';
import ScheduleIcon from '@mui/icons-material/Schedule';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import SpeedIcon from '@mui/icons-material/Speed';

const getIconForStat = (type) => {
  switch (type) {
    case 'total':
      return <EmailIcon style={{ fontSize: '30px', color: 'var(--primary-color)' }} />;
    case 'meetings':
      return <ScheduleIcon style={{ fontSize: '30px', color: '#F97316' }} />;
    case 'success':
      return <CheckCircleIcon style={{ fontSize: '30px', color: '#10B981' }} />;
    case 'speed':
      return <SpeedIcon style={{ fontSize: '30px', color: '#8B5CF6' }} />;
    default:
      return <EmailIcon style={{ fontSize: '30px', color: 'var(--primary-color)' }} />;
  }
};

const StatsCard = ({ title, value, change, type }) => {
  // Determine if change is positive or negative
  const isPositive = change > 0;
  const changeColor = isPositive ? '#10B981' : '#EF4444';
  const changePrefix = isPositive ? '+' : '';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      style={{
        backgroundColor: 'white',
        borderRadius: '10px',
        padding: '24px',
        boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h3 style={{ 
            fontSize: '14px', 
            color: 'var(--body-color)', 
            fontWeight: '500',
            marginBottom: '12px',
            margin: 0
          }}>
            {title}
          </h3>
          <div style={{ 
            fontSize: '24px', 
            fontWeight: '700',
            color: 'var(--text-color)',
            marginTop: '8px'
          }}>
            {value}
          </div>
          
          {change !== undefined && (
            <div style={{ 
              fontSize: '13px',
              marginTop: '8px',
              color: changeColor,
              display: 'flex',
              alignItems: 'center',
            }}>
              {changePrefix}{change}% from last period
            </div>
          )}
        </div>
        
        <div style={{
          backgroundColor: type === 'meetings' ? 'rgba(249, 115, 22, 0.1)' : 
                        type === 'success' ? 'rgba(16, 185, 129, 0.1)' :
                        type === 'speed' ? 'rgba(139, 92, 246, 0.1)' :
                        'rgba(74, 108, 247, 0.1)', 
          borderRadius: '8px',
          width: '50px',
          height: '50px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          {getIconForStat(type)}
        </div>
      </div>
    </motion.div>
  );
};

export default StatsCard;