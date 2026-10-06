import { useState } from "react";
import api, { getError } from "../services/api";

export default function Predict() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const analyze = async () => {
    setError("");
    setResult(null);
    setBusy(true);
    try {
      const res = await api.post("/sentiment/predict", { text });
      setResult(res.data);
    } catch (err) {
      setError(getError(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card form">
      <h2>Analyze a Review</h2>
      <textarea rows={6} placeholder="Type or paste a review..." value={text}
        onChange={(e) => setText(e.target.value)} />
      <button onClick={analyze} disabled={busy || !text.trim()}>{busy ? "Analyzing..." : "Analyze"}</button>
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="result">
          <p>Sentiment: <span className={`tag ${result.sentiment.toLowerCase()}`}>{result.sentiment}</span></p>
          <p>Confidence: <strong>{result.confidence}%</strong></p>
        </div>
      )}
    </div>
  );
}
