import { useState } from "react";

const CLOUDS = ["aws", "azure", "gcp", "iac"];

export default function IngestPage() {
  const [tab, setTab] = useState<'upload'|'live'>('upload');
  const [files, setFiles] = useState<File[]>([]);
  const [uploaded, setUploaded] = useState<Record<string, string>>({});
  const [uploading, setUploading] = useState(false);
  const [parsing, setParsing] = useState<string | null>(null);
  const [toast, setToast] = useState<string>("");
  // Live tab state
  const [liveCloud, setLiveCloud] = useState<'aws'|'azure'|'gcp'>('aws');
  const [liveLoading, setLiveLoading] = useState(false);
  const [liveProgress, setLiveProgress] = useState(0);
  const [showPerms, setShowPerms] = useState(false);
  const [permissions, setPermissions] = useState("");

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setFiles(Array.from(e.dataTransfer.files));
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    setFiles(Array.from(e.target.files || []));
  }

  async function handleUpload() {
    setUploading(true);
    setToast("");
    const formData = new FormData();
    files.forEach(f => formData.append("files", f));
    const res = await fetch("/api/ingest/files", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setUploaded(data.upload_ids || {});
    setUploading(false);
    setToast(res.ok ? "Files uploaded!" : "Upload failed.");
  }

  async function handleParse(cloud: string) {
    setParsing(cloud);
    setToast("");
    const res = await fetch(`/api/ingest/parse?cloud=${cloud}&upload_id=${Object.values(uploaded).join("&upload_id=")}`, {
      method: "POST",
    });
    const data = await res.json();
    setParsing(null);
    setToast(res.ok ? `Parsed: ${data.assets} assets` : "Parse failed.");
  }

  // Live tab handlers
  async function handleLiveStart() {
    setLiveLoading(true);
    setLiveProgress(10);
    setToast("");
    try {
      const res = await fetch("/api/ingest/live", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cloud: liveCloud }),
      });
      const data = await res.json();
      setLiveProgress(100);
      setToast(res.ok ? `Ingested: ${data.ingested} assets` : "Live ingest failed.");
    } catch {
      setToast("Live ingest failed.");
    } finally {
      setLiveLoading(false);
      setTimeout(() => setLiveProgress(0), 1000);
    }
  }

  async function handleViewPerms() {
    const res = await fetch(`/api/ingest/live/permissions?cloud=${liveCloud}`);
    const data = await res.json();
    setPermissions(data.permissions || "");
    setShowPerms(true);
  }

  return (
    <div className="max-w-2xl mx-auto py-10">
      <h1 className="text-3xl font-bold mb-8">Ingest</h1>
      <div className="mb-6 flex gap-4">
        <button className={tab==='upload'?"font-bold underline":""} onClick={()=>setTab('upload')}>Upload</button>
        <button className={tab==='live'?"font-bold underline":""} onClick={()=>setTab('live')}>Live</button>
      </div>
      {tab === 'upload' && (
        <>
          <div className="mb-6">
            <div
              className="border-2 border-dashed rounded p-6 text-center cursor-pointer bg-gray-50"
              onDrop={handleDrop}
              onDragOver={e => e.preventDefault()}
            >
              <input
                type="file"
                multiple
                className="hidden"
                id="file-upload"
                onChange={handleFileChange}
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                Drag & drop files here or click to select
              </label>
            </div>
            {files.length > 0 && (
              <div className="mt-4">
                <div className="font-semibold mb-2">Selected files:</div>
                <ul className="mb-2">
                  {files.map(f => <li key={f.name}>{f.name}</li>)}
                </ul>
                <button
                  className="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700 disabled:opacity-50"
                  onClick={handleUpload}
                  disabled={uploading}
                >
                  {uploading ? "Uploading..." : "Upload"}
                </button>
              </div>
            )}
          </div>
          {Object.keys(uploaded).length > 0 && (
            <div className="mb-6">
              <div className="font-semibold mb-2">Uploaded files:</div>
              <ul className="mb-2">
                {Object.keys(uploaded).map(f => <li key={f}>{f}</li>)}
              </ul>
              <div className="flex gap-4">
                {CLOUDS.map(cloud => (
                  <button
                    key={cloud}
                    className="bg-green-600 text-white px-4 py-2 rounded shadow hover:bg-green-700 disabled:opacity-50"
                    onClick={() => handleParse(cloud)}
                    disabled={!!parsing}
                  >
                    {parsing === cloud ? "Parsing..." : `Parse as ${cloud}`}
                  </button>
                ))}
              </div>
            </div>
          )}
        </>
      )}
      {tab === 'live' && (
        <div className="mb-6">
          <div className="mb-4">
            <label className="font-semibold mr-2">Cloud:</label>
            <select value={liveCloud} onChange={e=>setLiveCloud(e.target.value as any)} className="border rounded p-1">
              <option value="aws">AWS</option>
              <option value="azure">Azure</option>
              <option value="gcp">GCP</option>
            </select>
          </div>
          <div className="flex gap-4 mb-4">
            <button className="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700 disabled:opacity-50" onClick={handleLiveStart} disabled={liveLoading}>
              {liveLoading ? "Running..." : "Start"}
            </button>
            <button className="bg-gray-600 text-white px-4 py-2 rounded shadow hover:bg-gray-700" onClick={handleViewPerms}>
              View Permissions
            </button>
          </div>
          {liveLoading && <progress value={liveProgress} max={100} className="w-full" />}
          {showPerms && (
            <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
              <div className="bg-white p-6 rounded shadow max-w-md">
                <h2 className="text-xl font-bold mb-4">Required Permissions</h2>
                <div className="mb-4">{permissions}</div>
                <button className="bg-blue-600 text-white px-4 py-2 rounded" onClick={()=>setShowPerms(false)}>Close</button>
              </div>
            </div>
          )}
        </div>
      )}
      {toast && (
        <div className="fixed bottom-6 right-6 bg-black text-white px-4 py-2 rounded shadow">
          {toast}
        </div>
      )}
    </div>
  );
}
