'use client'

import { useState, useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import Terminal from './components/Terminal'

interface SimulationData {
  trucks: Array<{
    id: number
    status: string
    load: number
    position: { x: number; y: number }
  }>
  shovels: Array<{
    id: number
    queue: number
    efficiency: number
  }>
  production: {
    ore: number
    waste: number
  }
}

export default function HomePage() {
  const [simulationData, setSimulationData] = useState<SimulationData | null>(null)
  const [currentView, setCurrentView] = useState<'dashboard' | 'terminal'>('dashboard')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate data loading to prevent hydration mismatch
    setIsLoading(false)
    setSimulationData({
      trucks: [
        { id: 1, status: 'loading', load: 0, position: { x: 100, y: 200 } },
        { id: 2, status: 'moving', load: 180, position: { x: 300, y: 150 } },
        { id: 3, status: 'dumping', load: 200, position: { x: 500, y: 100 } },
      ],
      shovels: [
        { id: 1, queue: 2, efficiency: 0.85 },
        { id: 2, queue: 1, efficiency: 0.92 },
        { id: 3, queue: 0, efficiency: 0.78 },
      ],
      production: {
        ore: 1250,
        waste: 800,
      },
    })
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div>Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">Vivania Mining FMS</h1>
          <nav className="flex space-x-4">
            <button
              onClick={() => setCurrentView('dashboard')}
              className={`px-4 py-2 rounded ${
                currentView === 'dashboard' ? 'bg-blue-600' : 'bg-gray-600'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setCurrentView('terminal')}
              className={`px-4 py-2 rounded ${
                currentView === 'terminal' ? 'bg-blue-600' : 'bg-gray-600'
              }`}
            >
              Terminal
            </button>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6">
        <AnimatePresence mode="wait">
          {currentView === 'dashboard' && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <DashboardView simulationData={simulationData} />
            </motion.div>
          )}
          {currentView === 'terminal' && (
            <motion.div
              key="terminal"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <Terminal />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}

function DashboardView({ simulationData }: { simulationData: SimulationData | null }) {
  if (!simulationData) return <div>No data available</div>

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-gray-800 p-6 rounded-lg">
        <h2 className="text-xl font-semibold mb-4">Fleet Status</h2>
        <div className="space-y-3">
          {simulationData.trucks.map((truck) => (
            <div key={truck.id} className="flex justify-between items-center">
              <span>Truck {truck.id}</span>
              <span className="text-sm text-gray-400">{truck.status}</span>
              <span className="text-sm">{truck.load}t</span>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gray-800 p-6 rounded-lg">
        <h2 className="text-xl font-semibold mb-4">Production</h2>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span>Ore:</span>
            <span className="text-green-400">{simulationData.production.ore}t</span>
          </div>
          <div className="flex justify-between">
            <span>Waste:</span>
            <span className="text-yellow-400">{simulationData.production.waste}t</span>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 p-6 rounded-lg">
        <h2 className="text-xl font-semibold mb-4">Shovels</h2>
        <div className="space-y-3">
          {simulationData.shovels.map((shovel) => (
            <div key={shovel.id} className="flex justify-between items-center">
              <span>Shovel {shovel.id}</span>
              <span className="text-sm text-gray-400">Queue: {shovel.queue}</span>
              <span className="text-sm">{Math.round(shovel.efficiency * 100)}%</span>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gray-800 p-6 rounded-lg">
        <h2 className="text-xl font-semibold mb-4">System Status</h2>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span>Active Trucks:</span>
            <span className="text-green-400">{simulationData.trucks.length}</span>
          </div>
          <div className="flex justify-between">
            <span>System Health:</span>
            <span className="text-green-400">Operational</span>
          </div>
        </div>
      </div>
    </div>
  )
}