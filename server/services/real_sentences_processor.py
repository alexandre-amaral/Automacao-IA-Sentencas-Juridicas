"""
Processador de Sentenças Reais
Carrega, analisa e processa sentenças reais da juíza para criar templates precisos
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import fitz  # PyMuPDF
from docx import Document
import hashlib
from datetime import datetime
from dataclasses import dataclass, asdict

from .judge_style_analyzer import JudgeStyleAnalyzer, JudgeStyleProfile
from .legal_knowledge_manager import LegalKnowledgeManager
from .optimized_embedding_service import OptimizedEmbeddingService

@dataclass
class ProcessedSentence:
    """Sentença processada com metadados"""
    file_path: str
    case_number: str
    file_type: str  # docx, doc, pdf
    content: str
    year: str
    content_hash: str
    processed_at: str
    word_count: int
    char_count: int
    sections: Dict[str, str]  # relatorio, fundamentacao, dispositivo
    legal_citations: List[str]
    parties: Dict[str, List[str]]  # reclamante, reclamada
    decision_summary: str

class RealSentencesProcessor:
    """Processador completo de sentenças reais da juíza"""
    
    def __init__(self, project_root: Path):
        self.logger = logging.getLogger(__name__)
        self.project_root = project_root
        
        # Caminhos das pastas de sentenças
        self.sentences_paths = [
            project_root / "Sentenças_2023",
            project_root / "Sentenças_2024", 
            project_root / "Sentenças_2025"
        ]
        
        # Storage processado
        self.processed_storage = project_root / "server" / "storage" / "processed_sentences"
        self.processed_storage.mkdir(parents=True, exist_ok=True)
        
        # Componentes de análise
        self.style_analyzer = JudgeStyleAnalyzer()
        self.embedding_service = OptimizedEmbeddingService()
        
        # Cache
        self._processed_sentences = {}
        self._style_profile = None
        
    def extract_text_from_file(self, file_path: Path) -> str:
        """Extrai texto de arquivo (PDF, DOCX, DOC)"""
        try:
            if file_path.suffix.lower() == '.pdf':
                # PDF com PyMuPDF
                doc = fitz.open(str(file_path))
                text = ""
                for page in doc:
                    text += page.get_text("text") + "\\n"
                doc.close()
                return text.strip()
                
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                # DOCX/DOC com python-docx
                try:
                    doc = Document(str(file_path))
                    text = '\\n'.join([par.text for par in doc.paragraphs if par.text.strip()])
                    return text.strip()
                except Exception as e:
                    self.logger.warning(f"Erro python-docx em {file_path}, tentando fallback: {e}")
                    # Fallback: tentar como texto puro
                    return file_path.read_text(encoding='utf-8', errors='ignore')
            
            else:
                self.logger.warning(f"Tipo de arquivo não suportado: {file_path.suffix}")
                return ""
                
        except Exception as e:
            self.logger.error(f"Erro ao extrair texto de {file_path}: {e}")
            return ""
    
    def parse_case_number(self, filename: str) -> str:
        """Extrai número do processo do nome do arquivo"""
        # Padrão: 0000667-76.2023.5.09.0010
        import re
        pattern = r'(\\d{7}-\\d{2}\\.\\d{4}\\.\\d\\.\\d{2}\\.\\d{4})'
        match = re.search(pattern, filename)
        if match:
            return match.group(1)
        return filename.split('.')[0]  # Fallback
    
    def extract_year_from_filename(self, filename: str) -> str:
        """Extrai ano do nome do arquivo ou caminho"""
        import re
        # Tentar extrair do número do processo
        pattern = r'\\d{7}-\\d{2}\\.(\\d{4})\\.\\d\\.\\d{2}\\.\\d{4}'
        match = re.search(pattern, filename)
        if match:
            return match.group(1)
        
        # Tentar extrair do nome da pasta
        if "2023" in filename or "Sentenças_2023" in filename:
            return "2023"
        elif "2024" in filename or "Sentenças_2024" in filename:
            return "2024"
        elif "2025" in filename or "Sentenças_2025" in filename:
            return "2025"
        
        return "unknown"
    
    def identify_sections(self, text: str) -> Dict[str, str]:
        """Identifica seções da sentença"""
        import re
        sections = {}
        
        # Normalizar texto
        text_normalized = re.sub(r'\\s+', ' ', text)
        
        # Padrões de seções
        patterns = {
            "relatorio": [
                r'(?:I\\s*[-–]\\s*)?RELATÓRIO(.*?)(?:(?:II\\s*[-–]\\s*)?FUNDAMENTAÇÃO|(?:II\\s*[-–]\\s*)?VOTO|$)',
                r'VISTOS.*?AUTOS(.*?)(?:FUNDAMENTAÇÃO|VOTO|$)',
                r'Trata-se de(.*?)(?:FUNDAMENTAÇÃO|Passo ao exame|$)'
            ],
            "fundamentacao": [
                r'(?:II\\s*[-–]\\s*)?(?:FUNDAMENTAÇÃO|VOTO)(.*?)(?:(?:III\\s*[-–]\\s*)?DISPOSITIVO|POSTO ISTO|$)',
                r'Passo ao exame(.*?)(?:DISPOSITIVO|POSTO ISTO|JULGO|$)'
            ],
            "dispositivo": [
                r'(?:III\\s*[-–]\\s*)?DISPOSITIVO(.*?)$',
                r'POSTO ISTO(.*?)$',
                r'(?:Diante do exposto|Ante o exposto).{0,50}?JULGO(.*?)$'
            ]
        }
        
        for section_name, section_patterns in patterns.items():
            for pattern in section_patterns:
                match = re.search(pattern, text_normalized, re.DOTALL | re.IGNORECASE)
                if match:
                    sections[section_name] = match.group(1).strip()[:2000]  # Limitar tamanho
                    break
        
        return sections
    
    def extract_legal_citations(self, text: str) -> List[str]:
        """Extrai citações legais do texto"""
        import re
        citations = []
        
        patterns = [
            r'(?:art\\.?\\s*|artigo\\s+)(\\d+)(?:,?\\s*(?:§|parágrafo)\\s*(\\d+))?.*?(?:CLT|CF|CPC|CC)',
            r'Súmula\\s+(?:n?º?\\s*)?(\\d+).*?(?:TST|STF|STJ)',
            r'Orientação\\s+Jurisprudencial\\s+(?:n?º?\\s*)?(\\d+).*?TST',
            r'Enunciado\\s+(?:n?º?\\s*)?(\\d+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            citations.extend([str(m) if isinstance(m, str) else str(m[0]) for m in matches])
        
        return list(set(citations))[:20]  # Limitar e remover duplicatas
    
    def extract_parties(self, text: str) -> Dict[str, List[str]]:
        """Extrai partes do processo"""
        import re
        parties = {"reclamante": [], "reclamada": []}
        
        # Padrões para identificar partes
        reclamante_patterns = [
            r'(?:reclamante|autor|requerente)\\s*:?\\s*([A-ZÁÀÁÂÃÄÇÉÈÊËÍÌÎÏÑÓÒÔÕÖÚÙÛÜÝ][\\w\\s]+?)(?:\\s*(?:x|versus|contra)|\\n|,)',
            r'ajuizada\\s+por\\s+([A-ZÁÀÁÂÃÄÇÉÈÊËÍÌÎÏÑÓÒÔÕÖÚÙÛÜÝ][\\w\\s]+?)\\s+(?:x|contra)',
            r'([A-ZÁÀÁÂÃÄÇÉÈÊËÍÌÎÏÑÓÒÔÕÖÚÙÛÜÝ][\\w\\s]+?)\\s+(?:x|versus)\\s+[A-ZÁÀÁÂÃÄÇÉÈÊËÍÌÎÏÑÓÒÔÕÖÚÙÛÜÝ]'
        ]
        
        reclamada_patterns = [
            r'(?:reclamada|ré|requerida)\\s*:?\\s*([A-ZÁÀÁÂÃÄÇÉÈÊËÍÌÎÏÑÓÒÔÕÖÚÙÛÜÝ][\\w\\s\\.]+?)(?:\\n|,|\\.|;)',
            r'(?:x|contra)\\s+([A-ZÁÀÁÂÃÄÇÉÈÊËÍÌÎÏÑÓÒÔÕÖÚÙÛÜÝ][\\w\\s\\.]+?)(?:\\n|,)',
            r'[A-ZÁÀÁÂÃÄÇÉÈÊËÍÌÎÏÑÓÒÔÕÖÚÙÛÜÝ][\\w\\s]+?\\s+(?:x|versus)\\s+([A-ZÁÀÁÂÃÄÇÉÈÊËÍÌÎÏÑÓÒÔÕÖÚÙÛÜÝ][\\w\\s\\.]+?)(?:\\n|,|\\.)'
        ]
        
        for pattern in reclamante_patterns:
            matches = re.findall(pattern, text[:1000], re.IGNORECASE)  # Apenas início do texto
            parties["reclamante"].extend([m.strip() for m in matches if len(m.strip()) > 3])
        
        for pattern in reclamada_patterns:
            matches = re.findall(pattern, text[:1000], re.IGNORECASE)
            parties["reclamada"].extend([m.strip() for m in matches if len(m.strip()) > 3])
        
        # Limpar e limitar
        parties["reclamante"] = list(set(parties["reclamante"]))[:3]
        parties["reclamada"] = list(set(parties["reclamada"]))[:3]
        
        return parties
    
    def extract_decision_summary(self, text: str) -> str:
        """Extrai resumo da decisão"""
        import re
        
        # Procurar por padrões de decisão
        decision_patterns = [
            r'JULGO\\s+(PROCEDENTE|IMPROCEDENTE|PARCIALMENTE\\s+PROCEDENTE).*?(?:\\.|\\n)',
            r'(?:CONDENO|ABSOLVO|DETERMINO).*?(?:\\.|\\n)',
            r'(?:Diante do exposto|Ante o exposto).{0,100}?(?:JULGO|CONDENO|ABSOLVO).*?(?:\\.|\\n)'
        ]
        
        decisions = []
        for pattern in decision_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            decisions.extend(matches[:3])  # Máximo 3 decisões
        
        if decisions:
            return "; ".join([d.strip() for d in decisions])[:300]
        
        return "Decisão não identificada automaticamente"
    
    def process_single_sentence(self, file_path: Path, folder_year: str = None) -> Optional[ProcessedSentence]:
        """Processa uma única sentença"""
        try:
            # Extrair texto
            content = self.extract_text_from_file(file_path)
            if not content or len(content) < 100:
                self.logger.warning(f"Arquivo muito pequeno ou vazio: {file_path}")
                return None
            
            # Metadados básicos
            case_number = self.parse_case_number(file_path.name)
            year = folder_year or self.extract_year_from_filename(str(file_path))
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
            
            # Análises detalhadas
            sections = self.identify_sections(content)
            legal_citations = self.extract_legal_citations(content)
            parties = self.extract_parties(content)
            decision_summary = self.extract_decision_summary(content)
            
            # Criar objeto processado
            processed = ProcessedSentence(
                file_path=str(file_path),
                case_number=case_number,
                file_type=file_path.suffix.lower(),
                content=content,
                year=year,
                content_hash=content_hash,
                processed_at=datetime.now().isoformat(),
                word_count=len(content.split()),
                char_count=len(content),
                sections=sections,
                legal_citations=legal_citations,
                parties=parties,
                decision_summary=decision_summary
            )
            
            self.logger.info(f"✅ Processada: {file_path.name} | {len(content)} chars | {len(sections)} seções")
            return processed
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar {file_path}: {e}")
            return None
    
    def process_all_sentences(self, force_reprocess: bool = False) -> List[ProcessedSentence]:
        """Processa todas as sentenças das pastas"""
        self.logger.info("🚀 Iniciando processamento de sentenças reais...")
        
        all_processed = []
        total_files = 0
        
        for sentences_folder in self.sentences_paths:
            if not sentences_folder.exists():
                self.logger.warning(f"Pasta não encontrada: {sentences_folder}")
                continue
            
            folder_year = sentences_folder.name.split('_')[-1]  # Sentenças_2023 -> 2023
            self.logger.info(f"📁 Processando pasta: {sentences_folder} (ano: {folder_year})")
            
            # Processar arquivos da pasta
            for file_path in sentences_folder.glob('*'):
                if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.docx', '.doc']:
                    total_files += 1
                    
                    # Verificar se já foi processado
                    cache_key = f"{file_path.name}_{folder_year}"
                    cache_file = self.processed_storage / f"{cache_key}.json"
                    
                    if not force_reprocess and cache_file.exists():
                        try:
                            # Carregar do cache
                            with open(cache_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                processed = ProcessedSentence(**data)
                                all_processed.append(processed)
                                self.logger.info(f"📋 Cache: {file_path.name}")
                                continue
                        except Exception as e:
                            self.logger.warning(f"Cache inválido para {file_path.name}: {e}")
                    
                    # Processar arquivo
                    processed = self.process_single_sentence(file_path, folder_year)
                    
                    if processed:
                        all_processed.append(processed)
                        
                        # Salvar cache
                        with open(cache_file, 'w', encoding='utf-8') as f:
                            json.dump(asdict(processed), f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"🎉 Processamento concluído: {len(all_processed)}/{total_files} sentenças processadas")
        self._processed_sentences = {s.case_number: s for s in all_processed}
        
        return all_processed
    
    def analyze_judge_style_from_real_sentences(self, processed_sentences: List[ProcessedSentence] = None) -> JudgeStyleProfile:
        """Analisa estilo da juíza a partir das sentenças reais"""
        
        if processed_sentences is None:
            processed_sentences = list(self._processed_sentences.values())
        
        if not processed_sentences:
            self.logger.error("Nenhuma sentença processada disponível para análise de estilo")
            return None
        
        self.logger.info(f"🎨 Analisando estilo da juíza em {len(processed_sentences)} sentenças reais...")
        
        # Extrair textos das sentenças
        sentence_texts = [s.content for s in processed_sentences]
        
        # Análise completa do estilo
        style_profile = self.style_analyzer.analyze_judge_style(sentence_texts)
        
        # Salvar perfil de estilo
        style_file = self.processed_storage / "judge_style_profile.json"
        self.style_analyzer.save_style_profile(style_profile, style_file)
        
        self._style_profile = style_profile
        
        self.logger.info(f"✅ Perfil de estilo da juíza criado: {len(style_profile.linguistic_patterns)} padrões linguísticos")
        
        return style_profile
    
    def create_master_templates_from_real_data(self, processed_sentences: List[ProcessedSentence] = None) -> Dict[str, Any]:
        """Cria templates master a partir dos dados reais"""
        
        if processed_sentences is None:
            processed_sentences = list(self._processed_sentences.values())
        
        if not processed_sentences:
            self.logger.error("Nenhuma sentença para criar templates")
            return {}
        
        self.logger.info(f"📋 Criando templates master a partir de {len(processed_sentences)} sentenças reais...")
        
        # Estatísticas gerais
        total_sentences = len(processed_sentences)
        years = set(s.year for s in processed_sentences)
        
        # Análise de seções
        sections_analysis = self._analyze_sections(processed_sentences)
        
        # Análise de citações legais
        citations_analysis = self._analyze_legal_citations(processed_sentences)
        
        # Análise de partes
        parties_analysis = self._analyze_parties(processed_sentences)
        
        # Análise de decisões
        decisions_analysis = self._analyze_decisions(processed_sentences)
        
        # Criar template master
        master_template = {
            "metadata": {
                "created_from_real_sentences": True,
                "total_sentences_analyzed": total_sentences,
                "years_covered": sorted(list(years)),
                "created_at": datetime.now().isoformat(),
                "content_stats": {
                    "avg_word_count": sum(s.word_count for s in processed_sentences) / total_sentences,
                    "avg_char_count": sum(s.char_count for s in processed_sentences) / total_sentences,
                    "file_types": self._count_by_field(processed_sentences, "file_type")
                }
            },
            "sections_patterns": sections_analysis,
            "legal_citations_patterns": citations_analysis,
            "parties_patterns": parties_analysis,
            "decisions_patterns": decisions_analysis,
            "style_profile": asdict(self._style_profile) if self._style_profile else None
        }
        
        # Salvar template master
        template_file = self.processed_storage / "master_template_from_real_data.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(master_template, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"✅ Template master criado: {template_file}")
        
        return master_template
    
    def _analyze_sections(self, sentences: List[ProcessedSentence]) -> Dict[str, Any]:
        """Analisa padrões das seções"""
        sections_data = {section: [] for section in ["relatorio", "fundamentacao", "dispositivo"]}
        
        for sentence in sentences:
            for section_name, section_content in sentence.sections.items():
                if section_content and len(section_content) > 20:
                    sections_data[section_name].append({
                        "content": section_content[:500],  # Amostra
                        "length": len(section_content),
                        "case": sentence.case_number
                    })
        
        # Estatísticas por seção
        analysis = {}
        for section_name, section_list in sections_data.items():
            if section_list:
                analysis[section_name] = {
                    "total_found": len(section_list),
                    "avg_length": sum(s["length"] for s in section_list) / len(section_list),
                    "coverage": len(section_list) / len(sentences),
                    "examples": section_list[:3]  # Primeiros 3 exemplos
                }
            else:
                analysis[section_name] = {
                    "total_found": 0,
                    "coverage": 0.0
                }
        
        return analysis
    
    def _analyze_legal_citations(self, sentences: List[ProcessedSentence]) -> Dict[str, Any]:
        """Analisa padrões de citações legais"""
        all_citations = []
        for sentence in sentences:
            all_citations.extend(sentence.legal_citations)
        
        # Contar frequência
        citation_counts = {}
        for citation in all_citations:
            citation_counts[citation] = citation_counts.get(citation, 0) + 1
        
        # Top citações
        top_citations = sorted(citation_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            "total_citations": len(all_citations),
            "unique_citations": len(citation_counts),
            "avg_citations_per_sentence": len(all_citations) / len(sentences),
            "most_frequent": top_citations,
            "coverage": len([s for s in sentences if s.legal_citations]) / len(sentences)
        }
    
    def _analyze_parties(self, sentences: List[ProcessedSentence]) -> Dict[str, Any]:
        """Analisa padrões das partes"""
        reclamantes = []
        reclamadas = []
        
        for sentence in sentences:
            reclamantes.extend(sentence.parties.get("reclamante", []))
            reclamadas.extend(sentence.parties.get("reclamada", []))
        
        return {
            "reclamantes": {
                "total": len(reclamantes),
                "unique": len(set(reclamantes)),
                "examples": list(set(reclamantes))[:10]
            },
            "reclamadas": {
                "total": len(reclamadas),
                "unique": len(set(reclamadas)),
                "examples": list(set(reclamadas))[:10]
            }
        }
    
    def _analyze_decisions(self, sentences: List[ProcessedSentence]) -> Dict[str, Any]:
        """Analisa padrões de decisões"""
        decisions = [s.decision_summary for s in sentences if s.decision_summary]
        
        # Classificar tipos de decisão
        decision_types = {"procedente": 0, "improcedente": 0, "parcialmente_procedente": 0, "outros": 0}
        
        for decision in decisions:
            decision_lower = decision.lower()
            if "parcialmente procedente" in decision_lower:
                decision_types["parcialmente_procedente"] += 1
            elif "procedente" in decision_lower:
                decision_types["procedente"] += 1
            elif "improcedente" in decision_lower:
                decision_types["improcedente"] += 1
            else:
                decision_types["outros"] += 1
        
        return {
            "total_decisions": len(decisions),
            "decision_types": decision_types,
            "examples": decisions[:5]
        }
    
    def _count_by_field(self, items: List[Any], field: str) -> Dict[str, int]:
        """Conta itens por campo"""
        counts = {}
        for item in items:
            value = getattr(item, field, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    def get_processed_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas dos dados processados"""
        if not self._processed_sentences:
            return {"error": "Nenhuma sentença processada"}
        
        sentences = list(self._processed_sentences.values())
        
        return {
            "total_sentences": len(sentences),
            "years": self._count_by_field(sentences, "year"),
            "file_types": self._count_by_field(sentences, "file_type"),
            "avg_word_count": sum(s.word_count for s in sentences) / len(sentences),
            "avg_char_count": sum(s.char_count for s in sentences) / len(sentences),
            "sections_coverage": {
                "relatorio": len([s for s in sentences if "relatorio" in s.sections]) / len(sentences),
                "fundamentacao": len([s for s in sentences if "fundamentacao" in s.sections]) / len(sentences),
                "dispositivo": len([s for s in sentences if "dispositivo" in s.sections]) / len(sentences)
            },
            "total_legal_citations": sum(len(s.legal_citations) for s in sentences),
            "style_profile_available": self._style_profile is not None
        }
    
    def export_for_rag_integration(self, output_file: Path) -> Dict[str, Any]:
        """Exporta dados processados para integração com RAG"""
        
        if not self._processed_sentences:
            return {"error": "Nenhuma sentença processada"}
        
        sentences = list(self._processed_sentences.values())
        
        # Preparar dados para RAG
        rag_data = {
            "sentences_for_embeddings": [],
            "style_patterns": [],
            "legal_knowledge": [],
            "templates": {}
        }
        
        # Sentenças para embeddings
        for sentence in sentences:
            rag_data["sentences_for_embeddings"].append({
                "case_number": sentence.case_number,
                "content": sentence.content,
                "sections": sentence.sections,
                "year": sentence.year,
                "word_count": sentence.word_count,
                "legal_citations": sentence.legal_citations,
                "parties": sentence.parties
            })
        
        # Padrões de estilo
        if self._style_profile:
            rag_data["style_patterns"] = asdict(self._style_profile)
        
        # Conhecimento jurídico extraído
        all_citations = []
        for sentence in sentences:
            all_citations.extend(sentence.legal_citations)
        
        citation_counts = {}
        for citation in all_citations:
            citation_counts[citation] = citation_counts.get(citation, 0) + 1
        
        rag_data["legal_knowledge"] = {
            "frequent_citations": sorted(citation_counts.items(), key=lambda x: x[1], reverse=True)[:50],
            "sections_examples": self._get_best_section_examples(sentences)
        }
        
        # Templates derivados
        rag_data["templates"] = self.create_master_templates_from_real_data(sentences)
        
        # Salvar
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(rag_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"📤 Dados exportados para RAG: {output_file}")
        
        return rag_data
    
    def _get_best_section_examples(self, sentences: List[ProcessedSentence]) -> Dict[str, List[str]]:
        """Obtém melhores exemplos de cada seção"""
        examples = {"relatorio": [], "fundamentacao": [], "dispositivo": []}
        
        for section_name in examples.keys():
            # Coletar seções desta categoria
            section_contents = []
            for sentence in sentences:
                if section_name in sentence.sections and sentence.sections[section_name]:
                    content = sentence.sections[section_name]
                    if 100 <= len(content) <= 2000:  # Tamanho razoável
                        section_contents.append(content)
            
            # Selecionar os melhores (por tamanho e qualidade)
            section_contents.sort(key=len, reverse=True)
            examples[section_name] = section_contents[:5]  # Top 5
        
        return examples
