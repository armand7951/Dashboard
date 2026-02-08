import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { getFirestore, collection, addDoc, onSnapshot, serverTimestamp, query, where, doc, getDoc, updateDoc, arrayUnion } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";
import { getAuth, signInWithEmailAndPassword, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

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
const auth = getAuth(app);

// DOM Elements
const authContainer = document.getElementById('auth-container');
const mainContent = document.getElementById('main-content');
const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');
const userDisplay = document.getElementById('user-display-name');
const dashboard = document.getElementById('dashboard');
const staffContainer = document.getElementById('ai-staff');
const filterBtns = document.querySelectorAll('.filter-btn');

// Modal Elements
const taskModal = document.getElementById('task-modal');
const closeModal = document.getElementById('close-modal');
const modalTodo = document.getElementById('modal-todo-list');
const modalDone = document.getElementById('modal-done-list');
const modalProjName = document.getElementById('modal-project-name');

let currentUserProfile = null;
let allProjects = [];
let allStaff = [];
let currentFilter = 'all';

// --- Auth Logic ---
onAuthStateChanged(auth, async (user) => {
    if (user) {
        authContainer.classList.add('hidden');
        mainContent.classList.remove('hidden');
        
        // Fetch profile
        const userDoc = await getDoc(doc(db, "users", user.uid));
        if (userDoc.exists()) {
            currentUserProfile = userDoc.data();
            userDisplay.textContent = `${currentUserProfile.name} (${currentUserProfile.company})`;
        } else {
            userDisplay.textContent = user.email;
            currentUserProfile = { name: user.email, company: 'Unknown' };
        }
        
        setupSnapshots();
    } else {
        authContainer.classList.remove('hidden');
        mainContent.classList.add('hidden');
    }
});

loginBtn.addEventListener('click', async () => {
    const email = document.getElementById('login-email').value;
    const pass = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error');
    try {
        await signInWithEmailAndPassword(auth, email, pass);
    } catch (e) {
        errorEl.textContent = "Authentication Failed: " + e.message;
    }
});

logoutBtn.addEventListener('click', () => signOut(auth));

// --- Data Sync ---
function setupSnapshots() {
    onSnapshot(collection(db, "projects"), (snap) => {
        allProjects = snap.docs.map(d => ({ id: d.id, ...d.data() }));
        renderCards();
    });

    onSnapshot(collection(db, "agents"), (snap) => {
        allStaff = snap.docs.map(d => ({ id: d.id, ...d.data() }));
        renderStaff();
    });
}

function renderCards() {
    dashboard.innerHTML = '';
    const filtered = currentFilter === 'all' ? allProjects : allProjects.filter(p => p.group === currentFilter);

    filtered.forEach(p => {
        const card = document.createElement('div');
        card.className = `project-card ${p.agentActive ? 'agent-active' : ''}`;
        card.innerHTML = `
            <div class="card-header" style="cursor:pointer">
                <div>
                    <h2 class="project-name"><span class="agent-pulse"></span>${p.name}</h2>
                    <span class="group-tag">${p.group}</span>
                </div>
                <div class="status-tag" style="font-size: 0.7rem;">${p.status || 'Active'}</div>
            </div>
            <div class="progress-section">
                <div class="progress-label"><span>Progress</span><span>${p.progress}%</span></div>
                <div class="progress-bar-container"><div class="progress-bar" style="width: ${p.progress}%"></div></div>
            </div>
            <div class="todo-section">
                <div class="todo-title">RECENT TASKS</div>
                <ul class="todo-list">
                    ${(p.todos || []).slice(0, 3).map(t => `<li class="todo-item">${t.title || t}</li>`).join('')}
                </ul>
            </div>
            <button class="feedback-btn" data-id="${p.id}">View Tasks & Feedback</button>
        `;
        
        card.querySelector('.card-header').onclick = () => openTaskModal(p);
        card.querySelector('.feedback-btn').onclick = () => openTaskModal(p);
        dashboard.appendChild(card);
    });
}

function renderStaff() {
    staffContainer.innerHTML = '';
    allStaff.forEach(s => {
        const div = document.createElement('div');
        div.className = 'staff-card';
        div.innerHTML = `
            <div class="staff-avatar">${s.avatar || '🤖'}</div>
            <div class="staff-info">
                <h3>${s.name}</h3>
                <p>${s.role}</p>
                <span class="staff-status">${s.status}</span>
                <div class="staff-load-bar"><div class="staff-load-fill" style="width: ${s.load}%"></div></div>
            </div>
        `;
        staffContainer.appendChild(div);
    });
}

// --- Modal Logic ---
async function openTaskModal(project) {
    modalProjName.textContent = project.name;
    taskModal.classList.add('active');
    
    // In a real app, we'd query the sub-collection 'tasks' here.
    // For this migration, we'll look at the 'tasks' array if it exists, or use the old 'todos'.
    const tasks = project.tasks || (project.todos || []).map(t => typeof t === 'string' ? { title: t, status: 'todo' } : t);
    
    renderModalTasks(project.id, tasks);
}

function renderModalTasks(projectId, tasks) {
    modalTodo.innerHTML = '';
    modalDone.innerHTML = '';

    tasks.forEach((task, idx) => {
        const card = document.createElement('div');
        card.className = 'task-card';
        
        let commentsHtml = (task.comments || []).map(c => `
            <div class="comment-bubble">
                <span class="author">${c.userName}</span>: ${c.text}
                <div class="time">${new Date(c.time?.seconds * 1000).toLocaleString()}</div>
            </div>
        `).join('');

        card.innerHTML = `
            <h4>${task.title}</h4>
            <div class="task-meta">
                <span>Source: ${task.source || 'File'}</span>
                ${task.status === 'done' ? '<span style="color:#4ade80">✓ Completed</span>' : ''}
            </div>
            <div class="comment-section">
                ${commentsHtml}
                <input type="text" class="add-comment-input" placeholder="Add a comment..." data-proj="${projectId}" data-taskidx="${idx}">
            </div>
        `;

        if (task.status === 'done') {
            modalDone.appendChild(card);
        } else {
            modalTodo.appendChild(card);
        }
    });

    // Event listeners for new comments
    document.querySelectorAll('.add-comment-input').forEach(input => {
        input.onkeypress = async (e) => {
            if (e.key === 'Enter' && input.value.trim()) {
                const text = input.value.trim();
                const taskIdx = input.dataset.taskidx;
                await addComment(projectId, taskIdx, text);
                input.value = '';
            }
        };
    });
}

async function addComment(projectId, taskIdx, text) {
    const projRef = doc(db, "projects", projectId);
    const projSnap = await getDoc(projRef);
    if (!projSnap.exists()) return;
    
    const data = projSnap.data();
    const tasks = data.tasks || (data.todos || []).map(t => typeof t === 'string' ? { title: t, status: 'todo' } : t);
    
    if (!tasks[taskIdx].comments) tasks[taskIdx].comments = [];
    tasks[taskIdx].comments.push({
        userId: auth.currentUser.uid,
        userName: currentUserProfile.name,
        company: currentUserProfile.company,
        text: text,
        time: new Date()
    });

    await updateDoc(projRef, { tasks: tasks });
}

closeModal.onclick = () => taskModal.classList.remove('active');
window.onclick = (e) => { if (e.target == taskModal) taskModal.classList.remove('active'); };

// Filter Logic
filterBtns.forEach(btn => {
    btn.onclick = () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        renderCards();
    };
});
