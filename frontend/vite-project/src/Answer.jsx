import { useRef, useState } from "react";

export default function Answer({ message }) {
  const { loading, error, data } = message;
  const [open, setOpen] = useState(() => new Set());
  const [flash, setFlash] = useState(null);
  const refs = useRef({});

  if (loading) return <div className="a"><span className="dots"><i /><i /><i /></span></div>;
  if (error) return <div className="a"><div className="text err">{error}</div></div>;

  const ids = new Set(data.sources.map((s) => s.id));

  // Turn "[2]" markers into clickable chips without touching innerHTML
  const parts = data.answer.split(/(\[\d+\])/g).map((part, i) => {
    const m = part.match(/^\[(\d+)\]$/);
    const id = m && Number(m[1]);
    if (!m || !ids.has(id)) return part;
    return (
      <button key={i} type="button" className="cite" aria-label={`Show source ${id}`} onClick={() => jump(id)}>
        {id}
      </button>
    );
  });

  function jump(id) {
    setOpen((o) => new Set(o).add(id));
    setFlash(null);
    requestAnimationFrame(() => {
      setFlash(id);
      refs.current[id]?.scrollIntoView({ block: "nearest", behavior: "smooth" });
    });
  }

  return (
    <div className="a">
      <div className="text">{parts}</div>
      {data.sources.length > 0 && (
        <div className="src">
          {data.sources.map((s) => (
            <details
              key={s.id}
              ref={(el) => (refs.current[s.id] = el)}
              open={open.has(s.id)}
              className={(data.cited.includes(s.id) ? "cited " : "") + (flash === s.id ? "flash" : "")}
              onAnimationEnd={() => setFlash(null)}
              onToggle={(e) => {
                const isOpen = e.currentTarget.open;
                setOpen((o) => {
                  const n = new Set(o);
                  isOpen ? n.add(s.id) : n.delete(s.id);
                  return n;
                });
              }}
            >
              <summary>
                <b>{s.id}</b> {s.filename}
                {s.page ? `, page ${s.page}` : ""} <small>match {Math.round(s.score * 100)}%</small>
              </summary>
              <p>{s.text}</p>
            </details>
          ))}
        </div>
      )}
    </div>
  );
}