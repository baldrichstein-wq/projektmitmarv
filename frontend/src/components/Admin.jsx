import React, { useState, useEffect } from 'react';
import { ShieldAlert, Trash2, UserPlus, Users } from 'lucide-react';

export default function Admin({ baseUrl }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form states for creating a new user
  const [newName, setNewName] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newRole, setNewRole] = useState('benutzer');

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${baseUrl}/api/benutzer`);
      const data = await response.json();
      if (data.success) {
        setUsers(data.users);
      } else {
        setError(data.message || 'Fehler beim Laden der Benutzer.');
      }
    } catch (err) {
      setError('Netzwerkfehler beim Laden der Benutzer.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleRoleChange = async (userId, role) => {
    setError('');
    setSuccess('');
    try {
      const response = await fetch(`${baseUrl}/api/benutzer/rolle_aendern/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rolle: role })
      });
      const data = await response.json();
      if (data.success) {
        setSuccess(data.message);
        fetchUsers();
      } else {
        setError(data.message || 'Fehler beim Ändern der Rolle.');
      }
    } catch (err) {
      setError('Netzwerkfehler.');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Möchten Sie diesen Benutzer wirklich löschen?')) return;
    setError('');
    setSuccess('');
    try {
      const response = await fetch(`${baseUrl}/api/benutzer/loeschen/${userId}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        setSuccess(data.message);
        fetchUsers();
      } else {
        setError(data.message || 'Fehler beim Löschen.');
      }
    } catch (err) {
      setError('Netzwerkfehler.');
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!newName || !newEmail || !newPassword) {
      setError('Bitte alle Felder ausfüllen.');
      return;
    }
    try {
      const response = await fetch(`${baseUrl}/api/benutzer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newName, email: newEmail, password: newPassword, role: newRole })
      });
      const data = await response.json();
      if (data.success) {
        setSuccess(data.message);
        setNewName('');
        setNewEmail('');
        setNewPassword('');
        setNewRole('benutzer');
        fetchUsers();
      } else {
        setError(data.message || 'Fehler beim Anlegen des Benutzers.');
      }
    } catch (err) {
      setError('Netzwerkfehler.');
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      <div className="glass" style={{ padding: '30px' }}>
        <h2 style={{ fontSize: '1.6rem', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Users size={24} /> Admin-Bereich: Benutzerverwaltung
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Hier können Sie Benutzer löschen, neue Konten anlegen und Berechtigungsstufen verwalten.
        </p>
      </div>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '12px 16px', borderRadius: '10px', color: '#f87171' }}>
          {error}
        </div>
      )}

      {success && (
        <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '12px 16px', borderRadius: '10px', color: '#34d399' }}>
          {success}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '30px' }}>
        
        {/* User List */}
        <div className="glass" style={{ padding: '30px', overflowX: 'auto' }}>
          <h3 style={{ fontSize: '1.25rem', marginBottom: '20px' }}>Registrierte Benutzer</h3>
          {loading ? (
            <p style={{ color: 'var(--text-secondary)' }}>Lade Benutzer...</p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--card-border)', color: 'var(--text-secondary)' }}>
                  <th style={{ padding: '12px' }}>ID</th>
                  <th style={{ padding: '12px' }}>Name</th>
                  <th style={{ padding: '12px' }}>E-Mail</th>
                  <th style={{ padding: '12px' }}>Rolle</th>
                  <th style={{ padding: '12px', textAlign: 'right' }}>Aktionen</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                    <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>{u.id}</td>
                    <td style={{ padding: '12px', fontWeight: 600 }}>{u.name}</td>
                    <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>{u.email}</td>
                    <td style={{ padding: '12px' }}>
                      <select 
                        value={u.role} 
                        onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        style={{ 
                          background: 'rgba(255,255,255,0.05)', 
                          color: '#fff', 
                          border: '1px solid var(--card-border)', 
                          borderRadius: '6px',
                          padding: '4px 8px',
                          outline: 'none'
                        }}
                      >
                        <option value="gast" style={{ background: 'var(--bg-dark)' }}>Gast</option>
                        <option value="benutzer" style={{ background: 'var(--bg-dark)' }}>Benutzer</option>
                        <option value="admin" style={{ background: 'var(--bg-dark)' }}>Admin</option>
                      </select>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>
                      <button 
                        onClick={() => handleDeleteUser(u.id)} 
                        className="btn btn-danger" 
                        style={{ padding: '6px 10px', fontSize: '0.8rem' }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Create User Form */}
        <div className="glass" style={{ padding: '30px' }}>
          <h3 style={{ fontSize: '1.25rem', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <UserPlus size={20} /> Neuen Benutzer anlegen
          </h3>
          <form onSubmit={handleCreateUser} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
            <div className="input-group">
              <label className="input-label" htmlFor="admin-new-name">Name</label>
              <input 
                id="admin-new-name"
                type="text" 
                className="input-field" 
                placeholder="Name" 
                value={newName} 
                onChange={(e) => setNewName(e.target.value)} 
              />
            </div>
            <div className="input-group">
              <label className="input-label" htmlFor="admin-new-email">E-Mail</label>
              <input 
                id="admin-new-email"
                type="email" 
                className="input-field" 
                placeholder="E-Mail" 
                value={newEmail} 
                onChange={(e) => setNewEmail(e.target.value)} 
              />
            </div>
            <div className="input-group">
              <label className="input-label" htmlFor="admin-new-password">Passwort</label>
              <input 
                id="admin-new-password"
                type="password" 
                className="input-field" 
                placeholder="Passwort" 
                value={newPassword} 
                onChange={(e) => setNewPassword(e.target.value)} 
              />
            </div>
            <div className="input-group">
              <label className="input-label" htmlFor="admin-new-role">Rolle</label>
              <select 
                id="admin-new-role"
                value={newRole} 
                onChange={(e) => setNewRole(e.target.value)}
                className="input-field"
                style={{ height: '47px' }}
              >
                <option value="gast" style={{ background: 'var(--bg-dark)' }}>Gast</option>
                <option value="benutzer" style={{ background: 'var(--bg-dark)' }}>Benutzer</option>
                <option value="admin" style={{ background: 'var(--bg-dark)' }}>Admin</option>
              </select>
            </div>
            <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'flex-end' }}>
              <button type="submit" className="btn btn-primary" style={{ padding: '12px 24px' }}>
                Benutzer erstellen
              </button>
            </div>
          </form>
        </div>

      </div>
    </div>
  );
}
