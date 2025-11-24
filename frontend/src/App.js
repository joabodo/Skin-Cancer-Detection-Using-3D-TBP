import React from "react";
import { Routes, Route, Link, useLocation } from "react-router-dom";
import Login from "./pages/Login";
import TwoFA from "./pages/TwoFA";
import Register from "./pages/Register";
import Setup2FA from "./pages/Setup2FA";
import Dashboard from "./pages/Dashboard";
import Patient from "./pages/Patient";
import Admin from "./pages/Admin";
import ForgotPassword from "./pages/ForgotPassword";
import EmailVerification from "./pages/EmailVerification";
import ProfileSettings from "./pages/ProfileSettings";


export default function App() {
  const location = useLocation();

  // Pages where NAVBAR should NOT appear
 const hideNavbarOn = ["/", "/2fa", "/register", "/setup-2fa"];

  const hideNavbar = hideNavbarOn.includes(location.pathname);

  return (
    <div>
      {!hideNavbar && (
        <nav style={{ padding: 20 }}>
          <Link to="/" className="me-3">Home</Link>
          <Link to="/dashboard" className="me-3">Dashboard</Link>
          <Link to="/admin">Admin</Link>
        </nav>
      )}

      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/2fa" element={<TwoFA />} />
        <Route path="/register" element={<Register />} />
        <Route path="/setup-2fa" element={<Setup2FA />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/patient/:id" element={<Patient />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/forgot" element={<ForgotPassword />} />
        <Route path="/verify" element={<EmailVerification />} />
        <Route path="/profile" element={<ProfileSettings />} />
      </Routes>
    </div>
  );
}
