import { useRef, useState, useEffect, useCallback } from "react";
import api from "../api";
import styles from "./Record.module.css";

const STATES = {
  idle: "idle",
  requesting: "requesting",
  recording: "recording",
  stopping: "stopping",
  done: "done",
  error: "error",
};
const CHUNK_INTERVAL_MS = 5000;
const FRONT_CONSTRAINTS = {
  video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
  audio: false,
};
const REAR_CONSTRAINTS = {
  video: {
    facingMode: "environment",
    width: { ideal: 1280 },
    height: { ideal: 720 },
  },
  audio: false,
};

export default function Record() {
  const frontVideoRef = useRef(null);
  const rearVideoRef = useRef(null);
  const frontStream = useRef(null);
  const rearStream = useRef(null);
  const frontRecorder = useRef(null);
  const rearRecorder = useRef(null);
  const sessionIdRef = useRef(null);
  const chunkIndexRef = useRef(0);
  const timerRef = useRef(null);
  
  // 1. UPDATED: Added speed to the ref
  const locationRef = useRef({ lat: "", lon: "", speed: "0" });

  const [state, setState] = useState(STATES.idle);
  const [duration, setDuration] = useState(0);
  const [note, setNote] = useState("");
  
  // 2. UPDATED: Added speed to the state
  const [location, setLocation] = useState({ lat: "", lon: "", speed: "0" });
  const [detection, setDetection] = useState(null);
  const [uploadCount, setUploadCount] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [camReady, setCamReady] = useState({ front: false, rear: false });

  // Keep locationRef in sync for use inside callbacks
  useEffect(() => {
    locationRef.current = location;
  }, [location]);

  // Watch GPS on mount
  useEffect(() => {
    const id = navigator.geolocation?.watchPosition(
      (pos) => {
        // 3. UPDATED: Calculate km/h from meters per second
        const currentSpeed = pos.coords.speed ? (pos.coords.speed * 3.6).toFixed(1) : "0";
        
        setLocation({
          lat: pos.coords.latitude.toFixed(6),
          lon: pos.coords.longitude.toFixed(6),
          speed: currentSpeed,
        });
      },
      () => {},
      { enableHighAccuracy: true },
    );
    return () => {
      if (id) navigator.geolocation.clearWatch(id);
      stopAllStreams();
    };
  }, []);

  const stopAllStreams = () => {
    clearInterval(timerRef.current);
    frontStream.current?.getTracks().forEach((t) => t.stop());
    rearStream.current?.getTracks().forEach((t) => t.stop());
  };

  const requestCameras = async () => {
    setState(STATES.requesting);
    setError("");
    setCamReady({ front: false, rear: false });

    let front = null,
      rear = null;

    // Rear camera
    try {
      rear = await navigator.mediaDevices.getUserMedia(REAR_CONSTRAINTS);
    } catch {
      try {
        rear = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });
      } catch {}
    }

    // Front camera — needs a separate getUserMedia call with different constraints
    try {
      front = await navigator.mediaDevices.getUserMedia(FRONT_CONSTRAINTS);
    } catch {
      // On desktop only one camera exists — reuse the rear stream object reference
      front = rear;
    }

    if (!rear && !front) {
      setError(
        "No camera found. Allow camera permission in your browser and try again.",
      );
      setState(STATES.error);
      return;
    }

    frontStream.current = front;
    rearStream.current = rear;

    if (frontVideoRef.current && front) frontVideoRef.current.srcObject = front;
    if (rearVideoRef.current && rear) rearVideoRef.current.srcObject = rear;

    setCamReady({ front: !!front, rear: !!rear });
    setState(STATES.idle);
  };

  const uploadChunk = useCallback(async (blob, label) => {
    const idx = chunkIndexRef.current++;
    const loc = locationRef.current;
    const form = new FormData();
    form.append("chunk", blob, `chunk_${idx}.webm`);
    form.append("session_id", sessionIdRef.current);
    form.append("label", label);
    form.append("chunk_index", idx);
    form.append("lat", loc.lat);
    form.append("lon", loc.lon);
    
    // 4. UPDATED: Send speed with every chunk upload
    form.append("speed", loc.speed);

    try {
      const res = await api.post("/session/chunk", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setUploadCount((c) => c + 1);
      if (label === "rear" && res.data.detections) {
        setDetection(res.data.detections);
      }
    } catch (e) {
      console.warn("Chunk upload failed", e);
    }
  }, []);

  const startRecording = () => {
    sessionIdRef.current = `sess_${Date.now()}`;
    chunkIndexRef.current = 0;
    setUploadCount(0);
    setDetection(null);
    setResult(null);
    setError("");

    const makeRecorder = (stream, label) => {
      if (!stream) return null;
      const mime =
        [
          "video/webm;codecs=vp9",
          "video/webm;codecs=vp8",
          "video/webm",
          "video/mp4",
        ].find((t) => MediaRecorder.isTypeSupported(t)) || "";
      const mr = new MediaRecorder(stream, {
        mimeType: mime,
        videoBitsPerSecond: 1_500_000,
      });
      mr.ondataavailable = (e) => {
        if (e.data?.size > 0) uploadChunk(e.data, label);
      };
      mr.start(CHUNK_INTERVAL_MS);
      return mr;
    };

    frontRecorder.current = makeRecorder(frontStream.current, "front");
    rearRecorder.current = makeRecorder(rearStream.current, "rear");

    setState(STATES.recording);
    setDuration(0);
    timerRef.current = setInterval(() => setDuration((d) => d + 1), 1000);
  };

  const stopRecording = async () => {
    setState(STATES.stopping);
    clearInterval(timerRef.current);

    frontRecorder.current?.stop();
    rearRecorder.current?.stop();

    await new Promise((r) => setTimeout(r, 700));

    try {
      const res = await api.post("/session/finalize", {
        session_id: sessionIdRef.current,
        note,
        lat: locationRef.current.lat,
        lon: locationRef.current.lon,
        
        // 5. UPDATED: Send speed when finalizing the session
        speed: locationRef.current.speed, 
        duration,
      });
      setResult(res.data);
      setState(STATES.done);
    } catch (err) {
      setError(err.response?.data?.error || "Finalization failed");
      setState(STATES.error);
    }
  };

  const reset = () => {
    stopAllStreams();
    frontStream.current = rearStream.current = null;
    if (frontVideoRef.current) frontVideoRef.current.srcObject = null;
    if (rearVideoRef.current) rearVideoRef.current.srcObject = null;
    setState(STATES.idle);
    setCamReady({ front: false, rear: false });
    setResult(null);
    setError("");
    setDuration(0);
    setDetection(null);
    setUploadCount(0);
  };

  const fmt = (s) =>
    `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
  const isRec = state === STATES.recording;

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>RECORD INCIDENT</h1>
          <p className={styles.sub}>
            Dual-stream · Live cloud upload · OpenCV detection on rear camera
          </p>
        </div>
        {isRec && (
          <div className={styles.liveBadge}>
            <span className={`${styles.liveDot} pulse`} />
            LIVE &nbsp;·&nbsp; {fmt(duration)} &nbsp;·&nbsp; {uploadCount}{" "}
            chunks uploaded
          </div>
        )}
      </div>

      {/* Camera grid */}
      <div className={styles.cameraGrid}>
        {/* Front */}
        <div className={styles.cameraCard}>
          <div className={styles.camLabel}>
            FRONT CAMERA — DRIVER
            {camReady.front && <span className={styles.camOk}>●</span>}
          </div>
          <div className={styles.videoWrap}>
            <video
              ref={frontVideoRef}
              autoPlay
              muted
              playsInline
              className={styles.video}
              style={{ transform: "scaleX(-1)" }}
            />
            {!camReady.front && (
              <div className={styles.placeholder}>
                <span className={styles.placeholderIcon}>📷</span>
                <span>Front camera</span>
              </div>
            )}
          </div>
        </div>

        {/* Rear */}
        <div className={styles.cameraCard}>
          <div className={styles.camLabel}>
            REAR CAMERA — ROAD
            {camReady.rear && <span className={styles.camOk}>●</span>}
          </div>
          <div className={styles.videoWrap}>
            <video
              ref={rearVideoRef}
              autoPlay
              muted
              playsInline
              className={styles.video}
            />
            {!camReady.rear && (
              <div className={styles.placeholder}>
                <span className={styles.placeholderIcon}>🎥</span>
                <span>Rear camera</span>
              </div>
            )}

            {/* Detection overlay — shown when recording */}
            {isRec && (
              <div className={styles.detOverlay}>
                {detection ? (
                  <>
                    {detection.cars > 0 && (
                      <span className={styles.detTag}>
                        🚗 {detection.cars} car{detection.cars !== 1 ? "s" : ""}
                      </span>
                    )}
                    {detection.pedestrians > 0 && (
                      <span className={styles.detTag}>
                        🚶 {detection.pedestrians} ped
                      </span>
                    )}
                    {detection.speed_kmh != null && (
                      <span className={`${styles.detTag} ${styles.speedTag}`}>
                        {detection.speed_kmh} km/h
                      </span>
                    )}
                    {detection.cars === 0 && detection.pedestrians === 0 && (
                      <span className={styles.detTag} style={{ opacity: 0.6 }}>
                        No objects
                      </span>
                    )}
                  </>
                ) : (
                  <span className={styles.detTag} style={{ opacity: 0.5 }}>
                    Analyzing…
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Controls row */}
      <div className={styles.controlRow}>
        <div className={styles.btnGroup}>
          {state === STATES.idle && !camReady.front && !camReady.rear && (
            <button className={styles.primaryBtn} onClick={requestCameras}>
              📷 ENABLE CAMERAS
            </button>
          )}
          {state === STATES.requesting && (
            <button className={styles.primaryBtn} disabled>
              <Spin /> Requesting…
            </button>
          )}
          {state === STATES.idle && (camReady.front || camReady.rear) && (
            <button className={styles.primaryBtn} onClick={startRecording}>
              ⏺ START RECORDING
            </button>
          )}
          {state === STATES.recording && (
            <button
              className={`${styles.primaryBtn} ${styles.stopBtn}`}
              onClick={stopRecording}
            >
              ⏹ STOP & FINALIZE
            </button>
          )}
          {state === STATES.stopping && (
            <button className={styles.primaryBtn} disabled>
              <Spin /> Finalizing…
            </button>
          )}
          {(state === STATES.done || state === STATES.error) && (
            <button className={styles.primaryBtn} onClick={reset}>
              ↺ NEW RECORDING
            </button>
          )}
        </div>

        <div className={styles.gps}>
          <span className={styles.gpsLabel}>GPS</span>
          <span
            className="mono"
            style={{
              fontSize: 12,
              color: location.lat ? "var(--green)" : "var(--text3)",
            }}
          >
            {/* 6. UPDATED: Display speed alongside the coordinates */}
            {location.lat
              ? `${location.lat}, ${location.lon} | ${location.speed} km/h`
              : "Acquiring location…"}
          </span>
        </div>
      </div>

      {/* Note + result */}
      <div className={styles.sideRow}>
        <div className={styles.noteBox}>
          <label className={styles.boxLabel}>INCIDENT NOTE</label>
          <textarea
            className={styles.textarea}
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Brief description of the incident…"
            rows={3}
            disabled={isRec}
          />
        </div>

        <div className={styles.infoBox}>
          {error && <p className={styles.error}>{error}</p>}

          {!error && !result && (
            <div className={styles.howItWorks}>
              <p className={styles.boxLabel}>HOW IT WORKS</p>
              <p className={styles.hint}>
                Each camera records in 5-second chunks uploaded live to
                Firebase. The rear stream is analyzed frame-by-frame by OpenCV
                for cars, pedestrians, and speed. On stop, all chunks are
                merged, SHA-256 hashed, and the fingerprint is anchored on
                Polygon.
              </p>
            </div>
          )}

          {result && (
            <div className={styles.resultBox}>
              <p className={styles.boxLabel}>INCIDENT ANCHORED</p>
              <ResultRow
                k="SHA-256"
                v={result.video_hash?.slice(0, 26) + "…"}
                mono
              />
              <ResultRow
                k="TX Hash"
                v={result.tx_hash ? result.tx_hash.slice(0, 22) + "…" : "—"}
                link={
                  result.tx_hash
                    ? `https://amoy.polygonscan.com/tx/${result.tx_hash}`
                    : null
                }
                mono
              />
              <ResultRow k="Chunks uploaded" v={`${result.chunk_count}`} />
              <ResultRow k="Duration" v={`${result.duration}s`} />
              <ResultRow
                k="Status"
                v={result.blockchain_status?.toUpperCase()}
                color={
                  result.blockchain_status === "anchored"
                    ? "var(--green)"
                    : "var(--red)"
                }
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ResultRow({ k, v, mono, link, color }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 3,
        marginBottom: 10,
      }}
    >
      <span
        style={{
          fontFamily: "var(--mono)",
          fontSize: 9,
          letterSpacing: "0.14em",
          color: "var(--text3)",
          textTransform: "uppercase",
        }}
      >
        {k}
      </span>
      {link ? (
        <a
          href={link}
          target="_blank"
          rel="noreferrer"
          style={{
            fontSize: 12,
            fontFamily: mono ? "var(--mono)" : "var(--sans)",
            color: "var(--accent)",
            wordBreak: "break-all",
          }}
        >
          {v}
        </a>
      ) : (
        <span
          style={{
            fontSize: 12,
            fontFamily: mono ? "var(--mono)" : "var(--sans)",
            color: color || "var(--text)",
            wordBreak: "break-all",
          }}
        >
          {v}
        </span>
      )}
    </div>
  );
}

function Spin() {
  return (
    <span
      style={{
        display: "inline-block",
        width: 12,
        height: 12,
        border: "2px solid currentColor",
        borderTopColor: "transparent",
        borderRadius: "50%",
        animation: "spin 0.8s linear infinite",
        marginRight: 6,
        verticalAlign: "middle",
      }}
    />
  );
}