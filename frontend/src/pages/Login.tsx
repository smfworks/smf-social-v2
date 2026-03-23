import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Lock, Mail, Flame } from 'lucide-react'

export function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      // TODO: Replace with actual API call
      if (email === 'admin@smfworks.com' && password === 'admin') {
        localStorage.setItem('token', 'fake-jwt-token')
        navigate('/')
      } else {
        setError('Invalid credentials')
      }
    } catch (err) {
      setError('Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4"
         style={{ background: 'linear-gradient(135deg, #0a1628 0%, #1a2a3a 100%)' }}
    >
      <div className="w-full max-w-md p-8 rounded-xl border backdrop-blur-sm"
           style={{ 
             background: 'rgba(26, 42, 58, 0.8)',
             borderColor: '#2d3748'
           }}
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center animate-pulse"
                 style={{ 
                   background: 'linear-gradient(135deg, #00d4ff 0%, #0099cc 100%)',
                   boxShadow: '0 0 20px rgba(0, 212, 255, 0.3)'
                 }}
            >
              <Flame className="w-7 h-7" style={{ color: '#0a1628' }} />
            </div>
            <h1 className="text-3xl font-bold">
              <span style={{ color: '#e8eaed' }}>SMF</span>
              <span style={{ color: '#00d4ff' }}>Social</span>
            </h1>
          </div>
          <p className="text-sm" style={{ color: '#9ca3af' }}>
            Social media automation forged with AI
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-lg flex items-center gap-2"
               style={{ 
                 background: 'rgba(239, 68, 68, 0.1)',
                 border: '1px solid rgba(239, 68, 68, 0.3)',
                 color: '#ef4444'
               }}
          >
            <span className="text-sm">{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Email Field */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: '#e8eaed' }}>
              Email
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-5 h-5" style={{ color: '#6b7280' }} />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-3 rounded-lg transition-all duration-300"
                style={{
                  background: 'rgba(10, 22, 40, 0.6)',
                  border: '1px solid #2d3748',
                  color: '#e8eaed'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#00d4ff'
                  e.currentTarget.style.boxShadow = '0 0 0 3px rgba(0, 212, 255, 0.1)'
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = '#2d3748'
                  e.currentTarget.style.boxShadow = 'none'
                }}
                placeholder="admin@smfworks.com"
                required
              />
            </div>
          </div>

          {/* Password Field */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: '#e8eaed' }}>
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5" style={{ color: '#6b7280' }} />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-3 rounded-lg transition-all duration-300"
                style={{
                  background: 'rgba(10, 22, 40, 0.6)',
                  border: '1px solid #2d3748',
                  color: '#e8eaed'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#00d4ff'
                  e.currentTarget.style.boxShadow = '0 0 0 3px rgba(0, 212, 255, 0.1)'
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = '#2d3748'
                  e.currentTarget.style.boxShadow = 'none'
                }}
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 rounded-lg font-medium transition-all duration-300 disabled:opacity-50"
            style={{
              background: loading ? '#4b5563' : 'linear-gradient(135deg, #00d4ff 0%, #0099cc 100%)',
              color: '#0a1628'
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.currentTarget.style.boxShadow = '0 0 30px rgba(0, 212, 255, 0.4)'
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                Signing in...
              </span>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-xs italic" style={{ color: '#6b7280' }}>
            "Make it hot by striking"
          </p>
          <p className="text-xs mt-2" style={{ color: '#4b5563' }}>
            v2.0 — Customer 0 Ready
          </p>
        </div>
      </div>
    </div>
  )
}
