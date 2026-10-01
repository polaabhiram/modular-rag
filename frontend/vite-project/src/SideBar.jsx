import { useRef, useState } from "react";

export default function Sidebar({ documents, note, onUpload, onRebuild }) {
  const input = useRef(null);
  const [over, setOver] = useState(false);

  return (
    <aside>
      <div>
        <h1>Ask your documents</h1>
        <p>Answers come only from the files below, with the passage they came from.</p>
      </div>

      <div
        className={"drop" + (over ? " over" : "")}
        tabIndex={0}
        role="button"
        onClick={() => input.current.click()}
        onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), input.current.click())}
        onDragOver={(e) => (e.preventDefault(), setOver(true))}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => (e.preventDefault(), setOver(false), onUpload(e.dataTransfer.files))}
      >
        Drop PDF or TXT files here, or click to choose
        <input
          ref={input}
          type="file"
          accept=".pdf,.txt"
          multiple
          hidden
          onChange={(e) => (onUpload(e.target.files), (e.target.value = ""))}
        />
      </div>

      <div className={"note" + (note.error ? " err" : "")} role="status">{note.text}</div>

      <ul className="docs">
        {documents.length ? (
          documents.map((d) => (
            <li key={d.name}>
              <span title={d.name}>{d.name}</span>
              <span>{d.chunks} chunks</span>
            </li>
          ))
        ) : (
          <li><span>No documents yet</span></li>
        )}
      </ul>

      <button className="btn" type="button" onClick={onRebuild}>Rebuild index</button>
    </aside>
  );
}