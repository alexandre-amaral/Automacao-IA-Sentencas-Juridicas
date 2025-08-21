"""
RAG Service Isolado por Instância
Versão do RAG que trabalha exclusivamente dentro do namespace de uma instância
Garante zero contaminação entre diferentes processos
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import chromadb
from chromadb.config import Settings
from datetime import datetime

from .gemini_processor import ProcessoEstruturado
from .instance_manager import InstanceManager

class IsolatedRAGService:
    """RAG Service isolado por instância de processo"""
    
    def __init__(self, case_id: str):
        """
        Inicializa RAG isolado para uma instância específica
        
        Args:
            case_id: ID do caso para isolamento
        """
        self.case_id = case_id
        self.logger = logging.getLogger(__name__)
        
        # Inicializar InstanceManager
        self.instance_manager = InstanceManager()
        
        # Verificar se instância existe
        try:
            self.instance_info = self.instance_manager.get_instance_info(case_id)
            self.instance_dir = Path(self.instance_info['directories']['instance_root'])
        except ValueError:
            # Criar instância se não existir
            self.logger.info(f"[{case_id}] Criando nova instância isolada")
            self.instance_info = self.instance_manager.create_isolated_instance(case_id)
            self.instance_dir = Path(self.instance_info['directories']['instance_root'])
        
        # Inicializar ChromaDB isolado
        self._initialize_isolated_chromadb()
    
    def _initialize_isolated_chromadb(self):
        """Inicializa ChromaDB isolado para esta instância"""
        
        chroma_dir = self.instance_dir / "chroma_db"
        
        try:
            self.client = chromadb.PersistentClient(
                path=str(chroma_dir),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Obter ou criar coleções isoladas
            self.collection_estilo = self._get_or_create_collection(f"estilo_juiza_{self.case_id}")
            self.collection_caso = self._get_or_create_collection(f"caso_atual_{self.case_id}")
            self.collection_dialogo = self._get_or_create_collection(f"contexto_dialogo_{self.case_id}")
            
            # Inicializar conhecimento base se vazio
            self._initialize_estilo_knowledge()
            
            self.logger.info(f"🔒 [{self.case_id}] RAG isolado inicializado")
            
        except Exception as e:
            self.logger.error(f"❌ [{self.case_id}] Erro ao inicializar RAG: {str(e)}")
            raise Exception(f"Falha na inicialização do RAG isolado: {str(e)}")
    
    def _get_or_create_collection(self, name: str):
        """Obtém ou cria uma coleção isolada"""
        try:
            return self.client.get_collection(name=name)
        except Exception:
            return self.client.create_collection(
                name=name,
                metadata={
                    "case_id": self.case_id,
                    "created_at": datetime.now().isoformat(),
                    "type": "isolated"
                }
            )
    
    def _initialize_estilo_knowledge(self):
        """Inicializa conhecimento sobre estilo da juíza na instância"""
        
        try:
            # Verificar se já foi inicializado
            result = self.collection_estilo.get(ids=[f"estilo_base_{self.case_id}"])
            if result['ids']:
                self.logger.info(f"[{self.case_id}] Estilo da juíza já inicializado")
                return
        except Exception:
            pass
        
        # Carregar templates da instância local
        estilo_dir = self.instance_dir / "estilo_juiza"
        
        conhecimento_estilo = {}
        
        # Carregar todos os templates
        for template_file in estilo_dir.glob("*.json"):
            if template_file.name != "copied_at.txt":
                try:
                    template_content = json.loads(template_file.read_text(encoding='utf-8'))
                    conhecimento_estilo[template_file.stem] = template_content
                except Exception as e:
                    self.logger.warning(f"Erro ao carregar {template_file}: {e}")
        
        if conhecimento_estilo:
            # Criar documento para busca semântica
            estilo_texto = self._create_estilo_search_text(conhecimento_estilo)
            
            # Salvar na coleção isolada
            self.collection_estilo.add(
                documents=[estilo_texto],
                metadatas=[{
                    "case_id": self.case_id,
                    "tipo": "estilo_juiza",
                    "templates_carregados": ",".join(conhecimento_estilo.keys()),
                    "inicializado_em": datetime.now().isoformat()
                }],
                ids=[f"estilo_base_{self.case_id}"]
            )
            
            self.logger.info(f"📝 [{self.case_id}] Estilo da juíza inicializado na instância")
    
    def _create_estilo_search_text(self, conhecimento_estilo: Dict[str, Any]) -> str:
        """Cria texto otimizado para busca do estilo da juíza"""
        
        texto_partes = []
        
        # Extrair informações relevantes para busca
        if 'estilo_juiza' in conhecimento_estilo:
            estilo = conhecimento_estilo['estilo_juiza']
            
            if 'conectores_tipicos' in estilo.get('linguagem', {}):
                conectores = ", ".join(estilo['linguagem']['conectores_tipicos'])
                texto_partes.append(f"Conectores típicos: {conectores}")
            
            if 'expressoes_recorrentes' in estilo:
                expressoes = ", ".join(estilo['expressoes_recorrentes'])
                texto_partes.append(f"Expressões recorrentes: {expressoes}")
        
        if 'estrutura_sentenca' in conhecimento_estilo:
            estrutura = conhecimento_estilo['estrutura_sentenca']
            secoes = ", ".join(estrutura.get('sections', {}).keys())
            texto_partes.append(f"Estrutura de seções: {secoes}")
        
        if 'conhecimento_base' in conhecimento_estilo:
            base = conhecimento_estilo['conhecimento_base']
            if 'tipos_pedidos_comuns' in base:
                pedidos = ", ".join(base['tipos_pedidos_comuns'])
                texto_partes.append(f"Tipos de pedidos: {pedidos}")
        
        return "\n".join(texto_partes)
    
    def salvar_conhecimento_caso_isolado(
        self, 
        processo_estruturado: ProcessoEstruturado, 
        analise_audiencia: Optional[Dict[str, Any]] = None
    ):
        """
        Salva conhecimento do caso atual na instância isolada
        
        Args:
            processo_estruturado: Informações estruturadas do processo
            analise_audiencia: Análise da audiência (se houver)
        """
        
        try:
            # Preparar conhecimento do caso
            conhecimento_caso = {
                "case_id": self.case_id,
                "timestamp": datetime.now().isoformat(),
                "processo": {
                    "numero": processo_estruturado.numero_processo,
                    "partes": [
                        {
                            "nome": p.nome,
                            "tipo": p.tipo,
                            "qualificacao": p.qualificacao
                        }
                        for p in processo_estruturado.partes
                    ],
                    "pedidos": [
                        {
                            "descricao": p.descricao,
                            "categoria": p.categoria,
                            "valor_estimado": p.valor_estimado
                        }
                        for p in processo_estruturado.pedidos
                    ],
                    "fatos_relevantes": [
                        {
                            "descricao": f.descricao,
                            "fonte": f.fonte
                        }
                        for f in processo_estruturado.fatos_relevantes
                    ],
                    "periodo_contratual": processo_estruturado.periodo_contratual,
                    "valor_causa": processo_estruturado.valor_causa,
                    "fundamentacao_resumida": processo_estruturado.fundamentacao_resumida
                },
                "audiencia": analise_audiencia if analise_audiencia else None
            }
            
            # Criar texto para busca semântica
            texto_busca = self._criar_texto_busca_caso(conhecimento_caso)
            
            # Salvar na coleção isolada
            self.collection_caso.add(
                documents=[texto_busca],
                metadatas=[{
                    "case_id": self.case_id,
                    "tipo": "conhecimento_caso",
                    "numero_processo": processo_estruturado.numero_processo,
                    "total_pedidos": len(processo_estruturado.pedidos),
                    "tem_audiencia": analise_audiencia is not None,
                    "salvo_em": datetime.now().isoformat()
                }],
                ids=[f"caso_{self.case_id}"]
            )
            
            # Backup em arquivo JSON na instância
            dados_caso_dir = self.instance_dir / "dados_caso_atual"
            conhecimento_path = dados_caso_dir / "conhecimento_caso.json"
            conhecimento_path.write_text(
                json.dumps(conhecimento_caso, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            
            self.logger.info(f"💾 [{self.case_id}] Conhecimento do caso salvo na instância isolada")
            
        except Exception as e:
            self.logger.error(f"❌ [{self.case_id}] Erro ao salvar conhecimento: {str(e)}")
            raise Exception(f"Erro ao salvar conhecimento isolado: {str(e)}")
    
    def _criar_texto_busca_caso(self, conhecimento_caso: Dict[str, Any]) -> str:
        """Cria texto otimizado para busca do caso"""
        
        processo = conhecimento_caso["processo"]
        
        # Construir texto descritivo
        partes_texto = ", ".join([f"{p['nome']} ({p['tipo']})" for p in processo["partes"]])
        
        pedidos_texto = ". ".join([
            f"{p['categoria']}: {p['descricao']}" 
            for p in processo["pedidos"]
        ])
        
        fatos_texto = ". ".join([
            f.get('descricao', '') 
            for f in processo.get("fatos_relevantes", [])
        ])
        
        texto_busca = f"""
Processo: {processo.get('numero', 'N/A')}
Partes: {partes_texto}
Pedidos: {pedidos_texto}
Fatos: {fatos_texto}
Período: {processo.get('periodo_contratual', 'N/A')}
Valor: {processo.get('valor_causa', 'N/A')}
"""
        
        # Adicionar informações da audiência se houver
        if conhecimento_caso.get("audiencia"):
            audiencia = conhecimento_caso["audiencia"]
            
            if 'depoentes' in audiencia:
                depoentes = ", ".join([
                    f"{d.get('nome', 'N/A')} ({d.get('tipo', 'N/A')})" 
                    for d in audiencia.get('depoentes', [])
                ])
                texto_busca += f"\nAudiência - Depoentes: {depoentes}"
            
            if 'pontos_controvertidos' in audiencia:
                temas = ", ".join([
                    t.get('tema', '') 
                    for t in audiencia.get('pontos_controvertidos', [])
                ])
                texto_busca += f"\nTemas controvertidos: {temas}"
        
        return texto_busca.strip()
    
    def salvar_contexto_dialogo(self, dialogo_step: str, conteudo: Dict[str, Any]):
        """
        Salva contexto do diálogo Claude↔Gemini na instância
        
        Args:
            dialogo_step: Etapa do diálogo (etapa1, etapa2, etapa3)
            conteudo: Conteúdo do diálogo (perguntas, respostas, análises)
        """
        
        try:
            dialogo_id = f"dialogo_{dialogo_step}_{self.case_id}"
            
            # Criar texto de busca para o diálogo
            dialogo_texto = self._criar_texto_busca_dialogo(dialogo_step, conteudo)
            
            # Salvar na coleção de diálogo
            self.collection_dialogo.add(
                documents=[dialogo_texto],
                metadatas=[{
                    "case_id": self.case_id,
                    "tipo": "contexto_dialogo",
                    "etapa": dialogo_step,
                    "timestamp": datetime.now().isoformat()
                }],
                ids=[dialogo_id]
            )
            
            # Backup em arquivo na instância
            contexto_dir = self.instance_dir / "contexto_dialogo"
            dialogo_path = contexto_dir / f"{dialogo_step}.json"
            dialogo_path.write_text(
                json.dumps(conteudo, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            
            self.logger.info(f"💬 [{self.case_id}] Contexto do diálogo {dialogo_step} salvo")
            
        except Exception as e:
            self.logger.error(f"❌ [{self.case_id}] Erro ao salvar diálogo: {str(e)}")
            raise Exception(f"Erro ao salvar contexto de diálogo: {str(e)}")
    
    def _criar_texto_busca_dialogo(self, dialogo_step: str, conteudo: Dict[str, Any]) -> str:
        """Cria texto de busca para contexto de diálogo"""
        
        partes_texto = [f"Etapa: {dialogo_step}"]
        
        if 'perguntas_claude' in conteudo:
            perguntas = ". ".join(conteudo['perguntas_claude'])
            partes_texto.append(f"Perguntas Claude: {perguntas}")
        
        if 'respostas_gemini' in conteudo:
            if isinstance(conteudo['respostas_gemini'], dict):
                resumo_respostas = str(conteudo['respostas_gemini'])[:500]
                partes_texto.append(f"Respostas Gemini: {resumo_respostas}")
        
        if 'analises' in conteudo:
            analises = ". ".join(conteudo.get('analises', []))
            partes_texto.append(f"Análises: {analises}")
        
        return "\n".join(partes_texto)
    
    def recuperar_conhecimento_completo_isolado(self) -> Dict[str, Any]:
        """
        Recupera TODO o conhecimento da instância isolada
        
        Returns:
            Dict com conhecimento completo (estilo + caso + diálogo)
        """
        
        try:
            conhecimento_completo = {
                "case_id": self.case_id,
                "recuperado_em": datetime.now().isoformat(),
                "estilo_juiza": {},
                "conhecimento_caso": {},
                "contexto_dialogo": {}
            }
            
            # Recuperar estilo da juíza
            try:
                estilo_result = self.collection_estilo.get(
                    ids=[f"estilo_base_{self.case_id}"],
                    include=["documents", "metadatas"]
                )
                if estilo_result['ids']:
                    conhecimento_completo["estilo_juiza"] = {
                        "documento": estilo_result['documents'][0],
                        "metadata": estilo_result['metadatas'][0]
                    }
                    
                    # Carregar também os templates detalhados
                    estilo_dir = self.instance_dir / "estilo_juiza"
                    for template_file in estilo_dir.glob("*.json"):
                        template_name = template_file.stem
                        template_content = json.loads(template_file.read_text(encoding='utf-8'))
                        conhecimento_completo["estilo_juiza"][template_name] = template_content
            except Exception as e:
                self.logger.warning(f"Erro ao recuperar estilo: {e}")
            
            # Recuperar conhecimento do caso
            try:
                caso_result = self.collection_caso.get(
                    ids=[f"caso_{self.case_id}"],
                    include=["documents", "metadatas"]
                )
                if caso_result['ids']:
                    conhecimento_completo["conhecimento_caso"] = {
                        "documento": caso_result['documents'][0],
                        "metadata": caso_result['metadatas'][0]
                    }
                    
                    # Carregar também o JSON detalhado
                    caso_path = self.instance_dir / "dados_caso_atual" / "conhecimento_caso.json"
                    if caso_path.exists():
                        caso_detalhado = json.loads(caso_path.read_text(encoding='utf-8'))
                        conhecimento_completo["conhecimento_caso"]["detalhes"] = caso_detalhado
            except Exception as e:
                self.logger.warning(f"Erro ao recuperar caso: {e}")
            
            # Recuperar contexto de diálogo
            try:
                contexto_dir = self.instance_dir / "contexto_dialogo"
                for dialogo_file in contexto_dir.glob("*.json"):
                    etapa = dialogo_file.stem
                    dialogo_content = json.loads(dialogo_file.read_text(encoding='utf-8'))
                    conhecimento_completo["contexto_dialogo"][etapa] = dialogo_content
            except Exception as e:
                self.logger.warning(f"Erro ao recuperar diálogo: {e}")
            
            self.logger.info(f"📚 [{self.case_id}] Conhecimento completo recuperado da instância")
            return conhecimento_completo
            
        except Exception as e:
            self.logger.error(f"❌ [{self.case_id}] Erro ao recuperar conhecimento: {str(e)}")
            raise Exception(f"Erro na recuperação do conhecimento isolado: {str(e)}")
    
    def buscar_contexto_relevante(self, query: str, categoria: str = "all", limite: int = 5) -> List[Dict[str, Any]]:
        """
        Busca contexto relevante na instância isolada
        
        Args:
            query: Consulta de busca
            categoria: Categoria específica (estilo, caso, dialogo, all)
            limite: Número máximo de resultados
            
        Returns:
            Lista de resultados relevantes
        """
        
        resultados = []
        
        try:
            if categoria in ["estilo", "all"]:
                try:
                    estilo_results = self.collection_estilo.query(
                        query_texts=[query],
                        n_results=limite,
                        include=["documents", "metadatas", "distances"]
                    )
                    
                    for doc, metadata, distance in zip(
                        estilo_results['documents'][0],
                        estilo_results['metadatas'][0], 
                        estilo_results['distances'][0]
                    ):
                        resultados.append({
                            "categoria": "estilo_juiza",
                            "documento": doc,
                            "metadata": metadata,
                            "relevancia": 1 - distance,
                            "case_id": self.case_id
                        })
                except Exception:
                    pass
            
            if categoria in ["caso", "all"]:
                try:
                    caso_results = self.collection_caso.query(
                        query_texts=[query],
                        n_results=limite,
                        include=["documents", "metadatas", "distances"]
                    )
                    
                    for doc, metadata, distance in zip(
                        caso_results['documents'][0],
                        caso_results['metadatas'][0],
                        caso_results['distances'][0]
                    ):
                        resultados.append({
                            "categoria": "conhecimento_caso",
                            "documento": doc,
                            "metadata": metadata,
                            "relevancia": 1 - distance,
                            "case_id": self.case_id
                        })
                except Exception:
                    pass
            
            if categoria in ["dialogo", "all"]:
                try:
                    dialogo_results = self.collection_dialogo.query(
                        query_texts=[query],
                        n_results=limite,
                        include=["documents", "metadatas", "distances"]
                    )
                    
                    for doc, metadata, distance in zip(
                        dialogo_results['documents'][0],
                        dialogo_results['metadatas'][0],
                        dialogo_results['distances'][0]
                    ):
                        resultados.append({
                            "categoria": "contexto_dialogo",
                            "documento": doc,
                            "metadata": metadata,
                            "relevancia": 1 - distance,
                            "case_id": self.case_id
                        })
                except Exception:
                    pass
            
            # Ordenar por relevância
            resultados.sort(key=lambda x: x['relevancia'], reverse=True)
            
            self.logger.info(f"🔍 [{self.case_id}] Busca retornou {len(resultados)} resultados")
            return resultados[:limite]
            
        except Exception as e:
            self.logger.error(f"❌ [{self.case_id}] Erro na busca: {str(e)}")
            return []
    
    def validate_isolation(self) -> Dict[str, bool]:
        """Valida isolamento da instância RAG"""
        
        return self.instance_manager.validate_isolation(self.case_id)
