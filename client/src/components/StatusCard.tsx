'use client'

import { CheckCircle, Clock, AlertCircle, Loader2 } from 'lucide-react'

export type TaskStatus = 'pending' | 'running' | 'completed' | 'error'

interface Task {
  id: string
  name: string
  status: TaskStatus
  message?: string
}

interface StatusCardProps {
  tasks: Task[]
  currentStep?: string
}

export default function StatusCard({ tasks, currentStep }: StatusCardProps) {
  const getStatusIcon = (status: TaskStatus) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'running':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />
      default:
        return <Clock className="w-5 h-5 text-gray-400" />
    }
  }

  const getStatusText = (status: TaskStatus) => {
    switch (status) {
      case 'completed':
        return 'Concluído'
      case 'running':
        return 'Executando...'
      case 'error':
        return 'Erro'
      default:
        return 'Aguardando'
    }
  }

  const completedTasks = tasks.filter(t => t.status === 'completed').length
  const totalTasks = tasks.length
  const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0

  return (
    <div className="w-full max-w-2xl mx-auto bg-white rounded-lg border shadow-sm p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Status do Processamento
        </h3>
        
        {currentStep && (
          <p className="text-sm text-blue-600 mb-4">
            📋 {currentStep}
          </p>
        )}
        
        {/* Barra de Progresso */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
          <div
            className={`bg-blue-600 h-2 rounded-full progress-bar`}
            style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
          />
        </div>
        
        <p className="text-sm text-gray-600">
          Progresso: {completedTasks}/{totalTasks} ({Math.round(progress)}%)
        </p>
      </div>

      {/* Lista de Tarefas */}
      <div className="space-y-3">
        {tasks.map((task) => (
          <div
            key={task.id}
            className={`
              flex items-center justify-between p-3 rounded-lg border transition-all
              ${task.status === 'running' ? 'bg-blue-50 border-blue-200' : ''}
              ${task.status === 'completed' ? 'bg-green-50 border-green-200' : ''}
              ${task.status === 'error' ? 'bg-red-50 border-red-200' : ''}
              ${task.status === 'pending' ? 'bg-gray-50 border-gray-200' : ''}
            `}
          >
            <div className="flex items-center space-x-3">
              {getStatusIcon(task.status)}
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {task.name}
                </p>
                {task.message && (
                  <p className="text-xs text-gray-500 mt-1">
                    {task.message}
                  </p>
                )}
              </div>
            </div>
            
            <span className={`
              text-xs font-medium px-2 py-1 rounded-full
              ${task.status === 'running' ? 'bg-blue-100 text-blue-800' : ''}
              ${task.status === 'completed' ? 'bg-green-100 text-green-800' : ''}
              ${task.status === 'error' ? 'bg-red-100 text-red-800' : ''}
              ${task.status === 'pending' ? 'bg-gray-100 text-gray-800' : ''}
            `}>
              {getStatusText(task.status)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}