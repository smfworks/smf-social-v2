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

    try {
      // Save token directly (bypass OAuth flow)
      const response = await fetch('/api/integrations/manual-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform,
          tenant_id: 'tenant-1',
          access_token: token,
        }),
      })

      if (response.ok) {
        setSaved(true)
        setTimeout(() => {
          setSaved(false)
          setToken('')
        }, 3000)
      }
    } catch (error) {
      console.error('Failed to save token:', error)
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
      </form>
    </div>
  )
}
