import { useState } from 'react'

const HealthTips = ({ onClose }) => {
    const diseases = [
        {
            id: 'heart',
            name: 'Heart Disease',
            icon: '❤️',
            color: '#ef4444',
            overview: 'Heart disease refers to conditions affecting the heart\'s structure and function. It remains the leading cause of death worldwide.',
            riskFactors: [
                { name: 'High Blood Pressure', severity: 'high', icon: '🩸' },
                { name: 'High Cholesterol', severity: 'high', icon: '🧪' },
                { name: 'Smoking', severity: 'high', icon: '🚬' },
                { name: 'Diabetes', severity: 'medium', icon: '💉' },
                { name: 'Obesity', severity: 'medium', icon: '⚖️' },
                { name: 'Sedentary Lifestyle', severity: 'medium', icon: '🛋️' },
                { name: 'Family History', severity: 'low', icon: '👨‍👩‍👧‍👦' },
                { name: 'Age (>55)', severity: 'low', icon: '📅' },
            ],
            symptoms: ['Chest pain or discomfort', 'Shortness of breath', 'Pain in neck, jaw, or back', 'Numbness or coldness in limbs', 'Irregular heartbeat', 'Fatigue and dizziness'],
            prevention: [
                'Exercise at least 150 minutes per week',
                'Eat a heart-healthy diet (fruits, vegetables, whole grains)',
                'Maintain healthy weight (BMI 18.5-24.9)',
                'Quit smoking and limit alcohol',
                'Manage stress with meditation or yoga',
                'Monitor blood pressure regularly',
                'Get cholesterol checked every 4-6 years',
                'Sleep 7-9 hours per night'
            ],
            foods: {
                good: ['Salmon & Fatty Fish', 'Berries', 'Oats', 'Nuts & Seeds', 'Dark Leafy Greens', 'Olive Oil'],
                avoid: ['Red & Processed Meat', 'Sugary Drinks', 'Excessive Salt', 'Trans Fats', 'Refined Carbs']
            },
            emergencySigns: ['Severe chest pain', 'Difficulty breathing', 'Sudden arm/jaw pain', 'Loss of consciousness']
        },
        {
            id: 'diabetes',
            name: 'Diabetes',
            icon: '🩺',
            color: '#6366f1',
            overview: 'Diabetes is a chronic condition where the body cannot properly process blood sugar (glucose). Type 2 is the most common form.',
            riskFactors: [
                { name: 'Obesity/Overweight', severity: 'high', icon: '⚖️' },
                { name: 'Family History', severity: 'high', icon: '👨‍👩‍👧‍👦' },
                { name: 'Physical Inactivity', severity: 'high', icon: '🛋️' },
                { name: 'Age (>45)', severity: 'medium', icon: '📅' },
                { name: 'High Blood Pressure', severity: 'medium', icon: '🩸' },
                { name: 'Gestational Diabetes', severity: 'medium', icon: '🤰' },
                { name: 'PCOS', severity: 'low', icon: '👩' },
                { name: 'Poor Diet', severity: 'medium', icon: '🍔' },
            ],
            symptoms: ['Frequent urination', 'Excessive thirst', 'Unexplained weight loss', 'Blurred vision', 'Slow-healing wounds', 'Tingling in hands/feet', 'Fatigue'],
            prevention: [
                'Maintain a healthy weight',
                'Exercise regularly (30 min/day)',
                'Eat fiber-rich foods',
                'Choose whole grains over refined',
                'Monitor blood sugar levels',
                'Stay hydrated with water',
                'Limit processed sugar intake',
                'Get regular health checkups'
            ],
            foods: {
                good: ['Leafy Greens', 'Whole Grains', 'Lean Proteins', 'Beans & Lentils', 'Nuts', 'Citrus Fruits'],
                avoid: ['Sugary Drinks & Juices', 'White Bread & Pasta', 'Fried Foods', 'Candy & Sweets', 'Fruit Juice Concentrates']
            },
            emergencySigns: ['Very high blood sugar (>300)', 'Fruity breath odor', 'Nausea & vomiting', 'Confusion or unconsciousness']
        },
        {
            id: 'parkinsons',
            name: "Parkinson's Disease",
            icon: '🧠',
            color: '#a855f7',
            overview: "Parkinson's disease is a progressive neurological disorder that affects movement. It develops gradually, sometimes starting with a barely noticeable tremor.",
            riskFactors: [
                { name: 'Age (>60)', severity: 'high', icon: '📅' },
                { name: 'Family History', severity: 'high', icon: '👨‍👩‍👧‍👦' },
                { name: 'Male Gender', severity: 'medium', icon: '👨' },
                { name: 'Toxin Exposure', severity: 'medium', icon: '☠️' },
                { name: 'Head Injuries', severity: 'medium', icon: '🤕' },
                { name: 'Pesticide Exposure', severity: 'low', icon: '🧴' },
            ],
            symptoms: ['Tremor (shaking)', 'Slowed movement', 'Rigid muscles', 'Impaired posture', 'Loss of automatic movements', 'Speech changes', 'Writing changes'],
            prevention: [
                'Regular aerobic exercise',
                'Eat antioxidant-rich foods',
                'Protect your head from injuries',
                'Avoid toxin & pesticide exposure',
                'Stay socially and mentally active',
                'Get adequate sleep',
                'Consider caffeine (some studies suggest benefit)',
                'Practice balance exercises regularly'
            ],
            foods: {
                good: ['Berries & Antioxidants', 'Omega-3 Rich Foods', 'Turmeric', 'Green Tea', 'Beans', 'Fresh Vegetables'],
                avoid: ['Excessive Dairy', 'Processed Foods', 'High Mercury Fish', 'Excess Alcohol', 'High Iron Foods (excess)']
            },
            emergencySigns: ['Sudden inability to move', 'Severe muscle rigidity', 'Hallucinations', 'Falls causing injury']
        }
    ]

    const [activeDisease, setActiveDisease] = useState(0)
    const [activeTab, setActiveTab] = useState('overview')

    const disease = diseases[activeDisease]

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'high': return '#ef4444'
            case 'medium': return '#f59e0b'
            case 'low': return '#22c55e'
            default: return '#6b7280'
        }
    }

    return (
        <div className="tips-container">
            <div className="tips-header">
                <div>
                    <h2 className="tips-title">🏥 Health Information Center</h2>
                    <p className="tips-subtitle">Comprehensive medical information, prevention tips & dietary advice</p>
                </div>
                <button className="btn btn-secondary" onClick={onClose} style={{ width: 'auto' }}>
                    ← Back
                </button>
            </div>

            {/* Disease Selector Pills */}
            <div className="disease-pills">
                {diseases.map((d, i) => (
                    <button
                        key={d.id}
                        className={`disease-pill ${activeDisease === i ? 'active' : ''}`}
                        onClick={() => { setActiveDisease(i); setActiveTab('overview') }}
                        style={{ '--pill-color': d.color }}
                    >
                        <span className="pill-icon">{d.icon}</span>
                        <span>{d.name}</span>
                    </button>
                ))}
            </div>

            {/* Tab Navigation */}
            <div className="tips-tabs">
                {[
                    { key: 'overview', label: '📖 Overview', },
                    { key: 'risks', label: '⚠️ Risk Factors' },
                    { key: 'symptoms', label: '🔍 Symptoms' },
                    { key: 'prevention', label: '🛡️ Prevention' },
                    { key: 'diet', label: '🥗 Diet Guide' },
                    { key: 'emergency', label: '🚨 Emergency' }
                ].map(tab => (
                    <button
                        key={tab.key}
                        className={`tips-tab ${activeTab === tab.key ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.key)}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div className="tips-content">
                {activeTab === 'overview' && (
                    <div className="tips-panel animate-in">
                        <div className="overview-hero" style={{ '--accent': disease.color }}>
                            <span className="overview-icon">{disease.icon}</span>
                            <h3>{disease.name}</h3>
                            <p>{disease.overview}</p>
                        </div>
                        <div className="quick-stats-grid">
                            <div className="quick-stat">
                                <div className="quick-stat-number">{disease.riskFactors.length}</div>
                                <div className="quick-stat-label">Risk Factors</div>
                            </div>
                            <div className="quick-stat">
                                <div className="quick-stat-number">{disease.symptoms.length}</div>
                                <div className="quick-stat-label">Key Symptoms</div>
                            </div>
                            <div className="quick-stat">
                                <div className="quick-stat-number">{disease.prevention.length}</div>
                                <div className="quick-stat-label">Prevention Tips</div>
                            </div>
                            <div className="quick-stat">
                                <div className="quick-stat-number">{disease.emergencySigns.length}</div>
                                <div className="quick-stat-label">Emergency Signs</div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'risks' && (
                    <div className="tips-panel animate-in">
                        <h3>⚠️ Risk Factors for {disease.name}</h3>
                        <div className="risk-factors-grid">
                            {disease.riskFactors.map((rf, i) => (
                                <div key={i} className="risk-factor-card" style={{ animationDelay: `${i * 0.08}s` }}>
                                    <div className="risk-factor-header">
                                        <span className="risk-factor-icon">{rf.icon}</span>
                                        <span
                                            className="risk-severity-badge"
                                            style={{ background: getSeverityColor(rf.severity) }}
                                        >
                                            {rf.severity}
                                        </span>
                                    </div>
                                    <p className="risk-factor-name">{rf.name}</p>
                                </div>
                            ))}
                        </div>
                        <div className="severity-legend">
                            <span><span className="legend-dot" style={{ background: '#ef4444' }}></span> High Risk</span>
                            <span><span className="legend-dot" style={{ background: '#f59e0b' }}></span> Medium Risk</span>
                            <span><span className="legend-dot" style={{ background: '#22c55e' }}></span> Low Risk</span>
                        </div>
                    </div>
                )}

                {activeTab === 'symptoms' && (
                    <div className="tips-panel animate-in">
                        <h3>🔍 Common Symptoms of {disease.name}</h3>
                        <div className="symptoms-list">
                            {disease.symptoms.map((symptom, i) => (
                                <div key={i} className="symptom-item" style={{ animationDelay: `${i * 0.1}s` }}>
                                    <span className="symptom-number">{i + 1}</span>
                                    <span className="symptom-text">{symptom}</span>
                                </div>
                            ))}
                        </div>
                        <div className="symptoms-note">
                            <p>💡 <strong>Note:</strong> Having one or more symptoms doesn't necessarily mean you have {disease.name}. Consult a healthcare professional for proper diagnosis.</p>
                        </div>
                    </div>
                )}

                {activeTab === 'prevention' && (
                    <div className="tips-panel animate-in">
                        <h3>🛡️ Prevention Tips for {disease.name}</h3>
                        <div className="prevention-list">
                            {disease.prevention.map((tip, i) => (
                                <div key={i} className="prevention-item" style={{ animationDelay: `${i * 0.1}s` }}>
                                    <span className="prevention-check">✓</span>
                                    <span>{tip}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'diet' && (
                    <div className="tips-panel animate-in">
                        <h3>🥗 Dietary Recommendations for {disease.name}</h3>
                        <div className="diet-columns">
                            <div className="diet-column good">
                                <h4>✅ Foods to Include</h4>
                                <ul>
                                    {disease.foods.good.map((food, i) => (
                                        <li key={i}>{food}</li>
                                    ))}
                                </ul>
                            </div>
                            <div className="diet-column avoid">
                                <h4>❌ Foods to Limit/Avoid</h4>
                                <ul>
                                    {disease.foods.avoid.map((food, i) => (
                                        <li key={i}>{food}</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'emergency' && (
                    <div className="tips-panel animate-in">
                        <h3>🚨 Emergency Warning Signs</h3>
                        <p className="emergency-intro">Seek immediate medical attention if you experience any of these:</p>
                        <div className="emergency-signs">
                            {disease.emergencySigns.map((sign, i) => (
                                <div key={i} className="emergency-sign-card" style={{ animationDelay: `${i * 0.1}s` }}>
                                    <span className="emergency-icon">🚑</span>
                                    <span>{sign}</span>
                                </div>
                            ))}
                        </div>
                        <div className="emergency-cta">
                            <p>📞 <strong>In case of emergency, call your local emergency number immediately.</strong></p>
                            <p style={{ marginTop: '0.5rem', fontSize: '0.95rem', color: 'var(--text-light)' }}>India: 112 | US: 911 | UK: 999 | EU: 112</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

export default HealthTips
