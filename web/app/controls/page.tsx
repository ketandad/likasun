import { useEffect, useState } from "react";

const SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

export default function ControlsPage() {
  const [controls, setControls] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [severity, setSeverity] = useState("");
  const [framework, setFramework] = useState("");

  useEffect(() => {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (severity) params.set("severity", severity);
    if (framework) params.set("framework", framework);
    fetch(`/api/rules?${params.toString()}`)
      .then(r => r.json())
      .then(setControls);
  }, [search, severity, framework]);

  return (
    <div className="max-w-4xl mx-auto py-10">
      <h1 className="text-3xl font-bold mb-8">Controls Catalog</h1>
      <div className="mb-4 flex gap-4">
        <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search title or ID" className="border rounded p-1" />
        <select value={severity} onChange={e=>setSeverity(e.target.value)} className="border rounded p-1">
          <option value="">All Severities</option>
          {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <input value={framework} onChange={e=>setFramework(e.target.value)} placeholder="Framework" className="border rounded p-1" />
      </div>
      <table className="w-full border mb-4">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-2">ID</th>
            <th className="p-2">Title</th>
            <th className="p-2">Severity</th>
            <th className="p-2">Frameworks</th>
            <th className="p-2">Logic Hash</th>
          </tr>
        </thead>
        <tbody>
          {controls.map((c: any) => (
            <tr key={c.control_id} className="border-t">
              <td className="p-2 text-xs">{c.control_id}</td>
              <td className="p-2 text-xs">{c.title}</td>
              <td className="p-2 text-xs">{c.severity}</td>
              <td className="p-2 text-xs">
                {Array.isArray(c.frameworks) ? c.frameworks.map((f: string) => (
                  <span key={f} className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded mr-1 text-xs">{f}</span>
                )) : null}
              </td>
              <td className="p-2 text-xs">{c.logic_hash}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
