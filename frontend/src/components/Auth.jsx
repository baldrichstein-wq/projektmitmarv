import React, { useState } from 'react';
import { User, Mail, Lock, ShieldAlert } from 'lucide-react';

export default function Auth({ onLoginSuccess, baseUrl }) {
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!email || !password || (!isLogin && !name)) {
      setError('Bitte fülle alle Pflichtfelder aus.');
      return;
    }

    try {
      const endpoint = isLogin ? '/api/anmeldung' : '/api/registrierung';
      const body = isLogin ? { email, password } : { name, email, password };

      const response = await fetch(`${baseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        setError(data.message || 'Etwas ist schiefgelaufen.');
        return;
      }

      if (isLogin) {
        setSuccess('Erfolgreich angemeldet!');
        setTimeout(() => {
          onLoginSuccess(data.user);
        }, 1000);
      } else {
        setSuccess('Registrierung erfolgreich! Bitte melde dich jetzt an.');
        setIsLogin(true);
        setName('');
        setPassword('');
      }
    } catch (err) {
      setError('Netzwerkfehler: Stellen Sie sicher, dass das Backend läuft.');
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', justifyContent: 'center', margin: '40px 0' }}>
      <div className="glass" style={{ width: '100%', maxWidth: '450px', padding: '40px 30px' }}>
        
        {/* Toggle Mode */}
        <div style={{ display: 'flex', marginBottom: '30px', background: 'rgba(255,255,255,0.04)', borderRadius: '10px', padding: '4px' }}>
          <button 
            type="button"
            onClick={() => { setIsLogin(true); setError(''); setSuccess(''); }} 
            className="btn"
            style={{ 
              flex: 1, 
              background: isLogin ? 'var(--grad-primary)' : 'transparent',
              color: isLogin ? '#fff' : 'var(--text-secondary)',
              boxShadow: isLogin ? '0 4px 10px rgba(255,107,107,0.2)' : 'none'
            }}
          >
            Anmelden
          </button>
          <button 
            type="button"
            onClick={() => { setIsLogin(false); setError(''); setSuccess(''); }} 
            className="btn"
            style={{ 
              flex: 1, 
              background: !isLogin ? 'var(--grad-primary)' : 'transparent',
              color: !isLogin ? '#fff' : 'var(--text-secondary)',
              boxShadow: !isLogin ? '0 4px 10px rgba(255,107,107,0.2)' : 'none'
            }}
          >
            Registrieren
          </button>
        </div>

        <h2 style={{ fontSize: '1.6rem', marginBottom: '20px', textAlign: 'center' }}>
          {isLogin ? 'In Ihr Konto einloggen' : 'Neues Konto erstellen'}
        </h2>

        {error && (
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '10px', 
            background: 'rgba(239, 68, 68, 0.1)', 
            border: '1px solid rgba(239, 68, 68, 0.2)',
            padding: '12px 16px',
            borderRadius: '10px',
            color: '#f87171',
            marginBottom: '20px',
            fontSize: '0.9rem'
          }}>
            <ShieldAlert size={18} />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div style={{ 
            background: 'rgba(16, 185, 129, 0.1)', 
            border: '1px solid rgba(16, 185, 129, 0.2)',
            padding: '12px 16px',
            borderRadius: '10px',
            color: '#34d399',
            marginBottom: '20px',
            fontSize: '0.9rem'
          }}>
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="input-group">
              <label className="input-label" htmlFor="auth-name">Name</label>
              <div style={{ position: 'relative' }}>
                <span style={{ position: 'absolute', left: '14px', top: '15px', color: 'var(--text-muted)' }}>
                  <User size={16} />
                </span>
                <input 
                  id="auth-name"
                  type="text" 
                  className="input-field" 
                  placeholder="Ihr Name" 
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  style={{ paddingLeft: '40px', width: '100%' }}
                />
              </div>
            </div>
          )}

          <div className="input-group">
            <label className="input-label" htmlFor="auth-email">E-Mail Adresse</label>
            <div style={{ position: 'relative' }}>
              <span style={{ position: 'absolute', left: '14px', top: '15px', color: 'var(--text-muted)' }}>
                <Mail size={16} />
              </span>
              <input 
                id="auth-email"
                type="email" 
                className="input-field" 
                placeholder="beispiel@email.de" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ paddingLeft: '40px', width: '100%' }}
              />
            </div>
          </div>

          <div className="input-group" style={{ marginBottom: '30px' }}>
            <label className="input-label" htmlFor="auth-password">Passwort</label>
            <div style={{ position: 'relative' }}>
              <span style={{ position: 'absolute', left: '14px', top: '15px', color: 'var(--text-muted)' }}>
                <Lock size={16} />
              </span>
              <input 
                id="auth-password"
                type="password" 
                className="input-field" 
                placeholder="••••••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{ paddingLeft: '40px', width: '100%' }}
              />
            </div>
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '12px' }}>
            {isLogin ? 'Anmelden' : 'Registrierung abschließen'}
          </button>
        </form>

        <p style={{ marginTop: '20px', textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          {isLogin ? (
            <>
              Noch kein Konto?{' '}
              <span 
                onClick={() => { setIsLogin(false); setError(''); setSuccess(''); }} 
                style={{ color: '#ff6b6b', cursor: 'pointer', fontWeight: 600 }}
              >
                Jetzt registrieren
              </span>
            </>
          ) : (
            <>
              Bereits registriert?{' '}
              <span 
                onClick={() => { setIsLogin(true); setError(''); setSuccess(''); }} 
                style={{ color: '#ff6b6b', cursor: 'pointer', fontWeight: 600 }}
              >
                Hier anmelden
              </span>
            </>
          )}
        </p>

      </div>
    </div>
  );
}
