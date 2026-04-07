import { useState, useRef } from 'react'
import './App.css'
import LiveMap from './LiveMap'

function App() {
  const [severity, setSeverity] = useState(2)
  const [imageFile, setImageFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [showMap, setShowMap] = useState(false)
  const fileInputRef = useRef(null)

  const handleOptimize = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      let response;

      // MODE 1: VISION AI UPLOAD
      if (imageFile) {
        const formData = new FormData()
        formData.append('file', imageFile)

        response = await fetch('http://127.0.0.1:8000/optimize-with-vision', {
          method: 'POST',
          body: formData, 
        })
      } 
      // MODE 2: MANUAL TRIAGE
      else {
        response = await fetch('http://127.0.0.1:8000/optimize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ case_severity: severity }),
        })
      }

      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail || 'Backend connection failed.')
      }

      const data = await response.json()
      
      if (data.status === 'rejected') {
        throw new Error(data.message)
      }

      setTimeout(() => {
         setResult(data)
         setLoading(false)
      }, 800)
     
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setImageFile(e.target.files[0])
    }
  }

  const clearImage = () => {
    setImageFile(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div 
      className="animated-bg"
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        width: '100vw',
        position: 'absolute',
        top: 0,
        left: 0,
        margin: 0,
        padding: 0
      }}>
      {/* Conditional Rendering. If showMap is false, show dashboard. */}
      {!showMap ? (
        <div className="dashboard-panel">
          
          <header className="brand-header">
            <div className="logo-glow"></div>
            <h1>SMART<span>DISPATCH</span></h1>
            <p>AI-Powered Emergency Routing</p>
          </header>

          <div className="controls-container">
            <div className="input-group" style={{ opacity: imageFile ? 0.4 : 1, pointerEvents: imageFile ? 'none' : 'auto' }}>
              <label>Manual Condition Parameter</label>
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

            <div className="divider">OR</div>

            <div className="input-group">
              <label>AI Vision Auto-Triage</label>
              <div className={`file-upload-zone ${imageFile ? 'active' : ''}`}>
                <input 
                  type="file" 
                  accept="image/*" 
                  onChange={handleFileChange} 
                  ref={fileInputRef}
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="file-label">
                  {imageFile ? `📸 ${imageFile.name}` : '📁 Upload Accident Image'}
                </label>
                {imageFile && (
                  <button className="clear-img-btn" onClick={clearImage}>✕</button>
                )}
              </div>
            </div>

            <button className="run-btn" onClick={handleOptimize} disabled={loading}>
              {loading ? 'Processing ML Pipeline...' : (imageFile ? 'RUN VISION AI + ROUTING' : 'INITIALIZE OPTIMIZATION')}
            </button>
          </div>

          {loading && (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>{imageFile ? 'Analyzing image and calculating route...' : 'Evaluating dispatch permutations...'}</p>
            </div>
          )}
          
          {error && <div className="error-state">⚠️ {error}</div>}

          {result && !loading && (
            <div className="results-container fade-in">
              <div className="results-header">
                <h2>Optimization Complete</h2>
                <div className="fitness-score">
                  <span>Fitness</span>
                  <strong>{result.dispatch_details.fitness_score}</strong>
                </div>
              </div>
              
              {result.vision_analysis && (
                <div className="vision-badge">
                  <span>👁️ Vision AI Diagnosis: </span>
                  <strong>Level {result.vision_analysis.severity_level}</strong> 
                  <span className="conf">({result.vision_analysis.confidence}% Conf)</span>
                </div>
              )}

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

              {/* The toggle button to open the map */}
              <button 
                className="run-btn" 
                onClick={() => setShowMap(true)} 
                style={{ marginTop: '20px', backgroundColor: '#10b981', boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)' }}
              >
                🗺️ TRACK AMBULANCE ON LIVE MAP
              </button>
              
            </div>
          )}
        </div>
      ) : (
        /* Fullscreen Map View Container */
        <div className="map-view-container" style={{ position: 'relative', width: '100%', height: '100vh' }}>
          
          <button 
            onClick={() => setShowMap(false)}
            style={{
              position: 'absolute',
              top: '20px',
              right: '20px',
              zIndex: 9999, // Keeps it above the Leaflet map layers
              padding: '10px 20px',
              background: '#f43f5e',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 'bold',
              boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
            }}
          >
            ✖ CLOSE MAP
          </button>

          <LiveMap />
        </div>
      )}
    </div>
  )
}

export default App