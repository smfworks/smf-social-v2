import { useState, useEffect } from 'react'
import { Link2, CheckCircle, XCircle, Loader2 } from 'lucide-react'

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
  const [loading, setLoading] = useState(false)
  const [connecting, setConnecting] = useState<string | null>(null)

  useEffect(() => {
    // TODO: Fetch from API
    // fetch('/api/integrations?tenant_id=xxx').then(...)
    
    // Simulated data
    setIntegrations([
      { id: '1', platform: 'pinterest', account_name: '@michaelgannotti', is_active: true },
    ])
  }, [])

  const connectPlatform = async (platform: string) => {
    setConnecting(platform)
    
    try {
      // Start OAuth flow
      const response = await fetch(`/api/auth/${platform}/connect?tenant_id=tenant-1`)
      const data = await response.json()
      
      // Open OAuth window
      window.location.href = data.authorization_url
    } catch (error) {
      console.error('Failed to connect:', error)
    } finally {
      setConnecting(null)
    }
  }

  const disconnect = async (integrationId: string) => {
    if (!confirm('Disconnect this account?')) return
    
    // TODO: API call
    setIntegrations(integrations.filter(i => i.id !== integrationId))
  }

  const isConnected = (platform: string) => {
    return integrations.some(i => i.platform === platform && i.is_active)
  }

  const getIntegration = (platform: string) => {
    return integrations.find(i => i.platform === platform)
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Integrations</h1>
        <p className="text-gray-600 mt-1">Connect your social media accounts</p>
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
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm font-medium"
                  >
                    {connecting === platform.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
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

      {/* Setup Instructions */}
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
