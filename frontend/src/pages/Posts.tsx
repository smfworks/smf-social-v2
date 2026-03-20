import { useState, useEffect } from 'react'
import { Edit2, Trash2, ExternalLink, Clock, CheckCircle, AlertCircle } from 'lucide-react'

interface Post {
  id: string
  content: string
  platform: string
  status: 'draft' | 'scheduled' | 'published' | 'failed'
  scheduled_for?: string
  published_at?: string
  platform_url?: string
}

export function Posts() {
  const [posts, setPosts] = useState<Post[]>([])
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => {
    // TODO: Fetch from API
    setPosts([
      {
        id: '1',
        content: 'Check out our latest blog post on AI automation!',
        platform: 'pinterest',
        status: 'scheduled',
        scheduled_for: '2026-03-25T09:00:00Z',
      },
      {
        id: '2',
        content: 'How to leverage AI for small business growth',
        platform: 'linkedin',
        status: 'published',
        published_at: '2026-03-20T10:00:00Z',
        platform_url: 'https://linkedin.com/post/123',
      },
    ])
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'published':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'scheduled':
        return <Clock className="w-4 h-4 text-blue-600" />
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-600" />
      default:
        return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      draft: 'Draft',
      scheduled: 'Scheduled',
      publishing: 'Publishing...',
      published: 'Published',
      failed: 'Failed',
    }
    return texts[status] || status
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleString()
  }

  const filteredPosts = posts.filter((post) => {
    if (filter === 'all') return true
    return post.status === filter
  })

  const deletePost = (id: string) => {
    if (!confirm('Delete this post?')) return
    setPosts(posts.filter((p) => p.id !== id))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Posts</h1>
          <p className="text-gray-600">Manage your scheduled and published content</p>
        </div>

        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        >
          <option value="all">All Posts</option>
          <option value="draft">Drafts</option>
          <option value="scheduled">Scheduled</option>
          <option value="published">Published</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {filteredPosts.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No posts found
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Content</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Platform</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Status</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Date</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPosts.map((post) => (
                <tr key={post.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <p className="text-sm text-gray-900 line-clamp-2 max-w-md">
                      {post.content}
                    </p>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm capitalize">{post.platform}</span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(post.status)}
                      <span className="text-sm">{getStatusText(post.status)}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {post.status === 'scheduled'
                      ? formatDate(post.scheduled_for)
                      : formatDate(post.published_at)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {post.platform_url && (
                        <a
                          href={post.platform_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1 hover:bg-gray-200 rounded"
                          title="View on platform"
                        >
                          <ExternalLink className="w-4 h-4 text-gray-600" />
                        </a>
                      )}
                      {post.status !== 'published' && (
                        <>
                          <button
                            className="p-1 hover:bg-gray-200 rounded"
                            title="Edit"
                          >
                            <Edit2 className="w-4 h-4 text-gray-600" />
                          </button>
                          <button
                            onClick={() => deletePost(post.id)}
                            className="p-1 hover:bg-red-100 rounded"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4 text-red-600" />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
