const API_URL = "http://127.0.0.1:8000";

export const tokenStore = {
  get: () => localStorage.getItem("access_token"),
  set: (token) => localStorage.setItem("access_token", token),
  clear: () => localStorage.removeItem("access_token"),
};

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = tokenStore.get();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    if (response.status === 401) tokenStore.clear();
    const detail = typeof data === "object" ? data.detail : data;
    throw new Error(
      Array.isArray(detail)
        ? detail.map((item) => item.msg).join("; ")
        : detail || `Ошибка ${response.status}`,
    );
  }
  return data;
}

export const api = {
  async login(email, password) {
    const body = new URLSearchParams({ username: email, password });
    const data = await request("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    tokenStore.set(data.access_token);
    return data;
  },

  register(payload) {
    return request("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  },

  me: () => request("/users/me"),
  updateMe: (payload) =>
    request("/users/me", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  changePassword: (payload) =>
    request("/users/me/password", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  documents: () => request("/documents/"),
  stats: () => request("/documents/stats"),
  upload: (file) => {
    const body = new FormData();
    body.append("file", file);
    return request("/documents/upload", { method: "POST", body });
  },
  removeDocument: (id) => request(`/documents/${id}`, { method: "DELETE" }),
  download: async (id, name) => {
    const response = await fetch(`${API_URL}/documents/${id}/download`, {
      headers: { Authorization: `Bearer ${tokenStore.get()}` },
    });
    if (!response.ok) throw new Error("Не удалось скачать документ");
    const url = URL.createObjectURL(await response.blob());
    const link = document.createElement("a");
    link.href = url;
    link.download = name || "document.pdf";
    link.click();
    URL.revokeObjectURL(url);
  },
  summary: (id) => request(`/chat/documents/${id}/summary`, { method: "POST" }),
  questions: (id, amount = 5) =>
    request(`/chat/documents/${id}/questions?amount=${amount}`, { method: "POST" }),
  ask: (id, question) =>
    request(`/chat/documents/${id}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    }),
};
