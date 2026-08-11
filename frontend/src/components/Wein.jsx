import React, { useState, useEffect } from 'react';
import { Wine, Clock, Activity, Plus, Edit, Trash2, X, ChevronRight } from 'lucide-react';
import { apiFetch } from '../utils/api';

export default function Wein({ baseUrl, user, selectedPreloadWein, clearPreload }) {
  const [winesList, setWinesList] = useState([]);
  const [selectedWine, setSelectedWine] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Scaling state
  const [zielLiter, setZielLiter] = useState('');
  const [skalierteZutaten, setSkalierteZutaten] = useState([]);

  // Form state
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [formName, setFormName] = useState('');
  const [formLiter, setFormLiter] = useState('5');
  const [formIngredients, setFormIngredients] = useState('');
  const [formDesc, setFormDesc] = useState('');
  const [formInstructions, setFormInstructions] = useState('');
  const [formTime, setFormTime] = useState('8');
  const [formAlcohol, setFormAlcohol] = useState('15');

  const fetchWines = async () => {
    setLoading(true);
    try {
      const response = await apiFetch(`${baseUrl}/api/wein`);
      const data = await response.json();
      if (data.success) {
        setWinesList(data.wines);
        if (selectedPreloadWein) {
          const match = data.wines.find(w => w.id === selectedPreloadWein.id);
          if (match) handleSelectWine(match);
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
    fetchWines();
  }, [selectedPreloadWein]);

  const handleSelectWine = (item) => {
    setSelectedWine(item);
    setZielLiter(item.liter);
    setSkalierteZutaten(item.ingredients);
  };

  // Client-side quick scaling for wine
  useEffect(() => {
    if (!selectedWine || !zielLiter) return;
    const originalLiter = parseFloat(selectedWine.liter.toString().replace(',', '.')) || 1.0;
    const targetLiter = parseFloat(zielLiter.toString().replace(',', '.')) || 1.0;
    const factor = targetLiter / originalLiter;

    const scaled = selectedWine.ingredients.map(ingredient => {
      // Matches leading numbers like "5g", "500g", "1000g", "1.8", "1,8"
      const match = ingredient.match(/^(\d+([.,]\d+)?)\s*(.*)/);
      if (match) {
        const value = parseFloat(match[1].replace(',', '.'));
        const rest = match[3];
        const newValue = Math.round(value * factor * 100) / 100;
        const newValueStr = newValue.toString().replace('.', ',');
        return `${newValueStr} ${rest}`;
      }
      return ingredient;
    });

    setSkalierteZutaten(scaled);
  }, [zielLiter, selectedWine]);

  const handleEditClick = (e, item) => {
    e.stopPropagation();
    setEditId(item.id);
    setFormName(item.name);
    setFormLiter(item.liter.toString());
    setFormIngredients(item.ingredients.join(', '));
    setFormDesc(item.description || '');
    setFormInstructions(item.brewing_instructions || '');
    setFormTime(item.brewing_time.toString());
    setFormAlcohol(item.alcohol_content.toString());
    setShowForm(true);
  };

  const handleNewClick = () => {
    setEditId(null);
    setFormName('');
    setFormLiter('5');
    setFormIngredients('');
    setFormDesc('');
    setFormInstructions('');
    setFormTime('8');
    setFormAlcohol('15');
    setShowForm(true);
  };

  const handleDeleteClick = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm('Diesen Wein wirklich löschen?')) return;
    try {
      const response = await apiFetch(`${baseUrl}/api/wein/loeschen/${id}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        if (selectedWine && selectedWine.id === id) {
          setSelectedWine(null);
        }
        fetchWines();
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
      setError('Name darf nicht leer sein.');
      return;
    }
    const payload = {
      name: formName,
      liter: formLiter,
      ingredients: formIngredients.split(',').map(i => i.strip ? i.strip() : i.trim()).filter(Boolean),
      description: formDesc,
      brewing_instructions: formInstructions,
      brewing_time: parseInt(formTime) || 1,
      alcohol_content: parseFloat(formAlcohol) || 0.0
    };

    try {
      const url = editId ? `${baseUrl}/api/wein/${editId}` : `${baseUrl}/api/wein`;
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
        fetchWines();
      } else {
        setError(data.message || 'Speichern fehlgeschlagen.');
      }
    } catch (err) {
      setError('Netzwerkfehler.');
    }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <div>
          <h1 style={{ fontSize: '2.2rem' }}>Weine & Gebräue</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Verwalte deine Braurezepte, Met- und Fruchtweine.</p>
        </div>
        {(user.role === 'admin' || user.role === 'benutzer') && (
          <button onClick={handleNewClick} className="btn btn-primary">
            <Plus size={18} /> Wein hinzufügen
          </button>
        )}
      </div>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '12px 16px', borderRadius: '10px', color: '#f87171', marginBottom: '20px' }}>
          {error}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: selectedWine ? '1fr 1fr' : '1fr', gap: '30px', transition: 'all 0.3s ease' }}>
        
        {/* Left column: Wine Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {loading ? (
            <p>Lade Weine...</p>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: selectedWine ? '1fr' : 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
              {winesList.map((item) => (
                <div 
                  key={item.id} 
                  className="glass"
                  onClick={() => handleSelectWine(item)}
                  style={{ 
                    padding: '24px', 
                    cursor: 'pointer', 
                    transition: 'all 0.3s ease',
                    border: selectedWine?.id === item.id ? '1px solid rgba(233, 64, 87, 0.5)' : '1px solid var(--card-border)',
                    transform: selectedWine?.id === item.id ? 'scale(1.02)' : 'none'
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
                    {item.description || 'Keine Beschreibung vorhanden.'}
                  </p>
                  <div style={{ display: 'flex', gap: '15px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Clock size={14} /> {item.brewing_time} Wochen Gärzeit
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Activity size={14} /> {item.alcohol_content}% Vol.
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right column: Details Panel */}
        {selectedWine && (
          <div className="glass animate-fade-in" style={{ padding: '30px', height: 'fit-content', position: 'sticky', top: '100px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid var(--card-border)', paddingBottom: '10px' }}>
              <h2 style={{ fontSize: '1.6rem' }}>{selectedWine.name}</h2>
              <button onClick={() => setSelectedWine(null)} className="btn btn-secondary" style={{ padding: '6px' }}>
                <X size={18} />
              </button>
            </div>

            <p style={{ color: 'var(--text-secondary)', fontStyle: 'italic', marginBottom: '20px' }}>
              {selectedWine.description || 'Keine Beschreibung vorhanden.'}
            </p>

            <div style={{ display: 'flex', gap: '20px', marginBottom: '25px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(255,255,255,0.04)', padding: '6px 12px', borderRadius: '8px' }}>
                <Clock size={16} color="#e94057" />
                <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>Gärzeit: {selectedWine.brewing_time} Wochen</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(255,255,255,0.04)', padding: '6px 12px', borderRadius: '8px' }}>
                <Activity size={16} color="var(--color-success)" />
                <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>Alkohol: {selectedWine.alcohol_content}% Vol.</span>
              </div>
            </div>

            {/* Scale liters */}
            <div className="glass" style={{ padding: '20px', marginBottom: '25px', border: '1px solid rgba(233, 64, 87, 0.15)', background: 'rgba(233, 64, 87, 0.02)' }}>
              <h4 style={{ fontSize: '1rem', marginBottom: '10px' }}>Mengenrechner (Liter)</h4>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input 
                  type="number" 
                  className="input-field" 
                  value={zielLiter} 
                  onChange={(e) => setZielLiter(e.target.value)}
                  style={{ width: '80px', height: '40px' }}
                  min="1"
                />
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Liter Ansatzvolumen berechnen</span>
              </div>
            </div>

            {/* Ingredients */}
            <div style={{ marginBottom: '25px' }}>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '12px' }}>Zutaten ({zielLiter} Liter)</h3>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {skalierteZutaten.map((ingredient, idx) => (
                  <li key={idx} style={{ display: 'flex', alignItems: 'center', gap: '10px', borderBottom: '1px solid rgba(255,255,255,0.03)', paddingBottom: '6px' }}>
                    <ChevronRight size={14} color="#e94057" />
                    <span>{ingredient}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Brewing instructions */}
            <div>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '12px' }}>Herstellung / Brauanleitung</h3>
              <p style={{ color: 'var(--text-secondary)', whiteSpace: 'pre-wrap', lineHeight: '1.6', fontSize: '0.95rem' }}>
                {selectedWine.brewing_instructions || 'Keine Brauanleitung hinterlegt.'}
              </p>
            </div>
          </div>
        )}

      </div>

      {/* Editor Modal */}
      {showForm && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)',
          display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000,
          padding: '20px'
        }}>
          <div className="glass" style={{ width: '100%', maxWidth: '600px', padding: '30px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid var(--card-border)', paddingBottom: '10px' }}>
              <h2 style={{ fontSize: '1.4rem' }}>{editId ? 'Wein bearbeiten' : 'Neuen Wein eintragen'}</h2>
              <button onClick={() => setShowForm(false)} className="btn btn-secondary" style={{ padding: '6px' }}>
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleFormSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <div className="input-group">
                <label className="input-label" htmlFor="wine-name">Name des Weins</label>
                <input 
                  id="wine-name"
                  type="text" 
                  className="input-field" 
                  placeholder="z.B. Met traditionell"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px' }}>
                <div className="input-group">
                  <label className="input-label" htmlFor="wine-volume">Liter (Ansatz)</label>
                  <input 
                    id="wine-volume"
                    type="text" 
                    className="input-field" 
                    value={formLiter}
                    onChange={(e) => setFormLiter(e.target.value)}
                  />
                </div>
                <div className="input-group">
                  <label className="input-label" htmlFor="wine-time">Gärzeit (Wochen)</label>
                  <input 
                    id="wine-time"
                    type="number" 
                    className="input-field" 
                    value={formTime}
                    onChange={(e) => setFormTime(e.target.value)}
                  />
                </div>
                <div className="input-group">
                  <label className="input-label" htmlFor="wine-alcohol">Alkoholgehalt (%)</label>
                  <input 
                    id="wine-alcohol"
                    type="number" 
                    step="0.1"
                    className="input-field" 
                    value={formAlcohol}
                    onChange={(e) => setFormAlcohol(e.target.value)}
                  />
                </div>
              </div>

              <div className="input-group">
                <label className="input-label" htmlFor="wine-ingredients">Zutaten (Kommagetrennt)</label>
                <textarea 
                  id="wine-ingredients"
                  className="input-field" 
                  rows="3"
                  placeholder="1 Pack Weinhefe, 1800g Honig, Wasser..."
                  value={formIngredients}
                  onChange={(e) => setFormIngredients(e.target.value)}
                />
              </div>

              <div className="input-group">
                <label className="input-label" htmlFor="wine-desc">Kurzbeschreibung</label>
                <input 
                  id="wine-desc"
                  type="text" 
                  className="input-field" 
                  placeholder="Zusammenfassung des Geschmacks"
                  value={formDesc}
                  onChange={(e) => setFormDesc(e.target.value)}
                />
              </div>

              <div className="input-group">
                <label className="input-label" htmlFor="wine-instructions">Brauanleitung</label>
                <textarea 
                  id="wine-instructions"
                  className="input-field" 
                  rows="5"
                  placeholder="Utensilien desinfizieren, Hefe ansetzen, gären lassen..."
                  value={formInstructions}
                  onChange={(e) => setFormInstructions(e.target.value)}
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
