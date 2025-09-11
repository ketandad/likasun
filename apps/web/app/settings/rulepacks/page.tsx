'use client';
import { useEffect, useState } from 'react';
import api from '../../../lib/api';
import { useToast } from '../../../components/toast';

export default function RulepacksPage() {
  const [info, setInfo] = useState<any>(null);
  const { push } = useToast();
  useEffect(() => {
    api.get('/settings/rulepacks').then(r => setInfo(r.data));
  }, []);
  async function upload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const fd = new FormData();
    fd.append('file', file);
    await api.post('/settings/rulepacks/upload', fd);
    push('Uploaded');
  }
  async function rollback(version: string) {
    await api.post('/settings/rulepacks/rollback', { version });
    push('Rolled back');
  }
  return (
    <div>
      <h1 className="text-2xl mb-4">Rule Packs</h1>
      {info && (
        <div className="mb-4">
          <div>Version: {info.version}</div>
          <div>Date: {info.date}</div>
        </div>
      )}
      <input type="file" onChange={upload} className="mb-4" />
      {info && info.history && (
        <select onChange={e => rollback(e.target.value)} defaultValue="">
          <option value="" disabled>Rollback...</option>
          {info.history.map((v: string) => (
            <option key={v} value={v}>{v}</option>
          ))}
        </select>
      )}
    </div>
  );
}
