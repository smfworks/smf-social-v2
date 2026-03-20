import { useState } from 'react'
import { Eye, EyeOff, Save, CheckCircle, Key } from 'lucide-react'

export function ManualTokenEntry({ platform }: { platform: string }) {
  const [token, setToken] = useState('')
  const [showToken, setShowToken] = useState(false)
  const [saved, setSaved] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSaved(false)

    try {
      console.log('Saving token for platform:', platform)
      console.log('Token length:', token.length)
      
      const response = await fetch('/api/integrations/manual-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform,
          tenant_id: 'tenant-1',
          access_token: token,
        }),
      })

      console.log('Response status:', response.status)
      
      let data
      try {
        data = await response.json()
      } catch (parseError) {
        console.error('Failed to parse response:', parseError)
        const text = await response.text()
        console.log('Raw response:', text)
        throw new Error('Invalid response from server')
      }
      
      console.log('Response data:', data)

      if (response.ok) {
        setSaved(true)
        setToken('')
        setTimeout(() => setSaved(false), 5000)
      } else {
        setError(data.detail || data.message || `Error ${response.status}: Failed to save token`)
      }
    } catch (error: any) {
      console.error('Failed to save token:', error)
      setError(error.message || 'Network error - check console')
    } finally {
      setSaving(false)
    }
  }

  const platformNames: Record<string, string> = {
    pinterest: 'Pinterest',
    linkedin: 'LinkedIn',
    x: 'X (Twitter)',
  }

  return (
    <div className="card p-6 mt-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg flex items-center justify-center"
             style={{ background: 'linear-gradient(135deg, #00d4ff 0%, #0099cc 100%)' }}>
          <Key className="w-5 h-5" style={{ color: '#0a1628' }} />
        </div>
        <div>
          <h3 className="text-lg font-semibold" style={{ color: '#e8eaed' }}>
            Manual Token Entry
          </h3>
          <p className="text-sm" style={{ color: '#9ca3af' }}>
            For {platformNames[platform]} testing while app is pending approval
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2" style={{ color: '#9ca3af' }}>
            Access Token
          </label>
          <div className="relative">
            <input
              type={showToken ? 'text' : 'password'}
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Paste your Pinterest access token here"
              required
              className="pr-12"
            />
            <button
              type="button"
              onClick={() => setShowToken(!showToken)}
              className="absolute right-3 top-1/2 -translate-y-1/2"
              style={{ color: '#9ca3af' }}
            >
              {showToken ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          <p className="text-xs mt-2" style={{ color: '#9ca3af' }}>
            From Pinterest Developer → Your App → Generate Access Token
          </p>
        </div>

        <div className="flex items-center gap-3 pt-4">
          <button
            type="submit"
            disabled={saving || !token}
            className="btn-primary flex items-center gap-2"
          >
            {saving ? (
              <>
                <div className="w-4 h-4 border-2 border-[#0a1628] border-t-transparent rounded-full animate-spin" />
                Saving...
              </>
            ) : saved ? (
              <>
                <CheckCircle className="w-4 h-4" />
                Token Saved!
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save Access Token
              </>
            )}
          </button>

          {saved && (
            <span className="text-sm" style={{ color: '#00d4ff' }}>
              Ready to post!
            </span>
          )}
        </div>

        {error && (
          <div className="mt-4 p-3 rounded-lg" style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444' }}>
            <p className="text-sm" style={{ color: '#ef4444' }}>{error}</p>
          </div>
        )}
      </form>
    </div>
  )
}
