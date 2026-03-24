import { useState } from 'react'
import { Eye, EyeOff, Save, CheckCircle } from 'lucide-react'

interface OAuthAppForm {
  client_id: string
  client_secret: string
  redirect_uri: string
}

// Pinterest REMOVED 2026-03-23 (business application rejected)
const PLATFORM_CONFIGS: Record<string, { name: string; icon: string; docsUrl: string }> = {
  linkedin: {
    name: 'LinkedIn',
    icon: '💼',
    docsUrl: 'https://www.linkedin.com/developers/apps',
  },
  x: {
    name: 'X (Twitter)',
    icon: '🐦',
    docsUrl: 'https://developer.twitter.com/en/portal/projects-and-apps',
  },
  instagram: {
    name: 'Instagram',
    icon: '📷',
    docsUrl: 'https://developers.facebook.com/docs/instagram',
  },
  facebook: {
    name: 'Facebook',
    icon: '📘',
    docsUrl: 'https://developers.facebook.com/apps',
  },
  tiktok: {
    name: 'TikTok',
    icon: '🎵',
    docsUrl: 'https://developers.tiktok.com/doc/login-kit-web',
  },
}

export function OAuthAppConfig({ platform }: { platform: string }) {
  const [form, setForm] = useState<OAuthAppForm>({
    client_id: '',
    client_secret: '',
    redirect_uri: `http://localhost:8000/api/auth/${platform}/callback`,
  })
  const [showSecret, setShowSecret] = useState(false)
  const [saved, setSaved] = useState(false)
  const [saving, setSaving] = useState(false)

  const config = PLATFORM_CONFIGS[platform]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)

    try {
      // Save to backend
      const response = await fetch('/api/oauth-apps', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform,
          tenant_id: 'tenant-1',
          ...form,
        }),
      })

      if (response.ok) {
        setSaved(true)
        setTimeout(() => setSaved(false), 3000)
      }
    } catch (error) {
      console.error('Failed to save:', error)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="card p-6">
      <div className="flex items-center gap-3 mb-6">
        <span className="text-2xl">{config.icon}</span>
        <div>
          <h3 className="text-lg font-semibold" style={{ color: '#e8eaed' }}>
            {config.name} OAuth App
          </h3>
          <a
            href={config.docsUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm hover:underline"
            style={{ color: '#00d4ff' }}
          >
            Get credentials →
          </a>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2" style={{ color: '#9ca3af' }}>
            Client ID
          </label>
          <input
            type="text"
            value={form.client_id}
            onChange={(e) => setForm({ ...form, client_id: e.target.value })}
            placeholder="Enter your Client ID"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2" style={{ color: '#9ca3af' }}>
            Client Secret
          </label>
          <div className="relative">
            <input
              type={showSecret ? 'text' : 'password'}
              value={form.client_secret}
              onChange={(e) => setForm({ ...form, client_secret: e.target.value })}
              placeholder="Enter your Client Secret"
              required
            />
            <button
              type="button"
              onClick={() => setShowSecret(!showSecret)}
              className="absolute right-3 top-1/2 -translate-y-1/2"
              style={{ color: '#9ca3af' }}
            >
              {showSecret ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2" style={{ color: '#9ca3af' }}>
            Redirect URI
          </label>
          <input
            type="url"
            value={form.redirect_uri}
            onChange={(e) => setForm({ ...form, redirect_uri: e.target.value })}
            placeholder="http://localhost:8000/api/auth/.../callback"
            required
          />
          <p className="text-xs mt-1" style={{ color: '#9ca3af' }}>
            Must match exactly in your {config.name} app settings
          </p>
        </div>

        <div className="flex items-center gap-3 pt-4">
          <button
            type="submit"
            disabled={saving}
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
                Saved!
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save Credentials
              </>
            )}
          </button>

          {saved && (
            <span className="text-sm" style={{ color: '#00d4ff' }}>
              Ready to connect!
            </span>
          )}
        </div>
      </form>
    </div>
  )
}