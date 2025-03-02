import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import DashboardLayout from '../components/dashboard/DashboardLayout';

// MUI Icons
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import InfoIcon from '@mui/icons-material/Info';
import HelpIcon from '@mui/icons-material/Help';
import StarIcon from '@mui/icons-material/Star';
import PersonIcon from '@mui/icons-material/Person';
import EventIcon from '@mui/icons-material/Event';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import EventNoteIcon from '@mui/icons-material/EventNote';
import GroupIcon from '@mui/icons-material/Group';

// Mock emails data for demonstration
const mockEmailDetails = {
  msg1: {
    message_id: 'msg1',
    subject: 'Weekly Team Meeting - Planning Session',
    sender: 'john.smith@company.com',
    received_at: '2023-10-15T14:30:00Z',
    category: 'meeting',
    is_responded: true,
    content: {
      raw_content: "Hello team,\n\nI'd like to schedule our weekly planning meeting for next Tuesday at 10 AM in Conference Room A.\n\nPlease come prepared to discuss your progress on current projects and objectives for the upcoming sprint.\n\nLet me know if you have any conflicts.\n\nRegards,\nJohn Smith\nProject Manager",
      processed_content: "Hello team,\n\nI'd like to schedule our weekly planning meeting for next Tuesday at 10 AM in Conference Room A.\n\nPlease come prepared to discuss your progress on current projects and objectives for the upcoming sprint.\n\nLet me know if you have any conflicts.\n\nRegards,\nJohn Smith\nProject Manager",
    },
    analysis_results: {
      final_category: "meeting",
      meeting_details: {
        date: "next Tuesday",
        time: "10 AM",
        location: "Conference Room A",
        agenda: "discuss progress on current projects and objectives for the upcoming sprint",
        participants: ["team"],
        missing_elements: []
      },
      suggested_response: "Hi John,\n\nThanks for organizing the weekly planning meeting. I can confirm my attendance on Tuesday at 10 AM in Conference Room A.\n\nI'll prepare updates on my current projects and objectives for discussion.\n\nBest regards,\n[Your Name]",
      confidence_score: 0.92,
      processing_time_ms: 235
    }
  },
  msg2: {
    message_id: 'msg2',
    subject: 'Project Update Required',
    sender: 'project-manager@company.com',
    received_at: '2023-10-15T10:15:00Z',
    category: 'needs_review',
    is_responded: false,
    content: {
      raw_content: "Hi,\n\nI need an update on the current status of the dashboard project. Please provide details on:\n\n- Current completion percentage\n- Any blockers or challenges\n- Expected completion date\n\nThis information is needed for the executive review tomorrow.\n\nThanks,\nProject Management Team",
      processed_content: "Hi,\n\nI need an update on the current status of the dashboard project. Please provide details on:\n\n- Current completion percentage\n- Any blockers or challenges\n- Expected completion date\n\nThis information is needed for the executive review tomorrow.\n\nThanks,\nProject Management Team",
    },
    analysis_results: {
      final_category: "needs_review",
      confidence_score: 0.85,
      processing_time_ms: 210
    }
  }
};

const EmailDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [email, setEmail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchEmailDetails = async () => {
      try {
        setLoading(true);
        
        // In a real app, you would fetch from API
        // const response = await emailService.getEmailById(id);
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Get mock email detail by ID
        const emailDetail = mockEmailDetails[id];
        
        if (!emailDetail) {
          setError('Email not found');
          setLoading(false);
          return;
        }
        
        setEmail(emailDetail);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching email details:', err);
        setError('Failed to load email details. Please try again.');
        setLoading(false);
      }
    };
    
    fetchEmailDetails();
  }, [id]);
  
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
        padding: '6px 10px',
        borderRadius: '4px',
        fontSize: '13px',
        fontWeight: '500',
      }}>
        Responded
      </span>
    ) : (
      <span style={{
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        color: '#F59E0B',
        padding: '6px 10px',
        borderRadius: '4px',
        fontSize: '13px',
        fontWeight: '500',
      }}>
        Pending
      </span>
    );
  };
  
  const getCategoryBadge = (category) => {
    switch (category) {
      case 'meeting':
        return (
          <span style={{
            backgroundColor: 'rgba(249, 115, 22, 0.1)',
            color: '#F97316',
            padding: '6px 10px',
            borderRadius: '4px',
            fontSize: '13px',
            fontWeight: '500',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}>
            <StarIcon style={{ fontSize: '16px' }} />
            Meeting
          </span>
        );
      case 'needs_review':
        return (
          <span style={{
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            color: '#F59E0B',
            padding: '6px 10px',
            borderRadius: '4px',
            fontSize: '13px',
            fontWeight: '500',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}>
            <InfoIcon style={{ fontSize: '16px' }} />
            Needs Review
          </span>
        );
      case 'not_actionable':
        return (
          <span style={{
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            color: '#10B981',
            padding: '6px 10px',
            borderRadius: '4px',
            fontSize: '13px',
            fontWeight: '500',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}>
            <CheckCircleIcon style={{ fontSize: '16px' }} />
            Not Actionable
          </span>
        );
      default:
        return (
          <span style={{
            backgroundColor: 'rgba(107, 114, 128, 0.1)',
            color: '#6B7280',
            padding: '6px 10px',
            borderRadius: '4px',
            fontSize: '13px',
            fontWeight: '500',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}>
            <HelpIcon style={{ fontSize: '16px' }} />
            Unknown
          </span>
        );
    }
  };
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };
  
  if (loading) {
    return (
      <DashboardLayout>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div style={{ color: 'var(--body-color)', fontSize: '16px' }}>Loading email details...</div>
        </div>
      </DashboardLayout>
    );
  }
  
  if (error) {
    return (
      <DashboardLayout>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div style={{ color: 'var(--error-color)', fontSize: '16px' }}>{error}</div>
          <button
            onClick={() => navigate('/dashboard')}
            style={{
              marginTop: '20px',
              backgroundColor: 'var(--primary-color)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              padding: '8px 16px',
              cursor: 'pointer',
            }}
          >
            Return to Dashboard
          </button>
        </div>
      </DashboardLayout>
    );
  }
  
  if (!email) {
    return (
      <DashboardLayout>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div style={{ color: 'var(--error-color)', fontSize: '16px' }}>Email not found</div>
          <button
            onClick={() => navigate('/dashboard')}
            style={{
              marginTop: '20px',
              backgroundColor: 'var(--primary-color)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              padding: '8px 16px',
              cursor: 'pointer',
            }}
          >
            Return to Dashboard
          </button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        {/* Back Button */}
        <div style={{ marginBottom: '20px' }}>
          <button
            onClick={() => navigate('/dashboard')}
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
            Back to Dashboard
          </button>
        </div>
        
        {/* Email Header */}
        <div style={{ 
          backgroundColor: 'white',
          padding: '24px',
          borderRadius: '10px',
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
          marginBottom: '24px',
        }}>
          <div style={{ 
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            marginBottom: '16px',
          }}>
            <h1 style={{ 
              fontSize: '20px',
              fontWeight: '600',
              color: 'var(--text-color)',
              margin: 0,
            }}>
              {email.subject}
            </h1>
            {getStatusBadge(email.is_responded)}
          </div>
          
          <div style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ 
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                backgroundColor: 'var(--primary-light)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
              }}>
                <PersonIcon />
              </div>
              <div>
                <div style={{ fontWeight: '500', color: 'var(--text-color)' }}>
                  {email.sender}
                </div>
                <div style={{ fontSize: '13px', color: 'var(--body-color)' }}>
                  Received: {formatDate(email.received_at)}
                </div>
              </div>
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '10px' }}>
            {getCategoryBadge(email.category)}
            
            {email.analysis_results?.confidence_score && (
              <span style={{
                backgroundColor: 'rgba(107, 114, 128, 0.1)',
                color: '#6B7280',
                padding: '6px 10px',
                borderRadius: '4px',
                fontSize: '13px',
                fontWeight: '500',
              }}>
                Confidence: {Math.round(email.analysis_results.confidence_score * 100)}%
              </span>
            )}
          </div>
        </div>
        
        {/* Email Content and Analysis */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '24px' }}>
          {/* Email Content */}
          <div style={{ 
            backgroundColor: 'white',
            padding: '24px',
            borderRadius: '10px',
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
          }}>
            <h2 style={{ 
              fontSize: '16px',
              fontWeight: '600',
              color: 'var(--text-color)',
              marginBottom: '16px',
            }}>
              Email Content
            </h2>
            
            <div style={{ 
              whiteSpace: 'pre-wrap',
              fontSize: '14px',
              lineHeight: '1.6',
              color: 'var(--text-color)',
            }}>
              {email.content?.processed_content || email.content?.raw_content}
            </div>
          </div>
          
          {/* Analysis Results */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Meeting Details */}
            {email.analysis_results?.meeting_details && (
              <div style={{ 
                backgroundColor: 'white',
                padding: '24px',
                borderRadius: '10px',
                boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
              }}>
                <h2 style={{ 
                  fontSize: '16px',
                  fontWeight: '600',
                  color: 'var(--text-color)',
                  marginBottom: '16px',
                }}>
                  Meeting Details
                </h2>
                
                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                  {email.analysis_results.meeting_details.date && (
                    <li style={{ 
                      display: 'flex', 
                      alignItems: 'flex-start', 
                      gap: '12px',
                      marginBottom: '12px',
                    }}>
                      <EventIcon style={{ color: 'var(--primary-color)', fontSize: '18px', marginTop: '2px' }} />
                      <div>
                        <div style={{ fontSize: '13px', color: 'var(--body-color)', marginBottom: '2px' }}>Date</div>
                        <div style={{ fontSize: '14px', color: 'var(--text-color)' }}>
                          {email.analysis_results.meeting_details.date}
                        </div>
                      </div>
                    </li>
                  )}
                  
                  {email.analysis_results.meeting_details.time && (
                    <li style={{ 
                      display: 'flex', 
                      alignItems: 'flex-start', 
                      gap: '12px',
                      marginBottom: '12px',
                    }}>
                      <AccessTimeIcon style={{ color: 'var(--primary-color)', fontSize: '18px', marginTop: '2px' }} />
                      <div>
                        <div style={{ fontSize: '13px', color: 'var(--body-color)', marginBottom: '2px' }}>Time</div>
                        <div style={{ fontSize: '14px', color: 'var(--text-color)' }}>
                          {email.analysis_results.meeting_details.time}
                        </div>
                      </div>
                    </li>
                  )}
                  
                  {email.analysis_results.meeting_details.location && (
                    <li style={{ 
                      display: 'flex', 
                      alignItems: 'flex-start', 
                      gap: '12px',
                      marginBottom: '12px',
                    }}>
                      <LocationOnIcon style={{ color: 'var(--primary-color)', fontSize: '18px', marginTop: '2px' }} />
                      <div>
                        <div style={{ fontSize: '13px', color: 'var(--body-color)', marginBottom: '2px' }}>Location</div>
                        <div style={{ fontSize: '14px', color: 'var(--text-color)' }}>
                          {email.analysis_results.meeting_details.location}
                        </div>
                      </div>
                    </li>
                  )}
                  
                  {email.analysis_results.meeting_details.agenda && (
                    <li style={{ 
                      display: 'flex', 
                      alignItems: 'flex-start', 
                      gap: '12px',
                      marginBottom: '12px',
                    }}>
                      <EventNoteIcon style={{ color: 'var(--primary-color)', fontSize: '18px', marginTop: '2px' }} />
                      <div>
                        <div style={{ fontSize: '13px', color: 'var(--body-color)', marginBottom: '2px' }}>Agenda</div>
                        <div style={{ fontSize: '14px', color: 'var(--text-color)' }}>
                          {email.analysis_results.meeting_details.agenda}
                        </div>
                      </div>
                    </li>
                  )}
                  
                  {email.analysis_results.meeting_details.participants && 
                   email.analysis_results.meeting_details.participants.length > 0 && (
                    <li style={{ 
                      display: 'flex', 
                      alignItems: 'flex-start', 
                      gap: '12px',
                    }}>
                      <GroupIcon style={{ color: 'var(--primary-color)', fontSize: '18px', marginTop: '2px' }} />
                      <div>
                        <div style={{ fontSize: '13px', color: 'var(--body-color)', marginBottom: '2px' }}>Participants</div>
                        <div style={{ fontSize: '14px', color: 'var(--text-color)' }}>
                          {email.analysis_results.meeting_details.participants.join(', ')}
                        </div>
                      </div>
                    </li>
                  )}
                </ul>
              </div>
            )}
            
            {/* Suggested Response */}
            {email.analysis_results?.suggested_response && (
              <div style={{ 
                backgroundColor: 'white',
                padding: '24px',
                borderRadius: '10px',
                boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
              }}>
                <h2 style={{ 
                  fontSize: '16px',
                  fontWeight: '600',
                  color: 'var(--text-color)',
                  marginBottom: '16px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}>
                  <span>Suggested Response</span>
                  <button
                    style={{
                      backgroundColor: 'var(--primary-color)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      padding: '6px 12px',
                      fontSize: '13px',
                      cursor: 'pointer',
                    }}
                  >
                    Use This
                  </button>
                </h2>
                
                <div style={{ 
                  whiteSpace: 'pre-wrap',
                  fontSize: '14px',
                  lineHeight: '1.6',
                  color: 'var(--text-color)',
                  backgroundColor: 'rgba(74, 108, 247, 0.05)',
                  padding: '16px',
                  borderRadius: '6px',
                  border: '1px solid rgba(74, 108, 247, 0.1)',
                }}>
                  {email.analysis_results.suggested_response}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default EmailDetailPage;