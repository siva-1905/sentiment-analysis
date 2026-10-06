import { useState } from "react";
import { downloadReport } from "../services/api";

export default function Reports() {
  const [error, setError] = useState("");

  const download = async (type) => {
    setError("");
    try {
      await downloadReport(type);
    } catch (err) {
      setError("Could not download the report");
    }
  };

  return (
    <div className="card form">
      <h2>Reports</h2>
      <p>Download all of your predictions.</p>
      <button onClick={() => download("csv")}>Download CSV</button>
      <button onClick={() => download("excel")}>Download Excel</button>
      <button onClick={() => download("pdf")}>Download PDF</button>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
