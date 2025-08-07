'use client'

import { useState } from 'react'
import { Scale, Sparkles } from 'lucide-react'
import UploadZone from '@/components/UploadZone'
import ProcessButton from '@/components/ProcessButton'
import StatusCard, { TaskStatus } from '@/components/StatusCard'

interface UploadedFile {
  file: File
  type: 'processo' | 'audiencia'
  id: string
}

interface Task {
  id: string
  name: string
  status: TaskStatus
  message?: string
}

export default function Home() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [tasks, setTasks] = useState<Task[]>([])
  const [currentStep, setCurrentStep] = useState<string>('')

  const initializeTasks = () => {
    const newTasks: Task[] = [
      { id: '1', name: 'Análise de documentos', status: 'pending' },
      { id: '2', name: 'Transcrição de áudio', status: 'pending' },
      { id: '3', name: 'Extração de informações', status: 'pending' },
      { id: '4', name: 'Consulta de jurisprudência', status: 'pending' },
      { id: '5', name: 'Geração da sentença', status: 'pending' },
    ]
    setTasks(newTasks)
  }

  const updateTaskStatus = (taskId: string, status: TaskStatus, message?: string) => {
    setTasks(prevTasks =>
      prevTasks.map(task =>
        task.id === taskId ? { ...task, status, message } : task
      )
    )
  }

  const simulateProcessing = async () => {
    const steps = [
      { id: '1', name: 'Analisando documentos...', duration: 2000 },
      { id: '2', name: 'Transcrevendo áudio...', duration: 3000 },
      { id: '3', name: 'Extraindo informações...', duration: 2500 },
      { id: '4', name: 'Consultando jurisprudência...', duration: 2000 },
      { id: '5', name: 'Gerando sentença...', duration: 3000 },
    ]

    for (const step of steps) {
      setCurrentStep(step.name)
      updateTaskStatus(step.id, 'running', step.name)
      
      await new Promise(resolve => setTimeout(resolve, step.duration))
      
      updateTaskStatus(step.id, 'completed', 'Concluído')
    }
    
    setCurrentStep('Sentença gerada com sucesso! 🎉')
  }

  const handleProcess = async () => {
    setIsProcessing(true)
    initializeTasks()
    
    try {
      await simulateProcessing()
    } catch (error) {
      console.error('Erro no processamento:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  const hasFiles = uploadedFiles.length > 0
  const hasProcesso = uploadedFiles.some(f => f.type === 'processo')
  const hasAudiencia = uploadedFiles.some(f => f.type === 'audiencia')

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header Moderno */}
      <header className="bg-white/80 backdrop-blur-md shadow-sm border-b border-white/20 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl shadow-lg">
                <Scale className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                  AutoSentença IA
                </h1>
                <p className="text-sm text-gray-600 flex items-center space-x-1">
                  <Sparkles className="w-4 h-4" />
                  <span>Powered by AI • Versão 1.0</span>
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 text-sm">
              <div className="flex items-center space-x-2 px-3 py-2 bg-green-50 border border-green-200 rounded-lg">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-green-700 font-medium">Sistema Online</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="space-y-12">
          
          {/* Hero Section */}
          <div className="text-center space-y-6">
            <div className="space-y-4">
              <h2 className="text-4xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-indigo-800 bg-clip-text text-transparent">
                Gere Sentenças Judiciais
              </h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Transforme documentos processuais e gravações de audiência em minutas de sentença profissionais usando inteligência artificial avançada.
              </p>
            </div>
            
            <div className="flex items-center justify-center space-x-8 text-sm text-gray-500">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span>Análise Automática</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-emerald-400 rounded-full"></div>
                <span>Transcrição IA</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                <span>Jurisprudência Atualizada</span>
              </div>
            </div>
          </div>

          {/* Upload Section */}
          <div className="bg-white/70 backdrop-blur-sm rounded-3xl border border-white/20 shadow-xl p-8">
            <div className="text-center mb-8">
              <h3 className="text-2xl font-semibold text-gray-900 mb-2">
                Envie os Arquivos do Caso
              </h3>
              <p className="text-gray-600">
                Adicione um documento do processo e uma gravação da audiência para começar
              </p>
            </div>
            
            <UploadZone onFilesChange={setUploadedFiles} />
          </div>

          {/* Process Button */}
          {hasFiles && (
            <div className="bg-white/70 backdrop-blur-sm rounded-3xl border border-white/20 shadow-xl p-8">
              <div className="text-center space-y-6">
                <div className="space-y-2">
                  <h3 className="text-2xl font-semibold text-gray-900">
                    Pronto para Processar
                  </h3>
                  <div className="flex items-center justify-center space-x-6 text-sm">
                    {hasProcesso && (
                      <div className="flex items-center space-x-2 text-green-600">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="font-medium">Documento do processo carregado</span>
                      </div>
                    )}
                    {hasAudiencia && (
                      <div className="flex items-center space-x-2 text-green-600">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="font-medium">Gravação da audiência carregada</span>
                      </div>
                    )}
                  </div>
                </div>
                
                <ProcessButton
                  disabled={!hasFiles || isProcessing}
                  onProcess={handleProcess}
                />
              </div>
            </div>
          )}

          {/* Status Card */}
          {tasks.length > 0 && (
            <div className="bg-white/70 backdrop-blur-sm rounded-3xl border border-white/20 shadow-xl p-8">
              <StatusCard tasks={tasks} currentStep={currentStep} />
            </div>
          )}

          {/* Results Section */}
          {tasks.length > 0 && tasks.every(t => t.status === 'completed') && (
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-3xl shadow-xl p-8">
              <div className="text-center space-y-6">
                <div className="space-y-4">
                  <div className="mx-auto w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center shadow-lg">
                    <Sparkles className="w-10 h-10 text-white" />
                  </div>
                  
                  <div className="space-y-2">
                    <h3 className="text-3xl font-bold text-gray-900">
                      Sentença Gerada!
                    </h3>
                    <p className="text-lg text-gray-600">
                      Sua minuta de sentença foi criada com sucesso e está pronta para revisão
                    </p>
                  </div>
                </div>
                
                <div className="flex justify-center space-x-4">
                  <button className="inline-flex items-center px-6 py-3 bg-white border border-gray-300 rounded-xl text-gray-700 font-medium hover:bg-gray-50 transition-colors duration-200 shadow-sm">
                    <Scale className="w-5 h-5 mr-2" />
                    Visualizar Sentença
                  </button>
                  <button className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-medium hover:from-green-700 hover:to-emerald-700 transition-all duration-200 shadow-lg">
                    <Sparkles className="w-5 h-5 mr-2" />
                    Download DOCX
                  </button>
                </div>
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  )
}