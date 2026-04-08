import { useRef, useState, useEffect } from 'react'
import api from '../api'
import styles from './Record.module.css'

const CHUNK_INTERVAL_MS = 5000   // send a chunk every 5 s
const SESSION_ID = () => `sess_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`

export default function Record() {
  const videoRef    = useRef(null)
  const recorderRef = useRef(null)
  const sessionRef  = useRef(null)
  const chunkIdxRef = useRef(0)
  const intervalRef = useRef(null)

  const [status,    setStatus]    = useState('idle')   // idle | requesting | recording | uploading | done | error
  const [error,     setError]     = useState('')
  const [note,      setNote]      = useState('')
  const [coords,    setCoords]    = useState({ lat: '', lon: '' })
  const [result,    setResult]    = useState(null)
  const [chunksSent, setChunksSent] = useState(0)
  const startTimeRef = useRef(null)

  // Grab GPS once
  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      pos => setCoords({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
      () => {}
    )
  }, [])

  const startRecording = async () => {
    setError('')
    setStatus('requesting')
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      videoRef.current.srcObject = stream

      const recorder = new MediaRecorder(stream, { mimeType: 'video/webm;codecs=vp8' })
      recorderRef.current = recorder
      sessionRef.current  = SESSION_ID()
      chunkIdxRef.current = 0
      startTimeRef.current = Date.now()
      setChunksSent(0)
      setStatus('recording')

      recorder.ondataavailable = async (e) => {
        if (!e.data || e.data.size === 0) return
        const idx = chunkIdxRef.current++
        setChunksSent(idx + 1)

        const form = new FormData()
        form.append('chunk',       e.data, `chunk_${idx}.webm`)
        form.append('session_id',  sessionRef.current)
        form.append('label',       'front')
        form.append('chunk_index', idx)
        form.append('lat',         coords.lat)
        form.append('lon',         coords.lon)

        try {
          await api.post('/session/chunk', form, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
        } catch (err) {
          console.warn('Chunk upload failed:', err)
        }
      }

      // Request a data chunk every CHUNK_INTERVAL_MS
      intervalRef.current = setInterval(() => {
        if (recorder.state === 'recording') recorder.requestData()
      }, CHUNK_INTERVAL_MS)

      recorder.start()
    } catch (err) {
      setError('Camera access denied or not available.')
      setStatus('error')
    }
  }

  const stopRecording = async () => {
    clearInterval(intervalRef.current)
    const recorder = recorderRef.current
    if (!recorder || recorder.state === 'inactive') return

    setStatus('uploading')

    await new Promise(resolve => {
      recorder.onstop = resolve
      recorder.requestData()   // flush last chunk
      recorder.stop()
    })

    // Stop all tracks
    videoRef.current?.srcObject?.getTracks().forEach(t => t.stop())
    videoRef.current.srcObject = null

    const duration = Math.round((Date.now() - startTimeRef.current) / 1000)

    try {
      const r = await api.post('/session/finalize', {
        session_id: sessionRef.current,
        note,
        lat: coords.lat,
        lon: coords.lon,
        duration,
      })
      setResult(r.data)
      setStatus('done')
    } catch (err) {
      setError(err.response?.data?.error || 'Finalization failed.')
      setStatus('error')
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.header + ' fade-up'}>
        <h1 className={styles.title}>New Recording</h1>
        <p className={styles.sub}>Live video is chunked, hashed, and anchored on Polygon.</p>
      </div>

      <div className={styles.grid + ' fade-up'}>
        {/* Camera preview */}
        <div className={styles.cameraBox}>
          <video ref={videoRef} autoPlay muted playsInline className={styles.video} />
          {status === 'idle' && (
            <div className={styles.overlay}>
              <span className={styles.overlayCam}>📷</span>
              <span>Camera preview</span>
            </div>
          )}
          {status === 'recording' && (
            <div className={styles.recBadge}>
              <span className={`${styles.dot} pulse`} />
              REC · {chunksSent} chunk{chunksSent !== 1 ? 's' : ''} uploaded
            </div>
          )}
        </div>

        {/* Controls */}
        <div className={styles.controls}>
          <div className={styles.field}>
            <label className={styles.label}>Note (optional)</label>
            <textarea
              className={styles.textarea}
              value={note}
              onChange={e => setNote(e.target.value)}
              placeholder="Brief description of incident…"
              rows={3}
              disabled={status === 'recording' || status === 'uploading'}
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>GPS</label>
            <p className={styles.gps}>
              {coords.lat ? `${coords.lat}, ${coords.lon}` : 'Acquiring location…'}
            </p>
          </div>

          {error && <p className={styles.error}>{error}</p>}

          {(status === 'idle' || status === 'error') && (
            <button className={styles.btnStart} onClick={startRecording}>
              ▶ Start Recording
            </button>
          )}
          {status === 'requesting' && (
            <button className={styles.btnStart} disabled>Requesting camera…</button>
          )}
          {status === 'recording' && (
            <button className={styles.btnStop} onClick={stopRecording}>
              ■ Stop &amp; Upload
            </button>
          )}
          {status === 'uploading' && (
            <button className={styles.btnStart} disabled>Finalising…</button>
          )}
          {status === 'done' && result && (
            <div className={styles.result}>
              <p className={styles.resultOk}>✓ Incident secured</p>
              <div className={styles.resultRow}>
                <span className={styles.resultLabel}>Hash</span>
                <span className={styles.resultVal}>{result.video_hash?.slice(0,24)}…</span>
              </div>
              <div className={styles.resultRow}>
                <span className={styles.resultLabel}>Chain</span>
                <span className={result.blockchain_status === 'anchored' ? styles.green : styles.red}>
                  {result.blockchain_status}
                </span>
              </div>
              {result.tx_hash && (
                <div className={styles.resultRow}>
                  <span className={styles.resultLabel}>TX</span>
                  <a
                    href={`https://amoy.polygonscan.com/tx/${result.tx_hash}`}
                    target="_blank" rel="noreferrer"
                    className={styles.txLink}
                  >
                    {result.tx_hash.slice(0, 18)}…
                  </a>
                </div>
              )}
              <button className={styles.btnStart} style={{marginTop:12}}
                onClick={() => { setStatus('idle'); setResult(null); setNote(''); setChunksSent(0) }}>
                + New Recording
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
