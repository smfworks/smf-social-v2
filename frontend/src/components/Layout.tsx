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
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">SMF Social</h1>
          <p className="text-sm text-gray-500">v2.0</p>
        </div>
        
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-5 h-5" />
                {item.label}
              </Link>
            )
          })}
        </nav>
        
        <div className="p-4 border-t border-gray-200">
          <button className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-xs font-medium">
              A
            </div>
            <span>Admin</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
