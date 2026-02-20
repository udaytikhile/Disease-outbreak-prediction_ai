import { usePredictionHistory } from '../hooks/usePredictionHistory'
import { useState } from 'react'

const Dashboard = ({ onClose }) => {
    const { history, getStatistics } = usePredictionHistory()
    const stats = getStatistics()
    const [timeFilter, setTimeFilter] = useState('all')

    const getFilteredHistory = () => {
        if (timeFilter === 'all') return history
        const now = new Date()
        const filters = {
            'week': 7,
            'month': 30,
            '3months': 90
        }
        const days = filters[timeFilter]
        return history.filter(p => {
            const diff = (now - new Date(p.timestamp)) / (1000 * 60 * 60 * 24)
            return diff <= days
        })
    }

    const filtered = getFilteredHistory()

    // Calculate time-series data for the chart
    const getChartData = () => {
        if (filtered.length === 0) return []

        const grouped = {}
        filtered.forEach(p => {
            const date = new Date(p.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
            if (!grouped[date]) grouped[date] = { high: 0, low: 0, total: 0, avgConf: 0, confSum: 0 }
            grouped[date].total++
            if (p.risk_level === 'High') grouped[date].high++
            else grouped[date].low++
            if (p.confidence) grouped[date].confSum += p.confidence
        })

        return Object.entries(grouped).map(([date, data]) => ({
            date,
            ...data,
            avgConf: data.confSum / data.total
        })).slice(-10) // Last 10 data points
    }

    const chartData = getChartData()
    const maxTotal = Math.max(...chartData.map(d => d.total), 1)

    // Calculate disease distribution for donut-style display
    const diseaseColors = {
        'Heart Disease': '#ef4444',
        'Diabetes': '#6366f1',
        "Parkinson's Disease": '#a855f7'
    }

    const totalFiltered = filtered.length
    const highRiskFiltered = filtered.filter(p => p.risk_level === 'High').length
    const lowRiskFiltered = filtered.filter(p => p.risk_level === 'Low').length
    const avgConfFiltered = totalFiltered > 0
        ? (filtered.reduce((sum, p) => sum + (p.confidence || 0), 0) / totalFiltered)
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
                    <h2 className="dashboard-title">📊 Health Analytics Dashboard</h2>
                    <p className="dashboard-subtitle">Visual insights from your prediction history</p>
                </div>
                <div className="dashboard-actions">
                    <select
                        className="time-filter"
                        value={timeFilter}
                        onChange={(e) => setTimeFilter(e.target.value)}
                    >
                        <option value="all">All Time</option>
                        <option value="week">Last 7 Days</option>
                        <option value="month">Last 30 Days</option>
                        <option value="3months">Last 3 Months</option>
                    </select>
                    <button className="btn btn-secondary" onClick={onClose} style={{ width: 'auto' }}>
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
                    <div className="dashboard-stats">
                        <div className="dash-stat-card">
                            <div className="dash-stat-icon" style={{ background: 'linear-gradient(135deg, #6366f1, #7c3aed)' }}>🧬</div>
                            <div className="dash-stat-info">
                                <div className="dash-stat-number">{totalFiltered}</div>
                                <div className="dash-stat-label">Total Predictions</div>
                            </div>
                        </div>
                        <div className="dash-stat-card">
                            <div className="dash-stat-icon" style={{ background: 'linear-gradient(135deg, #ef4444, #f87171)' }}>⚠️</div>
                            <div className="dash-stat-info">
                                <div className="dash-stat-number">{highRiskFiltered}</div>
                                <div className="dash-stat-label">High Risk</div>
                            </div>
                        </div>
                        <div className="dash-stat-card">
                            <div className="dash-stat-icon" style={{ background: 'linear-gradient(135deg, #22c55e, #4ade80)' }}>✅</div>
                            <div className="dash-stat-info">
                                <div className="dash-stat-number">{lowRiskFiltered}</div>
                                <div className="dash-stat-label">Low Risk</div>
                            </div>
                        </div>
                        <div className="dash-stat-card">
                            <div className="dash-stat-icon" style={{ background: 'linear-gradient(135deg, #f59e0b, #fbbf24)' }}>🎯</div>
                            <div className="dash-stat-info">
                                <div className="dash-stat-number">{avgConfFiltered.toFixed(1)}%</div>
                                <div className="dash-stat-label">Avg Confidence</div>
                            </div>
                        </div>
                    </div>

                    {/* Charts Row */}
                    <div className="dashboard-charts-row">
                        {/* Bar Chart */}
                        <div className="dashboard-chart-card">
                            <h3>📊 Prediction Activity</h3>
                            {chartData.length > 0 ? (
                                <div className="bar-chart">
                                    <div className="bar-chart-bars">
                                        {chartData.map((d, i) => (
                                            <div key={i} className="bar-group">
                                                <div className="bar-wrapper">
                                                    <div
                                                        className="bar bar-high"
                                                        style={{ height: `${(d.high / maxTotal) * 100}%` }}
                                                        title={`${d.high} high risk`}
                                                    ></div>
                                                    <div
                                                        className="bar bar-low"
                                                        style={{ height: `${(d.low / maxTotal) * 100}%` }}
                                                        title={`${d.low} low risk`}
                                                    ></div>
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
                                                <div key={disease} className="distribution-item" style={{ animationDelay: `${i * 0.15}s` }}>
                                                    <div className="distribution-bar-container">
                                                        <div className="distribution-header">
                                                            <span className="distribution-name">{disease}</span>
                                                            <span className="distribution-pct">{pct}%</span>
                                                        </div>
                                                        <div className="distribution-bar-bg">
                                                            <div
                                                                className="distribution-bar-fill"
                                                                style={{
                                                                    width: `${pct}%`,
                                                                    background: diseaseColors[disease] || '#6366f1'
                                                                }}
                                                            ></div>
                                                        </div>
                                                        <span className="distribution-count">{count} prediction{count !== 1 ? 's' : ''}</span>
                                                    </div>
                                                </div>
                                            )
                                        })}
                                    </div>
                                ) : (
                                    <p className="no-chart-data">No disease data</p>
                                )}
                            </div>
                        </div>
                    </div>

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
