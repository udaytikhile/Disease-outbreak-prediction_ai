import { useState, useMemo } from 'react'
import { InputCard, Section, ProgressBar } from '../common/FormComponents'
import { convertNumericFields } from '../../utils/formUtils'

const KidneyForm = ({ onSubmit, loading }) => {
    const [formData, setFormData] = useState({
        age: '', bp: '', sg: '1.020', al: '0', su: '0',
        rbc: '', pc: '', pcc: '', ba: '',
        bgr: '', bu: '', sc: '', sod: '', pot: '',
        hemo: '', pcv: '', wc: '', rc: '',
        htn: '', dm: '', cad: '', appet: '', pe: '', ane: '',
    })
    const [errors, setErrors] = useState({})

    const progress = useMemo(() => {
        const fields = Object.values(formData)
        const filled = fields.filter(v => v !== '').length
        return Math.round((filled / fields.length) * 100)
    }, [formData])

    const validateField = (name, value) => {
        let error = ''
        if (name === 'age' && (!value || Number(value) < 1 || Number(value) > 120)) error = '1–120 years'
        if (name === 'bp' && (!value || Number(value) < 30 || Number(value) > 200)) error = '30–200 mm Hg'
        if (name === 'hemo' && (!value || Number(value) < 3 || Number(value) > 20)) error = '3–20 g/dL'
        return error
    }

    const validateForm = () => {
        const e = {}
        Object.keys(formData).forEach(key => {
            const err = validateField(key, formData[key])
            if (err) e[key] = err
        })
        setErrors(e)
        return Object.keys(e).length === 0
    }

    const handleBlur = (ev) => {
        const { name, value } = ev.target
        if (name) {
            const error = validateField(name, value)
            setErrors(prev => ({ ...prev, [name]: error }))
        }
    }

    const set = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value })
        if (errors[e.target.name]) setErrors({ ...errors, [e.target.name]: '' })
    }

    const handleSubmit = (e) => {
        e.preventDefault()
        if (validateForm()) onSubmit(convertNumericFields(formData))
    }

    return (
        <form onSubmit={handleSubmit} onBlur={handleBlur}>
            <ProgressBar percent={progress} />

            {/* ── Core Vitals ── */}
            <Section icon="💓" title="Core Vitals" subtitle="Basic patient information">
                <InputCard icon="🎂" label="Age" required error={errors.age}>
                    <input type="number" name="age" value={formData.age} onChange={set} placeholder="e.g., 48" min="1" max="120" />
                </InputCard>
                <InputCard icon="🩸" label="Blood Pressure" required error={errors.bp}>
                    <input type="number" name="bp" value={formData.bp} onChange={set} placeholder="e.g., 80 mm Hg" min="30" max="200" />
                </InputCard>
            </Section>

            {/* ── Urine Analysis ── */}
            <Section icon="🧪" title="Urine Analysis" subtitle="Microscopic and biochemical urine tests">
                <InputCard icon="⚗️" label="Specific Gravity" error={errors.sg}>
                    <select name="sg" value={formData.sg} onChange={set}>
                        <option value="1.005">1.005</option>
                        <option value="1.010">1.010</option>
                        <option value="1.015">1.015</option>
                        <option value="1.020">1.020</option>
                        <option value="1.025">1.025</option>
                    </select>
                </InputCard>
                <InputCard icon="💧" label="Albumin (0-5)" error={errors.al}>
                    <select name="al" value={formData.al} onChange={set}>
                        <option value="0">0 – None</option>
                        <option value="1">1 – Trace</option>
                        <option value="2">2 – Low</option>
                        <option value="3">3 – Moderate</option>
                        <option value="4">4 – High</option>
                        <option value="5">5 – Very High</option>
                    </select>
                </InputCard>
                <InputCard icon="🍬" label="Sugar (0-5)" error={errors.su}>
                    <select name="su" value={formData.su} onChange={set}>
                        <option value="0">0 – None</option>
                        <option value="1">1 – Trace</option>
                        <option value="2">2 – Low</option>
                        <option value="3">3 – Moderate</option>
                        <option value="4">4 – High</option>
                        <option value="5">5 – Very High</option>
                    </select>
                </InputCard>
                <InputCard icon="🔬" label="Red Blood Cells" error={errors.rbc}>
                    <select name="rbc" value={formData.rbc} onChange={set}>
                        <option value="">Unknown</option>
                        <option value="1">Normal</option>
                        <option value="0">Abnormal</option>
                    </select>
                </InputCard>
                <InputCard icon="🦠" label="Pus Cells" error={errors.pc}>
                    <select name="pc" value={formData.pc} onChange={set}>
                        <option value="">Unknown</option>
                        <option value="1">Normal</option>
                        <option value="0">Abnormal</option>
                    </select>
                </InputCard>
                <InputCard icon="🧫" label="Pus Cell Clumps" error={errors.pcc}>
                    <select name="pcc" value={formData.pcc} onChange={set}>
                        <option value="">Unknown</option>
                        <option value="0">Not Present</option>
                        <option value="1">Present</option>
                    </select>
                </InputCard>
                <InputCard icon="🔎" label="Bacteria" error={errors.ba}>
                    <select name="ba" value={formData.ba} onChange={set}>
                        <option value="">Unknown</option>
                        <option value="0">Not Present</option>
                        <option value="1">Present</option>
                    </select>
                </InputCard>
            </Section>

            {/* ── Blood Panel ── */}
            <Section icon="🩺" title="Blood Panel" subtitle="Complete blood chemistry and hematology">
                <InputCard icon="🍩" label="Blood Glucose Random">
                    <input type="number" name="bgr" value={formData.bgr} onChange={set} placeholder="mg/dL, e.g., 121" step="0.1" />
                </InputCard>
                <InputCard icon="💉" label="Blood Urea">
                    <input type="number" name="bu" value={formData.bu} onChange={set} placeholder="mg/dL, e.g., 36" step="0.1" />
                </InputCard>
                <InputCard icon="⚡" label="Serum Creatinine">
                    <input type="number" name="sc" value={formData.sc} onChange={set} placeholder="mg/dL, e.g., 1.2" step="0.1" />
                </InputCard>
                <InputCard icon="🧂" label="Sodium">
                    <input type="number" name="sod" value={formData.sod} onChange={set} placeholder="mEq/L, e.g., 140" step="0.1" />
                </InputCard>
                <InputCard icon="⚡" label="Potassium">
                    <input type="number" name="pot" value={formData.pot} onChange={set} placeholder="mEq/L, e.g., 4.5" step="0.1" />
                </InputCard>
                <InputCard icon="🔴" label="Hemoglobin" required error={errors.hemo}>
                    <input type="number" name="hemo" value={formData.hemo} onChange={set} placeholder="g/dL, e.g., 15.4" step="0.1" min="3" max="20" />
                </InputCard>
                <InputCard icon="📊" label="Packed Cell Volume">
                    <input type="number" name="pcv" value={formData.pcv} onChange={set} placeholder="%, e.g., 44" />
                </InputCard>
                <InputCard icon="⬜" label="White Blood Cell Count">
                    <input type="number" name="wc" value={formData.wc} onChange={set} placeholder="cells/cumm, e.g., 7800" />
                </InputCard>
                <InputCard icon="🔴" label="Red Blood Cell Count">
                    <input type="number" name="rc" value={formData.rc} onChange={set} placeholder="millions/cmm, e.g., 5.2" step="0.1" />
                </InputCard>
            </Section>

            {/* ── Clinical History ── */}
            <Section icon="📋" title="Clinical History" subtitle="Pre-existing conditions and symptoms">
                <InputCard icon="❤️‍🩹" label="Hypertension" error={errors.htn}>
                    <select name="htn" value={formData.htn} onChange={set}>
                        <option value="">Unknown</option><option value="1">Yes</option><option value="0">No</option>
                    </select>
                </InputCard>
                <InputCard icon="🩺" label="Diabetes Mellitus" error={errors.dm}>
                    <select name="dm" value={formData.dm} onChange={set}>
                        <option value="">Unknown</option><option value="1">Yes</option><option value="0">No</option>
                    </select>
                </InputCard>
                <InputCard icon="❤️" label="Coronary Artery Disease" error={errors.cad}>
                    <select name="cad" value={formData.cad} onChange={set}>
                        <option value="">Unknown</option><option value="1">Yes</option><option value="0">No</option>
                    </select>
                </InputCard>
                <InputCard icon="🍽️" label="Appetite" error={errors.appet}>
                    <select name="appet" value={formData.appet} onChange={set}>
                        <option value="">Unknown</option><option value="1">Good</option><option value="0">Poor</option>
                    </select>
                </InputCard>
                <InputCard icon="🦶" label="Pedal Edema" error={errors.pe}>
                    <select name="pe" value={formData.pe} onChange={set}>
                        <option value="">Unknown</option><option value="1">Yes</option><option value="0">No</option>
                    </select>
                </InputCard>
                <InputCard icon="🩸" label="Anemia" error={errors.ane}>
                    <select name="ane" value={formData.ane} onChange={set}>
                        <option value="">Unknown</option><option value="1">Yes</option><option value="0">No</option>
                    </select>
                </InputCard>
            </Section>

            {/* ── Sticky Predict Button ── */}
            <div className="med-sticky-footer">
                <button type="submit" className="med-predict-btn" disabled={loading}>
                    {loading ? (<><span className="spinner"></span> Analyzing…</>) : (<>🔍 Predict Kidney Disease Risk</>)}
                </button>
            </div>
        </form>
    )
}

export default KidneyForm
