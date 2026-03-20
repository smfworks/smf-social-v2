const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

async function fetchClient(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE}${endpoint}`
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })
  
  if (!response.ok) {
    const error = await response.text()
    throw new Error(error || 'API request failed')
  }
  
  return response.json()
}

export const api = {
  // Auth
  login: (email: string, password: string) =>
    fetchClient('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  
  // Integrations
  getIntegrations: () =>
    fetchClient('/integrations?tenant_id=tenant-1'),
  
  connectPlatform: (platform: string, test: boolean = true) =>
    fetchClient(`/auth/${platform}/connect?tenant_id=tenant-1&test=${test}`),
  
  disconnectIntegration: (id: string) =>
    fetchClient(`/integrations/${id}?tenant_id=tenant-1`, {
      method: 'DELETE',
    }),
  
  // Posts
  getPosts: () =>
    fetchClient('/posts?tenant_id=tenant-1'),
  
  createPost: (data: any) =>
    fetchClient('/posts', {
      method: 'POST',
      body: JSON.stringify({ ...data, tenant_id: 'tenant-1' }),
    }),
  
  publishPost: (id: string) =>
    fetchClient(`/posts/${id}/publish?tenant_id=tenant-1`, {
      method: 'POST',
    }),
}
