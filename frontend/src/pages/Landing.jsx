import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { useAuth } from "../hooks/useAuth";
import styles from "./Landing.module.css";

export default function Landing() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [vehicle, setVehicle] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [perms, setPerms] = useState({ camera: null, location: null });

  // Request camera + location permissions on mount so user grants them early
  useEffect(() => {
    // Camera permission probe
    navigator.mediaDevices
      ?.getUserMedia({ video: true, audio: false })
      .then((stream) => {
        stream.getTracks().forEach((t) => t.stop()); // release immediately
        setPerms((p) => ({ ...p, camera: "granted" }));
      })
      .catch(() => setPerms((p) => ({ ...p, camera: "denied" })));

    // Location permission probe
    navigator.geolocation?.getCurrentPosition(
      () => setPerms((p) => ({ ...p, location: "granted" })),
      () => setPerms((p) => ({ ...p, location: "denied" })),
      { timeout: 5000 },
    );
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(vehicle);
      navigate("/dashboard");
    } catch (err) {
      setError(
        err.response?.data?.error || "Vehicle not found. Register first.",
      );
    } finally {
      setLoading(false);
    }
  };

  const permIcon = (state) => {
    if (state === "granted")
      return <span style={{ color: "var(--green)" }}>●</span>;
    if (state === "denied")
      return <span style={{ color: "var(--red)" }}>●</span>;
    return (
      <span style={{ color: "var(--text3)", animation: "pulse 1.4s infinite" }}>
        ●
      </span>
    );
  };

  return (
    <div className={styles.page}>
      <div className={styles.grid} aria-hidden />

      <div className={styles.hero}>
        <div className={styles.badge}>VEHICULAR FORENSICS PLATFORM</div>

        {/* Fixed title — split into two lines so "IRON" and "CRATE" render separately */}
        <h1 className={styles.title}>
          <span className={styles.iron}>IRON</span>
          <span className={styles.crate}>CRATE</span>
        </h1>

        <p className={styles.sub}>
          Tamper-proof incident logging. SHA-256 hashed footage anchored on
          Polygon blockchain.
        </p>

        {/* Permission status row */}
        <div className={styles.permRow}>
          <span className={styles.permItem}>
            {permIcon(perms.camera)} Camera
          </span>
          <span className={styles.permItem}>
            {permIcon(perms.location)} Location
          </span>
          {perms.camera === "denied" && (
            <span className={styles.permWarn}>
              Allow camera access in browser settings
            </span>
          )}
        </div>

        <form className={styles.form} onSubmit={handleLogin}>
          <input
            value={vehicle}
            onChange={(e) => setVehicle(e.target.value.toUpperCase())}
            placeholder="VEHICLE REG NUMBER"
            className={styles.input}
            required
          />
          <button type="submit" className={styles.btn} disabled={loading}>
            {loading ? (
              <span
                style={{
                  display: "inline-block",
                  width: 14,
                  height: 14,
                  border: "2px solid var(--bg)",
                  borderTopColor: "transparent",
                  borderRadius: "50%",
                  animation: "spin 0.8s linear infinite",
                }}
              />
            ) : (
              "ACCESS →"
            )}
          </button>
        </form>

        {error && <p className={styles.error}>{error}</p>}

        <button
          className={styles.register}
          onClick={() => navigate("/register")}
        >
          New vehicle? Register here
        </button>
      </div>

      <div className={styles.features}>
        {[
          "Dual-Stream Recording",
          "OpenCV Object Detection",
          "Speed Estimation",
          "SHA-256 Fingerprinting",
          "Polygon Blockchain",
          "Live Cloud Streaming",
        ].map((f) => (
          <span key={f} className={styles.pill}>
            {f}
          </span>
        ))}
      </div>

      <div className={styles.footer}>
        <span className="mono muted" style={{ fontSize: 11 }}>
          MCA TECHNICAL PROJECT — 2026
        </span>
        <span className="mono muted" style={{ fontSize: 11 }}>
          POLYGON AMOY TESTNET
        </span>
      </div>
    </div>
  );
}
