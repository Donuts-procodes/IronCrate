import { useEffect, useState } from 'react'
import api from '../api'
import styles from './Incidents.module.css'

export default function Incidents() {
  const [incidents, setIncidents] = useState([])
  const [loading,   setLoading]   = useState(true)
  const [expanded,  setExpanded]  = useState(null)

  useEffect(() => {
    api.get('/incidents/')
      .then(r => setIncidents(r.data))
      .catch(() => setIncidents([]))
      .finally(() => setLoading(false))
  }, [])

  const toggle = (i) => setExpanded(expanded === i ? null : i)

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>INCIDENT LOG</h1>
        <span className={`${styles.count} mono`}>{incidents.length} RECORDS</span>
      </div>

      {loading && <p className={styles.empty}>Loading…</p>}
      {!loading && incidents.length === 0 && (
        <p className={styles.empty}>No incidents recorded yet.</p>
      )}

      <div className={styles.list}>
        {incidents.map((inc, i) => (
          <div key={i} className={styles.card} onClick={() => toggle(i)}>

            {/* Row summary */}
            <div className={styles.row}>
              <div className={styles.rowLeft}>
                <span className={`${styles.dot} ${inc.blockchain_status === 'anchored' ? styles.green : styles.orange}`} />
                <div>
                  <p className={`${styles.hash} mono`}>{inc.video_hash?.slice(0, 32)}…</p>
                  <p className={`${styles.time} mono`}>
                    {inc.metadata?.timestamp
                      ? new Date(inc.metadata.timestamp * 1000).toLocaleString()
                      : '—'}
                    {inc.metadata?.note && <span className={styles.noteSnip}> — {inc.metadata.note}</span>}
                  </p>
                </div>
              </div>
              <div className={styles.rowRight}>
                <span className={`${styles.badge} ${inc.blockchain_status === 'anchored' ? styles.badgeGreen : styles.badgeOrange}`}>
                  {inc.blockchain_status === 'anchored' ? 'ON-CHAIN' : 'PENDING'}
                </span>
                <span className={styles.chevron}>{expanded === i ? '▲' : '▼'}</span>
              </div>
            </div>

            {/* Expanded detail */}
            {expanded === i && (
              <div className={styles.detail} onClick={e => e.stopPropagation()}>
                <div className={styles.grid}>
                  <Field label="Full SHA-256" value={inc.video_hash} mono />
                  <Field label="TX Hash" value={inc.tx_hash || '—'} mono
                    link={inc.tx_hash ? `https://amoy.polygonscan.com/tx/${inc.tx_hash}` : null} />
                  <Field label="Vehicle" value={inc.metadata?.vehicle_number || '—'} />
                  <Field label="GPS" value={inc.metadata?.lat ? `${inc.metadata.lat}, ${inc.metadata.lon}` : 'N/A'} mono />
                  <Field label="Speed" value={inc.metadata?.speed_kmh ? `${inc.metadata.speed_kmh} km/h` : 'N/A'} />
                  <Field label="Note" value={inc.metadata?.note || '—'} />
                </div>
                {inc.video_url && (
                  <a href={inc.video_url} target="_blank" rel="noreferrer" className={styles.videoLink}>
                    View Video on Firebase ↗
                  </a>
                )}
                <div className={styles.integrityNote}>
                  <span className={styles.integrityIcon}>🔒</span>
                  <span>Hash is anchored immutably on Polygon Amoy. Any modification to the video will produce a different SHA-256 hash, proving tampering.</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function Field({ label, value, mono, link }) {
  return (
    <div className={styles.field}>
      <span className={styles.fieldLabel}>{label}</span>
      {link
        ? <a href={link} target="_blank" rel="noreferrer" className={`${styles.fieldVal} ${mono ? 'mono' : ''}`} style={{color:'var(--accent)'}}>
            {value}
          </a>
        : <span className={`${styles.fieldVal} ${mono ? 'mono' : ''}`}>{value}</span>
      }
    </div>
  )
}
