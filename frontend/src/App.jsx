import { useEffect, useMemo, useState } from "react";
import { api, tokenStore } from "./services/api.js";

const Icon = ({ name }) => {
  const icons = {
    home: "⌂",
    files: "▤",
    upload: "+",
    user: "○",
    logout: "↪",
    search: "⌕",
    spark: "✦",
    chat: "◌",
    download: "↓",
    trash: "×",
  };
  return <span className="icon" aria-hidden="true">{icons[name] || "•"}</span>;
};

const formatSize = (bytes = 0) => {
  if (!bytes) return "—";
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
};

const normalizeDocuments = (data) =>
  Array.isArray(data) ? data : data?.documents || data?.items || [];

function Auth({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "register") {
        await api.register(form);
      }
      await api.login(form.email, form.password);
      onAuthenticated();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-shell">
      <section className="auth-story">
        <div className="brand brand-light"><span className="brand-mark">A</span> AI Knowledge Hub</div>
        <div className="story-copy">
          <div className="eyebrow">YOUR PERSONAL AI WORKSPACE</div>
          <h1>Turn documents into <em>knowledge.</em></h1>
          <p>Upload your materials, ask questions and get clear answers grounded in your own documents.</p>
          <div className="feature-row">
            <span>✦ AI summaries</span><span>◌ Document chat</span><span>✓ Study questions</span>
          </div>
        </div>
        <div className="orb orb-one" /><div className="orb orb-two" />
      </section>
      <section className="auth-panel">
        <form className="auth-card" onSubmit={submit}>
          <div className="mobile-brand"><span className="brand-mark">A</span> AI Knowledge Hub</div>
          <p className="eyebrow">{mode === "login" ? "WELCOME BACK" : "CREATE YOUR SPACE"}</p>
          <h2>{mode === "login" ? "Sign in to continue" : "Create an account"}</h2>
          <p className="muted">{mode === "login" ? "Your documents are waiting for you." : "Start building your knowledge library."}</p>
          {mode === "register" && (
            <label>Username<input required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} placeholder="Darina" /></label>
          )}
          <label>Email<input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="you@example.com" /></label>
          <label>Password<input required minLength="6" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="••••••••" /></label>
          {error && <div className="alert">{error}</div>}
          <button className="primary wide" disabled={loading}>{loading ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}</button>
          <p className="switch-copy">{mode === "login" ? "New here?" : "Already have an account?"} <button type="button" className="text-button" onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>{mode === "login" ? "Create account" : "Sign in"}</button></p>
        </form>
      </section>
    </main>
  );
}

function Sidebar({ page, setPage, user, onLogout }) {
  const items = [["dashboard", "home", "Overview"], ["documents", "files", "Documents"], ["profile", "user", "Settings"]];
  return <aside className="sidebar">
    <div className="brand"><span className="brand-mark">A</span><span>AI Knowledge<br />Hub</span></div>
    <nav>{items.map(([id, icon, label]) => <button key={id} className={page === id ? "active" : ""} onClick={() => setPage(id)}><Icon name={icon} />{label}</button>)}</nav>
    <div className="sidebar-bottom"><div className="mini-user"><div className="avatar">{(user?.username || user?.email || "U")[0].toUpperCase()}</div><div><strong>{user?.username || "User"}</strong><small>{user?.email}</small></div></div><button onClick={onLogout}><Icon name="logout" />Log out</button></div>
  </aside>;
}

function Topbar({ title, onUpload }) {
  return <header className="topbar"><div><p className="eyebrow">AI KNOWLEDGE HUB</p><h1>{title}</h1></div>{onUpload && <button className="primary" onClick={onUpload}><Icon name="upload" /> Upload PDF</button>}</header>;
}

function DocumentCard({ doc, onOpen, onDelete, onDownload }) {
  return <article className="doc-card">
    <div className="file-badge">PDF</div>
    <div className="doc-copy"><h3 title={doc.name}>{doc.name || doc.filename || "Untitled document"}</h3><p>{formatSize(doc.size)} · {doc.page_count ? `${doc.page_count} pages` : "Ready for AI"}</p></div>
    <div className="doc-actions"><button title="Download" onClick={() => onDownload(doc)}><Icon name="download" /></button><button title="Delete" onClick={() => onDelete(doc.id)}><Icon name="trash" /></button></div>
    <button className="secondary wide" onClick={() => onOpen(doc)}>Open AI workspace <span>→</span></button>
  </article>;
}

function UploadModal({ onClose, onUploaded }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const upload = async () => {
    if (!file) return;
    setLoading(true); setError("");
    try { await api.upload(file); onUploaded(); onClose(); } catch (err) { setError(err.message); } finally { setLoading(false); }
  };
  return <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose()}><div className="modal"><button className="modal-close" onClick={onClose}>×</button><div className="modal-icon">↑</div><h2>Upload a document</h2><p className="muted">Add a PDF up to 50 MB. We’ll prepare it for AI search.</p><label className="dropzone"><input type="file" accept="application/pdf,.pdf" onChange={(e) => setFile(e.target.files[0])} /><strong>{file ? file.name : "Choose a PDF file"}</strong><span>{file ? formatSize(file.size) : "or drag and drop it here"}</span></label>{error && <div className="alert">{error}</div>}<button className="primary wide" disabled={!file || loading} onClick={upload}>{loading ? "Processing…" : "Upload document"}</button></div></div>;
}

function Dashboard({ documents, stats, onUpload, onOpen, onNavigate }) {
  const recent = documents.slice(0, 3);
  return <><Topbar title="Good to see you" onUpload={onUpload} /><div className="page-body">
    <section className="hero-card"><div><p className="eyebrow">YOUR KNOWLEDGE, AMPLIFIED</p><h2>Ask better questions.<br /><em>Learn faster.</em></h2><p>Open any document to create a summary, generate study questions or chat with its content.</p><button className="light-button" onClick={() => onNavigate("documents")}>Explore library →</button></div><div className="hero-glyph">✦</div></section>
    <section className="stats-grid"><div><span>Documents</span><strong>{stats?.total_documents ?? documents.length}</strong><small>in your library</small></div><div><span>Total storage</span><strong>{formatSize(stats?.total_size ?? documents.reduce((sum, d) => sum + (d.size || 0), 0))}</strong><small>uploaded content</small></div><div><span>AI ready</span><strong>{stats?.processed_documents ?? documents.length}</strong><small>documents processed</small></div></section>
    <div className="section-heading"><div><p className="eyebrow">LIBRARY</p><h2>Recent documents</h2></div><button className="text-button" onClick={() => onNavigate("documents")}>View all →</button></div>
    {recent.length ? <div className="documents-grid">{recent.map((doc) => <DocumentCard key={doc.id} doc={doc} onOpen={onOpen} onDelete={() => {}} onDownload={(d) => api.download(d.id, d.name)} />)}</div> : <Empty onUpload={onUpload} />}
  </div></>;
}

function Empty({ onUpload }) { return <div className="empty"><div>▧</div><h3>Your library is empty</h3><p>Upload your first PDF and start exploring it with AI.</p><button className="primary" onClick={onUpload}>+ Upload PDF</button></div>; }

function Documents({ documents, loading, onUpload, onOpen, onRefresh }) {
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => documents.filter((doc) => (doc.name || doc.filename || "").toLowerCase().includes(query.toLowerCase())), [documents, query]);
  const remove = async (id) => { if (!window.confirm("Delete this document?")) return; try { await api.removeDocument(id); onRefresh(); } catch (err) { window.alert(err.message); } };
  return <><Topbar title="Documents" onUpload={onUpload} /><div className="page-body"><div className="library-tools"><div><p className="eyebrow">YOUR LIBRARY</p><h2>{documents.length} document{documents.length === 1 ? "" : "s"}</h2></div><label className="search"><Icon name="search" /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search documents" /></label></div>{loading ? <div className="loading">Loading library…</div> : filtered.length ? <div className="documents-grid">{filtered.map((doc) => <DocumentCard key={doc.id} doc={doc} onOpen={onOpen} onDelete={remove} onDownload={(d) => api.download(d.id, d.name || d.filename)} />)}</div> : query ? <div className="empty"><h3>No matching documents</h3><p>Try a different search.</p></div> : <Empty onUpload={onUpload} />}</div></>;
}

function Workspace({ document, onBack }) {
  const [tab, setTab] = useState("chat");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const runTool = async (type) => { setTab(type); setLoading(true); setError(""); try { const data = type === "summary" ? await api.summary(document.id) : await api.questions(document.id); setContent(data); } catch (err) { setError(err.message); } finally { setLoading(false); } };
  const send = async (event) => { event.preventDefault(); if (!question.trim() || loading) return; const text = question.trim(); setQuestion(""); setMessages((items) => [...items, { role: "user", text }]); setLoading(true); setError(""); try { const data = await api.ask(document.id, text); setMessages((items) => [...items, { role: "assistant", text: data.answer || String(data) }]); } catch (err) { setError(err.message); } finally { setLoading(false); } };
  const rawQuestions = content?.questions;

  const questionLines = (
      Array.isArray(rawQuestions) ? rawQuestions : [rawQuestions]
    )
      .filter(Boolean)
      .flatMap((item) => {
        if (typeof item === "object") {
          return [
            item.question || item.text || "Question",
            `Ответ: ${item.answer || item.response || "Ответ не сгенерирован"}`,
          ];
        }

        return String(item).split("\n");
      })
      .map((item) =>
        item.replace(/^\s*(\d+[.)]|[-•])\s*/, "").trim()
      )
      .filter(Boolean);

  const questionPairs = [];

    questionLines.forEach((line) => {
      const isAnswer = /^(ответ|answer)\s*:/i.test(line);

      if (isAnswer && questionPairs.length > 0) {
        questionPairs[questionPairs.length - 1].answer = line.replace(
          /^(ответ|answer)\s*:\s*/i,
          ""
        );
      } else if (!isAnswer) {
        questionPairs.push({
          question: line,
          answer: "Ответ не сгенерирован",
        });
      }
    });
  const questions = Array.isArray(rawQuestions)
    ? rawQuestions.map((item) =>
        typeof item === "string"
          ? item
         : item.question || item.text || JSON.stringify(item)
      ) 
    : typeof rawQuestions === "string"
      ? rawQuestions
          .split("\n")
          .map((item) =>
            item.replace(/^\s*(\d+[.)]|[-•])\s*/, "").trim()
          )
          .filter(Boolean)
      : [];
  return <><header className="workspace-top"><button className="back" onClick={onBack}>←</button><div><p className="eyebrow">AI WORKSPACE</p><h2>{document.name || document.filename}</h2></div><button className="secondary" onClick={() => api.download(document.id, document.name)}>↓ Download</button></header><div className="workspace"><aside className="tool-rail"><button className={tab === "chat" ? "active" : ""} onClick={() => setTab("chat")}><Icon name="chat" /> Chat</button><button className={tab === "summary" ? "active" : ""} onClick={() => runTool("summary")}><Icon name="spark" /> Summary</button><button className={tab === "questions" ? "active" : ""} onClick={() => runTool("questions")}><span>?</span> Questions</button></aside><section className="workspace-main">{tab === "chat" ? <><div className="chat-feed">{messages.length === 0 && <div className="chat-welcome"><div>✦</div><h2>Ask this document anything</h2><p>I’ll answer using information found in the uploaded PDF.</p></div>}{messages.map((m, i) => <div key={i} className={`message ${m.role}`}>{m.text}</div>)}{loading && <div className="message assistant">Thinking…</div>}</div><form className="chat-form" onSubmit={send}><input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask a question about this document…" /><button className="primary">Send ↑</button></form></> : <div className="result-panel"><p className="eyebrow">AI GENERATED</p><h2>{tab === "summary" ? "Document summary" : "Study questions"}</h2>{loading ? <div className="loading">Generating…</div> : error ? <div className="alert">{error}</div> : tab === "summary" ? <div className="prose">{content?.summary || "Click Summary again to generate."}</div> : 
    <div className="question-accordion">
      {questionPairs.map((item, index) => (
        <details className="question-item" key={index}>
          <summary>
            <span className="question-number">{index + 1}</span>
            <span>{item.question}</span>
            <span className="question-plus">+</span>
          </summary>

          <div className="question-answer">
            <strong>Ответ</strong>
            <p>{item.answer}</p>
          </div>
        </details>
      ))}
    </div>
  }</div>}{error && tab === "chat" && <div className="alert floating-alert">{error}</div>}</section></div></>;
}

function Profile({ user, onUpdated }) {
  const [form, setForm] = useState({ username: user?.username || "", email: user?.email || "" });
  const [passwords, setPasswords] = useState({ current_password: "", new_password: "" });
  const [message, setMessage] = useState("");
  const save = async (event) => { event.preventDefault(); try { const result = await api.updateMe(form); onUpdated(result); setMessage("Profile saved."); } catch (err) { setMessage(err.message); } };
  const changePassword = async (event) => { event.preventDefault(); try { await api.changePassword(passwords); setPasswords({ current_password: "", new_password: "" }); setMessage("Password updated."); } catch (err) { setMessage(err.message); } };
  return <><Topbar title="Settings" /><div className="page-body settings"><div className="profile-head"><div className="avatar large">{(user?.username || "U")[0].toUpperCase()}</div><div><h2>{user?.username}</h2><p>{user?.email}</p></div></div>{message && <div className="notice">{message}</div>}<div className="settings-grid"><form className="settings-card" onSubmit={save}><p className="eyebrow">PROFILE</p><h3>Personal information</h3><label>Username<input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} /></label><label>Email<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label><button className="primary">Save changes</button></form><form className="settings-card" onSubmit={changePassword}><p className="eyebrow">SECURITY</p><h3>Change password</h3><label>Current password<input required type="password" value={passwords.current_password} onChange={(e) => setPasswords({ ...passwords, current_password: e.target.value })} /></label><label>New password<input required minLength="6" type="password" value={passwords.new_password} onChange={(e) => setPasswords({ ...passwords, new_password: e.target.value })} /></label><button className="secondary">Update password</button></form></div></div></>;
}

export default function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(tokenStore.get()));
  const [page, setPage] = useState("dashboard");
  const [user, setUser] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [selected, setSelected] = useState(null);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    if (!tokenStore.get()) return;
    setLoading(true);
    try {
      const [me, docs, docStats] = await Promise.all([api.me(), api.documents(), api.stats().catch(() => null)]);
      setUser(me); setDocuments(normalizeDocuments(docs)); setStats(docStats); setAuthenticated(true);
    } catch (err) {
      if (!tokenStore.get()) setAuthenticated(false);
      else console.error(err);
    } finally { setLoading(false); }
  };

  useEffect(() => { if (authenticated) loadData(); }, [authenticated]);
  const logout = () => { tokenStore.clear(); setAuthenticated(false); setUser(null); setDocuments([]); setSelected(null); };
  if (!authenticated) return <Auth onAuthenticated={() => setAuthenticated(true)} />;
  if (selected) return <Workspace document={selected} onBack={() => setSelected(null)} />;

  return <div className="app-shell"><Sidebar page={page} setPage={setPage} user={user} onLogout={logout} /><main className="content">{page === "dashboard" && <Dashboard documents={documents} stats={stats} onUpload={() => setUploadOpen(true)} onOpen={setSelected} onNavigate={setPage} />}{page === "documents" && <Documents documents={documents} loading={loading} onUpload={() => setUploadOpen(true)} onOpen={setSelected} onRefresh={loadData} />}{page === "profile" && <Profile user={user} onUpdated={setUser} />}</main>{uploadOpen && <UploadModal onClose={() => setUploadOpen(false)} onUploaded={loadData} />}</div>;
}
