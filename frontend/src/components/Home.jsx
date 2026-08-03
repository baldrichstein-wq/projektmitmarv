import React from 'react';
import { BookOpen, Wine, Search, Compass, Shield, Users } from 'lucide-react';

export default function Home({ setActiveTab, user }) {
  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>
      
      {/* Hero Header Banner */}
      <div className="glass" style={{
        padding: '60px 40px',
        borderRadius: '24px',
        background: 'linear-gradient(135deg, rgba(20, 16, 32, 0.7) 0%, rgba(10, 8, 16, 0.9) 100%)',
        position: 'relative',
        overflow: 'hidden',
        border: '1px solid rgba(255, 107, 107, 0.15)'
      }}>
        {/* Absolute Background Accent Blur */}
        <div style={{
          position: 'absolute',
          top: '-50px',
          right: '-50px',
          width: '250px',
          height: '250px',
          background: 'rgba(255, 107, 107, 0.15)',
          borderRadius: '50%',
          filter: 'blur(80px)',
          pointerEvents: 'none'
        }}></div>
        <div style={{
          position: 'absolute',
          bottom: '-50px',
          left: '-50px',
          width: '200px',
          height: '200px',
          background: 'rgba(138, 35, 135, 0.2)',
          borderRadius: '50%',
          filter: 'blur(80px)',
          pointerEvents: 'none'
        }}></div>

        <div style={{ maxWidth: '700px', position: 'relative', zIndex: 1 }}>
          <h1 style={{ fontSize: '3rem', lineHeight: '1.2', marginBottom: '20px', fontWeight: 800 }}>
            Willkommen im <br />
            <span style={{ 
              background: 'var(--grad-primary)', 
              WebkitBackgroundClip: 'text', 
              WebkitTextFillColor: 'transparent' 
            }}>
              Rezeptbuch & Brauportal
            </span>
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', marginBottom: '30px' }}>
            Entdecke traditionelle Speisen, berechne Portionsmengen im Handumdrehen und erforsche die Kunst der Met- und Weinbrauerei.
          </p>
          
          <div style={{ display: 'flex', gap: '15px' }}>
            {user.logged_in ? (
              <>
                <button onClick={() => setActiveTab('essen')} className="btn btn-primary">
                  <BookOpen size={18} /> Zu den Rezepten
                </button>
                <button onClick={() => setActiveTab('wein')} className="btn btn-secondary">
                  <Wine size={18} /> Weine ansehen
                </button>
              </>
            ) : (
              <>
                <button onClick={() => setActiveTab('login')} className="btn btn-primary">
                  Jetzt Anmelden
                </button>
                <button onClick={() => setActiveTab('suche')} className="btn btn-secondary">
                  <Search size={18} /> Rezepte suchen
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Feature Grid */}
      <div>
        <h2 style={{ fontSize: '1.8rem', marginBottom: '20px', textAlign: 'center' }}>
          Unsere Kernfunktionen
        </h2>
        <div className="card-grid">
          
          <div className="glass" style={{ padding: '30px', transition: 'transform 0.3s ease', cursor: 'pointer' }} onClick={() => setActiveTab('essen')}>
            <div style={{ background: 'rgba(255,107,107,0.1)', padding: '12px', borderRadius: '12px', width: 'fit-content', marginBottom: '20px', color: '#ff6b6b' }}>
              <BookOpen size={24} />
            </div>
            <h3 style={{ marginBottom: '10px' }}>Exquisite Rezepte</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
              Verwalte Speisenrezepte, passe Zutatenmengen dynamisch an die Personenanzahl an und koche mit klaren Schritt-für-Schritt Anweisungen.
            </p>
          </div>

          <div className="glass" style={{ padding: '30px', transition: 'transform 0.3s ease', cursor: 'pointer' }} onClick={() => setActiveTab('wein')}>
            <div style={{ background: 'rgba(233,64,87,0.1)', padding: '12px', borderRadius: '12px', width: 'fit-content', marginBottom: '20px', color: '#e94057' }}>
              <Wine size={24} />
            </div>
            <h3 style={{ marginBottom: '10px' }}>Braumeister Register</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
              Dokumentiere deine Weine, notiere Zutaten und Gärungszeiten, behalte den Alkoholgehalt im Auge und teile Brau-Geheimnisse.
            </p>
          </div>

          <div className="glass" style={{ padding: '30px', transition: 'transform 0.3s ease', cursor: 'pointer' }} onClick={() => setActiveTab('suche')}>
            <div style={{ background: 'rgba(242,113,33,0.1)', padding: '12px', borderRadius: '12px', width: 'fit-content', marginBottom: '20px', color: '#f27121' }}>
              <Search size={24} />
            </div>
            <h3 style={{ marginBottom: '10px' }}>Globale Suche</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
              Finde Rezepte und Weine blitzschnell nach Name, Beschreibung oder spezifischen Zutaten über unsere vereinheitlichte Suche.
            </p>
          </div>

        </div>
      </div>

      {/* Info Sections */}
      <div className="glass" style={{ padding: '30px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <h3 style={{ borderBottom: '1px solid var(--card-border)', paddingBottom: '10px' }}>
          Projektstatus & Rollensystem
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          <div style={{ display: 'flex', gap: '15px' }}>
            <div style={{ color: 'var(--color-success)', marginTop: '4px' }}>
              <Compass size={20} />
            </div>
            <div>
              <h4 style={{ fontSize: '1rem', marginBottom: '4px' }}>Offline-Fähig & SQLite</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                Alle Daten werden sicher im Backend in SQLite Datenbanken abgelegt und können direkt geladen werden.
              </p>
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '15px' }}>
            <div style={{ color: 'var(--color-warning)', marginTop: '4px' }}>
              <Shield size={20} />
            </div>
            <div>
              <h4 style={{ fontSize: '1rem', marginBottom: '4px' }}>Rechte & Rollen</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                Gäste können nur stöbern. Benutzer können Rezepte erstellen/bearbeiten. Admins besitzen vollumfängliche Löschrechte.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '15px' }}>
            <div style={{ color: '#8a2387', marginTop: '4px' }}>
              <Users size={20} />
            </div>
            <div>
              <h4 style={{ fontSize: '1rem', marginBottom: '4px' }}>Team-Kollaboration</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                Entwickelt von Marvin, Marina, Stefan und David als agiles Schulprojekt.
              </p>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
