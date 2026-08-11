import React, { useState, useEffect } from 'react';
import { BookOpen, Clock, Users, Plus, Edit, Trash2, X, ChevronRight, Calculator } from 'lucide-react';
import { apiFetch } from '../utils/api';

export default function Essen({ baseUrl, user, selectedPreloadEssen, clearPreload }) {
  const [essenList, setEssenList] = useState([]);
  const [selectedEssen, setSelectedEssen] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Portionsrechner state
  const [zielPortionen, setZielPortionen] = useState('');
  const [skalierteZutaten, setSkalierteZutaten] = useState([]);
  const [scalingLoading, setScalingLoading] = useState(false);

  // Form state
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [formName, setFormName] = useState('');
  const [formPersonen, setFormPersonen] = useState('4');
  const [formZutaten, setFormZutaten] = useState('');
  const [formDesc, setFormDesc] = useState('');
  const [formAnw, setFormAnw] = useState('');
  const [formZeit, setFormZeit] = useState('60');

  const fetchEssen = async () => {
    setLoading(true);
    try {
      const response = await apiFetch(`${baseUrl}/api/essen`);
      const data = await response.json();
      if (data.success) {
        setEssenList(data.essen);
        // Handle preloaded selection from search
        if (selectedPreloadEssen) {
          const match = data.essen.find(e => e.id === selectedPreloadEssen.id);
          if (match) handleSelectEssen(match);
          clearPreload();
        }
      } else {
        setError(data.message || 'Ladefehler');
      }
    } catch (err) {
      setError('Netzwerkfehler');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEssen();
  }, [selectedPreloadEssen]);

  const handleSelectEssen = (item) => {
    setSelectedEssen(item);
    setZielPortionen(item.personenanzahl);
    setSkalierteZutaten(item.zutaten);
    setError('');
  };

  const handleScaleZutaten = async (e) => {
    e.preventDefault();
    if (!zielPortionen || !selectedEssen) return;
    setScalingLoading(true);
    try {
      const response = await apiFetch(`${baseUrl}/api/essen/skalieren`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          zutaten: selectedEssen.zutaten,
          original_menge: selectedEssen.personenanzahl,
          ziel_menge: zielPortionen
        })
      });
      const data = await response.json();
      if (data.success) {
        setSkalierteZutaten(data.zutaten);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setScalingLoading(false);
    }
  };

  const handleEditClick = (e, item) => {
    e.stopPropagation();
    setEditId(item.id);
    setFormName(item.name);
    setFormPersonen(item.personenanzahl.toString());
    setFormZutaten(item.zutaten.join(', '));
    setFormDesc(item.description || '');
    setFormAnw(item.kochanweisung || '');
    setFormZeit(item.kochzeit_min.toString());
    setShowForm(true);
  };

  const handleNewClick = () => {
    setEditId(null);
    setFormName('');
    setFormPersonen('4');
    setFormZutaten('');
    setFormDesc('');
    setFormAnw('');
    setFormZeit('60');
    setShowForm(true);
  };

  const handleDeleteClick = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm('Dieses Rezept wirklich löschen?')) return;
    try {
      const response = await apiFetch(`${baseUrl}/api/essen/loeschen/${id}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        if (selectedEssen && selectedEssen.id === id) {
          setSelectedEssen(null);
        }
        fetchEssen();
      } else {
        setError(data.message || 'Löschen fehlgeschlagen.');
      }
    } catch (err) {
      setError('Netzwerkfehler.');
    }
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    if (!formName) {
      setError('Der Name darf nicht leer sein.');
      return;
    }
    const payload = {
      name: formName,
      personenanzahl: parseInt(formPersonen) || 1,
      zutaten: formZutaten.split(',').map(z => z.trim()).filter(Boolean),
      description: formDesc,
      kochanweisung: formAnw,
      kochzeit: parseInt(formZeit) || 0
    };

    try {
      const url = editId ? `${baseUrl}/api/essen/${editId}` : `${baseUrl}/api/essen`;
      const method = editId ? 'PUT' : 'POST';

      const response = await apiFetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      if (data.success) {
        setShowForm(false);
        setEditId(null);
        fetchEssen();
      } else {
        setError(data.message || 'Speichern fehlgeschlagen.');
      }
    } catch (err) {
      setError('Netzwerkfehler.');
    }
  };

  return (
    <div className="animate-fade-in">
      
      {/* Upper bar with creation button */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <div>
          <h1 style={{ fontSize: '2.2rem' }}>Speisen & Gerichte</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Finde und bearbeite köstliche Kochrezepte.</p>
        </div>
        {(user.role === 'admin' || user.role === 'benutzer') && (
          <button onClick={handleNewClick} className="btn btn-primary">
            <Plus size={18} /> Rezept erstellen
          </button>
        )}
      </div>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '12px 16px', borderRadius: '10px', color: '#f87171', marginBottom: '20px' }}>
          {error}
        </div>
      )}

      {/* Main Grid View */}
      <div style={{ display: 'grid', gridTemplateColumns: selectedEssen ? '1fr 1fr' : '1fr', gap: '30px', transition: 'all 0.3s ease' }}>
        
        {/* Left Side: Recipe Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {loading ? (
            <p>Lade Speisen...</p>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: selectedEssen ? '1fr' : 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
              {essenList.map((item) => (
                <div 
                  key={item.id} 
                  className={`glass ${selectedEssen?.id === item.id ? 'active-card' : ''}`}
                  onClick={() => handleSelectEssen(item)}
                  style={{ 
                    padding: '24px', 
                    cursor: 'pointer', 
                    transition: 'all 0.3s ease',
                    border: selectedEssen?.id === item.id ? '1px solid rgba(255, 107, 107, 0.5)' : '1px solid var(--card-border)',
                    transform: selectedEssen?.id === item.id ? 'scale(1.02)' : 'none'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                    <h3 style={{ fontSize: '1.2rem' }}>{item.name}</h3>
                    {(user.role === 'admin' || user.role === 'benutzer') && (
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button onClick={(e) => handleEditClick(e, item)} className="btn btn-secondary" style={{ padding: '6px' }}>
                          <Edit size={14} />
                        </button>
                        {user.role === 'admin' && (
                          <button onClick={(e) => handleDeleteClick(e, item.id)} className="btn btn-danger" style={{ padding: '6px' }}>
                            <Trash2 size={14} />
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '15px', display: '-webkit-box', WebkitLineClamp: '2', WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {item.description || 'Keine Beschreibung angegeben.'}
                  </p>
                  <div style={{ display: 'flex', gap: '15px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Clock size={14} /> {item.kochzeit}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Users size={14} /> {item.personenanzahl} Portionen
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Side: Detailed View */}
        {selectedEssen && (
          <div className="glass animate-fade-in" style={{ padding: '30px', height: 'fit-content', position: 'sticky', top: '100px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid var(--card-border)', paddingBottom: '10px' }}>
              <h2 style={{ fontSize: '1.6rem' }}>{selectedEssen.name}</h2>
              <button onClick={() => setSelectedEssen(null)} className="btn btn-secondary" style={{ padding: '6px' }}>
                <X size={18} />
              </button>
            </div>

            <p style={{ color: 'var(--text-secondary)', fontStyle: 'italic', marginBottom: '20px' }}>
              {selectedEssen.description || 'Keine Beschreibung angegeben.'}
            </p>

            <div style={{ display: 'flex', gap: '20px', marginBottom: '25px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(255,255,255,0.04)', padding: '6px 12px', borderRadius: '8px' }}>
                <Clock size={16} color="var(--color-warning)" />
                <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{selectedEssen.kochzeit}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(255,255,255,0.04)', padding: '6px 12px', borderRadius: '8px' }}>
                <Users size={16} color="var(--color-success)" />
                <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>Original: {selectedEssen.personenanzahl} Portionen</span>
              </div>
            </div>

            {/* Portionsrechner */}
            <div className="glass" style={{ padding: '20px', marginBottom: '25px', border: '1px solid rgba(255, 107, 107, 0.15)', background: 'rgba(255, 107, 107, 0.02)' }}>
              <h4 style={{ fontSize: '1rem', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Calculator size={16} /> Portionsrechner
              </h4>
              <form onSubmit={handleScaleZutaten} style={{ display: 'flex', gap: '10px' }}>
                <input 
                  type="number" 
                  className="input-field" 
                  value={zielPortionen} 
                  onChange={(e) => setZielPortionen(e.target.value)}
                  style={{ width: '80px', height: '40px' }}
                  min="1"
                />
                <button type="submit" className="btn btn-primary" style={{ padding: '8px 16px', fontSize: '0.85rem' }} disabled={scalingLoading}>
                  {scalingLoading ? 'Berechne...' : 'Umgerechnete Zutaten'}
                </button>
              </form>
            </div>

            {/* Ingredients */}
            <div style={{ marginBottom: '25px' }}>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '12px' }}>Zutaten ({zielPortionen} Portionen)</h3>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {skalierteZutaten.map((zutat, idx) => (
                  <li key={idx} style={{ display: 'flex', alignItems: 'center', gap: '10px', borderBottom: '1px solid rgba(255,255,255,0.03)', paddingBottom: '6px' }}>
                    <ChevronRight size={14} color="#ff6b6b" />
                    <span>{zutat}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Preparation instructions */}
            <div>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '12px' }}>Kochanweisung</h3>
              <p style={{ color: 'var(--text-secondary)', whiteSpace: 'pre-wrap', lineHeight: '1.6', fontSize: '0.95rem' }}>
                {selectedEssen.kochanweisung || 'Keine Kochanweisung hinterlegt.'}
              </p>
            </div>
          </div>
        )}

      </div>

      {/* Editor Modal Overlay */}
      {showForm && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)',
          display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000,
          padding: '20px'
        }}>
          <div className="glass" style={{ width: '100%', maxWidth: '600px', padding: '30px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid var(--card-border)', paddingBottom: '10px' }}>
              <h2 style={{ fontSize: '1.4rem' }}>{editId ? 'Rezept bearbeiten' : 'Neues Rezept hinzufügen'}</h2>
              <button onClick={() => setShowForm(false)} className="btn btn-secondary" style={{ padding: '6px' }}>
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleFormSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <div className="input-group">
                <label className="input-label" htmlFor="food-name">Name des Gerichts</label>
                <input 
                  id="food-name"
                  type="text" 
                  className="input-field" 
                  placeholder="z.B. Kaninchen mit Rosmarin"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div className="input-group">
                  <label className="input-label" htmlFor="food-portions">Personenanzahl (Portionen)</label>
                  <input 
                    id="food-portions"
                    type="number" 
                    className="input-field" 
                    value={formPersonen}
                    onChange={(e) => setFormPersonen(e.target.value)}
                  />
                </div>
                <div className="input-group">
                  <label className="input-label" htmlFor="food-time">Kochzeit (Minuten)</label>
                  <input 
                    id="food-time"
                    type="number" 
                    className="input-field" 
                    value={formZeit}
                    onChange={(e) => setFormZeit(e.target.value)}
                  />
                </div>
              </div>

              <div className="input-group">
                <label className="input-label" htmlFor="food-ingredients">Zutaten (Kommagetrennt)</label>
                <textarea 
                  id="food-ingredients"
                  className="input-field" 
                  rows="3"
                  placeholder="500g Fleisch, 2 Rosmarinzweige, Prise Salz..."
                  value={formZutaten}
                  onChange={(e) => setFormZutaten(e.target.value)}
                />
              </div>

              <div className="input-group">
                <label className="input-label" htmlFor="food-desc">Kurzbeschreibung</label>
                <input 
                  id="food-desc"
                  type="text" 
                  className="input-field" 
                  placeholder="Kurze Zusammenfassung für die Liste"
                  value={formDesc}
                  onChange={(e) => setFormDesc(e.target.value)}
                />
              </div>

              <div className="input-group">
                <label className="input-label" htmlFor="food-inst">Kochanweisung</label>
                <textarea 
                  id="food-inst"
                  className="input-field" 
                  rows="5"
                  placeholder="Vorbereitung, Backen, Braten..."
                  value={formAnw}
                  onChange={(e) => setFormAnw(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '15px' }}>
                <button type="button" onClick={() => setShowForm(false)} className="btn btn-secondary">
                  Abbrechen
                </button>
                <button type="submit" className="btn btn-primary">
                  Speichern
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
