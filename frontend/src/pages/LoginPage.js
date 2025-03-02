import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import GoogleIcon from '@mui/icons-material/Google';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();
  
  const handleLogin = async (e) => {
    e.preventDefault();
    
    // Basic validation
    if (!email || !password) {
      setError('Please enter both email and password');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      
      // In a real application, you would call your API here
      // For now, we'll simulate a login with a timeout
      setTimeout(() => {
        // Hardcoded demo credentials
        if (email === 'demo@example.com' && password === 'password') {
          console.log('Login successful');
          // Store token and redirect to dashboard
          localStorage.setItem('token', 'demo-token');
          navigate('/dashboard');
        } else {
          setError('Invalid credentials. Try demo@example.com / password');
        }
        setLoading(false);
      }, 1500);
      
    } catch (err) {
      setError('An error occurred during login. Please try again.');
      setLoading(false);
    }
  };
  
  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      setError('');
      
      // In a real application, you would initiate the Google OAuth flow here
      // For demonstration purposes, we'll simulate a successful login
      setTimeout(() => {
        console.log('Google login successful');
        localStorage.setItem('token', 'google-demo-token');
        navigate('/dashboard');
        setLoading(false);
      }, 1000);
      
    } catch (err) {
      setError('An error occurred with Google login. Please try again.');
      setLoading(false);
    }
  };
  
  return (
    <div style={{ 
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: 'var(--background-color)',
      padding: '20px'
    }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 5px 20px rgba(0, 0, 0, 0.1)',
          width: '100%',
          maxWidth: '460px',
          padding: '40px',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <Link to="/" style={{ textDecoration: 'none' }}>
            <h1 style={{ fontSize: '28px', fontWeight: 700, color: 'var(--text-color)' }}>
              Sentient<span style={{ color: 'var(--primary-color)' }}>Inbox</span>
            </h1>
          </Link>
          <p style={{ 
            fontSize: '16px',
            color: 'var(--body-color)',
            marginTop: '8px'
          }}>
            Sign in to your account
          </p>
        </div>
        
        {error && (
          <div style={{
            backgroundColor: 'rgba(209, 67, 67, 0.1)',
            color: 'var(--error-color)',
            padding: '12px',
            borderRadius: '6px',
            marginBottom: '20px',
            fontSize: '14px'
          }}>
            {error}
          </div>
        )}
        
        <form onSubmit={handleLogin}>
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
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '1.5px solid var(--border-color)',
                borderRadius: '6px',
                fontSize: '15px',
                outline: 'none',
                transition: 'border-color 0.3s ease',
              }}
            />
          </div>
          
          <div style={{ marginBottom: '24px' }}>
            <div style={{ 
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '8px'
            }}>
              <label 
                htmlFor="password" 
                style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: 'var(--text-color)'
                }}
              >
                Password
              </label>
              <a 
                href="#" 
                style={{
                  fontSize: '13px',
                  color: 'var(--primary-color)',
                  textDecoration: 'none'
                }}
              >
                Forgot password?
              </a>
            </div>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '1.5px solid var(--border-color)',
                borderRadius: '6px',
                fontSize: '15px',
                outline: 'none',
                transition: 'border-color 0.3s ease',
              }}
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '14px',
              backgroundColor: 'var(--primary-color)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '16px',
              fontWeight: '500',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
              transition: 'all 0.3s ease',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              marginBottom: '16px',
            }}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
          
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            margin: '16px 0',
            color: 'var(--body-color)',
            fontSize: '14px',
          }}>
            <div style={{ 
              flex: 1, 
              height: '1px', 
              backgroundColor: 'var(--border-color)' 
            }}></div>
            <span style={{ margin: '0 10px' }}>or</span>
            <div style={{ 
              flex: 1, 
              height: '1px', 
              backgroundColor: 'var(--border-color)' 
            }}></div>
          </div>
          
          <button
            type="button"
            onClick={handleGoogleLogin}
            disabled={loading}
            style={{
              width: '100%',
              padding: '14px',
              backgroundColor: 'white',
              color: '#333',
              border: '1.5px solid var(--border-color)',
              borderRadius: '6px',
              fontSize: '16px',
              fontWeight: '500',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
              transition: 'all 0.3s ease',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: '10px',
            }}
          >
            <GoogleIcon style={{ color: '#4285F4' }} />
            Sign in with Google
          </button>
        </form>
        
        <div style={{ 
          marginTop: '32px',
          textAlign: 'center',
          fontSize: '14px',
          color: 'var(--body-color)'
        }}>
          Don't have an account?{' '}
          <Link 
            to="#" 
            style={{
              color: 'var(--primary-color)',
              fontWeight: '500',
              textDecoration: 'none'
            }}
          >
            Sign up
          </Link>
        </div>
        
        <div style={{ 
          marginTop: '40px',
          textAlign: 'center'
        }}>
          <Link 
            to="/" 
            style={{
              fontSize: '14px',
              color: 'var(--body-color)',
              textDecoration: 'none'
            }}
          >
            ← Back to home
          </Link>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage;