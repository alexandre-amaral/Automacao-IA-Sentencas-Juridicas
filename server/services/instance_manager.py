"""
Gerenciador de Instâncias Isoladas
Garante isolamento completo entre diferentes processos
Cada processo tem seu próprio namespace e RAG isolado
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from uuid import uuid4
import chromadb
from chromadb.config import Settings

class InstanceManager:
    """Gerencia instâncias isoladas por processo"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_storage = Path(__file__).resolve().parent.parent / "storage"
        self.rag_storage = self.base_storage / "rag_storage"
        self.template_master = self.rag_storage / "template_master"
        
        # Criar estrutura base
        self._initialize_storage_structure()
    
    def _initialize_storage_structure(self):
        """Inicializa estrutura de storage"""
        self.rag_storage.mkdir(parents=True, exist_ok=True)
        self.template_master.mkdir(exist_ok=True)
        
        # Inicializar template master se não existir
        if not (self.template_master / "initialized.flag").exists():
            self._create_master_template()
            (self.template_master / "initialized.flag").touch()
            self.logger.info("✅ Template master inicializado")
    
    def _create_master_template(self):
        """Cria template master imutável para consistência"""
        
        # Estrutura padrão de sentenças trabalhistas
        estrutura_sentenca = {
            "sections": {
                "relatorio": {
                    "title": "I - RELATÓRIO",
                    "order": 1,
                    "subsections": [
                        "Identificação das partes",
                        "Síntese da petição inicial", 
                        "Síntese da contestação",
                        "Síntese da instrução probatória"
                    ]
                },
                "fundamentacao": {
                    "title": "II - FUNDAMENTAÇÃO",
                    "order": 2,
                    "subsections": [
                        "Das Preliminares",
                        "Das Prejudiciais de Mérito", 
                        "Do Mérito"
                    ]
                },
                "dispositivo": {
                    "title": "III - DISPOSITIVO",
                    "order": 3,
                    "subsections": [
                        "Decisão final",
                        "Condenações específicas",
                        "Custas e honorários"
                    ]
                }
            }
        }
        
        # Estilo da juíza (padrões de linguagem)
        estilo_juiza = {
            "linguagem": {
                "formal": True,
                "tecnica": True,
                "tempo_verbal": "presente_indicativo",
                "conectores_tipicos": [
                    "Outrossim", "Ademais", "Destarte", "Com efeito",
                    "Nesse sentido", "Assim sendo", "Por conseguinte",
                    "Nesta toada", "De outra banda", "Portanto"
                ]
            },
            "estrutura_paragrafo": {
                "introducao_topica": True,
                "desenvolvimento_argumentativo": True,
                "conclusao_transicional": True
            },
            "citacoes": {
                "formato_dispositivos": "Art. {numero} da {lei}",
                "formato_jurisprudencia": "Súmula {numero} do {tribunal}",
                "formato_doutrina": "Conforme ensina {autor}"
            },
            "expressoes_recorrentes": [
                "Vislumbro que", "Destarte", "É cediço que", 
                "Ademais", "Nesse diapasão", "Pelos fundamentos expostos"
            ]
        }
        
        # Conhecimento jurídico base
        conhecimento_base = {
            "dispositivos_clt": [
                "Art. 7º da CF/88 - Direitos dos trabalhadores",
                "Art. 59 da CLT - Horas extras",
                "Art. 71 da CLT - Intervalo intrajornada",
                "Art. 477 da CLT - Verbas rescisórias"
            ],
            "jurisprudencia_consolidada": [
                "Súmula 85 do TST - Horas extras habituais",
                "Súmula 437 do TST - Intervalo intrajornada",
                "OJ 342 da SDI-1 do TST - Horas in itinere"
            ],
            "tipos_pedidos_comuns": [
                "horas_extras", "intervalo_intrajornada", "verbas_rescisórias",
                "danos_morais", "adicional_noturno", "dsr_sobre_horas"
            ]
        }
        
        # Salvar templates no master
        (self.template_master / "estrutura_sentenca.json").write_text(
            json.dumps(estrutura_sentenca, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        (self.template_master / "estilo_juiza.json").write_text(
            json.dumps(estilo_juiza, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        (self.template_master / "conhecimento_base.json").write_text(
            json.dumps(conhecimento_base, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        self.logger.info("📝 Templates master criados")
    
    def create_isolated_instance(self, case_id: str) -> Dict[str, Any]:
        """
        Cria instância completamente isolada para um processo
        
        Args:
            case_id: ID único do caso
            
        Returns:
            Dict com informações da instância criada
        """
        
        try:
            # Criar namespace da instância
            instance_dir = self.rag_storage / f"processo_{case_id}"
            
            if instance_dir.exists():
                self.logger.warning(f"[{case_id}] Instância já existe, recriando...")
                shutil.rmtree(instance_dir)
            
            # Estrutura da instância isolada
            subdirs = [
                "estilo_juiza",      # Cópia local do template master
                "dados_caso_atual",  # Dados únicos deste processo
                "contexto_dialogo",  # Histórico da conversa IA
                "temp_generation",   # Arquivos temporários
                "final_output"       # Resultado final
            ]
            
            for subdir in subdirs:
                (instance_dir / subdir).mkdir(parents=True, exist_ok=True)
            
            # Copiar template master para instância local
            self._copy_master_template_to_instance(instance_dir)
            
            # Criar ChromaDB isolado para esta instância
            self._create_isolated_chromadb(case_id, instance_dir)
            
            # Criar metadados da instância
            instance_metadata = {
                "case_id": case_id,
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "namespace": f"processo_{case_id}",
                "directories": {
                    "instance_root": str(instance_dir),
                    "estilo_juiza": str(instance_dir / "estilo_juiza"),
                    "dados_caso": str(instance_dir / "dados_caso_atual"),
                    "contexto_dialogo": str(instance_dir / "contexto_dialogo"),
                    "temp_generation": str(instance_dir / "temp_generation"),
                    "final_output": str(instance_dir / "final_output")
                }
            }
            
            # Salvar metadados
            (instance_dir / "instance_metadata.json").write_text(
                json.dumps(instance_metadata, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            
            self.logger.info(f"🔒 [{case_id}] Instância isolada criada: {instance_dir}")
            return instance_metadata
            
        except Exception as e:
            self.logger.error(f"❌ [{case_id}] Erro ao criar instância: {str(e)}")
            raise Exception(f"Falha na criação da instância: {str(e)}")
    
    def _copy_master_template_to_instance(self, instance_dir: Path):
        """Copia template master para instância local"""
        
        estilo_dir = instance_dir / "estilo_juiza"
        
        # Copiar todos os arquivos do template master
        for template_file in self.template_master.glob("*.json"):
            if template_file.name != "initialized.flag":
                shutil.copy2(template_file, estilo_dir / template_file.name)
        
        # Criar timestamp de cópia
        (estilo_dir / "copied_at.txt").write_text(
            datetime.now().isoformat(), encoding='utf-8'
        )
    
    def _create_isolated_chromadb(self, case_id: str, instance_dir: Path):
        """Cria ChromaDB isolado para a instância"""
        
        chroma_dir = instance_dir / "chroma_db"
        chroma_dir.mkdir(exist_ok=True)
        
        # Criar cliente ChromaDB isolado
        client = chromadb.PersistentClient(
            path=str(chroma_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Criar coleções específicas da instância
        collections = [
            f"estilo_juiza_{case_id}",
            f"caso_atual_{case_id}",
            f"contexto_dialogo_{case_id}"
        ]
        
        for collection_name in collections:
            try:
                client.create_collection(
                    name=collection_name,
                    metadata={
                        "case_id": case_id,
                        "created_at": datetime.now().isoformat(),
                        "type": "isolated_instance"
                    }
                )
            except Exception:
                # Coleção já existe
                pass
        
        # Salvar configuração do ChromaDB
        chroma_config = {
            "case_id": case_id,
            "path": str(chroma_dir),
            "collections": collections,
            "created_at": datetime.now().isoformat()
        }
        
        (instance_dir / "chroma_config.json").write_text(
            json.dumps(chroma_config, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        self.logger.info(f"🗃️ [{case_id}] ChromaDB isolado criado")
    
    def get_instance_info(self, case_id: str) -> Dict[str, Any]:
        """Recupera informações de uma instância existente"""
        
        instance_dir = self.rag_storage / f"processo_{case_id}"
        
        if not instance_dir.exists():
            raise ValueError(f"Instância {case_id} não encontrada")
        
        metadata_file = instance_dir / "instance_metadata.json"
        if not metadata_file.exists():
            raise ValueError(f"Metadados da instância {case_id} não encontrados")
        
        return json.loads(metadata_file.read_text(encoding='utf-8'))
    
    def list_active_instances(self) -> List[Dict[str, Any]]:
        """Lista todas as instâncias ativas"""
        
        instances = []
        
        for instance_dir in self.rag_storage.glob("processo_*"):
            if instance_dir.is_dir():
                metadata_file = instance_dir / "instance_metadata.json"
                if metadata_file.exists():
                    try:
                        metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
                        instances.append(metadata)
                    except Exception as e:
                        self.logger.warning(f"Erro ao ler metadados de {instance_dir}: {e}")
        
        return instances
    
    def cleanup_instance(self, case_id: str, force: bool = False):
        """Remove instância isolada (cleanup)"""
        
        instance_dir = self.rag_storage / f"processo_{case_id}"
        
        if not instance_dir.exists():
            self.logger.warning(f"[{case_id}] Instância não encontrada para cleanup")
            return
        
        try:
            # Verificar idade da instância (30 dias)
            metadata_file = instance_dir / "instance_metadata.json"
            if metadata_file.exists() and not force:
                metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
                created_at = datetime.fromisoformat(metadata['created_at'])
                age = datetime.now() - created_at
                
                if age < timedelta(days=30):
                    self.logger.info(f"[{case_id}] Instância muito recente, pulando cleanup")
                    return
            
            # Backup antes de remover (opcional)
            backup_dir = self.rag_storage / "cleanup_backup" / f"processo_{case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_dir.parent.mkdir(exist_ok=True)
            shutil.move(str(instance_dir), str(backup_dir))
            
            self.logger.info(f"🧹 [{case_id}] Instância movida para backup: {backup_dir}")
            
        except Exception as e:
            self.logger.error(f"❌ [{case_id}] Erro no cleanup: {str(e)}")
    
    def validate_isolation(self, case_id: str) -> Dict[str, bool]:
        """Valida isolamento da instância"""
        
        validation_results = {
            "instance_exists": False,
            "directories_isolated": False,
            "chromadb_isolated": False,
            "no_contamination": False,
            "template_consistent": False
        }
        
        try:
            instance_dir = self.rag_storage / f"processo_{case_id}"
            
            # Verificar existência
            validation_results["instance_exists"] = instance_dir.exists()
            
            if not validation_results["instance_exists"]:
                return validation_results
            
            # Verificar diretórios isolados
            required_dirs = ["estilo_juiza", "dados_caso_atual", "contexto_dialogo", "temp_generation", "final_output"]
            validation_results["directories_isolated"] = all(
                (instance_dir / subdir).exists() for subdir in required_dirs
            )
            
            # Verificar ChromaDB isolado
            chroma_config_file = instance_dir / "chroma_config.json"
            validation_results["chromadb_isolated"] = chroma_config_file.exists()
            
            # Verificar template consistente
            estilo_dir = instance_dir / "estilo_juiza"
            required_templates = ["estrutura_sentenca.json", "estilo_juiza.json", "conhecimento_base.json"]
            validation_results["template_consistent"] = all(
                (estilo_dir / template).exists() for template in required_templates
            )
            
            # Verificar não contaminação (simplificado)
            metadata_file = instance_dir / "instance_metadata.json"
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
                validation_results["no_contamination"] = metadata.get('case_id') == case_id
            
            self.logger.info(f"✅ [{case_id}] Validação de isolamento concluída")
            return validation_results
            
        except Exception as e:
            self.logger.error(f"❌ [{case_id}] Erro na validação: {str(e)}")
            return validation_results
