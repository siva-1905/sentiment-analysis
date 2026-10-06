import { Link, useNavigate } from "react-router-dom";

export default function Navbar({ user, onLogout }) {
  const navigate = useNavigate();

  const handleLogout = async () => {
    await onLogout();
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <span className="brand">Sentiment Analysis</span>
      <div className="links">
        {!user && (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
        {user && (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/predict">Predict</Link>
            <Link to="/history">History</Link>
            <Link to="/upload">Upload</Link>
            <Link to="/reports">Reports</Link>
            {user.role === "admin" && (
              <>
                <Link to="/admin">Admin</Link>
                <Link to="/users">Users</Link>
              </>
            )}
            <span className="who">{user.name}</span>
            <button onClick={handleLogout}>Logout</button>
          </>
        )}
      </div>
    </nav>
  );
}
