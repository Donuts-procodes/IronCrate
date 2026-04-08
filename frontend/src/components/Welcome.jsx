import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Welcome() {
  const navigate = useNavigate();

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>IRONCRATE</h1>
        <p style={styles.subtitle}>Secure Incident Logging & Analysis</p>
        
        <div style={styles.infoBox}>
          <p style={styles.infoText}>
            This application requires strict access to your <strong>Camera</strong> and <strong>Location</strong> to verify and authenticate incident reports.
          </p>
        </div>

        <button 
          style={styles.button} 
          onClick={() => navigate('/camera')}
          onMouseOver={(e) => e.target.style.transform = 'translateY(-2px)'}
          onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
        >
          Initialize System
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0f172a', // Dark slate background matching your theme
    color: '#f8fafc',
    padding: '20px',
    fontFamily: "'Syne', sans-serif",
  },
  card: {
    backgroundColor: '#1e293b',
    padding: '3rem 2rem',
    borderRadius: '16px',
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)',
    textAlign: 'center',
    maxWidth: '450px',
    width: '100%',
    border: '1px solid #334155'
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: '800',
    letterSpacing: '2px',
    margin: '0 0 10px 0',
    background: 'linear-gradient(to right, #38bdf8, #818cf8)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  subtitle: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.9rem',
    color: '#94a3b8',
    marginBottom: '2rem',
  },
  infoBox: {
    backgroundColor: 'rgba(56, 189, 248, 0.1)',
    borderLeft: '4px solid #38bdf8',
    padding: '1rem',
    marginBottom: '2rem',
    borderRadius: '0 8px 8px 0',
    textAlign: 'left'
  },
  infoText: {
    margin: 0,
    fontSize: '0.95rem',
    color: '#cbd5e1',
    lineHeight: '1.5',
  },
  button: {
    backgroundColor: '#38bdf8',
    color: '#0f172a',
    border: 'none',
    padding: '14px 24px',
    fontSize: '1rem',
    fontWeight: '700',
    fontFamily: "'Syne', sans-serif",
    borderRadius: '8px',
    cursor: 'pointer',
    width: '100%',
    transition: 'transform 0.2s ease',
  }
};