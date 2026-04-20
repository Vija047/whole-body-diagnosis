import { useState } from 'react'
import '../styles/DiseaseForm.css'

const diseaseConfigs = {
  diabetes: {
    name: 'Diabetes',
    fields: [
      { label: 'HbA1c Level (%)', name: 'hba1c', placeholder: 'Enter HbA1c', type: 'number', step: '0.1' },
      { label: 'Glucose Level (mg/dL)', name: 'glucose', placeholder: 'Enter glucose', type: 'number', step: '1' },
      { label: 'Age (years)', name: 'age', placeholder: 'Enter age', type: 'number', step: '1' }
    ],
    apiEndpoint: '/predict/diabetes'
  },
  ckd: {
    name: 'Chronic Kidney Disease',
    fields: [
      { label: 'Age (years)', name: 'age', placeholder: 'Enter age', type: 'number', step: '0.1' },
      { label: 'Hemoglobin (g/dL)', name: 'hemo', placeholder: 'Hemoglobin level', type: 'number', step: '0.1' },
      { label: 'PCV (%)', name: 'pcv', placeholder: 'Packed Cell Volume', type: 'number', step: '0.1' },
      { label: 'RBC Count (millions/µL)', name: 'rbcc', placeholder: 'RBC Count', type: 'number', step: '0.1' },
      { label: 'Serum Creatinine (mg/dL)', name: 'sc', placeholder: 'Serum Creatinine', type: 'number', step: '0.1' }
    ],
    apiEndpoint: '/predict/ckd'
  },
  cld: {
    name: 'Chronic Liver Disease',
    fields: [
      { label: 'Alkaline Phosphatase (IU/L)', name: 'alkphos', placeholder: 'Alkaline Phosphatase', type: 'number', step: '1' },
      { label: 'SGOT (IU/L)', name: 'sgot', placeholder: 'SGOT level', type: 'number', step: '1' },
      { label: 'SGPT (IU/L)', name: 'sgpt', placeholder: 'SGPT level', type: 'number', step: '1' },
      { label: 'Total Bilirubin (mg/dL)', name: 'total_bilirubin', placeholder: 'Total Bilirubin', type: 'number', step: '0.1' },
      { label: 'Total Proteins (g/dL)', name: 'total_proteins', placeholder: 'Total Proteins', type: 'number', step: '0.1' },
      { label: 'Albumin (g/dL)', name: 'albumin', placeholder: 'Albumin level', type: 'number', step: '0.1' }
    ],
    apiEndpoint: '/predict/cld'
  },
  heart: {
    name: 'Heart Disease',
    fields: [
      { label: 'Age (years)', name: 'age', placeholder: 'Enter age', type: 'number', step: '1' },
      { label: 'Cholesterol (mg/dL)', name: 'chol', placeholder: 'Cholesterol level', type: 'number', step: '1' },
      { label: 'Resting Blood Pressure (mmHg)', name: 'trestbps', placeholder: 'Blood pressure', type: 'number', step: '1' },
      { label: 'Chest Pain Type (0-3)', name: 'cp', placeholder: 'Chest pain type', type: 'number', step: '1', min: '0', max: '3' },
      { label: 'Max Heart Rate (bpm)', name: 'thalachh', placeholder: 'Max heart rate', type: 'number', step: '1' }
    ],
    apiEndpoint: '/predict/heart'
  }
}

export default function DiseaseForm({ disease, onBack, onResultsReceived }) {
  const config = diseaseConfigs[disease]
  const [formData, setFormData] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: parseFloat(value)
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const apiKey = import.meta.env.VITE_API_KEY || 'dev-key-change-in-production'

    try {
      const response = await fetch(`${baseUrl}${config.apiEndpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey
        },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (response.ok) {
        onResultsReceived(data)
      } else {
        setError(data.detail || 'An error occurred')
      }
    } catch (err) {
      setError(`Failed to connect to API. Please make sure the backend is running at ${baseUrl}`)
    } finally {
      setLoading(false)
    }
  }


  return (
    <div className="form-container">
      <button className="back-btn" onClick={onBack}>← Back</button>
      
      <div className="form-card">
        <h2 className="form-title">{config.name} Assessment</h2>
        <p className="form-subtitle">Please fill in the medical parameters</p>

        <form onSubmit={handleSubmit} className="disease-form">
          <div className="fields-grid">
            {config.fields.map((field) => (
              <div key={field.name} className="form-group">
                <label htmlFor={field.name} className="form-label">
                  {field.label}
                </label>
                <input
                  type={field.type}
                  id={field.name}
                  name={field.name}
                  placeholder={field.placeholder}
                  step={field.step}
                  min={field.min}
                  max={field.max}
                  value={formData[field.name] || ''}
                  onChange={handleChange}
                  required
                  className="form-input"
                />
              </div>
            ))}
          </div>

          {error && <div className="error-message">{error}</div>}

          <button 
            type="submit" 
            className="submit-btn"
            disabled={loading}
          >
            {loading ? 'Analyzing...' : 'Get Assessment'}
          </button>
        </form>
      </div>
    </div>
  )
}
