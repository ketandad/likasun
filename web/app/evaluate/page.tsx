import { useState } from "react";

export default function EvaluatePage() {
  const [runId, setRunId] = useState<string>("");
  const [status, setStatus] = useState<string>("");
  const [progress, setProgress] = useState<number>(0);
  const [toast, setToast] = useState<string>("");

  async function handleEvaluate() {
    setToast("");
    setStatus("Running");
    setProgress(10);
    const res = await fetch("/api/evaluate/run", { method: "POST" });
    const data = await res.json();
    if (res.ok && data.run_id) {
      setRunId(data.run_id);
      pollStatus(data.run_id);
    } else {
      setStatus("Failed");
      setToast("Evaluation failed.");
    }
  }

  async function pollStatus(id: string) {
    let tries = 0;
    while (tries < 30) {
      const res = await fetch(`/api/evaluate/runs/${id}`);
      const data = await res.json();
      if (data.status === "completed" || data.status === "failed") {
        setStatus(data.status);
        setProgress(100);
        setToast(`Evaluation ${data.status}`);
        break;
      }
      setProgress(30 + tries * 2);
      await new Promise(r => setTimeout(r, 2000));
      tries++;
    }
  }

  return (
    <div className="max-w-xl mx-auto py-10">
      <h1 className="text-3xl font-bold mb-8">Evaluate Now</h1>
      <button
        className="bg-blue-600 text-white px-6 py-2 rounded shadow hover:bg-blue-700 disabled:opacity-50"
        onClick={handleEvaluate}
        disabled={status === "Running"}
      >
        {status === "Running" ? "Running..." : "Evaluate Now"}
      </button>
      {status && <div className="mt-4">Status: {status}</div>}
      {progress > 0 && <progress value={progress} max={100} className="w-full mt-2" />}
      {toast && (
        <div className="fixed bottom-6 right-6 bg-black text-white px-4 py-2 rounded shadow">
          {toast}
        </div>
      )}
    </div>
  );
}
