"""
RAG Service Aprimorado com Chunking Semântico e Recuperação Contextual
Integra todos os componentes otimizados para máxima qualidade
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from .instance_manager import InstanceManager
from .optimized_embedding_service import OptimizedEmbeddingService, EmbeddingResult
from .semantic_chunker import SemanticChunker, SemanticChunk, ChunkType
from .contextual_retriever import ContextualRetriever, QueryContext, QueryType, RetrievalResult
import chromadb
from chromadb.config import Settings

class EnhancedRAGService:
    """RAG Service com otimizações semânticas e contextuais"""
    
    def __init__(self, case_id: str):
        self.case_id = case_id
        self.logger = logging.getLogger(__name__)
        
        # Componentes otimizados
        self.instance_manager = InstanceManager()
        self.embedding_service = OptimizedEmbeddingService()
        self.chunker = SemanticChunker(max_chunk_size=800, overlap_size=100)
        self.retriever = ContextualRetriever(self.embedding_service)
        
        # Inicializar instância isolada
        self.instance_info = self.instance_manager.create_isolated_instance(case_id)
        self.rag_path = Path(self.instance_info["directories"]["instance_root"])
        
        # ChromaDB isolado
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.rag_path / "chroma_db"),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Coleções especializadas
        self.collections = {
            "estilo_juiza": self._get_or_create_collection("estilo_juiza"),
            "caso_atual": self._get_or_create_collection("caso_atual"),
            "dialogo_contexto": self._get_or_create_collection("dialogo_contexto"),
            "jurisprudencia": self._get_or_create_collection("jurisprudencia")
        }
        
        # Cache de chunks para evitar reprocessamento
        self._chunks_cache = {}
        
    def _get_or_create_collection(self, name: str):
        """Obtém ou cria coleção no ChromaDB"""
        try:
            return self.chroma_client.get_collection(f"{self.case_id}_{name}")
        except:
            return self.chroma_client.create_collection(f"{self.case_id}_{name}")
    
    def initialize_judge_style(self, sentences_examples: List[str], force_reload: bool = False):
        """Inicializa conhecimento do estilo da juíza"""
        collection = self.collections["estilo_juiza"]
        
        # Verificar se já foi inicializado
        if not force_reload and collection.count() > 0:
            self.logger.info("Estilo da juíza já inicializado")
            return
        
        self.logger.info("Inicializando conhecimento do estilo da juíza...")
        
        all_chunks = []
        all_embeddings = []
        all_metadatas = []
        all_ids = []
        
        for i, sentence_text in enumerate(sentences_examples):
            # Chunking semântico
            chunks = self.chunker.create_chunks(sentence_text, f"Sentença Exemplo {i+1}")
            
            for j, chunk in enumerate(chunks):
                chunk_id = f"estilo_{i}_{j}"
                
                # Embedding otimizado
                embedding_result = self.embedding_service.create_embedding(chunk.content)
                
                # Metadata enriquecida
                metadata = {
                    "case_id": self.case_id,
                    "tipo": "estilo_juiza",
                    "chunk_type": chunk.chunk_type.value,
                    "priority": chunk.priority,
                    "sentence_index": i,
                    "chunk_index": j,
                    "confidence": embedding_result.confidence,
                    "semantic_category": embedding_result.semantic_category,
                    "legal_concepts": ",".join(chunk.key_concepts),
                    "legal_references": ",".join(chunk.legal_references),
                    "section_title": chunk.section_title or "",
                    "created_at": datetime.now().isoformat()
                }
                
                all_chunks.append(chunk.content)
                all_embeddings.append(embedding_result.embedding.tolist())
                all_metadatas.append(metadata)
                all_ids.append(chunk_id)
        
        # Salvar em batch
        if all_chunks:
            collection.add(
                documents=all_chunks,
                embeddings=all_embeddings,
                metadatas=all_metadatas,
                ids=all_ids
            )
            
            self.logger.info(f"Salvos {len(all_chunks)} chunks de estilo da juíza")
            
            # Cache dos chunks
            self._chunks_cache["estilo_juiza"] = [
                self.chunker.create_chunks(text, f"Exemplo {i}")[0] 
                for i, text in enumerate(sentences_examples)
            ]
    
    def save_case_knowledge(self, processo_estruturado, transcricao_audiencia: str = ""):
        """Salva conhecimento específico do caso atual"""
        collection = self.collections["caso_atual"]
        
        self.logger.info("Salvando conhecimento do caso atual...")
        
        # Preparar textos para chunking
        case_texts = []
        
        # Dados estruturados do processo
        processo_text = self._serialize_processo_estruturado(processo_estruturado)
        case_texts.append(("processo_estruturado", processo_text))
        
        # Transcrição da audiência
        if transcricao_audiencia:
            case_texts.append(("transcricao_audiencia", transcricao_audiencia))
        
        all_chunks = []
        all_embeddings = []
        all_metadatas = []
        all_ids = []
        
        for source_type, text in case_texts:
            # Chunking semântico
            chunks = self.chunker.create_chunks(text, f"Caso Atual - {source_type}")
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"caso_{source_type}_{i}"
                
                # Embedding otimizado
                embedding_result = self.embedding_service.create_embedding(chunk.content)
                
                # Metadata específica do caso
                metadata = {
                    "case_id": self.case_id,
                    "tipo": "caso_atual",
                    "source_type": source_type,
                    "chunk_type": chunk.chunk_type.value,
                    "priority": chunk.priority,
                    "chunk_index": i,
                    "confidence": embedding_result.confidence,
                    "semantic_category": embedding_result.semantic_category,
                    "legal_concepts": ",".join(chunk.key_concepts),
                    "legal_references": ",".join(chunk.legal_references),
                    "section_title": chunk.section_title or "",
                    "numero_processo": getattr(processo_estruturado, 'numero_processo', ''),
                    "created_at": datetime.now().isoformat()
                }
                
                all_chunks.append(chunk.content)
                all_embeddings.append(embedding_result.embedding.tolist())
                all_metadatas.append(metadata)
                all_ids.append(chunk_id)
        
        # Salvar em batch
        if all_chunks:
            collection.add(
                documents=all_chunks,
                embeddings=all_embeddings,
                metadatas=all_metadatas,
                ids=all_ids
            )
            
            self.logger.info(f"Salvos {len(all_chunks)} chunks do caso atual")
            
            # Backup em JSON
            self._backup_case_knowledge(processo_estruturado, transcricao_audiencia)
    
    def save_dialogue_context(self, question: str, answer: str, dialogue_step: int):
        """Salva contexto do diálogo Claude-Gemini"""
        collection = self.collections["dialogo_contexto"]
        
        # Texto combinado da interação
        dialogue_text = f"PERGUNTA: {question}\n\nRESPOSTA: {answer}"
        
        # Chunking do diálogo
        chunks = self.chunker.create_chunks(dialogue_text, f"Diálogo Etapa {dialogue_step}")
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"dialogo_{dialogue_step}_{i}"
            
            # Embedding
            embedding_result = self.embedding_service.create_embedding(chunk.content)
            
            # Metadata do diálogo
            metadata = {
                "case_id": self.case_id,
                "tipo": "dialogo_contexto",
                "dialogue_step": dialogue_step,
                "chunk_type": chunk.chunk_type.value,
                "priority": chunk.priority + 2,  # Boost para contexto recente
                "chunk_index": i,
                "confidence": embedding_result.confidence,
                "question_preview": question[:100],
                "created_at": datetime.now().isoformat()
            }
            
            collection.add(
                documents=[chunk.content],
                embeddings=[embedding_result.embedding.tolist()],
                metadatas=[metadata],
                ids=[chunk_id]
            )
        
        self.logger.info(f"Salvo contexto do diálogo etapa {dialogue_step}")
    
    def query_knowledge(self, 
                       query: str, 
                       query_type: QueryType = None,
                       sources: List[str] = None,
                       top_k: int = 10,
                       include_explanation: bool = False) -> Dict[str, Any]:
        """Query otimizada no conhecimento com recuperação contextual"""
        
        # Fontes padrão se não especificadas
        if sources is None:
            sources = ["estilo_juiza", "caso_atual", "dialogo_contexto"]
        
        # Criar contexto da query
        case_context = self._get_case_context()
        query_context = self.retriever.create_query_context(
            query=query,
            case_data=case_context,
            explicit_type=query_type
        )
        
        self.logger.info(f"Query: '{query}' | Tipo: {query_context.query_type} | Fontes: {sources}")
        
        # Recuperar chunks de todas as fontes
        all_chunks = []
        for source in sources:
            if source in self.collections:
                source_chunks = self._get_chunks_from_collection(source)
                all_chunks.extend(source_chunks)
        
        # Recuperação contextual
        results = self.retriever.retrieve_relevant_chunks(
            query_context=query_context,
            available_chunks=all_chunks,
            top_k=top_k,
            min_relevance=0.15
        )
        
        # Diversificar resultados
        diversified_results = self.retriever.diversify_results(results, max_per_type=4)
        
        # Preparar resposta
        response = {
            "query": query,
            "query_type": query_context.query_type.value,
            "total_results": len(diversified_results),
            "results": []
        }
        
        for result in diversified_results:
            chunk_data = {
                "content": result.chunk.content,
                "relevance_score": result.relevance_score,
                "chunk_type": result.chunk.chunk_type.value,
                "section_title": result.chunk.section_title,
                "key_concepts": result.chunk.key_concepts,
                "legal_references": result.chunk.legal_references,
                "priority": result.chunk.priority,
                "rank": result.final_rank
            }
            
            if include_explanation:
                chunk_data["explanation"] = result.explanation
                chunk_data["embedding_similarity"] = result.embedding_similarity
                chunk_data["concept_match_score"] = result.concept_match_score
                chunk_data["type_match_score"] = result.type_match_score
            
            response["results"].append(chunk_data)
        
        # Adicionar explicação se solicitada
        if include_explanation:
            response["explanation"] = self.retriever.explain_retrieval(diversified_results)
        
        self.logger.info(f"Retornados {len(diversified_results)} resultados para query")
        
        return response
    
    def _get_chunks_from_collection(self, collection_name: str) -> List[SemanticChunk]:
        """Recupera chunks de uma coleção como objetos SemanticChunk"""
        collection = self.collections[collection_name]
        
        # Verificar cache primeiro
        cache_key = f"{collection_name}_{self.case_id}"
        if cache_key in self._chunks_cache:
            return self._chunks_cache[cache_key]
        
        try:
            # Recuperar todos os documentos da coleção
            results = collection.get(include=["documents", "metadatas"])
            
            chunks = []
            for i, (document, metadata) in enumerate(zip(results["documents"], results["metadatas"])):
                # Reconstruir SemanticChunk a partir dos dados
                chunk = SemanticChunk(
                    content=document,
                    chunk_type=ChunkType(metadata.get("chunk_type", "contexto")),
                    section_title=metadata.get("section_title") or None,
                    legal_references=metadata.get("legal_references", "").split(",") if metadata.get("legal_references") else [],
                    key_concepts=metadata.get("legal_concepts", "").split(",") if metadata.get("legal_concepts") else [],
                    priority=metadata.get("priority", 5),
                    char_start=0,
                    char_end=len(document),
                    context_before="",
                    context_after=""
                )
                chunks.append(chunk)
            
            # Cache para próximas consultas
            self._chunks_cache[cache_key] = chunks
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Erro ao recuperar chunks de {collection_name}: {e}")
            return []
    
    def _get_case_context(self) -> Dict[str, Any]:
        """Obtém contexto do caso atual"""
        try:
            # Tentar carregar do backup JSON
            backup_file = self.rag_path / "conhecimento_rag.json"
            if backup_file.exists():
                with open(backup_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Erro ao carregar contexto do caso: {e}")
        
        return {}
    
    def _serialize_processo_estruturado(self, processo) -> str:
        """Serializa processo estruturado para texto"""
        try:
            # Converter para dicionário primeiro
            if hasattr(processo, '__dict__'):
                data = processo.__dict__
            else:
                data = processo
            
            # Criar representação textual estruturada
            text_parts = []
            
            text_parts.append(f"NÚMERO DO PROCESSO: {data.get('numero_processo', 'N/A')}")
            
            if 'partes' in data and data['partes']:
                text_parts.append("\\nPARTES:")
                for parte in data['partes']:
                    text_parts.append(f"- {parte.get('nome', 'N/A')} ({parte.get('tipo', 'N/A')})")
            
            if 'pedidos' in data and data['pedidos']:
                text_parts.append("\\nPEDIDOS:")
                for pedido in data['pedidos']:
                    text_parts.append(f"- {pedido.get('descricao', 'N/A')} (Categoria: {pedido.get('categoria', 'N/A')})")
            
            if 'fatos_relevantes' in data and data['fatos_relevantes']:
                text_parts.append("\\nFATOS RELEVANTES:")
                for fato in data['fatos_relevantes']:
                    text_parts.append(f"- {fato.get('descricao', 'N/A')}")
            
            # Adicionar outros campos importantes
            for field in ['periodo_contratual', 'valor_causa', 'competencia']:
                if field in data and data[field]:
                    text_parts.append(f"\\n{field.upper().replace('_', ' ')}: {data[field]}")
            
            return "\\n".join(text_parts)
            
        except Exception as e:
            self.logger.error(f"Erro ao serializar processo: {e}")
            return str(processo)
    
    def _backup_case_knowledge(self, processo_estruturado, transcricao_audiencia: str):
        """Backup do conhecimento em JSON"""
        try:
            backup_data = {
                "case_id": self.case_id,
                "processo_estruturado": self._serialize_processo_estruturado(processo_estruturado),
                "transcricao_audiencia": transcricao_audiencia,
                "created_at": datetime.now().isoformat(),
                "conceitos_principais": []  # Será preenchido conforme necessário
            }
            
            backup_file = self.rag_path / "conhecimento_rag.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info("Backup do conhecimento salvo")
            
        except Exception as e:
            self.logger.error(f"Erro ao fazer backup: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas do RAG"""
        stats = {
            "case_id": self.case_id,
            "collections": {}
        }
        
        for name, collection in self.collections.items():
            try:
                count = collection.count()
                stats["collections"][name] = {
                    "chunk_count": count,
                    "status": "active" if count > 0 else "empty"
                }
            except Exception as e:
                stats["collections"][name] = {
                    "chunk_count": 0,
                    "status": f"error: {str(e)}"
                }
        
        return stats
