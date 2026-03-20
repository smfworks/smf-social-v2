import { Outlet, Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Link2, PenTool, Calendar, FileText, Settings } from 'lucide-react'

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
    <div className="min-h-screen bg-[#f8fafc] flex">
      {/* Sidebar - SMF Works Navy */}
      <aside className="w-72 bg-[#001F3F] flex flex-col text-white">
        {/* Header with SMF Branding */}
        <div className="p-6 border-b border-[#003366]">
          <h1 className="text-2xl font-bold tracking-tight">
            <span className="text-white">SMF</span>
            <span className="text-[#00D4FF]"> Social</span>
          </h1>
          <p className="text-sm text-gray-400 mt-1">v2.0 — Standalone Platform</p>
        </div>
        
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-[#00D4FF] text-[#001F3F] shadow-lg shadow-[#00D4FF]/20'
                    : 'text-gray-300 hover:bg-[#003366] hover:text-white'
                }`}
              >
                <Icon className="w-5 h-5" />
                {item.label}
              </Link>
            )
          })}
        </nav>
        
        {/* Footer with user info */}
        <div className="p-4 border-t border-[#003366]">
          <div className="flex items-center gap-3 text-sm text-gray-300">
            <div className="w-10 h-10 bg-gradient-to-br from-[#00D4FF] to-[#001F3F] rounded-full flex items-center justify-center text-white font-bold">
              M
            </div>
            <div>
              <p className="font-medium text-white">Michael</p>
              <p className="text-xs text-gray-400">Admin</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
