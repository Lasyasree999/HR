/**
 * HireGenius AI — Candidate Profile Logic
 */
let jobsList = [];

document.addEventListener('DOMContentLoaded', () => {
    initLayout('candidates', 'Candidate Profile', 'Candidates / Profile');
    const id = new URLSearchParams(window.location.search).get('id');
    if (id) {
        loadProfile(id);
        loadJobs();
    }
    else document.getElementById('profileContent').innerHTML = '<div class="empty-state"><h4>No candidate selected</h4></div>';
});

async function loadJobs() {
    try {
        jobsList = await API.get('/jobs');
    } catch (e) {
        console.warn('Failed to load jobs list:', e);
    }
}

function resolveJob(input) {
    if (!input) return null;
    const clean = input.trim();
    
    // Check if direct number
    const num = parseInt(clean);
    if (!isNaN(num)) {
        return num;
    }
    
    // Search by title (case-insensitive partial match)
    const match = jobsList.find(j => j.title.toLowerCase().includes(clean.toLowerCase()));
    if (match) {
        return match.id;
    }
    return null;
}

function showJobNotFoundError(input) {
    const listStr = jobsList.length > 0
        ? jobsList.map(j => `  - [ID: ${j.id}] ${j.title}`).join('\n')
        : '  (No jobs available. Create one first in Job Management)';
    alert(`Could not find a job matching "${input}".\n\nPlease enter a valid Job ID or Job Title.\n\nAvailable Jobs:\n${listStr}`);
}

async function loadProfile(id) {
    try {
        const c = await API.get(`/candidates/${id}`);
        renderProfile(c);
    } catch (e) { showToast('Failed to load profile', 'error'); }
}

function renderProfile(c) {
    const el = document.getElementById('profileContent');
    const skills = c.skills || [];
    const resume = c.resume_data || {};
    el.innerHTML = `
    <div class="grid-3" style="gap:var(--space-6);">
        <div class="card" style="grid-column:span 2;">
            <div class="flex items-center gap-4 mb-6">
                <div class="score-circle ${getScoreClass(c.match_score)}" style="width:72px;height:72px;font-size:var(--text-lg);">${Math.round(c.match_score)}%</div>
                <div><h2 style="margin:0;">${c.name}</h2>
                    <div class="text-muted">${c.email || ''} ${c.phone ? '• ' + c.phone : ''}</div>
                    <span class="badge ${getStatusBadge(c.status)} mt-2">${c.status}</span></div>
            </div>
            ${c.summary ? `<div class="mb-6"><h4 class="mb-2">AI Summary</h4><p class="text-sm" style="line-height:1.7;">${c.summary}</p></div>` : ''}
            <h4 class="mb-4">Skills</h4>
            <div class="flex flex-wrap gap-2 mb-6">${skills.map(s => `<span class="badge badge-primary">${s.name || s.skill_name || s}</span>`).join('') || '<span class="text-muted">No skills extracted</span>'}</div>
            ${resume.experience ? `<h4 class="mb-4">Experience</h4>${(resume.experience||[]).map(e => `
                <div style="padding:var(--space-3);background:var(--color-bg);border-radius:var(--radius-md);margin-bottom:var(--space-3);">
                    <div class="font-semibold">${e.title || ''} @ ${e.company || ''}</div>
                    <div class="text-xs text-muted">${e.duration || ''}</div>
                    <div class="text-sm mt-2">${e.description || ''}</div>
                </div>`).join('')}` : ''}
            ${resume.education ? `<h4 class="mb-4 mt-6">Education</h4>${(resume.education||[]).map(e => `
                <div class="text-sm mb-2"><strong>${e.degree || ''}</strong> — ${e.institution || ''} (${e.year || ''})</div>`).join('')}` : ''}
        </div>
        <div>
            <div class="card mb-4">
                <h4 class="mb-4">Actions</h4>
                <button class="btn btn-primary w-full mb-2" onclick="generateSummaryProfile(${c.id})"><i class="bi bi-stars"></i> AI Summary</button>
                <button class="btn btn-secondary w-full mb-2" onclick="skillGap(${c.id})"><i class="bi bi-bar-chart-steps"></i> Skill Gap</button>
                <button class="btn btn-secondary w-full mb-2" onclick="genInterview(${c.id})"><i class="bi bi-mic"></i> Interview Qs</button>
                <button class="btn btn-success w-full mb-2" onclick="recommend(${c.id})"><i class="bi bi-trophy"></i> Recommendation</button>
            </div>
            ${resume.certifications && resume.certifications.length ? `
            <div class="card"><h4 class="mb-4">Certifications</h4>${resume.certifications.map(cert => `<div class="badge badge-info mb-2">${cert}</div>`).join(' ')}</div>` : ''}
        </div>
    </div>`;
}

async function generateSummaryProfile(id) {
    showToast('Generating AI summary...', 'info');
    try { const r = await API.get(`/candidates/${id}/summary`); loadProfile(id); showToast('Summary generated!', 'success'); }
    catch (e) { showToast(e.message, 'error'); }
}

async function skillGap(id) {
    const input = prompt('Enter Job ID or Job Title for skill gap analysis:');
    if (!input) return;
    const jobId = resolveJob(input);
    if (!jobId) {
        showJobNotFoundError(input);
        return;
    }
    try { const r = await API.post(`/candidates/${id}/skill-gap?job_id=${jobId}`);
        alert(`Missing Skills: ${(r.missing_skills||[]).join(', ')}\n\nGrowth Suggestions:\n${(r.growth_suggestions||[]).join('\n')}`);
    } catch (e) { showToast(e.message, 'error'); }
}

async function genInterview(id) {
    const input = prompt('Enter Job ID or Job Title for interview generation:');
    if (!input) return;
    const jobId = resolveJob(input);
    if (!jobId) {
        showJobNotFoundError(input);
        return;
    }
    try { await API.post('/interviews/generate', { candidate_id: parseInt(id), job_id: jobId });
        showToast('Interview questions generated! Check Interview Panel.', 'success');
    } catch (e) { showToast(e.message, 'error'); }
}

async function recommend(id) {
    const input = prompt('Enter Job ID or Job Title for recommendation:');
    if (!input) return;
    const jobId = resolveJob(input);
    if (!jobId) {
        showJobNotFoundError(input);
        return;
    }
    try { const r = await API.post(`/ranking/recommend/${id}/${jobId}`);
        alert(`Decision: ${r.decision}\nConfidence: ${(r.confidence_score*100).toFixed(0)}%\n\n${r.reasoning}`);
    } catch (e) { showToast(e.message, 'error'); }
}
