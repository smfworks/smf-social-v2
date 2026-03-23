import { useState, useEffect } from 'react'
import { CheckCircle, Loader2, AlertCircle, Link2, Shield, Flame, ExternalLink } from 'lucide-react'
import { api } from '../api/client'
import { OAuthAppConfig } from '../components/OAuthAppConfig'
import { ManualTokenEntry } from '../components/ManualTokenEntry'

interface Integration {
  id: string
  platform: string
  account_name: string
  profile_picture?: string
  is_active: boolean
}

// Pinterest REMOVED 2026-03-23 (business application rejected)
const PLATFORMS = [
  {
    id: 'linkedin',
    name: 'LinkedIn',
    color: '#0077b5',
    bgColor: 'rgba(0, 119, 181, 0.1)',
    description: 'Professional networking and B2B marketing'
  },
  {
    id: 'x',
    name: 'X (Twitter)',
    color: '#e8eaed',
    bgColor: 'rgba(232, 234, 237, 0.1)',
    description: 'Real-time conversations and updates'
  },
  {
    id: 'instagram',
    name: 'Instagram',
    color: '#e1306c',
    bgColor: 'rgba(225, 48, 108, 0.1)',
    description: 'Visual content and stories'
  },
  {
    id: 'facebook',
    name: 'Facebook',
    color: '#1877f2',
    bgColor: 'rgba(24, 119, 242, 0.1)',
    description: 'Community engagement and pages'
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    color: '#ff0050',
    bgColor: 'rgba(255, 0, 80, 0.1)',
    description: 'Short-form video content'
  },
]

export function Integrations() {
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [connecting, setConnecting] = useState<string | null>(null)
  const [testMode, setTestMode] = useState(true)
  const [showConfig, setShowConfig] = useState(false)

  useEffect(() => {
    loadIntegrations()
  }, [])

  const loadIntegrations = async () => {
    try {
      setLoading(true)
      const data = await api.getIntegrations()
      setIntegrations(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load integrations')
    } finally {
      setLoading(false)
    }
  }

  const connectPlatform = async (platform: string) => {
    setConnecting(platform)
    
    try {
      const data = await api.connectPlatform(platform, testMode)
      
      if (data.mock_mode) {
        console.log('🧪 Mock OAuth mode:', data.note)
        const url = new URL(data.authorization_url)
        const state = url.searchParams.get('state')
        
        setTimeout(() => {
          const mockCode = `test-code-${platform}-${Date.now()}`
          handleMockCallback(platform, mockCode, state || '')
        }, 2000)
      } else {
        window.location.href = data.authorization_url
      }
    } catch (error: any) {
      setError(error.message || 'Failed to start OAuth')
    } finally {
      setConnecting(null)
    }
  }
  
  const handleMockCallback = async (platform: string, code: string, state: string) => {
    try {
      const response = await fetch(
        `/api/auth/${platform}/callback?code=${code}&state=${state}&tenant_id=tenant-1`
      )
      const data = await response.json()
      
      if (data.success) {
        setError('')
        loadIntegrations()
      }
    } catch (error: any) {
      setError('Mock callback failed: ' + error.message)
    }
  }

  const disconnect = async (integrationId: string) => {
    if (!confirm('Disconnect this account?')) return
    
    try {
      await api.disconnectIntegration(integrationId)
      setIntegrations(integrations.filter(i => i.id !== integrationId))
    } catch (error: any) {
      setError(error.message || 'Failed to disconnect')
    }
  }

  const isConnected = (platform: string) => {
    return integrations.some(i => i.platform === platform && i.is_active)
  }

  const getIntegration = (platform: string) => {
    return integrations.find(i => i.platform === platform)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin" style={{ color: '#00d4ff' }} />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Link2 className="w-8 h-8" style={{ color: '#00d4ff' }} />
            <h1 className="text-3xl font-bold" style={{ color: '#e8eaed' }}>Integrations</h1>
          </div>
          <p className="mt-2" style={{ color: '#9ca3af' }}>Connect your social media accounts</p>
        </div>
        
        <div className="flex items-center gap-2 px-4 py-2 rounded-lg"
             style={{ background: 'rgba(26, 42, 58, 0.8)' }}>
          <Shield className="w-4 h-4" style={{ color: '#00d4ff' }} />
          <span className="text-sm" style={{ color: '#9ca3af' }}>OAuth Ready</span>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg flex items-center gap-3"
             style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
          <AlertCircle className="w-5 h-5 flex-shrink-0" style={{ color: '#ef4444' }} />
          <span style={{ color: '#e8eaed' }}>{error}</span>
          <button 
            onClick={() => setError('')} 
            className="ml-auto text-sm hover:underline"
            style={{ color: '#9ca3af' }}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Test Mode Toggle */}
      <div className="p-6 rounded-xl border"
           style={{ 
             background: testMode ? 'rgba(234, 179, 8, 0.1)' : 'rgba(26, 42, 58, 0.6)',
             borderColor: testMode ? 'rgba(234, 179, 8, 0.3)' : '#2d3748'
           }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium" style={{ color: '#e8eaed' }}>Test Mode:</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={testMode}
                  onChange={(e) => setTestMode(e.target.checked)}
                  className="sr-only peer"
                />
                <div 
                  className="w-11 h-6 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"
                  style={{
                    background: testMode ? '#00d4ff' : '#4b5563'
                  }}
                />
              </label>
            </div>
            <span className="text-sm" style={{ color: testMode ? '#eab308' : '#9ca3af' }}>
              {testMode ? 'Using mock OAuth (no real credentials needed)' : 'Using real OAuth credentials'}
            </span>
          </div>
          
          <button
            onClick={() => setShowConfig(!showConfig)}
            className="text-sm hover:underline"
            style={{ color: '#00d4ff' }}
          >
            {showConfig ? 'Hide Config' : 'Show Config'}
          </button>
        </div>
      </div>

      {/* Platform Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {PLATFORMS.map((platform) => {
          const connected = isConnected(platform.id)
          const integration = getIntegration(platform.id)
          
          return (
            <div
              key={platform.id}
              className="p-6 rounded-xl border backdrop-blur-sm transition-all duration-300 hover:-translate-y-1"
              style={{ 
                background: 'rgba(26, 42, 58, 0.6)',
                borderColor: connected ? platform.color : '#2d3748',
                boxShadow: connected ? `0 0 20px ${platform.bgColor}` : 'none'
              }}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div 
                    className="w-12 h-12 rounded-lg flex items-center justify-center font-bold text-xl"
                    style={{ 
                      background: platform.bgColor,
                      color: platform.color,
                      border: `2px solid ${connected ? platform.color : 'transparent'}`
                    }}
                  >
                    {platform.name[0]}
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg" style={{ color: '#e8eaed' }}>{platform.name}</h3>
                    {connected && (
                      <div className="flex items-center gap-1">
                        <CheckCircle className="w-4 h-4" style={{ color: '#00d4ff' }} />
                        <span className="text-sm" style={{ color: '#00d4ff' }}>Connected</span>
                      </div>
                    )}
                  </div>
                </div>
                
                {connected ? (
                  <button
                    onClick={() => disconnect(integration!.id)}
                    className="text-sm font-medium px-3 py-1 rounded transition-colors"
                    style={{ color: '#ef4444' }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'transparent'
                    }}
                  >
                    Disconnect
                  </button>
                ) : (
                  <button
                    onClick={() => connectPlatform(platform.id)}
                    disabled={connecting === platform.id}
                    className="px-4 py-2 rounded-lg font-medium transition-all duration-300 disabled:opacity-50"
                    style={{
                      background: testMode ? 'rgba(234, 179, 8, 0.2)' : 'rgba(0, 212, 255, 0.2)',
                      color: testMode ? '#eab308' : '#00d4ff',
                      border: `1px solid ${testMode ? '#eab308' : '#00d4ff'}`
                    }}
                    onMouseEnter={(e) => {
                      if (connecting !== platform.id) {
                        e.currentTarget.style.background = testMode ? 'rgba(234, 179, 8, 0.3)' : 'rgba(0, 212, 255, 0.3)'
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = testMode ? 'rgba(234, 179, 8, 0.2)' : 'rgba(0, 212, 255, 0.2)'
                    }}
                  >
                    {connecting === platform.id ? (
                      <Loader2 className="w-4 h-4 animate-spin mx-auto" />
                    ) : (
                      testMode ? 'Connect (Test)' : 'Connect'
                    )}
                  </button>
                )}
              </div>
              
              <p className="text-sm mb-4" style={{ color: '#9ca3af' }}>{platform.description}</p>
              
              {connected && integration ? (
                <div className="p-3 rounded-lg flex items-center gap-3"
                     style={{ background: 'rgba(26, 42, 58, 0.8)' }}>
                  {integration.profile_picture ? (
                    <img
                      src={integration.profile_picture}
                      alt=""
                      className="w-10 h-10 rounded-full border-2"
                      style={{ borderColor: platform.color }}
                    />
                  ) : (
                    <div 
                      className="w-10 h-10 rounded-full flex items-center justify-center font-bold"
                      style={{ 
                        background: platform.bgColor,
                        color: platform.color
                      }}
                    >
                      {integration.account_name[0]?.toUpperCase()}
                    </div>
                  )}
                  <div>
                    <p className="font-medium" style={{ color: '#e8eaed' }}>{integration.account_name}</p>
                    <p className="text-xs" style={{ color: '#6b7280' }}>{platform.name} Account</p>
                  </div>                
                </div>
              ) : (
                <div className="p-3 rounded-lg text-sm"
                     style={{ background: 'rgba(26, 42, 58, 0.4)', color: '#6b7280' }}>
                  Click Connect to link your {platform.name} account
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* OAuth Configuration Section */}
      {showConfig && !testMode && (
        <div className="space-y-6">
          <div className="p-6 rounded-xl border"
               style={{ background: 'rgba(26, 42, 58, 0.6)', borderColor: '#2d3748' }}>
            <div className="flex items-center gap-3 mb-6">
              <ExternalLink className="w-5 h-5" style={{ color: '#00d4ff' }} />
              <h3 className="text-lg font-semibold" style={{ color: '#e8eaed' }}>OAuth App Configuration</h3>
            </div>            
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <OAuthAppConfig platform="linkedin" />
              <OAuthAppConfig platform="x" />
              <OAuthAppConfig platform="instagram" />
              <OAuthAppConfig platform="facebook" />
              <OAuthAppConfig platform="tiktok" />
            </div>
          </div>

          <div className="p-6 rounded-xl border"
               style={{ background: 'rgba(26, 42, 58, 0.6)', borderColor: '#2d3748' }}>
            <div className="flex items-center gap-3 mb-6">
              <Flame className="w-5 h-5" style={{ color: '#ff6b35' }} />
              <h3 className="text-lg font-semibold" style={{ color: '#e8eaed' }}>Manual Token Entry</h3>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <ManualTokenEntry platform="linkedin" />
              <ManualTokenEntry platform="x" />
              <ManualTokenEntry platform="instagram" />
              <ManualTokenEntry platform="facebook" />
              <ManualTokenEntry platform="tiktok" />
            </div>
          </div>
        </div>
      )}

      {/* Help Section */}
      {!showConfig && (
        <div className="p-6 rounded-xl border text-center"
             style={{ background: 'rgba(26, 42, 58, 0.4)', borderColor: '#2d3748' }}>
          <p className="text-sm" style={{ color: '#9ca3af' }}>
            Need help setting up OAuth apps? Check the{' '}
            <a href="#" className="hover:underline" style={{ color: '#00d4ff' }}>OAuth Setup Guide</a>
            {' '}for step-by-step instructions.
          </p>
        </div>
      )}
    </div>
  )
}
