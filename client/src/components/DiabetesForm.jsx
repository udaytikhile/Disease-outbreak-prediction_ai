import { useState } from 'react'

const DiabetesForm = ({ onSubmit, loading }) => {
    const [formData, setFormData] = useState({
        pregnancies: '',
        glucose: '',
        bloodPressure: '',
        skinThickness: '',
        insulin: '',
        bmi: '',
        dpf: '',
        age: '',
    })
    const [errors, setErrors] = useState({})

    const validateForm = () => {
        const newErrors = {}

        if (formData.pregnancies === '' || isNaN(formData.pregnancies) || Number(formData.pregnancies) < 0 || Number(formData.pregnancies) > 20) {
            newErrors.pregnancies = 'Must be 0-20'
        }
        if (formData.glucose === '' || isNaN(formData.glucose) || Number(formData.glucose) < 0 || Number(formData.glucose) > 300) {
            newErrors.glucose = 'Must be 0-300 mg/dL'
        }
        if (formData.bloodPressure === '' || isNaN(formData.bloodPressure) || Number(formData.bloodPressure) < 0 || Number(formData.bloodPressure) > 200) {
            newErrors.bloodPressure = 'Must be 0-200 mm Hg'
        }
        if (formData.skinThickness === '' || isNaN(formData.skinThickness) || Number(formData.skinThickness) < 0 || Number(formData.skinThickness) > 100) {
            newErrors.skinThickness = 'Must be 0-100 mm'
        }
        if (formData.insulin === '' || isNaN(formData.insulin) || Number(formData.insulin) < 0 || Number(formData.insulin) > 900) {
            newErrors.insulin = 'Must be 0-900 μU/mL'
        }
        if (formData.bmi === '' || isNaN(formData.bmi) || Number(formData.bmi) < 10 || Number(formData.bmi) > 70) {
            newErrors.bmi = 'Must be 10-70'
        }
        if (formData.dpf === '' || isNaN(formData.dpf) || Number(formData.dpf) < 0 || Number(formData.dpf) > 3) {
            newErrors.dpf = 'Must be 0-3'
        }
        if (formData.age === '' || isNaN(formData.age) || Number(formData.age) < 1 || Number(formData.age) > 120) {
            newErrors.age = 'Must be 1-120 years'
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
                <h2 className="card-title">🩺 Diabetes Prediction</h2>
                <p className="card-subtitle">Enter patient health metrics</p>
            </div>

            <div className="form-grid">
                <div className="form-group">
                    <label htmlFor="pregnancies">Number of Pregnancies *</label>
                    <input
                        type="number"
                        id="pregnancies"
                        name="pregnancies"
                        value={formData.pregnancies}
                        onChange={handleChange}
                        placeholder="Enter number"
                        required
                        min="0"
                        max="20"
                        className={errors.pregnancies ? 'input-error' : ''}
                    />
                    {errors.pregnancies && <span className="error-text">⚠️ {errors.pregnancies}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="glucose">Glucose Level (mg/dL) *</label>
                    <input
                        type="number"
                        id="glucose"
                        name="glucose"
                        value={formData.glucose}
                        onChange={handleChange}
                        placeholder="e.g., 120"
                        required
                        min="0"
                        max="300"
                        className={errors.glucose ? 'input-error' : ''}
                    />
                    {errors.glucose && <span className="error-text">⚠️ {errors.glucose}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="bloodPressure">Blood Pressure (mm Hg) *</label>
                    <input
                        type="number"
                        id="bloodPressure"
                        name="bloodPressure"
                        value={formData.bloodPressure}
                        onChange={handleChange}
                        placeholder="e.g., 80"
                        required
                        min="0"
                        max="200"
                        className={errors.bloodPressure ? 'input-error' : ''}
                    />
                    {errors.bloodPressure && <span className="error-text">⚠️ {errors.bloodPressure}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="skinThickness">Skin Thickness (mm) *</label>
                    <input
                        type="number"
                        id="skinThickness"
                        name="skinThickness"
                        value={formData.skinThickness}
                        onChange={handleChange}
                        placeholder="e.g., 20"
                        required
                        min="0"
                        max="100"
                        className={errors.skinThickness ? 'input-error' : ''}
                    />
                    {errors.skinThickness && <span className="error-text">⚠️ {errors.skinThickness}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="insulin">Insulin Level (μU/mL) *</label>
                    <input
                        type="number"
                        id="insulin"
                        name="insulin"
                        value={formData.insulin}
                        onChange={handleChange}
                        placeholder="e.g., 80"
                        required
                        min="0"
                        max="900"
                        className={errors.insulin ? 'input-error' : ''}
                    />
                    {errors.insulin && <span className="error-text">⚠️ {errors.insulin}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="bmi">Body Mass Index (BMI) *</label>
                    <input
                        type="number"
                        id="bmi"
                        name="bmi"
                        value={formData.bmi}
                        onChange={handleChange}
                        placeholder="e.g., 25.5"
                        required
                        step="0.1"
                        min="10"
                        max="70"
                        className={errors.bmi ? 'input-error' : ''}
                    />
                    {errors.bmi && <span className="error-text">⚠️ {errors.bmi}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="dpf">Diabetes Pedigree Function *</label>
                    <input
                        type="number"
                        id="dpf"
                        name="dpf"
                        value={formData.dpf}
                        onChange={handleChange}
                        placeholder="e.g., 0.5"
                        required
                        step="0.001"
                        min="0"
                        max="3"
                        className={errors.dpf ? 'input-error' : ''}
                    />
                    {errors.dpf && <span className="error-text">⚠️ {errors.dpf}</span>}
                </div>

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
            </div>

            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                {loading ? (
                    <>
                        <span className="spinner"></span>
                        Analyzing...
                    </>
                ) : (
                    <>
                        🔍 Predict Diabetes Risk
                    </>
                )}
            </button>
        </form>
    )
}

export default DiabetesForm
