import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import styles from './Auth.module.css'

export default function Register() {
  const { register } = useAuth()
  const navigate     = useNavigate()
  const [form, setForm]   = useState({ vehicle_number: '', owner_name: '', phone: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register({ ...form, vehicle_number: form.vehicle_number.trim().toUpperCase() })
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed.')
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
        <p className={styles.sub}>Register your vehicle</p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <label className={styles.label}>Vehicle Number</label>
          <input value={form.vehicle_number} onChange={set('vehicle_number')} placeholder="DL01AB1234" required />

          <label className={styles.label}>Owner Name</label>
          <input value={form.owner_name} onChange={set('owner_name')} placeholder="Full name" required />

          <label className={styles.label}>Phone</label>
          <input value={form.phone} onChange={set('phone')} placeholder="+91 98765 43210" type="tel" />

          {error && <p className={styles.error}>{error}</p>}

          <button className={styles.btn} disabled={loading}>
            {loading ? <span className="spin" style={{display:'inline-block',width:14,height:14,border:'2px solid #0a0a0a',borderTopColor:'transparent',borderRadius:'50%'}} /> : 'Register →'}
          </button>
        </form>

        <p className={styles.footer}>
          Already registered? <Link to="/" className={styles.link}>Login</Link>
        </p>
      </div>
    </div>
  )
}
