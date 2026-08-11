import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Home from './components/Home';
import Essen from './components/Essen';
import Wein from './components/Wein';
import Search from './components/Search';
import Admin from './components/Admin';
import Auth from './components/Auth';
import UeberUns from './components/UeberUns';
import Impressum from './components/Impressum';
import './App.css';

const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:5005' : ''; // Flask backend address (dev vs prod)

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [user, setUser] = useState({
    logged_in: false,
    name: 'Gast',
    role: 'gast',
    email: null
  });
  
  // Highlighting selected recipes from the Search page
  const [preloadEssen, setPreloadEssen] = useState(null);
  const [preloadWein, setPreloadWein] = useState(null);

  // Authenticate session on load
  const checkSession = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/me`, {
        // Essential to pass cookies across origins
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setUser(data);
      }
    } catch (err) {
      console.warn("Backend session check failed (backend might not be running yet).");
    }
  };

  useEffect(() => {
    checkSession();
  }, []);

  const handleLoginSuccess = (userData) => {
    setUser({
      logged_in: true,
      name: userData.name,
      role: userData.role,
      email: userData.email
    });
    setActiveTab('home');
  };

  const handleLogout = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/abmeldung`, {
        method: 'POST',
        credentials: 'include'
      });
    } catch (err) {
      console.error("Logout failed:", err);
    }
    setUser({
      logged_in: false,
      name: 'Gast',
      role: 'gast',
      email: null
    });
    setActiveTab('home');
  };

  const handleSelectEssenFromSearch = (item) => {
    setPreloadEssen(item);
    setActiveTab('essen');
  };

  const handleSelectWeinFromSearch = (item) => {
    setPreloadWein(item);
    setActiveTab('wein');
  };

  // Render view depending on state routing
  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return <Home setActiveTab={setActiveTab} user={user} />;
      case 'essen':
        return (
          <Essen 
            baseUrl={API_BASE_URL} 
            user={user} 
            selectedPreloadEssen={preloadEssen} 
            clearPreload={() => setPreloadEssen(null)} 
          />
        );
      case 'wein':
        return (
          <Wein 
            baseUrl={API_BASE_URL} 
            user={user} 
            selectedPreloadWein={preloadWein} 
            clearPreload={() => setPreloadWein(null)} 
          />
        );
      case 'suche':
        return (
          <Search 
            baseUrl={API_BASE_URL} 
            onSelectEssen={handleSelectEssenFromSearch} 
            onSelectWein={handleSelectWeinFromSearch} 
          />
        );
      case 'ueberuns':
        return <UeberUns />;
      case 'impressum':
        return <Impressum />;
      case 'admin':
        if (user.role !== 'admin') return <Home setActiveTab={setActiveTab} user={user} />;
        return <Admin baseUrl={API_BASE_URL} />;
      case 'login':
        return <Auth onLoginSuccess={handleLoginSuccess} baseUrl={API_BASE_URL} />;
      default:
        return <Home setActiveTab={setActiveTab} user={user} />;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        user={user} 
        onLogout={handleLogout} 
      />
      <main className="page-container">
        {renderContent()}
      </main>
      <footer style={{ 
        marginTop: 'auto', 
        padding: '30px 24px', 
        borderTop: '1px solid var(--card-border)', 
        textAlign: 'center',
        color: 'var(--text-muted)',
        fontSize: '0.85rem'
      }}>
        © 2026 Rezeptbuch & Brauportal. Alle Rechte vorbehalten. Schulprojekt-Sim.
        {' · '}
        <span
          onClick={() => setActiveTab('impressum')}
          style={{ cursor: 'pointer', textDecoration: 'underline' }}
        >
          Impressum
        </span>
      </footer>
    </div>
  );
}
