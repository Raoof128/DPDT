/**
 * Data Poisoning Detection Tool - Dashboard JavaScript
 * Handles API interactions, charts, and UI updates
 */

// API Base URL
const API_BASE = '';

// State
const state = {
    scanned: 0,
    threats: 0,
    cleaned: 0,
    avgRisk: 0,
    activities: []
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initForms();
    initCharts();
    checkHealth();
});

// Navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.section');
    const pageTitle = document.getElementById('page-title');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const sectionId = item.dataset.section;

            // Update nav
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            // Update sections
            sections.forEach(s => s.classList.remove('active'));
            document.getElementById(`${sectionId}-section`).classList.add('active');

            // Update title
            const titles = {
                dashboard: 'Dashboard',
                scan: 'Dataset Scanner',
                detect: 'Poison Detection',
                clean: 'Dataset Cleanser',
                risk: 'Risk Analysis',
                docs: 'Documentation'
            };
            pageTitle.textContent = titles[sectionId] || 'Dashboard';
        });
    });
}

// Forms
function initForms() {
    // Scan form
    document.getElementById('scan-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await runScan();
    });

    // Detect form
    document.getElementById('detect-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await runDetection();
    });

    // Clean form
    document.getElementById('clean-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await runCleaning();
    });

    // Risk form
    document.getElementById('risk-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await runRiskAnalysis();
    });

    // Refresh button
    document.getElementById('refresh-btn').addEventListener('click', checkHealth);
}

// Charts
let poisoningChart, methodsChart;

function initCharts() {
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: { color: '#a0a0b0' }
            }
        },
        scales: {
            x: {
                ticks: { color: '#6e6e80' },
                grid: { color: 'rgba(255,255,255,0.05)' }
            },
            y: {
                ticks: { color: '#6e6e80' },
                grid: { color: 'rgba(255,255,255,0.05)' }
            }
        }
    };

    // Poisoning chart
    const poisoningCtx = document.getElementById('poisoning-chart');
    if (poisoningCtx) {
        poisoningChart = new Chart(poisoningCtx, {
            type: 'bar',
            data: {
                labels: ['Run 1', 'Run 2', 'Run 3', 'Run 4', 'Run 5'],
                datasets: [{
                    label: 'Poisoning Score',
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: 'rgba(79, 141, 249, 0.6)',
                    borderColor: '#4f8df9',
                    borderWidth: 1
                }]
            },
            options: chartOptions
        });
    }

    // Methods chart
    const methodsCtx = document.getElementById('methods-chart');
    if (methodsCtx) {
        methodsChart = new Chart(methodsCtx, {
            type: 'doughnut',
            data: {
                labels: ['Spectral', 'Clustering', 'Influence', 'Trigger'],
                datasets: [{
                    data: [25, 25, 25, 25],
                    backgroundColor: [
                        'rgba(79, 141, 249, 0.8)',
                        'rgba(156, 91, 245, 0.8)',
                        'rgba(0, 212, 170, 0.8)',
                        'rgba(255, 140, 66, 0.8)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#a0a0b0', padding: 20 }
                    }
                }
            }
        });
    }
}

// API Functions
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            document.querySelector('.status-indicator').classList.add('online');
            addActivity('System health check passed', 'success');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        document.querySelector('.status-indicator').classList.remove('online');
    }
}

async function runScan() {
    const resultsDiv = document.getElementById('scan-results');
    const contentDiv = document.getElementById('scan-results-content');

    resultsDiv.style.display = 'block';
    contentDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Scanning dataset...</p></div>';

    try {
        const response = await fetch(`${API_BASE}/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                dataset_type: document.getElementById('scan-type').value,
                n_samples: parseInt(document.getElementById('scan-samples').value),
                n_classes: parseInt(document.getElementById('scan-classes').value),
                poison_ratio: parseFloat(document.getElementById('scan-poison').value),
                seed: 42
            })
        });

        const data = await response.json();
        state.scanned++;
        updateStats();

        contentDiv.innerHTML = `
            <div class="result-box">
                <div class="result-header">
                    <h3>Quality Score</h3>
                    <span class="result-score ${data.quality_score < 50 ? 'high' : data.quality_score < 80 ? 'medium' : 'low'}">
                        ${data.quality_score.toFixed(1)}
                    </span>
                </div>
                <div class="result-grid">
                    <div class="result-item">
                        <h4>Status</h4>
                        <p>${data.is_valid ? '✅ Valid' : '❌ Invalid'}</p>
                    </div>
                    <div class="result-item">
                        <h4>Samples</h4>
                        <p>${data.n_samples.toLocaleString()}</p>
                    </div>
                    <div class="result-item">
                        <h4>Classes</h4>
                        <p>${data.n_classes}</p>
                    </div>
                    <div class="result-item">
                        <h4>Anomalies</h4>
                        <p>${data.anomalies.length}</p>
                    </div>
                </div>
                ${data.warnings.length > 0 ? `
                    <div style="margin-top: 16px;">
                        <h4 style="color: var(--accent-orange); margin-bottom: 8px;">⚠️ Warnings</h4>
                        <ul class="recommendations-list">
                            ${data.warnings.map(w => `<li>${w}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;

        addActivity(`Scanned ${data.n_samples} samples - Quality: ${data.quality_score.toFixed(0)}%`,
            data.is_valid ? 'success' : 'warning');

    } catch (error) {
        contentDiv.innerHTML = `<p style="color: var(--accent-red);">Error: ${error.message}</p>`;
        addActivity('Scan failed', 'danger');
    }
}

async function runDetection() {
    const resultsDiv = document.getElementById('detect-results');
    const contentDiv = document.getElementById('detect-results-content');

    resultsDiv.style.display = 'block';
    contentDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Running detection pipeline...</p></div>';

    try {
        const response = await fetch(`${API_BASE}/detect_poison`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                dataset_type: document.getElementById('detect-type').value,
                n_samples: parseInt(document.getElementById('detect-samples').value),
                n_classes: 10,
                poison_ratio: parseFloat(document.getElementById('detect-poison').value),
                seed: 42,
                run_spectral: document.getElementById('method-spectral').checked,
                run_clustering: document.getElementById('method-clustering').checked,
                run_influence: document.getElementById('method-influence').checked,
                run_trigger: document.getElementById('method-trigger').checked
            })
        });

        const data = await response.json();
        state.threats += data.suspected_indices.length;
        updateStats();
        updateCharts(data);

        const scoreClass = data.poisoning_score < 25 ? 'low' : data.poisoning_score < 50 ? 'medium' : 'high';

        contentDiv.innerHTML = `
            <div class="result-box">
                <div class="result-header">
                    <h3>Poisoning Score</h3>
                    <span class="result-score ${scoreClass}">${data.poisoning_score.toFixed(1)}</span>
                </div>
                <div class="result-grid">
                    <div class="result-item">
                        <h4>Suspected Samples</h4>
                        <p>${data.suspected_indices.length}</p>
                    </div>
                    <div class="result-item">
                        <h4>Ground Truth Poisoned</h4>
                        <p>${data.ground_truth_poison_indices.length}</p>
                    </div>
                    <div class="result-item">
                        <h4>Precision</h4>
                        <p>${(data.detection_accuracy.precision * 100).toFixed(1)}%</p>
                    </div>
                    <div class="result-item">
                        <h4>Recall</h4>
                        <p>${(data.detection_accuracy.recall * 100).toFixed(1)}%</p>
                    </div>
                </div>
            </div>
            <div class="result-grid" style="margin-top: 16px;">
                <div class="result-item">
                    <h4>Spectral Score</h4>
                    <p>${data.spectral_result.score.toFixed(1)}</p>
                </div>
                <div class="result-item">
                    <h4>Clustering Score</h4>
                    <p>${data.clustering_result.score.toFixed(1)}</p>
                </div>
                <div class="result-item">
                    <h4>Influence Score</h4>
                    <p>${data.influence_result.score.toFixed(1)}</p>
                </div>
                <div class="result-item">
                    <h4>Trigger Score</h4>
                    <p>${data.trigger_result.score.toFixed(1)}</p>
                </div>
            </div>
        `;

        addActivity(`Detection complete - ${data.suspected_indices.length} suspected samples`,
            data.poisoning_score > 50 ? 'danger' : 'success');

    } catch (error) {
        contentDiv.innerHTML = `<p style="color: var(--accent-red);">Error: ${error.message}</p>`;
        addActivity('Detection failed', 'danger');
    }
}

async function runCleaning() {
    const resultsDiv = document.getElementById('clean-results');
    const contentDiv = document.getElementById('clean-results-content');

    resultsDiv.style.display = 'block';
    contentDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Cleaning dataset...</p></div>';

    try {
        const response = await fetch(`${API_BASE}/clean`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                dataset_type: 'image',
                n_samples: parseInt(document.getElementById('clean-samples').value),
                n_classes: 10,
                poison_ratio: parseFloat(document.getElementById('clean-poison').value),
                seed: 42,
                mode: document.getElementById('clean-mode').value,
                confidence_threshold: parseFloat(document.getElementById('clean-threshold').value)
            })
        });

        const data = await response.json();
        state.cleaned++;
        updateStats();

        contentDiv.innerHTML = `
            <div class="result-box">
                <div class="result-header">
                    <h3>Cleaning Summary</h3>
                    <span class="risk-badge risk-${data.removal_ratio < 0.1 ? 'low' : data.removal_ratio < 0.2 ? 'medium' : 'high'}">
                        Mode: ${data.mode.toUpperCase()}
                    </span>
                </div>
                <div class="result-grid">
                    <div class="result-item">
                        <h4>Original Samples</h4>
                        <p>${data.original_samples.toLocaleString()}</p>
                    </div>
                    <div class="result-item">
                        <h4>Removed</h4>
                        <p>${data.removed_samples}</p>
                    </div>
                    <div class="result-item">
                        <h4>Remaining</h4>
                        <p>${data.remaining_samples.toLocaleString()}</p>
                    </div>
                    <div class="result-item">
                        <h4>Removal Rate</h4>
                        <p>${(data.removal_ratio * 100).toFixed(1)}%</p>
                    </div>
                </div>
                ${data.relabel_suggestions.length > 0 ? `
                    <div style="margin-top: 16px;">
                        <h4 style="margin-bottom: 8px;">Relabel Suggestions</h4>
                        <p style="color: var(--text-muted); font-size: 14px;">
                            ${data.relabel_suggestions.length} samples flagged for potential relabeling
                        </p>
                    </div>
                ` : ''}
            </div>
        `;

        addActivity(`Cleaned dataset - Removed ${data.removed_samples} samples`, 'success');

    } catch (error) {
        contentDiv.innerHTML = `<p style="color: var(--accent-red);">Error: ${error.message}</p>`;
        addActivity('Cleaning failed', 'danger');
    }
}

async function runRiskAnalysis() {
    const resultsDiv = document.getElementById('risk-results');
    const contentDiv = document.getElementById('risk-results-content');

    resultsDiv.style.display = 'block';
    contentDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Analyzing risk...</p></div>';

    try {
        const response = await fetch(`${API_BASE}/collapse_risk`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                dataset_type: 'image',
                n_samples: parseInt(document.getElementById('risk-samples').value),
                n_classes: parseInt(document.getElementById('risk-classes').value),
                poison_ratio: parseFloat(document.getElementById('risk-poison').value),
                seed: 42
            })
        });

        const data = await response.json();
        state.avgRisk = ((state.avgRisk * (state.scanned - 1) + data.collapse_risk_score) / state.scanned) || data.collapse_risk_score;
        updateStats();

        const riskClass = data.risk_level.toLowerCase();

        contentDiv.innerHTML = `
            <div class="result-box">
                <div class="result-header">
                    <h3>Collapse Risk Score</h3>
                    <span class="result-score ${riskClass === 'low' ? 'low' : riskClass === 'critical' ? 'high' : 'medium'}">
                        ${data.collapse_risk_score.toFixed(1)}
                    </span>
                </div>
                <div style="text-align: center; margin: 20px 0;">
                    <span class="risk-badge risk-${riskClass}">${data.risk_level}</span>
                </div>
                <div class="result-grid">
                    ${Object.entries(data.risk_factors).map(([key, value]) => `
                        <div class="result-item">
                            <h4>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                            <p>${(value * 100).toFixed(1)}%</p>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div style="margin-top: 16px;">
                <h4 style="margin-bottom: 12px;">Recommendations</h4>
                <ul class="recommendations-list">
                    ${data.recommendations.map(r => `<li>${r}</li>`).join('')}
                </ul>
            </div>
        `;

        addActivity(`Risk analysis: ${data.risk_level} (${data.collapse_risk_score.toFixed(0)})`,
            riskClass === 'low' ? 'success' : riskClass === 'critical' ? 'danger' : 'warning');

    } catch (error) {
        contentDiv.innerHTML = `<p style="color: var(--accent-red);">Error: ${error.message}</p>`;
        addActivity('Risk analysis failed', 'danger');
    }
}

// UI Updates
function updateStats() {
    document.getElementById('stat-scanned').textContent = state.scanned;
    document.getElementById('stat-threats').textContent = state.threats;
    document.getElementById('stat-cleaned').textContent = state.cleaned;
    document.getElementById('stat-risk').textContent = `${state.avgRisk.toFixed(0)}%`;
}

function updateCharts(data) {
    if (poisoningChart) {
        const labels = poisoningChart.data.labels;
        const scores = poisoningChart.data.datasets[0].data;

        // Shift data
        labels.shift();
        labels.push(`Run ${state.scanned}`);
        scores.shift();
        scores.push(data.poisoning_score);

        poisoningChart.update();
    }

    if (methodsChart && data.spectral_result) {
        methodsChart.data.datasets[0].data = [
            data.spectral_result.score,
            data.clustering_result.score,
            data.influence_result.score,
            data.trigger_result.score
        ];
        methodsChart.update();
    }
}

function addActivity(message, type = 'info') {
    const list = document.getElementById('activity-list');
    const item = document.createElement('li');
    item.className = 'activity-item';
    item.innerHTML = `
        <span class="activity-icon ${type}">${type === 'success' ? '✓' : type === 'danger' ? '✗' : '!'}</span>
        <div class="activity-content">
            <p>${message}</p>
            <span class="activity-time">Just now</span>
        </div>
    `;

    list.insertBefore(item, list.firstChild);

    // Keep only last 10 activities
    while (list.children.length > 10) {
        list.removeChild(list.lastChild);
    }
}
