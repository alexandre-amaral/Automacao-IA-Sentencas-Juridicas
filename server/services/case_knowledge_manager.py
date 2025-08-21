"""
Gerenciador de Conhecimento do Caso Atual
Storage versionado e contextual de toda informação específica do processo
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import uuid

@dataclass
class ProcessAnalysisVersion:
    """Versão de análise do processo"""
    version_id: str
    timestamp: str
    analysis_type: str  # gemini_extraction, claude_analysis, dialogue_step
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    content_hash: str

@dataclass 
class DialogueStep:
    """Passo do diálogo Claude-Gemini"""
    step_number: int
    timestamp: str
    question: str
    answer: str
    question_type: str  # facts, legal_foundation, evidence, etc.
    answer_confidence: float
    extracted_concepts: List[str]
    references_used: List[str]
    step_hash: str

@dataclass
class DecisionContext:
    """Contexto acumulado de decisões por seção"""
    section: str  # relatorio, fundamentacao, dispositivo
    decisions_made: List[Dict[str, Any]]
    reasoning_chain: List[str]
    legal_foundations: List[str]
    evidence_used: List[str]
    confidence_score: float
    last_updated: str

class CaseKnowledgeManager:
    """Gerenciador completo do conhecimento do caso atual"""
    
    def __init__(self, case_id: str, storage_path: Path):
        self.case_id = case_id
        self.storage_path = storage_path / f"processo_{case_id}"
        self.logger = logging.getLogger(__name__)
        
        # Estrutura de storage
        self.process_data_path = self.storage_path / "dados_processo"
        self.dialogue_path = self.storage_path / "dialogo_contexto"
        self.decisions_path = self.storage_path / "contexto_decisoes"
        self.versions_path = self.storage_path / "versoes_analise"
        
        # Criar estrutura
        for path in [self.process_data_path, self.dialogue_path, self.decisions_path, self.versions_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Cache ativo
        self._current_dialogue = []
        self._decision_contexts = {}
        self._analysis_versions = []
        
        # Carregar dados existentes
        self._load_existing_data()
    
    def save_process_transcription(self, transcription_text: str, document_type: str = "processo") -> str:
        """Salva transcrição completa do processo com versionamento"""
        # Gerar hash para detectar mudanças
        content_hash = hashlib.sha256(transcription_text.encode('utf-8')).hexdigest()[:16]
        
        # Criar versão
        version = ProcessAnalysisVersion(
            version_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now().isoformat(),
            analysis_type="transcription",
            content={
                "document_type": document_type,
                "transcription": transcription_text,
                "character_count": len(transcription_text),
                "word_count": len(transcription_text.split())
            },
            metadata={
                "source": "document_extraction",
                "quality": "original",
                "processing_method": "automated"
            },
            content_hash=content_hash
        )
        
        # Salvar versão
        version_file = self.versions_path / f"transcription_{document_type}_{version.version_id}.json"
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(version), f, ensure_ascii=False, indent=2)
        
        # Salvar como atual também
        current_file = self.process_data_path / f"transcricao_{document_type}.txt"
        current_file.write_text(transcription_text, encoding='utf-8')
        
        # Metadata do arquivo atual
        metadata_file = self.process_data_path / f"transcricao_{document_type}_metadata.json"
        metadata = {
            "version_id": version.version_id,
            "content_hash": content_hash,
            "last_updated": version.timestamp,
            "character_count": len(transcription_text),
            "word_count": len(transcription_text.split())
        }
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        self._analysis_versions.append(version)
        self.logger.info(f"Transcrição salva: {document_type} - {len(transcription_text)} chars - versão {version.version_id}")
        
        return version.version_id
    
    def save_hearing_transcription(self, transcription_text: str, audio_metadata: Dict[str, Any] = None) -> str:
        """Salva transcrição da audiência com metadados de áudio"""
        content_hash = hashlib.sha256(transcription_text.encode('utf-8')).hexdigest()[:16]
        
        version = ProcessAnalysisVersion(
            version_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now().isoformat(),
            analysis_type="hearing_transcription",
            content={
                "transcription": transcription_text,
                "character_count": len(transcription_text),
                "word_count": len(transcription_text.split()),
                "audio_metadata": audio_metadata or {}
            },
            metadata={
                "source": "whisper_api",
                "quality": "high_accuracy",
                "processing_method": "ai_transcription"
            },
            content_hash=content_hash
        )
        
        # Salvar versão
        version_file = self.versions_path / f"hearing_transcription_{version.version_id}.json"
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(version), f, ensure_ascii=False, indent=2)
        
        # Salvar como atual
        current_file = self.process_data_path / "transcricao_audiencia.txt"
        current_file.write_text(transcription_text, encoding='utf-8')
        
        # Metadata
        metadata_file = self.process_data_path / "transcricao_audiencia_metadata.json"
        metadata = {
            "version_id": version.version_id,
            "content_hash": content_hash,
            "last_updated": version.timestamp,
            "character_count": len(transcription_text),
            "audio_metadata": audio_metadata or {}
        }
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        self._analysis_versions.append(version)
        self.logger.info(f"Transcrição audiência salva: {len(transcription_text)} chars - versão {version.version_id}")
        
        return version.version_id
    
    def save_dialogue_step(self, 
                          question: str, 
                          answer: str, 
                          question_type: str,
                          answer_confidence: float = 0.8,
                          extracted_concepts: List[str] = None,
                          references_used: List[str] = None) -> DialogueStep:
        """Salva passo do diálogo Claude-Gemini"""
        
        step_number = len(self._current_dialogue) + 1
        step_hash = hashlib.sha256(f"{question}{answer}".encode('utf-8')).hexdigest()[:12]
        
        dialogue_step = DialogueStep(
            step_number=step_number,
            timestamp=datetime.now().isoformat(),
            question=question,
            answer=answer,
            question_type=question_type,
            answer_confidence=answer_confidence,
            extracted_concepts=extracted_concepts or [],
            references_used=references_used or [],
            step_hash=step_hash
        )
        
        # Salvar passo individual
        step_file = self.dialogue_path / f"step_{step_number:03d}_{step_hash}.json"
        with open(step_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(dialogue_step), f, ensure_ascii=False, indent=2)
        
        # Adicionar ao diálogo atual
        self._current_dialogue.append(dialogue_step)
        
        # Salvar histórico completo do diálogo
        self._save_dialogue_history()
        
        # Criar versão de análise do diálogo
        dialogue_version = ProcessAnalysisVersion(
            version_id=f"dialogue_{step_number:03d}_{step_hash[:8]}",
            timestamp=dialogue_step.timestamp,
            analysis_type="dialogue_step",
            content={
                "step_number": step_number,
                "question": question,
                "answer": answer,
                "question_type": question_type,
                "extracted_concepts": extracted_concepts or [],
                "references_used": references_used or []
            },
            metadata={
                "dialogue_context": f"step_{step_number}_of_{len(self._current_dialogue)}",
                "confidence": answer_confidence,
                "hash": step_hash
            },
            content_hash=step_hash
        )
        
        # Salvar versão
        version_file = self.versions_path / f"dialogue_step_{step_number:03d}_{step_hash}.json"
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(dialogue_version), f, ensure_ascii=False, indent=2)
        
        self._analysis_versions.append(dialogue_version)
        
        self.logger.info(f"Diálogo passo {step_number} salvo: {question_type} - confiança {answer_confidence}")
        
        return dialogue_step
    
    def save_decision_context(self, 
                            section: str,
                            decision: Dict[str, Any],
                            reasoning: List[str],
                            legal_foundations: List[str] = None,
                            evidence_used: List[str] = None,
                            confidence: float = 0.8):
        """Salva contexto de decisão por seção da sentença"""
        
        if section not in self._decision_contexts:
            self._decision_contexts[section] = DecisionContext(
                section=section,
                decisions_made=[],
                reasoning_chain=[],
                legal_foundations=[],
                evidence_used=[],
                confidence_score=0.0,
                last_updated=""
            )
        
        context = self._decision_contexts[section]
        
        # Adicionar nova decisão
        context.decisions_made.append({
            "decision": decision,
            "timestamp": datetime.now().isoformat(),
            "confidence": confidence
        })
        
        # Atualizar cadeia de raciocínio
        context.reasoning_chain.extend(reasoning)
        
        # Atualizar fundamentações legais
        if legal_foundations:
            context.legal_foundations.extend(legal_foundations)
            # Remover duplicatas
            context.legal_foundations = list(set(context.legal_foundations))
        
        # Atualizar evidências
        if evidence_used:
            context.evidence_used.extend(evidence_used)
            context.evidence_used = list(set(context.evidence_used))
        
        # Atualizar confiança (média ponderada)
        total_confidence = sum(d["confidence"] for d in context.decisions_made)
        context.confidence_score = total_confidence / len(context.decisions_made)
        
        context.last_updated = datetime.now().isoformat()
        
        # Salvar contexto atualizado
        context_file = self.decisions_path / f"context_{section}.json"
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(context), f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Contexto de decisão salvo: {section} - confiança {confidence:.2f}")
    
    def get_dialogue_history(self, max_steps: Optional[int] = None) -> List[DialogueStep]:
        """Obtém histórico do diálogo"""
        if max_steps:
            return self._current_dialogue[-max_steps:]
        return self._current_dialogue.copy()
    
    def get_decision_context(self, section: str) -> Optional[DecisionContext]:
        """Obtém contexto de decisão de uma seção"""
        return self._decision_contexts.get(section)
    
    def get_all_decision_contexts(self) -> Dict[str, DecisionContext]:
        """Obtém todos os contextos de decisão"""
        return self._decision_contexts.copy()
    
    def get_analysis_versions(self, analysis_type: Optional[str] = None) -> List[ProcessAnalysisVersion]:
        """Obtém versões de análise"""
        if analysis_type:
            return [v for v in self._analysis_versions if v.analysis_type == analysis_type]
        return self._analysis_versions.copy()
    
    def get_current_transcriptions(self) -> Dict[str, str]:
        """Obtém transcrições atuais"""
        transcriptions = {}
        
        # Processo
        processo_file = self.process_data_path / "transcricao_processo.txt"
        if processo_file.exists():
            transcriptions["processo"] = processo_file.read_text(encoding='utf-8')
        
        # Audiência
        audiencia_file = self.process_data_path / "transcricao_audiencia.txt"
        if audiencia_file.exists():
            transcriptions["audiencia"] = audiencia_file.read_text(encoding='utf-8')
        
        return transcriptions
    
    def search_dialogue_by_topic(self, topic: str) -> List[DialogueStep]:
        """Busca no diálogo por tópico"""
        results = []
        topic_lower = topic.lower()
        
        for step in self._current_dialogue:
            if (topic_lower in step.question.lower() or 
                topic_lower in step.answer.lower() or
                topic_lower in step.question_type.lower() or
                any(topic_lower in concept.lower() for concept in step.extracted_concepts)):
                results.append(step)
        
        return results
    
    def get_accumulated_knowledge_summary(self) -> Dict[str, Any]:
        """Obtém resumo do conhecimento acumulado"""
        transcriptions = self.get_current_transcriptions()
        
        return {
            "case_id": self.case_id,
            "transcriptions": {
                "processo": {
                    "available": "processo" in transcriptions,
                    "length": len(transcriptions.get("processo", ""))
                },
                "audiencia": {
                    "available": "audiencia" in transcriptions,
                    "length": len(transcriptions.get("audiencia", ""))
                }
            },
            "dialogue": {
                "total_steps": len(self._current_dialogue),
                "question_types": list(set(step.question_type for step in self._current_dialogue)),
                "avg_confidence": sum(step.answer_confidence for step in self._current_dialogue) / len(self._current_dialogue) if self._current_dialogue else 0
            },
            "decisions": {
                "sections_analyzed": list(self._decision_contexts.keys()),
                "total_decisions": sum(len(ctx.decisions_made) for ctx in self._decision_contexts.values()),
                "avg_confidence": sum(ctx.confidence_score for ctx in self._decision_contexts.values()) / len(self._decision_contexts) if self._decision_contexts else 0
            },
            "analysis_versions": {
                "total": len(self._analysis_versions),
                "by_type": self._count_by_type([v.analysis_type for v in self._analysis_versions])
            }
        }
    
    def _save_dialogue_history(self):
        """Salva histórico completo do diálogo"""
        history_file = self.dialogue_path / "dialogue_history.json"
        dialogue_data = [asdict(step) for step in self._current_dialogue]
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump({
                "case_id": self.case_id,
                "total_steps": len(self._current_dialogue),
                "last_updated": datetime.now().isoformat(),
                "dialogue_steps": dialogue_data
            }, f, ensure_ascii=False, indent=2)
    
    def _load_existing_data(self):
        """Carrega dados existentes do disco"""
        # Carregar histórico do diálogo
        history_file = self.dialogue_path / "dialogue_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._current_dialogue = [DialogueStep(**step) for step in data.get("dialogue_steps", [])]
                    self.logger.info(f"Carregados {len(self._current_dialogue)} passos do diálogo")
            except Exception as e:
                self.logger.error(f"Erro ao carregar histórico do diálogo: {e}")
        
        # Carregar contextos de decisão
        for context_file in self.decisions_path.glob("context_*.json"):
            try:
                with open(context_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    context = DecisionContext(**data)
                    self._decision_contexts[context.section] = context
            except Exception as e:
                self.logger.error(f"Erro ao carregar contexto {context_file}: {e}")
        
        # Carregar versões de análise
        for version_file in self.versions_path.glob("*.json"):
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    version = ProcessAnalysisVersion(**data)
                    self._analysis_versions.append(version)
            except Exception as e:
                self.logger.error(f"Erro ao carregar versão {version_file}: {e}")
        
        self.logger.info(f"Dados carregados: {len(self._current_dialogue)} diálogo, {len(self._decision_contexts)} contextos, {len(self._analysis_versions)} versões")
    
    def _count_by_type(self, items: List[str]) -> Dict[str, int]:
        """Conta itens por tipo"""
        counts = {}
        for item in items:
            counts[item] = counts.get(item, 0) + 1
        return counts
    
    def cleanup_old_versions(self, keep_latest: int = 10):
        """Limpa versões antigas mantendo apenas as mais recentes"""
        # Ordenar por timestamp
        sorted_versions = sorted(self._analysis_versions, key=lambda x: x.timestamp, reverse=True)
        
        # Manter apenas as mais recentes
        versions_to_keep = sorted_versions[:keep_latest]
        versions_to_delete = sorted_versions[keep_latest:]
        
        # Deletar arquivos das versões antigas
        for version in versions_to_delete:
            for version_file in self.versions_path.glob(f"*{version.version_id}*"):
                try:
                    version_file.unlink()
                    self.logger.info(f"Versão antiga deletada: {version_file.name}")
                except Exception as e:
                    self.logger.error(f"Erro ao deletar versão {version_file}: {e}")
        
        # Atualizar lista em memória
        self._analysis_versions = versions_to_keep
        
        self.logger.info(f"Cleanup concluído: mantidas {len(versions_to_keep)} versões, deletadas {len(versions_to_delete)}")
    
    def export_case_knowledge(self, output_file: Path):
        """Exporta todo conhecimento do caso para um arquivo"""
        export_data = {
            "case_id": self.case_id,
            "export_timestamp": datetime.now().isoformat(),
            "transcriptions": self.get_current_transcriptions(),
            "dialogue_history": [asdict(step) for step in self._current_dialogue],
            "decision_contexts": {k: asdict(v) for k, v in self._decision_contexts.items()},
            "analysis_versions": [asdict(v) for v in self._analysis_versions],
            "summary": self.get_accumulated_knowledge_summary()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Conhecimento do caso exportado: {output_file}")
        return export_data
