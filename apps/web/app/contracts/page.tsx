
import { useState } from "react";

function ParsedFields({ fields }: { fields: any }) {
  if (!fields) return null;
  return (
    <div className="bg-gray-50 p-4 rounded mb-4">
      <h2 className="text-lg font-bold mb-2">Parsed Fields</h2>
      <ul className="text-sm">
        <li><b>Renewal Date:</b> {fields.renewal_date || "-"}</li>
        <li><b>Termination Notice (days):</b> {fields.termination_notice_days || "-"}</li>
        <li><b>Breach Window (hours):</b> {fields.breach_window_hours || "-"}</li>
        <li><b>Data Location:</b> {fields.data_location || "-"}</li>
        <li><b>DPA Present:</b> {fields.dpa_present ? "Yes" : "No"}</li>
      </ul>
    </div>
  );
}

export default function ContractsPage() {
  const [file, setFile] = useState<File|null>(null);
  const [uploadPath, setUploadPath] = useState("");
  const [fields, setFields] = useState<any>(null);
  const [meta, setMeta] = useState({ vendor: "", product: "", region: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [evidence, setEvidence] = useState<string>("");

  function handleFile(e: any) {
    setFile(e.target.files[0]);
  }

  async function handleUpload() {
    if (!file) return;
    setLoading(true);
    setError("");
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch("/api/modules/contracts/upload", { method: "POST", body: form });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setUploadPath(data.doc_path);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleIngest() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/modules/contracts/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ doc_path: uploadPath, ...meta })
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      // Simulate parsed fields fetch (in real app, fetch from /api/documents)
      setFields(data.fields || {});
      setEvidence(data.evidence || uploadPath);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto py-10">
      <h1 className="text-2xl font-bold mb-6">Contracts</h1>
      <div className="mb-4">
        <input type="file" accept=".pdf,.docx,.txt" onChange={handleFile} />
        <button className="ml-2 px-4 py-2 bg-blue-600 text-white rounded" disabled={!file || loading} onClick={handleUpload}>Upload</button>
      </div>
      {uploadPath && (
        <div className="mb-4">
          <input value={meta.vendor} onChange={e=>setMeta(m=>({...m, vendor: e.target.value}))} placeholder="Vendor" className="border rounded p-1 mr-2" />
          <input value={meta.product} onChange={e=>setMeta(m=>({...m, product: e.target.value}))} placeholder="Product" className="border rounded p-1 mr-2" />
          <input value={meta.region} onChange={e=>setMeta(m=>({...m, region: e.target.value}))} placeholder="Region" className="border rounded p-1 mr-2" />
          <button className="px-4 py-2 bg-green-600 text-white rounded" disabled={loading} onClick={handleIngest}>Ingest & Extract</button>
        </div>
      )}
      {error && <div className="text-red-600 mb-2">{error}</div>}
      <ParsedFields fields={fields} />
      {evidence && (
        <div className="mb-4">
          <b>Evidence:</b> <a href={"/evidence/" + encodeURIComponent(evidence)} className="underline">View Source</a>
        </div>
      )}
    </div>
  );
}
