import { Navigate } from "react-router-dom";

// UX only. The Flask API enforces authentication on its own.
export default function ProtectedRoute({ user, children }) {
  return user ? children : <Navigate to="/login" replace />;
}
