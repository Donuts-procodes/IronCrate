import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import styles from './Auth.module.css'

export default function Landing() {
  const { login } = useAuth()
  const navigate  = useNavigate()
  const [vehicle, setVehicle] = useState('')
  const [error,   setError]   = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(vehicle.trim().toUpperCase())
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card + ' fade-up'}>
        <div className={styles.logo}>
          IRON<span className={styles.accent}>CRATE</span>
        </div>
        <p className={styles.sub}>Tamper-proof vehicular incident logging</p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <label className={styles.label}>Vehicle Number</label>
          <input
            value={vehicle}
            onChange={e => setVehicle(e.target.value)}
            placeholder="e.g. DL01AB1234"
            required
            autoFocus
          />
          {error && <p className={styles.error}>{error}</p>}
          <button className={styles.btn} disabled={loading}>
            {loading ? <span className="spin" style={{display:'inline-block',width:14,height:14,border:'2px solid #0a0a0a',borderTopColor:'transparent',borderRadius:'50%'}} /> : 'Login →'}
          </button>
        </form>

        <p className={styles.footer}>
          New vehicle? <Link to="/register" className={styles.link}>Register here</Link>
        </p>
      </div>
    </div>
  )
}
