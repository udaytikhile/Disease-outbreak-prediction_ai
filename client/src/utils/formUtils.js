/**
 * Convert all numeric-looking string values in a form data object to Numbers.
 * Preserves strings that are intentionally categorical (e.g., 'Male', 'TRUE').
 *
 * @param {Object} data - The form data object
 * @param {string[]} stringFields - Field names that should stay as strings
 * @returns {Object} The form data with numeric values properly typed
 */
export const convertNumericFields = (data, stringFields = []) => {
    const converted = {}
    for (const [key, value] of Object.entries(data)) {
        if (stringFields.includes(key) || value === '' || value === null || value === undefined) {
            converted[key] = value
        } else if (!isNaN(value) && value !== '') {
            converted[key] = Number(value)
        } else {
            converted[key] = value
        }
    }
    return converted
}
