import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Send, Calendar, Image as ImageIcon, PenTool, Hash, Clock } from 'lucide-react'

interface Integration {
  id: string
  platform: string
  account_name: string
}

const PLATFORM_COLORS: Record<string, string> = {
  linkedin: '#0077b5',
  x: '#e8eaed',
  instagram: '#e1306c',
  facebook: '#1877f2',
  tiktok: '#ff0050',
}

export function Composer() {
  const navigate = useNavigate()
  const [content, setContent] = useState('')
  const [selectedPlatform, setSelectedPlatform] = useState('')
  const [scheduledDate, setScheduledDate] = useState('')
  const [scheduledTime, setScheduledTime] = useState('')
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Fetch connected integrations from backend
    const fetchIntegrations = async () => {
      try {
        const response = await fetch('/api/integrations/?tenant_id=tenant-1')
        if (response.ok) {
          const data = await response.json()
          setIntegrations(data)
          // Auto-select first integration if available
          if (data.length > 0 && !selectedPlatform) {
            setSelectedPlatform(data[0].platform)
          }
        }
      } catch (error) {
        console.error('Failed to fetch integrations:', error)
      }
    }

    fetchIntegrations()
  }, [selectedPlatform])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedPlatform) return

    setLoading(true)

    try {
      const scheduledFor = scheduledDate && scheduledTime
        ? new Date(`${scheduledDate}T${scheduledTime}`).toISOString()
        : null

      console.log('Creating post:', { content, selectedPlatform, scheduledFor })
      
      navigate('/posts')
    } catch (error) {
      console.error('Failed to create post:', error)
    } finally {
      setLoading(false)
    }
  }

  const characterCount = content.length
  const maxCharacters = 500
  const progress = Math.min((characterCount / maxCharacters) * 100, 100)

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <PenTool className="w-8 h-8" style={{ color: '#00d4ff' }} />
        <div>
          <h1 className="text-3xl font-bold" style={{ color: '#e8eaed' }}>Create Post</h1>
          <p className="mt-1" style={{ color: '#9ca3af' }}>Compose and schedule your content</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Platform Selection */}
        <div className="p-6 rounded-xl border"
             style={{ background: 'rgba(26, 42, 58, 0.6)', borderColor: '#2d3748' }}
        >
          <label className="block text-sm font-medium mb-4" style={{ color: '#e8eaed' }}>
            Select Platform
          </label>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {integrations.map((integration) => {
              const isSelected = selectedPlatform === integration.id
              const platformColor = PLATFORM_COLORS[integration.platform] || '#00d4ff'
              
              return (
                <button
                  key={integration.id}
                  type="button"
                  onClick={() => setSelectedPlatform(integration.id)}
                  className="p-4 rounded-lg border-2 transition-all duration-300 text-left"
                  style={{
                    background: isSelected ? `${platformColor}20` : 'rgba(10, 22, 40, 0.6)',
                    borderColor: isSelected ? platformColor : '#2d3748',
                    boxShadow: isSelected ? `0 0 20px ${platformColor}30` : 'none'
                  }}
                  onMouseEnter={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.borderColor = platformColor
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.borderColor = '#2d3748'
                    }
                  }}
                >
                  <div className="flex items-center gap-3">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ background: platformColor }}
                    />
                    <span className="font-medium capitalize" style={{ color: '#e8eaed' }}>
                      {integration.platform}
                    </span>
                  </div>
                  <p className="text-xs mt-2" style={{ color: '#9ca3af' }}>
                    {integration.account_name}
                  </p>
                </button>
              )
            })}
          </div>
          
          {integrations.length === 0 && (
            <div className="mt-4 p-4 rounded-lg text-center"
                 style={{ background: 'rgba(10, 22, 40, 0.6)' }}
            >
              <p style={{ color: '#9ca3af' }}>
                No platforms connected.{''}
                <a href="/integrations" style={{ color: '#00d4ff' }} className="hover:underline">
                  Connect one first →
                </a>
              </p>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-6 rounded-xl border"
             style={{ background: 'rgba(26, 42, 58, 0.6)', borderColor: '#2d3748' }}
        >
          <div className="flex items-center gap-2 mb-4">
            <Hash className="w-5 h-5" style={{ color: '#00d4ff' }} />
            <label className="text-sm font-medium" style={{ color: '#e8eaed' }}>
              Content
            </label>
          </div>
          
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={6}
            className="w-full px-4 py-3 rounded-lg resize-none transition-all duration-300"
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
            placeholder="What do you want to share?"
            maxLength={maxCharacters}
            required
          />
          
          {/* Character Count with Progress Bar */}
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-2">
              <span style={{ color: '#9ca3af' }}>{characterCount} / {maxCharacters}</span>
              {characterCount > maxCharacters && (
                <span style={{ color: '#ef4444' }}>Too long</span>
              )}
            </div>            
            <div className="h-1 rounded-full overflow-hidden" style={{ background: 'rgba(45, 55, 72, 0.5)' }}>
              <div 
                className="h-full rounded-full transition-all duration-300"
                style={{
                  width: `${progress}%`,
                  background: characterCount > maxCharacters ? '#ef4444' : '#00d4ff'
                }}
              />
            </div>
          </div>
        </div>

        {/* Media Upload */}
        <div className="p-6 rounded-xl border"
             style={{ background: 'rgba(26, 42, 58, 0.6)', borderColor: '#2d3748' }}
        >
          <div className="flex items-center gap-2 mb-4">
            <ImageIcon className="w-5 h-5" style={{ color: '#00d4ff' }} />
            <label className="text-sm font-medium" style={{ color: '#e8eaed' }}>
              Media
            </label>
          </div>
          
          <div 
            className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-300"
            style={{ 
              borderColor: '#2d3748',
              background: 'rgba(10, 22, 40, 0.4)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#00d4ff'
              e.currentTarget.style.background = 'rgba(0, 212, 255, 0.05)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#2d3748'
              e.currentTarget.style.background = 'rgba(10, 22, 40, 0.4)'
            }}
          >
            <ImageIcon className="w-10 h-10 mx-auto mb-3" style={{ color: '#6b7280' }} />
            <p style={{ color: '#9ca3af' }}>Click to upload images</p>
            <p className="text-xs mt-1" style={{ color: '#6b7280' }}>or drag and drop</p>
          </div>
        </div>

        {/* Scheduling */}
        <div className="p-6 rounded-xl border"
             style={{ background: 'rgba(26, 42, 58, 0.6)', borderColor: '#2d3748' }}
        >
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-5 h-5" style={{ color: '#00d4ff' }} />
            <label className="text-sm font-medium" style={{ color: '#e8eaed' }}>
              Schedule (optional)
            </label>
          </div>
          
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <input
                type="date"
                value={scheduledDate}
                onChange={(e) => setScheduledDate(e.target.value)}
                className="w-full px-4 py-3 rounded-lg transition-all duration-300"
                style={{
                  background: 'rgba(10, 22, 40, 0.6)',
                  border: '1px solid #2d3748',
                  color: '#e8eaed'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#00d4ff'
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = '#2d3748'
                }}
              />
            </div>
            
            <div className="flex-1 min-w-[200px]">
              <input
                type="time"
                value={scheduledTime}
                onChange={(e) => setScheduledTime(e.target.value)}
                className="w-full px-4 py-3 rounded-lg transition-all duration-300"
                style={{
                  background: 'rgba(10, 22, 40, 0.6)',
                  border: '1px solid #2d3748',
                  color: '#e8eaed'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#00d4ff'
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = '#2d3748'
                }}
              />
            </div>
          </div>
          
          {!scheduledDate && (
            <p className="text-xs mt-3" style={{ color: '#6b7280' }}>
              Leave blank to save as draft
            </p>
          )}
        </div>

        {/* Submit */}
        <div className="flex gap-4 pt-4">
          <button
            type="submit"
            disabled={loading || !selectedPlatform || !content}
            className="flex-1 py-4 px-6 rounded-lg font-medium transition-all duration-300 disabled:opacity-50 flex items-center justify-center gap-2"
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
              <>
                <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                {scheduledDate ? 'Schedule Post' : 'Save as Draft'}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
