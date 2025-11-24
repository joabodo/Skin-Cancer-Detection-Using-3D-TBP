import React, { useState } from "react";
import { register } from "../api";
import { useNavigate } from "react-router-dom";
import "../styles/Auth.css";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");

    if (password !== confirm) {
      setError("Passwords do not match");
      return;
    }

    try {
      const res = await register(email, password);

      // Store the QR code URL that backend returns
      localStorage.setItem("qr_uri", res.totp_uri);

      // Redirect user to QR code page
      navigate("/setup-2fa");
    } catch (err) {
      setError("Registration failed. Email might already be in use.");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Create Account</h2>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={submit}>
          <label>Email</label>
          <div className="input-group">
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <label>Password</label>
          <div className="input-group">
            <input
              type="password"
              placeholder="Create password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <label>Confirm Password</label>
          <div className="input-group">
            <input
              type="password"
              placeholder="Repeat password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
            />
          </div>

          <button className="auth-btn">Register</button>
        </form>

        <div className="auth-footer">
          Already have an account? <a href="/">Login</a>
        </div>
      </div>
    </div>
  );
}
