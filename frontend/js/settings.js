/**
 * HireGenius AI — Settings Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    initLayout('settings', 'Settings', 'System / Settings');
    loadSettings();
});

function loadSettings() {
    const user = Auth.getUser();
    if (user) {
        document.getElementById('settingsUsername').textContent = user.username;
        document.getElementById('settingsEmail').textContent = user.email;
        document.getElementById('settingsRole').textContent = user.role === 'admin' ? 'Administrator' : 'HR Manager';
        document.getElementById('settingsName').textContent = user.full_name;
    }

    if (Auth.isAdmin()) {
        document.getElementById('adminSection').classList.remove('hidden');
        loadUsers();
    }
}

async function loadUsers() {
    try {
        const users = await API.get('/auth/users');
        const el = document.getElementById('usersList');
        el.innerHTML = `<div class="table-container"><table class="data-table"><thead><tr>
            <th>Username</th><th>Email</th><th>Name</th><th>Role</th><th>Status</th><th>Actions</th>
        </tr></thead><tbody>${users.map(u => `<tr>
            <td class="font-semibold">${u.username}</td><td>${u.email}</td><td>${u.full_name}</td>
            <td><span class="badge ${u.role === 'admin' ? 'badge-info' : 'badge-primary'}">${u.role}</span></td>
            <td><span class="badge ${u.is_active ? 'badge-success' : 'badge-danger'}">${u.is_active ? 'Active' : 'Inactive'}</span></td>
            <td>${u.username !== 'admin' ? `<button class="btn btn-ghost btn-sm" onclick="toggleUser(${u.id}, ${!u.is_active})"><i class="bi bi-toggle-${u.is_active ? 'on' : 'off'}"></i></button>` : '—'}</td>
        </tr>`).join('')}</tbody></table></div>`;
    } catch (e) { showToast('Failed to load users', 'error'); }
}

async function toggleUser(id, active) {
    try { await API.put(`/auth/users/${id}/status?is_active=${active}`); showToast('User updated', 'success'); loadUsers(); }
    catch (e) { showToast(e.message, 'error'); }
}

function openAddUserModal() { document.getElementById('addUserModal').classList.add('active'); }
function closeAddUserModal() { document.getElementById('addUserModal').classList.remove('active'); }

async function addUser(e) {
    e.preventDefault();
    try {
        await API.post('/auth/register', {
            username: document.getElementById('newUsername').value,
            email: document.getElementById('newEmail').value,
            password: document.getElementById('newPassword').value,
            full_name: document.getElementById('newFullName').value,
            role: document.getElementById('newRole').value,
        });
        showToast('User created!', 'success');
        closeAddUserModal();
        loadUsers();
    } catch (e) { showToast(e.message, 'error'); }
}
