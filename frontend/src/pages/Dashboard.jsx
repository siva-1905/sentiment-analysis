import { useEffect, useState } from "react";
import api, { getError } from "../services/api";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/dashboard").then((res) => setStats(res.data)).catch((e) => setError(getError(e)));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!stats) return <p>Loading...</p>;

  const pct = (n) => (stats.total ? Math.round((n / stats.total) * 100) : 0);
  const cards = [
    ["Total Predictions", stats.total, "total"],
    ["Positive", stats.positive, "positive"],
    ["Negative", stats.negative, "negative"],
    ["Neutral", stats.neutral, "neutral"],
  ];

  return (
    <>
      <h2>Dashboard {stats.scope === "system" && <small>(system-wide)</small>}</h2>
      <div className="cards">
        {cards.map(([label, value, cls]) => (
          <div key={label} className={`card stat ${cls}`}>
            <h3>{value}</h3>
            <p>{label}</p>
          </div>
        ))}
      </div>
      <div className="card">
        {["positive", "negative", "neutral"].map((k) => (
          <div key={k} className="bar-row">
            <span className="bar-label">{k}</span>
            <div className="bar-track"><div className={`bar-fill ${k}`} style={{ width: `${pct(stats[k])}%` }} /></div>
            <span>{pct(stats[k])}%</span>
          </div>
        ))}
      </div>
    </>
  );
}
