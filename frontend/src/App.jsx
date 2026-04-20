import { useState, useEffect } from 'react'

import './App.css'
import Home from './pages/Home'
import DiseaseForm from './components/DiseaseForm'
import ResultsDisplay from './components/ResultsDisplay'
import { HeartIcon } from '@heroicons/react/24/solid'

function App() {
  const [currentPage, setCurrentPage] = useState('home')
  const [selectedDisease, setSelectedDisease] = useState(null)
  const [results, setResults] = useState(null)
  const [apiStatus, setApiStatus] = useState({ active: 0, total: 4, loading: true })

  useEffect(() => {
    checkHealth()
  }, [])

  const checkHealth = async () => {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    try {
      const start = Date.now()
      const response = await fetch(`${baseUrl}/health`)
      const data = await response.json()
      if (response.ok) {
        setApiStatus({ 
          active: 4, 
          total: 4, 
          loading: false,
          accuracy: '94.3%'
        })
      }
    } catch (err) {
      setApiStatus({ active: 0, total: 4, loading: false, error: true })
    }
  }

  const handleDiseaseSelect = (disease) => {
    setSelectedDisease(disease)
    setCurrentPage('form')
    setResults(null)
  }

  const handleBackHome = () => {
    setCurrentPage('home')
    setSelectedDisease(null)
    setResults(null)
  }

  const handleResultsReceived = (result) => {
    setResults(result)
    setCurrentPage('results')
  }

  return (
    <div className="app">
      <nav>
        <div className="nav-inner">
          <a className="nav-logo" href="#" onClick={handleBackHome}>
            <div className="logo-icon"><HeartIcon width={24} height={24} /></div>
            MediScan
            <span className="logo-tag">P-v2.1</span>
          </a>
          <div className="nav-vitals">
            <div className="vital-item">
              <div className={`vital-dot ${apiStatus.active > 0 ? 'green' : 'red'}`}></div>
              <span>Connection&nbsp;</span><span className="vital-val">{apiStatus.loading ? '...' : (apiStatus.active > 0 ? 'Online' : 'Offline')}</span>
            </div>
            <div className="vital-item">
              <div className="vital-dot cyan"></div>
              <span>Models&nbsp;</span><span className="vital-val">{apiStatus.active}/{apiStatus.total}</span>
            </div>
            <div className="vital-item">
              <div className="vital-dot amber"></div>
              <span>Platform&nbsp;</span><span className="vital-val">Production</span>
            </div>
          </div>

          <div className="nav-actions">
            <button className="btn-ghost">Patient History</button>
            <button className="btn-primary" onClick={() => handleDiseaseSelect('diabetes')}>+ New Report</button>
          </div>
        </div>
      </nav>

      {currentPage === 'home' && (
        <Home onSelectDisease={handleDiseaseSelect} />
      )}
      {currentPage === 'form' && selectedDisease && (
        <DiseaseForm
          disease={selectedDisease}
          onBack={handleBackHome}
          onResultsReceived={handleResultsReceived}
        />
      )}
      {currentPage === 'results' && results && (
        <ResultsDisplay
          results={results}
          onBack={handleBackHome}
        />
      )}

      <footer>
        <div className="footer-strip">
          <span>© 2025 MediScan — Health Risk Assessment Platform</span>
          <div className="footer-disclaimer">For informational use only. Not a substitute for professional medical diagnosis.</div>
          <span>Built with ML + <HeartIcon width={16} height={16} style={{display: 'inline', marginLeft: '4px'}} /></span>
        </div>
      </footer>
    </div>
  )
}

export default App
