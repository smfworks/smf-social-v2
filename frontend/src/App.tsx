import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { Integrations } from './pages/Integrations'
import { Composer } from './pages/Composer'
import { Calendar } from './pages/Calendar'
import { Posts } from './pages/Posts'
import { Settings } from './pages/Settings'
import { OAuthCallback } from './pages/OAuthCallback'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="integrations" element={<Integrations />} />
        <Route path="composer" element={<Composer />} />
        <Route path="calendar" element={<Calendar />} />
        <Route path="posts" element={<Posts />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="/auth/:platform/callback" element={<OAuthCallback />} />
    </Routes>
  )
}

export default App
