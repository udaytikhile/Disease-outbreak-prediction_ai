import { useState, useMemo } from 'react'
import { InputCard, Section, ProgressBar } from '../common/FormComponents'
import { convertNumericFields } from '../../utils/formUtils'

const DEPRESSION_STRING_FIELDS = [
    'gender', 'profession', 'sleep_duration', 'dietary_habits',
    'degree', 'suicidal_thoughts', 'family_history'
]

const DepressionForm = ({ onSubmit, loading }) => {
    const [formData, setFormData] = useState({
        gender: 'Male', age: '', profession: 'Student',
        academic_pressure: '3', work_pressure: '0', cgpa: '',
        study_satisfaction: '3', job_satisfaction: '0',
        sleep_duration: '7-8 hours', dietary_habits: 'Moderate',
        degree: 'BSc', suicidal_thoughts: 'No',
        work_study_hours: '', financial_stress: '3', family_history: 'No',
    })
    const [errors, setErrors] = useState({})

    const progress = useMemo(() => {
        const fields = Object.values(formData)
        const filled = fields.filter(v => v !== '').length
        return Math.round((filled / fields.length) * 100)
    }, [formData])

    const validateForm = () => {
        const e = {}
        if (!formData.age || Number(formData.age) < 10 || Number(formData.age) > 80) e.age = '10–80 years'
        if (!formData.cgpa || Number(formData.cgpa) < 0 || Number(formData.cgpa) > 10) e.cgpa = '0–10'
        if (formData.work_study_hours === '' || Number(formData.work_study_hours) < 0 || Number(formData.work_study_hours) > 24) e.work_study_hours = '0–24 hours'
        setErrors(e)
        return Object.keys(e).length === 0
    }

    const set = (ev) => {
        setFormData({ ...formData, [ev.target.name]: ev.target.value })
        if (errors[ev.target.name]) setErrors({ ...errors, [ev.target.name]: '' })
    }

    const handleSubmit = (ev) => {
        ev.preventDefault()
        if (validateForm()) onSubmit(convertNumericFields(formData, DEPRESSION_STRING_FIELDS))
    }

    return (
        <form onSubmit={handleSubmit}>
            <ProgressBar percent={progress} />

            {/* ── Demographics ── */}
            <Section icon="👤" title="Demographics" subtitle="Basic personal information">
                <InputCard icon="⚧" label="Gender" required>
                    <select name="gender" value={formData.gender} onChange={set}>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                    </select>
                </InputCard>
                <InputCard icon="🎂" label="Age" required error={errors.age}>
                    <input type="number" name="age" value={formData.age} onChange={set} placeholder="e.g., 21" min="10" max="80" />
                </InputCard>
                <InputCard icon="💼" label="Profession">
                    <select name="profession" value={formData.profession} onChange={set}>
                        <option value="Student">Student</option>
                        <option value="Working Professional">Working Professional</option>
                        <option value="Other">Other</option>
                    </select>
                </InputCard>
                <InputCard icon="🎓" label="Degree">
                    <select name="degree" value={formData.degree} onChange={set}>
                        <option value="BSc">BSc</option><option value="BA">BA</option>
                        <option value="BCA">BCA</option><option value="B.Com">B.Com</option>
                        <option value="B.Tech">B.Tech</option><option value="B.Pharm">B.Pharm</option>
                        <option value="BBA">BBA</option><option value="B.Ed">B.Ed</option>
                        <option value="M.Tech">M.Tech</option><option value="MSc">MSc</option>
                        <option value="MBA">MBA</option><option value="MCA">MCA</option>
                        <option value="Other">Other</option>
                    </select>
                </InputCard>
            </Section>

            {/* ── Academic & Work ── */}
            <Section icon="📚" title="Academic & Work Life" subtitle="Pressure, satisfaction, and workload">
                <InputCard icon="📖" label="CGPA (0-10)" required error={errors.cgpa}>
                    <input type="number" name="cgpa" value={formData.cgpa} onChange={set} placeholder="e.g., 7.5" step="0.01" min="0" max="10" />
                </InputCard>
                <InputCard icon="⏰" label="Work/Study Hours per Day" required error={errors.work_study_hours}>
                    <input type="number" name="work_study_hours" value={formData.work_study_hours} onChange={set} placeholder="e.g., 6" min="0" max="24" />
                </InputCard>
                <InputCard icon="📝" label="Academic Pressure (0-5)">
                    <select name="academic_pressure" value={formData.academic_pressure} onChange={set}>
                        <option value="0">0 – None</option><option value="1">1 – Very Low</option>
                        <option value="2">2 – Low</option><option value="3">3 – Moderate</option>
                        <option value="4">4 – High</option><option value="5">5 – Very High</option>
                    </select>
                </InputCard>
                <InputCard icon="💼" label="Work Pressure (0-5)">
                    <select name="work_pressure" value={formData.work_pressure} onChange={set}>
                        <option value="0">0 – None</option><option value="1">1 – Very Low</option>
                        <option value="2">2 – Low</option><option value="3">3 – Moderate</option>
                        <option value="4">4 – High</option><option value="5">5 – Very High</option>
                    </select>
                </InputCard>
                <InputCard icon="😊" label="Study Satisfaction (0-5)">
                    <select name="study_satisfaction" value={formData.study_satisfaction} onChange={set}>
                        <option value="0">0 – Very Dissatisfied</option><option value="1">1 – Dissatisfied</option>
                        <option value="2">2 – Slightly</option><option value="3">3 – Neutral</option>
                        <option value="4">4 – Satisfied</option><option value="5">5 – Very Satisfied</option>
                    </select>
                </InputCard>
                <InputCard icon="🏢" label="Job Satisfaction (0-5)">
                    <select name="job_satisfaction" value={formData.job_satisfaction} onChange={set}>
                        <option value="0">0 – Very Dissatisfied</option><option value="1">1 – Dissatisfied</option>
                        <option value="2">2 – Slightly</option><option value="3">3 – Neutral</option>
                        <option value="4">4 – Satisfied</option><option value="5">5 – Very Satisfied</option>
                    </select>
                </InputCard>
            </Section>

            {/* ── Lifestyle ── */}
            <Section icon="🌙" title="Lifestyle & Habits" subtitle="Sleep, diet, and financial well-being">
                <InputCard icon="😴" label="Sleep Duration" required>
                    <select name="sleep_duration" value={formData.sleep_duration} onChange={set}>
                        <option value="Less than 5 hours">Less than 5 hours</option>
                        <option value="5-6 hours">5–6 hours</option>
                        <option value="7-8 hours">7–8 hours</option>
                        <option value="More than 8 hours">More than 8 hours</option>
                        <option value="Others">Others / Irregular</option>
                    </select>
                </InputCard>
                <InputCard icon="🍽️" label="Dietary Habits" required>
                    <select name="dietary_habits" value={formData.dietary_habits} onChange={set}>
                        <option value="Healthy">Healthy</option>
                        <option value="Moderate">Moderate</option>
                        <option value="Unhealthy">Unhealthy</option>
                        <option value="Others">Others</option>
                    </select>
                </InputCard>
                <InputCard icon="💸" label="Financial Stress (0-5)">
                    <select name="financial_stress" value={formData.financial_stress} onChange={set}>
                        <option value="0">0 – None</option><option value="1">1 – Very Low</option>
                        <option value="2">2 – Low</option><option value="3">3 – Moderate</option>
                        <option value="4">4 – High</option><option value="5">5 – Very High</option>
                    </select>
                </InputCard>
            </Section>

            {/* ── Mental Health History ── */}
            <Section icon="🧠" title="Mental Health History" subtitle="Family history and self-assessment">
                <InputCard icon="💭" label="Ever Had Suicidal Thoughts?" required>
                    <select name="suicidal_thoughts" value={formData.suicidal_thoughts} onChange={set}>
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                    </select>
                </InputCard>
                <InputCard icon="👨‍👩‍👧" label="Family History of Mental Illness" required>
                    <select name="family_history" value={formData.family_history} onChange={set}>
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                    </select>
                </InputCard>
            </Section>

            <div className="med-sticky-footer">
                <button type="submit" className="med-predict-btn" disabled={loading}>
                    {loading ? (<><span className="spinner"></span> Analyzing…</>) : (<>🔍 Screen for Depression Risk</>)}
                </button>
            </div>
        </form>
    )
}

export default DepressionForm
