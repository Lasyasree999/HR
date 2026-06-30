/**
 * HireGenius AI — Policy Assistant Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    initLayout('policies', 'Policy Assistant', 'Insights / Policies');
    loadPolicies();
});

async function loadPolicies() {
    try {
        const policies = await API.get('/policies');
        renderPolicies(policies);
    } catch (e) { showToast('Failed to load policies', 'error'); }
}

function renderPolicies(policies) {
    const el = document.getElementById('policiesList');
    if (!policies.length) {
        el.innerHTML = '<div class="empty-state"><i class="bi bi-shield-check"></i><h4>No policies uploaded</h4><p class="text-muted">Upload HR policy documents for RAG-based Q&A</p></div>';
        return;
    }
    el.innerHTML = policies.map(p => `
        <div class="card mb-3 hover-lift">
            <div class="flex items-center justify-between">
                <div><h4 style="margin:0;">${p.title}</h4><div class="text-xs text-muted mt-1">${p.file_name || 'Text content'} • ${formatDate(p.uploaded_at)}</div></div>
                <span class="badge ${p.is_embedded ? 'badge-success' : 'badge-warning'}">${p.is_embedded ? 'Indexed' : 'Pending'}</span>
            </div>
            ${p.content_preview ? `<p class="text-sm text-secondary mt-2">${p.content_preview}</p>` : ''}
        </div>
    `).join('');
}

async function uploadPolicy(e) {
    e.preventDefault();
    const file = document.getElementById('policyFile').files[0];
    const title = document.getElementById('policyTitle').value;
    if (!file || !title) { showToast('Provide title and file', 'warning'); return; }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);

    try {
        await API.upload('/policies/upload', formData);
        showToast('Policy uploaded and indexed!', 'success');
        document.getElementById('policyTitle').value = '';
        document.getElementById('policyFile').value = '';
        loadPolicies();
    } catch (e) { showToast(e.message, 'error'); }
}

async function queryPolicy(e) {
    e.preventDefault();
    const question = document.getElementById('policyQuestion').value;
    if (!question) return;

    const resultEl = document.getElementById('policyAnswer');
    resultEl.innerHTML = '<div class="flex items-center gap-2"><span class="loading-spinner"></span> Searching policies...</div>';

    try {
        const result = await API.post('/policies/query', { question });
        resultEl.innerHTML = `
            <div class="card"><h4 class="mb-2">Answer</h4>
                <p class="text-sm" style="line-height:1.7;white-space:pre-line;">${result.answer}</p>
                ${result.source_policies && result.source_policies.length ? `<div class="mt-4 text-xs text-muted">Sources: ${result.source_policies.join(', ')}</div>` : ''}
            </div>`;
    } catch (e) { resultEl.innerHTML = `<div class="card text-danger">${e.message}</div>`; }
}
