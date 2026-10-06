import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import api from "./services/api";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Predict from "./pages/Predict";
import History from "./pages/History";
import Upload from "./pages/Upload";
import Reports from "./pages/Reports";
import AdminDashboard from "./pages/AdminDashboard";
import Users from "./pages/Users";

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On first load, ask the backend if the session cookie is still valid
  useEffect(() => {
    api
      .get("/auth/me")
      .then((res) => setUser(res.data.user))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const logout = async () => {
    try {
      await api.post("/auth/logout");
    } catch (e) {
      /* ignore: we clear the local state anyway */
    }
    setUser(null);
  };

  if (loading) return <p className="center">Loading...</p>;

  const guard = (el) => <ProtectedRoute user={user}>{el}</ProtectedRoute>;
  const adminGuard = (el) => <AdminRoute user={user}>{el}</AdminRoute>;

  return (
    <>
      <Navbar user={user} onLogout={logout} />
      <main className="container">
        <Routes>
          <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} replace />} />
          <Route path="/login" element={user ? <Navigate to="/dashboard" replace /> : <Login onLogin={setUser} />} />
          <Route path="/register" element={user ? <Navigate to="/dashboard" replace /> : <Register />} />
          <Route path="/dashboard" element={guard(<Dashboard />)} />
          <Route path="/predict" element={guard(<Predict />)} />
          <Route path="/history" element={guard(<History />)} />
          <Route path="/upload" element={guard(<Upload />)} />
          <Route path="/reports" element={guard(<Reports />)} />
          <Route path="/admin" element={adminGuard(<AdminDashboard />)} />
          <Route path="/users" element={adminGuard(<Users currentUser={user} />)} />
          <Route path="*" element={<p>Page not found</p>} />
        </Routes>
      </main>
    </>
  );
}
