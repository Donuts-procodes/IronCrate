import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import api from '../api'
import styles from './Dashboard.module.css'

export default function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [incidents, setIncidents] = useState([])
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    api.get('/incidents/')
      .then(r => setIncidents(r.data))
      .catch(() => setIncidents([]))
      .finally(() => setLoading(false))
  }, [])

  const total    = incidents.length
  const anchored = incidents.filter(i => i.blockchain_status === 'anchored').length
  const latest   = incidents[0]

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <p className={styles.greeting}>Welcome back</p>
          <h1 className={styles.name}>{user?.owner_name}</h1>
        </div>
        <div className={styles.vehicleBadge}>
          <span className={styles.vehicleLabel}>VEHICLE</span>
          <span className={styles.vehicleNum}>{user?.vehicle_number}</span>
        </div>
      </div>

      {/* Stats */}
      <div className={styles.stats}>
        <div className={styles.stat}>
          <span className={styles.statVal}>{loading ? '—' : total}</span>
          <span className={styles.statKey}>Total Incidents</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statVal} style={{color:'var(--green)'}}>{loading ? '—' : anchored}</span>
          <span className={styles.statKey}>On-Chain</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statVal} style={{color: total - anchored > 0 ? 'var(--red)' : 'var(--text2)'}}>{loading ? '—' : total - anchored}</span>
          <span className={styles.statKey}>Pending</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statVal} style={{color:'var(--accent)'}}>AMOY</span>
          <span className={styles.statKey}>Network</span>
        </div>
      </div>

      {/* CTA */}
      <div className={styles.cta}>
        <div className={styles.ctaText}>
          <h2>Start Recording</h2>
          <p>Record an incident and anchor it immutably on the blockchain.</p>
        </div>
        <button className={styles.ctaBtn} onClick={() => navigate('/record')}>
          ⏺ NEW RECORDING
        </button>
      </div>

      {/* Recent incidents */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <h3>Recent Incidents</h3>
          <button className={styles.viewAll} onClick={() => navigate('/incidents')}>View all →</button>
        </div>

        {loading && <p className={styles.empty}>Loading…</p>}
        {!loading && incidents.length === 0 && (
          <p className={styles.empty}>No incidents recorded yet.</p>
        )}

        {incidents.slice(0, 3).map((inc, i) => (
          <div key={i} className={styles.row}>
            <div className={styles.rowLeft}>
              <span className={`${styles.dot} ${inc.blockchain_status === 'anchored' ? styles.green : styles.red}`} />
              <div>
                <p className={styles.rowHash}>{inc.video_hash?.slice(0, 20)}…</p>
                <p className={styles.rowTime}>{new Date(inc.metadata?.timestamp * 1000).toLocaleString()}</p>
              </div>
            </div>
            <span className={`${styles.badge} ${inc.blockchain_status === 'anchored' ? styles.badgeGreen : styles.badgeRed}`}>
              {inc.blockchain_status === 'anchored' ? 'ANCHORED' : 'PENDING'}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
