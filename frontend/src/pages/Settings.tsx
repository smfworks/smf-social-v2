import { useState } from 'react'
import { Save } from 'lucide-react'

export function Settings() {
  const [settings, setSettings] = useState({
    tenantName: 'SMF Works',
    timezone: 'America/New_York',
    defaultBoard: '',
  })

  const handleSave = () => {
    // TODO: API call
    alert('Settings saved!')
  }

  return (
    <div className="max-w-2xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Manage your account preferences</p>
      </div>

      <div className="bg-white p-6 rounded-lg border border-gray-200 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Organization Name
          </label>
          <input
            type="text"
            value={settings.tenantName}
            onChange={(e) => setSettings({ ...settings, tenantName: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Timezone
          </label>
          <select
            value={settings.timezone}
            onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="America/New_York">Eastern Time (ET)</option>
            <option value="America/Chicago">Central Time (CT)</option>
            <option value="America/Denver">Mountain Time (MT)</option>
            <option value="America/Los_Angeles">Pacific Time (PT)</option>
            <option value="UTC">UTC</option>
          </select>
        </div>

        <div className="pt-4">
          <button
            onClick={handleSave}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Save className="w-4 h-4" />
            Save Changes
          </button>
        </div>
      </div>

      <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
        <h3 className="font-semibold text-gray-900 mb-2">OAuth Apps</h3>
        <p className="text-sm text-gray-600">
          Manage your OAuth app credentials for each platform.
          <a href="/integrations" className="text-blue-600 hover:underline">
            Go to Integrations →
          </a>
        </p>
      </div>
    </div>
  )
}
