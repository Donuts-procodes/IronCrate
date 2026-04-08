import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import api from '../api'
import styles from './Dashboard.module.css'

export default function Dashboard() {
  const { user }              = useAuth()
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading]     = useState(true)

  useEffect(() => {
    api.get('/incidents/list')
      .then(r => setIncidents(r.data))
      .catch(() => setIncidents([]))
      .finally(() => setLoading(false))
  }, [])

  const anchored = incidents.filter(i => i.blockchain_status === 'anchored').length

  return (
    <div className={styles.page}>
      <div className={styles.header + ' fade-up'}>
        <div>
          <h1 className={styles.title}>Dashboard</h1>
          <p className={styles.sub}>
            Welcome back, <span className={styles.accent}>{user?.owner_name || user?.vehicle_number}</span>
          </p>
        </div>
        <Link to="/record" className={styles.recordBtn}>+ New Recording</Link>
      </div>

      <div className={styles.stats + ' fade-up'}>
        <StatCard label="Total Incidents" value={incidents.length} />
        <StatCard label="Chain Anchored"  value={anchored} accent />
        <StatCard label="Vehicle"         value={user?.vehicle_number || '—'} mono />
      </div>

      <div className={styles.section + ' fade-up'}>
        <div className={styles.sectionHead}>
          <span>Recent Incidents</span>
          <Link to="/incidents" className={styles.viewAll}>View all →</Link>
        </div>

        {loading && <p className={styles.muted}>Loading…</p>}
        {!loading && incidents.length === 0 && (
          <p className={styles.muted}>No incidents recorded yet. <Link to="/record" className={styles.accent}>Start a recording.</Link></p>
        )}
        {!loading && incidents.slice(0, 5).map(inc => (
          <IncidentRow key={inc.id || inc.incident_id} incident={inc} />
        ))}
      </div>
    </div>
  )
}

function StatCard({ label, value, accent, mono }) {
  return (
    <div className={styles.statCard}>
      <span className={styles.statLabel}>{label}</span>
      <span className={`${styles.statValue} ${accent ? styles.accent : ''} ${mono ? styles.mono : ''}`}>
        {value}
      </span>
    </div>
  )
}

function IncidentRow({ incident }) {
  const ts = incident.metadata?.timestamp || incident.timestamp
  const date = ts ? new Date(ts * 1000).toLocaleString() : '—'
  return (
    <div className={styles.row}>
      <div>
        <span className={styles.rowHash}>{(incident.video_hash || '').slice(0, 16)}…</span>
        <span className={styles.rowDate}>{date}</span>
      </div>
      <span className={incident.blockchain_status === 'anchored' ? styles.tagGreen : styles.tagRed}>
        {incident.blockchain_status === 'anchored' ? 'Anchored' : 'Pending'}
      </span>
    </div>
  )
}
