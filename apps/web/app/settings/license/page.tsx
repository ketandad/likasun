'use client';
import { useEffect, useState } from 'react';
import api from '../../../lib/api';
import { useToast } from '../../../components/toast';

export default function LicensePage() {
  const [info, setInfo] = useState<any>(null);
  const { push } = useToast();
  useEffect(() => {
    api.get('/settings/license').then((r) => setInfo(r.data));
  }, []);
  async function upload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const fd = new FormData();
    fd.append('file', file);
    await api.post('/settings/license/upload', fd);
    push('License uploaded');
  }
  return (
    <div>
      <h1 className="text-2xl mb-4">License</h1>
      {info && (
        <div className="mb-4">
          <div>Org: {info.org}</div>
          <div>Edition: {info.edition}</div>
          <div>Expiry: {info.expiry}</div>
        </div>
      )}
      <input type="file" onChange={upload} />
    </div>
  );
}
