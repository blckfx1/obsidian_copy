// script.js
import { initDB, getAllNotes, getNote, saveNote, deleteNote } from './db.js';

// Global state: which note ID is in each pane (0, 1, 2)
let activePaneNotes = [null, null, null];

// Wait for page to load
window.addEventListener('DOMContentLoaded', async () => {
  await initDB();
  
  // Load all notes into left sidebar
  await refreshNoteList();
  
  // Get all notes, create a welcome note if empty
  const notes = await getAllNotes();
  if (notes.length === 0) {
    const welcome = { id: Date.now().toString(), title: 'Welcome', content: '# Hello\n\nStart writing here.' };
    await saveNote(welcome);
    await refreshNoteList();
    notes.push(welcome);
  }
  
  // Open the first three notes into the three panes (or fewer)
  for (let i = 0; i < 3 && i < notes.length; i++) {
    await openNoteInPane(i, notes[i].id);
  }
});

// ----- Helper: refresh left sidebar list -----
async function refreshNoteList() {
  const notes = await getAllNotes();
  notes.sort((a, b) => b.updatedAt - a.updatedAt); // newest first
  const sidebarUl = document.getElementById('note-list');
  if (!sidebarUl) return;
  sidebarUl.innerHTML = '';
  for (const note of notes) {
    const li = document.createElement('li');
    li.textContent = note.title;
    li.style.cursor = 'pointer';
    li.addEventListener('click', () => {
      // Find first empty pane, or overwrite pane 0
      let paneIndex = activePaneNotes.findIndex(id => id === null);
      if (paneIndex === -1) paneIndex = 0; // overwrite first pane if all full
      openNoteInPane(paneIndex, note.id);
    });
    
    // Delete button (small X)
    const delBtn = document.createElement('span');
    delBtn.textContent = ' ❌';
    delBtn.style.marginLeft = '10px';
    delBtn.style.cursor = 'pointer';
    delBtn.addEventListener('click', async (e) => {
      e.stopPropagation();
      if (confirm(`Delete "${note.title}"?`)) {
        await deleteNote(note.id);
        // Remove from any pane that had it open
        for (let i = 0; i < activePaneNotes.length; i++) {
          if (activePaneNotes[i] === note.id) {
            activePaneNotes[i] = null;
            // Clear the pane UI
            const pane = document.querySelector(`.pane[data-pane="${i}"]`);
            if (pane) {
              const titleDiv = pane.querySelector('.note-title');
              const textarea = pane.querySelector('textarea');
              if (titleDiv) titleDiv.textContent = '[Empty]';
              if (textarea) textarea.value = '';
            }
          }
        }
        await refreshNoteList();
      }
    });
    li.appendChild(delBtn);
    sidebarUl.appendChild(li);
  }
}

// ----- Open a note into a specific pane (0,1,2) -----
async function openNoteInPane(paneIndex, noteId) {
  const note = await getNote(noteId);
  if (!note) return;
  
  // Update global state
  activePaneNotes[paneIndex] = noteId;
  
  // Get the pane element (each pane must have data-pane="0", "1", "2")
  const pane = document.querySelector(`.pane[data-pane="${paneIndex}"]`);
  if (! pane) return;
  
  // Update title and textarea inside the pane
  const titleElem = pane.querySelector('.note-title');
  const textarea = pane.querySelector('textarea');
  if (titleElem) titleElem.textContent = note.title;
  if (textarea) {
    textarea.value = note.content;
    // 🔥 ATTACH AUTO-SAVE to this textarea
    setupAutoSave(textarea, noteId);
  }
}

// ----- Auto-save with debounce (500ms) -----
function setupAutoSave(textareaElement, noteId) {
  let timeout;
  const handler = () => {
    clearTimeout(timeout);
    timeout = setTimeout(async () => {
      const note = await getNote(noteId);
      if (note) {
        note.content = textareaElement.value;
        await saveNote(note);
        console.log(`Auto-saved "${note.title}"`);
      }
    }, 500);
  };
  textareaElement.addEventListener('input', handler);
  // Optional: store handler to remove later if needed, but fine for now
}

// ----- Create a new note -----
async function createNewNote() {
  const newId = Date.now().toString();
  const newNote = { id: newId, title: 'Untitled', content: '' };
  await saveNote(newNote);
  await refreshNoteList();
  // Open it in the first empty pane, or pane 0
  const emptyIndex = activePaneNotes.findIndex(id => id === null);
  const target = emptyIndex !== -1 ? emptyIndex : 0;
  await openNoteInPane(target, newId);
}

// Make createNewNote available globally for the "New Note" button
window.createNewNote = createNewNote;