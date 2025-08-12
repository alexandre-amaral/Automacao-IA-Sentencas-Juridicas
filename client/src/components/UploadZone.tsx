'use client'

import { useState, useCallback } from 'react'
import { Upload, FileText, Music, X, CheckCircle, AlertTriangle } from 'lucide-react'

interface UploadedFile {
  file: File
  type: 'processo' | 'audiencia'
  id: string
}

interface UploadZoneProps {
  onFilesChange: (files: UploadedFile[]) => void
}

interface ModernDropZoneProps {
  type: 'processo' | 'audiencia'
  onDrop: (file: File, type: 'processo' | 'audiencia') => void
  file: UploadedFile | null
  onRemoveFile: () => void
}

function ModernDropZone({ type, onDrop, file, onRemoveFile }: ModernDropZoneProps) {
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState<string>('')

  const isProcesso = type === 'processo'
  const acceptedFormats = isProcesso ? ['.pdf', '.docx', '.doc'] : ['.mp4', '.mp3', '.wav', '.m4a', '.aac']
  const acceptString = isProcesso ? acceptedFormats.join(',') : 'video/mp4,audio/mp3,audio/wav,audio/m4a,audio/aac,.mp4,.mp3,.wav,.m4a,.aac'

  const validateFile = (file: File): boolean => {
    const extension = file.name.split('.').pop()?.toLowerCase()
    if (!extension) return false

    const validExtensions = isProcesso 
      ? ['pdf', 'docx', 'doc'] 
      : ['mp4', 'mp3', 'wav', 'm4a', 'aac']
    
    return validExtensions.includes(extension)
  }

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    setError('')
    
    const droppedFiles = Array.from(e.dataTransfer.files)
    if (droppedFiles.length === 0) return

    const droppedFile = droppedFiles[0] // Pegar apenas o primeiro arquivo
    
    if (validateFile(droppedFile)) {
      onDrop(droppedFile, type)
    } else {
      setError(`Formato inválido. Use: ${acceptedFormats.join(', ').toUpperCase()}`)
      setTimeout(() => setError(''), 4000)
    }
  }, [onDrop, type, acceptedFormats])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setError('')
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      
      if (validateFile(selectedFile)) {
        onDrop(selectedFile, type)
      } else {
        setError(`Formato inválido. Use: ${acceptedFormats.join(', ').toUpperCase()}`)
        setTimeout(() => setError(''), 4000)
      }
    }
  }, [onDrop, type, acceptedFormats])

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const config = {
    processo: {
      title: 'Documento do Processo',
      description: 'Arrastar arquivo PDF ou DOCX',
      icon: FileText,
      color: 'blue',
      gradient: 'from-blue-500 to-indigo-600',
      bgGradient: 'from-blue-50 to-indigo-50',
      borderColor: 'border-blue-200',
      hoverBorder: 'hover:border-blue-400',
      dragBorder: 'border-blue-500',
      dragBg: 'bg-blue-100',
    },
    audiencia: {
      title: 'Gravação da Audiência',
      description: 'Arrastar arquivo MP3 ou WAV',
      icon: Music,
      color: 'emerald',
      gradient: 'from-emerald-500 to-teal-600',
      bgGradient: 'from-emerald-50 to-teal-50',
      borderColor: 'border-emerald-200',
      hoverBorder: 'hover:border-emerald-400',
      dragBorder: 'border-emerald-500',
      dragBg: 'bg-emerald-100',
    }
  }

  const conf = config[type]
  const Icon = conf.icon

  return (
    <div className="space-y-4">
      {/* Zona de Upload */}
      <div
        className={`
          relative group transition-all duration-300 ease-in-out transform hover:scale-[1.02]
          ${file ? 'scale-95' : ''}
        `}
      >
        <div
          className={`
            relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300
            ${dragActive 
              ? `${conf.dragBorder} ${conf.dragBg} shadow-lg` 
              : error
                ? 'border-red-400 bg-red-50'
                : file
                  ? `${conf.borderColor} bg-gradient-to-br ${conf.bgGradient}`
                  : `${conf.borderColor} ${conf.hoverBorder} bg-gradient-to-br ${conf.bgGradient} hover:shadow-md`
            }
            ${!file ? 'min-h-[200px] flex items-center justify-center' : 'min-h-[160px]'}
          `}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {!file && (
            <input
              type="file"
              accept={acceptString}
              onChange={handleFileInput}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              aria-label={`Selecionar arquivo de ${type}`}
              title={`Clique para selecionar arquivo de ${type}`}
            />
          )}
          
          {/* Estado sem arquivo */}
          {!file && (
            <div className="space-y-6">
              <div className={`mx-auto w-20 h-20 rounded-full bg-gradient-to-br ${conf.gradient} flex items-center justify-center shadow-lg`}>
                <Icon className="w-10 h-10 text-white" />
              </div>
              
              <div className="space-y-2">
                <h3 className="text-xl font-semibold text-gray-900">
                  {conf.title}
                </h3>
                <p className="text-gray-600">
                  {conf.description}
                </p>
                <p className="text-sm text-gray-500">
                  ou clique para selecionar
                </p>
              </div>
              
              <div className="flex items-center justify-center space-x-2">
                <Upload className="w-5 h-5 text-gray-400" />
                <span className="text-sm font-medium text-gray-500">
                  {acceptedFormats.join(', ').toUpperCase()}
                </span>
              </div>
            </div>
          )}

          {/* Estado com arquivo */}
          {file && (
            <div className="space-y-4">
              <div className="flex items-center justify-center space-x-3">
                <div className={`p-3 rounded-full bg-gradient-to-br ${conf.gradient} shadow-lg`}>
                  <Icon className="w-8 h-8 text-white" />
                </div>
                <CheckCircle className="w-8 h-8 text-green-500" />
              </div>
              
              <div className="space-y-2">
                <h4 className="font-semibold text-gray-900">
                  {conf.title}
                </h4>
                <p className="text-sm font-medium text-gray-700 truncate max-w-xs mx-auto">
                  {file.file.name}
                </p>
                <p className="text-xs text-gray-500">
                  {formatFileSize(file.file.size)}
                </p>
              </div>
              
              <button
                onClick={onRemoveFile}
                className="inline-flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors duration-200"
                aria-label={`Remover arquivo ${file.file.name}`}
              >
                <X className="w-4 h-4" />
                <span className="text-sm font-medium">Remover</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Mensagem de Erro */}
      {error && (
        <div className="flex items-center space-x-3 p-4 bg-red-50 border border-red-200 rounded-xl">
          <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <p className="text-sm text-red-700 font-medium">{error}</p>
        </div>
      )}
    </div>
  )
}

export default function UploadZone({ onFilesChange }: UploadZoneProps) {
  const [processoFile, setProcessoFile] = useState<UploadedFile | null>(null)
  const [audienciaFile, setAudienciaFile] = useState<UploadedFile | null>(null)

  const handleDrop = (file: File, type: 'processo' | 'audiencia') => {
    const newFile: UploadedFile = {
      file,
      type,
      id: Math.random().toString(36).substr(2, 9)
    }
    
    if (type === 'processo') {
      setProcessoFile(newFile)
    } else {
      setAudienciaFile(newFile)
    }
    
    // Atualizar lista completa
    const allFiles = []
    if (type === 'processo') {
      allFiles.push(newFile)
      if (audienciaFile) allFiles.push(audienciaFile)
    } else {
      if (processoFile) allFiles.push(processoFile)
      allFiles.push(newFile)
    }
    
    onFilesChange(allFiles)
  }

  const removeProcessoFile = () => {
    setProcessoFile(null)
    const allFiles = audienciaFile ? [audienciaFile] : []
    onFilesChange(allFiles)
  }

  const removeAudienciaFile = () => {
    setAudienciaFile(null)
    const allFiles = processoFile ? [processoFile] : []
    onFilesChange(allFiles)
  }

  return (
    <div className="w-full max-w-5xl mx-auto p-6">
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Zona de Processo */}
        <ModernDropZone
          type="processo"
          onDrop={handleDrop}
          file={processoFile}
          onRemoveFile={removeProcessoFile}
        />

        {/* Zona de Audiência */}
        <ModernDropZone
          type="audiencia"
          onDrop={handleDrop}
          file={audienciaFile}
          onRemoveFile={removeAudienciaFile}
        />
      </div>

      {/* Status Geral */}
      {(processoFile || audienciaFile) && (
        <div className="mt-8 p-6 bg-white border border-gray-200 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              Status dos Arquivos
            </h3>
            <div className="flex items-center space-x-4 text-sm">
              <div className={`flex items-center space-x-2 ${processoFile ? 'text-green-600' : 'text-gray-400'}`}>
                <div className={`w-2 h-2 rounded-full ${processoFile ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span>Processo</span>
              </div>
              <div className={`flex items-center space-x-2 ${audienciaFile ? 'text-green-600' : 'text-gray-400'}`}>
                <div className={`w-2 h-2 rounded-full ${audienciaFile ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span>Audiência</span>
              </div>
            </div>
          </div>
          
          {!processoFile && (
            <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <p className="text-sm text-amber-700">
                📝 Para uma análise completa, recomendamos incluir um documento do processo
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}