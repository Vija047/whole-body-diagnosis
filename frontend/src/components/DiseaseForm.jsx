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
    apiEndpoint: '/api/diabetes'
  },
  ckd: {
    name: 'Chronic Kidney Disease',
    fields: [
      { label: 'PCV (%)', name: 'pcv', placeholder: 'Packed Cell Volume', type: 'number', step: '0.1' },
      { label: 'Specific Gravity', name: 'sg', placeholder: 'Specific Gravity', type: 'number', step: '0.001' },
      { label: 'Hemoglobin (g/dL)', name: 'hemo', placeholder: 'Hemoglobin level', type: 'number', step: '0.1' },
      { label: 'Albumin (g/dL)', name: 'al', placeholder: 'Albumin level', type: 'number', step: '0.1' },
      { label: 'Serum Creatinine (mg/dL)', name: 'sc', placeholder: 'Serum Creatinine', type: 'number', step: '0.1' },
      { label: 'RBC Count (millions/cmm)', name: 'rbcc', placeholder: 'RBC Count', type: 'number', step: '0.1' },
      { label: 'Blood Glucose Random (mg/dL)', name: 'bgr', placeholder: 'Blood Glucose Random', type: 'number', step: '1' }
    ],
    apiEndpoint: '/api/ckd'
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
    apiEndpoint: '/api/cld'
  },
  heart: {
    name: 'Heart Disease',
    fields: [
      { label: 'Age (years)', name: 'age', placeholder: 'Enter age', type: 'number', step: '1' },
      { label: 'Cholesterol (mg/dL)', name: 'chol', placeholder: 'Cholesterol level', type: 'number', step: '1' },
      { label: 'Resting Blood Pressure (mmHg)', name: 'trestbps', placeholder: 'Blood pressure', type: 'number', step: '1' },
      { label: 'Chest Pain Type (0-3)', name: 'cp', placeholder: 'Chest pain type', type: 'number', step: '1', min: '0', max: '3' },
      { label: 'Max Heart Rate', name: 'thalachh', placeholder: 'Max heart rate', type: 'number', step: '1' }
    ],
    apiEndpoint: '/api/heart'
  },
  lungs: {
    name: 'Lung Disease',
    fields: [
      { label: 'Smoking Status (0=Never, 1=Former, 2=Current)', name: 'smoking_status', placeholder: 'Smoking status', type: 'number', step: '1', min: '0', max: '2' },
      { label: 'Air Pollution Level (AQI)', name: 'air_pollution_level', placeholder: 'Air quality index', type: 'number', step: '1' },
      { label: 'Chest Pain Severity (0-10)', name: 'chest_pain_severity', placeholder: 'Pain scale', type: 'number', step: '0.1', min: '0', max: '10' },
      { label: 'Cough Duration (days)', name: 'cough_duration_days', placeholder: 'Days of cough', type: 'number', step: '1' },
      { label: 'Respiratory Rate (breaths/min)', name: 'respiratory_rate', placeholder: 'Breaths per minute', type: 'number', step: '1' },
      { label: 'Age (years)', name: 'age', placeholder: 'Enter age', type: 'number', step: '1' },
      { label: 'Chemical Exposure Level (0-100)', name: 'exposure_to_chemicals', placeholder: 'Chemical exposure', type: 'number', step: '1' },
      { label: 'Exercise Frequency (days/week)', name: 'exercise_frequency', placeholder: 'Days per week', type: 'number', step: '0.5' }
    ],
    apiEndpoint: '/api/lungs'
  },
  neurological: {
    name: 'Neurological Risk Assessment',
    fields: [
      { label: 'Age (years)', name: 'age', placeholder: 'Enter age', type: 'number', step: '1' },
      { label: 'Systolic Blood Pressure (mmHg)', name: 'systolic_bp', placeholder: 'Systolic BP', type: 'number', step: '1' },
      { label: 'Diastolic Blood Pressure (mmHg)', name: 'diastolic_bp', placeholder: 'Diastolic BP', type: 'number', step: '1' },
      { label: 'Total Cholesterol (mg/dL)', name: 'total_cholesterol', placeholder: 'Total cholesterol', type: 'number', step: '1' },
      { label: 'LDL Cholesterol (mg/dL)', name: 'ldl_cholesterol', placeholder: 'LDL cholesterol', type: 'number', step: '1' },
      { label: 'HDL Cholesterol (mg/dL)', name: 'hdl_cholesterol', placeholder: 'HDL cholesterol', type: 'number', step: '1' },
      { label: 'Diabetes (0=No, 1=Yes)', name: 'diabetes', placeholder: 'Diabetes status', type: 'number', step: '1', min: '0', max: '1' },
      { label: 'Family History (0=No, 1=Yes)', name: 'family_history', placeholder: 'Family history', type: 'number', step: '1', min: '0', max: '1' },
      { label: 'Cognitive Score (Mini-Cog)', name: 'cognitive_score', placeholder: 'Cognitive score', type: 'number', step: '0.1' },
      { label: 'BMI (kg/m²)', name: 'bmi', placeholder: 'Body mass index', type: 'number', step: '0.1' },
      { label: 'Physical Activity (min/week)', name: 'physical_activity', placeholder: 'Minutes per week', type: 'number', step: '1' },
      { label: 'Alcohol Consumption (0=None, 1=Moderate, 2=Heavy, 3=VeryHeavy)', name: 'alcohol_consumption', placeholder: 'Alcohol consumption', type: 'number', step: '1', min: '0', max: '3' }
    ],
    apiEndpoint: '/api/neurological'
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
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`http://localhost:5000${config.apiEndpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (data.success) {
        onResultsReceived(data)
      } else {
        setError(data.error || 'An error occurred')
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure it\'s running on http://localhost:5000')
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
