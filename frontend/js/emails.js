/**
 * HireGenius AI — Email Automation Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    initLayout('emails', 'Email Automation', 'AI Intelligence / Emails');
    loadEmails();
    loadCandidatesForEmail();
});

async function loadCandidatesForEmail() {
    try {
        const candidates = await API.get('/candidates');
        const sel = document.getElementById('emailCandidate');
        sel.innerHTML = '<option value="">Select candidate...</option>' +
            candidates.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    } catch(e) {}
}

async function loadEmails() {
    try {
        const emails = await API.get('/emails');
        renderEmails(emails);
    } catch (e) { showToast('Failed to load emails', 'error'); }
}

function renderEmails(emails) {
    const el = document.getElementById('emailsList');
    if (!emails.length) {
        el.innerHTML = '<div class="empty-state"><i class="bi bi-envelope"></i><h4>No emails generated yet</h4></div>';
        return;
    }
    
    // Store globally for safe reference
    window.generatedEmails = emails;
    
    el.innerHTML = emails.map(e => `
        <div class="card mb-3 hover-lift" style="position:relative;">
            <div class="flex items-center justify-between mb-2">
                <div><span class="badge ${e.email_type === 'offer' ? 'badge-success' : e.email_type === 'rejection' ? 'badge-danger' : 'badge-primary'}">${e.email_type.replace('_',' ')}</span></div>
                <span class="text-xs text-muted">${formatDate(e.created_at)}</span>
            </div>
            <h4 class="mb-2" style="font-weight: 600; font-size: var(--text-md);">${e.subject}</h4>
            <div style="position:relative; margin-bottom: 8px;">
                <div id="email-body-text-${e.id}" class="text-sm text-secondary" style="white-space:pre-line; max-height: 100px; overflow:hidden; transition: max-height 0.2s ease-out; line-height:1.6;">
                    ${e.body}
                </div>
                <div id="fade-overlay-${e.id}" style="position: absolute; bottom: 0; left: 0; right: 0; height: 40px; background: linear-gradient(transparent, #ffffff); pointer-events: none;"></div>
            </div>
            <div class="flex items-center justify-between mt-3" style="display:flex; justify-content:space-between; align-items:center;">
                <button id="toggle-btn-${e.id}" class="btn btn-link btn-sm text-primary" onclick="toggleEmailBody(${e.id})" style="padding:0; font-weight:500; font-size:var(--text-xs); border:none; background:none; cursor:pointer;">Read More</button>
                <button class="btn btn-ghost btn-sm" onclick="copyEmail(${e.id})"><i class="bi bi-clipboard"></i> Copy</button>
            </div>
        </div>
    `).join('');
}

function toggleEmailBody(id) {
    const container = document.getElementById(`email-body-text-${id}`);
    const btn = document.getElementById(`toggle-btn-${id}`);
    const overlay = document.getElementById(`fade-overlay-${id}`);
    
    if (container.style.maxHeight === 'none') {
        container.style.maxHeight = '100px';
        overlay.style.display = 'block';
        btn.textContent = 'Read More';
    } else {
        container.style.maxHeight = 'none';
        overlay.style.display = 'none';
        btn.textContent = 'Read Less';
    }
}

async function generateEmail(e) {
    e.preventDefault();
    const candidateId = document.getElementById('emailCandidate').value;
    const emailType = document.getElementById('emailType').value;
    if (!candidateId || !emailType) { showToast('Select candidate and type', 'warning'); return; }
    showToast('Generating email...', 'info');
    try {
        await API.post('/emails/generate', {
            candidate_id: parseInt(candidateId),
            email_type: emailType,
            additional_context: document.getElementById('emailContext').value,
        });
        showToast('Email generated!', 'success');
        loadEmails();
    } catch (e) { showToast(e.message, 'error'); }
}

function copyEmail(id) {
    const email = window.generatedEmails.find(item => item.id === id);
    if (!email) return;
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(email.body)
            .then(() => showToast('Email copied to clipboard!', 'success'))
            .catch(() => fallbackCopy(email.body));
    } else {
        fallbackCopy(email.body);
    }
}

function fallbackCopy(text) {
    const el = document.createElement('textarea');
    el.value = text;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    showToast('Email copied to clipboard!', 'success');
}

