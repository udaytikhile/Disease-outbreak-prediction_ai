import { usePredictionHistory } from '../hooks/usePredictionHistory'
import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'

const Dashboard = ({ onClose }) => {
    const { history, statistics: stats, exportAsCSV, exportAsJSON } = usePredictionHistory()
    const [timeFilter, setTimeFilter] = useState('all')
    const [diseaseFilter, setDiseaseFilter] = useState('all')

    const MotionDiv = motion.div

    const diseaseOptions = Array.from(new Set(history.map(p => p.disease))).filter(Boolean)

    // #1: Memoize time-filtered history
    const timeFiltered = useMemo(() => {
        if (timeFilter === 'all') return history
        // Avoid Date.now() lint: use Date object for current timestamp.
        const now = +new Date()
        const days = { week: 7, month: 30, '3months': 90 }[timeFilter]
        const cutoffMs = days * 86_400_000
        return history.filter(p => now - new Date(p.timestamp).getTime() <= cutoffMs)
    }, [history, timeFilter])

    const filtered = useMemo(() =>
        diseaseFilter === 'all'
            ? timeFiltered
            : timeFiltered.filter(p => p.disease === diseaseFilter)
        , [timeFiltered, diseaseFilter])

    // #2: Memoize chart data and maxTotal together
    const { chartData, maxTotal } = useMemo(() => {
        if (filtered.length === 0) return { chartData: [], maxTotal: 1 }
        const grouped = {}
        filtered.forEach(p => {
            const date = new Date(p.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
            if (!grouped[date]) grouped[date] = { high: 0, low: 0, total: 0, confSum: 0 }
            grouped[date].total++
            if (p.risk_level === 'High') grouped[date].high++
            else grouped[date].low++
            if (p.confidence) grouped[date].confSum += p.confidence
        })
        const data = Object.entries(grouped)
            .map(([date, d]) => ({ date, ...d, avgConf: d.confSum / d.total }))
            .slice(-10)
        return { chartData: data, maxTotal: Math.max(...data.map(d => d.total), 1) }
    }, [filtered])

    // Calculate disease distribution for donut-style display
    const diseaseColors = {
        'Heart Disease': '#ef4444',
        'Diabetes': '#3b82f6',
        'Kidney Disease': '#10b981',
        'Depression': '#8b5cf6'
    }

    const totalFiltered = filtered.length
    const highRiskFiltered = filtered.filter(p => p.risk_level === 'High').length
    const lowRiskFiltered = filtered.filter(p => p.risk_level === 'Low').length

    const validConfPredictions = filtered.filter(p => typeof p.confidence === 'number')
    const avgConfFiltered = validConfPredictions.length > 0
        ? (validConfPredictions.reduce((sum, p) => sum + p.confidence, 0) / validConfPredictions.length)
        : 0

    // Recent trend
    const recentTrend = () => {
        if (filtered.length < 2) return 'neutral'
        const recent = filtered.slice(0, 5)
        const highCount = recent.filter(p => p.risk_level === 'High').length
        if (highCount >= 3) return 'worsening'
        if (highCount <= 1) return 'improving'
        return 'stable'
    }

    const trend = recentTrend()
    const trendInfo = {
        improving: { icon: '📈', text: 'Improving', color: '#22c55e' },
        stable: { icon: '➡️', text: 'Stable', color: '#f59e0b' },
        worsening: { icon: '📉', text: 'Needs Attention', color: '#ef4444' },
        neutral: { icon: '➖', text: 'Not enough data', color: '#6b7280' }
    }

    return (
        <div className="dashboard-container">
            <div className="dashboard-header">
                <div>
                    <h2 className="dashboard-title"><span aria-hidden="true">📊</span> Health Analytics Dashboard</h2>
                    <p className="dashboard-subtitle">Visual insights from your prediction history</p>
                </div>
                <div className="dashboard-actions">
                    <select
                        className="time-filter"
                        value={diseaseFilter}
                        onChange={(e) => setDiseaseFilter(e.target.value)}
                        aria-label="Filter by disease"
                    >
                        <option value="all">All Diseases</option>
                        {diseaseOptions.map((disease) => (
                            <option key={disease} value={disease}>{disease}</option>
                        ))}
                    </select>
                    <select
                        className="time-filter"
                        value={timeFilter}
                        onChange={(e) => setTimeFilter(e.target.value)}
                        aria-label="Filter by time period"
                    >
                        <option value="all">All Time</option>
                        <option value="week">Last 7 Days</option>
                        <option value="month">Last 30 Days</option>
                        <option value="3months">Last 3 Months</option>
                    </select>
                    <button
                        className="btn btn-secondary"
                        type="button"
                        onClick={exportAsCSV}
                        style={{ width: 'auto' }}
                        aria-label="Export predictions as CSV file"
                    >
                        ⬇️ Export CSV
                    </button>
                    <button
                        className="btn btn-secondary"
                        type="button"
                        onClick={exportAsJSON}
                        style={{ width: 'auto' }}
                        aria-label="Export predictions as JSON file"
                    >
                        ⬇️ Export JSON
                    </button>
                    <button className="btn btn-secondary" onClick={onClose} style={{ width: 'auto' }} aria-label="Back to Home">
                        ← Back to Home
                    </button>
                </div>
            </div>

            {totalFiltered === 0 ? (
                <div className="empty-dashboard">
                    <div className="empty-dashboard-icon">📊</div>
                    <h3>No Data Yet</h3>
                    <p>Make some predictions to see your analytics dashboard come alive!</p>
                </div>
            ) : (
                <>
                    {/* Summary Cards */}
                    {/* #3: CSS modifier classes instead of inline styles */}
                    <MotionDiv
                        className="dashboard-stats"
                        initial="hidden"
                        animate="visible"
                        variants={{
                            hidden: { opacity: 0 },
                            visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
                        }}
                    >
                        <MotionDiv className="dash-stat-card" variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}>
                            <div className="dash-stat-icon dash-stat-icon--primary" aria-hidden="true">🧬</div>
                            <div className="dash-stat-info">
                                <div className="dash-stat-number">{totalFiltered}</div>
                                <div className="dash-stat-label">Total Predictions</div>
                            </div>
                        </MotionDiv>
                        <MotionDiv className="dash-stat-card" variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}>
                            <div className="dash-stat-icon dash-stat-icon--danger">⚠️</div>
                            <div className="dash-stat-info">
                                <div className="dash-stat-number">{highRiskFiltered}</div>
                                <div className="dash-stat-label">High Risk</div>
                            </div>
                        </MotionDiv>
                        <MotionDiv className="dash-stat-card" variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}>
                            <div className="dash-stat-icon dash-stat-icon--success">✅</div>
                            <div className="dash-stat-info">
                                <div className="dash-stat-number">{lowRiskFiltered}</div>
                                <div className="dash-stat-label">Low Risk</div>
                            </div>
                        </MotionDiv>
                        <MotionDiv className="dash-stat-card" variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}>
                            <div className="dash-stat-icon dash-stat-icon--warning">🎯</div>
                            <div className="dash-stat-info">
                                <div className="dash-stat-number">{avgConfFiltered.toFixed(1)}%</div>
                                <div className="dash-stat-label">Avg Confidence</div>
                            </div>
                        </MotionDiv>
                    </MotionDiv>

                    {/* Charts Row */}
                    <MotionDiv
                        className="dashboard-charts-row"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                    >
                        {/* Bar Chart */}
                        <div className="dashboard-chart-card">
                            <h3>📊 Prediction Activity</h3>
                            {chartData.length > 0 ? (
                                <div className="bar-chart" role="img" aria-label={`Bar chart showing prediction activity: ${chartData.map(d => `${d.date}: ${d.high} high risk, ${d.low} low risk`).join('; ')}`}>
                                    <div className="bar-chart-bars">
                                        {chartData.map((d, i) => (
                                            <div key={i} className="bar-group">
                                                <div className="bar-wrapper">
                                                    <MotionDiv
                                                        className="bar bar-high"
                                                        initial={{ height: 0 }}
                                                        animate={{ height: `${(d.high / maxTotal) * 100}%` }}
                                                        transition={{ duration: 0.8, delay: i * 0.05 + 0.3 }}
                                                        title={`${d.high} high risk`}
                                                    ></MotionDiv>
                                                    <MotionDiv
                                                        className="bar bar-low"
                                                        initial={{ height: 0 }}
                                                        animate={{ height: `${(d.low / maxTotal) * 100}%` }}
                                                        transition={{ duration: 0.8, delay: i * 0.05 + 0.3 }}
                                                        title={`${d.low} low risk`}
                                                    ></MotionDiv>
                                                </div>
                                                <span className="bar-label">{d.date}</span>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="chart-legend">
                                        <span><span className="legend-box" style={{ background: '#ef4444' }}></span> High Risk</span>
                                        <span><span className="legend-box" style={{ background: '#22c55e' }}></span> Low Risk</span>
                                    </div>
                                </div>
                            ) : (
                                <p className="no-chart-data">No data for chart</p>
                            )}
                        </div>

                        {/* Disease Distribution */}
                        <div className="dashboard-chart-card">
                            <h3>🧬 Disease Distribution</h3>
                            <div className="donut-chart-container">
                                {Object.entries(stats.byDisease).length > 0 ? (
                                    <div className="disease-distribution">
                                        {Object.entries(stats.byDisease).map(([disease, count], i) => {
                                            const pct = ((count / totalFiltered) * 100).toFixed(0)
                                            return (
                                                <MotionDiv
                                                    key={disease}
                                                    className="distribution-item"
                                                    initial={{ opacity: 0, x: -20 }}
                                                    animate={{ opacity: 1, x: 0 }}
                                                    transition={{ delay: i * 0.15 + 0.3 }}
                                                >
                                                    <div className="distribution-bar-container">
                                                        <div className="distribution-header">
                                                            <span className="distribution-name">{disease}</span>
                                                            <span className="distribution-pct">{pct}%</span>
                                                        </div>
                                                        <div className="distribution-bar-bg">
                                                            <MotionDiv
                                                                className="distribution-bar-fill"
                                                                initial={{ width: 0 }}
                                                                animate={{ width: `${pct}%` }}
                                                                transition={{ duration: 1, ease: 'easeOut', delay: i * 0.15 + 0.5 }}
                                                                style={{
                                                                    background: diseaseColors[disease] || '#6366f1'
                                                                }}
                                                            ></MotionDiv>
                                                        </div>
                                                        <span className="distribution-count">{count} prediction{count !== 1 ? 's' : ''}</span>
                                                    </div>
                                                </MotionDiv>
                                            )
                                        })}
                                    </div>
                                ) : (
                                    <p className="no-chart-data">No disease data</p>
                                )}
                            </div>
                        </div>
                    </MotionDiv>

                    {/* Trend & Insights */}
                    <div className="dashboard-insights">
                        <div className="insight-card">
                            <div className="insight-header">
                                <span className="insight-icon">{trendInfo[trend].icon}</span>
                                <h3>Health Trend</h3>
                            </div>
                            <p className="insight-value" style={{ color: trendInfo[trend].color }}>
                                {trendInfo[trend].text}
                            </p>
                            <p className="insight-detail">Based on your last 5 predictions</p>
                        </div>

                        <div className="insight-card">
                            <div className="insight-header">
                                <span className="insight-icon">🏆</span>
                                <h3>Most Checked</h3>
                            </div>
                            <p className="insight-value">
                                {Object.entries(stats.byDisease).sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A'}
                            </p>
                            <p className="insight-detail">Your most frequently assessed disease</p>
                        </div>

                        <div className="insight-card">
                            <div className="insight-header">
                                <span className="insight-icon">📅</span>
                                <h3>Last Prediction</h3>
                            </div>
                            <p className="insight-value">
                                {filtered[0]
                                    ? new Date(filtered[0].timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
                                    : 'N/A'}
                            </p>
                            <p className="insight-detail">{filtered[0]?.disease || ''} — {filtered[0]?.risk_level || ''} Risk</p>
                        </div>

                        <div className="insight-card">
                            <div className="insight-header">
                                <span className="insight-icon">💡</span>
                                <h3>AI Insight</h3>
                            </div>
                            <p className="insight-value" style={{ fontSize: '1rem', lineHeight: '1.5' }}>
                                {highRiskFiltered > lowRiskFiltered
                                    ? 'Consider scheduling a health checkup. Multiple high-risk predictions detected.'
                                    : highRiskFiltered === 0
                                        ? 'Great job! No high-risk predictions. Keep maintaining your healthy lifestyle.'
                                        : 'Your results are mixed. Focus on prevention for high-risk areas.'}
                            </p>
                        </div>
                    </div>
                </>
            )}
        </div>
    )
}

export default Dashboard
