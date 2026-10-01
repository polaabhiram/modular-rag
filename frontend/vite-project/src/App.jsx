import { useEffect, useRef, useState } from "react";
import Sidebar from "./Sidebar.jsx";
import Answer from "./Answer.jsx";
import { ask, getStatus, rebuildIndex, uploadFiles } from "./api.js";

export default function App() {
  const [status, setStatus] = useState({ ready: false, documents: [] });
  const [note, setNote] = useState({ text: "", error: false });
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const logRef = useRef(null);
  const taRef = useRef(null);
  const say = (text, error = false) => setNote({ text, error });

  useEffect(() => {
    getStatus()
  .then((data) => {
    setStatus({
      ready: data.ready ?? false,
      documents: data.documents ?? [],
    });
  })
  .catch((e) => {
    say("Cannot reach the server: " + e.message, true);
  });
  }, []);

  useEffect(() => {
    logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [messages]);

  async function onUpload(files) {
    if (!files.length) return;
    say(`Indexing ${files.length} file(s)…`);
    try {
      const r = await uploadFiles(files);
      setStatus({ ready: r.ready, documents: r.documents });
      say(r.errors.length ? r.errors.join(" • ") : "Added " + r.saved.join(", "), r.errors.length > 0);
    } catch (e) {
      say(e.message, true);
    }
  }

  async function onRebuild() {
    say("Rebuilding index…");
    try {
      const r = await rebuildIndex();
      setStatus({ ready: r.ready, documents: r.documents });
      say(`Index rebuilt (${r.chunks} chunks).`);
    } catch (e) {
      say(e.message, true);
    }
  }

  async function submit(e) {
    e.preventDefault();
    const q = input.trim();
    if (!q || busy) return;
    if (!status.ready) return say("Upload a document before asking a question.", true);

    const id = Date.now();
    setInput("");
    setBusy(true);
    setMessages((m) => [...m, { id, role: "user", text: q }, { id: id + 1, role: "assistant", loading: true }]);
    let patch;
    try {
      patch = { loading: false, data: await ask(q) };
    } catch (err) {
      patch = { loading: false, error: err.message };
    }
    setMessages((m) => m.map((x) => (x.id === id + 1 ? { ...x, ...patch } : x)));
    setBusy(false);
    taRef.current?.focus();
  }

  function grow(e) {
    setInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = e.target.scrollHeight + "px";
  }

  return (
    <>
      <Sidebar documents={status.documents} note={note} onUpload={onUpload} onRebuild={onRebuild} />
      <main>
        <div className="log" ref={logRef} aria-live="polite">
          {messages.length === 0 ? (
            <div className="empty">
              <b>{status.ready ? "What would you like to know?" : "Add a document to begin"}</b>
              {status.ready
                ? "Each answer links to the exact passages it used."
                : "Upload a PDF or TXT file in the panel, then ask about it."}
            </div>
          ) : (
            messages.map((m) => (m.role === "user" ? <div key={m.id} className="q">{m.text}</div> : <Answer key={m.id} message={m} />))
          )}
        </div>
        <form onSubmit={submit}>
          <textarea
            ref={taRef}
            rows={1}
            value={input}
            onChange={grow}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), e.currentTarget.form.requestSubmit())}
            placeholder="Ask a question about your documents"
            aria-label="Question"
          />
          <button className="send" type="submit" disabled={busy}>Ask</button>
        </form>
      </main>
    </>
  );
}