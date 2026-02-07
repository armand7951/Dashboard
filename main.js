let allProjects = [];

async function init() {
    await fetchProjects();
    setupEventListeners();
    renderDashboard('all');
}

async function fetchProjects() {
    try {
        const response = await fetch('data/projects_status.json');
        allProjects = await response.json();
    } catch (error) {
        console.error('Failed to fetch projects:', error);
    }
}

function renderDashboard(filter) {
    const dashboard = document.getElementById('dashboard');
    dashboard.innerHTML = '';

    const filteredProjects = filter === 'all' 
        ? allProjects 
        : allProjects.filter(p => p.group === filter);

    filteredProjects.forEach(project => {
        const card = createProjectCard(project);
        dashboard.appendChild(card);
    });
}

function createProjectCard(project) {
    const card = document.createElement('div');
    card.className = 'project-card';

    const todosHtml = project.todos.length > 0 
        ? project.todos.map(todo => `<li class="todo-item">${todo}</li>`).join('')
        : '<li class="todo-item" style="color: var(--text-secondary); font-style: italic;">No pending tasks</li>';

    card.innerHTML = `
        <div class="card-header">
            <div>
                <h2 class="project-name">${project.name}</h2>
                <span class="group-tag">${project.group === 'DT' ? 'DT Group' : 'B-Side'}</span>
            </div>
        </div>
        <div class="progress-section">
            <div class="progress-label">
                <span>Progress</span>
                <span>${project.progress}%</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: ${project.progress}%"></div>
            </div>
        </div>
        <div class="todo-section">
            <h3 class="todo-title">To-Do List</h3>
            <ul class="todo-list">
                ${todosHtml}
            </ul>
        </div>
        <button class="feedback-btn">Feedback</button>
    `;

    return card;
}

function setupEventListeners() {
    const buttons = document.querySelectorAll('.filter-btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Filter dashboard
            const filter = btn.getAttribute('data-filter');
            renderDashboard(filter);
        });
    });
}

window.addEventListener('DOMContentLoaded', init);