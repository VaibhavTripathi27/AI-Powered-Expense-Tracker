import { createContext, useContext, useEffect, useState } from 'react'
import { authService } from '../services/authService'
import { TOKEN_KEY } from '../utils/constants'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      setLoading(false)
      return
    }
    authService
      .me()
      .then(setUser)
      .catch(() => localStorage.removeItem(TOKEN_KEY))
      .finally(() => setLoading(false))
  }, [])

  const handleAuth = (data) => {
    localStorage.setItem(TOKEN_KEY, data.access_token)
    setUser(data.user)
    return data.user
  }

  const login = async (email, password) =>
    handleAuth(await authService.login({ email, password }))

  const register = async (name, email, password) =>
    handleAuth(await authService.register({ name, email, password }))

  const logout = async () => {
    try {
      await authService.logout()
    } catch {
      /* token already cleared client-side */
    }
    localStorage.removeItem(TOKEN_KEY)
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{ user, setUser, loading, login, register, logout, isAuthenticated: !!user }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
