import { useEffect, useState } from "react";

const CLOUDS = ["aws", "azure", "gcp", "iac"];

function AssetDrawer({ assetId, onClose }: { assetId: string, onClose: () => void }) {
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    if (!assetId) return;
    fetch(`/api/assets/${assetId}`)
      .then(r => r.json())
      .then(setData);
  }, [assetId]);
  if (!assetId) return null;
  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded shadow max-w-lg w-full relative">
        <button className="absolute top-2 right-2 text-gray-500" onClick={onClose}>✕</button>
        <h2 className="text-xl font-bold mb-2">Asset Details</h2>
        {!data ? <div>Loading...</div> : (
          <>
            <pre className="bg-gray-100 p-2 rounded text-xs mb-2">{JSON.stringify(data.asset, null, 2)}</pre>
            <div className="mb-2 font-semibold">Evidence:</div>
            <pre className="bg-gray-100 p-2 rounded text-xs mb-2">{JSON.stringify(data.asset.evidence, null, 2)}</pre>
            <div className="mb-2 font-semibold">Linked Results:</div>
            <ul className="mb-2">
              {data.results.map((r: any) => (
                <li key={r.control_id} className="mb-1">
                  <span className="font-bold">{r.control_title}</span> [{r.status}] <span className="text-xs">{r.frameworks.join(", ")}</span>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </div>
  );
}

export default function AssetsPage() {
  const [assets, setAssets] = useState<any[]>([]);
  const [cloud, setCloud] = useState<string>("");
  const [type, setType] = useState<string>("");
  const [tag, setTag] = useState<string>("");
  const [page, setPage] = useState(1);
  const [drawerId, setDrawerId] = useState<string>("");

  useEffect(() => {
    const params = new URLSearchParams();
    if (cloud) params.set("cloud", cloud);
    if (type) params.set("type", type);
    if (tag) params.set("tag", tag);
    params.set("page", String(page));
    params.set("page_size", "20");
    fetch(`/api/assets?${params.toString()}`)
      .then(r => r.json())
      .then(setAssets);
  }, [cloud, type, tag, page]);

  return (
    <div className="max-w-4xl mx-auto py-10">
      <h1 className="text-3xl font-bold mb-8">Assets</h1>
      <div className="mb-4 flex gap-4">
        <select value={cloud} onChange={e=>setCloud(e.target.value)} className="border rounded p-1">
          <option value="">All Clouds</option>
          {CLOUDS.map(c => <option key={c} value={c}>{c.toUpperCase()}</option>)}
        </select>
        <input value={type} onChange={e=>setType(e.target.value)} placeholder="Type" className="border rounded p-1" />
        <input value={tag} onChange={e=>setTag(e.target.value)} placeholder="Tag" className="border rounded p-1" />
      </div>
      <table className="w-full border mb-4">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-2">Asset ID</th>
            <th className="p-2">Cloud</th>
            <th className="p-2">Type</th>
            <th className="p-2">Region</th>
            <th className="p-2">Tags</th>
            <th className="p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {assets.map((a: any) => (
            <tr key={a.asset_id} className="border-t">
              <td className="p-2 text-xs">{a.asset_id}</td>
              <td className="p-2 text-xs">{a.cloud}</td>
              <td className="p-2 text-xs">{a.type}</td>
              <td className="p-2 text-xs">{a.region}</td>
              <td className="p-2 text-xs">{JSON.stringify(a.tags)}</td>
              <td className="p-2">
                <button className="text-blue-600 underline" onClick={()=>setDrawerId(a.asset_id)}>Details</button>
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
      {drawerId && <AssetDrawer assetId={drawerId} onClose={()=>setDrawerId("")} />}
    </div>
  );
}
