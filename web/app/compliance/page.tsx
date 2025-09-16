import { useEffect, useState } from "react";

const FRAMEWORKS = [
  "PCI_DSS",
  "GDPR",
  "DPDP",
  "ISO27001",
  "NIST_800_53",
  "HIPAA",
  "FEDRAMP_LOW",
  "FEDRAMP_MODERATE",
  "FEDRAMP_HIGH",
  "SOC2",
  "CIS",
  "CCPA",
];

export default function CompliancePage() {
  const [framework, setFramework] = useState("PCI_DSS");
  const [matrix, setMatrix] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/compliance/summary?framework=${framework}`)
      .then(r => r.json())
      .then(data => {
        setMatrix(data);
        setLoading(false);
      });
  }, [framework]);

  function handleRequirementClick(reqId: string) {
    window.location.href = `/results?framework=${framework}&status=FAIL&requirement=${reqId}`;
  }

  function exportPDF() {
    window.open(`/api/compliance/evidence-pack?framework=${framework}`);
  }

  return (
    <div className="max-w-5xl mx-auto py-10">
      <h1 className="text-3xl font-bold mb-8">Compliance Summary</h1>
      <div className="mb-4 flex gap-4 items-center">
        <select value={framework} onChange={e=>setFramework(e.target.value)} className="border rounded p-1">
          {FRAMEWORKS.map(f => <option key={f} value={f}>{f.replace(/_/g, " ")}</option>)}
        </select>
        <button className="bg-green-600 text-white px-4 py-2 rounded shadow hover:bg-green-700" onClick={exportPDF}>Export Evidence Pack (PDF)</button>
      </div>
      {loading ? <div>Loading...</div> : matrix && (
        <div>
          <div className="mb-4 font-semibold">Score: {matrix.score}</div>
          <table className="w-full border mb-4">
            <thead>
              <tr className="bg-gray-100">
                <th className="p-2">Requirement</th>
                <th className="p-2">Title</th>
                <th className="p-2">Status</th>
                <th className="p-2">Controls</th>
              </tr>
            </thead>
            <tbody>
              {matrix.requirements?.map((r: any) => (
                <tr key={r.id} className="border-t cursor-pointer" onClick={()=>handleRequirementClick(r.id)}>
                  <td className="p-2 text-xs">{r.id}</td>
                  <td className="p-2 text-xs">{r.title}</td>
                  <td className={`p-2 text-xs ${r.status === "PASS" ? "bg-green-100 text-green-800" : r.status === "FAIL" ? "bg-red-100 text-red-800" : r.status === "WAIVED" ? "bg-yellow-100 text-yellow-800" : "bg-gray-100 text-gray-800"}`}>{r.status}</td>
                  <td className="p-2 text-xs">{r.mapped_controls?.join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
