import { useState } from "react";
import api, { getError } from "../services/api";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const upload = async () => {
    setError("");
    setData(null);
    const form = new FormData();
    form.append("file", file);
    setBusy(true);
    try {
      const res = await api.post("/sentiment/upload", form);
      setData(res.data);
    } catch (err) {
      setError(getError(err, "Upload failed"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <div className="card form">
        <h2>Upload CSV / Excel</h2>
        <p>The file needs a column named <code>review</code> or <code>text</code> (max 1000 rows, 5 MB).</p>
        <input type="file" accept=".csv,.xlsx,.xls" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={upload} disabled={!file || busy}>{busy ? "Analyzing..." : "Upload & Analyze"}</button>
        {error && <p className="error">{error}</p>}
      </div>
      {data && (
        <>
          <h3>
            {data.count} reviews analysed: {data.summary.Positive} positive, {data.summary.Negative} negative,{" "}
            {data.summary.Neutral} neutral
          </h3>
          <table>
            <thead><tr><th>Review</th><th>Sentiment</th><th>Confidence</th></tr></thead>
            <tbody>
              {data.results.slice(0, 100).map((r, i) => (
                <tr key={i}>
                  <td className="wrap">{r.text.length > 150 ? r.text.slice(0, 150) + "..." : r.text}</td>
                  <td><span className={`tag ${r.sentiment.toLowerCase()}`}>{r.sentiment}</span></td>
                  <td>{r.confidence}%</td>
                </tr>
              ))}
            </tbody>
          </table>
          {data.results.length > 100 && <p>Showing the first 100 rows. All rows are saved in your history.</p>}
        </>
      )}
    </>
  );
}
