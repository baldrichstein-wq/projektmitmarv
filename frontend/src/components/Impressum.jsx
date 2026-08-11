import React from 'react';
import { Info, Mail } from 'lucide-react';

export default function Impressum() {
  const contacts = [
    { name: 'Stefan K.', email: 'stefan.kallinich@student.syntax-institut.de' },
    { name: 'David L.', email: 'David.Ludwig@student.syntax-institut.de' },
  ];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      <div className="glass" style={{ padding: '40px' }}>
        <h1 style={{ fontSize: '2.2rem', marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Info size={26} /> Impressum
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', lineHeight: '1.7', marginBottom: '10px' }}>
          Dieses Rezeptbuch- & Braumeister-Portal ist ein nicht-kommerzielles Schulprojekt
          (Sprint-Simulations-Projekt) ohne Gewinnerzielungsabsicht, das ausschließlich zu
          Lern- und Demonstrationszwecken betrieben wird. Es werden keine Waren oder
          Dienstleistungen angeboten oder verkauft.
        </p>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.6' }}>
          Da es sich um kein geschäftsmäßiges Telemedienangebot im Sinne von §5 DDG
          (vormals TMG) handelt, besteht keine Impressumspflicht. Aus Transparenzgründen
          nennen wir dennoch freiwillig Kontaktmöglichkeiten zu den Projektverantwortlichen.
        </p>
      </div>

      <div>
        <h2 style={{ fontSize: '1.6rem', marginBottom: '20px' }}>Kontakt</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
          {contacts.map((person) => (
            <div key={person.email} className="glass" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ color: 'var(--text-secondary)' }}>
                <Mail size={22} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.1rem', marginBottom: '2px' }}>{person.name}</h3>
                <a href={`mailto:${person.email}`} style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                  {person.email}
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="glass" style={{ padding: '30px' }}>
        <h3 style={{ marginBottom: '15px' }}>Haftungshinweis</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: '1.7' }}>
          Trotz sorgfältiger inhaltlicher Kontrolle übernehmen wir keine Haftung für die
          Inhalte externer Links. Für den Inhalt der verlinkten Seiten sind ausschließlich
          deren Betreiber verantwortlich. Dieses Projekt entstand im Rahmen einer
          Ausbildungsmaßnahme und erhebt keinen Anspruch auf dauerhafte Verfügbarkeit.
        </p>
      </div>
    </div>
  );
}
