'use client'

import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

interface LogEntry {
  id: number
  timestamp: string
  type: 'info' | 'warning' | 'error' | 'success'
  message: string
}

export default function Terminal() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [command, setCommand] = useState('')
  const terminalRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Initialize with some sample logs
    const initialLogs: LogEntry[] = [
      {
        id: 1,
        timestamp: new Date().toISOString(),
        type: 'info',
        message: 'Mining Fleet Management System initialized'
      },
      {
        id: 2,
        timestamp: new Date().toISOString(),
        type: 'success',
        message: 'Connected to simulation engine'
      },
      {
        id: 3,
        timestamp: new Date().toISOString(),
        type: 'info',
        message: 'Fleet status: 30 trucks online'
      }
    ]
    setLogs(initialLogs)
  }, [])

  useEffect(() => {
    // Auto-scroll to bottom when new logs are added
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [logs])

  const handleCommand = (e: React.FormEvent) => {
    e.preventDefault()
    if (!command.trim()) return

    // Add user command to logs
    const userLog: LogEntry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      type: 'info',
      message: `> ${command}`
    }

    // Simulate command processing
    let responseLog: LogEntry
    switch (command.toLowerCase()) {
      case 'status':
        responseLog = {
          id: Date.now() + 1,
          timestamp: new Date().toISOString(),
          type: 'success',
          message: 'System operational: 30 trucks active, 6 shovels online'
        }
        break
      case 'help':
        responseLog = {
          id: Date.now() + 1,
          timestamp: new Date().toISOString(),
          type: 'info',
          message: 'Available commands: status, help, clear, production, fleet'
        }
        break
      case 'clear':
        setLogs([])
        setCommand('')
        return
      case 'production':
        responseLog = {
          id: Date.now() + 1,
          timestamp: new Date().toISOString(),
          type: 'success',
          message: 'Production today: 1,250t ore, 800t waste'
        }
        break
      case 'fleet':
        responseLog = {
          id: Date.now() + 1,
          timestamp: new Date().toISOString(),
          type: 'info',
          message: 'Fleet: 16x 200t trucks, 14x 180t trucks - Utilization: 85%'
        }
        break
      default:
        responseLog = {
          id: Date.now() + 1,
          timestamp: new Date().toISOString(),
          type: 'error',
          message: `Unknown command: ${command}. Type 'help' for available commands.`
        }
    }

    setLogs(prev => [...prev, userLog, responseLog])
    setCommand('')
  }

  const getTypeColor = (type: LogEntry['type']) => {
    switch (type) {
      case 'error':
        return 'text-red-400'
      case 'warning':
        return 'text-yellow-400'
      case 'success':
        return 'text-green-400'
      default:
        return 'text-gray-300'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-gray-900 border border-gray-700 rounded-lg p-4 h-96 flex flex-col"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">System Terminal</h3>
        <button
          onClick={() => setLogs([])}
          className="text-sm text-gray-400 hover:text-white transition-colors"
        >
          Clear
        </button>
      </div>

      <div
        ref={terminalRef}
        className="flex-1 overflow-y-auto space-y-1 mb-4 font-mono text-sm"
      >
        {logs.map((log) => (
          <div key={log.id} className="flex gap-2">
            <span className="text-gray-500 text-xs min-w-fit">
              {formatTimestamp(log.timestamp)}
            </span>
            <span className={getTypeColor(log.type)}>
              {log.message}
            </span>
          </div>
        ))}
      </div>

      <form onSubmit={handleCommand} className="flex gap-2">
        <span className="text-green-400 font-mono">$</span>
        <input
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="Enter command..."
          className="flex-1 bg-transparent border-none outline-none text-white font-mono"
          autoFocus
        />
      </form>
    </motion.div>
  )
}