'use client';
import { useEffect, useState } from 'react';
import api from '../../lib/api';
import { DataTable } from '../../components/data-table';
import { StatusBadge } from '../../components/status-badge';

interface Result {
  id: string;
  control: string;
  status: 'PASS' | 'FAIL' | 'WAIVED' | 'NA';
}

export default function ResultsPage() {
  const [data, setData] = useState<Result[]>([]);
  useEffect(() => {
    api.get('/results').then(r => setData(r.data || [])).catch(() => {});
  }, []);
  return (
    <div>
      <h1 className="text-2xl mb-4">Results</h1>
      <DataTable<Result>
        data={data}
        columns={[
          { key: 'control', header: 'Control' },
          { key: 'status', header: 'Status', render: row => <StatusBadge status={row.status} /> },
        ]}
      />
    </div>
  );
}
