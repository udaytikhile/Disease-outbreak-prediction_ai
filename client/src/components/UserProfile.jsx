import { useState, useEffect } from 'react'

const UserProfile = ({ onClose }) => {
    const [profile, setProfile] = useState(() => {
        try {
            const saved = localStorage.getItem('user_profile')
            return saved ? JSON.parse(saved) : {
                name: '',
                age: '',
                gender: 'male',
                bloodGroup: '',
                emergencyContact: '',
                allergies: '',
                medications: '',
                conditions: ''
            }
        } catch (e) {
            console.error('Failed to parse user profile:', e)
            return {
                name: '',
                age: '',
                gender: 'male',
                bloodGroup: '',
                emergencyContact: '',
                allergies: '',
                medications: '',
                conditions: ''
            }
        }
    })
    const [saved, setSaved] = useState(false)

    const handleChange = (e) => {
        setProfile(prev => ({
            ...prev,
            [e.target.name]: e.target.value
        }))
        setSaved(false)
    }

    const handleSave = () => {
        localStorage.setItem('user_profile', JSON.stringify(profile))
        setSaved(true)
        setTimeout(() => setSaved(false), 2000)
    }

    const handleClear = () => {
        if (window.confirm('Clear your profile? This cannot be undone.')) {
            const empty = {
                name: '', age: '', gender: 'male', bloodGroup: '',
                emergencyContact: '', allergies: '', medications: '', conditions: ''
            }
            setProfile(empty)
            localStorage.removeItem('user_profile')
        }
    }

    return (
        <div className="profile-container">
            <div className="profile-header">
                <div>
                    <h2 className="profile-title">👤 My Health Profile</h2>
                    <p className="profile-subtitle">Save your health info for personalized experience</p>
                </div>
                <button className="btn btn-secondary" onClick={onClose} style={{ width: 'auto' }}>
                    ← Back
                </button>
            </div>

            <div className="profile-grid">
                <div className="profile-section">
                    <h3>📋 Personal Information</h3>
                    <div className="form-grid">
                        <div className="form-group">
                            <label htmlFor="profile-name">Full Name</label>
                            <input
                                type="text"
                                id="profile-name"
                                name="name"
                                value={profile.name}
                                onChange={handleChange}
                                placeholder="Enter your name"
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="profile-age">Age</label>
                            <input
                                type="number"
                                id="profile-age"
                                name="age"
                                value={profile.age}
                                onChange={handleChange}
                                placeholder="Enter your age"
                                min="1"
                                max="120"
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="profile-gender">Gender</label>
                            <select id="profile-gender" name="gender" value={profile.gender} onChange={handleChange}>
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label htmlFor="profile-blood">Blood Group</label>
                            <select id="profile-blood" name="bloodGroup" value={profile.bloodGroup} onChange={handleChange}>
                                <option value="">Select</option>
                                <option value="A+">A+</option>
                                <option value="A-">A-</option>
                                <option value="B+">B+</option>
                                <option value="B-">B-</option>
                                <option value="AB+">AB+</option>
                                <option value="AB-">AB-</option>
                                <option value="O+">O+</option>
                                <option value="O-">O-</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div className="profile-section">
                    <h3>🏥 Medical Information</h3>
                    <div className="form-grid">
                        <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                            <label htmlFor="profile-allergies">Known Allergies</label>
                            <input
                                type="text"
                                id="profile-allergies"
                                name="allergies"
                                value={profile.allergies}
                                onChange={handleChange}
                                placeholder="e.g., Penicillin, Peanuts"
                            />
                        </div>
                        <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                            <label htmlFor="profile-meds">Current Medications</label>
                            <input
                                type="text"
                                id="profile-meds"
                                name="medications"
                                value={profile.medications}
                                onChange={handleChange}
                                placeholder="e.g., Metformin, Aspirin"
                            />
                        </div>
                        <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                            <label htmlFor="profile-conditions">Existing Conditions</label>
                            <input
                                type="text"
                                id="profile-conditions"
                                name="conditions"
                                value={profile.conditions}
                                onChange={handleChange}
                                placeholder="e.g., Hypertension, Asthma"
                            />
                        </div>
                    </div>
                </div>

                <div className="profile-section">
                    <h3>📞 Emergency Contact</h3>
                    <div className="form-grid">
                        <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                            <label htmlFor="profile-emergency">Emergency Contact Number</label>
                            <input
                                type="tel"
                                id="profile-emergency"
                                name="emergencyContact"
                                value={profile.emergencyContact}
                                onChange={handleChange}
                                placeholder="Enter emergency contact number"
                            />
                        </div>
                    </div>
                </div>
            </div>

            <div className="profile-actions">
                <button className="btn btn-primary" onClick={handleSave}>
                    {saved ? '✅ Saved!' : '💾 Save Profile'}
                </button>
                <button className="btn btn-secondary" onClick={handleClear} style={{ width: 'auto' }}>
                    🗑️ Clear Profile
                </button>
            </div>

            <div className="profile-privacy">
                <p>🔒 Your data is stored locally on your device and is never sent to any server.</p>
            </div>
        </div>
    )
}

export default UserProfile
