// IMPROVED: Added shared Framer Motion variants for staggered field entrance and loading-aware progress animation.
/**
 * Shared form building blocks for all prediction forms.
 * Extracted from the 4 duplicate copies in HeartForm, DiabetesForm, KidneyForm, DepressionForm.
 */
import React, { useId } from 'react'
import { motion } from 'framer-motion'

const FIELD_VARIANTS = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.2, ease: [0.4, 0, 0.2, 1] } },
}

const SECTION_VARIANTS = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
}

export const InputCard = ({ icon, label, required, error, children }) => {
    const id = useId()
    const errorId = `${id}-error`

    return (
        <motion.div className={`med-input-card${error ? ' has-error' : ''}`} variants={FIELD_VARIANTS}>
            <label htmlFor={id} className="med-card-label">
                <span className="med-card-icon" aria-hidden="true">{icon}</span>
                <span className="med-card-label-text">
                    {label}{required && <span className="med-required" aria-hidden="true">*</span>}
                    {required && <span className="sr-only"> (required)</span>}
                </span>
            </label>
            {React.Children.map(children, child =>
                React.isValidElement(child)
                    ? React.cloneElement(child, {
                        id,
                        'aria-required': required || undefined,
                        'aria-invalid': error ? true : undefined,
                        'aria-describedby': error ? errorId : undefined,
                    })
                    : child
            )}
            {error && <div id={errorId} className="med-card-error med-field-error-shake" role="alert">⚠️ {error}</div>}
        </motion.div>
    )
}

export const Section = ({ icon, title, subtitle, children }) => (
    <motion.fieldset className="med-form-section" variants={SECTION_VARIANTS} initial="hidden" animate="visible">
        <legend className="med-section-header">
            <span className="med-section-icon" aria-hidden="true">{icon}</span>
            <span>
                <span className="med-section-title">{title}</span>
                {subtitle && <span className="med-section-subtitle">{subtitle}</span>}
            </span>
        </legend>
        <div className="med-card-grid">{children}</div>
    </motion.fieldset>
)

export const ProgressBar = ({ percent, loading = false }) => (
    <div role="progressbar" aria-valuenow={percent} aria-valuemin={0} aria-valuemax={100} aria-label={`Form completion: ${percent}%`}>
        <div className="med-progress-label">
            <span>Form Completion</span>
            <span className="med-progress-pct">{percent}%</span>
        </div>
        <div className="med-progress-bar">
            <motion.div className={`med-progress-fill ${loading ? 'is-loading' : ''}`} layoutId="prediction-progress" style={{ width: `${Math.max(percent, 2)}%` }} />
        </div>
    </div>
)

