import { useState } from 'react'
import './App.css'

function App() {
  // Defaulting to 2 (Critical) so you can see the new red styling immediately
  const [severity, setSeverity] = useState(2) 
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleOptimize = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('http://127.0.0.1:8000/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ case_severity: severity }),
      })

      if (!response.ok) throw new Error('Backend connection failed.')

      const data = await response.json()
      setTimeout(() => {
         setResult(data)
         setLoading(false)
      }, 800)
     
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  return (
    <div className="animated-bg">
      <div className="glass-panel">
        
        {/* HEADER */}
        <header className="brand-header">
          <div className="logo-glow"></div>
          <h1>SMART<span>DISPATCH</span></h1>
          <p>AI-Powered Emergency Routing</p>
        </header>

        {/* CONTROLS */}
        <div className="controls-container">
          <div className="input-group">
            <label>Patient Condition Parameter (3-Tier Protocol)</label>
            <select 
              value={severity} 
              onChange={(e) => setSeverity(parseInt(e.target.value))}
              className={`severity-level-${severity}`}
            >
              <option value={2}>🔴 Level 2 - CRITICAL TRAUMA</option>
              <option value={1}>🟠 Level 1 - MODERATE / URGENT</option>
              <option value={0}>🟢 Level 0 - MINOR / NON-EMERGENCY</option>
            </select>
          </div>
          <button 
            className="run-btn" 
            onClick={handleOptimize} 
            disabled={loading}
          >
            {loading ? 'Processing...' : 'INITIALIZE AI OPTIMIZATION'}
          </button>
        </div>

        {/* LOADING STATE */}
        {loading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Evaluating 1,500+ dispatch permutations...</p>
          </div>
        )}

        {/* ERROR STATE */}
        {error && <div className="error-state">⚠️ Connection Error: {error}</div>}

        {/* RESULTS */}
        {result && !loading && (
          <div className="results-container fade-in">
            <div className="results-header">
              <h2>Optimization Complete</h2>
              <div className="fitness-score">
                <span>Fitness</span>
                <strong>{result.dispatch_details.fitness_score}</strong>
              </div>
            </div>
            
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="icon-wrapper blue">🚑</div>
                <p className="label">Dispatched Unit</p>
                <p className="value">{result.dispatch_details.ambulance_id}</p>
              </div>
              
              <div className="metric-card">
                <div className="icon-wrapper red">🏥</div>
                <p className="label">Destination</p>
                <p className="value">{result.dispatch_details.hospital_id}</p>
              </div>
              
              <div className="metric-card">
                <div className="icon-wrapper purple">🗺️</div>
                <p className="label">Optimal Route</p>
                <p className="value">Path {result.dispatch_details.route_index}</p>
              </div>
            </div>

            {/* CONTEXT FOOTER */}
            <div className="context-bars">
              <div className="bar-group">
                <div className="bar-labels">
                  <span>Traffic Density</span>
                  <span>{Number(result.environment_context.traffic_level).toFixed(2)}x</span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill yellow" style={{width: `${Number(result.environment_context.traffic_level) * 30}%`}}></div>
                </div>
              </div>
              
              <div className="bar-group">
                <div className="bar-labels">
                  <span>Weather Impact</span>
                  <span>{Number(result.environment_context.weather_severity).toFixed(2)}x</span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill blue" style={{width: `${Number(result.environment_context.weather_severity) * 30}%`}}></div>
                </div>
              </div>
            </div>
            
          </div>
        )}
      </div>
    </div>
  )
}

export default App