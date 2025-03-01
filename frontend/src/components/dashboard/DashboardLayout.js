import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';

// MUI Icons
import DashboardIcon from '@mui/icons-material/Dashboard';
import EmailIcon from '@mui/icons-material/Email';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import SmartToyIcon from '@mui/icons-material/SmartToy';

const DashboardLayout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const handleLogout = () => {
    // Clear authentication
    localStorage.removeItem('token');
    // Redirect to login
    navigate('/login');
  };
  
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
  
  const navItems = [
    {
      name: 'Dashboard',
      icon: <DashboardIcon />,
      path: '/dashboard',
    },
    {
      name: 'AI Agents',
      icon: <SmartToyIcon />,
      path: '/agents',
    },
    {
      name: 'Settings',
      icon: <SettingsIcon />,
      path: '/settings',
    },
  ];
  
  const isActive = (path) => {
    return location.pathname === path;
  };
  
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar for desktop */}
      <aside
        style={{
          width: '250px',
          backgroundColor: 'var(--text-color)',
          color: 'white',
          padding: '20px 0',
          display: 'flex',
          flexDirection: 'column',
          position: 'fixed',
          height: '100vh',
          left: 0,
          top: 0,
          zIndex: 50,
          transition: 'transform 0.3s ease',
          transform: sidebarOpen ? 'translateX(0)' : 'translateX(-100%)',
          '@media (min-width: 1024px)': {
            transform: 'translateX(0)',
          },
        }}
        className="lg:translate-x-0"
      >
        {/* Logo */}
        <div style={{ padding: '0 20px', marginBottom: '40px' }}>
          <Link to="/dashboard" style={{ textDecoration: 'none' }}>
            <h1 style={{ fontSize: '24px', fontWeight: 700, color: 'white' }}>
              Sentient<span style={{ color: 'var(--primary-light)' }}>Inbox</span>
            </h1>
          </Link>
        </div>
        
        {/* Navigation Links */}
        <nav style={{ flex: 1 }}>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {navItems.map((item) => (
              <li key={item.name} style={{ marginBottom: '8px' }}>
                <Link
                  to={item.path}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '12px 20px',
                    color: 'white',
                    textDecoration: 'none',
                    backgroundColor: isActive(item.path)
                      ? 'rgba(255, 255, 255, 0.1)'
                      : 'transparent',
                    borderLeft: isActive(item.path)
                      ? '4px solid var(--primary-color)'
                      : '4px solid transparent',
                    transition: 'all 0.3s ease',
                  }}
                  onClick={() => setSidebarOpen(false)}
                >
                  <span style={{ marginRight: '12px', display: 'flex', alignItems: 'center' }}>
                    {item.icon}
                  </span>
                  <span>{item.name}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        
        {/* Logout Button */}
        <div style={{ padding: '20px' }}>
          <button
            onClick={handleLogout}
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '12px 20px',
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              width: '100%',
              transition: 'all 0.3s ease',
            }}
          >
            <span style={{ marginRight: '12px', display: 'flex', alignItems: 'center' }}>
              <LogoutIcon />
            </span>
            <span>Logout</span>
          </button>
        </div>
      </aside>
      
      {/* Mobile sidebar toggle */}
      <button
        onClick={toggleSidebar}
        style={{
          position: 'fixed',
          top: '20px',
          left: '20px',
          zIndex: 60,
          backgroundColor: 'var(--primary-color)',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          width: '40px',
          height: '40px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          '@media (min-width: 1024px)': {
            display: 'none',
          },
        }}
        className="lg:hidden"
      >
        {sidebarOpen ? <CloseIcon /> : <MenuIcon />}
      </button>
      
      {/* Overlay when sidebar is open on mobile */}
      {sidebarOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            zIndex: 40,
            '@media (min-width: 1024px)': {
              display: 'none',
            },
          }}
          className="lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      {/* Main content */}
      <main
        style={{
          flex: 1,
          marginLeft: '250px',
          padding: '20px',
          backgroundColor: 'var(--background-color)',
          '@media (max-width: 1023px)': {
            marginLeft: 0,
          },
        }}
        className="lg:ml-[250px] ml-0"
      >
        {children}
      </main>
    </div>
  );
};

export default DashboardLayout;