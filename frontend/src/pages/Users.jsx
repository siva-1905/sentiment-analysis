import { useEffect, useState } from "react";
import api, { getError } from "../services/api";

const EMPTY = { name: "", email: "", password: "", role: "user" };

export default function Users({ currentUser }) {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  const load = () =>
    api.get("/admin/users").then((res) => setUsers(res.data.users)).catch((e) => setError(getError(e)));

  useEffect(() => { load(); }, []);

  const run = async (fn) => {
    setError("");
    try {
      await fn();
      await load();
    } catch (err) {
      setError(getError(err));
    }
  };

  const submit = (e) => {
    e.preventDefault();
    run(async () => {
      if (editingId) {
        const body = { name: form.name, email: form.email, role: form.role };
        if (form.password) body.password = form.password;
        await api.put(`/admin/users/${editingId}`, body);
      } else {
        await api.post("/admin/users", form);
      }
      setForm(EMPTY);
      setEditingId(null);
    });
  };

  const startEdit = (u) => {
    setEditingId(u.id);
    setForm({ name: u.name, email: u.email, password: "", role: u.role });
  };

  const toggleStatus = (u) =>
    run(() => api.patch(`/admin/users/${u.id}/status`, { status: u.status === "active" ? "disabled" : "active" }));

  const changeRole = (u, role) => run(() => api.patch(`/admin/users/${u.id}/role`, { role }));

  const remove = (u) => {
    if (window.confirm(`Delete ${u.email}? Their predictions will also be deleted.`)) {
      run(() => api.delete(`/admin/users/${u.id}`));
    }
  };

  return (
    <>
      <h2>Users</h2>
      {error && <p className="error">{error}</p>}
      <form className="card inline-form" onSubmit={submit}>
        <input placeholder="Name" value={form.name} required onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input type="email" placeholder="Email" value={form.email} required onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input type="password" placeholder={editingId ? "New password (optional)" : "Password"} value={form.password}
          required={!editingId} minLength={form.password ? 6 : undefined}
          onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
          <option value="user">user</option>
          <option value="admin">admin</option>
        </select>
        <button type="submit">{editingId ? "Save changes" : "Add user"}</button>
        {editingId && <button type="button" onClick={() => { setEditingId(null); setForm(EMPTY); }}>Cancel</button>}
      </form>
      <table>
        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.id}</td>
              <td>{u.name}</td>
              <td>{u.email}</td>
              <td>
                <select value={u.role} disabled={u.id === currentUser.id} onChange={(e) => changeRole(u, e.target.value)}>
                  <option value="user">user</option>
                  <option value="admin">admin</option>
                </select>
              </td>
              <td><span className={`tag ${u.status === "active" ? "positive" : "negative"}`}>{u.status}</span></td>
              <td className="actions">
                <button onClick={() => startEdit(u)}>Edit</button>
                <button disabled={u.id === currentUser.id} onClick={() => toggleStatus(u)}>
                  {u.status === "active" ? "Deactivate" : "Activate"}
                </button>
                <button className="danger" disabled={u.id === currentUser.id} onClick={() => remove(u)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
