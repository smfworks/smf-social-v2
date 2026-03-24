import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Calendar, CheckCircle, AlertCircle, TrendingUp, Clock, Flame } from 'lucide-react'

interface Stats {
  scheduled: number
  published: number
  integrations: number
}

export function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    scheduled: 0,
    published: 0,
    integrations: 0
  })

  useEffect(() => {
    // TODO: Fetch from API
    setStats({
      scheduled: 3,
      published: 12,
      integrations: 2
    })
  }, [])

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold" style={{ color: '#e8eaed' }}>
            Dashboard
          </h1>
          <p className="mt-2" style={{ color: '#9ca3af' }}>
            Overview of your social media automation
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full animate-pulse" style={{ background: '#00d4ff' }}></div>
          <span className="text-sm" style={{ color: '#9ca3af' }}>System Online</span>
        </div>
      </div>

      {/* Stats Cards - Dark Theme with Glow */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-xl border backdrop-blur-sm transition-all duration-300 hover:-translate-y-1"
             style={{ 
               background: 'rgba(26, 42, 58, 0.6)',
               borderColor: '#2d3748'
             }}
             onMouseEnter={(e) => {
               e.currentTarget.style.borderColor = '#00d4ff'
               e.currentTarget.style.boxShadow = '0 10px 40px rgba(0, 212, 255, 0.1)'
             }}
             onMouseLeave={(e) => {
               e.currentTarget.style.borderColor = '#2d3748'
               e.currentTarget.style.boxShadow = 'none'
             }}>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center"
                 style={{ background: 'rgba(0, 212, 255, 0.1)' }}>
              <Calendar className="w-6 h-6" style={{ color: '#00d4ff' }} />
            </div>
            <div>
              <p className="text-sm" style={{ color: '#9ca3af' }}>Scheduled Posts</p>
              <p className="text-3xl font-bold" style={{ color: '#e8eaed' }}>{stats.scheduled}</p>
            </div>
          </div>
        </div>

        <div className="p-6 rounded-xl border backdrop-blur-sm transition-all duration-300 hover:-translate-y-1"
             style={{ 
               background: 'rgba(26, 42, 58, 0.6)',
               borderColor: '#2d3748'
             }}
             onMouseEnter={(e) => {
               e.currentTarget.style.borderColor = '#00d4ff'
               e.currentTarget.style.boxShadow = '0 10px 40px rgba(0, 212, 255, 0.1)'
             }}
             onMouseLeave={(e) => {
               e.currentTarget.style.borderColor = '#2d3748'
               e.currentTarget.style.boxShadow = 'none'
             }}>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center"
                 style={{ background: 'rgba(0, 212, 255, 0.1)' }}>
              <CheckCircle className="w-6 h-6" style={{ color: '#00d4ff' }} />
            </div>
            <div>
              <p className="text-sm" style={{ color: '#9ca3af' }}>Published</p>
              <p className="text-3xl font-bold" style={{ color: '#e8eaed' }}>{stats.published}</p>
            </div>
          </div>
        </div>

        <div className="p-6 rounded-xl border backdrop-blur-sm transition-all duration-300 hover:-translate-y-1"
             style={{ 
               background: 'rgba(26, 42, 58, 0.6)',
               borderColor: '#2d3748'
             }}
             onMouseEnter={(e) => {
               e.currentTarget.style.borderColor = '#ff6b35'
               e.currentTarget.style.boxShadow = '0 10px 40px rgba(255, 107, 53, 0.1)'
             }}
             onMouseLeave={(e) => {
               e.currentTarget.style.borderColor = '#2d3748'
               e.currentTarget.style.boxShadow = 'none'
             }}>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center"
                 style={{ background: 'rgba(255, 107, 53, 0.1)' }}>
              <TrendingUp className="w-6 h-6" style={{ color: '#ff6b35' }} />
            </div>
            <div>
              <p className="text-sm" style={{ color: '#9ca3af' }}>Connected Platforms</p>
              <p className="text-3xl font-bold" style={{ color: '#e8eaed' }}>{stats.integrations}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="p-6 rounded-xl border"
           style={{ 
             background: 'rgba(26, 42, 58, 0.6)',
             borderColor: '#2d3748'
           }}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold" style={{ color: '#e8eaed' }}>Quick Actions</h2>
            <p className="text-sm mt-1" style={{ color: '#9ca3af' }}>Get started with these common tasks</p>
          </div>
          <Flame className="w-5 h-5" style={{ color: '#ff6b35' }} />
        </div>
        
        <div className="flex flex-wrap gap-4">
          <Link
            to="/composer"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all duration-300 hover:scale-105"
            style={{
              background: 'linear-gradient(135deg, #00d4ff 0%, #0099cc 100%)',
              color: '#0a1628'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = '0 0 30px rgba(0, 212, 255, 0.4)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <Plus className="w-4 h-4" />
            Create Post
          </Link>
          
          <Link
            to="/integrations"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all duration-300 border-2"
            style={{
              background: 'transparent',
              borderColor: '#00d4ff',
              color: '#00d4ff'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#00d4ff'
              e.currentTarget.style.color = '#0a1628'
              e.currentTarget.style.boxShadow = '0 0 20px rgba(0, 212, 255, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent'
              e.currentTarget.style.color = '#00d4ff'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            Connect Platform
          </Link>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="p-6 rounded-xl border"
           style={{ 
             background: 'rgba(26, 42, 58, 0.6)',
             borderColor: '#2d3748'
           }}>
        <div className="flex items-center gap-3 mb-6">
          <Clock className="w-5 h-5" style={{ color: '#00d4ff' }} />
          <h2 className="text-xl font-semibold" style={{ color: '#e8eaed' }}>Recent Activity</h2>
        </div>
        
        <div className="text-center py-12">
          <div className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center"
               style={{ background: 'rgba(26, 42, 58, 0.8)' }}>
            <AlertCircle className="w-8 h-8" style={{ color: '#9ca3af' }} />
          </div>
          <p style={{ color: '#9ca3af' }}>No recent activity to display</p>
          <p className="text-sm mt-2" style={{ color: '#6b7280' }}>Create your first post to get started</p>
        </div>
      </div>
    </div>
  )
}
