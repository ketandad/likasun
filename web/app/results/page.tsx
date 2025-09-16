import { useEffect, useState } from "react";

const STATUSES = ["PASS", "FAIL", "WAIVED", "NA"];
const SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

// Error boundary (simple)
function ErrorBoundary({ children }: { children: any }) {
  const [error, setError] = useState<string | null>(null);
  if (error) {
    return (
      <div className="p-8 text-center">
        <div className="text-red-600 mb-4">Something went wrong.</div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded" onClick={()=>window.location.reload()}>Retry</button>
        <a href="mailto:support@raybeam.io" className="ml-4 underline">Contact Support</a>
      </div>
    );
  }
  return children;
}
function ResultDrawer({ resultId, onClose }: { resultId: string, onClose: () => void }) {
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    if (!resultId) return;
    fetch(`/api/results/${resultId}`)
      .then(r => r.json())
      .then(setData);
  }, [resultId]);
  if (!resultId) return null;
  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded shadow max-w-lg w-full relative">
        <button className="absolute top-2 right-2 text-gray-500" onClick={onClose}>✕</button>
        <h2 className="text-xl font-bold mb-2">Result Details</h2>
        {!data ? <div>Loading...</div> : (
          <>
            <div className="mb-2 font-semibold">Control:</div>
            <div className="mb-2">{data.control_title} <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">{data.status}</span></div>
            <div className="mb-2 font-semibold">Frameworks:</div>
            <div className="mb-2">{data.frameworks?.join(", ")}</div>
            <div className="mb-2 font-semibold">Asset:</div>
            <pre className="bg-gray-100 p-2 rounded text-xs mb-2">{JSON.stringify(data.asset, null, 2)}</pre>
            <div className="mb-2 font-semibold">Evidence:</div>
            <pre className="bg-gray-100 p-2 rounded text-xs mb-2">{JSON.stringify(data.evidence, null, 2)}</pre>
            <div className="mb-2 font-semibold">Fix Guidance:</div>
            <pre className="bg-gray-100 p-2 rounded text-xs mb-2">{JSON.stringify(data.fix, null, 2)}</pre>
            <button className="bg-gray-200 px-2 py-1 rounded text-xs" onClick={()=>navigator.clipboard.writeText(JSON.stringify(data.fix, null, 2))}>Copy Fix</button>
          </>
        )}
      </div>
    </div>
  );
}

export default function ResultsPage() {
  const [results, setResults] = useState<any[]>([]);
  const [status, setStatus] = useState("");
  const [severity, setSeverity] = useState("");
  const [cloud, setCloud] = useState("");
  const [framework, setFramework] = useState("");
  const [page, setPage] = useState(1);
  const [drawerId, setDrawerId] = useState<string>("");
  const [presetName, setPresetName] = useState("");
  const [presets, setPresets] = useState<any[]>([]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (status) params.set("status", status);
    if (severity) params.set("severity", severity);
    if (cloud) params.set("cloud", cloud);
    if (framework) params.set("framework", framework);
    params.set("page", String(page));
    params.set("page_size", "20");
    fetch(`/api/results?${params.toString()}`)
      .then(r => r.json())
      .then(data => setResults(data.items || []));
  }, [status, severity, cloud, framework, page]);

  useEffect(() => {
    const saved = localStorage.getItem("rb.resultPresets");
    setPresets(saved ? JSON.parse(saved) : []);
  }, []);

  function savePreset() {
    const newPreset = { name: presetName, status, severity, cloud, framework, lastUsed: Date.now() };
    const updated = [newPreset, ...presets.filter(p => p.name !== presetName)].sort((a, b) => b.lastUsed - a.lastUsed);
    setPresets(updated);
    localStorage.setItem("rb.resultPresets", JSON.stringify(updated));
    setPresetName("");
  }

  function applyPreset(p: any) {
    setStatus(p.status || "");
    setSeverity(p.severity || "");
    setCloud(p.cloud || "");
    setFramework(p.framework || "");
    p.lastUsed = Date.now();
    savePreset();
  }


  function getParams() {
    const params = new URLSearchParams();
    if (status) params.set("status", status);
    if (severity) params.set("severity", severity);
    if (cloud) params.set("cloud", cloud);
    if (framework) params.set("framework", framework);
    return params;
  }

  async function exportCSV() {
    const params = getParams();
    const res = await fetch(`/api/results/export.csv?${params.toString()}`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'results.csv';
    a.click();
    URL.revokeObjectURL(url);
    alert(`CSV size: ${blob.size} bytes`);
  }

  async function exportJSON() {
    const params = getParams();
    const res = await fetch(`/api/results/export.json?${params.toString()}`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'results.json';
    a.click();
    URL.revokeObjectURL(url);
    alert(`JSON size: ${blob.size} bytes`);
  }

  // Show banner if any result is WAIVED
  const waived = results.filter(r => r.status === "WAIVED");
  return (
    <div className="max-w-5xl mx-auto py-10">
      <h1 className="text-3xl font-bold mb-8">Results</h1>
      {waived.length > 0 && (
        <div className="mb-4 p-3 bg-yellow-100 text-yellow-800 rounded border border-yellow-300">
          {waived.length} result{waived.length > 1 ? "s" : ""} waived by exception. <a href="/exceptions" className="underline">Manage exceptions</a>
        </div>
      )}
      <div className="sticky top-0 bg-white z-10 mb-4 flex gap-4 items-center p-2 border-b">
        <select value={status} onChange={e=>setStatus(e.target.value)} className="border rounded p-1">
          <option value="">All Statuses</option>
          {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={severity} onChange={e=>setSeverity(e.target.value)} className="border rounded p-1">
          <option value="">All Severities</option>
          {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <input value={cloud} onChange={e=>setCloud(e.target.value)} placeholder="Cloud" className="border rounded p-1" />
        <input value={framework} onChange={e=>setFramework(e.target.value)} placeholder="Framework" className="border rounded p-1" />
        <div className="relative">
          <button className="bg-green-600 text-white px-4 py-2 rounded shadow hover:bg-green-700" onClick={exportCSV}>Export CSV</button>
          <button className="bg-blue-600 text-white px-4 py-2 rounded ml-2" onClick={exportJSON}>Export JSON</button>
        </div>
        <input value={presetName} onChange={e=>setPresetName(e.target.value)} placeholder="Preset name" className="border rounded p-1" />
        <button className="bg-blue-600 text-white px-2 py-1 rounded" onClick={savePreset}>Save Preset</button>
        {presets.map((p, i) => (
          <button key={i} className="bg-gray-200 px-2 py-1 rounded text-xs" onClick={()=>applyPreset(p)}>{p.name}</button>
        ))}
      </div>
      <button aria-label="Toggle dark mode" className="px-2 py-1 border rounded mb-2" onClick={() => {
        const dark = document.documentElement.classList.toggle('dark');
        localStorage.setItem('rb.darkMode', dark ? '1' : '');
      }}>🌓</button>
      <table className="w-full border mb-4" aria-label="Results Table">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-2">Control</th>
            <th className="p-2">Status</th>
            <th className="p-2">Severity</th>
            <th className="p-2">Cloud</th>
            <th className="p-2">Asset</th>
            <th className="p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {results.length === 0 ? (
            <tr>
              <td colSpan={6} className="p-4 text-center text-gray-500">
                No results found.<br />
                <button className="mt-2 px-4 py-2 bg-blue-600 text-white rounded" onClick={()=>window.location.href='/ingest'}>Ingest Data</button>
                <button className="mt-2 ml-2 px-4 py-2 bg-green-600 text-white rounded" onClick={()=>window.location.href='/assets'}>Evaluate</button>
              </td>
            </tr>
          ) : results.map((r: any, idx: number) => (
            <tr key={r.control_id + r.asset_id} className="border-t" tabIndex={0} aria-label={`Result row ${idx+1}`}
              onKeyDown={e => { if (e.key === 'Enter') setDrawerId(r.control_id + ":" + r.asset_id); }}>
              <td className="p-2 text-xs">{r.control_title}</td>
              <td className="p-2 text-xs">
                <span className={`px-2 py-1 rounded text-xs ${r.status === "PASS" ? "bg-green-100 text-green-800" : r.status === "FAIL" ? "bg-red-100 text-red-800" : r.status === "WAIVED" ? "bg-yellow-100 text-yellow-800" : "bg-gray-100 text-gray-800"}`}>{r.status}</span>
              </td>
              <td className="p-2 text-xs">{r.severity}</td>
              <td className="p-2 text-xs">{r.cloud}</td>
              <td className="p-2 text-xs">{r.asset_id}</td>
              <td className="p-2">
                <button className="text-blue-600 underline" aria-label="View details" onClick={()=>setDrawerId(r.control_id + ":" + r.asset_id)}>Details</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex gap-2 mb-8">
        <button disabled={page===1} onClick={()=>setPage(page-1)} className="px-2 py-1 border rounded">Prev</button>
        <span>Page {page}</span>
        <button onClick={()=>setPage(page+1)} className="px-2 py-1 border rounded">Next</button>
      </div>
      {drawerId && <ResultDrawer resultId={drawerId} onClose={()=>setDrawerId("")} />}
    </div>
  );
}
