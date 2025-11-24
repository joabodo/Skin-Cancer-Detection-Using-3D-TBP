import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/theme.css";

export default function ProfileSettings() {
  const [profile, setProfile] = useState({ email: "", name: "" });
  const [msg, setMsg] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    axios
      .get("/api/users/me", { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => setProfile(r.data))
      .catch(() => {});
  }, []);

  const save = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem("access_token");
      await axios.put("/api/users/me", profile, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMsg("Profile updated");
    } catch (err) {
      setMsg("Update failed");
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <div style={{ maxWidth: 700 }}>
        <h2>Profile Settings</h2>
        <form onSubmit={save}>
          <label>Email</label>
          <input
            className="form-control mb-2"
            value={profile.email}
            onChange={(e) => setProfile({ ...profile, email: e.target.value })}
          />
          <label>Full name</label>
          <input
            className="form-control mb-2"
            value={profile.name}
            onChange={(e) => setProfile({ ...profile, name: e.target.value })}
          />
          <button className="btn btn-primary">Save</button>
          {msg && <div style={{ marginTop: 12 }}>{msg}</div>}
        </form>
      </div>
    </div>
  );
}
