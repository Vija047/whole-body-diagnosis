import { useState } from 'react'
import '../styles/DiseaseForm.css'

const diseaseConfigs = {
  diabetes: {
    name: 'Diabetes',
    fields: [
      { label: 'HbA1c Level (%)', name: 'hbA1c_level', placeholder: '4.0 - 15.0', type: 'number', step: '0.1', min: '4', max: '15' },
      { label: 'Glucose Level (mg/dL)', name: 'blood_glucose_level', placeholder: '70 - 400', type: 'number', step: '1', min: '70', max: '400' },
      { label: 'Age (years)', name: 'age', placeholder: '1 - 120', type: 'number', step: '1', min: '1', max: '120' }
    ],
    apiEndpoint: '/predict/diabetes'
  },
  ckd: {
    name: 'Chronic Kidney Disease',
    fields: [
      { label: 'Age (years)', name: 'age', placeholder: '1 - 120', type: 'number', step: '0.1', min: '1', max: '120' },
      { label: 'Hemoglobin (g/dL)', name: 'hemo', placeholder: '3.0 - 20.0', type: 'number', step: '0.1', min: '3', max: '20' },
      { label: 'PCV (%)', name: 'pcv', placeholder: '10 - 55', type: 'number', step: '0.1', min: '10', max: '55' },
      { label: 'RBC Count (millions/µL)', name: 'rbcc', placeholder: '2.0 - 8.0', type: 'number', step: '0.1', min: '2', max: '8' },
      { label: 'Serum Creatinine (mg/dL)', name: 'sc', placeholder: '0.5 - 10.0', type: 'number', step: '0.1', min: '0.5', max: '10' }
    ],
    apiEndpoint: '/predict/ckd'
  },
  cld: {
    name: 'Chronic Liver Disease',
    fields: [
      { label: 'Alkaline Phosphatase (IU/L)', name: 'alkphos', placeholder: '30 - 500', type: 'number', step: '1', min: '30', max: '500' },
      { label: 'SGOT (IU/L)', name: 'sgot', placeholder: '10 - 300', type: 'number', step: '1', min: '10', max: '300' },
      { label: 'SGPT (IU/L)', name: 'sgpt', placeholder: '5 - 300', type: 'number', step: '1', min: '5', max: '300' },
      { label: 'Total Bilirubin (mg/dL)', name: 'total_bilirubin', placeholder: '0.1 - 20.0', type: 'number', step: '0.1', min: '0.1', max: '20' },
      { label: 'Total Proteins (g/dL)', name: 'total_proteins', placeholder: '4.0 - 10.0', type: 'number', step: '0.1', min: '4', max: '10' },
      { label: 'Albumin (g/dL)', name: 'albumin', placeholder: '2.0 - 6.0', type: 'number', step: '0.1', min: '2', max: '6' }
    ],
    apiEndpoint: '/predict/cld'
  },
  heart: {
    name: 'Heart Disease',
    fields: [
      { label: 'Age (years)', name: 'age', placeholder: '1 - 120', type: 'number', step: '1', min: '1', max: '120' },
      { label: 'Cholesterol (mg/dL)', name: 'chol', placeholder: '100 - 400', type: 'number', step: '1', min: '100', max: '400' },
      { label: 'Resting Blood Pressure (mmHg)', name: 'trestbps', placeholder: '80 - 200', type: 'number', step: '1', min: '80', max: '200' },
      { label: 'Chest Pain Type (0-3)', name: 'cp', placeholder: '0 - 3', type: 'number', step: '1', min: '0', max: '3' },
      { label: 'Max Heart Rate (bpm)', name: 'thalachh', placeholder: '60 - 220', type: 'number', step: '1', min: '60', max: '220' }
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
        // Handle Pydantic validation errors (often objects or arrays)
        const errorDetail = typeof data.detail === 'string' 
          ? data.detail 
          : Array.isArray(data.detail)
            ? data.detail.map(err => `${err.loc[1]}: ${err.msg}`).join(', ')
            : 'Unprocessable input. Please check your data.'
        setError(errorDetail)
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
