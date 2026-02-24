/**
 * Shared form building blocks for all prediction forms.
 * Extracted from the 4 duplicate copies in HeartForm, DiabetesForm, KidneyForm, DepressionForm.
 */
import React, { useId } from 'react'

export const InputCard = ({ icon, label, required, error, children }) => {
    const id = useId()
    const errorId = `${id}-error`

    return (
        <div className={`med-input-card${error ? ' has-error' : ''}`}>
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
            {error && <div id={errorId} className="med-card-error" role="alert">⚠️ {error}</div>}
        </div>
    )
}

export const Section = ({ icon, title, subtitle, children }) => (
    <fieldset className="med-form-section">
        <legend className="med-section-header">
            <span className="med-section-icon" aria-hidden="true">{icon}</span>
            <span>
                <span className="med-section-title">{title}</span>
                {subtitle && <span className="med-section-subtitle">{subtitle}</span>}
            </span>
        </legend>
        <div className="med-card-grid">{children}</div>
    </fieldset>
)

export const ProgressBar = ({ percent }) => (
    <div role="progressbar" aria-valuenow={percent} aria-valuemin={0} aria-valuemax={100} aria-label={`Form completion: ${percent}%`}>
        <div className="med-progress-label">
            <span>Form Completion</span>
            <span className="med-progress-pct">{percent}%</span>
        </div>
        <div className="med-progress-bar">
            <div className="med-progress-fill" style={{ width: `${Math.max(percent, 2)}%` }} />
        </div>
    </div>
)

