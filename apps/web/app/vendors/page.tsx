
import { useEffect, useState } from "react";

function AddVendorModal({ onClose, onAdd }: { onClose: () => void, onAdd: (vendor: any) => void }) {
  const [name, setName] = useState("");
  const [risk, setRisk] = useState("medium");
  const [dpaSigned, setDpaSigned] = useState(false);
  const [pii, setPii] = useState(false);
  const [error, setError] = useState("");
  function handleSubmit(e: any) {
    e.preventDefault();
    fetch("/api/vendors", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, risk, dpa_signed: dpaSigned, pii })
    })
      .then(async r => {
        if (!r.ok) throw new Error(await r.text());
        return r.json();
      })
      .then(vendor => { onAdd(vendor); onClose(); })
      .catch(err => setError(err.message));
  }
  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <form className="bg-white p-6 rounded shadow max-w-md w-full" onSubmit={handleSubmit}>
        <h2 className="text-xl font-bold mb-4">Add Vendor</h2>
        <input required value={name} onChange={e=>setName(e.target.value)} placeholder="Vendor Name" className="border rounded p-2 mb-2 w-full" />
        <select value={risk} onChange={e=>setRisk(e.target.value)} className="border rounded p-2 mb-2 w-full">
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <label className="block mb-2"><input type="checkbox" checked={dpaSigned} onChange={e=>setDpaSigned(e.target.checked)} /> DPA Signed</label>
        <label className="block mb-2"><input type="checkbox" checked={pii} onChange={e=>setPii(e.target.checked)} /> Handles PII</label>
        {error && <div className="text-red-600 mb-2 text-xs">{error}</div>}
        <div className="flex gap-2 justify-end">
          <button type="button" className="px-3 py-1 bg-gray-200 rounded" onClick={onClose}>Cancel</button>
          <button type="submit" className="px-3 py-1 bg-blue-600 text-white rounded">Add</button>
        </div>
      </form>
    </div>
  );
}

function BulkUploadModal({ onClose, onBulkAdd }: { onClose: () => void, onBulkAdd: (vendors: any[]) => void }) {
  const [json, setJson] = useState("");
  const [error, setError] = useState("");
  function handleSubmit(e: any) {
    e.preventDefault();
    let vendors;
    try { vendors = JSON.parse(json); } catch { setError("Invalid JSON"); return; }
    fetch("/api/vendors/bulk", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ vendors })
    })
      .then(async r => {
        if (!r.ok) throw new Error(await r.text());
        return r.json();
      })
      .then(vs => { onBulkAdd(vs); onClose(); })
      .catch(err => setError(err.message));
  }
  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <form className="bg-white p-6 rounded shadow max-w-md w-full" onSubmit={handleSubmit}>
        <h2 className="text-xl font-bold mb-4">Bulk Upload Vendors</h2>
        <textarea required value={json} onChange={e=>setJson(e.target.value)} placeholder='[{"name": "Vendor", "risk": "low", "dpa_signed": true, "pii": false}]' className="border rounded p-2 mb-2 w-full" rows={4} />
        {error && <div className="text-red-600 mb-2 text-xs">{error}</div>}
        <div className="flex gap-2 justify-end">
          <button type="button" className="px-3 py-1 bg-gray-200 rounded" onClick={onClose}>Cancel</button>
          <button type="submit" className="px-3 py-1 bg-blue-600 text-white rounded">Upload</button>
        </div>
      </form>
    </div>
  );
}

export default function VendorsPage() {
  const [vendors, setVendors] = useState<any[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [showBulk, setShowBulk] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  function load() {
    setLoading(true);
    fetch("/api/vendors")
      .then(r => r.json())
      .then(setVendors)
      .catch(e => setError("Failed to load vendors"))
      .finally(() => setLoading(false));
  }
  useEffect(load, []);

  function handleAdd(vendor: any) {
    setVendors([...vendors, vendor]);
  }
  function handleBulkAdd(vs: any[]) {
    setVendors([...vendors, ...vs]);
  }

  return (
    <div className="max-w-3xl mx-auto py-10">
      <h1 className="text-2xl font-bold mb-6">Vendors</h1>
      <div className="mb-4 flex gap-2">
        <button className="px-4 py-2 bg-blue-600 text-white rounded" onClick={()=>setShowAdd(true)}>Add Vendor</button>
        <button className="px-4 py-2 bg-green-600 text-white rounded" onClick={()=>setShowBulk(true)}>Bulk Upload</button>
      </div>
      {error && <div className="text-red-600 mb-2">{error}</div>}
      {loading ? <div>Loading...</div> : (
        <table className="w-full border mb-4">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-2">Name</th>
              <th className="p-2">Risk</th>
              <th className="p-2">DPA Signed</th>
              <th className="p-2">Handles PII</th>
            </tr>
          </thead>
          <tbody>
            {vendors.map(v => (
              <tr key={v.id} className="border-t">
                <td className="p-2 text-xs">{v.name || v.vendor_id || v.product}</td>
                <td className="p-2 text-xs">{v.risk}</td>
                <td className="p-2 text-xs">{v.dpa_signed ? "Yes" : "No"}</td>
                <td className="p-2 text-xs">{v.pii ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {showAdd && <AddVendorModal onClose={()=>setShowAdd(false)} onAdd={handleAdd} />}
      {showBulk && <BulkUploadModal onClose={()=>setShowBulk(false)} onBulkAdd={handleBulkAdd} />}
    </div>
  );
}
