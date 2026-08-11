import React, { useState, useEffect } from 'react';
import { ShieldCheck, ShieldAlert, KeyRound, Lock } from 'lucide-react';
import { apiFetch } from '../utils/api';

export default function Sicherheit({ baseUrl }) {
  const [loading, setLoading] = useState(true);
  const [enabled, setEnabled] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Setup-Flow (2FA aktivieren)
  const [setupData, setSetupData] = useState(null); // { secret, otpauth_uri, qr_svg }
  const [confirmCode, setConfirmCode] = useState('');

  // Deaktivieren-Flow
  const [showDisableForm, setShowDisableForm] = useState(false);
  const [disablePassword, setDisablePassword] = useState('');

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const response = await apiFetch(`${baseUrl}/api/2fa/status`);
      const data = await response.json();
      if (data.success) setEnabled(data.enabled);
    } catch (err) {
      setError('Netzwerkfehler beim Laden des 2FA-Status.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const startSetup = async () => {
    setError('');
    setSuccess('');
    try {
      const response = await apiFetch(`${baseUrl}/api/2fa/setup`, { method: 'POST' });
      const data = await response.json();
      if (data.success) {
        setSetupData(data);
      } else {
        setError(data.message || 'Setup fehlgeschlagen.');
      }
    } catch (err) {
      setError('Netzwerkfehler.');
    }
  };

  const confirmSetup = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const response = await apiFetch(`${baseUrl}/api/2fa/aktivieren`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: confirmCode.trim() }),
      });
      const data = await response.json();
      if (data.success) {
        setSuccess(data.message);
        setSetupData(null);
        setConfirmCode('');
        setEnabled(true);
      } else {
        setError(data.message || 'Code ungültig.');
      }
    } catch (err) {
      setError('Netzwerkfehler.');
    }
  };

  const handleDisable = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const response = await apiFetch(`${baseUrl}/api/2fa/deaktivieren`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: disablePassword }),
      });
      const data = await response.json();
      if (data.success) {
        setSuccess(data.message);
        setEnabled(false);
        setShowDisableForm(false);
        setDisablePassword('');
      } else {
        setError(data.message || 'Deaktivieren fehlgeschlagen.');
      }
    } catch (err) {
      setError('Netzwerkfehler.');
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '30px', maxWidth: '600px', margin: '0 auto' }}>
      <div className="glass" style={{ padding: '40px' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <ShieldCheck size={26} /> Sicherheit
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Schütze dein Konto zusätzlich mit einer Zwei-Faktor-Authentifizierung (TOTP) über eine
          Authenticator-App wie Google Authenticator, Authy oder Ente Auth.
        </p>
      </div>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '12px 16px', borderRadius: '10px', color: '#f87171', fontSize: '0.9rem' }}>
          <ShieldAlert size={18} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '12px 16px', borderRadius: '10px', color: '#34d399', fontSize: '0.9rem' }}>
          {success}
        </div>
      )}

      {loading ? (
        <p style={{ color: 'var(--text-secondary)' }}>Lade Status...</p>
      ) : enabled ? (
        <div className="glass" style={{ padding: '30px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
            <div style={{ color: 'var(--color-success)' }}><ShieldCheck size={24} /></div>
            <div>
              <h3 style={{ fontSize: '1.1rem' }}>Zwei-Faktor-Authentifizierung ist aktiv</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Beim Anmelden wird zusätzlich ein Code aus deiner Authenticator-App verlangt.</p>
            </div>
          </div>

          {!showDisableForm ? (
            <button className="btn btn-danger" onClick={() => setShowDisableForm(true)}>
              2FA deaktivieren
            </button>
          ) : (
            <form onSubmit={handleDisable} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <div className="input-group">
                <label className="input-label" htmlFor="disable-password">Passwort zur Bestätigung</label>
                <div style={{ position: 'relative' }}>
                  <span style={{ position: 'absolute', left: '14px', top: '15px', color: 'var(--text-muted)' }}>
                    <Lock size={16} />
                  </span>
                  <input
                    id="disable-password"
                    type="password"
                    className="input-field"
                    value={disablePassword}
                    onChange={(e) => setDisablePassword(e.target.value)}
                    style={{ paddingLeft: '40px', width: '100%' }}
                  />
                </div>
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button type="submit" className="btn btn-danger">Endgültig deaktivieren</button>
                <button type="button" className="btn btn-secondary" onClick={() => { setShowDisableForm(false); setDisablePassword(''); }}>
                  Abbrechen
                </button>
              </div>
            </form>
          )}
        </div>
      ) : (
        <div className="glass" style={{ padding: '30px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
            <div style={{ color: 'var(--text-muted)' }}><KeyRound size={24} /></div>
            <div>
              <h3 style={{ fontSize: '1.1rem' }}>Zwei-Faktor-Authentifizierung ist inaktiv</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Aktiviere sie für zusätzlichen Schutz beim Login.</p>
            </div>
          </div>

          {!setupData ? (
            <button className="btn btn-primary" onClick={startSetup}>
              2FA einrichten
            </button>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                1. QR-Code mit deiner Authenticator-App scannen (oder den Schlüssel manuell eingeben).<br />
                2. Den 6-stelligen Code aus der App unten eingeben, um die Einrichtung abzuschließen.
              </p>

              <div
                style={{ background: '#fff', padding: '16px', borderRadius: '10px', width: 'fit-content' }}
                dangerouslySetInnerHTML={{ __html: setupData.qr_svg }}
              />

              <div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Manueller Schlüssel:</p>
                <code style={{ fontSize: '0.9rem', wordBreak: 'break-all', background: 'rgba(255,255,255,0.05)', padding: '8px 12px', borderRadius: '6px', display: 'block' }}>
                  {setupData.secret}
                </code>
              </div>

              <form onSubmit={confirmSetup} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                <div className="input-group">
                  <label className="input-label" htmlFor="confirm-code">Bestätigungscode</label>
                  <input
                    id="confirm-code"
                    type="text"
                    inputMode="numeric"
                    maxLength={6}
                    className="input-field"
                    placeholder="123456"
                    value={confirmCode}
                    onChange={(e) => setConfirmCode(e.target.value.replace(/\D/g, ''))}
                    style={{ width: '100%', textAlign: 'center', fontSize: '1.2rem', letterSpacing: '0.3em' }}
                  />
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button type="submit" className="btn btn-primary">Aktivieren</button>
                  <button type="button" className="btn btn-secondary" onClick={() => { setSetupData(null); setConfirmCode(''); }}>
                    Abbrechen
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
