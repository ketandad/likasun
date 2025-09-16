'use client';
import { useEffect, useState } from 'react';

export default function SystemPage() {
  const [health, setHealth] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);
  const [metricsEnabled, setMetricsEnabled] = useState(false);
  const [latestRun, setLatestRun] = useState<any>(null);
  const [aboutOpen, setAboutOpen] = useState(false);

  useEffect(() => {
    fetch('/api/health').then(r => r.json()).then(setHealth);
    fetch('/api/results/summary').then(r => r.json()).then(setSummary);
    fetch('/api/metrics').then(r => setMetricsEnabled(r.ok));
    // Simulate latest run info
    setLatestRun({ date: '2025-09-16', status: 'PASS' });
  }, []);

  function copyDiagnostics() {
    navigator.clipboard.writeText(JSON.stringify(summary, null, 2));
  }

  return (
    <div className="max-w-xl mx-auto py-10">
      <h1 className="text-2xl font-bold mb-6">System Health</h1>
      {health && (
        <div className="mb-4">API Version: {health.version}</div>
      )}
      {latestRun && (
        <div className="mb-4">Latest Run: {latestRun.date} ({latestRun.status})</div>
      )}
      <div className="mb-4">
        {metricsEnabled ? (
          <a href="/api/metrics" target="_blank" rel="noopener" className="underline text-blue-600">View Metrics</a>
        ) : (
          <span className="text-gray-500">Metrics not enabled</span>
        )}
      </div>
      <button className="mb-4 px-4 py-2 bg-gray-200 rounded" onClick={copyDiagnostics}>Copy Diagnostic Bundle</button>
      <button className="mb-4 px-4 py-2 bg-gray-100 rounded" onClick={()=>setAboutOpen(true)}>About</button>
      {aboutOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow max-w-md w-full relative">
            <button className="absolute top-2 right-2 text-gray-500" onClick={()=>setAboutOpen(false)}>✕</button>
            <h2 className="text-xl font-bold mb-2">About</h2>
            <div>Version: {health?.version || '-'}</div>
            <div>Commit: {health?.commit || '-'}</div>
          </div>
        </div>
      )}
    </div>
  );
}
