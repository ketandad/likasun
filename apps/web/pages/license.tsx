import { useEffect, useState } from "react";

interface LicenseInfo {
  org: string;
  edition: string;
  expiry: string;
  seats: number;
  features: string[];
  valid: boolean;
}

export default function LicensePage() {
  const [info, setInfo] = useState<LicenseInfo | null>(null);
  const [file, setFile] = useState<File | null>(null);

  async function load() {
    const res = await fetch("/api/settings/license");
    if (res.ok) setInfo(await res.json());
  }

  useEffect(() => {
    load();
  }, []);

  async function upload() {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    await fetch("/api/settings/license/upload", { method: "POST", body: form });
    setFile(null);
    load();
  }

  const daysLeft = info
    ? Math.ceil((new Date(info.expiry).getTime() - Date.now()) / (1000 * 3600 * 24))
    : 0;

  return (
    <div>
      <h1>License</h1>
      {info && (
        <ul>
          <li>Org: {info.org}</li>
          <li>Edition: {info.edition}</li>
          <li>
            Expiry: <span style={{ color: daysLeft < 30 ? "red" : "inherit" }}>{info.expiry}</span>
          </li>
          <li>Seats: {info.seats}</li>
          <li>Features: {info.features.join(", ")}</li>
        </ul>
      )}
      <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <button onClick={upload}>Upload</button>
    </div>
  );
}
