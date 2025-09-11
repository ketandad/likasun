'use client';
import { useState, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useToast } from '../../components/toast';
import {
  uploadFiles,
  parseUpload,
  validatePermissions,
  startLiveIngestion,
  loadDemoAssets,
} from '../../lib/api';

const ALLOWED = ['.csv', '.json', '.zip', '.tar.gz'];

function detectCloud(name: string): string {
  if (/^aws_.*\.(csv|json)$/i.test(name)) return 'aws';
  if (/^azure_.*\.json$/i.test(name)) return 'azure';
  if (/^gcp_.*\.json$/i.test(name)) return 'gcp';
  if (/^terraform_.*\.(json|tfstate)$/i.test(name)) return 'iac';
  return 'aws';
}

export default function IngestPage() {
  const router = useRouter();
  const { push } = useToast();
  const [files, setFiles] = useState<File[]>([]);
  const [summary, setSummary] = useState<{ files: number; assets: number } | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);

  const [tab, setTab] = useState<'aws' | 'azure' | 'gcp'>('aws');
  const [perm, setPerm] = useState<Record<string, boolean> | null>(null);
  const [ingest, setIngest] = useState<{ ingested: number; errors: string[] } | null>(null);
  const [validating, setValidating] = useState(false);
  const [starting, setStarting] = useState(false);

  function handleFiles(list: FileList | null) {
    if (!list) return;
    const arr = Array.from(list).filter(f => ALLOWED.some(ext => f.name.endsWith(ext)));
    setFiles(prev => [...prev, ...arr]);
  }

  async function uploadAndParse() {
    if (!files.length) return;
    setUploading(true);
    try {
      const form = new FormData();
      files.forEach(f => form.append('files', f));
      const uploads = await uploadFiles(form);
      const groups: Record<string, string[]> = {};
      files.forEach(f => {
        const cloud = detectCloud(f.name);
        const uid = uploads[f.name];
        if (!uid) return;
        groups[cloud] = groups[cloud] || [];
        groups[cloud].push(uid);
      });
      let total = 0;
      for (const [cloud, ids] of Object.entries(groups)) {
        const res = await parseUpload(cloud, ids);
        total += res.ingested;
      }
      push(`Ingested ${total} assets`);
      setSummary({ files: files.length, assets: total });
      setFiles([]);
    } catch (e) {
      push('Upload failed');
    } finally {
      setUploading(false);
    }
  }

  async function onValidate() {
    setValidating(true);
    try {
      const res = await validatePermissions(tab);
      setPerm(res);
    } finally {
      setValidating(false);
    }
  }

  async function onStart() {
    setStarting(true);
    try {
      const res = await startLiveIngestion(tab);
      setIngest(res);
      push(`Ingested ${res.ingested} assets`);
    } finally {
      setStarting(false);
    }
  }

  async function onLoadDemo() {
    const res = await loadDemoAssets();
    push(`Demo assets loaded (${res.ingested})`);
    router.push('/results?env=demo');
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl">Ingest</h1>
        <button
          onClick={onLoadDemo}
          className="bg-green-600 text-white px-3 py-2 rounded"
        >
          Load Demo Assets
        </button>
      </div>
      <div className="grid md:grid-cols-2 gap-8">
        <section>
          <h2 className="text-xl mb-2">Offline Exports</h2>
          <div
            onDragOver={e => e.preventDefault()}
            onDrop={e => {
              e.preventDefault();
              handleFiles(e.dataTransfer.files);
            }}
            className="border-2 border-dashed p-6 text-center rounded cursor-pointer"
            role="button"
            tabIndex={0}
            aria-label="Upload files"
            onKeyDown={e => {
              if (e.key === 'Enter') fileInput.current?.click();
            }}
            onClick={() => fileInput.current?.click()}
          >
            <input
              ref={fileInput}
              type="file"
              multiple
              accept={ALLOWED.join(',')}
              className="hidden"
              onChange={e => handleFiles(e.target.files)}
            />
            <p>Drag files here or click to select</p>
          </div>
          <ul className="mt-2 space-y-1">
            {files.map((f, i) => (
              <li key={i} className="flex justify-between text-sm">
                <span>{f.name}</span>
                <button
                  onClick={() => setFiles(files.filter((_, idx) => idx !== i))}
                  className="text-red-600"
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
          <button
            disabled={!files.length || uploading}
            onClick={uploadAndParse}
            className="mt-2 bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            {uploading ? 'Uploading...' : 'Upload & Parse'}
          </button>
          {summary && (
            <div className="mt-2" aria-live="polite">
              {summary.files} files uploaded • {summary.assets} assets normalized –{' '}
              <Link
                href="/results?sort_by=evaluated_at&sort_dir=desc"
                className="underline"
              >
                View assets
              </Link>
            </div>
          )}
        </section>
        <section>
          <h2 className="text-xl mb-2">Live Ingestion</h2>
          <div className="mb-2 flex space-x-2">
            {['aws', 'azure', 'gcp'].map(c => (
              <button
                key={c}
                onClick={() => setTab(c as 'aws' | 'azure' | 'gcp')}
                className={`px-3 py-1 border rounded ${
                  tab === c ? 'bg-gray-200' : ''
                }`}
              >
                {c.toUpperCase()}
              </button>
            ))}
          </div>
          <p className="text-sm mb-2">
            Need creds? See{' '}
            <a href="/INGEST.md" className="underline">
              docs
            </a>
          </p>
          <div className="space-x-2">
            <button
              disabled={validating || starting}
              onClick={onValidate}
              className="bg-blue-600 text-white px-3 py-2 rounded disabled:opacity-50"
            >
              {validating ? 'Validating...' : 'Validate Permissions'}
            </button>
            <button
              disabled={starting || validating}
              onClick={onStart}
              className="bg-green-600 text-white px-3 py-2 rounded disabled:opacity-50"
            >
              {starting ? 'Starting...' : 'Start Live Ingestion'}
            </button>
          </div>
          {perm && (
            <div className="mt-2">
              {Object.entries(perm).map(([k, v]) => (
                <div key={k} className={v ? 'text-green-700' : 'text-red-600'}>
                  {k}: {v ? 'ok' : 'missing'}
                </div>
              ))}
            </div>
          )}
          {ingest && (
            <div className="mt-2" aria-live="polite">
              Ingested {ingest.ingested} assets
              {ingest.errors.length ? `, errors: ${ingest.errors.join(', ')}` : ''}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

