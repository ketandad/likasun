import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE,
  withCredentials: true,
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401 && typeof window !== 'undefined') {
      window.location.href = '/login';
  }
  return Promise.reject(error);
  }
);

export default api;

export async function uploadFiles(formData: FormData): Promise<Record<string, string>> {
  const res = await api.post('/ingest/files', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data.upload_ids || {};
}

export async function parseUpload(cloud: string, uploadId: string[]): Promise<{ ingested: number }> {
  const res = await api.post('/ingest/parse', null, {
    params: { cloud, upload_id: uploadId },
  });
  return { ingested: res.data.assets || res.data.ingested || 0 };
}

export async function validatePermissions(cloud: string): Promise<Record<string, boolean>> {
  const res = await api.get('/ingest/live/permissions', { params: { cloud } });
  return res.data || {};
}

export async function startLiveIngestion(
  cloud: string,
): Promise<{ ingested: number; errors: string[] }> {
  const res = await api.post('/ingest/live', null, { params: { cloud } });
  return { ingested: res.data.ingested || 0, errors: res.data.errors || [] };
}

export async function loadDemoAssets(): Promise<{ ingested: number }> {
  const res = await api.post('/assets/load-demo');
  return { ingested: res.data.ingested || 0 };
}
