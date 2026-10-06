import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api, { getError } from "../services/api";

export default function Login({ onLogin }) {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await api.post("/auth/login", form);
      onLogin(res.data.user);
      navigate("/dashboard");
    } catch (err) {
      setError(getError(err, "Login failed"));
    }
  };

  return (
    <form className="card form" onSubmit={submit}>
      <h2>Login</h2>
      {error && <p className="error">{error}</p>}
      <input type="email" placeholder="Email" value={form.email} required
        onChange={(e) => setForm({ ...form, email: e.target.value })} />
      <input type="password" placeholder="Password" value={form.password} required
        onChange={(e) => setForm({ ...form, password: e.target.value })} />
      <button type="submit">Login</button>
      <p>No account? <Link to="/register">Register</Link></p>
    </form>
  );
}
