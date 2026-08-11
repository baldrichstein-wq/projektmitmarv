import React from 'react';
import { BookOpen, Wine, Search, User, LogOut, Info, Home as HomeIcon, ShieldCheck } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, user, onLogout }) {
  return (
    <nav className="navbar glass">
      <div className="navbar-container">
        <div 
          className="brand" 
          style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}
          onClick={() => setActiveTab('home')}
        >
          <div style={{
            background: 'var(--grad-primary)',
            padding: '8px',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 10px rgba(255,107,107,0.3)'
          }}>
            <BookOpen size={20} color="#fff" />
          </div>
          <span style={{ 
            fontFamily: 'var(--font-heading)', 
            fontWeight: 800, 
            fontSize: '1.2rem',
            background: 'var(--grad-primary)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Rezept&Brau
          </span>
        </div>

        <div className="nav-links">
          <span 
            className={`nav-link ${activeTab === 'home' ? 'active' : ''}`}
            onClick={() => setActiveTab('home')}
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <HomeIcon size={16} /> Home
          </span>
          
          {user.role !== 'gast' && (
            <>
              <span 
                className={`nav-link ${activeTab === 'essen' ? 'active' : ''}`}
                onClick={() => setActiveTab('essen')}
                style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                <BookOpen size={16} /> Rezepte
              </span>
              <span 
                className={`nav-link ${activeTab === 'wein' ? 'active' : ''}`}
                onClick={() => setActiveTab('wein')}
                style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                <Wine size={16} /> Weine
              </span>
            </>
          )}

          <span 
            className={`nav-link ${activeTab === 'suche' ? 'active' : ''}`}
            onClick={() => setActiveTab('suche')}
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Search size={16} /> Suche
          </span>

          <span 
            className={`nav-link ${activeTab === 'ueberuns' ? 'active' : ''}`}
            onClick={() => setActiveTab('ueberuns')}
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Info size={16} /> Über uns
          </span>

          {user.role !== 'gast' && (
            <span
              className={`nav-link ${activeTab === 'sicherheit' ? 'active' : ''}`}
              onClick={() => setActiveTab('sicherheit')}
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <ShieldCheck size={16} /> Sicherheit
            </span>
          )}

          {user.role === 'admin' && (
            <span
              className={`nav-link ${activeTab === 'admin' ? 'active' : ''}`}
              onClick={() => setActiveTab('admin')}
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <User size={16} /> Admin
            </span>
          )}
        </div>

        <div className="nav-auth" style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          {user.logged_in ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{user.name}</span>
                <span className={`badge badge-role-${user.role}`} style={{ fontSize: '0.7rem', padding: '2px 6px' }}>
                  {user.role.toUpperCase()}
                </span>
              </div>
              <button onClick={onLogout} className="btn btn-secondary" style={{ padding: '8px 12px', fontSize: '0.85rem' }}>
                <LogOut size={14} /> Abmelden
              </button>
            </div>
          ) : (
            <button onClick={() => setActiveTab('login')} className="btn btn-primary" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
              Anmelden
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
