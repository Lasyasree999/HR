/**
 * HireGenius AI — Jobs Management Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    initLayout('jobs', 'Job Management', 'Recruitment / Jobs');
    loadJobs();
});

async function loadJobs() {
    try {
        const jobs = await API.get('/jobs');
        renderJobsTable(jobs);
    } catch (e) {
        showToast('Failed to load jobs', 'error');
    }
}

function renderJobsTable(jobs) {
    const container = document.getElementById('jobsContent');
    if (!jobs.length) {
        container.innerHTML = '<div class="empty-state"><i class="bi bi-briefcase"></i><h4>No jobs yet</h4><p class="text-muted">Create your first job posting</p></div>';
        return;
    }
    container.innerHTML = `<div class="table-container"><table class="data-table"><thead><tr>
        <th>Job Title</th><th>Department</th><th>Location</th><th>Experience</th><th>Candidates</th><th>Status</th><th>Actions</th>
    </tr></thead><tbody>${jobs.map(j => `<tr>
        <td><strong>${j.title}</strong></td>
        <td>${j.department || '—'}</td><td>${j.location || '—'}</td>
        <td>${j.experience_range || '—'}</td>
        <td><span class="badge badge-primary">${j.candidate_count || 0}</span></td>
        <td><span class="badge ${getStatusBadge(j.status)}">${j.status}</span></td>
        <td><button class="btn btn-ghost btn-sm" onclick="viewJob(${j.id})"><i class="bi bi-eye"></i></button>
            <button class="btn btn-ghost btn-sm" onclick="deleteJob(${j.id})"><i class="bi bi-trash"></i></button></td>
    </tr>`).join('')}</tbody></table></div>`;
}

function openCreateJobModal() {
    document.getElementById('jobModal').classList.add('active');
}

function closeJobModal() {
    document.getElementById('jobModal').classList.remove('active');
}

async function createJob(e) {
    e.preventDefault();
    const data = {
        title: document.getElementById('jobTitle').value,
        description: document.getElementById('jobDescription').value,
        required_skills: document.getElementById('jobSkills').value,
        experience_range: document.getElementById('jobExperience').value,
        department: document.getElementById('jobDepartment').value,
        salary_range: document.getElementById('jobSalary').value,
        location: document.getElementById('jobLocation').value,
    };
    try {
        await API.post('/jobs', data);
        showToast('Job created successfully!', 'success');
        closeJobModal();
        loadJobs();
    } catch (e) { showToast(e.message, 'error'); }
}

async function generateAIDescription() {
    const title = document.getElementById('jobTitle').value;
    if (!title) { showToast('Enter a job title first', 'warning'); return; }
    const btn = event.target;
    btn.disabled = true; btn.innerHTML = '<span class="loading-spinner" style="width:14px;height:14px;border-width:2px;"></span> Generating...';
    try {
        const result = await API.post('/jobs/generate-description', {
            title, department: document.getElementById('jobDepartment').value,
            required_skills: document.getElementById('jobSkills').value,
        });
        document.getElementById('jobDescription').value = result.description || '';
        if (result.required_skills) document.getElementById('jobSkills').value = result.required_skills;
        showToast('AI description generated!', 'success');
    } catch (e) { showToast(e.message, 'error'); }
    btn.disabled = false; btn.innerHTML = '<i class="bi bi-stars"></i> AI Generate';
}

async function deleteJob(id) {
    if (!confirm('Delete this job?')) return;
    try { await API.delete(`/jobs/${id}`); showToast('Job deleted', 'success'); loadJobs(); }
    catch (e) { showToast(e.message, 'error'); }
}

function viewJob(id) { showToast('Job details view — coming in full release', 'info'); }
