import React from 'react';
import { Sparkles, Calendar, BookOpen, ShieldCheck } from 'lucide-react';

export default function UeberUns() {
  const team = [
    { name: 'David', role: 'Deployment & Betrieb (NAS)', initial: 'D', color: '#ff6b6b' },
    { name: 'Stefan', role: 'Deployment & Betrieb (AWS)', initial: 'S', color: '#8a2387' },
  ];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      <div className="glass" style={{ padding: '40px' }}>
        <h1 style={{ fontSize: '2.2rem', marginBottom: '15px' }}>Über dieses Projekt</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', lineHeight: '1.7', marginBottom: '20px' }}>
          Dieses Projekt entstand im Rahmen der Backend-Projektphase.
          Ziel war es ursprünglich, ein Python/Flask-basiertes Rezeptbuch mit SQLite und Hashing-Sicherheitsfunktionen
          zu erstellen. Wir haben das Projekt seitdem zu einem modernen, reaktiven Frontend (Vite/React), einem
          entkoppelten JSON API Backend und einer produktiven PostgreSQL/MongoDB-Anbindung umgebaut — inklusive
          eigenständigem Deployment auf NAS (David) und AWS (Stefan).
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginTop: '30px' }}>
          <div style={{ display: 'flex', gap: '12px' }}>
            <div style={{ color: 'var(--color-success)' }}><ShieldCheck size={20} /></div>
            <div>
              <h4 style={{ fontSize: '0.95rem', marginBottom: '4px' }}>Sicherheit</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>Scrypt/PBKDF2 Passwort Hashing im Backend.</p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <div style={{ color: '#ff6b6b' }}><BookOpen size={20} /></div>
            <div>
              <h4 style={{ fontSize: '0.95rem', marginBottom: '4px' }}>Flexibilität</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>Dynamische Mengenumrechnung & Skalierung.</p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <div style={{ color: '#e94057' }}><Sparkles size={20} /></div>
            <div>
              <h4 style={{ fontSize: '0.95rem', marginBottom: '4px' }}>Moderner Stack</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>Vite, React, Flask, PostgreSQL, MongoDB und Glassmorphism.</p>
            </div>
          </div>
        </div>
      </div>

      <div>
        <h2 style={{ fontSize: '1.6rem', marginBottom: '20px' }}>Das Entwickler-Team</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
          {team.map((member) => (
            <div key={member.name} className="glass" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{
                width: '50px',
                height: '50px',
                borderRadius: '12px',
                background: member.color,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontFamily: 'var(--font-heading)',
                fontWeight: 800,
                fontSize: '1.2rem',
                boxShadow: '0 4px 10px rgba(0,0,0,0.15)'
              }}>
                {member.initial}
              </div>
              <div>
                <h3 style={{ fontSize: '1.1rem', marginBottom: '2px' }}>{member.name}</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{member.role}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="glass" style={{ padding: '30px' }}>
        <h3 style={{ marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Calendar size={18} /> Sprint Zeitplan (Agile Light)
        </h3>
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '12px', color: 'var(--text-secondary)' }}>
          <li style={{ display: 'flex', gap: '15px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '8px' }}>
            <strong style={{ color: '#fff', minWidth: '80px' }}>Woche 1</strong>
            <span>Datenbankanbindung, grundlegende CRUD-Funktionalität, Session-Management und Login.</span>
          </li>
          <li style={{ display: 'flex', gap: '15px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '8px' }}>
            <strong style={{ color: '#fff', minWidth: '80px' }}>Woche 2</strong>
            <span>Portionsrechner, Weinempfehlungen, globale Suchfunktion, Kommentar- und Bewertungssystem.</span>
          </li>
          <li style={{ display: 'flex', gap: '15px' }}>
            <strong style={{ color: '#fff', minWidth: '80px' }}>Woche 3</strong>
            <span>Refactoring auf React/Vite-Architektur, responsive UI-Optimierung, Deployment-Vorbereitungen.</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
