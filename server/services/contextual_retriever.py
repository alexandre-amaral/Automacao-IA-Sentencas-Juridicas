"""
Recuperação Contextual Avançada para RAG Jurídico
Sistema inteligente de ranking e seleção de conhecimento relevante
"""

import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import re
from collections import defaultdict

from .semantic_chunker import SemanticChunk, ChunkType
from .optimized_embedding_service import OptimizedEmbeddingService, EmbeddingResult

class QueryType(Enum):
    """Tipos de query para otimização específica"""
    BUSCA_JURISPRUDENCIA = "jurisprudencia"
    ANALISE_FATOS = "fatos"
    FUNDAMENTACAO_LEGAL = "fundamentacao"
    ESTRUTURA_SENTENCA = "estrutura"
    ESTILO_REDACAO = "estilo"
    PROCEDIMENTO = "procedimento"
    GERAL = "geral"

@dataclass
class RetrievalResult:
    """Resultado de recuperação com score detalhado"""
    chunk: SemanticChunk
    relevance_score: float
    embedding_similarity: float
    context_bonus: float
    concept_match_score: float
    type_match_score: float
    final_rank: int
    explanation: str

@dataclass
class QueryContext:
    """Contexto da query para otimização"""
    query_text: str
    query_type: QueryType
    case_context: Dict[str, Any]
    required_concepts: List[str]
    preferred_chunk_types: List[ChunkType]
    temporal_context: Optional[str]
    
class ContextualRetriever:
    """Recuperador contextual inteligente"""
    
    def __init__(self, embedding_service: OptimizedEmbeddingService):
        self.logger = logging.getLogger(__name__)
        self.embedding_service = embedding_service
        
        # Pesos para diferentes aspectos do ranking
        self.ranking_weights = {
            "embedding_similarity": 0.4,
            "concept_match": 0.25,
            "type_match": 0.2,
            "context_bonus": 0.1,
            "priority_bonus": 0.05
        }
        
        # Boost por tipo de chunk para diferentes queries
        self.type_boost_matrix = {
            QueryType.BUSCA_JURISPRUDENCIA: {
                ChunkType.JURISPRUDENCIA: 0.3,
                ChunkType.CITACAO_LEGAL: 0.2,
                ChunkType.FUNDAMENTACAO: 0.1
            },
            QueryType.ANALISE_FATOS: {
                ChunkType.PROVA: 0.3,
                ChunkType.RELATÓRIO: 0.2,
                ChunkType.CONTEXTO: 0.1
            },
            QueryType.FUNDAMENTACAO_LEGAL: {
                ChunkType.FUNDAMENTACAO: 0.3,
                ChunkType.JURISPRUDENCIA: 0.2,
                ChunkType.CITACAO_LEGAL: 0.1
            },
            QueryType.ESTRUTURA_SENTENCA: {
                ChunkType.DISPOSITIVO: 0.3,
                ChunkType.FUNDAMENTACAO: 0.2,
                ChunkType.RELATÓRIO: 0.1
            },
            QueryType.ESTILO_REDACAO: {
                ChunkType.FUNDAMENTACAO: 0.2,
                ChunkType.DISPOSITIVO: 0.2,
                ChunkType.RELATÓRIO: 0.1
            }
        }
    
    def classify_query_type(self, query: str) -> QueryType:
        """Classifica automaticamente o tipo da query"""
        query_lower = query.lower()
        
        # Padrões para identificação de tipo
        patterns = {
            QueryType.BUSCA_JURISPRUDENCIA: [
                "jurisprudência", "súmula", "precedente", "acórdão", "decisão",
                "entendimento", "orientação jurisprudencial"
            ],
            QueryType.ANALISE_FATOS: [
                "fatos", "aconteceu", "prova", "testemunha", "depoimento",
                "evidência", "circunstância", "evento"
            ],
            QueryType.FUNDAMENTACAO_LEGAL: [
                "fundamentação", "base legal", "artigo", "lei", "norma",
                "fundamento", "amparo legal"
            ],
            QueryType.ESTRUTURA_SENTENCA: [
                "estrutura", "formato", "modelo", "template", "seção",
                "parte da sentença", "organização"
            ],
            QueryType.ESTILO_REDACAO: [
                "estilo", "linguagem", "redação", "forma de escrever",
                "padrão de escrita", "tom"
            ],
            QueryType.PROCEDIMENTO: [
                "procedimento", "processo", "tramitação", "etapa",
                "passo", "sequência"
            ]
        }
        
        for query_type, keywords in patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                return query_type
        
        return QueryType.GERAL
    
    def extract_required_concepts(self, query: str) -> List[str]:
        """Extrai conceitos obrigatórios da query"""
        concepts = []
        query_lower = query.lower()
        
        # Conceitos jurídicos fundamentais
        legal_terms = [
            "horas extras", "adicional noturno", "justa causa", "aviso prévio",
            "rescisão", "férias", "13º salário", "FGTS", "PIS", "dano moral",
            "equiparação salarial", "assédio moral", "acidente trabalho",
            "insalubridade", "periculosidade"
        ]
        
        for term in legal_terms:
            if term in query_lower:
                concepts.append(term)
        
        # Conceitos procedimentais
        procedural_terms = [
            "petição inicial", "contestação", "réplica", "audiência",
            "depoimento", "testemunha", "documento", "sentença"
        ]
        
        for term in procedural_terms:
            if term in query_lower:
                concepts.append(term)
        
        return concepts
    
    def create_query_context(self, 
                           query: str, 
                           case_data: Dict[str, Any] = None,
                           explicit_type: QueryType = None) -> QueryContext:
        """Cria contexto enriquecido para a query"""
        
        query_type = explicit_type or self.classify_query_type(query)
        required_concepts = self.extract_required_concepts(query)
        
        # Determinar tipos preferidos de chunk
        preferred_types = []
        if query_type in self.type_boost_matrix:
            boost_dict = self.type_boost_matrix[query_type]
            preferred_types = sorted(boost_dict.keys(), key=lambda x: boost_dict[x], reverse=True)
        
        return QueryContext(
            query_text=query,
            query_type=query_type,
            case_context=case_data or {},
            required_concepts=required_concepts,
            preferred_chunk_types=preferred_types,
            temporal_context=None
        )
    
    def calculate_concept_match_score(self, chunk: SemanticChunk, context: QueryContext) -> float:
        """Calcula score de match de conceitos"""
        if not context.required_concepts:
            return 0.0
        
        chunk_concepts = set(chunk.key_concepts)
        required_concepts = set(context.required_concepts)
        
        # Interseção de conceitos
        matched_concepts = chunk_concepts.intersection(required_concepts)
        
        if not matched_concepts:
            return 0.0
        
        # Score baseado na proporção de conceitos matched
        match_ratio = len(matched_concepts) / len(required_concepts)
        
        # Bonus para match completo
        complete_match_bonus = 0.2 if match_ratio == 1.0 else 0.0
        
        return min(1.0, match_ratio + complete_match_bonus)
    
    def calculate_type_match_score(self, chunk: SemanticChunk, context: QueryContext) -> float:
        """Calcula score de match de tipo"""
        if chunk.chunk_type in context.preferred_chunk_types:
            # Score baseado na posição na lista de preferência
            position = context.preferred_chunk_types.index(chunk.chunk_type)
            max_positions = len(context.preferred_chunk_types)
            
            return (max_positions - position) / max_positions
        
        return 0.0
    
    def calculate_context_bonus(self, chunk: SemanticChunk, context: QueryContext) -> float:
        """Calcula bonus contextual"""
        bonus = 0.0
        
        # Bonus por prioridade do chunk
        priority_bonus = chunk.priority / 10.0 * 0.3
        
        # Bonus por referências legais
        legal_ref_bonus = min(0.2, len(chunk.legal_references) * 0.05)
        
        # Bonus por contexto de caso
        case_bonus = 0.0
        if context.case_context:
            # Se há dados do caso atual, dar bonus para chunks relacionados
            case_concepts = context.case_context.get('conceitos_principais', [])
            if any(concept in chunk.content.lower() for concept in case_concepts):
                case_bonus = 0.2
        
        return priority_bonus + legal_ref_bonus + case_bonus
    
    def calculate_final_relevance(self, 
                                chunk: SemanticChunk,
                                embedding_similarity: float,
                                context: QueryContext) -> Tuple[float, str]:
        """Calcula relevância final com explicação"""
        
        # Componentes do score
        concept_score = self.calculate_concept_match_score(chunk, context)
        type_score = self.calculate_type_match_score(chunk, context)
        context_bonus = self.calculate_context_bonus(chunk, context)
        
        # Aplicar boost específico do tipo de query
        type_boost = 0.0
        if context.query_type in self.type_boost_matrix:
            type_boost = self.type_boost_matrix[context.query_type].get(chunk.chunk_type, 0.0)
        
        # Score final ponderado
        final_score = (
            embedding_similarity * self.ranking_weights["embedding_similarity"] +
            concept_score * self.ranking_weights["concept_match"] +
            type_score * self.ranking_weights["type_match"] +
            context_bonus * self.ranking_weights["context_bonus"] +
            type_boost
        )
        
        # Explicação detalhada
        explanation = f"Emb:{embedding_similarity:.2f} Conc:{concept_score:.2f} Tipo:{type_score:.2f} Ctx:{context_bonus:.2f} Boost:{type_boost:.2f}"
        
        return min(1.0, final_score), explanation
    
    def retrieve_relevant_chunks(self,
                               query_context: QueryContext,
                               available_chunks: List[SemanticChunk],
                               top_k: int = 10,
                               min_relevance: float = 0.1) -> List[RetrievalResult]:
        """Recupera chunks mais relevantes com ranking avançado"""
        
        if not available_chunks:
            return []
        
        # Criar embedding da query
        query_embedding = self.embedding_service.create_embedding(query_context.query_text)
        
        results = []
        
        for chunk in available_chunks:
            # Embedding do chunk
            chunk_embedding = self.embedding_service.create_embedding(chunk.content)
            
            # Similaridade básica
            embedding_similarity = self.embedding_service.compare_embeddings(
                query_embedding.embedding, 
                chunk_embedding.embedding
            )
            
            # Score contextual final
            final_score, explanation = self.calculate_final_relevance(
                chunk, embedding_similarity, query_context
            )
            
            # Filtrar por relevância mínima
            if final_score >= min_relevance:
                results.append(RetrievalResult(
                    chunk=chunk,
                    relevance_score=final_score,
                    embedding_similarity=embedding_similarity,
                    context_bonus=self.calculate_context_bonus(chunk, query_context),
                    concept_match_score=self.calculate_concept_match_score(chunk, query_context),
                    type_match_score=self.calculate_type_match_score(chunk, query_context),
                    final_rank=0,  # Será definido após ordenação
                    explanation=explanation
                ))
        
        # Ordenar por relevância
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Atribuir ranks finais
        for i, result in enumerate(results[:top_k]):
            result.final_rank = i + 1
        
        self.logger.info(f"Recuperados {len(results[:top_k])} chunks para query tipo {query_context.query_type}")
        
        return results[:top_k]
    
    def diversify_results(self, results: List[RetrievalResult], max_per_type: int = 3) -> List[RetrievalResult]:
        """Diversifica resultados para evitar concentração em um tipo"""
        if not results:
            return results
        
        diversified = []
        type_counts = defaultdict(int)
        
        for result in results:
            chunk_type = result.chunk.chunk_type
            
            if type_counts[chunk_type] < max_per_type:
                diversified.append(result)
                type_counts[chunk_type] += 1
            
            # Parar se já temos resultados suficientes
            if len(diversified) >= len(results):
                break
        
        # Se ainda há espaço, preencher com os melhores restantes
        remaining_slots = len(results) - len(diversified)
        if remaining_slots > 0:
            used_results = set(r.chunk.content for r in diversified)
            remaining = [r for r in results if r.chunk.content not in used_results]
            diversified.extend(remaining[:remaining_slots])
        
        self.logger.info(f"Diversificação: {len(results)} -> {len(diversified)} chunks")
        return diversified
    
    def explain_retrieval(self, results: List[RetrievalResult]) -> str:
        """Gera explicação detalhada dos resultados"""
        if not results:
            return "Nenhum chunk relevante encontrado."
        
        explanation = f"Encontrados {len(results)} chunks relevantes:\n\n"
        
        for i, result in enumerate(results[:5], 1):
            chunk = result.chunk
            explanation += f"{i}. [{chunk.chunk_type.value.upper()}] "
            explanation += f"Score: {result.relevance_score:.3f} "
            explanation += f"({result.explanation})\n"
            
            if chunk.section_title:
                explanation += f"   Seção: {chunk.section_title}\n"
            
            if chunk.key_concepts:
                explanation += f"   Conceitos: {', '.join(chunk.key_concepts[:3])}\n"
            
            preview = chunk.content[:150] + "..." if len(chunk.content) > 150 else chunk.content
            explanation += f"   Preview: {preview}\n\n"
        
        return explanation
