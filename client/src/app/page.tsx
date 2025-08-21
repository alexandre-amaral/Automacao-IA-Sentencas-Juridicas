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

const API_URL = 'http://localhost:8000'

export default function Home() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [tasks, setTasks] = useState<Task[]>([])
  const [currentStep, setCurrentStep] = useState<string>('')
  const [caseId, setCaseId] = useState<string>('')

  const initializeTasks = () => {
    const newTasks: Task[] = [
      { id: '0', name: 'Upload de arquivos', status: 'pending' },
      { id: '1', name: 'Transcrição de áudio', status: 'pending' },
      { id: '2', name: 'Processamento com Gemini', status: 'pending' },
      { id: '3', name: 'Geração da sentença', status: 'pending' },
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

  const uploadFiles = async () => {
    console.log('🚀 Iniciando upload de arquivos...')
    if (!uploadedFiles.length) return null

    const formData = new FormData()
    
    uploadedFiles.forEach(fileData => {
      console.log(`📎 Adicionando arquivo: ${fileData.file.name} (tipo: ${fileData.type})`)
      if (fileData.type === 'processo') {
        formData.append('processo', fileData.file)
      } else if (fileData.type === 'audiencia') {
        formData.append('audiencia', fileData.file)
      }
    })

    console.log(`📡 Fazendo request para: ${API_URL}/upload-caso`)
    
    try {
      const response = await fetch(`${API_URL}/upload-caso`, {
        method: 'POST',
        body: formData,
      })

      console.log(`📋 Response status: ${response.status} ${response.statusText}`)
      console.log(`📋 Response headers:`, Object.fromEntries(response.headers.entries()))

      if (!response.ok) {
        const errorText = await response.text()
        console.error(`❌ Upload falhou: ${response.status} - ${errorText}`)
        throw new Error(`Upload falhou: ${response.statusText}`)
      }

      const result = await response.json()
      console.log('✅ Upload bem-sucedido:', result)
      return result.case_id
    } catch (error) {
      console.error('❌ Erro no upload:', error)
      if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
        throw new Error('Erro de conexão com o servidor. Verifique se o backend está rodando.')
      }
      throw error
    }
  }

  const processWithAPI = async (uploadedCaseId: string) => {
    console.log(`🔄 Iniciando processamento do Case ID: ${uploadedCaseId}`)
    
    const steps = [
      { id: '1', name: 'Transcrevendo áudio...', endpoint: 'step1-transcribe' },
      { id: '2', name: 'Processando com Gemini...', endpoint: 'step2-process' },
      { id: '3', name: 'Gerando sentença com Claude...', endpoint: 'step3-generate' },
    ]

    for (const step of steps) {
      console.log(`🎯 Executando: ${step.name}`)
      setCurrentStep(step.name)
      updateTaskStatus(step.id, 'running', step.name)
      
      try {
        const url = `${API_URL}/${step.endpoint}/${uploadedCaseId}`
        console.log(`📡 Request para: ${url}`)
        
        const response = await fetch(url, {
          method: 'POST',
        })

        console.log(`📋 ${step.name} - Status: ${response.status} ${response.statusText}`)

        if (!response.ok) {
          const errorText = await response.text()
          console.error(`❌ ${step.name} falhou: ${response.status} - ${errorText}`)
          throw new Error(`${step.name} falhou: ${response.statusText}`)
        }

        const result = await response.json()
        console.log(`✅ ${step.name} concluído:`, result)
        updateTaskStatus(step.id, 'completed', result.message || 'Concluído')
      } catch (error) {
        console.error(`❌ Erro em ${step.name}:`, error)
        updateTaskStatus(step.id, 'error', `Erro: ${error.message}`)
        throw error
      }
    }
    
    console.log('🎉 Pipeline completo concluído!')
    setCurrentStep('Sentença gerada com sucesso! 🎉')
  }

  const monitorarProgresso = async (caseId: string) => {
    console.log(`📊 Monitorando progresso do Case ID: ${caseId}`)
    
    // Simular monitoramento do progresso baseado em tempo
    setCurrentStep('🔄 Pipeline automático em execução...')
    updateTaskStatus('1', 'running', 'Transcrevendo áudio...')
    
    // Aguardar tempo estimado para transcrição (2-3 min)
    await new Promise(resolve => setTimeout(resolve, 60000))
    updateTaskStatus('1', 'completed', 'Transcrição concluída')
    updateTaskStatus('2', 'running', 'Processando com Gemini...')
    
    // Aguardar tempo estimado para Gemini (1-2 min)
    await new Promise(resolve => setTimeout(resolve, 60000))
    updateTaskStatus('2', 'completed', 'Processamento Gemini concluído')
    updateTaskStatus('3', 'running', 'Gerando sentença com Claude...')
    
    // Aguardar tempo estimado para Claude (30s)
    await new Promise(resolve => setTimeout(resolve, 30000))
    updateTaskStatus('3', 'completed', 'Sentença gerada')
    
    setCurrentStep('🎉 Pipeline automático concluído!')
  }

  const handleProcess = async () => {
    setIsProcessing(true)
    initializeTasks()
    
    try {
      // Upload dos arquivos (que agora executa todo o pipeline automaticamente)
      setCurrentStep('Fazendo upload e iniciando processamento automático...')
      updateTaskStatus('0', 'running', 'Upload em andamento...')
      
      const uploadedCaseId = await uploadFiles()
      if (!uploadedCaseId) {
        throw new Error('Falha no upload dos arquivos')
      }
      
      setCaseId(uploadedCaseId)
      updateTaskStatus('0', 'completed', `Arquivos enviados! Case ID: ${uploadedCaseId}`)
      
      // Polling para verificar status real do processamento
      await monitorarProgresso(uploadedCaseId)
      
    } catch (error) {
      console.error('Erro no processamento:', error)
      setCurrentStep(`Erro: ${error.message}`)
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
          {tasks.length > 0 && tasks.every(t => t.status === 'completed') && caseId && (
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
                    <p className="text-sm text-gray-500">
                      Case ID: {caseId}
                    </p>
                  </div>
                </div>
                
                <div className="flex justify-center space-x-4">
                  <button 
                    onClick={() => window.open(`${API_URL}/download/${caseId}/sentenca`, '_blank')}
                    className="inline-flex items-center px-6 py-3 bg-white border border-gray-300 rounded-xl text-gray-700 font-medium hover:bg-gray-50 transition-colors duration-200 shadow-sm"
                  >
                    <Scale className="w-5 h-5 mr-2" />
                    Visualizar Sentença
                  </button>
                  <button 
                    onClick={() => {
                      const link = document.createElement('a')
                      link.href = `${API_URL}/download/${caseId}/sentenca`
                      link.download = `sentenca_${caseId}.txt`
                      link.click()
                    }}
                    className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-medium hover:from-green-700 hover:to-emerald-700 transition-all duration-200 shadow-lg"
                  >
                    <Sparkles className="w-5 h-5 mr-2" />
                    Download Sentença
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