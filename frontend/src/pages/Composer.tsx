import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Send, Calendar, Image as ImageIcon } from 'lucide-react'

interface Integration {
  id: string
  platform: string
  account_name: string
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
    // TODO: Fetch connected integrations
    setIntegrations([
      { id: '1', platform: 'pinterest', account_name: '@michaelgannotti' },
    ])
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedPlatform) return

    setLoading(true)

    try {
      const scheduledFor = scheduledDate && scheduledTime
        ? new Date(`${scheduledDate}T${scheduledTime}`).toISOString()
        : null

      // TODO: API call
      // await fetch('/api/posts', {
      //   method: 'POST',
      //   body: JSON.stringify({ content, integration_id: selectedPlatform, scheduled_for: scheduledFor })
      // })

      console.log('Creating post:', { content, selectedPlatform, scheduledFor })
      
      // Redirect to posts list
      navigate('/posts')
    } catch (error) {
      console.error('Failed to create post:', error)
    } finally {
      setLoading(false)
    }
  }

  const characterCount = content.length
  const maxCharacters = 500 // Pinterest limit

  return (
    <div className="max-w-2xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Create Post</h1>
        <p className="text-gray-600 mt-1">Compose and schedule your content</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Platform Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Platform
          </label>
          <div className="grid grid-cols-3 gap-3">
            {integrations.map((integration) => (
              <button
                key={integration.id}
                type="button"
                onClick={() => setSelectedPlatform(integration.id)}
                className={`p-3 border rounded-lg text-left transition-colors ${
                  selectedPlatform === integration.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${
                    integration.platform === 'pinterest' ? 'bg-red-600' :
                    integration.platform === 'linkedin' ? 'bg-blue-700' :
                    'bg-black'
                  }`} />
                  <span className="text-sm font-medium capitalize">
                    {integration.platform}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{integration.account_name}</p>
              </button>
            ))}
          </div>
          
          {integrations.length === 0 && (
            <p className="text-sm text-gray-500 mt-2">
              No platforms connected.{' '}
              <a href="/integrations" className="text-blue-600 hover:underline">
                Connect one first →
              </a>
            </p>
          )}
        </div>

        {/* Content */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Content
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={6}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            placeholder="What do you want to share?"
            maxLength={maxCharacters}
            required
          />
          <div className="flex justify-between text-sm mt-2">
            <span className="text-gray-500">
              {characterCount} / {maxCharacters}
            </span>
            {characterCount > maxCharacters && (
              <span className="text-red-600">Too long</span>
            )}
          </div>
        </div>

        {/* Media Upload (Placeholder) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Media
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors cursor-pointer">
            <ImageIcon className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm text-gray-600">Click to upload images</p>
            <p className="text-xs text-gray-400 mt-1">or drag and drop</p>
          </div>
        </div>

        {/* Scheduling */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Calendar className="w-4 h-4 inline mr-1" />
            Schedule (optional)
          </label>
          <div className="flex gap-3">
            <input
              type="date"
              value={scheduledDate}
              onChange={(e) => setScheduledDate(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="time"
              value={scheduledTime}
              onChange={(e) => setScheduledTime(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          {!scheduledDate && (
            <p className="text-xs text-gray-500 mt-1">
              Leave blank to save as draft
            </p>
          )}
        </div>

        {/* Submit */}
        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={loading || !selectedPlatform || !content}
            className="flex-1 py-3 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                {scheduledDate ? 'Schedule Post' : 'Save as Draft'}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
