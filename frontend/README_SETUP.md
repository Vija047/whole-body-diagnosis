# Disease Predictor - Professional UI with React

A modern, professional web application for machine learning-based disease risk assessment using React.js and Flask backend API.

## 🎯 Features

- **Modern React Interface**: Built with React 19 and Vite for fast development and production builds
- **Multiple Disease Predictions**: 
  - Diabetes Risk Assessment
  - Chronic Kidney Disease (CKD)
  - Chronic Liver Disease (CLD)
  - Heart Disease Risk
- **Professional UI Design**: Clean, modern interface with gradient colors and smooth animations
- **Real-time Risk Assessment**: Instant predictions with probability scores
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Secure API**: CORS-enabled Flask backend for safe communication

## 📋 Project Structure

```
frontend/
├── src/
│   ├── pages/
│   │   └── Home.jsx          # Landing page with disease cards
│   ├── components/
│   │   ├── DiseaseForm.jsx   # Dynamic form for disease input
│   │   └── ResultsDisplay.jsx # Results and recommendations
│   ├── styles/
│   │   ├── Home.css
│   │   ├── DiseaseForm.css
│   │   └── ResultsDisplay.css
│   ├── App.jsx               # Main application component
│   ├── App.css               # Global styles
│   ├── main.jsx              # React entry point
│   └── index.css             # Base styles
├── index.html                # HTML entry point
├── package.json              # React dependencies
└── vite.config.js            # Vite configuration
```

## 🚀 Getting Started

### Requirements

- Python 3.8+
- Node.js 14+ and npm
- Trained ML models in `models/` directory

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Flask API server**:
   ```bash
   python app.py
   ```
   The server will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173` (or another port if 5173 is busy)

## 🔧 Available Scripts

### Frontend

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint for code quality

## 🎨 UI Components

### Home Page
- Beautiful hero section with gradient backgrounds
- 4 disease prediction cards with hover effects
- Info section highlighting key features
- Responsive grid layout

### Disease Form
- Dynamic form fields based on disease type
- Real-time form validation
- Beautiful input styling with focus states
- Loading state during prediction
- Error handling with user-friendly messages

### Results Display
- Visual result badge (Positive/Negative)
- Risk probability visualization with animated bar
- Personalized recommendations based on results
- Medical disclaimer
- Option to start new assessment

## 📱 API Endpoints

All endpoints expect JSON requests and return JSON responses.

```
POST /api/health              # Health check
POST /api/diabetes            # Diabetes prediction
POST /api/ckd                 # Chronic Kidney Disease prediction
POST /api/cld                 # Chronic Liver Disease prediction
POST /api/heart               # Heart Disease prediction
```

## 🎨 Design Highlights

- **Color Scheme**: Professional blue gradient primary colors
- **Typography**: Clean system fonts with proper hierarchy
- **Animations**: Smooth transitions and scaling effects
- **Spacing**: Consistent padding and margins
- **Shadows**: Layered shadows for depth perception
- **Accessibility**: ARIA labels and semantic HTML

## 🔒 Security & Privacy

- CORS enabled for secure cross-origin requests
- No data persistence - predictions are not stored
- Client-side error handling
- Server validates all inputs

## 📦 Dependencies

### Frontend
- React 19.2.4
- React DOM 19.2.4
- Vite 8.0.1

### Backend
- Flask
- Flask-CORS
- Scikit-learn
- Joblib
- NumPy
- Pandas

## 🐛 Troubleshooting

**Connection Error**: Ensure Flask server is running on `http://localhost:5000`

**Port Already in Use**: 
- For frontend: Vite will automatically use next available port
- For backend: Change port in `app.py`: `app.run(debug=True, port=5001)`

**Missing Models**: Ensure `.pkl` files are in the `models/` directory

## 📝 License

This project is part of a minor project for healthcare ML applications.

---

**Built with ❤️ using React, Flask, and Machine Learning**
