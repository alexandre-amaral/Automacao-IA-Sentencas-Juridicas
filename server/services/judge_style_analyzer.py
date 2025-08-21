"""
Analisador de Estilo da Juíza
Extrai padrões de linguagem, estruturas e expressões características
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set
from collections import Counter, defaultdict
from dataclasses import dataclass
import statistics

@dataclass
class StylePattern:
    """Padrão de estilo identificado"""
    pattern_type: str  # linguistic, structural, legal
    pattern: str
    frequency: int
    contexts: List[str]
    confidence: float
    examples: List[str]

@dataclass
class JudgeStyleProfile:
    """Perfil completo do estilo da juíza"""
    linguistic_patterns: List[StylePattern]
    structural_patterns: List[StylePattern]
    legal_expressions: List[StylePattern]
    sentence_structures: List[str]
    paragraph_patterns: List[str]
    transition_phrases: List[str]
    citation_styles: List[str]
    decision_patterns: Dict[str, List[str]]
    statistical_summary: Dict[str, Any]

class JudgeStyleAnalyzer:
    """Analisador avançado do estilo da juíza"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Padrões linguísticos jurídicos
        self.linguistic_patterns = {
            "conectores": [
                r"\b(?:contudo|entretanto|todavia|no entanto|porém)\b",
                r"\b(?:ademais|outrossim|além disso|por outro lado)\b", 
                r"\b(?:posto isto|diante do exposto|ante o exposto)\b",
                r"\b(?:nesse sentido|nessa esteira|nessa toada)\b",
                r"\b(?:com efeito|de fato|efetivamente)\b"
            ],
            "expressoes_decisao": [
                r"\b(?:julgo procedente|julgo improcedente|julgo parcialmente procedente)\b",
                r"\b(?:condeno|absolvo|determino|defiro|indefiro)\b",
                r"\b(?:acolho|rejeito|reconheço|declaro)\b"
            ],
            "fundamentacao": [
                r"\b(?:é cediço que|é consabido que|é pacífico que)\b",
                r"\b(?:conforme se depreende|verifica-se que|constata-se que)\b",
                r"\b(?:nesse contexto|nesse diapasão|sob esse prisma)\b"
            ],
            "citacoes": [
                r"(?:art\.?\s*\d+|artigo\s+\d+).*?(?:da\s+)?(?:CLT|CF|CPC|CC)",
                r"Súmula\s+n?º?\s*\d+.*?(?:TST|STF|STJ)",
                r"Orientação\s+Jurisprudencial\s+n?º?\s*\d+"
            ]
        }
        
        # Padrões estruturais
        self.structural_patterns = {
            "inicio_paragrafo": [
                r"^(?:Passo ao exame|Analiso|Verifico|Constato)",
                r"^(?:No caso em tela|No presente caso|Na hipótese)",
                r"^(?:Com efeito|De fato|Efetivamente)"
            ],
            "conclusao_paragrafo": [
                r"(?:razão pela qual|motivo pelo qual).*\.$",
                r"(?:dessa forma|assim sendo|portanto).*\.$",
                r"(?:logo|destarte|por conseguinte).*\.$"
            ],
            "secoes": [
                r"^(?:I\s*[-–]\s*RELATÓRIO|RELATÓRIO)",
                r"^(?:II\s*[-–]\s*FUNDAMENTAÇÃO|FUNDAMENTAÇÃO)", 
                r"^(?:III\s*[-–]\s*DISPOSITIVO|DISPOSITIVO)"
            ]
        }
    
    def extract_sentence_patterns(self, text: str) -> List[str]:
        """Extrai padrões de estrutura de frases"""
        sentences = re.split(r'[.!?]+', text)
        patterns = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip muito curtas
                continue
                
            # Identificar estrutura da frase
            words = sentence.split()
            if len(words) < 5:
                continue
                
            # Padrões de início
            start_pattern = ' '.join(words[:3]).lower()
            
            # Padrões de estrutura (sujeito-verbo-objeto simplificado)
            structure = self._identify_sentence_structure(sentence)
            
            patterns.append({
                "start": start_pattern,
                "structure": structure,
                "length": len(words),
                "example": sentence[:100] + "..." if len(sentence) > 100 else sentence
            })
        
        return patterns
    
    def _identify_sentence_structure(self, sentence: str) -> str:
        """Identifica estrutura básica da frase"""
        sentence_lower = sentence.lower()
        
        # Padrões estruturais
        if re.search(r'\b(?:alega|sustenta|afirma|aduz)\b', sentence_lower):
            return "alegacao"
        elif re.search(r'\b(?:julgo|condeno|absolvo|determino)\b', sentence_lower):
            return "decisao"
        elif re.search(r'\b(?:verifico|constato|observo|analiso)\b', sentence_lower):
            return "analise"
        elif re.search(r'\b(?:conforme|segundo|de acordo)\b', sentence_lower):
            return "fundamentacao"
        elif re.search(r'\b(?:portanto|logo|assim|destarte)\b', sentence_lower):
            return "conclusao"
        else:
            return "geral"
    
    def extract_paragraph_patterns(self, text: str) -> List[str]:
        """Extrai padrões de organização de parágrafos"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        patterns = []
        
        for paragraph in paragraphs:
            if len(paragraph) < 50:  # Skip muito curtos
                continue
                
            # Analisar início do parágrafo
            first_sentence = paragraph.split('.')[0] + '.'
            
            # Analisar estrutura geral
            sentence_count = len(re.split(r'[.!?]+', paragraph))
            
            # Identificar função do parágrafo
            function = self._identify_paragraph_function(paragraph)
            
            patterns.append({
                "function": function,
                "start": first_sentence,
                "sentence_count": sentence_count,
                "length": len(paragraph),
                "example": paragraph[:200] + "..." if len(paragraph) > 200 else paragraph
            })
        
        return patterns
    
    def _identify_paragraph_function(self, paragraph: str) -> str:
        """Identifica função do parágrafo na argumentação"""
        para_lower = paragraph.lower()
        
        if re.search(r'\b(?:relatório|histórico|síntese)\b', para_lower):
            return "relatorio"
        elif re.search(r'\b(?:fundamentação|análise|exame)\b', para_lower):
            return "fundamentacao"
        elif re.search(r'\b(?:dispositivo|julgo|condeno)\b', para_lower):
            return "dispositivo"
        elif re.search(r'\b(?:preliminar|questão prévia)\b', para_lower):
            return "preliminar"
        elif re.search(r'\b(?:mérito|questão de fundo)\b', para_lower):
            return "merito"
        elif re.search(r'\b(?:prova|evidência|documento)\b', para_lower):
            return "prova"
        else:
            return "geral"
    
    def extract_transition_phrases(self, text: str) -> List[Tuple[str, int]]:
        """Extrai frases de transição características"""
        transitions = []
        
        # Padrões de transição comuns
        transition_patterns = [
            r"\b(?:nesse sentido|nessa esteira|nesse diapasão|nessa toada)\b",
            r"\b(?:diante do exposto|ante o exposto|posto isto)\b",
            r"\b(?:por outro lado|ademais|outrossim|além disso)\b",
            r"\b(?:com efeito|de fato|efetivamente|realmente)\b",
            r"\b(?:contudo|entretanto|todavia|no entanto|porém)\b",
            r"\b(?:assim sendo|dessa forma|destarte|portanto)\b",
            r"\b(?:passo ao exame|analiso|verifico|constato)\b"
        ]
        
        for pattern in transition_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Normalizar matches
                normalized = [m.lower().strip() for m in matches]
                frequency = len(normalized)
                transitions.append((pattern, frequency))
        
        return sorted(transitions, key=lambda x: x[1], reverse=True)
    
    def extract_citation_styles(self, text: str) -> List[Dict[str, Any]]:
        """Extrai estilos de citação de dispositivos legais"""
        citations = []
        
        # Padrões de citação
        citation_patterns = {
            "artigo_clt": r"(?:art\.?\s*|artigo\s+)(\d+)(?:,?\s*(?:§|parágrafo)\s*(\d+))?.*?CLT",
            "artigo_cf": r"(?:art\.?\s*|artigo\s+)(\d+)(?:,?\s*(?:inciso\s+)?([IVX]+))?.*?(?:CF|Constituição)",
            "sumula_tst": r"Súmula\s+(?:n?º?\s*)?(\d+).*?TST",
            "oj_tst": r"Orientação\s+Jurisprudencial\s+(?:n?º?\s*)?(\d+).*?TST",
            "artigo_cpc": r"(?:art\.?\s*|artigo\s+)(\d+).*?CPC"
        }
        
        for citation_type, pattern in citation_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                citations.append({
                    "type": citation_type,
                    "count": len(matches),
                    "numbers": [m[0] if isinstance(m, tuple) else m for m in matches],
                    "examples": re.findall(pattern, text, re.IGNORECASE)[:3]
                })
        
        return citations
    
    def extract_decision_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extrai padrões de decisão por tipo de pedido"""
        decision_patterns = defaultdict(list)
        
        # Identificar seções de dispositivo
        dispositivo_match = re.search(r'(?:III\s*[-–]\s*)?DISPOSITIVO(.*?)(?:\n\n|$)', text, re.DOTALL | re.IGNORECASE)
        
        if dispositivo_match:
            dispositivo_text = dispositivo_match.group(1)
            
            # Padrões por tipo de decisão
            patterns = {
                "procedente": r"JULGO\s+PROCEDENTE(?:\s+EM\s+PARTE)?.*?(?:\.|;)",
                "improcedente": r"JULGO\s+IMPROCEDENTE.*?(?:\.|;)",
                "condeno": r"CONDENO.*?(?:\.|;)",
                "absolvo": r"ABSOLVO.*?(?:\.|;)",
                "determino": r"DETERMINO.*?(?:\.|;)",
                "defiro": r"DEFIRO.*?(?:\.|;)",
                "indefiro": r"INDEFIRO.*?(?:\.|;)"
            }
            
            for decision_type, pattern in patterns.items():
                matches = re.findall(pattern, dispositivo_text, re.IGNORECASE | re.DOTALL)
                if matches:
                    decision_patterns[decision_type].extend(matches)
        
        return dict(decision_patterns)
    
    def calculate_statistical_summary(self, sentences: List[str], paragraphs: List[str]) -> Dict[str, Any]:
        """Calcula resumo estatístico do estilo"""
        # Estatísticas de frases
        sentence_lengths = [len(s.split()) for s in sentences if len(s.split()) > 3]
        
        # Estatísticas de parágrafos
        paragraph_lengths = [len(p.split()) for p in paragraphs if len(p.split()) > 10]
        
        # Análise de complexidade
        complex_sentences = [s for s in sentences if len(s.split()) > 25]
        
        return {
            "sentence_stats": {
                "count": len(sentence_lengths),
                "avg_length": statistics.mean(sentence_lengths) if sentence_lengths else 0,
                "median_length": statistics.median(sentence_lengths) if sentence_lengths else 0,
                "max_length": max(sentence_lengths) if sentence_lengths else 0,
                "min_length": min(sentence_lengths) if sentence_lengths else 0
            },
            "paragraph_stats": {
                "count": len(paragraph_lengths),
                "avg_length": statistics.mean(paragraph_lengths) if paragraph_lengths else 0,
                "median_length": statistics.median(paragraph_lengths) if paragraph_lengths else 0
            },
            "complexity": {
                "complex_sentence_ratio": len(complex_sentences) / len(sentences) if sentences else 0,
                "avg_complex_length": statistics.mean([len(s.split()) for s in complex_sentences]) if complex_sentences else 0
            }
        }
    
    def analyze_judge_style(self, sentence_texts: List[str]) -> JudgeStyleProfile:
        """Análise completa do estilo da juíza"""
        self.logger.info(f"Analisando estilo em {len(sentence_texts)} sentenças...")
        
        # Combinar todas as sentenças
        combined_text = "\n\n".join(sentence_texts)
        
        # Extrair todos os padrões
        sentence_patterns = self.extract_sentence_patterns(combined_text)
        paragraph_patterns = self.extract_paragraph_patterns(combined_text)
        transition_phrases = self.extract_transition_phrases(combined_text)
        citation_styles = self.extract_citation_styles(combined_text)
        decision_patterns = self.extract_decision_patterns(combined_text)
        
        # Dividir em frases e parágrafos para estatísticas
        sentences = [s.strip() for s in re.split(r'[.!?]+', combined_text) if s.strip()]
        paragraphs = [p.strip() for p in combined_text.split('\n\n') if p.strip()]
        
        # Calcular estatísticas
        stats = self.calculate_statistical_summary(sentences, paragraphs)
        
        # Identificar padrões linguísticos
        linguistic_patterns = []
        for pattern_type, patterns in self.linguistic_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, combined_text, re.IGNORECASE)
                if matches:
                    linguistic_patterns.append(StylePattern(
                        pattern_type="linguistic",
                        pattern=pattern,
                        frequency=len(matches),
                        contexts=[pattern_type],
                        confidence=min(1.0, len(matches) / 10),  # Normalizar
                        examples=matches[:5]
                    ))
        
        # Identificar padrões estruturais
        structural_patterns = []
        for pattern_type, patterns in self.structural_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, combined_text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    structural_patterns.append(StylePattern(
                        pattern_type="structural",
                        pattern=pattern,
                        frequency=len(matches),
                        contexts=[pattern_type],
                        confidence=min(1.0, len(matches) / 5),
                        examples=matches[:3]
                    ))
        
        # Padrões de expressões legais
        legal_patterns = []
        for citation in citation_styles:
            legal_patterns.append(StylePattern(
                pattern_type="legal",
                pattern=citation["type"],
                frequency=citation["count"],
                contexts=["citation"],
                confidence=min(1.0, citation["count"] / 20),
                examples=[str(ex) for ex in citation["examples"][:3]]
            ))
        
        self.logger.info(f"Análise concluída: {len(linguistic_patterns)} padrões linguísticos, {len(structural_patterns)} estruturais")
        
        return JudgeStyleProfile(
            linguistic_patterns=linguistic_patterns,
            structural_patterns=structural_patterns,
            legal_expressions=legal_patterns,
            sentence_structures=[str(p) for p in sentence_patterns],
            paragraph_patterns=[str(p) for p in paragraph_patterns],
            transition_phrases=[str(t) for t in transition_phrases],
            citation_styles=[str(c) for c in citation_styles],
            decision_patterns=decision_patterns,
            statistical_summary=stats
        )
    
    def save_style_profile(self, profile: JudgeStyleProfile, output_path: Path):
        """Salva perfil de estilo em JSON estruturado"""
        # Converter para dicionário serializável
        profile_dict = {
            "linguistic_patterns": [
                {
                    "pattern_type": p.pattern_type,
                    "pattern": p.pattern,
                    "frequency": p.frequency,
                    "contexts": p.contexts,
                    "confidence": p.confidence,
                    "examples": p.examples
                } for p in profile.linguistic_patterns
            ],
            "structural_patterns": [
                {
                    "pattern_type": p.pattern_type,
                    "pattern": p.pattern,
                    "frequency": p.frequency,
                    "contexts": p.contexts,
                    "confidence": p.confidence,
                    "examples": p.examples
                } for p in profile.structural_patterns
            ],
            "legal_expressions": [
                {
                    "pattern_type": p.pattern_type,
                    "pattern": p.pattern,
                    "frequency": p.frequency,
                    "contexts": p.contexts,
                    "confidence": p.confidence,
                    "examples": p.examples
                } for p in profile.legal_expressions
            ],
            "sentence_structures": profile.sentence_structures,
            "paragraph_patterns": profile.paragraph_patterns,
            "transition_phrases": profile.transition_phrases,
            "citation_styles": profile.citation_styles,
            "decision_patterns": profile.decision_patterns,
            "statistical_summary": profile.statistical_summary
        }
        
        # Salvar JSON
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(profile_dict, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Perfil de estilo salvo: {output_path}")
        
        return profile_dict
