document.addEventListener('DOMContentLoaded', () => {
    // State management
    const state = {
        jobs: [],
        applications: [],
        currentView: 'dashboard'
    };

    // DOM Elements
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view');
    const viewTitle = document.getElementById('view-title');
    const backendStatus = document.getElementById('backend-status');
    const statusDot = document.querySelector('.dot');
    const currentDate = document.getElementById('current-date');
    const triggerSearchBtn = document.getElementById('trigger-search');
    const searchLoading = document.getElementById('search-loading');
    const jobResultsGrid = document.getElementById('job-results');

    // Set current date
    currentDate.textContent = new Date().toLocaleDateString('en-US', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });

    // View Switching
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.getAttribute('data-view');
            switchView(view);
        });
    });

    function switchView(viewName) {
        state.currentView = viewName;

        // Update Nav
        navItems.forEach(nav => {
            nav.classList.toggle('active', nav.getAttribute('data-view') === viewName);
        });

        // Update View
        views.forEach(view => {
            view.classList.toggle('active', view.id === `${viewName}-view`);
        });

        // Update Title
        viewTitle.textContent = viewName.charAt(0).toUpperCase() + viewName.slice(1);

        // Fetch data for the specific view
        if (viewName === 'dashboard') fetchDashboardData();
        if (viewName === 'applications') fetchApplications();
    }

    // Backend Connection Check
    async function checkHealth() {
        try {
            const res = await fetch('/health');
            if (res.ok) {
                backendStatus.textContent = 'Online';
                statusDot.className = 'dot online';
            } else {
                throw new Error();
            }
        } catch (err) {
            backendStatus.textContent = 'Offline';
            statusDot.className = 'dot offline';
        }
    }

    // Data Fetching
    async function fetchDashboardData() {
        try {
            const res = await fetch('/applications');
            const data = await res.json();
            state.applications = data.applications || [];

            // Update Stats
            document.getElementById('stat-total-apps').textContent = state.applications.length;
            document.getElementById('stat-interviews').textContent = state.applications.filter(a => a.status === 'interviewing').length;
            document.getElementById('stat-pending').textContent = state.applications.filter(a => a.status === 'applied').length;

            // Update Recent Table
            const tbody = document.querySelector('#recent-apps-table tbody');
            tbody.innerHTML = '';

            state.applications.slice(0, 5).forEach(app => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${app.company}</td>
                    <td>${app.title}</td>
                    <td>${app.applied_date}</td>
                    <td><span class="badge ${app.status}">${app.status}</span></td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            showNotification('Error fetching dashboard data', 'error');
        }
    }

    async function fetchApplications() {
        try {
            const res = await fetch('/applications');
            const data = await res.json();
            state.applications = data.applications || [];
            renderKanban();
        } catch (err) {
            showNotification('Error fetching applications', 'error');
        }
    }

    function renderKanban() {
        const columns = ['applied', 'interviewing', 'offered', 'rejected'];

        columns.forEach(status => {
            const container = document.getElementById(`column-${status}`);
            const countEl = container.parentElement.querySelector('.count');
            const filtered = state.applications.filter(a => a.status === status);

            countEl.textContent = filtered.length;
            container.innerHTML = '';

            filtered.forEach(app => {
                const card = document.createElement('div');
                card.className = 'kanban-card';
                card.innerHTML = `
                    <div style="font-weight: 700; margin-bottom: 4px;">${app.title}</div>
                    <div style="font-size: 13px; color: var(--primary);">${app.company}</div>
                    <div style="font-size: 11px; color: var(--text-muted); margin-top: 8px;">${app.applied_date}</div>
                `;
                container.appendChild(card);
            });
        });
    }

    // Job Search Pipeline
    triggerSearchBtn.addEventListener('click', async () => {
        triggerSearchBtn.disabled = true;
        searchLoading.classList.remove('hidden');
        jobResultsGrid.innerHTML = '';

        try {
            const res = await fetch('/jobs');
            const data = await res.json();
            state.jobs = data.jobs || [];

            document.getElementById('stat-total-jobs').textContent = state.jobs.length;
            renderJobs();
            showNotification(`Found ${state.jobs.length} relevant jobs!`);
        } catch (err) {
            showNotification('Search pipeline failed', 'error');
        } finally {
            triggerSearchBtn.disabled = false;
            searchLoading.classList.add('hidden');
        }
    });

    function renderJobs() {
        jobResultsGrid.innerHTML = '';
        state.jobs.forEach(job => {
            const card = document.createElement('div');
            card.className = 'job-card';

            const isApplied = state.applications.some(a => a.url === job.url);

            card.innerHTML = `
                <div class="job-header">
                    <div class="company-logo">
                        ${job.company.charAt(0)}
                    </div>
                    <span class="job-source">${job.source}</span>
                </div>
                <div>
                    <div class="job-title">${job.title}</div>
                    <div class="job-company">${job.company}</div>
                </div>
                <div class="job-meta">
                    <span><i class="fas fa-map-marker-alt"></i> ${job.location}</span>
                    <span><i class="fas fa-calendar-alt"></i> ${job.posted_date || 'Recent'}</span>
                </div>
                <div class="job-footer">
                    <a href="${job.url}" target="_blank" class="btn-outline">View Details</a>
                    <button class="btn-primary apply-btn" ${isApplied ? 'disabled' : ''}
                        data-title="${job.title}"
                        data-company="${job.company}"
                        data-location="${job.location}"
                        data-url="${job.url}"
                        data-source="${job.source}">
                        ${isApplied ? 'Applied' : 'Track Application'}
                    </button>
                </div>
            `;
            jobResultsGrid.appendChild(card);
        });

        // Add event listeners to apply buttons
        document.querySelectorAll('.apply-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const btnData = e.target.dataset;
                await recordApplication(btnData, e.target);
            });
        });
    }

    async function recordApplication(data, button) {
        try {
            const res = await fetch('/applications', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: data.title,
                    company: data.company,
                    location: data.location,
                    url: data.url,
                    source: data.source
                })
            });

            if (res.ok) {
                button.disabled = true;
                button.textContent = 'Applied';
                showNotification(`Applied to ${data.company}!`);
                fetchDashboardData();
            } else {
                const err = await res.json();
                showNotification(err.detail || 'Failed to record application', 'error');
            }
        } catch (err) {
            showNotification('Network error', 'error');
        }
    }

    function showNotification(message, type = 'success') {
        const container = document.getElementById('notification-container');
        const notif = document.createElement('div');
        notif.className = `notification ${type}`;
        notif.textContent = message;

        container.appendChild(notif);

        setTimeout(() => {
            notif.style.opacity = '0';
            notif.style.transform = 'translateX(100%)';
            setTimeout(() => notif.remove(), 300);
        }, 3000);
    }

    // Initial load
    checkHealth();
    fetchDashboardData();
});
