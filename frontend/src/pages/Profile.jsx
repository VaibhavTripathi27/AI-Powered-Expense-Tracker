import { useAuth } from '../context/AuthContext.jsx'
import { useTheme } from '../context/ThemeContext.jsx'
import { formatDate } from '../utils/format'
import PageHeader from '../components/PageHeader.jsx'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import { useNavigate } from 'react-router-dom'

export default function Profile() {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div>
      <PageHeader title="Profile" subtitle="Your account details" />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Account">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-600 text-2xl font-bold text-white">
              {user?.name?.[0]?.toUpperCase()}
            </div>
            <div>
              <p className="text-lg font-semibold text-slate-800 dark:text-slate-100">
                {user?.name}
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {user?.email}
              </p>
            </div>
          </div>
          <dl className="mt-6 space-y-2 text-sm">
            <div className="flex justify-between border-t border-slate-100 pt-2 dark:border-slate-800">
              <dt className="text-slate-400">Member since</dt>
              <dd className="text-slate-700 dark:text-slate-200">
                {formatDate(user?.created_at)}
              </dd>
            </div>
            <div className="flex justify-between border-t border-slate-100 pt-2 dark:border-slate-800">
              <dt className="text-slate-400">User ID</dt>
              <dd className="text-slate-700 dark:text-slate-200">#{user?.id}</dd>
            </div>
          </dl>
        </Card>

        <Card title="Preferences">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-700 dark:text-slate-200">
                Theme
              </p>
              <p className="text-xs text-slate-400">
                Currently {theme === 'dark' ? 'Dark' : 'Light'} mode
              </p>
            </div>
            <Button variant="secondary" onClick={toggleTheme}>
              {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
            </Button>
          </div>
          <div className="mt-6 border-t border-slate-100 pt-4 dark:border-slate-800">
            <Button variant="danger" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </Card>
      </div>
    </div>
  )
}
