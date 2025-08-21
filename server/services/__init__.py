"""
Serviços de processamento de IA para geração de sentenças judiciais
Inclui novos serviços de instâncias isoladas para evitar contaminação entre casos
PARTE B: RAG Otimizado e Contextual implementado
"""

from .gemini_processor import GeminiProcessor, ProcessoEstruturado
from .whisper_service import WhisperService, TranscricaoAudiencia
from .rag_service import RAGService
from .claude_service import ClaudeService
from .instance_manager import InstanceManager
from .isolated_rag_service import IsolatedRAGService

# PARTE B: Componentes RAG Otimizado
from .optimized_embedding_service import OptimizedEmbeddingService, EmbeddingResult
from .semantic_chunker import SemanticChunker, SemanticChunk, ChunkType
from .contextual_retriever import ContextualRetriever, QueryContext, QueryType, RetrievalResult
from .enhanced_rag_service import EnhancedRAGService

# MÓDULO 2: Diálogo Inteligente Avançado
from .intelligent_dialogue_service import IntelligentDialogueService

__all__ = [
    # Core services
    'GeminiProcessor',
    'ProcessoEstruturado',
    'WhisperService', 
    'TranscricaoAudiencia',
    'RAGService',
    'ClaudeService',
    
    # Instâncias isoladas
    'InstanceManager',
    'IsolatedRAGService',
    
    # RAG Otimizado (PARTE B)
    'OptimizedEmbeddingService',
    'EmbeddingResult',
    'SemanticChunker',
    'SemanticChunk',
    'ChunkType',
    'ContextualRetriever',
    'QueryContext',
    'QueryType',
    'RetrievalResult',
    'EnhancedRAGService',
    
    # MÓDULO 2: Diálogo Inteligente
    'IntelligentDialogueService'
]
