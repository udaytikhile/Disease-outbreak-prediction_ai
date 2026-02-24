import { useState, useMemo } from 'react'
import { InputCard, Section, ProgressBar, convertNumericFields } from '../common/FormComponents'

const HEART_STRING_FIELDS = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']

const HeartForm = ({ onSubmit, loading }) => {
    const [formData, setFormData] = useState({
        age: '', sex: 'Male', cp: 'typical angina', trestbps: '', chol: '',
        fbs: 'FALSE', restecg: 'normal', thalch: '', exang: 'FALSE',
        oldpeak: '', slope: 'upsloping', ca: '0', thal: 'normal',
    })
    const [errors, setErrors] = useState({})

    const progress = useMemo(() => {
        const fields = Object.values(formData)
        const filled = fields.filter(v => v !== '').length
        return Math.round((filled / fields.length) * 100)
    }, [formData])

    const validateForm = () => {
        const e = {}
        if (!formData.age || Number(formData.age) < 1 || Number(formData.age) > 120) e.age = '1–120 years'
        if (!formData.trestbps || Number(formData.trestbps) < 0 || Number(formData.trestbps) > 300) e.trestbps = '0–300 mm Hg'
        if (!formData.chol || Number(formData.chol) < 0 || Number(formData.chol) > 600) e.chol = '0–600 mg/dl'
        if (!formData.thalch || Number(formData.thalch) < 60 || Number(formData.thalch) > 220) e.thalch = '60–220 bpm'
        if (formData.oldpeak === '' || Number(formData.oldpeak) < -5 || Number(formData.oldpeak) > 10) e.oldpeak = '-5 to 10'
        setErrors(e)
        return Object.keys(e).length === 0
    }

    const set = (ev) => {
        setFormData({ ...formData, [ev.target.name]: ev.target.value })
        if (errors[ev.target.name]) setErrors({ ...errors, [ev.target.name]: '' })
    }

    const handleSubmit = (ev) => {
        ev.preventDefault()
        if (validateForm()) onSubmit(convertNumericFields(formData, HEART_STRING_FIELDS))
    }

    return (
        <form onSubmit={handleSubmit}>
            <ProgressBar percent={progress} />

            {/* ── Demographics ── */}
            <Section icon="👤" title="Patient Demographics" subtitle="Basic identification info">
                <InputCard icon="🎂" label="Age" required error={errors.age}>
                    <input type="number" name="age" value={formData.age} onChange={set} placeholder="e.g., 63" min="1" max="120" />
                </InputCard>
                <InputCard icon="⚧" label="Sex" required>
                    <select name="sex" value={formData.sex} onChange={set}>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                    </select>
                </InputCard>
            </Section>

            {/* ── Symptoms ── */}
            <Section icon="🫀" title="Symptoms & Signs" subtitle="Chest pain, exercise response, and angina">
                <InputCard icon="💢" label="Chest Pain Type" required>
                    <select name="cp" value={formData.cp} onChange={set}>
                        <option value="typical angina">Typical Angina</option>
                        <option value="atypical angina">Atypical Angina</option>
                        <option value="non-anginal">Non-anginal Pain</option>
                        <option value="asymptomatic">Asymptomatic</option>
                    </select>
                </InputCard>
                <InputCard icon="🏃" label="Exercise Induced Angina" required>
                    <select name="exang" value={formData.exang} onChange={set}>
                        <option value="FALSE">No</option>
                        <option value="TRUE">Yes</option>
                    </select>
                </InputCard>
            </Section>

            {/* ── Vitals & Labs ── */}
            <Section icon="🩺" title="Vitals & Lab Work" subtitle="Blood pressure, cholesterol, and glucose tests">
                <InputCard icon="🩸" label="Resting Blood Pressure" required error={errors.trestbps}>
                    <input type="number" name="trestbps" value={formData.trestbps} onChange={set} placeholder="mm Hg, e.g., 145" min="0" max="300" />
                </InputCard>
                <InputCard icon="🧪" label="Serum Cholesterol" required error={errors.chol}>
                    <input type="number" name="chol" value={formData.chol} onChange={set} placeholder="mg/dl, e.g., 233" min="0" max="600" />
                </InputCard>
                <InputCard icon="🍬" label="Fasting Blood Sugar > 120" required>
                    <select name="fbs" value={formData.fbs} onChange={set}>
                        <option value="FALSE">No (≤ 120 mg/dl)</option>
                        <option value="TRUE">Yes (&gt; 120 mg/dl)</option>
                    </select>
                </InputCard>
                <InputCard icon="💓" label="Max Heart Rate Achieved" required error={errors.thalch}>
                    <input type="number" name="thalch" value={formData.thalch} onChange={set} placeholder="bpm, e.g., 150" min="60" max="220" />
                </InputCard>
            </Section>

            {/* ── ECG & Diagnostics ── */}
            <Section icon="📈" title="ECG & Diagnostics" subtitle="Electrocardiographic and imaging results">
                <InputCard icon="📊" label="Resting ECG Results" required>
                    <select name="restecg" value={formData.restecg} onChange={set}>
                        <option value="normal">Normal</option>
                        <option value="st-t abnormality">ST-T Wave Abnormality</option>
                        <option value="lv hypertrophy">Left Ventricular Hypertrophy</option>
                    </select>
                </InputCard>
                <InputCard icon="📉" label="ST Depression" required error={errors.oldpeak}>
                    <input type="number" name="oldpeak" value={formData.oldpeak} onChange={set} placeholder="e.g., 2.3" step="0.1" min="-5" max="10" />
                </InputCard>
                <InputCard icon="📐" label="Slope of Peak Exercise ST" required>
                    <select name="slope" value={formData.slope} onChange={set}>
                        <option value="upsloping">Upsloping</option>
                        <option value="flat">Flat</option>
                        <option value="downsloping">Downsloping</option>
                    </select>
                </InputCard>
                <InputCard icon="🫁" label="Major Vessels (0-3)" required>
                    <select name="ca" value={formData.ca} onChange={set}>
                        <option value="0">0</option>
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                    </select>
                </InputCard>
                <InputCard icon="🔬" label="Thalassemia" required>
                    <select name="thal" value={formData.thal} onChange={set}>
                        <option value="normal">Normal</option>
                        <option value="fixed defect">Fixed Defect</option>
                        <option value="reversable defect">Reversible Defect</option>
                    </select>
                </InputCard>
            </Section>

            <div className="med-sticky-footer">
                <button type="submit" className="med-predict-btn" disabled={loading}>
                    {loading ? (<><span className="spinner"></span> Analyzing…</>) : (<>🔍 Predict Heart Disease Risk</>)}
                </button>
            </div>
        </form>
    )
}

export default HeartForm
