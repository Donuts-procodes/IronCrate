import { useEffect, useState } from 'react'
import api from '../api'
import styles from './Incidents.module.css'

export default function Incidents() {
  const [incidents, setIncidents] = useState([])
  const [loading,   setLoading]   = useState(true)
  const [expanded,  setExpanded]  = useState(null)

  useEffect(() => {
    api.get('/incidents/list')
      .then(r => setIncidents(r.data.reverse()))   // newest first
      .catch(() => setIncidents([]))
      .finally(() => setLoading(false))
  }, [])

  const toggle = (id) => setExpanded(e => e === id ? null : id)

  return (
    <div className={styles.page}>
      <div className={styles.header + ' fade-up'}>
        <h1 className={styles.title}>Incident Log</h1>
        <p className={styles.sub}>{incidents.length} record{incidents.length !== 1 ? 's' : ''} on file</p>
      </div>

      {loading && <p className={styles.muted}>Loading…</p>}

      {!loading && incidents.length === 0 && (
        <div className={styles.empty}>
          <p>No incidents recorded yet.</p>
        </div>
      )}

      <div className={styles.list + ' fade-up'}>
        {incidents.map((inc, i) => {
          const id   = inc.id || inc.incident_id || i
          const ts   = inc.metadata?.timestamp || inc.timestamp
          const date = ts ? new Date(ts * 1000).toLocaleString() : '—'
          const open = expanded === id

          return (
            <div key={id} className={styles.card}>
              <div className={styles.cardHead} onClick={() => toggle(id)}>
                <div>
                  <span className={styles.hash}>{(inc.video_hash || '').slice(0, 20)}…</span>
                  <span className={styles.date}>{date}</span>
                </div>
                <div className={styles.cardRight}>
                  <span className={inc.blockchain_status === 'anchored' ? styles.tagGreen : styles.tagOrange}>
                    {inc.blockchain_status === 'anchored' ? 'Anchored' : inc.blockchain_status || 'Pending'}
                  </span>
                  <span className={styles.chevron}>{open ? '▲' : '▼'}</span>
                </div>
              </div>

              {open && (
                <div className={styles.detail}>
                  <Row label="Video Hash"    value={inc.video_hash} mono />
                  <Row label="Vehicle"       value={inc.vehicle_number || inc.metadata?.vehicle_number} />
                  <Row label="Duration"      value={inc.duration ? `${inc.duration}s` : '—'} />
                  <Row label="Chunks"        value={inc.chunk_count ?? '—'} />
                  <Row label="Location"      value={
                    inc.metadata?.lat
                      ? `${inc.metadata.lat}, ${inc.metadata.lon}`
                      : inc.location_coords || '—'
                  } />
                  <Row label="Note"          value={inc.metadata?.note || '—'} />
                  {inc.video_url && (
                    <div className={styles.row}>
                      <span className={styles.rowLabel}>Video</span>
                      <a href={inc.video_url} target="_blank" rel="noreferrer" className={styles.link}>
                        Open ↗
                      </a>
                    </div>
                  )}
                  {inc.tx_hash && (
                    <div className={styles.row}>
                      <span className={styles.rowLabel}>TX Hash</span>
                      <a
                        href={`https://amoy.polygonscan.com/tx/${inc.tx_hash}`}
                        target="_blank" rel="noreferrer"
                        className={styles.link}
                      >
                        {inc.tx_hash.slice(0, 20)}… ↗
                      </a>
                    </div>
                  )}
                  {inc.ai_analysis && (
                    <>
                      <div className={styles.divider}>CV Analysis</div>
                      <Row label="Max Pedestrians" value={inc.ai_analysis.max_pedestrians_in_frame} />
                      <Row label="Max Cars"        value={inc.ai_analysis.max_cars_in_frame} />
                      <Row label="Collision Risk"  value={inc.ai_analysis.collision_risk_factor} />
                    </>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

function Row({ label, value, mono }) {
  return (
    <div className={styles.row}>
      <span className={styles.rowLabel}>{label}</span>
      <span className={`${styles.rowVal} ${mono ? styles.mono : ''}`}>{value ?? '—'}</span>
    </div>
  )
}
