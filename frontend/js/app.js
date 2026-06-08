import {
  createNote,
  deleteAllNotes,
  deleteNote,
  getNotes,
  updateNote,
} from "./api.js";

const notesList = document.getElementById("notes-list");
const noteCount = document.getElementById("note-count");
const toastEl = document.getElementById("toast");

let toastTimer;

function showToast(message, isError = false) {
  clearTimeout(toastTimer);
  toastEl.textContent = message;
  toastEl.className = `toast show${isError ? " error" : ""}`;
  toastTimer = setTimeout(() => toastEl.classList.remove("show"), 3000);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function priorityClass(priority) {
  const value = (priority || "").toLowerCase();
  if (value === "high") return "badge-high";
  if (value === "low") return "badge-low";
  return "badge-medium";
}

function formatDate(value) {
  if (!value) return "";
  return new Date(value).toLocaleString();
}

function renderNotes(notes) {
  noteCount.textContent = `${notes.length} note${notes.length === 1 ? "" : "s"}`;

  if (!notes.length) {
    notesList.innerHTML =
      '<div class="empty">No notes yet. Add one above.</div>';
    return;
  }

  notesList.innerHTML = notes
    .map(
      (note) => `
        <article class="note-card" data-id="${note.id}">
          <div class="note-meta">
            <span class="badge badge-category">${escapeHtml(note.category)}</span>
            <span class="badge ${priorityClass(note.priority)}">${escapeHtml(note.priority)}</span>
          </div>
          <div class="note-summary">${escapeHtml(note.summary)}</div>
          <div class="note-content">${escapeHtml(note.content)}</div>
          <div class="note-date">
            Created ${formatDate(note.created_on)}${
              note.updated_on ? ` · Updated ${formatDate(note.updated_on)}` : ""
            }
          </div>
          <div class="edit-area" id="edit-${note.id}">
            <textarea id="edit-text-${note.id}">${escapeHtml(note.content)}</textarea>
            <div class="actions">
              <button class="btn btn-primary btn-sm save-edit-btn" data-id="${note.id}">Save</button>
              <button class="btn btn-secondary btn-sm cancel-edit-btn" data-id="${note.id}">Cancel</button>
            </div>
          </div>
          <div class="note-actions">
            <button class="btn btn-secondary btn-sm edit-btn" data-id="${note.id}">Edit</button>
            <button class="btn btn-danger btn-sm delete-btn" data-id="${note.id}">Delete</button>
          </div>
        </article>
      `
    )
    .join("");
}

async function loadNotes() {
  const data = await getNotes();
  renderNotes(data.notes || []);
}

async function handleAddNote() {
  const input = document.getElementById("new-note");
  const button = document.getElementById("add-btn");
  const content = input.value.trim();

  if (!content) {
    showToast("Enter some text first", true);
    return;
  }

  button.disabled = true;
  button.textContent = "Saving...";

  try {
    const data = await createNote(content);
    input.value = "";
    showToast(data.note?.summary ? `Added: ${data.note.summary}` : "Note added");
    await loadNotes();
  } catch (error) {
    showToast(error.message, true);
  } finally {
    button.disabled = false;
    button.textContent = "Enter";
  }
}

async function handleDeleteNote(id) {
  if (!confirm("Delete this note?")) return;

  try {
    await deleteNote(id);
    showToast("Note deleted");
    await loadNotes();
  } catch (error) {
    showToast(error.message, true);
  }
}

async function handleDeleteAll() {
  if (!confirm("Delete all notes? This cannot be undone.")) return;

  try {
    const data = await deleteAllNotes();
    showToast(data.message);
    await loadNotes();
  } catch (error) {
    showToast(error.message, true);
  }
}

async function handleSaveEdit(id) {
  const content = document.getElementById(`edit-text-${id}`).value.trim();

  if (!content) {
    showToast("Note cannot be empty", true);
    return;
  }

  try {
    await updateNote(id, content);
    showToast("Note updated");
    await loadNotes();
  } catch (error) {
    showToast(error.message, true);
  }
}

document.getElementById("add-btn").addEventListener("click", handleAddNote);
document
  .getElementById("delete-all-btn")
  .addEventListener("click", handleDeleteAll);

notesList.addEventListener("click", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;

  const id = target.dataset.id;
  if (!id) return;

  if (target.classList.contains("delete-btn")) {
    handleDeleteNote(id);
  }

  if (target.classList.contains("edit-btn")) {
    document.getElementById(`edit-${id}`).classList.add("open");
  }

  if (target.classList.contains("cancel-edit-btn")) {
    document.getElementById(`edit-${id}`).classList.remove("open");
  }

  if (target.classList.contains("save-edit-btn")) {
    handleSaveEdit(id);
  }
});

loadNotes().catch((error) => showToast(error.message, true));
