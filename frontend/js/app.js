/**
 * ============================================================
 * HireGenius AI — App Bootstrap
 * ============================================================
 * Sidebar navigation, toast notifications, animated counters,
 * and shared utilities used across all pages.
 * ============================================================
 */

/**
 * Generate the sidebar navigation HTML.
 * @param {string} activePage - Currently active page identifier.
 * @returns {string} Sidebar HTML string.
 */
function generateSidebar(activePage) {
    const user = Auth.getUser();
    const initials = user ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase() : 'U';

    const navItems = [
        { section: 'OVERVIEW', items: [
            { id: 'dashboard', label: 'Dashboard', icon: 'bi-grid-1x2-fill', href: '/dashboard' },
        ]},
        { section: 'RECRUITMENT', items: [
            { id: 'jobs', label: 'Job Management', icon: 'bi-briefcase-fill', href: '/jobs' },
            { id: 'resumes', label: 'Resume Upload', icon: 'bi-file-earmark-person-fill', href: '/resumes' },
            { id: 'candidates', label: 'Candidates', icon: 'bi-people-fill', href: '/candidates' },
        ]},
        { section: 'AI INTELLIGENCE', items: [
            { id: 'interviews', label: 'Interview Panel', icon: 'bi-mic-fill', href: '/interviews' },
            { id: 'emails', label: 'Email Automation', icon: 'bi-envelope-fill', href: '/emails' },
            { id: 'chatbot', label: 'HR Copilot', icon: 'bi-robot', href: '/chatbot' },
        ]},
        { section: 'INSIGHTS', items: [
            { id: 'analytics', label: 'Analytics', icon: 'bi-bar-chart-line-fill', href: '/analytics' },
            { id: 'policies', label: 'Policy Assistant', icon: 'bi-shield-check', href: '/policies' },
        ]},
        { section: 'SYSTEM', items: [
            { id: 'settings', label: 'Settings', icon: 'bi-gear-fill', href: '/settings' },
        ]},
    ];

    let navHTML = '';
    for (const section of navItems) {
        navHTML += `<div class="nav-section">
            <div class="nav-section-title">${section.section}</div>`;
        for (const item of section.items) {
            const isActive = item.id === activePage ? 'active' : '';
            navHTML += `<a href="${item.href}" class="nav-link ${isActive}" id="nav-${item.id}">
                <i class="bi ${item.icon}"></i>
                <span>${item.label}</span>
            </a>`;
        }
        navHTML += '</div>';
    }

    return `
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-brand">
            <div class="brand-icon">🧠</div>
            <div>
                <div class="brand-text">HireGenius</div>
                <div class="brand-subtitle">AI RECRUITMENT</div>
            </div>
        </div>
        <nav class="sidebar-nav">${navHTML}</nav>
        <div class="sidebar-footer">
            <div class="sidebar-user">
                <div class="user-avatar">${initials}</div>
                <div class="user-info">
                    <div class="user-name">${user?.full_name || 'User'}</div>
                    <div class="user-role">${user?.role === 'admin' ? 'Administrator' : 'HR Manager'}</div>
                </div>
                <button class="btn-ghost" onclick="Auth.logout()" title="Logout">
                    <i class="bi bi-box-arrow-right"></i>
                </button>
            </div>
        </div>
    </aside>`;
}

/**
 * Generate the top bar HTML.
 * @param {string} title - Page title.
 * @param {string} breadcrumb - Breadcrumb trail.
 * @returns {string} Topbar HTML string.
 */
function generateTopbar(title, breadcrumb) {
    return `
    <header class="topbar" id="topbar">
        <div class="topbar-left">
            <div>
                <div class="page-title">${title}</div>
                <div class="page-breadcrumb">${breadcrumb}</div>
            </div>
        </div>
        <div class="topbar-right">
            <div class="topbar-search">
                <i class="bi bi-search"></i>
                <input type="text" placeholder="Search candidates, jobs..." id="globalSearch">
            </div>
            <button class="btn-ghost" title="Notifications">
                <i class="bi bi-bell"></i>
            </button>
        </div>
    </header>`;
}

/**
 * Initialize the page layout (sidebar + topbar).
 * @param {string} activePage - Active page identifier.
 * @param {string} title - Page title.
 * @param {string} breadcrumb - Breadcrumb text.
 */
function initLayout(activePage, title, breadcrumb) {
    if (!Auth.guard()) return;

    const layoutEl = document.querySelector('.app-layout');
    if (!layoutEl) return;

    // Insert sidebar
    layoutEl.insertAdjacentHTML('afterbegin', generateSidebar(activePage));

    // Insert topbar into main content
    const mainContent = layoutEl.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertAdjacentHTML('afterbegin', generateTopbar(title, breadcrumb));
    }
}

/**
 * Show a toast notification.
 * @param {string} message - Toast message.
 * @param {string} type - Toast type: 'success', 'error', 'warning', 'info'.
 * @param {number} duration - Auto-dismiss in ms (default 4000).
 */
function showToast(message, type = 'info', duration = 4000) {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const icons = {
        success: 'bi-check-circle-fill',
        error: 'bi-x-circle-fill',
        warning: 'bi-exclamation-triangle-fill',
        info: 'bi-info-circle-fill',
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<i class="bi ${icons[type] || icons.info}"></i><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(40px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Animate a counter from 0 to a target value.
 * @param {HTMLElement} element - Element to animate.
 * @param {number} target - Target number.
 * @param {number} duration - Animation duration in ms.
 */
function animateCounter(element, target, duration = 1200) {
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + (target - start) * eased);

        element.textContent = current.toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

/**
 * Format a date string for display.
 * @param {string} dateStr - ISO date string.
 * @returns {string} Formatted date.
 */
function formatDate(dateStr) {
    if (!dateStr) return '—';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric'
    });
}

/**
 * Format relative time (e.g., "2 hours ago").
 */
function timeAgo(dateStr) {
    const now = new Date();
    const date = new Date(dateStr);
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return formatDate(dateStr);
}

/**
 * Get badge class for recommendation.
 */
function getRecommendationBadge(decision) {
    const map = {
        'strong_hire': 'badge-strong-hire',
        'Strong Hire': 'badge-strong-hire',
        'hire': 'badge-hire',
        'Hire': 'badge-hire',
        'consider': 'badge-consider',
        'Consider': 'badge-consider',
        'reject': 'badge-reject',
        'Reject': 'badge-reject',
    };
    return map[decision] || 'badge-neutral';
}

/**
 * Get score CSS class based on value.
 */
function getScoreClass(score) {
    if (score >= 75) return 'score-high';
    if (score >= 50) return 'score-medium';
    return 'score-low';
}

/**
 * Get status badge class.
 */
function getStatusBadge(status) {
    const map = {
        'new': 'badge-info',
        'screening': 'badge-primary',
        'interview': 'badge-warning',
        'offered': 'badge-success',
        'hired': 'badge-success',
        'rejected': 'badge-danger',
        'open': 'badge-success',
        'closed': 'badge-neutral',
        'on_hold': 'badge-warning',
    };
    return map[status] || 'badge-neutral';
}
