import { useState, useEffect } from 'react'
import { Link2, CheckCircle, XCircle, Loader2, AlertCircle } from 'lucide-react'
import { api } from '../api/client'
import { OAuthAppConfig } from '../components/OAuthAppConfig'

interface Integration {
  id: string
  platform: string
  account_name: string
  profile_picture?: string
  is_active: boolean
}

const PLATFORMS = [
  { id: 'pinterest', name: 'Pinterest', color: 'bg-red-600' },
  { id: 'linkedin', name: 'LinkedIn', color: 'bg-blue-700' },
  { id: 'x', name: 'X (Twitter)', color: 'bg-black' },
]

export function Integrations() {
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [connecting, setConnecting] = useState<string | null>(null)
  const [testMode, setTestMode] = useState(true) // Default to test mode

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
      // Use test mode by default for development
      const data = await api.connectPlatform(platform, testMode)
      
      if (data.mock_mode) {
        console.log('🧪 Mock OAuth mode:', data.note)
        // In test mode, simulate the OAuth redirect
        // Parse the state from the URL
        const url = new URL(data.authorization_url)
        const state = url.searchParams.get('state')
        
        // Simulate user authorization
        setTimeout(() => {
          const mockCode = `test-code-${platform}-${Date.now()}`
          handleMockCallback(platform, mockCode, state || '')
        }, 2000)
      } else {
        // Real OAuth - redirect to provider
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
      // Call the callback endpoint with mock code
      const response = await fetch(
        `/api/auth/${platform}/callback?code=${code}&state=${state}&tenant_id=tenant-1`
      )
      const data = await response.json()
      
      if (data.success) {
        setError('') // Clear any errors
        loadIntegrations() // Refresh the list
        alert(`✅ Test OAuth successful! Connected as ${data.account}`)
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
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Integrations</h1>
        <p className="text-gray-600 mt-1">Connect your social media accounts</p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
          <AlertCircle className="w-5 h-5" />
          {error}
          <button onClick={() => setError('')} className="ml-auto text-sm hover:underline">Dismiss</button>
        </div>
      )}

      {/* Test Mode Toggle */}
      <div className="flex items-center gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <span className="text-sm font-medium text-yellow-800">Test Mode:</span>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={testMode}
            onChange={(e) => setTestMode(e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
        </label>
        <span className="text-sm text-yellow-700">
          {testMode ? 'Using mock OAuth (no real credentials needed)' : 'Using real OAuth'}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {PLATFORMS.map((platform) => {
          const connected = isConnected(platform.id)
          const integration = getIntegration(platform.id)
          
          return (
            <div
              key={platform.id}
              className="bg-white p-6 rounded-lg border border-gray-200"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 ${platform.color} rounded-lg flex items-center justify-center text-white font-bold`}>
                    {platform.name[0]}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{platform.name}</h3>
                    {connected && (
                      <span className="text-sm text-green-600 flex items-center gap-1">
                        <CheckCircle className="w-4 h-4" />
                        Connected
                      </span>
                    )}
                  </div>
                </div>
                
                {connected ? (
                  <button
                    onClick={() => disconnect(integration!.id)}
                    className="text-red-600 hover:text-red-700 text-sm font-medium"
                  >
                    Disconnect
                  </button>
                ) : (
                  <button
                    onClick={() => connectPlatform(platform.id)}
                    disabled={connecting === platform.id}
                    className={`px-4 py-2 rounded-lg disabled:opacity-50 text-sm font-medium ${
                      testMode 
                        ? 'bg-yellow-500 text-white hover:bg-yellow-600' 
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    {connecting === platform.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : testMode ? (
                      'Connect (Test)'
                    ) : (
                      'Connect'
                    )}
                  </button>
                )}
              </div>
              
              {connected && integration ? (
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  {integration.profile_picture ? (
                    <img
                      src={integration.profile_picture}
                      alt=""
                      className="w-8 h-8 rounded-full"
                    />
                  ) : (
                    <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-xs">
                      {integration.account_name[0]?.toUpperCase()}
                    </div>
                  )}
                  <span className="text-sm text-gray-700">{integration.account_name}</span>
                </div>
              ) : (
                <p className="text-sm text-gray-500">
                  Connect your {platform.name} account to start posting
                </p>
              )}
            </div>
          )
        })}
      </div>

      {/* OAuth Configuration Forms - Show when test mode is OFF */}
      {!testMode && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold" style={{ color: '#e8eaed' }}>
            OAuth App Configuration
          </h3>
          <p className="text-sm" style={{ color: '#9ca3af' }}>
            Enter your OAuth credentials for each platform you want to connect.
          </p>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <OAuthAppConfig platform="pinterest" />
            <OAuthAppConfig platform="linkedin" />
            <OAuthAppConfig platform="x" />
          </div>
        </div>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-2">Setup Required</h3>
        <p className="text-blue-800 text-sm mb-4">
          Before connecting accounts, you need to create OAuth apps on each platform.
          <a href="#" className="underline">View setup guide →</a>
        </p>
        
        <div className="flex flex-wrap gap-2">
          {PLATFORMS.map((platform) => (
            <a
              key={platform.id}
              href="#"
              className="text-xs px-3 py-1 bg-white rounded-full text-blue-700 hover:bg-blue-100"
            >
              {platform.name} Setup
            </a>
          ))}
        </div>
      </div>
    </div>
  )
}
