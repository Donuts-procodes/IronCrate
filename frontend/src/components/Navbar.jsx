import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import styles from './Navbar.module.css'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  return (
    <nav className={styles.nav}>
      <span className={styles.brand}>
        IRON<span className={styles.accent}>CRATE</span>
      </span>

      <div className={styles.links}>
        <NavLink to="/dashboard" className={({ isActive }) => isActive ? styles.active : ''}>
          Dashboard
        </NavLink>
        <NavLink to="/record" className={({ isActive }) => isActive ? styles.active : ''}>
          Record
        </NavLink>
        <NavLink to="/incidents" className={({ isActive }) => isActive ? styles.active : ''}>
          Incidents
        </NavLink>
      </div>

      <div className={styles.right}>
        {user && (
          <span className={styles.vehicle}>{user.vehicle_number}</span>
        )}
        <button className={styles.logout} onClick={handleLogout}>Logout</button>
      </div>
    </nav>
  )
}
