import React, { useEffect, useState } from "react";
import axios from "axios";
import "../styles/theme.css";
import { useSearchParams, useNavigate } from "react-router-dom";

export default function EmailVerification() {
  const [status, setStatus] = useState("Verifying...");
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get("token");
    if (!token) {
      setStatus("Invalid verification link.");
      return;
    }
    axios
      .post("/api/auth/verify-email", { token })
      .then(() => {
        setStatus("Email verified — redirecting to login...");
        setTimeout(() => navigate("/"), 2000);
      })
      .catch(() => {
        setStatus("Verification failed or link expired.");
      });
  }, [searchParams, navigate]);

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Email verification</h2>
        <p className="muted">{status}</p>
        <div className="auth-footer">
          <a href="/">Go to Login</a>
        </div>
      </div>
    </div>
  );
}
