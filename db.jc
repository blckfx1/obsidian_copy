// db.js
const DB_NAME = 'ObsidianClone';
const STORE_NAME = 'notes';
let db = null;

export async function initDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, 1);
    request.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'id' });
        store.createIndex('title', 'title', { unique: true });
        store.createIndex('updatedAt', 'updatedAt');
      }
    };
    request.onsuccess = () => {
      db = request.result;
      resolve(db);
    };
    request.onerror = () => reject(request.error);
  });
}

export async function getAllNotes() {
  const tx = db.transaction(STORE_NAME, 'readonly');
  return tx.objectStore(STORE_NAME).getAll();
}

export async function getNote(id) {
  const tx = db.transaction(STORE_NAME, 'readonly');
  return tx.objectStore(STORE_NAME).get(id);
}

export async function saveNote(note) {
  note.updatedAt = Date.now();
  const tx = db.transaction(STORE_NAME, 'readwrite');
  return tx.objectStore(STORE_NAME).put(note);
}

export async function deleteNote(id) {
  const tx = db.transaction(STORE_NAME, 'readwrite');
  return tx.objectStore(STORE_NAME).delete(id);
}