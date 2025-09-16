import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

function SkeletonCard() {
  return (
    <div className="bg-gray-200 animate-pulse h-24 rounded mb-4" />
  );
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<any>(null);
  const [latestRun, setLatestRun] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const router = useRouter();

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const [summaryRes, runRes] = await Promise.all([
          fetch("/api/results/summary").then(r => r.json()),
          fetch("/api/evaluate/runs/latest").then(r => r.json()),
        ]);
        setSummary(summaryRes);
        setLatestRun(runRes);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  async function handleRunEvaluation() {
    setRunning(true);
    const res = await fetch("/api/evaluate/run", { method: "POST" });
    if (res.ok) {
      router.push("/results");
    } else {
      alert("Evaluation is already running or failed.");
    }
    setRunning(false);
  }

  return (
    <div className="max-w-4xl mx-auto py-10">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : (
          <>
            <div className="bg-white rounded shadow p-4">
              <div className="text-gray-500">Assets</div>
              <div className="text-2xl font-bold">{latestRun?.assets_count ?? 0}</div>
            </div>
            <div className="bg-white rounded shadow p-4">
              <div className="text-gray-500">Fails</div>
              <div className="text-2xl font-bold">{summary?.by_status?.FAIL ?? 0}</div>
            </div>
            <div className="bg-white rounded shadow p-4">
              <div className="text-gray-500">Waived</div>
              <div className="text-2xl font-bold">{summary?.by_status?.WAIVED ?? 0}</div>
            </div>
            <div className="bg-white rounded shadow p-4">
              <div className="text-gray-500">Last Run</div>
              <div className="text-lg">{latestRun?.finished_at ? new Date(latestRun.finished_at).toLocaleString() : "Never"}</div>
            </div>
          </>
        )}
      </div>
      <button
        className="bg-blue-600 text-white px-6 py-2 rounded shadow hover:bg-blue-700 disabled:opacity-50"
        onClick={handleRunEvaluation}
        disabled={running}
      >
        {running ? "Running..." : "Run Evaluation"}
      </button>
    </div>
  );
}
