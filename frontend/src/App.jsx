import React, { useState, useEffect } from 'react';

function SupplyCloset() {
  const [yarns, setYarns] = useState([]);
  const [color, setColor] = useState('');
  const [weight, setWeight] = useState('Worsted');
  const [texture, setTexture] = useState('Smooth');

  // Fetch all yarn from FastAPI when the page loads
  useEffect(() => {
    fetchYarnStash();
  }, []);

  const fetchYarnStash = async () => {
    const response = await fetch('http://127.0.0.1:8000/api/yarn');
    const data = await response.json();
    setYarns(data);
  };

  const handleYarnSubmit = async (e) => {
    e.preventDefault();
    await fetch('http://127.0.0.1:8000/api/yarn', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ color, weight, texture})
    });
    // Reset forms and refresh list
    setColor('');
    setWeight('');
    setTexture('');
    fetchYarnStash();
  };

  return (
    <div style={{ padding: '20px', backgroundColor: '#F4F1DE', fontFamily: '"Comic Sans MS", sans-serif' }}>
      <h2 style={{ color: '#3D405B' }}>🐱 Inside My Supply Closet</h2>
      
      {/* Pusheen Aesthetic Pastel Card */}
      <div style={{ backgroundColor: '#F2CC8F', padding: '20px', borderRadius: '15px', border: '3px solid #3D405B' }}>
        <h3>🧶 Add New Yarn</h3>
        <form onSubmit={handleYarnSubmit}>
          <input type="text" placeholder="Colorway" value={color} onChange={e => setColor(e.target.value)} required />
          <input type="text" placeholder="Worsted" value={weight} onChange={e => setWeight(e.target.value)} required />
          <input type="text" placeholder="Smooth" value={texture} onChange={e => setTexture(e.target.value)} required />

          <button type="submit" style={{ backgroundColor: '#E07A5F', color: 'white', borderRadius: '8px', padding: '5px 10px' }}>
            Stash Yarn
          </button>
        </form>
      </div>

      <h3 style={{ marginTop: '20px' }}>Current Inventory Vault</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
        {yarns.map(yarn => (
          <div key={yarn.id} style={{ background: 'white', border: '2px solid #3D405B', borderRadius: '10px', padding: '10px' }}>
            <h4>({yarn.color})</h4>
            <p>Weight: {yarn.weight} | Textures: {yarn.texture}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SupplyCloset;
//npm create vite@latest frontend -- --template react