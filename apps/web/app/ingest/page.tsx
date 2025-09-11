'use client';
import { useState } from 'react';
import api from '../../lib/api';
import { useToast } from '../../components/toast';

export default function IngestPage() {
  const { push } = useToast();
  const [file, setFile] = useState<File | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    const fd = new FormData();
    fd.append('file', file);
    await api.post('/ingest', fd);
    push('Upload started');
  }

  return (
    <div>
      <h1 className="text-2xl mb-4">Ingest</h1>
      <form onSubmit={submit} className="space-y-2">
        <input type="file" onChange={e => setFile(e.target.files?.[0] || null)} />
        <button type="submit" className="bg-blue-600 text-white p-2 rounded">Upload</button>
      </form>
    </div>
  );
}
