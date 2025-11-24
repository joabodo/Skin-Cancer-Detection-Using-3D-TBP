import React, { useState } from "react";
import axios from "axios";
import "../styles/theme.css";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setMsg("");
    try {
      // backend: POST /auth/forgot-password  -> { ok: true }
      await axios.post("/api/auth/forgot-password", { email });
      setMsg(
        "If an account exists for that email, a reset link has been sent. Check your inbox."
      );
    } catch (err) {
      setMsg("Unable to process request. Try again later.");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Reset your password</h2>
        <p className="muted">Enter your account email and we'll send a password reset link.</p>

        <form onSubmit={submit}>
          <label>Email</label>
          <div className="input-group">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <button className="auth-btn">Send reset link</button>
        </form>

        {msg && <div style={{ marginTop: 12 }}>{msg}</div>}

        <div className="auth-footer">
          <a href="/">Back to login</a>
        </div>
      </div>
    </div>
  );
}
