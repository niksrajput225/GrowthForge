/**
 * GrowthForge Mobile & Web Interactive Client Engine
 * Handles REST API interaction, JWT tokens, offline cache, UI tabs, and celebrations.
 */

let appState = {
    user: null,
    tasks: [],
    weeklyTasks: [],
    skills: [],
    noteContent: '',
    dailyProgress: 0,
    weeklyProgress: 0,
    overallProgress: 0,
    activeFilter: 'all'
};

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    initOfflineListeners();
    initTabNavigation();
    initFilterChips();
    initFormHandlers();
    initAvatarUpload();
    
    // Initial fetch
    if (document.querySelector('.dashboard-wrapper')) {
        loadDashboardData();
    }
});

// --- API Client with Dual Auth (Bearer Token + Cookies) ---
async function apiRequest(endpoint, options = {}) {
    const headers = options.headers || {};
    const token = localStorage.getItem('gf_access_token');
    
    if (token && !headers['Authorization']) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
    }
    
    options.headers = headers;
    options.credentials = 'same-origin';
    
    try {
        const response = await fetch(endpoint, options);
        if (response.status === 401) {
            // If on dashboard and unauthorized, redirect to login
            if (window.location.pathname === '/' || window.location.pathname === '/dashboard') {
                window.location.href = '/login';
            }
            return { success: false, error: 'Unauthorized' };
        }
        return await response.json();
    } catch (err) {
        console.warn('Network request failed, checking local cache:', err);
        return { success: false, error: 'Network error', offline: true };
    }
}

// --- Dashboard Data Loader & Cache ---
async function loadDashboardData() {
    const res = await apiRequest('/api/v1/user/summary');
    
    if (res.success) {
        appState.user = res.user;
        appState.tasks = res.tasks || [];
        appState.weeklyTasks = res.weekly_tasks || [];
        appState.skills = res.skills || [];
        appState.noteContent = res.note_content || '';
        appState.dailyProgress = res.daily_progress || 0;
        appState.weeklyProgress = res.weekly_progress || 0;
        appState.overallProgress = res.overall_progress || 0;
        
        // Cache in localStorage for offline resiliency
        localStorage.setItem('gf_cached_dashboard', JSON.stringify(appState));
        
        renderAll();
    } else {
        // Fallback to cache if offline
        const cached = localStorage.getItem('gf_cached_dashboard');
        if (cached) {
            try {
                appState = JSON.parse(cached);
                renderAll();
                showToast('Using cached offline data', 'info');
            } catch (e) {
                console.error(e);
            }
        }
    }
}

// --- Render Engine ---
function renderAll() {
    renderUserMeta();
    renderOverview();
    renderTasks();
    renderWeekly();
    renderSkills();
    renderNotes();
}

function renderUserMeta() {
    if (!appState.user) return;
    
    const u = appState.user;
    const nameEl = document.getElementById('user-display-name');
    const levelEl = document.getElementById('user-level-badge');
    const xpEl = document.getElementById('user-xp-badge');
    const streakEl = document.getElementById('streak-days');
    const avatarEl = document.getElementById('user-avatar-img');
    const setAvatarEl = document.getElementById('settings-avatar-img');
    const setUsernameEl = document.getElementById('settings-username');
    const setLevelLabel = document.getElementById('settings-level-label');
    
    if (nameEl) nameEl.textContent = u.username;
    if (levelEl) levelEl.innerHTML = `<i class="fa-solid fa-bolt"></i> Level ${u.level || 1}`;
    if (xpEl) xpEl.textContent = `${u.xp_points || 0} XP`;
    if (streakEl) streakEl.textContent = u.streak_count || 1;
    if (avatarEl && u.avatar_url) avatarEl.src = u.avatar_url;
    if (setAvatarEl && u.avatar_url) setAvatarEl.src = u.avatar_url;
    if (setUsernameEl) setUsernameEl.textContent = u.username;
    if (setLevelLabel) setLevelLabel.textContent = `Level ${u.level || 1} • Forger`;
}

function renderOverview() {
    // 1. Overall Progress Gauge
    const percent = appState.overallProgress;
    const textEl = document.getElementById('overall-progress-text');
    const circleEl = document.getElementById('overall-progress-circle');
    
    if (textEl) textEl.textContent = `${percent}%`;
    if (circleEl) {
        const circumference = 2 * Math.PI * 42; // ~263.89
        const offset = circumference - (percent / 100) * circumference;
        circleEl.style.strokeDashoffset = offset;
    }
    
    // 2. Metrics Glance
    const totalDaily = appState.tasks.length;
    const compDaily = appState.tasks.filter(t => t.completed).length;
    const dailyMetric = document.getElementById('daily-metric-val');
    const dailyFill = document.getElementById('daily-bar-fill');
    if (dailyMetric) dailyMetric.textContent = `${compDaily} / ${totalDaily}`;
    if (dailyFill) dailyFill.style.width = `${appState.dailyProgress}%`;
    
    const totalWeekly = appState.weeklyTasks.length;
    const compWeekly = appState.weeklyTasks.filter(w => w.completed).length;
    const weeklyMetric = document.getElementById('weekly-metric-val');
    const weeklyFill = document.getElementById('weekly-bar-fill');
    if (weeklyMetric) weeklyMetric.textContent = `${compWeekly} / ${totalWeekly}`;
    if (weeklyFill) weeklyFill.style.width = `${appState.weeklyProgress}%`;
    
    const skillsMetric = document.getElementById('skills-metric-val');
    const skillsFill = document.getElementById('skills-bar-fill');
    if (skillsMetric) skillsMetric.textContent = `${appState.skills.length} Trees`;
    if (skillsFill) {
        const avgSkillProgress = appState.skills.length 
            ? Math.round(appState.skills.reduce((acc, s) => acc + s.progress, 0) / appState.skills.length) 
            : 0;
        skillsFill.style.width = `${avgSkillProgress}%`;
    }
    
    // XP to next level
    const currentXp = (appState.user && appState.user.xp_points) || 100;
    const currentLevel = (appState.user && appState.user.level) || 1;
    const nextLevelTarget = currentLevel * 100;
    const xpIntoLevel = currentXp % 100;
    const nextValEl = document.getElementById('next-level-val');
    const xpBarFill = document.getElementById('xp-bar-fill');
    if (nextValEl) nextValEl.textContent = `${xpIntoLevel} / 100`;
    if (xpBarFill) xpBarFill.style.width = `${xpIntoLevel}%`;

    // 3. Priority Objectives Preview
    const previewList = document.getElementById('overview-tasks-preview');
    if (previewList) {
        const highTasks = appState.tasks.filter(t => !t.completed && t.priority === 'high');
        const displayTasks = highTasks.length ? highTasks : appState.tasks.slice(0, 3);
        
        if (!displayTasks.length) {
            previewList.innerHTML = `<div style="text-align:center; padding:16px; color:var(--text-muted); font-size:0.85rem;">All caught up! Add a new quest to forge ahead.</div>`;
        } else {
            previewList.innerHTML = displayTasks.map(t => `
                <div class="task-item ${t.completed ? 'completed' : ''}" style="margin-bottom:8px;">
                    <div class="task-checkbox" onclick="toggleTask(${t.id})">
                        ${t.completed ? '<i class="fa-solid fa-check"></i>' : ''}
                    </div>
                    <div class="task-content">
                        <div class="task-title">${escapeHtml(t.title)}</div>
                        <div class="task-meta">
                            <span class="badge-priority ${t.priority}">${t.priority}</span>
                            <span class="task-category-tag">${escapeHtml(t.category || 'General')}</span>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    }
}

function renderTasks() {
    const container = document.getElementById('daily-tasks-list');
    if (!container) return;
    
    let filtered = appState.tasks;
    if (appState.activeFilter === 'pending') {
        filtered = filtered.filter(t => !t.completed);
    } else if (appState.activeFilter === 'completed') {
        filtered = filtered.filter(t => t.completed);
    } else if (appState.activeFilter === 'high') {
        filtered = filtered.filter(t => t.priority === 'high');
    }
    
    if (!filtered.length) {
        container.innerHTML = `
            <div style="text-align:center; padding: 40px 10px; color:var(--text-muted);">
                <i class="fa-solid fa-clipboard-check" style="font-size:2.5rem; margin-bottom:12px; opacity:0.3;"></i>
                <p>No quests match this filter.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = filtered.map(t => `
        <div class="task-item ${t.completed ? 'completed' : ''}" id="task-card-${t.id}">
            <div class="task-checkbox" onclick="toggleTask(${t.id})">
                ${t.completed ? '<i class="fa-solid fa-check"></i>' : ''}
            </div>
            <div class="task-content">
                <div class="task-title">${escapeHtml(t.title)}</div>
                <div class="task-meta">
                    <span class="badge-priority ${t.priority}">${t.priority}</span>
                    <span class="task-category-tag">${escapeHtml(t.category || 'General')}</span>
                </div>
            </div>
            <button class="item-delete-btn" onclick="deleteTask(${t.id})" title="Delete Task">
                <i class="fa-solid fa-trash"></i>
            </button>
        </div>
    `).join('');
}

function renderWeekly() {
    const container = document.getElementById('weekly-tasks-list');
    if (!container) return;
    
    if (!appState.weeklyTasks.length) {
        container.innerHTML = `
            <div style="text-align:center; padding: 40px 10px; color:var(--text-muted);">
                <i class="fa-solid fa-calendar-plus" style="font-size:2.5rem; margin-bottom:12px; opacity:0.3;"></i>
                <p>No weekly milestones defined yet.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = appState.weeklyTasks.map(w => `
        <div class="task-item ${w.completed ? 'completed' : ''}">
            <div class="task-checkbox" onclick="toggleWeekly(${w.id})">
                ${w.completed ? '<i class="fa-solid fa-check"></i>' : ''}
            </div>
            <div class="task-content">
                <div class="task-title">${escapeHtml(w.title)}</div>
            </div>
            <button class="item-delete-btn" onclick="deleteWeekly(${w.id})" title="Delete Goal">
                <i class="fa-solid fa-trash"></i>
            </button>
        </div>
    `).join('');
}

function renderSkills() {
    const container = document.getElementById('skills-categories-container');
    if (!container) return;
    
    if (!appState.skills.length) {
        container.innerHTML = `
            <div style="text-align:center; padding: 40px 10px; color:var(--text-muted);">
                <i class="fa-solid fa-seedling" style="font-size:2.5rem; margin-bottom:12px; opacity:0.3;"></i>
                <p>No skill trees planted. Create one above to track mastery!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = appState.skills.map(cat => {
        const theme = cat.color_theme || 'cyan';
        return `
            <div class="skill-tree-card ${theme}">
                <div class="tree-header">
                    <div class="tree-title-group">
                        <div class="tree-icon ${theme}">
                            <i class="fa-solid ${cat.icon || 'fa-star'}"></i>
                        </div>
                        <div>
                            <h4>${escapeHtml(cat.name)}</h4>
                            <span style="font-size:0.75rem; color:var(--text-muted);">${cat.logs_count || 0} Reps Logged</span>
                        </div>
                    </div>
                    <div style="display:flex; gap:8px;">
                        <button class="icon-btn" onclick="openAddModuleModal(${cat.id})" title="Add Module">
                            <i class="fa-solid fa-plus"></i>
                        </button>
                        <button class="item-delete-btn" onclick="deleteCategory(${cat.id})" title="Delete Tree">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                </div>

                <div class="tree-progress-wrap">
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; font-weight:700;">
                        <span>Tree Mastery</span>
                        <span class="accent-${theme}">${cat.progress || 0}%</span>
                    </div>
                    <div class="tree-progress-bar">
                        <div class="bar-fill" style="width: ${cat.progress || 0}%; background: var(--accent-${theme});"></div>
                    </div>
                </div>

                <div class="tree-modules-list">
                    ${(cat.modules || []).map(mod => `
                        <div class="module-box">
                            <div class="module-box-head">
                                <span>${escapeHtml(mod.title)}</span>
                                <div style="display:flex; gap:6px;">
                                    <button class="link-btn" onclick="openAddLogModal(${mod.id})">
                                        <i class="fa-solid fa-plus"></i> Log
                                    </button>
                                    <button class="item-delete-btn" onclick="deleteModule(${mod.id})" style="padding:0;">
                                        <i class="fa-solid fa-xmark"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="log-pill-row">
                                ${(mod.logs || []).map(l => `
                                    <div class="log-pill">
                                        <span>${escapeHtml(l.name)}: <strong>${escapeHtml(l.metric)}</strong></span>
                                        <i class="fa-solid fa-xmark log-del" onclick="deleteLog(${l.id})" title="Delete"></i>
                                    </div>
                                `).join('')}
                                ${(!mod.logs || !mod.logs.length) ? '<span style="font-size:0.72rem; color:var(--text-muted);">No entries yet</span>' : ''}
                            </div>
                        </div>
                    `).join('')}
                    ${(!cat.modules || !cat.modules.length) ? '<span style="font-size:0.78rem; color:var(--text-muted); text-align:center; display:block; padding:8px;">No modules added yet.</span>' : ''}
                </div>
            </div>
        `;
    }).join('');
}

function renderNotes() {
    const textarea = document.getElementById('quick-note-textarea');
    if (textarea && textarea.value !== appState.noteContent) {
        textarea.value = appState.noteContent;
    }
}

// --- User Actions & API Handlers ---
async function toggleTask(taskId) {
    const task = appState.tasks.find(t => t.id === taskId);
    if (!task) return;
    
    // Optimistic UI Update
    task.completed = !task.completed;
    renderAll();
    
    const res = await apiRequest(`/api/v1/tasks/${taskId}/toggle`, { method: 'POST' });
    if (res.success) {
        if (appState.user) {
            appState.user.xp_points = res.user_xp;
            appState.user.level = res.user_level;
        }
        
        // Recalculate daily progress
        const completedCount = appState.tasks.filter(t => t.completed).length;
        appState.dailyProgress = Math.round((completedCount / appState.tasks.length) * 100);
        
        // Check for 100% completion celebration!
        if (appState.dailyProgress === 100) {
            fireConfettiCelebration();
            showToast('All Daily Quests Complete! Master Forger Status!', 'success');
        } else if (task.completed) {
            showToast('+15 XP Earned!', 'success');
        }
        renderAll();
    } else {
        // Rollback
        task.completed = !task.completed;
        renderAll();
        showToast('Failed to update task status.', 'error');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Permanently delete this task?')) return;
    
    const res = await apiRequest(`/api/v1/tasks/${taskId}`, { method: 'DELETE' });
    if (res.success) {
        appState.tasks = appState.tasks.filter(t => t.id !== taskId);
        loadDashboardData();
        showToast('Task removed.', 'info');
    }
}

async function toggleWeekly(goalId) {
    const goal = appState.weeklyTasks.find(w => w.id === goalId);
    if (!goal) return;
    
    goal.completed = !goal.completed;
    renderAll();
    
    const res = await apiRequest(`/api/v1/tasks/weekly/${goalId}/toggle`, { method: 'POST' });
    if (res.success) {
        if (appState.user) {
            appState.user.xp_points = res.user_xp;
            appState.user.level = res.user_level;
        }
        if (goal.completed) showToast('+30 XP Weekly Milestone!', 'success');
        loadDashboardData();
    }
}

async function deleteWeekly(goalId) {
    if (!confirm('Permanently delete this weekly goal?')) return;
    
    const res = await apiRequest(`/api/v1/tasks/weekly/${goalId}`, { method: 'DELETE' });
    if (res.success) {
        appState.weeklyTasks = appState.weeklyTasks.filter(w => w.id !== goalId);
        loadDashboardData();
    }
}

async function deleteCategory(catId) {
    if (!confirm('Permanently delete this skill tree and all its modules?')) return;
    const res = await apiRequest(`/api/v1/skills/categories/${catId}`, { method: 'DELETE' });
    if (res.success) {
        loadDashboardData();
        showToast('Skill tree deleted.', 'info');
    }
}

async function deleteModule(modId) {
    if (!confirm('Delete this module?')) return;
    const res = await apiRequest(`/api/v1/skills/modules/${modId}`, { method: 'DELETE' });
    if (res.success) {
        loadDashboardData();
    }
}

async function deleteLog(logId) {
    const res = await apiRequest(`/api/v1/skills/logs/${logId}`, { method: 'DELETE' });
    if (res.success) {
        loadDashboardData();
    }
}

// --- Navigation Tabs ---
function initTabNavigation() {
    const navItems = document.querySelectorAll('.bottom-nav .nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabName = item.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    document.querySelectorAll('.bottom-nav .nav-item').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-tab') === tabName);
    });
    
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    const targetPane = document.getElementById(`tab-${tabName}`);
    if (targetPane) {
        targetPane.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// --- Filter Chips ---
function initFilterChips() {
    const chips = document.querySelectorAll('.filter-chips .chip');
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            chips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            appState.activeFilter = chip.getAttribute('data-filter');
            renderTasks();
        });
    });
}

// --- Form & Modal Handlers ---
function initFormHandlers() {
    // Add Task
    const openTaskBtn = document.getElementById('open-add-task-modal');
    if (openTaskBtn) openTaskBtn.addEventListener('click', () => openModal('task-modal'));
    
    const taskForm = document.getElementById('create-task-form');
    if (taskForm) {
        taskForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = document.getElementById('task-input-title').value.trim();
            const priority = document.getElementById('task-input-priority').value;
            const category = document.getElementById('task-input-category').value.trim() || 'General';
            
            const res = await apiRequest('/api/v1/tasks', {
                method: 'POST',
                body: JSON.stringify({ title, priority, category })
            });
            if (res.success) {
                closeModal('task-modal');
                taskForm.reset();
                loadDashboardData();
                showToast('Quest added!', 'success');
            }
        });
    }

    // Add Weekly
    const openWeeklyBtn = document.getElementById('open-add-weekly-modal');
    if (openWeeklyBtn) openWeeklyBtn.addEventListener('click', () => openModal('weekly-modal'));
    
    const weeklyForm = document.getElementById('create-weekly-form');
    if (weeklyForm) {
        weeklyForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = document.getElementById('weekly-input-title').value.trim();
            const res = await apiRequest('/api/v1/tasks/weekly', {
                method: 'POST',
                body: JSON.stringify({ title })
            });
            if (res.success) {
                closeModal('weekly-modal');
                weeklyForm.reset();
                loadDashboardData();
                showToast('Weekly milestone created!', 'success');
            }
        });
    }

    // Add Category
    const openCatBtn = document.getElementById('open-add-category-modal');
    if (openCatBtn) openCatBtn.addEventListener('click', () => openModal('category-modal'));
    
    const catForm = document.getElementById('create-category-form');
    if (catForm) {
        catForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('cat-input-name').value.trim();
            const color_theme = document.getElementById('cat-input-color').value;
            const icon = document.getElementById('cat-input-icon').value;
            
            const res = await apiRequest('/api/v1/skills/categories', {
                method: 'POST',
                body: JSON.stringify({ name, color_theme, icon })
            });
            if (res.success) {
                closeModal('category-modal');
                catForm.reset();
                loadDashboardData();
                showToast('New skill tree planted!', 'success');
            }
        });
    }

    // Add Module
    const moduleForm = document.getElementById('create-module-form');
    if (moduleForm) {
        moduleForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const category_id = document.getElementById('module-category-id').value;
            const title = document.getElementById('module-input-title').value.trim();
            
            const res = await apiRequest('/api/v1/skills/modules', {
                method: 'POST',
                body: JSON.stringify({ category_id, title })
            });
            if (res.success) {
                closeModal('module-modal');
                moduleForm.reset();
                loadDashboardData();
            }
        });
    }

    // Add Log
    const logForm = document.getElementById('create-log-form');
    if (logForm) {
        logForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const module_id = document.getElementById('log-module-id').value;
            const name = document.getElementById('log-input-name').value.trim();
            const metric = document.getElementById('log-input-metric').value.trim();
            
            const res = await apiRequest('/api/v1/skills/logs', {
                method: 'POST',
                body: JSON.stringify({ module_id, name, metric })
            });
            if (res.success) {
                closeModal('log-modal');
                logForm.reset();
                loadDashboardData();
                showToast('+10 XP Logged!', 'success');
            }
        });
    }

    // Save Note
    const saveNoteBtn = document.getElementById('save-note-btn');
    if (saveNoteBtn) {
        saveNoteBtn.addEventListener('click', async () => {
            const content = document.getElementById('quick-note-textarea').value;
            const res = await apiRequest('/api/v1/notes', {
                method: 'POST',
                body: JSON.stringify({ content })
            });
            if (res.success) {
                appState.noteContent = content;
                const syncEl = document.getElementById('notes-last-saved');
                if (syncEl) syncEl.textContent = `Saved just now`;
                showToast('Notes synchronized!', 'success');
            }
        });
    }

    // Settings Modal
    const settingsBtn = document.getElementById('open-settings-btn');
    if (settingsBtn) settingsBtn.addEventListener('click', () => openModal('settings-modal'));
    const avatarRing = document.getElementById('header-avatar-btn');
    if (avatarRing) avatarRing.addEventListener('click', () => openModal('settings-modal'));
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('hidden');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('hidden');
}

function openAddModuleModal(categoryId) {
    document.getElementById('module-category-id').value = categoryId;
    openModal('module-modal');
}

function openAddLogModal(moduleId) {
    document.getElementById('log-module-id').value = moduleId;
    openModal('log-modal');
}

// --- Avatar Uploader ---
function initAvatarUpload() {
    const fileInput = document.getElementById('avatar-file-input');
    if (!fileInput) return;
    
    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('avatar', file);
        
        const res = await apiRequest('/api/v1/user/avatar', {
            method: 'POST',
            body: formData
        });
        
        if (res.success) {
            if (appState.user) appState.user.avatar_url = res.avatar_url;
            renderUserMeta();
            showToast('Avatar updated!', 'success');
        } else {
            showToast(res.error || 'Avatar upload failed', 'error');
        }
    });
}

// --- Offline Listener ---
function initOfflineListeners() {
    const banner = document.getElementById('offline-banner');
    function updateOnlineStatus() {
        if (!banner) return;
        if (navigator.onLine) {
            banner.classList.add('hidden');
        } else {
            banner.classList.remove('hidden');
        }
    }
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();
}

// --- Celebrations & Toasts ---
function fireConfettiCelebration() {
    if (typeof confetti === 'function') {
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 }
        });
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? 'fa-circle-check' : (type === 'error' ? 'fa-circle-exclamation' : 'fa-circle-info');
    toast.innerHTML = `<i class="fa-solid ${icon}"></i><span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3200);
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
