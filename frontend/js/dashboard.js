/**
 * HireGenius AI — Dashboard Logic
 * Loads KPIs, charts, activities, and AI insights.
 */

document.addEventListener('DOMContentLoaded', () => {
    initLayout('dashboard', 'Dashboard', 'Home / Dashboard');
    loadDashboard();
});

async function loadDashboard() {
    try {
        const data = await API.get('/analytics/dashboard');
        renderKPIs(data);
        renderRecentActivities(data.recent_activities || []);
        loadCharts();
    } catch (error) {
        console.error('Dashboard load failed:', error);
        showToast('Failed to load dashboard data', 'error');
    }
}

function renderKPIs(data) {
    const kpis = [
        { icon: 'bi-people-fill', color: 'blue', value: data.total_candidates, label: 'Total Candidates' },
        { icon: 'bi-briefcase-fill', color: 'green', value: data.active_jobs, label: 'Active Jobs' },
        { icon: 'bi-person-check-fill', color: 'purple', value: data.shortlisted, label: 'Shortlisted' },
        { icon: 'bi-calendar-event-fill', color: 'orange', value: data.interviews_scheduled, label: 'Interviews' },
        { icon: 'bi-trophy-fill', color: 'cyan', value: data.hired, label: 'Hired' },
    ];

    const grid = document.getElementById('kpiGrid');
    grid.innerHTML = kpis.map((kpi, i) => `
        <div class="kpi-card animate-fade-in-up stagger-${i + 1}">
            <div class="kpi-icon ${kpi.color}"><i class="bi ${kpi.icon}"></i></div>
            <div class="kpi-value" data-target="${kpi.value}">0</div>
            <div class="kpi-label">${kpi.label}</div>
        </div>
    `).join('');

    // Animate counters
    setTimeout(() => {
        document.querySelectorAll('.kpi-value').forEach(el => {
            const target = parseInt(el.dataset.target) || 0;
            animateCounter(el, target);
        });
    }, 200);
}

function renderRecentActivities(activities) {
    const list = document.getElementById('activityList');
    if (!activities.length) {
        list.innerHTML = '<div class="empty-state"><i class="bi bi-inbox"></i><h4>No recent activity</h4><p class="text-muted">Upload resumes to get started</p></div>';
        return;
    }
    list.innerHTML = activities.map(a => `
        <div class="activity-item">
            <div class="activity-dot ${a.status}"></div>
            <div>
                <div class="activity-text">${a.message}</div>
                <div class="activity-time">${timeAgo(a.time)}</div>
            </div>
        </div>
    `).join('');
}

async function loadCharts() {
    try {
        const [funnel, skills] = await Promise.all([
            API.get('/analytics/funnel'),
            API.get('/analytics/skills'),
        ]);
        renderFunnelChart(funnel);
        renderSkillsChart(skills);
    } catch (e) {
        console.warn('Charts failed to load:', e);
    }
}

function renderFunnelChart(data) {
    const ctx = document.getElementById('funnelChart');
    if (!ctx) return;
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['New', 'Screening', 'Interview', 'Offered', 'Hired', 'Rejected'],
            datasets: [{
                label: 'Candidates',
                data: [data.new || 0, data.screening || 0, data.interview || 0,
                       data.offered || 0, data.hired || 0, data.rejected || 0],
                backgroundColor: ['#6366F1', '#3B82F6', '#F59E0B', '#38BDF8', '#10B981', '#EF4444'],
                borderRadius: 8,
                barThickness: 36,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: '#F1F5F9' } },
                x: { grid: { display: false } }
            }
        }
    });
}

function renderSkillsChart(data) {
    const ctx = document.getElementById('skillsChart');
    if (!ctx || !data.length) return;
    const top8 = data.slice(0, 8);
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: top8.map(s => s.skill),
            datasets: [{
                data: top8.map(s => s.count),
                backgroundColor: ['#2563EB','#38BDF8','#10B981','#F59E0B','#EF4444','#6366F1','#EC4899','#14B8A6'],
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { padding: 12, font: { size: 11 } } }
            }
        }
    });
}
