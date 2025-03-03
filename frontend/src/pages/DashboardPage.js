import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import StatsCard from '../components/dashboard/StatsCard';
import EmailList from '../components/dashboard/EmailList';
import { dashboardService, emailService } from '../services/api';

// MUI Icons
import RefreshIcon from '@mui/icons-material/Refresh';
import FilterListIcon from '@mui/icons-material/FilterList';
import MoreVertIcon from '@mui/icons-material/MoreVert';

// Mock data for demonstration
const mockEmails = [
  {
    message_id: 'msg1',
    subject: 'Weekly Team Meeting - Planning Session',
    sender: 'john.smith@company.com',
    received_at: '2023-10-15T14:30:00Z',
    category: 'meeting',
    is_responded: true
  },
  {
    message_id: 'msg2',
    subject: 'Project Update Required',
    sender: 'project-manager@company.com',
    received_at: '2023-10-15T10:15:00Z',
    category: 'needs_review',
    is_responded: false
  },
  {
    message_id: 'msg3',
    subject: 'Department Lunch Next Week',
    sender: 'events@company.com',
    received_at: '2023-10-14T16:45:00Z',
    category: 'meeting',
    is_responded: false
  },
  {
    message_id: 'msg4',
    subject: 'System Maintenance Notice',
    sender: 'it-support@company.com',
    received_at: '2023-10-14T09:20:00Z',
    category: 'not_actionable',
    is_responded: true
  },
  {
    message_id: 'msg5',
    subject: 'Interview Scheduling - Frontend Developer Position',
    sender: 'hr@company.com',
    received_at: '2023-10-13T13:10:00Z',
    category: 'meeting',
    is_responded: true
  }
];

const mockStats = {
  total_emails: 138,
  meeting_emails: 47,
  success_rate: 95,
  avg_process_time: 250
};

const DashboardPage = () => {
  const [emails, setEmails] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');

  useEffect(() => {
    // Fetch data from the API
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch dashboard stats and email data simultaneously
        const [statsResponse, emailsResponse] = await Promise.all([
          dashboardService.getStats(),
          emailService.getEmails(10)
        ]);
        
        setEmails(emailsResponse.emails || []);
        
        // Extract relevant stats from the dashboard stats response
        const dashStats = {
          total_emails: statsResponse.total_emails,
          meeting_emails: statsResponse.meeting_emails,
          success_rate: statsResponse.success_rate,
          avg_process_time: statsResponse.avg_processing_time
        };
        
        setStats(dashStats);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
        
        // Fall back to mock data in case of error
        setEmails(mockEmails);
        setStats(mockStats);
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  const handleRefresh = async () => {
    try {
      setLoading(true);
      
      // Fetch updated data from the API
      const [statsResponse, emailsResponse] = await Promise.all([
        dashboardService.getStats(),
        emailService.getEmails(10)
      ]);
      
      setEmails(emailsResponse.emails || []);
      
      // Extract relevant stats from the dashboard stats response
      const dashStats = {
        total_emails: statsResponse.total_emails,
        meeting_emails: statsResponse.meeting_emails,
        success_rate: statsResponse.success_rate,
        avg_process_time: statsResponse.avg_processing_time
      };
      
      setStats(dashStats);
      setLoading(false);
    } catch (err) {
      console.error('Error refreshing dashboard data:', err);
      setError('Failed to refresh data. Please try again.');
      setLoading(false);
    }
  };
  
  const handleFilterChange = async (filter) => {
    setActiveFilter(filter);
    setLoading(true);
    
    try {
      // Fetch filtered emails from the API
      const response = await emailService.getEmails(10, 0, filter === 'all' ? null : filter);
      setEmails(response.emails || []);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching filtered emails:', err);
      setError('Failed to load filtered emails. Please try again.');
      
      // Fall back to filtering the existing emails
      if (filter === 'all') {
        setEmails(mockEmails);
      } else {
        setEmails(mockEmails.filter(email => email.category === filter));
      }
      setLoading(false);
    }
  };
  
  const getFilteredEmails = () => {
    if (activeFilter === 'all') return emails;
    return emails.filter(email => email.category === activeFilter);
  };
  
  return (
    <DashboardLayout>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <header style={{ marginBottom: '24px' }}>
          <h1 style={{ 
            fontSize: '24px', 
            fontWeight: '700', 
            color: 'var(--text-color)',
            marginBottom: '8px'
          }}>
            Dashboard
          </h1>
          <p style={{ fontSize: '15px', color: 'var(--body-color)' }}>
            Monitor and manage your emails
          </p>
        </header>
        
        {/* Stats Section */}
        <section style={{ marginBottom: '32px' }}>
          <div style={{ 
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
            gap: '20px'
          }}>
            <StatsCard 
              title="Total Emails" 
              value={stats?.total_emails || '-'} 
              change={+12} 
              type="total" 
            />
            <StatsCard 
              title="Meeting Emails" 
              value={stats?.meeting_emails || '-'} 
              change={+8} 
              type="meetings" 
            />
            <StatsCard 
              title="Success Rate" 
              value={`${stats?.success_rate || '-'}%`} 
              change={+2} 
              type="success" 
            />
            <StatsCard 
              title="Avg. Process Time" 
              value={`${stats?.avg_process_time || '-'} ms`} 
              change={-5} 
              type="speed" 
            />
          </div>
        </section>
        
        {/* Email List Section */}
        <section>
          <div style={{ 
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '16px'
          }}>
            <h2 style={{ 
              fontSize: '18px', 
              fontWeight: '600',
              color: 'var(--text-color)',
              margin: 0
            }}>
              Recent Emails
            </h2>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleRefresh}
                style={{
                  backgroundColor: 'transparent',
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '8px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  color: 'var(--body-color)',
                }}
              >
                <RefreshIcon style={{ fontSize: '20px' }} />
              </motion.button>
              
              <div style={{ position: 'relative' }}>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  style={{
                    backgroundColor: 'transparent',
                    border: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '8px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    color: 'var(--body-color)',
                  }}
                >
                  <FilterListIcon style={{ fontSize: '20px' }} />
                </motion.button>
                
                <div style={{ 
                  position: 'absolute',
                  top: 'calc(100% + 8px)',
                  right: 0,
                  backgroundColor: 'white',
                  borderRadius: '8px',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                  padding: '8px 0',
                  zIndex: 10,
                  width: '180px',
                  display: 'none' // Hidden by default, would be controlled by state in a real app
                }}>
                  <div style={{ padding: '8px 16px', fontSize: '14px', fontWeight: '600', color: 'var(--body-color)' }}>
                    Filter by:
                  </div>
                  
                  {['all', 'meeting', 'needs_review', 'not_actionable'].map(filter => (
                    <button
                      key={filter}
                      onClick={() => handleFilterChange(filter)}
                      style={{
                        display: 'block',
                        width: '100%',
                        textAlign: 'left',
                        padding: '8px 16px',
                        fontSize: '14px',
                        border: 'none',
                        backgroundColor: activeFilter === filter ? 'rgba(74, 108, 247, 0.1)' : 'transparent',
                        color: activeFilter === filter ? 'var(--primary-color)' : 'var(--text-color)',
                        cursor: 'pointer',
                      }}
                    >
                      {filter === 'all' ? 'All Emails' : 
                       filter === 'meeting' ? 'Meeting Emails' :
                       filter === 'needs_review' ? 'Needs Review' : 'Not Actionable'}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
          
          <EmailList 
            emails={getFilteredEmails()} 
            loading={loading} 
            error={error} 
          />
        </section>
      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;