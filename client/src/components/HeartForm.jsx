import { useState } from 'react'

const HeartForm = ({ onSubmit, loading }) => {
    const [formData, setFormData] = useState({
        age: '',
        sex: '1',
        cp: '0',
        trestbps: '',
        chol: '',
        fbs: '0',
        restecg: '0',
        thalach: '',
        exang: '0',
        oldpeak: '',
        slope: '0',
        ca: '0',
        thal: '0',
    })
    const [errors, setErrors] = useState({})

    const validateForm = () => {
        const newErrors = {}

        if (formData.age === '' || isNaN(formData.age) || Number(formData.age) < 1 || Number(formData.age) > 120) {
            newErrors.age = 'Must be 1-120 years'
        }
        if (formData.trestbps === '' || isNaN(formData.trestbps) || Number(formData.trestbps) < 0 || Number(formData.trestbps) > 300) {
            newErrors.trestbps = 'Must be 0-300 mm Hg'
        }
        if (formData.chol === '' || isNaN(formData.chol) || Number(formData.chol) < 0 || Number(formData.chol) > 600) {
            newErrors.chol = 'Must be 0-600 mg/dl'
        }
        if (formData.thalach === '' || isNaN(formData.thalach) || Number(formData.thalach) < 60 || Number(formData.thalach) > 220) {
            newErrors.thalach = 'Must be 60-220 bpm'
        }
        if (formData.oldpeak === '' || isNaN(formData.oldpeak) || Number(formData.oldpeak) < 0 || Number(formData.oldpeak) > 10) {
            newErrors.oldpeak = 'Must be 0-10'
        }

        setErrors(newErrors)
        return Object.keys(newErrors).length === 0
    }

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        })
        // Clear error for this field when user starts typing
        if (errors[e.target.name]) {
            setErrors({
                ...errors,
                [e.target.name]: ''
            })
        }
    }

    const handleSubmit = (e) => {
        e.preventDefault()
        if (validateForm()) {
            onSubmit(formData)
        }
    }

    return (
        <form onSubmit={handleSubmit}>
            <div className="card-header">
                <h2 className="card-title">❤️ Heart Disease Prediction</h2>
                <p className="card-subtitle">Enter patient information and clinical parameters</p>
            </div>

            <div className="form-grid">
                <div className="form-group">
                    <label htmlFor="age">Age *</label>
                    <input
                        type="number"
                        id="age"
                        name="age"
                        value={formData.age}
                        onChange={handleChange}
                        placeholder="Enter age"
                        required
                        min="1"
                        max="120"
                        className={errors.age ? 'input-error' : ''}
                    />
                    {errors.age && <span className="error-text">⚠️ {errors.age}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="sex">Sex *</label>
                    <select id="sex" name="sex" value={formData.sex} onChange={handleChange} required>
                        <option value="1">Male</option>
                        <option value="0">Female</option>
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="cp">Chest Pain Type *</label>
                    <select id="cp" name="cp" value={formData.cp} onChange={handleChange} required>
                        <option value="0">Type 0 - Typical Angina</option>
                        <option value="1">Type 1 - Atypical Angina</option>
                        <option value="2">Type 2 - Non-anginal Pain</option>
                        <option value="3">Type 3 - Asymptomatic</option>
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="trestbps">Resting Blood Pressure (mm Hg) *</label>
                    <input
                        type="number"
                        id="trestbps"
                        name="trestbps"
                        value={formData.trestbps}
                        onChange={handleChange}
                        placeholder="e.g., 120"
                        required
                        min="0"
                        max="300"
                        className={errors.trestbps ? 'input-error' : ''}
                    />
                    {errors.trestbps && <span className="error-text">⚠️ {errors.trestbps}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="chol">Serum Cholesterol (mg/dl) *</label>
                    <input
                        type="number"
                        id="chol"
                        name="chol"
                        value={formData.chol}
                        onChange={handleChange}
                        placeholder="e.g., 200"
                        required
                        min="0"
                        max="600"
                        className={errors.chol ? 'input-error' : ''}
                    />
                    {errors.chol && <span className="error-text">⚠️ {errors.chol}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="fbs">Fasting Blood Sugar &gt; 120 mg/dl *</label>
                    <select id="fbs" name="fbs" value={formData.fbs} onChange={handleChange} required>
                        <option value="0">No (≤ 120 mg/dl)</option>
                        <option value="1">Yes (&gt; 120 mg/dl)</option>
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="restecg">Resting ECG Results *</label>
                    <select id="restecg" name="restecg" value={formData.restecg} onChange={handleChange} required>
                        <option value="0">Normal</option>
                        <option value="1">ST-T Wave Abnormality</option>
                        <option value="2">Left Ventricular Hypertrophy</option>
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="thalach">Maximum Heart Rate Achieved *</label>
                    <input
                        type="number"
                        id="thalach"
                        name="thalach"
                        value={formData.thalach}
                        onChange={handleChange}
                        placeholder="e.g., 150"
                        required
                        min="60"
                        max="220"
                        className={errors.thalach ? 'input-error' : ''}
                    />
                    {errors.thalach && <span className="error-text">⚠️ {errors.thalach}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="exang">Exercise Induced Angina *</label>
                    <select id="exang" name="exang" value={formData.exang} onChange={handleChange} required>
                        <option value="0">No</option>
                        <option value="1">Yes</option>
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="oldpeak">ST Depression *</label>
                    <input
                        type="number"
                        id="oldpeak"
                        name="oldpeak"
                        value={formData.oldpeak}
                        onChange={handleChange}
                        placeholder="e.g., 1.5"
                        required
                        step="0.1"
                        min="0"
                        max="10"
                        className={errors.oldpeak ? 'input-error' : ''}
                    />
                    {errors.oldpeak && <span className="error-text">⚠️ {errors.oldpeak}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="slope">Slope of Peak Exercise ST Segment *</label>
                    <select id="slope" name="slope" value={formData.slope} onChange={handleChange} required>
                        <option value="0">Upsloping</option>
                        <option value="1">Flat</option>
                        <option value="2">Downsloping</option>
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="ca">Number of Major Vessels (0-3) *</label>
                    <select id="ca" name="ca" value={formData.ca} onChange={handleChange} required>
                        <option value="0">0</option>
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="thal">Thalassemia *</label>
                    <select id="thal" name="thal" value={formData.thal} onChange={handleChange} required>
                        <option value="0">Normal</option>
                        <option value="1">Fixed Defect</option>
                        <option value="2">Reversible Defect</option>
                        <option value="3">Unknown / Other</option>
                    </select>
                </div>
            </div>

            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                {loading ? (
                    <>
                        <span className="spinner"></span>
                        Analyzing...
                    </>
                ) : (
                    <>
                        🔍 Predict Heart Disease Risk
                    </>
                )}
            </button>
        </form>
    )
}

export default HeartForm
