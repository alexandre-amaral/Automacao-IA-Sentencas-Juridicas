"""
Chunking Semântico Inteligente para Textos Jurídicos
Divide documentos preservando contexto jurídico e estrutura lógica
"""

import logging
import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ChunkType(Enum):
    """Tipos de chunks jurídicos"""
    RELATÓRIO = "relatório"
    FUNDAMENTACAO = "fundamentacao"
    DISPOSITIVO = "dispositivo"
    PEDIDO = "pedido"
    DEFESA = "defesa"
    PROVA = "prova"
    JURISPRUDENCIA = "jurisprudencia"
    CITACAO_LEGAL = "citacao_legal"
    CONTEXTO = "contexto"

@dataclass
class SemanticChunk:
    """Chunk semântico com metadata jurídica"""
    content: str
    chunk_type: ChunkType
    section_title: Optional[str]
    legal_references: List[str]
    key_concepts: List[str]
    priority: int  # 1-10, sendo 10 mais importante
    char_start: int
    char_end: int
    context_before: str
    context_after: str

class SemanticChunker:
    """Chunker inteligente para documentos jurídicos"""
    
    def __init__(self, max_chunk_size: int = 1000, overlap_size: int = 100):
        self.logger = logging.getLogger(__name__)
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        
        # Padrões de estrutura jurídica
        self.section_patterns = {
            ChunkType.RELATÓRIO: [
                r"RELATÓRIO",
                r"VISTOS.*AUTOS",
                r"Trata-se de",
                r"Cuida-se de",
                r"HISTÓRICO"
            ],
            ChunkType.FUNDAMENTACAO: [
                r"FUNDAMENTAÇÃO",
                r"VOTO",
                r"ANÁLISE",
                r"MÉRITO",
                r"Passo ao exame",
                r"Analiso os pedidos"
            ],
            ChunkType.DISPOSITIVO: [
                r"DISPOSITIVO",
                r"JULGO",
                r"CONDENO",
                r"ABSOLVO",
                r"DETERMINO",
                r"Posto isto"
            ],
            ChunkType.PEDIDO: [
                r"DOS PEDIDOS",
                r"REQUER",
                r"SOLICITA",
                r"PLEITEIA"
            ],
            ChunkType.DEFESA: [
                r"CONTESTAÇÃO",
                r"DEFESA",
                r"IMPUGNA",
                r"CONTESTA"
            ],
            ChunkType.PROVA: [
                r"PROVA",
                r"TESTEMUNHA",
                r"DEPOIMENTO",
                r"DOCUMENTO"
            ]
        }
        
        # Padrões de citações legais
        self.legal_citation_patterns = [
            r"art\.?\s*\d+.*?(?:CF|CLT|CPC|CC)",
            r"súmula\s+\d+.*?(?:TST|STF|STJ)",
            r"enunciado\s+\d+",
            r"precedente\s+\d+",
            r"orientação\s+jurisprudencial\s+\d+"
        ]
        
        # Conceitos-chave para priorização
        self.priority_concepts = {
            10: ["justa causa", "dano moral", "equiparação salarial"],
            9: ["horas extras", "adicional noturno", "rescisão"],
            8: ["aviso prévio", "férias", "13º salário"],
            7: ["FGTS", "PIS", "insalubridade"],
            6: ["audiência", "depoimento", "prova"],
            5: ["petição inicial", "contestação", "réplica"]
        }
    
    def identify_section_type(self, text: str) -> ChunkType:
        """Identifica o tipo de seção do texto"""
        text_upper = text.upper()
        
        for chunk_type, patterns in self.section_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_upper):
                    return chunk_type
        
        # Análise por conteúdo se não encontrou padrão
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["julgo", "condeno", "absolvo"]):
            return ChunkType.DISPOSITIVO
        elif any(word in text_lower for word in ["súmula", "jurisprudência", "precedente"]):
            return ChunkType.JURISPRUDENCIA
        elif any(word in text_lower for word in ["requer", "solicita", "pleiteia"]):
            return ChunkType.PEDIDO
        elif any(word in text_lower for word in ["contesta", "impugna", "nega"]):
            return ChunkType.DEFESA
        elif any(word in text_lower for word in ["testemunha", "depoimento", "prova"]):
            return ChunkType.PROVA
        else:
            return ChunkType.CONTEXTO
    
    def extract_legal_references(self, text: str) -> List[str]:
        """Extrai referências legais do texto"""
        references = []
        
        for pattern in self.legal_citation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            references.extend(matches)
        
        return list(set(references))  # Remover duplicatas
    
    def extract_key_concepts(self, text: str) -> List[str]:
        """Extrai conceitos-chave do texto"""
        concepts = []
        text_lower = text.lower()
        
        # Buscar conceitos por prioridade
        for priority, concept_list in self.priority_concepts.items():
            for concept in concept_list:
                if concept in text_lower:
                    concepts.append(concept)
        
        return list(set(concepts))
    
    def calculate_priority(self, chunk_content: str, chunk_type: ChunkType) -> int:
        """Calcula prioridade do chunk"""
        base_priority = {
            ChunkType.DISPOSITIVO: 10,
            ChunkType.FUNDAMENTACAO: 9,
            ChunkType.JURISPRUDENCIA: 8,
            ChunkType.PROVA: 7,
            ChunkType.PEDIDO: 6,
            ChunkType.DEFESA: 6,
            ChunkType.RELATÓRIO: 5,
            ChunkType.CITACAO_LEGAL: 8,
            ChunkType.CONTEXTO: 3
        }.get(chunk_type, 3)
        
        # Boost baseado em conceitos-chave
        key_concepts = self.extract_key_concepts(chunk_content)
        concept_boost = 0
        
        for priority, concept_list in self.priority_concepts.items():
            for concept in key_concepts:
                if concept in concept_list:
                    concept_boost = max(concept_boost, priority - 5)  # Max +5
        
        # Boost para citações legais
        legal_refs = self.extract_legal_references(chunk_content)
        legal_boost = min(2, len(legal_refs))  # Max +2
        
        final_priority = min(10, base_priority + concept_boost + legal_boost)
        return final_priority
    
    def find_natural_breaks(self, text: str) -> List[int]:
        """Encontra pontos naturais de quebra no texto"""
        breaks = []
        
        # Quebras por parágrafos
        for match in re.finditer(r'\n\s*\n', text):
            breaks.append(match.start())
        
        # Quebras por seções
        section_patterns = [
            r'\n\s*[A-Z][^a-z\n]{10,}\s*\n',  # Títulos em maiúscula
            r'\n\s*\d+\.\s+[A-Z]',  # Numeração
            r'\n\s*[a-z]\)\s+',  # Letras com parênteses
            r'\.(\s+[A-Z][a-z])',  # Final de frase + início de nova
        ]
        
        for pattern in section_patterns:
            for match in re.finditer(pattern, text):
                breaks.append(match.start())
        
        return sorted(list(set(breaks)))
    
    def create_chunks(self, text: str, document_title: str = "") -> List[SemanticChunk]:
        """Cria chunks semânticos do documento"""
        chunks = []
        
        if not text or len(text.strip()) == 0:
            return chunks
        
        # Encontrar quebras naturais
        natural_breaks = self.find_natural_breaks(text)
        natural_breaks = [0] + natural_breaks + [len(text)]
        
        current_pos = 0
        
        while current_pos < len(text):
            # Determinar fim do chunk
            end_pos = min(current_pos + self.max_chunk_size, len(text))
            
            # Ajustar para quebra natural mais próxima
            if end_pos < len(text):
                best_break = None
                for break_pos in natural_breaks:
                    if current_pos < break_pos <= end_pos:
                        best_break = break_pos
                
                if best_break:
                    end_pos = best_break
            
            # Extrair conteúdo do chunk
            chunk_content = text[current_pos:end_pos].strip()
            
            if len(chunk_content) < 20:  # Skip chunks muito pequenos
                current_pos = end_pos
                continue
            
            # Extrair contexto
            context_before = text[max(0, current_pos - 200):current_pos].strip()
            context_after = text[end_pos:min(len(text), end_pos + 200)].strip()
            
            # Identificar tipo e metadata
            chunk_type = self.identify_section_type(chunk_content)
            legal_references = self.extract_legal_references(chunk_content)
            key_concepts = self.extract_key_concepts(chunk_content)
            priority = self.calculate_priority(chunk_content, chunk_type)
            
            # Extrair título da seção se houver
            section_title = self._extract_section_title(chunk_content)
            
            # Criar chunk
            chunk = SemanticChunk(
                content=chunk_content,
                chunk_type=chunk_type,
                section_title=section_title,
                legal_references=legal_references,
                key_concepts=key_concepts,
                priority=priority,
                char_start=current_pos,
                char_end=end_pos,
                context_before=context_before,
                context_after=context_after
            )
            
            chunks.append(chunk)
            
            # Próxima posição com overlap
            if end_pos >= len(text):
                break
            
            next_pos = end_pos - self.overlap_size
            current_pos = max(current_pos + 1, next_pos)  # Garantir progresso
        
        self.logger.info(f"Criados {len(chunks)} chunks semânticos")
        return chunks
    
    def _extract_section_title(self, content: str) -> Optional[str]:
        """Extrai título da seção se houver"""
        lines = content.split('\n')
        
        for line in lines[:3]:  # Verificar primeiras 3 linhas
            line = line.strip()
            
            # Título em maiúscula
            if len(line) > 5 and line.isupper() and len(line) < 100:
                return line
            
            # Título numerado
            if re.match(r'^\d+\.?\s+[A-Z]', line) and len(line) < 100:
                return line
        
        return None
    
    def merge_related_chunks(self, chunks: List[SemanticChunk]) -> List[SemanticChunk]:
        """Mescla chunks relacionados se necessário"""
        if not chunks:
            return chunks
        
        merged = []
        current_chunk = chunks[0]
        
        for next_chunk in chunks[1:]:
            # Verificar se devem ser mesclados
            should_merge = (
                current_chunk.chunk_type == next_chunk.chunk_type and
                len(current_chunk.content) + len(next_chunk.content) < self.max_chunk_size * 1.5 and
                current_chunk.priority == next_chunk.priority
            )
            
            if should_merge:
                # Mesclar chunks
                merged_content = current_chunk.content + "\n\n" + next_chunk.content
                merged_concepts = list(set(current_chunk.key_concepts + next_chunk.key_concepts))
                merged_references = list(set(current_chunk.legal_references + next_chunk.legal_references))
                
                current_chunk = SemanticChunk(
                    content=merged_content,
                    chunk_type=current_chunk.chunk_type,
                    section_title=current_chunk.section_title or next_chunk.section_title,
                    legal_references=merged_references,
                    key_concepts=merged_concepts,
                    priority=max(current_chunk.priority, next_chunk.priority),
                    char_start=current_chunk.char_start,
                    char_end=next_chunk.char_end,
                    context_before=current_chunk.context_before,
                    context_after=next_chunk.context_after
                )
            else:
                merged.append(current_chunk)
                current_chunk = next_chunk
        
        merged.append(current_chunk)
        
        self.logger.info(f"Chunks após mesclagem: {len(merged)} (original: {len(chunks)})")
        return merged
