'use client'

import { useState } from 'react'
import { Sparkles, Loader2 } from 'lucide-react'

interface ProcessButtonProps {
  disabled: boolean
  onProcess: () => Promise<void>
}

export default function ProcessButton({ disabled, onProcess }: ProcessButtonProps) {
  const [isProcessing, setIsProcessing] = useState(false)

  const handleClick = async () => {
    if (disabled || isProcessing) return
    
    setIsProcessing(true)
    try {
      await onProcess()
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <button
      onClick={handleClick}
      disabled={disabled || isProcessing}
      className={`
        relative group inline-flex items-center px-8 py-4 rounded-2xl font-semibold text-lg transition-all duration-300 transform
        ${disabled || isProcessing
          ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
          : 'bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white hover:from-blue-700 hover:via-indigo-700 hover:to-purple-700 hover:scale-105 hover:shadow-2xl shadow-lg'
        }
        ${!disabled && !isProcessing ? 'hover:shadow-blue-500/25' : ''}
      `}
    >
      {/* Background animation */}
      {!disabled && !isProcessing && (
        <div className="absolute inset-0 bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 rounded-2xl opacity-0 group-hover:opacity-20 transition-opacity duration-300" />
      )}
      
      {/* Icon and text */}
      <div className="relative flex items-center">
        {isProcessing ? (
          <>
            <Loader2 className="w-6 h-6 mr-3 animate-spin" />
            <span>Processando com IA...</span>
          </>
        ) : (
          <>
            <Sparkles className="w-6 h-6 mr-3" />
            <span>Gerar Sentença</span>
            {!disabled && (
              <div className="ml-2 px-2 py-1 bg-white/20 rounded-lg text-sm font-normal">
                IA
              </div>
            )}
          </>
        )}
      </div>
      
      {/* Shine effect */}
      {!disabled && !isProcessing && (
        <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 transform -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
        </div>
      )}
    </button>
  )
}