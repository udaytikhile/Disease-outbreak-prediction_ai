import React from 'react'
import '../../styles/body-map.css'
import { REGION_SYMPTOMS } from './constants'

const BodyMap = ({ onSelectSymptoms, activeRegion }) => {
    return (
        <div className="body-map-container">
            <svg viewBox="0 0 200 400" className="human-body-svg">
                {/* HEAD */}
                <g
                    className={`body-region ${activeRegion === 'Head' ? 'active' : ''}`}
                    onClick={() => onSelectSymptoms('Head', REGION_SYMPTOMS['Head'])}
                >
                    <circle cx="100" cy="50" r="30" />
                    <title>Head (Headaches, Dizziness...)</title>
                </g>

                {/* CHEST */}
                <g
                    className={`body-region ${activeRegion === 'Chest' ? 'active' : ''}`}
                    onClick={() => onSelectSymptoms('Chest', REGION_SYMPTOMS['Chest'])}
                >
                    <path d="M 65 90 C 65 80, 135 80, 135 90 L 132 150 C 132 160, 68 160, 68 150 Z" />
                    <title>Chest (Chest Pain, Shortness of Breath...)</title>
                </g>

                {/* ABDOMEN */}
                <g
                    className={`body-region ${activeRegion === 'Abdomen' ? 'active' : ''}`}
                    onClick={() => onSelectSymptoms('Abdomen', REGION_SYMPTOMS['Abdomen'])}
                >
                    <path d="M 68 155 C 68 145, 132 145, 132 155 L 125 215 C 125 225, 75 225, 75 215 Z" />
                    <title>Abdomen (Nausea, Stomach Issues...)</title>
                </g>

                {/* ARMS */}
                <g
                    className={`body-region ${activeRegion === 'Arms' ? 'active' : ''}`}
                    onClick={() => onSelectSymptoms('Arms', REGION_SYMPTOMS['Arms'])}
                >
                    {/* Left Arm */}
                    <rect x="35" y="90" width="25" height="110" rx="12.5" />
                    {/* Right Arm */}
                    <rect x="140" y="90" width="25" height="110" rx="12.5" />
                    <title>Arms (Tingling, Numbness, Pain...)</title>
                </g>

                {/* LEGS */}
                <g
                    className={`body-region ${activeRegion === 'Legs' ? 'active' : ''}`}
                    onClick={() => onSelectSymptoms('Legs', REGION_SYMPTOMS['Legs'])}
                >
                    {/* Left Leg */}
                    <rect x="72" y="222" width="26" height="140" rx="13" />
                    {/* Right Leg */}
                    <rect x="102" y="222" width="26" height="140" rx="13" />
                    <title>Legs (Swelling, Walking issues...)</title>
                </g>
            </svg>

            <div className="body-map-controls">
                <p className="body-map-hint">Click a body region to filter symptoms</p>
                <button
                    type="button"
                    className={`general-symptoms-btn ${activeRegion === 'General' ? 'active' : ''}`}
                    onClick={() => onSelectSymptoms('General', REGION_SYMPTOMS['General'])}
                >
                    🌐 View Full Body / General
                </button>
            </div>
        </div>
    )
}

export default BodyMap
