import React, { useState } from "react";
import { verify2fa } from "../api";
import { useNavigate } from "react-router-dom";
import "../styles/Auth.css";

export default function TwoFA() {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const token = localStorage.getItem("twofa_token");
      const res = await verify2fa(token, code);

      localStorage.setItem("access_token", res.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError("Invalid authentication code");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Two-Factor Authentication</h2>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={submit}>
          <label>Enter 6-digit code</label>
          <div className="input-group">
            <input
              type="text"
              placeholder="123456"
              value={code}
              maxLength={6}
              onChange={(e) => setCode(e.target.value)}
              required
            />
          </div>

          <button className="auth-btn">Verify</button>
        </form>
      </div>
    </div>
  );
}
