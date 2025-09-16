
import { useEffect, useState } from "react";

function AddExceptionModal({ onClose, onAdd }: { onClose: () => void, onAdd: (exc: any) => void }) {
  const [controlId, setControlId] = useState("");
  const [selector, setSelector] = useState("{}");
  const [reason, setReason] = useState("");
  const [expiresAt, setExpiresAt] = useState("");
  const [error, setError] = useState("");
  function handleSubmit(e: any) {
    e.preventDefault();
    let sel;
    try { sel = JSON.parse(selector); } catch { setError("Selector must be valid JSON"); return; }
    fetch("/api/exceptions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ control_id: controlId, selector: sel, reason, expires_at: expiresAt })
    })
      .then(async r => {
        if (!r.ok) throw new Error(await r.text());
        return r.json();
      })
      .then(exc => { onAdd(exc); onClose(); })
      .catch(err => setError(err.message));
  }
  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <form className="bg-white p-6 rounded shadow max-w-md w-full" onSubmit={handleSubmit}>
        <h2 className="text-xl font-bold mb-4">Add Exception</h2>
        <input required value={controlId} onChange={e=>setControlId(e.target.value)} placeholder="Control ID" className="border rounded p-2 mb-2 w-full" />
        <textarea required value={selector} onChange={e=>setSelector(e.target.value)} placeholder='Selector (JSON: {"asset_id": "..."})' className="border rounded p-2 mb-2 w-full" rows={2} />
        <input required value={reason} onChange={e=>setReason(e.target.value)} placeholder="Reason" className="border rounded p-2 mb-2 w-full" />
        <input required type="date" value={expiresAt} onChange={e=>setExpiresAt(e.target.value)} className="border rounded p-2 mb-2 w-full" />
        {error && <div className="text-red-600 mb-2 text-xs">{error}</div>}
        <div className="flex gap-2 justify-end">
          <button type="button" className="px-3 py-1 bg-gray-200 rounded" onClick={onClose}>Cancel</button>
          <button type="submit" className="px-3 py-1 bg-blue-600 text-white rounded">Add</button>
        </div>
      </form>
    </div>
  );
}

export default function ExceptionsPage() {
  const [exceptions, setExceptions] = useState<any[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  function load() {
    setLoading(true);
    fetch("/api/exceptions?active=true")
      .then(r => r.json())
      .then(setExceptions)
      .catch(e => setError("Failed to load exceptions"))
      .finally(() => setLoading(false));
  }
  useEffect(load, []);

  function handleDelete(id: string) {
    fetch(`/api/exceptions/${id}`, { method: "DELETE" })
      .then(r => {
        if (!r.ok) throw new Error("Delete failed");
        setExceptions(exceptions.filter(e => e.id !== id));
      })
      .catch(() => setError("Delete failed"));
  }

  function handleAdd(exc: any) {
    setExceptions([...exceptions, exc]);
  }

  return (
    <div className="max-w-3xl mx-auto py-10">
      <h1 className="text-2xl font-bold mb-6">Active Exceptions (Waivers)</h1>
      <button className="mb-4 px-4 py-2 bg-blue-600 text-white rounded" onClick={()=>setShowAdd(true)}>Add Exception</button>
      {error && <div className="text-red-600 mb-2">{error}</div>}
      {loading ? <div>Loading...</div> : (
        <table className="w-full border mb-4">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-2">Control ID</th>
              <th className="p-2">Selector</th>
              <th className="p-2">Reason</th>
              <th className="p-2">Expires At</th>
              <th className="p-2">Created By</th>
              <th className="p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {exceptions.map(exc => (
              <tr key={exc.id} className="border-t">
                <td className="p-2 text-xs">{exc.control_id}</td>
                <td className="p-2 text-xs"><pre className="bg-gray-100 p-1 rounded text-xs">{JSON.stringify(exc.selector)}</pre></td>
                <td className="p-2 text-xs">{exc.reason}</td>
                <td className="p-2 text-xs">{exc.expires_at}</td>
                <td className="p-2 text-xs">{exc.created_by}</td>
                <td className="p-2 text-xs">
                  <button className="text-red-600 underline" onClick={()=>handleDelete(exc.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {showAdd && <AddExceptionModal onClose={()=>setShowAdd(false)} onAdd={handleAdd} />}
    </div>
  );
}
