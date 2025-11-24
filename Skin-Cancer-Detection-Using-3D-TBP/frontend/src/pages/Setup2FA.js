import React from "react";
import "../styles/Auth.css";

export default function Setup2FA() {
  const uri = localStorage.getItem("qr_uri");

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Set up Two-Factor Authentication</h2>

        <p>Scan this QR code using Google Authenticator or Authy.</p>

        <div style={{ textAlign: "center", marginTop: 20 }}>
          <img
            src={`https://api.qrserver.com/v1/create-qr-code/?data=${encodeURIComponent(
              uri
            )}&size=200x200`}
            alt="2FA QR"
            style={{ borderRadius: "8px" }}
          />
        </div>

        <p style={{ marginTop: 20 }}>
          After scanning, click below to continue:
        </p>

        <a href="/" className="auth-btn" style={{ display: "inline-block", textDecoration: "none" }}>
          Go to Login
        </a>
      </div>
    </div>
  );
}
