import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './hooks/useAuth'
import Landing    from './pages/Landing'
import Register   from './pages/Register'
import Dashboard  from './pages/Dashboard'
import Record     from './pages/Record'
import Incidents  from './pages/Incidents'
import Navbar     from './components/Navbar'

function Protected({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div style={{display:'flex',alignItems:'center',justifyContent:'center',height:'100vh',color:'var(--text2)'}}>Loading…</div>
  return user ? children : <Navigate to="/" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/"         element={<Landing />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Protected><Navbar /><Dashboard /></Protected>} />
        <Route path="/record"    element={<Protected><Navbar /><Record /></Protected>} />
        <Route path="/incidents" element={<Protected><Navbar /><Incidents /></Protected>} />
      </Routes>
    </AuthProvider>
  )
}
