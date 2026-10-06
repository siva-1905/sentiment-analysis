import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api, { getError } from "../services/api";

export default function Register() {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/auth/register", form);
      navigate("/login");
    } catch (err) {
      setError(getError(err, "Registration failed"));
    }
  };

  return (
    <form className="card form" onSubmit={submit}>
      <h2>Register</h2>
      {error && <p className="error">{error}</p>}
      <input placeholder="Name" value={form.name} required
        onChange={(e) => setForm({ ...form, name: e.target.value })} />
      <input type="email" placeholder="Email" value={form.email} required
        onChange={(e) => setForm({ ...form, email: e.target.value })} />
      <input type="password" placeholder="Password (min 6 characters)" value={form.password} required minLength={6}
        onChange={(e) => setForm({ ...form, password: e.target.value })} />
      <button type="submit">Create account</button>
      <p>Already registered? <Link to="/login">Login</Link></p>
    </form>
  );
}
