
import { useState } from "react";

function FindingsChart({ findings }: { findings: any[] }) {
  const summary = findings.reduce((acc, f) => {
    acc[f.status] = (acc[f.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  return (
    <div className="bg-gray-50 p-4 rounded mb-4">
      <h2 className="text-lg font-bold mb-2">Findings by Status</h2>
      <div className="flex gap-4">
        <div className="text-green-700">PASS: {summary.PASS || 0}</div>
        <div className="text-red-700">FAIL: {summary.FAIL || 0}</div>
        <div className="text-yellow-700">WAIVED: {summary.WAIVED || 0}</div>
      </div>
    </div>
  );
}

export default function AccessPage() {
  const [hrFile, setHrFile] = useState<File|null>(null);
  const [iamFile, setIamFile] = useState<File|null>(null);
  const [paths, setPaths] = useState<{hr_path:string, iam_path:string}|null>(null);
  const [findings, setFindings] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleHr(e: any) { setHrFile(e.target.files[0]); }
  function handleIam(e: any) { setIamFile(e.target.files[0]); }

  async function handleUpload() {
    if (!hrFile || !iamFile) return;
    setLoading(true);
    setError("");
    const form = new FormData();
    form.append("hr", hrFile);
    form.append("iam", iamFile);
    try {
      const res = await fetch("/api/modules/access/upload", { method: "POST", body: form });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setPaths(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleIngest() {
    if (!paths) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/modules/access/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(paths)
      });
      if (!res.ok) throw new Error(await res.text());
      // Simulate findings fetch (in real app, fetch from /api/results)
      setFindings([
        { status: "FAIL", control: "GHOST_ACCOUNT" },
        { status: "FAIL", control: "ADMIN_NO_MFA" },
        { status: "FAIL", control: "STALE_ACCOUNT_90D" },
        { status: "PASS", control: "GHOST_ACCOUNT" },
      ]);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto py-10">
      <h1 className="text-2xl font-bold mb-6">Access Module</h1>
      <div className="mb-4">
        <input type="file" accept=".csv" onChange={handleHr} />
        <input type="file" accept=".csv" onChange={handleIam} className="ml-2" />
        <button className="ml-2 px-4 py-2 bg-blue-600 text-white rounded" disabled={!hrFile || !iamFile || loading} onClick={handleUpload}>Upload</button>
      </div>
      {paths && (
        <div className="mb-4">
          <button className="px-4 py-2 bg-green-600 text-white rounded" disabled={loading} onClick={handleIngest}>Ingest & Detect</button>
        </div>
      )}
      {error && <div className="text-red-600 mb-2">{error}</div>}
      <FindingsChart findings={findings} />
    </div>
  );
}
