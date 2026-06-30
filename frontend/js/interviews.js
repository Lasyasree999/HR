/**
 * HireGenius AI — Interview Panel Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    initLayout('interviews', 'Interview Panel', 'AI Intelligence / Interviews');
    loadInterviews();
});

async function loadInterviews() {
    try {
        const interviews = await API.get('/interviews');
        renderInterviews(interviews);
    } catch (e) { showToast('Failed to load interviews', 'error'); }
}

function renderInterviews(interviews) {
    const el = document.getElementById('interviewsContent');
    if (!interviews.length) {
        el.innerHTML = '<div class="empty-state"><i class="bi bi-mic"></i><h4>No interviews generated yet</h4><p class="text-muted">Go to a candidate profile and generate interview questions</p></div>';
        return;
    }
    el.innerHTML = interviews.map(iv => `
        <div class="card mb-4 animate-fade-in-up hover-lift" style="cursor:pointer;" onclick="viewInterview(${iv.id})">
            <div class="flex items-center justify-between">
                <div><h4>${iv.candidate_name}</h4><div class="text-sm text-muted">${iv.job_title} • ${formatDate(iv.created_at)}</div></div>
                <span class="badge ${iv.status === 'pending' ? 'badge-warning' : 'badge-success'}">${iv.status}</span>
            </div>
        </div>
    `).join('');
}

async function viewInterview(id) {
    try {
        const iv = await API.get(`/interviews/${id}`);
        const modal = document.getElementById('interviewModal');
        document.getElementById('interviewDetail').innerHTML = `
            <h3 class="mb-4">${iv.candidate_name} — ${iv.job_title}</h3>
            <h4 class="mb-2"><i class="bi bi-code-square text-secondary"></i> Technical Questions</h4>
            <ol class="mb-6">${(iv.technical_questions||[]).map(q => `<li class="mb-3"><div class="font-semibold">${q.question}</div><div class="text-xs text-muted">Level: ${q.level} | Weight: ${q.scoring_weight || 1}</div>${q.expected_points ? `<div class="text-xs mt-1">Key points: ${q.expected_points.join(', ')}</div>` : ''}</li>`).join('')}</ol>
            <h4 class="mb-2"><i class="bi bi-people text-success"></i> HR Questions</h4>
            <ol class="mb-6">${(iv.hr_questions||[]).map(q => `<li class="mb-3"><div class="font-semibold">${q.question}</div><div class="text-xs text-muted">Level: ${q.level}</div></li>`).join('')}</ol>
            <h4 class="mb-2"><i class="bi bi-puzzle text-warning"></i> Scenario Questions</h4>
            <ol class="mb-6">${(iv.scenario_questions||[]).map(q => `<li class="mb-3"><div class="font-semibold">${q.question}</div><div class="text-xs text-muted">Level: ${q.level}</div></li>`).join('')}</ol>
            <h4 class="mb-2">Evaluation Criteria</h4>
            <div class="table-container"><table class="data-table"><thead><tr><th>Criterion</th><th>Description</th><th>Weight</th></tr></thead>
            <tbody>${(iv.evaluation_criteria||[]).map(c => `<tr><td class="font-semibold">${c.criterion}</td><td>${c.description}</td><td>${c.weight}%</td></tr>`).join('')}</tbody></table></div>
        `;
        modal.classList.add('active');
    } catch (e) { showToast(e.message, 'error'); }
}

function closeInterviewModal() { document.getElementById('interviewModal').classList.remove('active'); }
