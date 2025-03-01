import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

// MUI Icons
import StarIcon from '@mui/icons-material/Star';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import InfoIcon from '@mui/icons-material/Info';
import HelpIcon from '@mui/icons-material/Help';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

const getCategoryIcon = (category) => {
  switch (category) {
    case 'meeting':
      return <StarIcon style={{ color: '#F97316' }} />;
    case 'needs_review':
      return <InfoIcon style={{ color: '#F59E0B' }} />;
    case 'not_actionable':
      return <CheckCircleIcon style={{ color: '#10B981' }} />;
    default:
      return <HelpIcon style={{ color: '#6B7280' }} />;
  }
};

const getStatusBadge = (isResponded) => {
  return isResponded ? (
    <span style={{
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      color: '#10B981',
      padding: '4px 8px',
      borderRadius: '4px',
      fontSize: '12px',
      fontWeight: '500',
    }}>
      Responded
    </span>
  ) : (
    <span style={{
      backgroundColor: 'rgba(245, 158, 11, 0.1)',
      color: '#F59E0B',
      padding: '4px 8px',
      borderRadius: '4px',
      fontSize: '12px',
      fontWeight: '500',
    }}>
      Pending
    </span>
  );
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

const EmailList = ({ emails = [], loading = false, error = null }) => {
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <div style={{ color: 'var(--body-color)', fontSize: '16px' }}>Loading emails...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <div style={{ color: 'var(--error-color)', fontSize: '16px' }}>{error}</div>
      </div>
    );
  }

  if (emails.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <div style={{ color: 'var(--body-color)', fontSize: '16px' }}>No emails found</div>
      </div>
    );
  }

  return (
    <div style={{ 
      backgroundColor: 'white', 
      borderRadius: '8px',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
      overflow: 'hidden',
    }}>
      {emails.map((email, index) => (
        <motion.div
          key={email.message_id}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: index * 0.05 }}
        >
          <Link
            to={`/emails/${email.message_id}`}
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '16px',
              borderBottom: index === emails.length - 1 ? 'none' : '1px solid var(--border-color)',
              textDecoration: 'none',
              color: 'inherit',
              transition: 'background-color 0.2s ease',
            }}
            className="hover:bg-gray-50"
          >
            <div style={{ marginRight: '16px' }}>
              {getCategoryIcon(email.category)}
            </div>
            
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                marginBottom: '4px'
              }}>
                <h3 style={{ 
                  fontSize: '15px',
                  fontWeight: '600',
                  color: 'var(--text-color)',
                  margin: 0,
                  textOverflow: 'ellipsis',
                  overflow: 'hidden',
                  whiteSpace: 'nowrap',
                  maxWidth: '70%',
                }}>
                  {email.subject || '(No subject)'}
                </h3>
                <div style={{ fontSize: '14px', color: 'var(--body-color)' }}>
                  {formatDate(email.received_at)}
                </div>
              </div>
              
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <span style={{ 
                  fontSize: '14px',
                  color: 'var(--body-color)',
                  textOverflow: 'ellipsis',
                  overflow: 'hidden',
                  whiteSpace: 'nowrap',
                }}>
                  {email.sender}
                </span>
                {getStatusBadge(email.is_responded)}
              </div>
            </div>
            
            <div style={{ marginLeft: '16px' }}>
              <ArrowForwardIcon style={{ color: 'var(--body-color)', fontSize: '18px' }} />
            </div>
          </Link>
        </motion.div>
      ))}
    </div>
  );
};

export default EmailList;