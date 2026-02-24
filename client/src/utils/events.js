/**
 * Pub/sub for toast events. 
 * Moved here from Toast.jsx/PredictionContext.jsx to satisfy React Fast Refresh.
 */
export const toastEmitter = new EventTarget()

export const showToast = (message, type = 'info', duration = 4000) => {
    toastEmitter.dispatchEvent(new CustomEvent('toast', { detail: { message, type, duration } }))
}
