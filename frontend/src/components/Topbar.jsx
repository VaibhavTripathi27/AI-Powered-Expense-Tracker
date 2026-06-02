import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { useTheme } from '../context/ThemeContext.jsx'

export default function Topbar({ onMenu }) {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-slate-200 bg-white/80 px-4 backdrop-blur dark:border-slate-800 dark:bg-slate-900/80 md:px-6">
      <button
        className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 md:hidden"
        onClick={onMenu}
        aria-label="Open menu"
      >
        ☰
      </button>
      <div className="hidden text-sm text-slate-500 dark:text-slate-400 md:block">
        Welcome back, <span className="font-semibold">{user?.name}</span>
      </div>
      <div className="ml-auto flex items-center gap-3">
        <button
          onClick={toggleTheme}
          className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-600 text-sm font-semibold text-white">
            {user?.name?.[0]?.toUpperCase() || 'U'}
          </div>
          <button
            onClick={handleLogout}
            className="btn-secondary px-3 py-1.5 text-xs"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}
