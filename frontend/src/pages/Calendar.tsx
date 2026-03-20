import { Calendar as CalendarIcon } from 'lucide-react'

export function Calendar() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Calendar</h1>
      <p className="text-gray-600 mt-4">Calendar view coming soon. Use Posts list for now.</p>
      <div className="mt-8 p-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 flex flex-col items-center">
        <CalendarIcon className="w-12 h-12 text-gray-400 mb-4" />
        <p className="text-gray-500">Calendar visualization</p>
      </div>
    </div>
  )
}
