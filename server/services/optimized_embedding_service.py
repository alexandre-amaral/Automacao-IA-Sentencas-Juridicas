"""
Serviço de Embeddings Otimizado para Textos Jurídicos
Especializado em compreender nuances jurídicas e maximizar relevância
"""

import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from sentence_transformers import SentenceTransformer
import torch
from dataclasses import dataclass
import re
from pathlib import Path

@dataclass
class EmbeddingResult:
    """Resultado de embedding com metadata"""
    text: str
    embedding: np.ndarray
    confidence: float
    semantic_category: str
    legal_concepts: List[str]

class OptimizedEmbeddingService:
    """Serviço otimizado de embeddings para contexto jurídico"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Modelo especializado em português jurídico
        self.model = SentenceTransformer('rufimelo/Legal-BERTimbau-sts-base-ma-v3')
        
        # Fallback para modelo geral caso o especializado falhe
        self.fallback_model = SentenceTransformer('neuralmind/bert-base-portuguese-cased')
        
        # Conceitos jurídicos fundamentais para boost
        self.legal_concepts = {
            "direito_trabalho": [
                "horas extras", "adicional noturno", "rescisão", "justa causa",
                "aviso prévio", "férias", "13º salário", "FGTS", "PIS",
                "equiparação salarial", "assédio moral", "acidente trabalho"
            ],
            "procedimento": [
                "petição inicial", "contestação", "réplica", "audiência",
                "depoimento", "prova testemunhal", "documento", "sentença"
            ],
            "fundamentacao": [
                "súmula", "jurisprudência", "precedente", "CLT", "constituição",
                "dano moral", "responsabilidade", "nexo causal", "prova"
            ]
        }
        
        # Padrões jurídicos para identificação
        self.legal_patterns = {
            "artigo_lei": r"art\.?\s*\d+|artigo\s+\d+",
            "sumula": r"súmula\s+\d+|enunciado\s+\d+",
            "processo": r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}",
            "valor_monetario": r"R\$\s*[\d.,]+",
            "data": r"\d{1,2}/\d{1,2}/\d{4}",
            "percentual": r"\d+%|\d+\s*por\s*cento"
        }
    
    def extract_legal_concepts(self, text: str) -> List[str]:
        """Extrai conceitos jurídicos do texto"""
        concepts = []
        text_lower = text.lower()
        
        for category, terms in self.legal_concepts.items():
            for term in terms:
                if term in text_lower:
                    concepts.append(f"{category}:{term}")
        
        # Identificar padrões jurídicos
        for pattern_name, pattern in self.legal_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                concepts.extend([f"pattern:{pattern_name}" for _ in matches[:3]])  # Max 3
        
        return concepts
    
    def classify_semantic_category(self, text: str) -> str:
        """Classifica categoria semântica do texto"""
        text_lower = text.lower()
        
        # Categorias por palavras-chave
        categories = {
            "relatório": ["relatório", "histórico", "resumo", "contexto"],
            "fundamentacao": ["fundamentação", "decisão", "entendimento", "precedente"],
            "dispositivo": ["dispositivo", "julgo", "condeno", "absolvo", "determino"],
            "pedido": ["requer", "solicita", "pleiteia", "pede"],
            "defesa": ["contesta", "impugna", "refuta", "nega"],
            "prova": ["testemunha", "depoimento", "documento", "prova"],
            "jurisprudencia": ["súmula", "jurisprudência", "acórdão", "decisão"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return "geral"
    
    def calculate_confidence(self, text: str, embedding: np.ndarray) -> float:
        """Calcula confiança do embedding baseado em características do texto"""
        base_confidence = 0.5
        
        # Boost para textos com conceitos jurídicos
        legal_concepts = self.extract_legal_concepts(text)
        concept_boost = min(0.3, len(legal_concepts) * 0.05)
        
        # Boost para textos com estrutura jurídica
        structure_boost = 0.0
        if any(pattern in text.lower() for pattern in ["considerando", "visto que", "posto isto"]):
            structure_boost = 0.1
        
        # Penalidade para textos muito curtos
        length_penalty = 0.0
        if len(text) < 50:
            length_penalty = -0.2
        
        # Boost para embeddings com magnitude adequada
        magnitude_boost = 0.0
        magnitude = np.linalg.norm(embedding)
        if 0.8 <= magnitude <= 1.2:
            magnitude_boost = 0.1
        
        confidence = base_confidence + concept_boost + structure_boost + length_penalty + magnitude_boost
        return max(0.1, min(1.0, confidence))
    
    def create_embedding(self, text: str) -> EmbeddingResult:
        """Cria embedding otimizado com metadata"""
        try:
            # Preprocessing específico para textos jurídicos
            processed_text = self._preprocess_legal_text(text)
            
            # Tentar modelo especializado primeiro
            try:
                embedding = self.model.encode([processed_text])[0]
            except Exception as e:
                self.logger.warning(f"Modelo especializado falhou, usando fallback: {e}")
                embedding = self.fallback_model.encode([processed_text])[0]
            
            # Normalizar embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            # Extrair metadata
            legal_concepts = self.extract_legal_concepts(text)
            semantic_category = self.classify_semantic_category(text)
            confidence = self.calculate_confidence(text, embedding)
            
            return EmbeddingResult(
                text=text,
                embedding=embedding,
                confidence=confidence,
                semantic_category=semantic_category,
                legal_concepts=legal_concepts
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao criar embedding: {e}")
            # Embedding zero como fallback
            return EmbeddingResult(
                text=text,
                embedding=np.zeros(768),
                confidence=0.1,
                semantic_category="erro",
                legal_concepts=[]
            )
    
    def _preprocess_legal_text(self, text: str) -> str:
        """Preprocessamento específico para textos jurídicos"""
        # Preservar estruturas jurídicas importantes
        text = re.sub(r'\s+', ' ', text)  # Normalizar espaços
        text = text.strip()
        
        # Manter formatação de artigos e numerações
        text = re.sub(r'(\d+)\s*[°º]\s*', r'\1º ', text)
        text = re.sub(r'Art\.\s*(\d+)', r'Artigo \1', text)
        
        return text
    
    def create_batch_embeddings(self, texts: List[str]) -> List[EmbeddingResult]:
        """Cria embeddings em lote para eficiência"""
        results = []
        
        try:
            # Preprocessar todos os textos
            processed_texts = [self._preprocess_legal_text(text) for text in texts]
            
            # Embeddings em batch
            try:
                embeddings = self.model.encode(processed_texts)
            except Exception as e:
                self.logger.warning(f"Modelo especializado falhou em batch, usando fallback: {e}")
                embeddings = self.fallback_model.encode(processed_texts)
            
            # Processar resultados individuais
            for text, embedding in zip(texts, embeddings):
                # Normalizar
                embedding = embedding / np.linalg.norm(embedding)
                
                # Metadata
                legal_concepts = self.extract_legal_concepts(text)
                semantic_category = self.classify_semantic_category(text)
                confidence = self.calculate_confidence(text, embedding)
                
                results.append(EmbeddingResult(
                    text=text,
                    embedding=embedding,
                    confidence=confidence,
                    semantic_category=semantic_category,
                    legal_concepts=legal_concepts
                ))
                
        except Exception as e:
            self.logger.error(f"Erro no batch de embeddings: {e}")
            # Fallback individual
            for text in texts:
                results.append(self.create_embedding(text))
        
        return results
    
    def compare_embeddings(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calcula similaridade entre embeddings com otimização jurídica"""
        # Similaridade cosseno padrão
        base_similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        # Aplicar boost baseado na magnitude (embeddings mais "confiantes")
        magnitude_factor = (np.linalg.norm(emb1) + np.linalg.norm(emb2)) / 2
        magnitude_boost = min(0.1, (magnitude_factor - 0.8) * 0.2) if magnitude_factor > 0.8 else 0
        
        final_similarity = base_similarity + magnitude_boost
        return max(-1.0, min(1.0, final_similarity))
