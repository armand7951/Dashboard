const admin = require('firebase-admin');
const fs = require('fs');

// Initialize with application default credentials (since user is logged in via gcloud)
admin.initializeApp({
  projectId: 'dashboard-amen-v2'
});

const db = admin.firestore();
const projects = JSON.parse(fs.readFileSync('./data/projects_status.json', 'utf8'));

async function sync() {
  console.log('Starting sync to Firestore...');
  const batch = db.batch();
  
  projects.forEach(project => {
    const docRef = db.collection('projects').doc(project.id);
    batch.set(docRef, {
      ...project,
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    });
  });

  await batch.commit();
  console.log('Sync complete!');
}

sync().catch(err => {
  console.error('Sync failed:', err);
  process.exit(1);
});
