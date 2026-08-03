import React, { useState, useEffect } from 'react';
import { Search as SearchIcon, BookOpen, Wine, Sparkles } from 'lucide-react';

export default function Search({ baseUrl, onSelectEssen, onSelectWein }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState({ weine: [], speisen: [] });

  const handleSearch = async (searchQuery) => {
    if (!searchQuery.trim()) {
      setResults({ weine: [], speisen: [] });
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(`${baseUrl}/api/suche?q=${encodeURIComponent(searchQuery)}`);
      const data = await response.json();
      if (data.success) {
        setResults({ weine: data.weine || [], speisen: data.speisen || [] });
      }
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      handleSearch(query);
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [query]);

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      
      {/* Search Input Card */}
      <div className="glass" style={{ padding: '30px' }}>
        <h2 style={{ fontSize: '1.6rem', marginBottom: '15px' }}>Globale Rezeptsuche</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '20px' }}>
          Suche nach Name, Beschreibung oder Zutaten von Gerichten und Weinen.
        </p>

        <div style={{ position: 'relative' }}>
          <span style={{ position: 'absolute', left: '16px', top: '15px', color: 'var(--text-muted)' }}>
            <SearchIcon size={20} />
          </span>
          <input 
            type="text" 
            className="input-field" 
            placeholder="z.B. Rosmarin, Weinhefe, Kaninchen..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ width: '100%', paddingLeft: '48px', fontSize: '1.05rem', height: '50px' }}
          />
        </div>
      </div>

      {/* Results Section */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
          Wird gesucht...
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
          
          {/* Meals Results */}
          {query.trim() && (
            <div>
              <h3 style={{ fontSize: '1.3rem', marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BookOpen size={20} color="#ff6b6b" /> Speisen ({results.speisen.length})
              </h3>
              
              {results.speisen.length > 0 ? (
                <div className="card-grid" style={{ marginTop: '0' }}>
                  {results.speisen.map((item) => (
                    <div 
                      key={`essen-${item.id}`} 
                      className="glass" 
                      style={{ padding: '24px', cursor: 'pointer', transition: 'transform 0.2s' }}
                      onClick={() => onSelectEssen(item)}
                    >
                      <h4 style={{ fontSize: '1.1rem', marginBottom: '8px' }}>{item.name}</h4>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '12px', display: '-webkit-box', WebkitLineClamp: '2', WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                        {item.description || 'Keine Beschreibung vorhanden.'}
                      </p>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span className="badge">{item.kochzeit}</span>
                        <span className="badge">{item.personenanzahl} Portionen</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Keine Speisen gefunden.</p>
              )}
            </div>
          )}

          {/* Wines Results */}
          {query.trim() && (
            <div>
              <h3 style={{ fontSize: '1.3rem', marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Wine size={20} color="#e94057" /> Weine ({results.weine.length})
              </h3>

              {results.weine.length > 0 ? (
                <div className="card-grid" style={{ marginTop: '0' }}>
                  {results.weine.map((item) => (
                    <div 
                      key={`wein-${item.id}`} 
                      className="glass" 
                      style={{ padding: '24px', cursor: 'pointer', transition: 'transform 0.2s' }}
                      onClick={() => onSelectWein(item)}
                    >
                      <h4 style={{ fontSize: '1.1rem', marginBottom: '8px' }}>{item.name}</h4>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '12px', display: '-webkit-box', WebkitLineClamp: '2', WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                        {item.description || 'Keine Beschreibung vorhanden.'}
                      </p>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span className="badge">{item.alcohol_content}% Vol.</span>
                        <span className="badge">{item.liter} Liter</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Keine Weine gefunden.</p>
              )}
            </div>
          )}

          {!query.trim() && (
            <div className="glass" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <Sparkles size={24} style={{ marginBottom: '10px', color: 'var(--color-warning)' }} />
              <p>Tippe etwas ein, um die Live-Suche zu starten!</p>
            </div>
          )}

        </div>
      )}

    </div>
  );
}
