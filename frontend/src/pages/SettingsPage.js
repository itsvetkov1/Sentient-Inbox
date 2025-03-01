import React, { useState } from 'react';
import { motion } from 'framer-motion';
import DashboardLayout from '../components/dashboard/DashboardLayout';

const SettingsPage = () => {
  const [settings, setSettings] = useState({
    emailProcessingEnabled: true,
    processingFrequency: '15',
    batchSize: '50',
    autoRespond: true,
    notificationsEnabled: true,
    emailAddress: 'user@example.com',
    name: 'John Doe',
  });
  
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      setSuccess(false);
      
      // In a real app, you would send settings to API
      // await emailService.updateSettings(settings);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccess(true);
      setLoading(false);
    } catch (err) {
      console.error('Error updating settings:', err);
      setError('Failed to update settings. Please try again.');
      setLoading(false);
    }
  };
  
  return (
    <DashboardLayout>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <header style={{ marginBottom: '24px' }}>
          <h1 style={{ 
            fontSize: '24px', 
            fontWeight: '700', 
            color: 'var(--text-color)',
            marginBottom: '8px'
          }}>
            Settings
          </h1>
          <p style={{ fontSize: '15px', color: 'var(--body-color)' }}>
            Configure your email processing preferences
          </p>
        </header>
        
        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            style={{
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              borderRadius: '6px',
              padding: '12px 16px',
              marginBottom: '24px',
              color: '#10B981',
              fontSize: '14px',
            }}
          >
            Settings saved successfully!
          </motion.div>
        )}
        
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            style={{
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              borderRadius: '6px',
              padding: '12px 16px',
              marginBottom: '24px',
              color: '#EF4444',
              fontSize: '14px',
            }}
          >
            {error}
          </motion.div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div style={{ 
            backgroundColor: 'white', 
            borderRadius: '10px',
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
            padding: '24px',
            marginBottom: '24px',
          }}>
            <h2 style={{ 
              fontSize: '18px',
              fontWeight: '600',
              color: 'var(--text-color)',
              marginBottom: '20px',
            }}>
              Email Processing
            </h2>
            
            <div style={{ marginBottom: '20px' }}>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '16px',
              }}>
                <div>
                  <label 
                    htmlFor="emailProcessingEnabled" 
                    style={{ 
                      fontWeight: '500',
                      color: 'var(--text-color)', 
                      display: 'block',
                      marginBottom: '4px',
                    }}
                  >
                    Enable Email Processing
                  </label>
                  <div style={{ fontSize: '14px', color: 'var(--body-color)' }}>
                    Automatically process and categorize incoming emails
                  </div>
                </div>
                <label className="switch" style={{ position: 'relative', display: 'inline-block', width: '50px', height: '24px' }}>
                  <input
                    type="checkbox"
                    id="emailProcessingEnabled"
                    name="emailProcessingEnabled"
                    checked={settings.emailProcessingEnabled}
                    onChange={handleChange}
                    style={{ opacity: 0, width: 0, height: 0 }}
                  />
                  <span style={{
                    position: 'absolute',
                    cursor: 'pointer',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: settings.emailProcessingEnabled ? 'var(--primary-color)' : '#ccc',
                    borderRadius: '34px',
                    transition: '0.4s',
                    '&:before': {
                      position: 'absolute',
                      content: '""',
                      height: '16px',
                      width: '16px',
                      left: '4px',
                      bottom: '4px',
                      backgroundColor: 'white',
                      borderRadius: '50%',
                      transition: '0.4s',
                      transform: settings.emailProcessingEnabled ? 'translateX(26px)' : 'translateX(0)',
                    }
                  }}>
                    <div style={{
                      position: 'absolute',
                      height: '16px',
                      width: '16px',
                      left: '4px',
                      bottom: '4px',
                      backgroundColor: 'white',
                      borderRadius: '50%',
                      transition: '0.4s',
                      transform: settings.emailProcessingEnabled ? 'translateX(26px)' : 'translateX(0)',
                    }} />
                  </span>
                </label>
              </div>
              
              <div style={{ 
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '16px',
                marginBottom: '16px',
              }}>
                <div>
                  <label 
                    htmlFor="processingFrequency" 
                    style={{ 
                      fontWeight: '500',
                      color: 'var(--text-color)', 
                      display: 'block',
                      marginBottom: '8px',
                      fontSize: '14px',
                    }}
                  >
                    Processing Frequency (minutes)
                  </label>
                  <input
                    type="number"
                    id="processingFrequency"
                    name="processingFrequency"
                    value={settings.processingFrequency}
                    onChange={handleChange}
                    min="5"
                    max="60"
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '1.5px solid var(--border-color)',
                      borderRadius: '6px',
                      fontSize: '14px',
                    }}
                  />
                </div>
                
                <div>
                  <label 
                    htmlFor="batchSize" 
                    style={{ 
                      fontWeight: '500',
                      color: 'var(--text-color)', 
                      display: 'block',
                      marginBottom: '8px',
                      fontSize: '14px',
                    }}
                  >
                    Batch Size
                  </label>
                  <input
                    type="number"
                    id="batchSize"
                    name="batchSize"
                    value={settings.batchSize}
                    onChange={handleChange}
                    min="10"
                    max="100"
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '1.5px solid var(--border-color)',
                      borderRadius: '6px',
                      fontSize: '14px',
                    }}
                  />
                </div>
              </div>
              
              <div style={{ 
                display: 'flex', 
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '16px',
              }}>
                <div>
                  <label 
                    htmlFor="autoRespond" 
                    style={{ 
                      fontWeight: '500',
                      color: 'var(--text-color)', 
                      display: 'block',
                      marginBottom: '4px',
                    }}
                  >
                    Auto-Respond to Meetings
                  </label>
                  <div style={{ fontSize: '14px', color: 'var(--body-color)' }}>
                    Automatically respond to meeting invitations
                  </div>
                </div>
                <label className="switch" style={{ position: 'relative', display: 'inline-block', width: '50px', height: '24px' }}>
                  <input
                    type="checkbox"
                    id="autoRespond"
                    name="autoRespond"
                    checked={settings.autoRespond}
                    onChange={handleChange}
                    style={{ opacity: 0, width: 0, height: 0 }}
                  />
                  <span style={{
                    position: 'absolute',
                    cursor: 'pointer',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: settings.autoRespond ? 'var(--primary-color)' : '#ccc',
                    borderRadius: '34px',
                    transition: '0.4s',
                  }}>
                    <div style={{
                      position: 'absolute',
                      height: '16px',
                      width: '16px',
                      left: '4px',
                      bottom: '4px',
                      backgroundColor: 'white',
                      borderRadius: '50%',
                      transition: '0.4s',
                      transform: settings.autoRespond ? 'translateX(26px)' : 'translateX(0)',
                    }} />
                  </span>
                </label>
              </div>
              
              <div style={{ 
                display: 'flex', 
                alignItems: 'center',
                justifyContent: 'space-between',
              }}>
                <div>
                  <label 
                    htmlFor="notificationsEnabled" 
                    style={{ 
                      fontWeight: '500',
                      color: 'var(--text-color)', 
                      display: 'block',
                      marginBottom: '4px',
                    }}
                  >
                    Email Notifications
                  </label>
                  <div style={{ fontSize: '14px', color: 'var(--body-color)' }}>
                    Receive notifications for processed emails
                  </div>
                </div>
                <label className="switch" style={{ position: 'relative', display: 'inline-block', width: '50px', height: '24px' }}>
                  <input
                    type="checkbox"
                    id="notificationsEnabled"
                    name="notificationsEnabled"
                    checked={settings.notificationsEnabled}
                    onChange={handleChange}
                    style={{ opacity: 0, width: 0, height: 0 }}
                  />
                  <span style={{
                    position: 'absolute',
                    cursor: 'pointer',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: settings.notificationsEnabled ? 'var(--primary-color)' : '#ccc',
                    borderRadius: '34px',
                    transition: '0.4s',
                  }}>
                    <div style={{
                      position: 'absolute',
                      height: '16px',
                      width: '16px',
                      left: '4px',
                      bottom: '4px',
                      backgroundColor: 'white',
                      borderRadius: '50%',
                      transition: '0.4s',
                      transform: settings.notificationsEnabled ? 'translateX(26px)' : 'translateX(0)',
                    }} />
                  </span>
                </label>
              </div>
            </div>
          </div>
          
          <div style={{ 
            backgroundColor: 'white', 
            borderRadius: '10px',
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
            padding: '24px',
            marginBottom: '24px',
          }}>
            <h2 style={{ 
              fontSize: '18px',
              fontWeight: '600',
              color: 'var(--text-color)',
              marginBottom: '20px',
            }}>
              Account Information
            </h2>
            
            <div style={{ marginBottom: '20px' }}>
              <div style={{ 
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '16px',
              }}>
                <div>
                  <label 
                    htmlFor="name" 
                    style={{ 
                      fontWeight: '500',
                      color: 'var(--text-color)', 
                      display: 'block',
                      marginBottom: '8px',
                      fontSize: '14px',
                    }}
                  >
                    Full Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={settings.name}
                    onChange={handleChange}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '1.5px solid var(--border-color)',
                      borderRadius: '6px',
                      fontSize: '14px',
                    }}
                  />
                </div>
                
                <div>
                  <label 
                    htmlFor="emailAddress" 
                    style={{ 
                      fontWeight: '500',
                      color: 'var(--text-color)', 
                      display: 'block',
                      marginBottom: '8px',
                      fontSize: '14px',
                    }}
                  >
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="emailAddress"
                    name="emailAddress"
                    value={settings.emailAddress}
                    onChange={handleChange}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '1.5px solid var(--border-color)',
                      borderRadius: '6px',
                      fontSize: '14px',
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              type="submit"
              disabled={loading}
              style={{
                backgroundColor: 'var(--primary-color)',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                padding: '12px 24px',
                fontSize: '15px',
                fontWeight: '500',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1,
                transition: 'all 0.3s ease',
              }}
            >
              {loading ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
};

export default SettingsPage;