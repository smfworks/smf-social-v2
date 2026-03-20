import { Outlet, Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Link2, PenTool, Calendar, FileText, Settings, Flame } from 'lucide-react'

export function Layout() {
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/integrations', label: 'Integrations', icon: Link2 },
    { path: '/composer', label: 'Composer', icon: PenTool },
    { path: '/calendar', label: 'Calendar', icon: Calendar },
    { path: '/posts', label: 'Posts', icon: FileText },
    { path: '/settings', label: 'Settings', icon: Settings },
  ]

  return (
    <div className="min-h-screen flex" style={{ background: '#0a1628' }}>
      {/* Sidebar - SMF Works Dark Theme */}
      <aside className="w-72 flex flex-col" style={{ 
        background: 'linear-gradient(180deg, #0a1628 0%, #1a2a3a 100%)',
        borderRight: '1px solid #2d3748'
      }}>
        {/* Header with SMF Branding */}
        <div className="p-6" style={{ borderBottom: '1px solid #2d3748' }}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg flex items-center justify-center animate-pulse-glow" 
                 style={{ 
                   background: 'linear-gradient(135deg, #00d4ff 0%, #0099cc 100%)',
                 }}>
              <Flame className="w-6 h-6" style={{ color: '#0a1628' }} />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">
                <span style={{ color: '#e8eaed' }}>SMF</span>
                <span style={{ color: '#00d4ff' }}>Social</span>
              </h1>
              <p className="text-xs mt-1" style={{ color: '#9ca3af' }}>v2.0 — Forged with AI</p>
            </div>
          </div>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-300"
                style={{
                  background: isActive 
                    ? 'linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 212, 255, 0.05) 100%)'
                    : 'transparent',
                  color: isActive ? '#00d4ff' : '#9ca3af',
                  border: isActive ? '1px solid rgba(0, 212, 255, 0.3)' : '1px solid transparent',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.color = '#e8eaed'
                    e.currentTarget.style.background = 'rgba(26, 42, 58, 0.8)'
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.color = '#9ca3af'
                    e.currentTarget.style.background = 'transparent'
                  }
                }}
              >
                <Icon className="w-5 h-5" />
                {item.label}
              </Link>
            )
          })}
        </nav>
        
        {/* Footer with forge quote */}
        <div className="p-4" style={{ borderTop: '1px solid #2d3748' }}>
          <div className="flex items-center gap-3 text-sm" style={{ color: '#9ca3af' }}>
            <div className="w-10 h-10 rounded-full flex items-center justify-center font-bold"
                 style={{ 
                   background: 'linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%)',
                   color: '#0a1628'
                 }}>
              M
            </div>
            <div>
              <p className="font-medium" style={{ color: '#e8eaed' }}>Michael</p>
              <p className="text-xs">Founder</p>
            </div>
          </div>
          <p className="text-xs mt-3 italic" style={{ color: '#9ca3af' }}>
            "Make it hot by striking"
          </p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto" style={{ background: '#0a1628' }}>
        <div className="max-w-7xl mx-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}