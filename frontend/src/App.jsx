import { useState } from 'react'
import './App.css'
import Home from './pages/Home'
import DiseaseForm from './components/DiseaseForm'
import ResultsDisplay from './components/ResultsDisplay'
import { HeartIcon } from '@heroicons/react/24/solid'

function App() {
  const [currentPage, setCurrentPage] = useState('home')
  const [selectedDisease, setSelectedDisease] = useState(null)
  const [results, setResults] = useState(null)

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
            <span className="logo-tag">v2.1</span>
          </a>
          <div className="nav-vitals">
            <div className="vital-item">
              <div className="vital-dot green"></div>
              <span>Models Active&nbsp;</span><span className="vital-val">6/6</span>
            </div>
            <div className="vital-item">
              <div className="vital-dot cyan"></div>
              <span>Assessments Today&nbsp;</span><span className="vital-val">1,247</span>
            </div>
            <div className="vital-item">
              <div className="vital-dot amber"></div>
              <span>Avg Accuracy&nbsp;</span><span className="vital-val">94.3%</span>
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
