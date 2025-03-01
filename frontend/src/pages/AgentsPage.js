import React, { useState } from 'react';
import { motion } from 'framer-motion';
import DashboardLayout from '../components/dashboard/DashboardLayout';

// MUI Icons
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PsychologyIcon from '@mui/icons-material/Psychology';
import SchoolIcon from '@mui/icons-material/School';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import MeetingRoomIcon from '@mui/icons-material/MeetingRoom';
import SupervisedUserCircleIcon from '@mui/icons-material/SupervisedUserCircle';
import AlarmIcon from '@mui/icons-material/Alarm';
import LanguageIcon from '@mui/icons-material/Language';
import InfoIcon from '@mui/icons-material/Info';
import AddIcon from '@mui/icons-material/Add';
import MailOutlineIcon from '@mui/icons-material/MailOutline';
import EmailIcon from '@mui/icons-material/Email';
import SettingsIcon from '@mui/icons-material/Settings';
import GoogleIcon from '@mui/icons-material/Google';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CloseIcon from '@mui/icons-material/Close';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

const AgentsPage = () => {
  // AI Agents data
  // Email accounts data
  const [emailAccounts, setEmailAccounts] = useState([
    {
      id: 'account1',
      email: 'user@example.com',
      provider: 'gmail',
      authenticated: true,
      isActive: true
    }
  ]);
  
  const [showAddEmailModal, setShowAddEmailModal] = useState(false);
  const [newEmail, setNewEmail] = useState('');
  const [selectedEmailId, setSelectedEmailId] = useState('account1');
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  
  // AI Agents data
  const [agents, setAgents] = useState([
    {
      id: 'meeting-agent',
      name: 'Meeting Agent',
      description: 'Specialized agent for handling meeting requests and scheduling.',
      icon: <MeetingRoomIcon />,
      enabled: true,
      active: true,
      status: 'active',
      canToggle: true,
    },
    // Coming soon agents
    {
      id: 'calendar-agent',
      name: 'Calendar Agent',
      description: 'Manages calendar integration for scheduling and availability checks.',
      icon: <AlarmIcon />,
      enabled: false,
      active: false,
      status: 'coming_soon',
    },
    {
      id: 'general-support',
      name: 'General Support Agent',
      description: 'Stores basic information for topics and answers questions based on it.',
      icon: <SupervisedUserCircleIcon />,
      enabled: false,
      active: false,
      status: 'coming_soon',
    },
    {
      id: 'custom-agent',
      name: 'Customized Agent',
      description: 'Adapts to specific needs and workflow requirements for your organization.',
      icon: <LanguageIcon />,
      enabled: false,
      active: false,
      status: 'coming_soon',
    },
  ]);

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  // Handle adding a new email account
  const handleAddEmail = async () => {
    if (!newEmail || !newEmail.includes('@')) {
      setError('Please enter a valid email address');
      return;
    }
    
    setLoading(true);
    setError(null);
    setSuccess(false);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Add new email (but not authenticated yet)
      const newAccount = {
        id: `account${emailAccounts.length + 1}`,
        email: newEmail,
        provider: newEmail.endsWith('gmail.com') ? 'gmail' : 'other',
        authenticated: false,
        isActive: false
      };
      
      setEmailAccounts([...emailAccounts, newAccount]);
      setNewEmail('');
      setShowAddEmailModal(false);
      setSuccess(true);
      setLoading(false);
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Error adding email:', err);
      setError('Failed to add email. Please try again.');
      setLoading(false);
    }
  };
  
  // Handle authenticating an email account
  const handleAuthenticate = async (accountId) => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update email account to authenticated
      const updatedAccounts = emailAccounts.map(account => {
        if (account.id === accountId) {
          return { ...account, authenticated: true };
        }
        return account;
      });
      
      setEmailAccounts(updatedAccounts);
      setSuccess(true);
      setLoading(false);
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Error authenticating email:', err);
      setError('Failed to authenticate email. Please try again.');
      setLoading(false);
    }
  };
  
  // Handle activating/deactivating an email account
  const handleToggleActive = async (accountId) => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Toggle active status
      const updatedAccounts = emailAccounts.map(account => {
        if (account.id === accountId) {
          return { ...account, isActive: !account.isActive };
        }
        return account;
      });
      
      setEmailAccounts(updatedAccounts);
      setSuccess(true);
      setLoading(false);
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Error toggling email status:', err);
      setError('Failed to update email status. Please try again.');
      setLoading(false);
    }
  };
  
  // Handle selecting an email account to view advanced settings
  const handleSelectEmail = (accountId) => {
    setSelectedEmailId(accountId);
    setShowAdvancedSettings(true);
  };
  
  // Handle toggle for AI agent within advanced settings
  const handleAgentToggle = async (agentId) => {
    // Don't allow toggling for coming soon agents or agents that can't be toggled
    const agentIndex = agents.findIndex(agent => agent.id === agentId);
    if (agents[agentIndex].status === 'coming_soon' || !agents[agentIndex].canToggle) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 800));

      // Update agent state
      const updatedAgents = [...agents];
      updatedAgents[agentIndex].enabled = !updatedAgents[agentIndex].enabled;
      setAgents(updatedAgents);

      setSuccess(true);
      setLoading(false);

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Error toggling agent:', err);
      setError('Failed to update agent status. Please try again.');
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <header style={{ marginBottom: '24px' }}>
          <h1 style={{ 
            fontSize: '24px', 
            fontWeight: '700', 
            color: 'var(--text-color)',
            marginBottom: '8px'
          }}>
            AI Agents
          </h1>
          <p style={{ fontSize: '15px', color: 'var(--body-color)' }}>
            Manage the AI agents that process and respond to your emails
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
            {success === true ? 'Operation completed successfully!' : success}
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

        {/* Email Accounts Section */}
        {!showAdvancedSettings && (
          <section style={{ marginBottom: '40px' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '16px',
            }}>
              <h2 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: 'var(--text-color)',
                margin: 0,
              }}>
                Email Accounts
              </h2>
              
              <button
                onClick={() => setShowAddEmailModal(true)}
                style={{
                  backgroundColor: 'var(--primary-color)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '8px 12px',
                  fontSize: '14px',
                  fontWeight: '500',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  cursor: 'pointer',
                }}
              >
                <AddIcon style={{ fontSize: '18px' }} />
                Add Email
              </button>
            </div>
            
            <div style={{
              backgroundColor: 'white',
              borderRadius: '10px',
              boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
              overflow: 'hidden',
            }}>
              {emailAccounts.map((account, index) => (
                <motion.div
                  key={account.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  style={{
                    padding: '16px 20px',
                    borderBottom: index === emailAccounts.length - 1 ? 'none' : '1px solid var(--border-color)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                      width: '40px',
                      height: '40px',
                      borderRadius: '8px',
                      backgroundColor: account.provider === 'gmail' ? 'rgba(234, 67, 53, 0.1)' : 'rgba(74, 108, 247, 0.1)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}>
                      {account.provider === 'gmail' ? (
                        <GoogleIcon style={{ color: '#EA4335', fontSize: '20px' }} />
                      ) : (
                        <MailOutlineIcon style={{ color: 'var(--primary-color)', fontSize: '20px' }} />
                      )}
                    </div>
                    
                    <div>
                      <div style={{ fontWeight: '500', color: 'var(--text-color)', fontSize: '15px' }}>
                        {account.email}
                      </div>
                      <div style={{ fontSize: '13px', color: 'var(--body-color)' }}>
                        {account.authenticated ? 'Authenticated' : 'Not authenticated'}
                      </div>
                    </div>
                  </div>
                  
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {/* Authentication status indicator/button */}
                    {account.authenticated ? (
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        color: '#10B981',
                        fontSize: '14px',
                        gap: '4px',
                      }}>
                        <CheckCircleIcon style={{ fontSize: '18px' }} />
                        <span>Verified</span>
                      </div>
                    ) : (
                      <button
                        onClick={() => handleAuthenticate(account.id)}
                        disabled={loading}
                        style={{
                          backgroundColor: 'rgba(79, 70, 229, 0.1)',
                          color: '#4F46E5',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '6px 12px',
                          fontSize: '14px',
                          fontWeight: '500',
                          cursor: loading ? 'not-allowed' : 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                        }}
                      >
                        <GoogleIcon style={{ fontSize: '16px' }} />
                        Authenticate
                      </button>
                    )}
                    
                    {/* Toggle active status */}
                    {account.authenticated && (
                      <label className="switch" style={{ position: 'relative', display: 'inline-block', width: '40px', height: '20px' }}>
                        <input
                          type="checkbox"
                          checked={account.isActive}
                          onChange={() => handleToggleActive(account.id)}
                          disabled={loading || !account.authenticated}
                          style={{ opacity: 0, width: 0, height: 0 }}
                        />
                        <span style={{
                          position: 'absolute',
                          cursor: !account.authenticated ? 'not-allowed' : 'pointer',
                          top: 0,
                          left: 0,
                          right: 0,
                          bottom: 0,
                          backgroundColor: account.isActive ? 'var(--primary-color)' : '#ccc',
                          borderRadius: '34px',
                          transition: '0.3s',
                        }}>
                          <div style={{
                            position: 'absolute',
                            height: '14px',
                            width: '14px',
                            left: '3px',
                            bottom: '3px',
                            backgroundColor: 'white',
                            borderRadius: '50%',
                            transition: '0.3s',
                            transform: account.isActive ? 'translateX(20px)' : 'translateX(0)',
                          }} />
                        </span>
                      </label>
                    )}
                    
                    {/* Advanced settings button */}
                    {account.authenticated && (
                      <button
                        onClick={() => handleSelectEmail(account.id)}
                        style={{
                          backgroundColor: 'transparent',
                          color: 'var(--body-color)',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '6px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <SettingsIcon style={{ fontSize: '18px' }} />
                      </button>
                    )}
                  </div>
                </motion.div>
              ))}
              
              {emailAccounts.length === 0 && (
                <div style={{
                  padding: '40px 20px',
                  textAlign: 'center',
                  color: 'var(--body-color)',
                }}>
                  No email accounts added yet. Click "Add Email" to get started.
                </div>
              )}
            </div>
          </section>
        )}
        
        {/* Add Email Modal */}
        {showAddEmailModal && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}>
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              style={{
                backgroundColor: 'white',
                borderRadius: '10px',
                width: '100%',
                maxWidth: '400px',
                padding: '24px',
                boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
              }}
            >
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '20px',
              }}>
                <h3 style={{
                  fontSize: '18px',
                  fontWeight: '600',
                  color: 'var(--text-color)',
                  margin: 0,
                }}>
                  Add Email Account
                </h3>
                <button
                  onClick={() => setShowAddEmailModal(false)}
                  style={{
                    backgroundColor: 'transparent',
                    border: 'none',
                    color: 'var(--body-color)',
                    cursor: 'pointer',
                    padding: '4px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <CloseIcon />
                </button>
              </div>
              
              <div style={{ marginBottom: '20px' }}>
                <label 
                  htmlFor="email" 
                  style={{ 
                    display: 'block',
                    marginBottom: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: 'var(--text-color)'
                  }}
                >
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  placeholder="Enter your email address"
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    border: '1.5px solid var(--border-color)',
                    borderRadius: '6px',
                    fontSize: '14px',
                  }}
                />
              </div>
              
              <div style={{
                display: 'flex',
                justifyContent: 'flex-end',
                gap: '12px',
              }}>
                <button
                  onClick={() => setShowAddEmailModal(false)}
                  style={{
                    backgroundColor: 'transparent',
                    color: 'var(--body-color)',
                    border: '1.5px solid var(--border-color)',
                    borderRadius: '6px',
                    padding: '10px 16px',
                    fontSize: '14px',
                    fontWeight: '500',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddEmail}
                  disabled={loading || !newEmail}
                  style={{
                    backgroundColor: 'var(--primary-color)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '10px 16px',
                    fontSize: '14px',
                    fontWeight: '500',
                    cursor: (!newEmail || loading) ? 'not-allowed' : 'pointer',
                    opacity: (!newEmail || loading) ? 0.7 : 1,
                  }}
                >
                  {loading ? 'Adding...' : 'Add Email'}
                </button>
              </div>
            </motion.div>
          </div>
        )}

        {/* Advanced Settings Section */}
        {showAdvancedSettings && (
          <>
            {/* Back button */}
            <div style={{ marginBottom: '24px' }}>
              <button
                onClick={() => setShowAdvancedSettings(false)}
                style={{
                  backgroundColor: 'transparent',
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  color: 'var(--body-color)',
                  padding: '8px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                <ArrowBackIcon style={{ fontSize: '18px' }} />
                Back to Email Accounts
              </button>
            </div>
            
            {/* Email Account Header */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '10px',
              padding: '20px',
              boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
              marginBottom: '24px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '8px',
                  backgroundColor: emailAccounts.find(a => a.id === selectedEmailId)?.provider === 'gmail' ? 
                    'rgba(234, 67, 53, 0.1)' : 'rgba(74, 108, 247, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  {emailAccounts.find(a => a.id === selectedEmailId)?.provider === 'gmail' ? (
                    <GoogleIcon style={{ color: '#EA4335', fontSize: '20px' }} />
                  ) : (
                    <MailOutlineIcon style={{ color: 'var(--primary-color)', fontSize: '20px' }} />
                  )}
                </div>
                
                <div>
                  <div style={{ fontWeight: '600', color: 'var(--text-color)', fontSize: '16px' }}>
                    {emailAccounts.find(a => a.id === selectedEmailId)?.email}
                  </div>
                  <div style={{ 
                    fontSize: '13px', 
                    color: emailAccounts.find(a => a.id === selectedEmailId)?.isActive ? '#10B981' : '#9CA3AF',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}>
                    {emailAccounts.find(a => a.id === selectedEmailId)?.isActive ? (
                      <>
                        <span style={{ display: 'flex', alignItems: 'center' }}>
                          <CheckCircleIcon style={{ fontSize: '14px' }} />
                        </span>
                        <span>Active</span>
                      </>
                    ) : 'Inactive'}
                  </div>
                </div>
              </div>
              
              <div>
                <button
                  onClick={() => handleToggleActive(selectedEmailId)}
                  style={{
                    backgroundColor: emailAccounts.find(a => a.id === selectedEmailId)?.isActive ? 
                      'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                    color: emailAccounts.find(a => a.id === selectedEmailId)?.isActive ? 
                      '#EF4444' : '#10B981',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '8px 16px',
                    fontSize: '14px',
                    fontWeight: '500',
                    cursor: 'pointer',
                  }}
                >
                  {emailAccounts.find(a => a.id === selectedEmailId)?.isActive ? 'Deactivate' : 'Activate'}
                </button>
              </div>
            </div>
            
            {/* AI Agents Section */}
            <section style={{ marginBottom: '40px' }}>
              <h2 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: 'var(--text-color)',
                marginBottom: '16px',
              }}>
                Configured Agents
              </h2>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                gap: '20px',
              }}>
                {agents
                  .filter(agent => agent.status === 'active')
                  .map((agent, index) => (
                    <motion.div
                      key={agent.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4, delay: index * 0.1 }}
                      style={{
                        backgroundColor: 'white',
                        borderRadius: '10px',
                        padding: '24px',
                        boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
                        position: 'relative',
                      }}
                    >
                      <div style={{
                        position: 'absolute',
                        top: '20px',
                        right: '20px',
                      }}>
                        <label className="switch" style={{ position: 'relative', display: 'inline-block', width: '50px', height: '24px' }}>
                          <input
                            type="checkbox"
                            checked={agent.enabled}
                            onChange={() => handleAgentToggle(agent.id)}
                            disabled={loading || agent.status === 'coming_soon' || !agent.canToggle}
                            style={{ opacity: 0, width: 0, height: 0 }}
                          />
                          <span style={{
                            position: 'absolute',
                            cursor: (agent.status === 'coming_soon' || !agent.canToggle) ? 'not-allowed' : 'pointer',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            backgroundColor: agent.enabled ? 'var(--primary-color)' : '#ccc',
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
                              transform: agent.enabled ? 'translateX(26px)' : 'translateX(0)',
                            }} />
                          </span>
                        </label>
                      </div>

                      <div style={{
                        width: '48px',
                        height: '48px',
                        borderRadius: '10px',
                        backgroundColor: 'rgba(74, 108, 247, 0.1)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        marginBottom: '16px',
                      }}>
                        <div style={{ color: 'var(--primary-color)', fontSize: '28px' }}>
                          {agent.icon}
                        </div>
                      </div>

                      <h3 style={{
                        fontSize: '16px',
                        fontWeight: '600',
                        color: 'var(--text-color)',
                        marginBottom: '8px',
                      }}>
                        {agent.name}
                      </h3>

                      <p style={{
                        fontSize: '14px',
                        color: 'var(--body-color)',
                        lineHeight: '1.5',
                        marginBottom: '16px',
                      }}>
                        {agent.description}
                      </p>

                      <div style={{
                        fontSize: '13px',
                        color: agent.enabled ? '#10B981' : '#9CA3AF',
                        fontWeight: '500',
                      }}>
                        {agent.enabled ? 'Enabled' : 'Disabled'}
                      </div>
                    </motion.div>
                  ))}
              </div>
            </section>
            
            {/* Info Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.4 }}
              style={{
                backgroundColor: 'rgba(74, 108, 247, 0.05)',
                borderRadius: '10px',
                padding: '20px',
                marginTop: '40px',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '16px',
              }}
            >
              <div style={{ 
                color: 'var(--primary-color)', 
                display: 'flex', 
                marginTop: '2px' 
              }}>
                <InfoIcon />
              </div>
              <div>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: 'var(--text-color)',
                  marginBottom: '8px',
                }}>
                  About Advanced Settings
                </h3>
                <p style={{
                  fontSize: '14px',
                  color: 'var(--body-color)',
                  lineHeight: '1.6',
                  margin: 0,
                }}>
                  Configure which AI agents should process emails from this account. Currently, 
                  you can enable or disable the Meeting Agent. Additional agents will be available 
                  in future updates to enhance your email management experience.
                </p>
              </div>
            </motion.div>
          </>
        )}
        
        {/* Coming Soon Agents Section - Only show on main screen */}
        {!showAdvancedSettings && (
          <section>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              marginBottom: '16px',
              gap: '8px'
            }}>
              <h2 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: 'var(--text-color)',
                margin: 0,
              }}>
                Coming Soon
              </h2>
              <span style={{
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                color: '#4F46E5',
                fontSize: '12px',
                fontWeight: '500',
                padding: '4px 8px',
                borderRadius: '6px',
              }}>
                In Development
              </span>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
              gap: '20px',
            }}>
              {agents
                .filter(agent => agent.status === 'coming_soon')
                .map((agent, index) => (
                  <motion.div
                    key={agent.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    style={{
                      backgroundColor: 'white',
                      borderRadius: '10px',
                      padding: '24px',
                      boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
                      position: 'relative',
                      opacity: 0.7,
                    }}
                  >
                    <div style={{
                      position: 'absolute',
                      top: '20px',
                      right: '20px',
                    }}>
                      <label className="switch" style={{ position: 'relative', display: 'inline-block', width: '50px', height: '24px' }}>
                        <input
                          type="checkbox"
                          checked={false}
                          disabled={true}
                          style={{ opacity: 0, width: 0, height: 0 }}
                        />
                        <span style={{
                          position: 'absolute',
                          cursor: 'not-allowed',
                          top: 0,
                          left: 0,
                          right: 0,
                          bottom: 0,
                          backgroundColor: '#ccc',
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
                          }} />
                        </span>
                      </label>
                    </div>

                    <div style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '10px',
                      backgroundColor: 'rgba(156, 163, 175, 0.1)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      marginBottom: '16px',
                    }}>
                      <div style={{ color: '#9CA3AF', fontSize: '28px' }}>
                        {agent.icon}
                      </div>
                    </div>

                    <h3 style={{
                      fontSize: '16px',
                      fontWeight: '600',
                      color: 'var(--text-color)',
                      marginBottom: '8px',
                    }}>
                      {agent.name}
                    </h3>

                    <p style={{
                      fontSize: '14px',
                      color: 'var(--body-color)',
                      lineHeight: '1.5',
                      marginBottom: '16px',
                    }}>
                      {agent.description}
                    </p>

                    <div style={{
                      fontSize: '13px',
                      color: '#9CA3AF',
                      fontWeight: '500',
                    }}>
                      Coming Soon
                    </div>
                  </motion.div>
                ))}
            </div>
          </section>
        )}

        {/* Info Section - Only show on main screen */}
        {!showAdvancedSettings && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.4 }}
            style={{
              backgroundColor: 'rgba(74, 108, 247, 0.05)',
              borderRadius: '10px',
              padding: '20px',
              marginTop: '40px',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '16px',
            }}
          >
            <div style={{ 
              color: 'var(--primary-color)', 
              display: 'flex', 
              marginTop: '2px' 
            }}>
              <InfoIcon />
            </div>
            <div>
              <h3 style={{
                fontSize: '16px',
                fontWeight: '600',
                color: 'var(--text-color)',
                marginBottom: '8px',
              }}>
                About AI Agents
              </h3>
              <p style={{
                fontSize: '14px',
                color: 'var(--body-color)',
                lineHeight: '1.6',
                margin: 0,
              }}>
                AI Agents help automate your email workflow by handling specific tasks. Currently, you can enable or disable 
                the Meeting Agent which manages meeting-related emails. More specialized agents are under development 
                and will be available soon to further enhance your email management experience.
              </p>
            </div>
          </motion.div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default AgentsPage;