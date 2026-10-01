async function request(url, opts) {
  const r = await fetch(url, opts);
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(typeof d.detail === "string" ? d.detail : `Request failed (${r.status})`);
  return d;
}

export const getStatus = () => request("/api/status");
export const rebuildIndex = () => request("/api/ingest", { method: "POST" });
export const uploadFiles = (files) => {
  const fd = new FormData();
  [...files].forEach((f) => fd.append("files", f));
  return request("/api/upload", { method: "POST", body: fd });
};
export const ask = (question) =>
  request("/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });