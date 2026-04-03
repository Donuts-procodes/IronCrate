import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import styles from './Register.module.css'

/* Insurance removed per requirements */
const FIELDS = [
  { key: 'vehicle_number', label: 'Registration Number', placeholder: 'DL01AB1234', mono: true },
  { key: 'owner_name',     label: 'Owner Full Name',     placeholder: 'Ayush Kumar',  mono: false },
  { key: 'phone',          label: 'Phone Number',        placeholder: '+91 9876543210', mono: true },
]

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form,    setForm]    = useState({ vehicle_number: '', owner_name: '', phone: '' })
  const [error,   setError]   = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (key) => (e) => {
    const val = key === 'vehicle_number' ? e.target.value.toUpperCase() : e.target.value
    setForm(f => ({ ...f, [key]: val }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(form)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.grid} aria-hidden />

      <div className={styles.card}>
        <button className={styles.back} onClick={() => navigate('/')}>← BACK</button>

        <div className={styles.header}>
          <h2 className={styles.title}>REGISTER VEHICLE</h2>
          <p className={styles.sub}>Register your vehicle to start tamper-proof incident logging.</p>
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
          {FIELDS.map(({ key, label, placeholder, mono }) => (
            <div className={styles.field} key={key}>
              <label className={styles.label}>{label}</label>
              <input
                value={form[key]}
                onChange={handleChange(key)}
                placeholder={placeholder}
                style={mono ? { fontFamily: 'var(--mono)', letterSpacing: '0.06em' } : {}}
                required
              />
            </div>
          ))}

          {error && <p className={styles.error}>{error}</p>}

          <button type="submit" className={styles.btn} disabled={loading}>
            {loading
              ? <span style={{display:'inline-block',width:14,height:14,border:'2px solid var(--bg)',borderTopColor:'transparent',borderRadius:'50%',animation:'spin 0.8s linear infinite'}} />
              : 'REGISTER →'
            }
          </button>
        </form>
      </div>
    </div>
  )
}
