import { useState } from 'react'
import '../styles/Home.css'
import { HeartIcon, CheckCircleIcon, SparklesIcon, BeakerIcon, LockClosedIcon, BoltIcon, ChartBarIcon } from '@heroicons/react/24/solid'

const diseases = [
  {
    id: 'diabetes',
    name: 'Diabetes',
    icon: HeartIcon,
    description: 'Predict type-2 diabetes risk using glucose levels, insulin, BMI, and metabolic markers.',
    accuracy: '93% Accuracy',
    speed: '~1.2s',
    riskLevel: 72,
    color: 'diabetes',
    topBar: 'diabetes'
  },
  {
    id: 'ckd',
    name: 'Chronic Kidney Disease',
    icon: CheckCircleIcon,
    description: 'Assess CKD risk through creatinine, albumin, urea, and kidney function biomarkers.',
    accuracy: '96% Accuracy',
    speed: '~0.9s',
    riskLevel: 48,
    color: 'kidney',
    topBar: 'kidney'
  },
  {
    id: 'cld',
    name: 'Chronic Liver Disease',
    icon: SparklesIcon,
    description: 'Evaluate liver health via ALT, AST, bilirubin, and hepatic enzyme function tests.',
    accuracy: '91% Accuracy',
    speed: '~1.5s',
    riskLevel: 55,
    color: 'liver',
    topBar: 'liver'
  },
  {
    id: 'heart',
    name: 'Heart Disease',
    icon: HeartIcon,
    description: 'Cardiovascular risk via cholesterol, blood pressure, ECG, and cardiac biomarkers.',
    accuracy: '95% Accuracy',
    speed: '~1.1s',
    riskLevel: 68,
    color: 'heart',
    topBar: 'heart'
  }
]

export default function Home({ onSelectDisease }) {
  const [stats] = useState({
    modelsActive: '4/4',
    assessmentsToday: '1,247',
    avgAccuracy: '94.3%',
    totalAssessed: '42.8K',
    accuracyChange: '↑ 1.2%',
    highRiskFlagged: '2,341',
    avgScanTime: '1.4s'
  })

  const getRiskGradient = (color) => {
    const gradients = {
      diabetes: 'linear-gradient(90deg, var(--cyan), #0099bb)',
      kidney: 'linear-gradient(90deg, var(--emerald), #006644)',
      liver: 'linear-gradient(90deg, var(--amber), #cc7700)',
      heart: 'linear-gradient(90deg, var(--red), #aa0033)'
    }
    return gradients[color] || gradients.diabetes
  }

  return (
    <main>
      {/* HERO */}
      <div className="hero">
        <div className="hero-left">
          <div className="hero-badge">
            <div className="badge-dot"></div>
            ML-Powered · Real-time Analysis
          </div>
          <h1>Predict Disease Risk<br/>with <em>Clinical Precision</em></h1>
          <p>Advanced machine learning models trained on millions of patient records provide early detection insights for 4 critical conditions — empowering better health decisions.</p>
          <div className="hero-actions">
            <button className="btn-hero" onClick={() => onSelectDisease('diabetes')}>Start Assessment →</button>
            <button className="btn-outline">View Demo</button>
          </div>
        </div>

        <div className="hero-stats">
          <div className="stats-header">
            <span className="stats-title">System Overview</span>
            <span className="stats-live"><span className="vital-dot-small green"></span>Live</span>
          </div>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Total Assessed</div>
              <div className="stat-value cyan">{stats.totalAssessed}</div>
              <div className="stat-change">↑ 12% this week</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Model Accuracy</div>
              <div className="stat-value emerald">94.3%</div>
              <div className="stat-change">{stats.accuracyChange} this month</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">High Risk Flagged</div>
              <div className="stat-value amber">{stats.highRiskFlagged}</div>
              <div className="stat-change">Referred to doctors</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Avg Scan Time</div>
              <div className="stat-value violet">{stats.avgScanTime}</div>
              <div className="stat-change">Real-time results</div>
            </div>
          </div>
          <div className="heartbeat-container">
            <div className="heartbeat-label">ECG Monitor — System Health</div>
            <svg className="heartbeat-svg" viewBox="0 0 400 40" preserveAspectRatio="none">
              <path className="ecg-path" d="M0,20 L40,20 L50,20 L55,5 L60,35 L65,5 L70,20 L100,20 L110,20 L115,8 L120,32 L125,8 L130,20 L160,20 L170,20 L175,5 L180,35 L185,5 L190,20 L220,20 L230,20 L235,8 L240,32 L245,8 L250,20 L280,20 L290,20 L295,5 L300,35 L305,5 L310,20 L340,20 L350,20 L355,8 L360,32 L365,8 L370,20 L400,20"
                fill="none" stroke="#00e5a0" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        </div>
      </div>

      {/* ASSESSMENT CARDS */}
      <div className="section">
        <div className="section-header">
          <div>
            <div className="section-eyebrow">Diagnostic Modules</div>
            <div className="section-title">Select an Assessment</div>
          </div>
          <a href="#" className="section-link">View All Models →</a>
        </div>
        <div className="cards-grid">
          {diseases.map((disease) => (
            <div key={disease.id} className="assessment-card">
              <div className={`card-top-bar ${disease.topBar}`}></div>
              <div className="card-body">
                <div className={`card-icon-wrap ${disease.color}`}><disease.icon width={32} height={32} /></div>
                <div className="card-name">{disease.name}</div>
                <div className="card-desc">{disease.description}</div>
                <div className="card-meta">
                  <span className="meta-tag accuracy">{disease.accuracy}</span>
                  <span className="meta-tag speed">{disease.speed}</span>
                </div>
                <div className="risk-meter">
                  <div className="risk-header">
                    <span>Population Risk Index</span>
                    <span>{disease.riskLevel > 60 ? 'High Prevalence' : disease.riskLevel > 40 ? 'Moderate' : 'Low–Medium'}</span>
                  </div>
                  <div className="risk-bar">
                    <div 
                      className="risk-fill" 
                      style={{
                        width: `${disease.riskLevel}%`,
                        background: getRiskGradient(disease.color)
                      }}
                    ></div>
                  </div>
                </div>
                <button 
                  className={`card-btn ${disease.color}`}
                  onClick={() => onSelectDisease(disease.id)}
                >
                  Begin {disease.name.split(' ')[0]} Scan →
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* HOW IT WORKS */}
      <div className="how-strip">
        <div className="how-inner">
          <div className="section-header" style={{ marginBottom: '40px' }}>
            <div>
              <div className="section-eyebrow">Process</div>
              <div className="section-title">How It Works</div>
            </div>
          </div>
          <div className="steps-row">
            <div className="step">
              <div className="step-num s1">01</div>
              <h3>Input Biomarkers</h3>
              <p>Enter your lab results and health metrics from standard medical tests.</p>
            </div>
            <div className="step">
              <div className="step-num s2">02</div>
              <h3>ML Analysis</h3>
              <p>Models process data against millions of clinical case training records.</p>
            </div>
            <div className="step">
              <div className="step-num s3">03</div>
              <h3>Risk Scoring</h3>
              <p>Receive a probability score with confidence intervals and risk factors.</p>
            </div>
            <div className="step">
              <div className="step-num s4">04</div>
              <h3>Clinical Report</h3>
              <p>Download a detailed PDF report to share with your healthcare provider.</p>
            </div>
          </div>
        </div>
      </div>

      {/* FEATURES */}
      <div className="section">
        <div className="section-header">
          <div>
            <div className="section-eyebrow">Capabilities</div>
            <div className="section-title">Why MediScan</div>
          </div>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon" style={{ background: 'var(--cyan-dim)' }}><BeakerIcon width={24} height={24} /></div>
            <div className="feature-text">
              <h3>Research-Grade Models</h3>
              <p>Trained on peer-reviewed datasets with rigorous cross-validation. Each model undergoes independent clinical testing before deployment.</p>
            </div>
          </div>
          <div className="feature-card">
            <div className="feature-icon" style={{ background: 'var(--emerald-dim)' }}><LockClosedIcon width={24} height={24} /></div>
            <div className="feature-text">
              <h3>HIPAA-Compliant Privacy</h3>
              <p>Your data never leaves the session. All processing is ephemeral — zero patient data stored on our servers.</p>
            </div>
          </div>
          <div className="feature-card">
            <div className="feature-icon" style={{ background: 'var(--amber-dim)' }}><BoltIcon width={24} height={24} /></div>
            <div className="feature-text">
              <h3>Real-Time Results</h3>
              <p>Sub-2-second inference powered by optimized model serving infrastructure. Get results instantly.</p>
            </div>
          </div>
          <div className="feature-card">
            <div className="feature-icon" style={{ background: 'rgba(167,139,250,0.12)' }}><ChartBarIcon width={24} height={24} /></div>
            <div className="feature-text">
              <h3>Explainable AI</h3>
              <p>Every prediction includes SHAP-based feature importance scores so clinicians understand which factors drove the result.</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
