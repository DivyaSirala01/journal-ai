const API_BASE = import.meta.env.VITE_API_URL || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message =
      typeof data.detail === "string"
        ? data.detail
        : data.message || "Request failed";
    throw new Error(message);
  }

  return data;
}

export function getNotes() {
  return request("/notes");
}

export function createNote(content) {
  return request("/notes", {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export function updateNote(id, content) {
  return request(`/notes/${id}`, {
    method: "PUT",
    body: JSON.stringify({ content }),
  });
}

export function deleteNote(id) {
  return request(`/notes/${id}`, { method: "DELETE" });
}

export function deleteAllNotes() {
  return request("/notes", { method: "DELETE" });
}
