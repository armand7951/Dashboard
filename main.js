import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { getFirestore, collection, addDoc, onSnapshot, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";

console.log("Dashboard Version: 2.1.0 (Frontier Force)");

const firebaseConfig = {
  "projectId": "dashboard-amen-v2",
  "appId": "1:846149076695:web:8325caa2bf24a4b9531292",
  "storageBucket": "dashboard-amen-v2.firebasestorage.app",
  "apiKey": "AIzaSyCOIK4s_JyYvrFsJ62VB5T_bbPYgJUZXPQ",
  "authDomain": "dashboard-amen-v2.firebaseapp.com",
  "messagingSenderId": "846149076695",
  "projectNumber": "846149076695"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const dashboard = document.getElementById('dashboard');
const staffContainer = document.getElementById('ai-staff');
const filterBtns = document.querySelectorAll('.filter-btn');

let currentFilter = 'all';
let allProjects = [];
let allStaff = [];

function renderStaff() {
    staffContainer.innerHTML = '';
    allStaff.forEach(staff => {
        const card = document.createElement('div');
        card.className = 'staff-card';
        card.innerHTML = `
            <div class="staff-avatar">${staff.avatar}</div>
            <div class="staff-info">
                <h3>${staff.name}</h3>
                <p>${staff.role}</p>
                <span class="staff-status">${staff.status}</span>
                <div class="staff-load-bar">
                    <div class="staff-load-fill" style="width: ${staff.load}%"></div>
                </div>
            </div>
        `;
        staffContainer.appendChild(card);
    });
}

function renderCards() {
    dashboard.innerHTML = '';
    const filtered = currentFilter === 'all' 
        ? allProjects 
        : allProjects.filter(p => p.group === currentFilter);

    if (filtered.length === 0) {
        dashboard.innerHTML = '<p style="text-align: center; grid-column: 1/-1; color: var(--text-secondary); margin-top: 50px;">No projects found.</p>';
        return;
    }

    filtered.forEach(project => {
        const card = document.createElement('div');
        card.className = `project-card ${project.agentActive ? 'agent-active' : ''}`;
        
        let commitHtml = '';
        if (project.lastCommit) {
            const date = new Date(project.lastCommit.date);
            const timeStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            commitHtml = `
                <div class="github-activity">
                    <div class="activity-title">LATEST SUBMIT</div>
                    <div class="commit-msg">"${project.lastCommit.message}"</div>
                    <div class="commit-meta">${timeStr} by ${project.lastCommit.author}</div>
                </div>
            `;
        }

        let terminalHtml = '';
        if (project.agentActive && project.agentLogs) {
            terminalHtml = `
                <div class="agent-terminal">
                    ${project.agentLogs.map(log => `<div class="terminal-line">${log}</div>`).join('')}
                </div>
            `;
        }

        card.innerHTML = `
            <div class="card-header">
                <div>
                    <h2 class="project-name">
                        <span class="agent-pulse"></span>${project.name}
                    </h2>
                    <span class="group-tag">${project.group}</span>
                </div>
                <div class="status-tag" style="font-size: 0.75rem; color: var(--text-secondary);">${project.status}</div>
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
            ${commitHtml}
            ${terminalHtml}
            <div class="todo-section">
                <h3 class="todo-title">To-Do List</h3>
                <ul class="todo-list">
                    ${project.todos && project.todos.length > 0 
                        ? project.todos.map(todo => `<li class="todo-item">${todo}</li>`).join('')
                        : '<li class="todo-item" style="color: #64748b; font-style: italic;">No pending tasks</li>'}
                </ul>
            </div>
            <button class="feedback-btn" data-id="${project.id}">Add Feedback</button>
        `;
        dashboard.appendChild(card);
    });

    document.querySelectorAll('.feedback-btn').forEach(btn => {
        btn.addEventListener('click', () => openFeedback(btn.dataset.id));
    });
}

// Listen for Projects
onSnapshot(collection(db, "projects"), (querySnapshot) => {
    allProjects = [];
    querySnapshot.forEach((doc) => {
        allProjects.push({ id: doc.id, ...doc.data() });
    });
    renderCards();
});

// Listen for Staff
onSnapshot(collection(db, "agents"), (querySnapshot) => {
    allStaff = [];
    querySnapshot.forEach((doc) => {
        allStaff.push({ id: doc.id, ...doc.data() });
    });
    renderStaff();
});

filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        renderCards();
    });
});

async function openFeedback(id) {
    const feedbackText = prompt(`Enter feedback for project [${id}]:`);
    if (feedbackText) {
        try {
            await addDoc(collection(db, "feedback"), {
                projectId: id,
                text: feedbackText,
                timestamp: serverTimestamp()
            });
            alert("Feedback submitted successfully!");
        } catch (e) {
            console.error("Error adding feedback: ", e);
            alert("Failed to submit feedback.");
        }
    }
}
