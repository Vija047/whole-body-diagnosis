import '../styles/ResultsDisplay.css'
import { CheckCircleIcon, ClipboardDocumentIcon, SparklesIcon, ChartBarIcon, FireIcon, EllipsisHorizontalIcon, CalendarIcon } from '@heroicons/react/24/solid'

export default function ResultsDisplay({ results, onBack }) {
  const isPositive = results.result === 'Positive'
  const probability = results.probability

  return (
    <div className="results-container">
      <button className="back-btn" onClick={onBack}>← Back</button>

      <div className="results-card">
        <h2 className="results-title">{results.disease}</h2>
        <p className="results-subtitle">Assessment Complete</p>

        <div className={`result-badge ${isPositive ? 'positive' : 'negative'}`}>
          <div className="result-icon">
            {isPositive ? <CheckCircleIcon width={32} height={32} /> : <CheckCircleIcon width={32} height={32} />}
          </div>
          <div className="result-text">
            <p className="result-status">{results.result}</p>
            <p className="result-description">
              {isPositive 
                ? 'Risk indicator detected' 
                : 'No risk indicator detected'}
            </p>
          </div>
        </div>

        <div className="probability-section">
          <h3>Risk Probability</h3>
          <div className="probability-bar">
            <div 
              className="probability-fill"
              style={{ 
                width: `${probability}%`,
                backgroundColor: probability > 70 ? '#FF6B6B' : probability > 40 ? '#FFE66D' : '#2ECC71'
              }}
            />
          </div>
          <p className="probability-text">{probability}% Risk Score</p>
        </div>

        <div className="recommendations">
          <h3>Recommendations</h3>
          <ul>
            {isPositive ? (
              <>
                <li><SparklesIcon width={20} height={20} /> Schedule a consultation with a healthcare professional</li>
                <li><ClipboardDocumentIcon width={20} height={20} /> Discuss results with your doctor for further evaluation</li>
                <li><CheckCircleIcon width={20} height={20} /> Follow medical advice and treatment plans</li>
                <li><ChartBarIcon width={20} height={20} /> Monitor health metrics regularly</li>
              </>
            ) : (
              <>
                <li><CheckCircleIcon width={20} height={20} /> Continue maintaining healthy lifestyle habits</li>
                <li><FireIcon width={20} height={20} /> Stay physically active and exercise regularly</li>
                <li><EllipsisHorizontalIcon width={20} height={20} /> Maintain a balanced and nutritious diet</li>
                <li><CalendarIcon width={20} height={20} /> Get regular health check-ups annually</li>
              </>
            )}
          </ul>
        </div>

        <div className="disclaimer">
          <p>
            <strong>Disclaimer:</strong> This assessment is for informational purposes only and 
            should not be considered as medical advice. Always consult with qualified healthcare 
            professionals for proper diagnosis and treatment.
          </p>
        </div>

        <button className="new-assessment-btn" onClick={onBack}>
          New Assessment
        </button>
      </div>
    </div>
  )
}
