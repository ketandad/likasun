'use client';
import { useState } from 'react';

const frameworks = [
  'PCI',
  'GDPR',
  'DPDP',
  'ISO',
  'NIST',
  'HIPAA',
  'FedRAMP L',
  'FedRAMP M',
  'FedRAMP H',
  'SOC2',
  'CIS',
  'CCPA',
];

export default function CompliancePage() {
  const [fw, setFw] = useState(frameworks[0]);
  return (
    <div>
      <h1 className="text-2xl mb-4">Compliance</h1>
      <select
        value={fw}
        onChange={(e) => setFw(e.target.value)}
        className="mb-4 p-2 bg-gray-800 text-white"
      >
        {frameworks.map((f) => (
          <option key={f} value={f}>
            {f}
          </option>
        ))}
      </select>
      <div className="mb-4">Coverage matrix for {fw}</div>
      <div className="flex gap-2">
        <button
          className="bg-blue-600 text-white p-2 rounded"
          onClick={() => (window.location.href = `/compliance/evidence-pack?fw=${fw}`)}
        >
          Evidence Pack
        </button>
        <button
          className="bg-blue-600 text-white p-2 rounded"
          onClick={() => (window.location.href = `/compliance/export.csv?fw=${fw}`)}
        >
          Export CSV
        </button>
      </div>
    </div>
  );
}
