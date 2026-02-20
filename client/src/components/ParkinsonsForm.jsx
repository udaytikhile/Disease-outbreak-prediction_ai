import { useState } from 'react'

const ParkinsonsForm = ({ onSubmit, loading }) => {
    const [formData, setFormData] = useState({
        fo: '',
        fhi: '',
        flo: '',
        jitter: '',
        jitterAbs: '',
        rap: '',
        ppq: '',
        ddp: '',
        shimmer: '',
        shimmerDb: '',
        apq3: '',
        apq5: '',
        apq: '',
        dda: '',
        nhr: '',
        hnr: '',
        rpde: '',
        dfa: '',
        spread1: '',
        spread2: '',
        d2: '',
        ppe: '',
    })
    const [errors, setErrors] = useState({})

    const validateForm = () => {
        const newErrors = {}
        const fields = Object.keys(formData)

        fields.forEach(field => {
            if (formData[field] === '' || formData[field] === null || formData[field] === undefined || isNaN(formData[field])) {
                newErrors[field] = 'Required & must be numeric'
            }
        })

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
                <h2 className="card-title">🧠 Parkinson's Disease Prediction</h2>
                <p className="card-subtitle">Enter voice measurement parameters</p>
            </div>

            <div className="form-grid">
                <div className="form-group">
                    <label htmlFor="fo">MDVP:Fo(Hz) *</label>
                    <input
                        type="number"
                        id="fo"
                        name="fo"
                        value={formData.fo}
                        onChange={handleChange}
                        placeholder="e.g., 150"
                        required
                        step="0.001"
                        className={errors.fo ? 'input-error' : ''}
                    />
                    {errors.fo && <span className="error-text">⚠️ {errors.fo}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="fhi">MDVP:Fhi(Hz) *</label>
                    <input
                        type="number"
                        id="fhi"
                        name="fhi"
                        value={formData.fhi}
                        onChange={handleChange}
                        placeholder="e.g., 200"
                        required
                        step="0.001"
                        className={errors.fhi ? 'input-error' : ''}
                    />
                    {errors.fhi && <span className="error-text">⚠️ {errors.fhi}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="flo">MDVP:Flo(Hz) *</label>
                    <input
                        type="number"
                        id="flo"
                        name="flo"
                        value={formData.flo}
                        onChange={handleChange}
                        placeholder="e.g., 100"
                        required
                        step="0.001"
                        className={errors.flo ? 'input-error' : ''}
                    />
                    {errors.flo && <span className="error-text">⚠️ {errors.flo}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="jitter">MDVP:Jitter(%) *</label>
                    <input
                        type="number"
                        id="jitter"
                        name="jitter"
                        value={formData.jitter}
                        onChange={handleChange}
                        placeholder="e.g., 0.005"
                        required
                        step="0.00001"
                        className={errors.jitter ? 'input-error' : ''}
                    />
                    {errors.jitter && <span className="error-text">⚠️ {errors.jitter}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="jitterAbs">MDVP:Jitter(Abs) *</label>
                    <input
                        type="number"
                        id="jitterAbs"
                        name="jitterAbs"
                        value={formData.jitterAbs}
                        onChange={handleChange}
                        placeholder="e.g., 0.00003"
                        required
                        step="0.0000001"
                        className={errors.jitterAbs ? 'input-error' : ''}
                    />
                    {errors.jitterAbs && <span className="error-text">⚠️ {errors.jitterAbs}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="rap">MDVP:RAP *</label>
                    <input
                        type="number"
                        id="rap"
                        name="rap"
                        value={formData.rap}
                        onChange={handleChange}
                        placeholder="e.g., 0.003"
                        required
                        step="0.00001"
                        className={errors.rap ? 'input-error' : ''}
                    />
                    {errors.rap && <span className="error-text">⚠️ {errors.rap}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="ppq">MDVP:PPQ *</label>
                    <input
                        type="number"
                        id="ppq"
                        name="ppq"
                        value={formData.ppq}
                        onChange={handleChange}
                        placeholder="e.g., 0.003"
                        required
                        step="0.00001"
                        className={errors.ppq ? 'input-error' : ''}
                    />
                    {errors.ppq && <span className="error-text">⚠️ {errors.ppq}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="ddp">Jitter:DDP *</label>
                    <input
                        type="number"
                        id="ddp"
                        name="ddp"
                        value={formData.ddp}
                        onChange={handleChange}
                        placeholder="e.g., 0.009"
                        required
                        step="0.00001"
                        className={errors.ddp ? 'input-error' : ''}
                    />
                    {errors.ddp && <span className="error-text">⚠️ {errors.ddp}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="shimmer">MDVP:Shimmer *</label>
                    <input
                        type="number"
                        id="shimmer"
                        name="shimmer"
                        value={formData.shimmer}
                        onChange={handleChange}
                        placeholder="e.g., 0.03"
                        required
                        step="0.00001"
                        className={errors.shimmer ? 'input-error' : ''}
                    />
                    {errors.shimmer && <span className="error-text">⚠️ {errors.shimmer}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="shimmerDb">MDVP:Shimmer(dB) *</label>
                    <input
                        type="number"
                        id="shimmerDb"
                        name="shimmerDb"
                        value={formData.shimmerDb}
                        onChange={handleChange}
                        placeholder="e.g., 0.3"
                        required
                        step="0.001"
                        className={errors.shimmerDb ? 'input-error' : ''}
                    />
                    {errors.shimmerDb && <span className="error-text">⚠️ {errors.shimmerDb}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="apq3">Shimmer:APQ3 *</label>
                    <input
                        type="number"
                        id="apq3"
                        name="apq3"
                        value={formData.apq3}
                        onChange={handleChange}
                        placeholder="e.g., 0.015"
                        required
                        step="0.00001"
                        className={errors.apq3 ? 'input-error' : ''}
                    />
                    {errors.apq3 && <span className="error-text">⚠️ {errors.apq3}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="apq5">Shimmer:APQ5 *</label>
                    <input
                        type="number"
                        id="apq5"
                        name="apq5"
                        value={formData.apq5}
                        onChange={handleChange}
                        placeholder="e.g., 0.018"
                        required
                        step="0.00001"
                        className={errors.apq5 ? 'input-error' : ''}
                    />
                    {errors.apq5 && <span className="error-text">⚠️ {errors.apq5}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="apq">MDVP:APQ *</label>
                    <input
                        type="number"
                        id="apq"
                        name="apq"
                        value={formData.apq}
                        onChange={handleChange}
                        placeholder="e.g., 0.02"
                        required
                        step="0.00001"
                        className={errors.apq ? 'input-error' : ''}
                    />
                    {errors.apq && <span className="error-text">⚠️ {errors.apq}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="dda">Shimmer:DDA *</label>
                    <input
                        type="number"
                        id="dda"
                        name="dda"
                        value={formData.dda}
                        onChange={handleChange}
                        placeholder="e.g., 0.045"
                        required
                        step="0.00001"
                        className={errors.dda ? 'input-error' : ''}
                    />
                    {errors.dda && <span className="error-text">⚠️ {errors.dda}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="nhr">NHR *</label>
                    <input
                        type="number"
                        id="nhr"
                        name="nhr"
                        value={formData.nhr}
                        onChange={handleChange}
                        placeholder="e.g., 0.02"
                        required
                        step="0.00001"
                        className={errors.nhr ? 'input-error' : ''}
                    />
                    {errors.nhr && <span className="error-text">⚠️ {errors.nhr}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="hnr">HNR *</label>
                    <input
                        type="number"
                        id="hnr"
                        name="hnr"
                        value={formData.hnr}
                        onChange={handleChange}
                        placeholder="e.g., 20"
                        required
                        step="0.001"
                        className={errors.hnr ? 'input-error' : ''}
                    />
                    {errors.hnr && <span className="error-text">⚠️ {errors.hnr}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="rpde">RPDE *</label>
                    <input
                        type="number"
                        id="rpde"
                        name="rpde"
                        value={formData.rpde}
                        onChange={handleChange}
                        placeholder="e.g., 0.5"
                        required
                        step="0.00001"
                        className={errors.rpde ? 'input-error' : ''}
                    />
                    {errors.rpde && <span className="error-text">⚠️ {errors.rpde}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="dfa">DFA *</label>
                    <input
                        type="number"
                        id="dfa"
                        name="dfa"
                        value={formData.dfa}
                        onChange={handleChange}
                        placeholder="e.g., 0.7"
                        required
                        step="0.00001"
                        className={errors.dfa ? 'input-error' : ''}
                    />
                    {errors.dfa && <span className="error-text">⚠️ {errors.dfa}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="spread1">Spread1 *</label>
                    <input
                        type="number"
                        id="spread1"
                        name="spread1"
                        value={formData.spread1}
                        onChange={handleChange}
                        placeholder="e.g., -5"
                        required
                        step="0.00001"
                        className={errors.spread1 ? 'input-error' : ''}
                    />
                    {errors.spread1 && <span className="error-text">⚠️ {errors.spread1}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="spread2">Spread2 *</label>
                    <input
                        type="number"
                        id="spread2"
                        name="spread2"
                        value={formData.spread2}
                        onChange={handleChange}
                        placeholder="e.g., 0.2"
                        required
                        step="0.00001"
                        className={errors.spread2 ? 'input-error' : ''}
                    />
                    {errors.spread2 && <span className="error-text">⚠️ {errors.spread2}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="d2">D2 *</label>
                    <input
                        type="number"
                        id="d2"
                        name="d2"
                        value={formData.d2}
                        onChange={handleChange}
                        placeholder="e.g., 2.5"
                        required
                        step="0.00001"
                        className={errors.d2 ? 'input-error' : ''}
                    />
                    {errors.d2 && <span className="error-text">⚠️ {errors.d2}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="ppe">PPE *</label>
                    <input
                        type="number"
                        id="ppe"
                        name="ppe"
                        value={formData.ppe}
                        onChange={handleChange}
                        placeholder="e.g., 0.2"
                        required
                        step="0.00001"
                        className={errors.ppe ? 'input-error' : ''}
                    />
                    {errors.ppe && <span className="error-text">⚠️ {errors.ppe}</span>}
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
                        🔍 Predict Parkinson's Risk
                    </>
                )}
            </button>
        </form>
    )
}

export default ParkinsonsForm