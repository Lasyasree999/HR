/**
 * HireGenius AI — Candidates Ranking Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    initLayout('candidates', 'Candidate Ranking', 'Recruitment / Candidates');
    loadJobsForFilter();
    loadCandidates();
});

async function loadJobsForFilter() {
    try {
        const jobs = await API.get('/jobs');
        const sel = document.getElementById('jobFilter');
        sel.innerHTML = '<option value="">All Jobs</option>' + jobs.map(j => `<option value="${j.id}">${j.title}</option>`).join('');
    } catch(e) {}
}

async function loadCandidates() {
    const jobId = document.getElementById('jobFilter')?.value;
    try {
        const url = jobId ? `/candidates?job_id=${jobId}` : '/candidates';
        const candidates = await API.get(url);
        renderCandidatesTable(candidates);
    } catch (e) { showToast('Failed to load candidates', 'error'); }
}

function renderCandidatesTable(candidates) {
    const c = document.getElementById('candidatesContent');
    if (!candidates.length) {
        c.innerHTML = '<div class="empty-state"><i class="bi bi-people"></i><h4>No candidates yet</h4><p class="text-muted">Upload resumes to see candidates</p></div>';
        return;
    }

    // Partition candidates: Shortlisted vs Not Shortlisted
    const shortlisted = candidates.filter(cd => 
        cd.status === 'screening' || 
        cd.status === 'interview' || 
        cd.status === 'offered' || 
        cd.status === 'hired' ||
        (cd.status === 'new' && cd.match_score >= 40)
    );
    
    const notShortlisted = candidates.filter(cd => 
        cd.status === 'rejected' || 
        (cd.status === 'new' && cd.match_score < 40)
    );

    const renderTableHTML = (list, title, isShortlistedSection) => {
        if (!list.length) {
            return `
            <div class="card mb-6" style="padding: var(--space-4);">
                <h3 class="mb-2 flex items-center justify-between" style="font-size:var(--text-lg); font-weight:600; margin:0;">
                    <span>${title}</span>
                    <span class="badge badge-neutral" style="font-size: var(--text-xs);">${list.length}</span>
                </h3>
                <div class="empty-state" style="padding: var(--space-4); min-height: 100px; display:flex; flex-direction:column; justify-content:center; align-items:center;">
                    <p class="text-muted text-sm" style="margin:0;">No candidates in this category</p>
                </div>
            </div>`;
        }

        return `
        <div class="card mb-6" style="padding: var(--space-4); border-left: 4px solid ${isShortlistedSection ? '#10b981' : '#ef4444'};">
            <h3 class="mb-4 flex items-center justify-between" style="font-size:var(--text-lg); font-weight:600; margin:0 0 16px 0;">
                <span>${title}</span>
                <span class="badge ${isShortlistedSection ? 'badge-success' : 'badge-danger'}" style="font-size: var(--text-xs);">${list.length}</span>
            </h3>
            <div class="table-container" style="overflow-x:auto;">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Candidate</th>
                            <th>Applied Job</th>
                            <th>Email</th>
                            <th>Skills</th>
                            <th>Match Score</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${list.map((cd, i) => `
                        <tr class="animate-fade-in-up stagger-${Math.min(i+1,6)}">
                            <td><strong>${i + 1}</strong></td>
                            <td><strong>${cd.name}</strong></td>
                            <td><span style="font-weight: 500; font-size: var(--text-sm);">${cd.job_title || 'General Application'}</span></td>
                            <td class="text-muted text-sm">${cd.email || '—'}</td>
                            <td>
                                ${(cd.skills||[]).slice(0,3).map(s => `<span class="badge badge-primary" style="margin:1px;">${s.name||s}</span>`).join('')}
                                ${(cd.skills||[]).length > 3 ? `<span class="badge badge-neutral">+${cd.skills.length-3}</span>` : ''}
                            </td>
                            <td>
                                <div class="score-circle ${getScoreClass(cd.match_score)}">${Math.round(cd.match_score)}%</div>
                            </td>
                            <td>
                                <span class="badge ${getStatusBadge(cd.status)}">${cd.status}</span>
                            </td>
                            <td>
                                <div class="flex gap-1" style="display:flex; gap: 4px;">
                                    <a href="/candidate-profile?id=${cd.id}" class="btn btn-ghost btn-sm" title="View Profile"><i class="bi bi-eye"></i></a>
                                    <button class="btn btn-ghost btn-sm" onclick="generateSummary(${cd.id})" title="Generate AI Summary"><i class="bi bi-stars"></i></button>
                                    ${isShortlistedSection ? 
                                        `<button class="btn btn-ghost btn-sm" onclick="updateCandidateStatus(${cd.id}, 'rejected')" title="Reject Candidate"><i class="bi bi-ban" style="color:#ef4444;"></i></button>` :
                                        `<button class="btn btn-ghost btn-sm" onclick="updateCandidateStatus(${cd.id}, 'screening')" title="Shortlist Candidate"><i class="bi bi-check-circle" style="color:#10b981;"></i></button>`
                                    }
                                </div>
                            </td>
                        </tr>`).join('')}
                    </tbody>
                </table>
            </div>
        </div>`;
    };

    c.innerHTML = `
        ${renderTableHTML(shortlisted, "Shortlisted Candidates", true)}
        ${renderTableHTML(notShortlisted, "Not Shortlisted Candidates", false)}
    `;
}

async function updateCandidateStatus(id, newStatus) {
    showToast(`Updating status...`, 'info');
    try {
        await API.put(`/candidates/${id}/status?status=${newStatus}`);
        showToast(`Candidate status updated!`, 'success');
        loadCandidates();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function rankCandidates() {
    const jobId = document.getElementById('jobFilter').value;
    if (!jobId) { showToast('Select a job first', 'warning'); return; }
    showToast('Ranking candidates with AI...', 'info');
    try {
        await API.post(`/ranking/match/${jobId}`);
        showToast('Candidates ranked successfully!', 'success');
        loadCandidates();
    } catch (e) { showToast(e.message, 'error'); }
}

async function generateSummary(id) {
    showToast('Generating AI summary...', 'info');
    try {
        const result = await API.get(`/candidates/${id}/summary`);
        alert(`Summary for ${result.candidate_name}:\n\n${result.summary}\n\nStrengths: ${(result.strengths||[]).join(', ')}\nWeaknesses: ${(result.weaknesses||[]).join(', ')}`);
    } catch (e) { showToast(e.message, 'error'); }
}

