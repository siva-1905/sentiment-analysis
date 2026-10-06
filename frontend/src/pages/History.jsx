import { useEffect, useState } from "react";
import api, { getError } from "../services/api";

export default function History() {
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");

  const load = () =>
    api.get("/sentiment/history").then((res) => setRows(res.data.history)).catch((e) => setError(getError(e)));

  useEffect(() => { load(); }, []);

  const remove = async (id) => {
    if (!window.confirm("Delete this prediction?")) return;
    try {
      await api.delete(`/sentiment/history/${id}`);
      setRows(rows.filter((r) => r.id !== id));
    } catch (err) {
      setError(getError(err));
    }
  };

  return (
    <>
      <h2>History</h2>
      {error && <p className="error">{error}</p>}
      {rows.length === 0 ? <p>No predictions yet.</p> : (
        <table>
          <thead><tr><th>Review</th><th>Sentiment</th><th>Confidence</th><th>Date</th><th>Delete</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td className="wrap">{r.text.length > 150 ? r.text.slice(0, 150) + "..." : r.text}</td>
                <td><span className={`tag ${r.sentiment.toLowerCase()}`}>{r.sentiment}</span></td>
                <td>{r.confidence}%</td>
                <td>{new Date(r.date).toLocaleString()}</td>
                <td><button className="danger" onClick={() => remove(r.id)}>Delete</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
