import axios from "axios";

// Base URL comes from VITE_API_URL (see .env.example). Cookies are sent with every request.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api",
  withCredentials: true,
});

export const getError = (err, fallback = "Something went wrong") =>
  err?.response?.data?.message || fallback;

export async function downloadReport(type) {
  const res = await api.get(`/reports/${type}`, { responseType: "blob" });
  const ext = { csv: "csv", excel: "xlsx", pdf: "pdf" }[type];
  const url = URL.createObjectURL(res.data);
  const a = document.createElement("a");
  a.href = url;
  a.download = `sentiment_report.${ext}`;
  a.click();
  URL.revokeObjectURL(url);
}

export default api;
