/**
 * HireGenius AI — Resume Upload Logic (Drag & Drop + Bulk)
 */
document.addEventListener('DOMContentLoaded', () => {
    initLayout('resumes', 'Resume Upload', 'Recruitment / Resumes');
    setupDragDrop();
    loadJobs();
});

function setupDragDrop() {
    const area = document.getElementById('uploadArea');
    const input = document.getElementById('fileInput');

    area.addEventListener('click', () => input.click());
    area.addEventListener('dragover', (e) => { e.preventDefault(); area.classList.add('drag-over'); });
    area.addEventListener('dragleave', () => area.classList.remove('drag-over'));
    area.addEventListener('drop', (e) => {
        e.preventDefault(); area.classList.remove('drag-over');
        handleFiles(e.dataTransfer.files);
    });
    input.addEventListener('change', (e) => handleFiles(e.target.files));
}

async function loadJobs() {
    try {
        const jobs = await API.get('/jobs');
        const select = document.getElementById('jobSelect');
        select.innerHTML = '<option value="">No specific job</option>' +
            jobs.map(j => `<option value="${j.id}">${j.title}</option>`).join('');
    } catch (e) { console.warn('Jobs load failed:', e); }
}

async function handleFiles(files) {
    if (!files.length) return;
    const jobId = document.getElementById('jobSelect').value;
    const results = document.getElementById('uploadResults');
    const progressBar = document.getElementById('progressFill');
    const progressContainer = document.getElementById('progressContainer');

    progressContainer.classList.remove('hidden');
    results.innerHTML = '';

    const formData = new FormData();
    for (const file of files) {
        formData.append('files', file);
    }
    if (jobId) formData.append('job_id', jobId);

    try {
        progressBar.style.width = '30%';
        const response = await API.upload('/resumes/bulk-upload', formData);
        progressBar.style.width = '100%';

        showToast(`Uploaded ${response.uploaded} resumes successfully!`, 'success');

        results.innerHTML = response.results.map(r => `
            <div class="flex items-center gap-3" style="padding:var(--space-3);background:var(--color-bg);border-radius:var(--radius-md);margin-bottom:var(--space-2);">
                <i class="bi ${r.status === 'success' || r.status === 'uploaded' ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger'}"></i>
                <div class="flex-1">
                    <div class="font-semibold text-sm">${r.file}</div>
                    ${r.candidate_name ? `<div class="text-xs text-muted">Candidate: ${r.candidate_name}</div>` : ''}
                    ${r.error ? `<div class="text-xs text-danger">${r.error}</div>` : ''}
                </div>
                ${r.status === 'success' || r.status === 'uploaded' ? `<span class="badge badge-success">Parsed</span>` : `<span class="badge badge-danger">Failed</span>`}
            </div>
        `).join('');
    } catch (e) {
        showToast(e.message, 'error');
        progressBar.style.width = '0';
    }
}
