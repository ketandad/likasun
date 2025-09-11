import { useEffect, useState } from "react";

interface Exception {
  id: string;
  control_id: string;
  selector: Record<string, any>;
  reason: string;
  expires_at: string;
  created_by: string;
}

export default function ExceptionsPage() {
  const [items, setItems] = useState<Exception[]>([]);
  const [form, setForm] = useState({
    control_id: "",
    selector: "{}",
    reason: "",
    expires_at: "",
  });

  async function load() {
    const res = await fetch("/api/exceptions");
    if (res.ok) setItems(await res.json());
  }

  useEffect(() => {
    load();
  }, []);

  async function add() {
    const body = {
      control_id: form.control_id,
      selector: JSON.parse(form.selector || "{}"),
      reason: form.reason,
      expires_at: form.expires_at,
    };
    await fetch("/api/exceptions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    setForm({ control_id: "", selector: "{}", reason: "", expires_at: "" });
    load();
  }

  async function del(id: string) {
    await fetch(`/api/exceptions/${id}`, { method: "DELETE" });
    load();
  }

  return (
    <div>
      <h1>Exceptions</h1>
      <table>
        <thead>
          <tr>
            <th>Control</th>
            <th>Selector</th>
            <th>Reason</th>
            <th>Expires</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((e) => (
            <tr key={e.id}>
              <td>{e.control_id}</td>
              <td>{JSON.stringify(e.selector)}</td>
              <td>{e.reason}</td>
              <td>{e.expires_at}</td>
              <td>
                <button onClick={() => del(e.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <h2>Add Exception</h2>
      <input
        placeholder="control_id"
        value={form.control_id}
        onChange={(e) => setForm({ ...form, control_id: e.target.value })}
      />
      <input
        placeholder="selector JSON"
        value={form.selector}
        onChange={(e) => setForm({ ...form, selector: e.target.value })}
      />
      <input
        placeholder="reason"
        value={form.reason}
        onChange={(e) => setForm({ ...form, reason: e.target.value })}
      />
      <input
        placeholder="expires_at"
        value={form.expires_at}
        onChange={(e) => setForm({ ...form, expires_at: e.target.value })}
      />
      <button onClick={add}>Add</button>
    </div>
  );
}
