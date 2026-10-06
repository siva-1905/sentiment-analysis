import { Navigate } from "react-router-dom";

// UX only. The Flask API returns 403 for non-admins on its own.
export default function AdminRoute({ user, children }) {
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== "admin") return <Navigate to="/dashboard" replace />;
  return children;
}
