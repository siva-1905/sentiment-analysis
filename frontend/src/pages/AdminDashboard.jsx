import { useEffect, useState } from "react";
import api, { getError } from "../services/api";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.get("/dashboard"), api.get("/admin/audit-logs")])
      .then(([s, l]) => { setStats(s.data); setLogs(l.data.logs); })
      .catch((e) => setError(getError(e)));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!stats) return <p>Loading...</p>;

  return (
    <>
      <h2>Admin Dashboard</h2>
      <div className="cards">
        <div className="card stat total"><h3>{stats.users}</h3><p>Users</p></div>
        <div className="card stat total"><h3>{stats.total}</h3><p>Total Predictions</p></div>
        <div className="card stat positive"><h3>{stats.positive}</h3><p>Positive</p></div>
        <div className="card stat negative"><h3>{stats.negative}</h3><p>Negative</p></div>
        <div className="card stat neutral"><h3>{stats.neutral}</h3><p>Neutral</p></div>
      </div>
      <h3>Audit Logs (latest 200)</h3>
      <table>
        <thead><tr><th>Time</th><th>User</th><th>Action</th><th>Description</th></tr></thead>
        <tbody>
          {logs.map((l) => (
            <tr key={l.id}>
              <td>{new Date(l.timestamp).toLocaleString()}</td>
              <td>{l.user_email || "-"}</td>
              <td>{l.action}</td>
              <td className="wrap">{l.description}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
