/**
 * HireGenius AI — Analytics Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    initLayout('analytics', 'Analytics', 'Insights / Analytics');
    loadAnalytics();
});

async function loadAnalytics() {
    try {
        const [funnel, trends, skills, departments, insights] = await Promise.all([
            API.get('/analytics/funnel'),
            API.get('/analytics/trends'),
            API.get('/analytics/skills'),
            API.get('/analytics/departments'),
            API.get('/analytics/insights'),
        ]);
        renderFunnel(funnel);
        renderTrends(trends);
        renderSkills(skills);
        renderDepartments(departments);
        renderInsights(insights);
    } catch (e) { showToast('Failed to load analytics', 'error'); }
}

function renderFunnel(data) {
    const ctx = document.getElementById('funnelAnalytics');
    if (!ctx) return;
    new Chart(ctx, {
        type: 'bar', data: {
            labels: ['New', 'Screening', 'Interview', 'Offered', 'Hired', 'Rejected'],
            datasets: [{ data: [data.new||0, data.screening||0, data.interview||0, data.offered||0, data.hired||0, data.rejected||0],
                backgroundColor: ['#6366F1','#3B82F6','#F59E0B','#38BDF8','#10B981','#EF4444'], borderRadius: 8, barThickness: 40 }]
        }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, grid: { color: '#F1F5F9' } }, x: { grid: { display: false } } } }
    });
}

function renderTrends(data) {
    const ctx = document.getElementById('trendsChart');
    if (!ctx || !data.length) return;
    new Chart(ctx, {
        type: 'line', data: {
            labels: data.map(d => d.period),
            datasets: [
                { label: 'Applied', data: data.map(d => d.applied), borderColor: '#2563EB', tension: 0.3, fill: false },
                { label: 'Hired', data: data.map(d => d.hired), borderColor: '#10B981', tension: 0.3, fill: false },
                { label: 'Rejected', data: data.map(d => d.rejected), borderColor: '#EF4444', tension: 0.3, fill: false },
            ]
        }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } },
            scales: { y: { beginAtZero: true, grid: { color: '#F1F5F9' } }, x: { grid: { display: false } } } }
    });
}

function renderSkills(data) {
    const ctx = document.getElementById('skillsAnalytics');
    if (!ctx || !data.length) return;
    const top10 = data.slice(0, 10);
    new Chart(ctx, {
        type: 'bar', data: {
            labels: top10.map(s => s.skill),
            datasets: [{ data: top10.map(s => s.count), backgroundColor: '#2563EB', borderRadius: 6 }]
        }, options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y', plugins: { legend: { display: false } },
            scales: { x: { beginAtZero: true, grid: { color: '#F1F5F9' } }, y: { grid: { display: false } } } }
    });
}

function renderDepartments(data) {
    const el = document.getElementById('departmentStats');
    if (!data.length) { el.innerHTML = '<p class="text-muted">No department data</p>'; return; }
    el.innerHTML = `<div class="table-container"><table class="data-table"><thead><tr><th>Department</th><th>Open Jobs</th><th>Candidates</th><th>Hired</th></tr></thead>
        <tbody>${data.map(d => `<tr><td class="font-semibold">${d.department}</td><td>${d.open_jobs}</td><td>${d.total_candidates}</td><td>${d.hired}</td></tr>`).join('')}</tbody></table></div>`;
}

function renderInsights(data) {
    const el = document.getElementById('aiInsights');
    if (!data.length) { el.innerHTML = '<p class="text-muted">No insights yet</p>'; return; }
    el.innerHTML = data.map(i => `<div class="insight-item"><i class="bi bi-lightbulb-fill"></i><span>${i}</span></div>`).join('');
}
