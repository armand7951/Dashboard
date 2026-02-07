import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { getFirestore, collection, addDoc, onSnapshot, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";

console.log("Dashboard Version: 1.2.0 (GitHub Activity)");

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
const filterBtns = document.querySelectorAll('.filter-btn');

let currentFilter = 'all';
let allProjects = [];

function renderCards() {
    dashboard.innerHTML = '';
    
    const filtered = currentFilter === 'all' 
        ? allProjects 
        : allProjects.filter(p => p.group === currentFilter);

    if (filtered.length === 0) {
        dashboard.innerHTML = '<p style="text-align: center; grid-column: 1/-1; color: var(--text-secondary); margin-top: 50px;">No projects found in this category.</p>';
        return;
    }

    filtered.forEach(project => {
        const card = document.createElement('div');
        card.className = 'project-card';
        
        // Format relative time if possible
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
        } else {
            commitHtml = `
                <div class="github-activity no-activity">
                    <div class="activity-title">LATEST SUBMIT</div>
                    <div class="commit-meta">No GitHub records found</div>
                </div>
            `;
        }

        card.innerHTML = `
            <div class="card-header">
                <div>
                    <h2 class="project-name">${project.name}</h2>
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

onSnapshot(collection(db, "projects"), (querySnapshot) => {
    allProjects = [];
    querySnapshot.forEach((doc) => {
        const data = doc.data();
        allProjects.push({ id: doc.id, ...data });
    });
    renderCards();
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
