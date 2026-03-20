import { useEffect, useState } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { CheckCircle, XCircle, Loader2 } from 'lucide-react'

export function OAuthCallback() {
  const { platform } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')

      if (!code || !state) {
        setStatus('error')
        setMessage('Missing authorization code or state')
        return
      }

      try {
        const response = await fetch(`/api/auth/${platform}/callback?code=${code}&state=${state}`)
        
        if (response.ok) {
          setStatus('success')
          setMessage('Account connected successfully!')
          
          setTimeout(() => {
            navigate('/integrations')
          }, 2000)
        } else {
          const error = await response.text()
          setStatus('error')
          setMessage(error || 'Failed to connect account')
        }
      } catch (error) {
        setStatus('error')
        setMessage('Network error. Please try again.')
      }
    }

    handleCallback()
  }, [platform, searchParams, navigate])

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md text-center max-w-md">
        {status === 'loading' && (
          <>
            <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
            <h1 className="text-xl font-semibold text-gray-900">Connecting...</h1>
            <p className="text-gray-600 mt-2">Please wait while we connect your {platform} account.</p>
          </>
        )}

        {status === 'success' && (
          <>
            <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
            <h1 className="text-xl font-semibold text-gray-900">Connected!</h1>
            <p className="text-gray-600 mt-2">{message}</p>
            <p className="text-sm text-gray-500 mt-4">Redirecting...</p>
          </>
        )}

        {status === 'error' && (
          <>
            <XCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
            <h1 className="text-xl font-semibold text-gray-900">Connection Failed</h1>
            <p className="text-red-600 mt-2">{message}</p>
            <button
              onClick={() => navigate('/integrations')}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Back to Integrations
            </button>
          </>
        )}
      </div>
    </div>
  )
}