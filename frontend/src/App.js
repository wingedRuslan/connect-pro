import React, { useState } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // API Call Logic
  const handleSubmit = async (e) => {
    e.preventDefault();               // Prevents page refresh on form submit
    setLoading(true);                 // Start loading
    setError('');                     // Clear any previous errors

    try {
      // Make API call to backend
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to analyze profile');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>LinkedIn Profile Analyzer</h1>
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter name, company, position..."
        />
        <button type="submit" disabled={loading || !query.trim()}>
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}
      
      {result && (
        <div className="result">
          <h2>Professional Summary</h2>
          <p>{result.insights.professional_summary}</p>
          
          <h2>Personal Background</h2>
          <p>{result.insights.personal_background}</p>
          
          <h2>Interesting Facts</h2>
          <ul>
            {result.insights.interesting_facts.map((fact, index) => (
              <li key={index}>{fact}</li>
            ))}
          </ul>
          
          <a href={result.profile_url} target="_blank" rel="noopener noreferrer">
            View LinkedIn Profile
          </a>
        </div>
      )}
    </div>
  );
}

export default App;
