import { useState, useMemo } from 'react'
import { InputCard, Section, ProgressBar } from '../common/FormComponents'
import { convertNumericFields } from '../../utils/formUtils'

const DiabetesForm = ({ onSubmit, loading }) => {
    const [formData, setFormData] = useState({
        HighBP: '0', HighChol: '0', CholCheck: '1', BMI: '', Smoker: '0',
        Stroke: '0', HeartDiseaseorAttack: '0', PhysActivity: '1',
        Fruits: '1', Veggies: '1', HvyAlcoholConsump: '0',
        AnyHealthcare: '1', NoDocbcCost: '0', GenHlth: '3',
        MentHlth: '', PhysHlth: '', DiffWalk: '0',
        Sex: '1', Age: '5', Education: '4', Income: '5',
    })
    const [errors, setErrors] = useState({})

    const progress = useMemo(() => {
        const fields = Object.values(formData)
        const filled = fields.filter(v => v !== '').length
        return Math.round((filled / fields.length) * 100)
    }, [formData])

    const validateField = (name, value) => {
        let error = ''
        if (name === 'BMI' && (!value || Number(value) < 10 || Number(value) > 100)) error = '10–100'
        if (name === 'MentHlth' && (value === '' || Number(value) < 0 || Number(value) > 30)) error = '0–30 days'
        if (name === 'PhysHlth' && (value === '' || Number(value) < 0 || Number(value) > 30)) error = '0–30 days'
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

    const set = (ev) => {
        setFormData({ ...formData, [ev.target.name]: ev.target.value })
        if (errors[ev.target.name]) setErrors({ ...errors, [ev.target.name]: '' })
    }

    const handleSubmit = (ev) => {
        ev.preventDefault()
        if (validateForm()) onSubmit(convertNumericFields(formData))
    }

    return (
        <form onSubmit={handleSubmit} onBlur={handleBlur}>
            <ProgressBar percent={progress} />

            {/* ── Demographics ── */}
            <Section icon="👤" title="Demographics" subtitle="Age, sex, and socioeconomic factors">
                <InputCard icon="⚧" label="Sex" required error={errors.Sex}>
                    <select name="Sex" value={formData.Sex} onChange={set}>
                        <option value="1">Male</option>
                        <option value="0">Female</option>
                    </select>
                </InputCard>
                <InputCard icon="🎂" label="Age Category" required error={errors.Age}>
                    <select name="Age" value={formData.Age} onChange={set}>
                        <option value="1">18–24</option><option value="2">25–29</option>
                        <option value="3">30–34</option><option value="4">35–39</option>
                        <option value="5">40–44</option><option value="6">45–49</option>
                        <option value="7">50–54</option><option value="8">55–59</option>
                        <option value="9">60–64</option><option value="10">65–69</option>
                        <option value="11">70–74</option><option value="12">75–79</option>
                        <option value="13">80+</option>
                    </select>
                </InputCard>
                <InputCard icon="🎓" label="Education Level" required error={errors.Education}>
                    <select name="Education" value={formData.Education} onChange={set}>
                        <option value="1">Never Attended</option>
                        <option value="2">Elementary</option>
                        <option value="3">Some High School</option>
                        <option value="4">High School Graduate</option>
                        <option value="5">Some College</option>
                        <option value="6">College Graduate</option>
                    </select>
                </InputCard>
                <InputCard icon="💰" label="Income Level" required error={errors.Income}>
                    <select name="Income" value={formData.Income} onChange={set}>
                        <option value="1">{"< $10K"}</option>
                        <option value="2">$10K – $15K</option>
                        <option value="3">$15K – $20K</option>
                        <option value="4">$20K – $25K</option>
                        <option value="5">$25K – $35K</option>
                        <option value="6">$35K – $50K</option>
                        <option value="7">$50K – $75K</option>
                        <option value="8">$75K+</option>
                    </select>
                </InputCard>
            </Section>

            {/* ── Body & Fitness ── */}
            <Section icon="🏋️" title="Body & Fitness" subtitle="BMI, physical activity, and diet habits">
                <InputCard icon="⚖️" label="BMI (Body Mass Index)" required error={errors.BMI}>
                    <input type="number" name="BMI" value={formData.BMI} onChange={set} placeholder="e.g., 26" step="0.1" min="10" max="100" />
                </InputCard>
                <InputCard icon="🏃" label="Physical Activity (past 30 days)" required error={errors.PhysActivity}>
                    <select name="PhysActivity" value={formData.PhysActivity} onChange={set}>
                        <option value="1">Yes</option><option value="0">No</option>
                    </select>
                </InputCard>
                <InputCard icon="🍎" label="Eat Fruit Daily" required error={errors.Fruits}>
                    <select name="Fruits" value={formData.Fruits} onChange={set}>
                        <option value="1">Yes</option><option value="0">No</option>
                    </select>
                </InputCard>
                <InputCard icon="🥦" label="Eat Vegetables Daily" required error={errors.Veggies}>
                    <select name="Veggies" value={formData.Veggies} onChange={set}>
                        <option value="1">Yes</option><option value="0">No</option>
                    </select>
                </InputCard>
                <InputCard icon="🚬" label="Smoked 100+ Cigarettes" required error={errors.Smoker}>
                    <select name="Smoker" value={formData.Smoker} onChange={set}>
                        <option value="0">No</option><option value="1">Yes</option>
                    </select>
                </InputCard>
                <InputCard icon="🍺" label="Heavy Alcohol Consumption" required error={errors.HvyAlcoholConsump}>
                    <select name="HvyAlcoholConsump" value={formData.HvyAlcoholConsump} onChange={set}>
                        <option value="0">No</option><option value="1">Yes</option>
                    </select>
                </InputCard>
            </Section>

            {/* ── Medical History ── */}
            <Section icon="🏥" title="Medical History" subtitle="Chronic conditions and risk factors">
                <InputCard icon="🩸" label="High Blood Pressure" required error={errors.HighBP}>
                    <select name="HighBP" value={formData.HighBP} onChange={set}>
                        <option value="0">No</option><option value="1">Yes</option>
                    </select>
                </InputCard>
                <InputCard icon="🧪" label="High Cholesterol" required error={errors.HighChol}>
                    <select name="HighChol" value={formData.HighChol} onChange={set}>
                        <option value="0">No</option><option value="1">Yes</option>
                    </select>
                </InputCard>
                <InputCard icon="📋" label="Cholesterol Check (5 yr)" required error={errors.CholCheck}>
                    <select name="CholCheck" value={formData.CholCheck} onChange={set}>
                        <option value="1">Yes</option><option value="0">No</option>
                    </select>
                </InputCard>
                <InputCard icon="⚡" label="Ever Had a Stroke" required error={errors.Stroke}>
                    <select name="Stroke" value={formData.Stroke} onChange={set}>
                        <option value="0">No</option><option value="1">Yes</option>
                    </select>
                </InputCard>
                <InputCard icon="❤️" label="Heart Disease / Attack" required error={errors.HeartDiseaseorAttack}>
                    <select name="HeartDiseaseorAttack" value={formData.HeartDiseaseorAttack} onChange={set}>
                        <option value="0">No</option><option value="1">Yes</option>
                    </select>
                </InputCard>
                <InputCard icon="🚶" label="Difficulty Walking" required error={errors.DiffWalk}>
                    <select name="DiffWalk" value={formData.DiffWalk} onChange={set}>
                        <option value="0">No</option><option value="1">Yes</option>
                    </select>
                </InputCard>
            </Section>

            {/* ── Health Status ── */}
            <Section icon="📊" title="Health Status" subtitle="Self-reported health and healthcare access">
                <InputCard icon="⭐" label="General Health (1-5)" required error={errors.GenHlth}>
                    <select name="GenHlth" value={formData.GenHlth} onChange={set}>
                        <option value="1">1 – Excellent</option>
                        <option value="2">2 – Very Good</option>
                        <option value="3">3 – Good</option>
                        <option value="4">4 – Fair</option>
                        <option value="5">5 – Poor</option>
                    </select>
                </InputCard>
                <InputCard icon="🧠" label="Mental Health (bad days)" required error={errors.MentHlth}>
                    <input type="number" name="MentHlth" value={formData.MentHlth} onChange={set} placeholder="Days in past 30, 0–30" min="0" max="30" />
                </InputCard>
                <InputCard icon="💪" label="Physical Health (bad days)" required error={errors.PhysHlth}>
                    <input type="number" name="PhysHlth" value={formData.PhysHlth} onChange={set} placeholder="Days in past 30, 0–30" min="0" max="30" />
                </InputCard>
                <InputCard icon="🏥" label="Have Health Insurance" required error={errors.AnyHealthcare}>
                    <select name="AnyHealthcare" value={formData.AnyHealthcare} onChange={set}>
                        <option value="1">Yes</option><option value="0">No</option>
                    </select>
                </InputCard>
                <InputCard icon="💸" label="Couldn't See Doctor (Cost)" required error={errors.NoDocbcCost}>
                    <select name="NoDocbcCost" value={formData.NoDocbcCost} onChange={set}>
                        <option value="0">No</option><option value="1">Yes</option>
                    </select>
                </InputCard>
            </Section>

            <div className="med-sticky-footer">
                <button type="submit" className="med-predict-btn" disabled={loading}>
                    {loading ? (<><span className="spinner"></span> Analyzing…</>) : (<>🔍 Predict Diabetes Risk</>)}
                </button>
            </div>
        </form>
    )
}

export default DiabetesForm
