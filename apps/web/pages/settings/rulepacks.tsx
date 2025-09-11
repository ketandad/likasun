import { useEffect, useState } from "react";

interface Status {
  current: string | null;
  available: string[];
}

export default function RulepacksPage() {
  const [status, setStatus] = useState<Status>({ current: null, available: [] });
  const [file, setFile] = useState<File | null>(null);
  const [rollback, setRollback] = useState<string>("");

  async function load() {
    const res = await fetch("/api/rules/status");
    if (res.ok) setStatus(await res.json());
  }

  useEffect(() => {
    load();
  }, []);

  async function upload(apply: boolean) {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    await fetch(`/api/rules/upload?apply=${apply}`, { method: "POST", body: form });
    setFile(null);
    load();
  }

  async function doRollback() {
    if (!rollback) return;
    await fetch(`/api/rules/rollback?version=${rollback}`, { method: "POST" });
    load();
  }

  return (
    <div>
      <h1>Rule Packs</h1>
      <p>Current version: {status.current || "none"}</p>
      <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <button onClick={() => upload(false)}>Preview</button>
      <button onClick={() => upload(true)}>Apply</button>
      <div>
        <select value={rollback} onChange={(e) => setRollback(e.target.value)}>
          <option value="">Select version</option>
          {status.available.map((v) => (
            <option key={v} value={v}>
              {v}
            </option>
          ))}
        </select>
        <button onClick={doRollback}>Rollback</button>
      </div>
    </div>
  );
}
