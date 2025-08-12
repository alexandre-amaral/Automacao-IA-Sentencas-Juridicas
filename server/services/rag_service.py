"""
Serviço RAG para gerenciar base de conhecimento de casos
Salva e recupera informações processadas pelos modelos
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import chromadb
from chromadb.config import Settings
import uuid
from datetime import datetime

from .gemini_processor import ProcessoEstruturado

class RAGService:
    """Serviço para gerenciar base de conhecimento RAG"""
    
    def __init__(self):
        """Inicializa o serviço RAG"""
        self.logger = logging.getLogger(__name__)
        
        # Inicializar ChromaDB
        chroma_dir = Path(__file__).resolve().parent.parent / "chroma_db"
        chroma_dir.mkdir(exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(chroma_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Coleções
        self.collection_casos = self._get_or_create_collection("casos_processados")
        self.collection_estrutura = self._get_or_create_collection("estrutura_sentencas")
        
        # Inicializar conhecimento base se não existir
        self._inicializar_conhecimento_base()
    
    def _get_or_create_collection(self, name: str):
        """Obtém ou cria uma coleção"""
        try:
            return self.client.get_collection(name=name)
        except:
            return self.client.create_collection(
                name=name,
                metadata={"description": f"Coleção {name}"}
            )
    
    def _inicializar_conhecimento_base(self):
        """Inicializa conhecimento base sobre estrutura de sentenças"""
        
        # Verificar se já existe conhecimento base
        try:
            result = self.collection_estrutura.get(ids=["estrutura_base"])
            if result['ids']:
                self.logger.info("Conhecimento base já inicializado")
                return
        except:
            pass
        
        # Conhecimento base sobre estrutura de sentenças
        conhecimento_estrutura = {
            "estrutura_sentenca": """
ESTRUTURA OBRIGATÓRIA DE SENTENÇAS TRABALHISTAS:

1. RELATÓRIO
   - Identificação das partes
   - Resumo da petição inicial
   - Resumo da contestação
   - Resumo da instrução probatória

2. FUNDAMENTAÇÃO
   - Análise das preliminares (se houver)
   - Análise do mérito
   - Exame das provas
   - Aplicação do direito
   - Citação de jurisprudência

3. DISPOSITIVO
   - Decisão final
   - Condenações específicas
   - Custas processuais
   - Honorários advocatícios
""",
            "estilo_redacao": """
ESTILO DE REDAÇÃO JUDICIAL:

- Linguagem formal e técnica
- Uso correto de terminologia jurídica
- Paragrafação adequada
- Conectores lógicos
- Citação precisa de dispositivos legais
- Fundamentação clara e objetiva
- Conclusões motivadas
""",
            "precedentes_importantes": """
PRECEDENTES RELEVANTES:

- Súmulas do TST
- Orientações Jurisprudenciais
- Decisões do STF em matéria trabalhista
- Jurisprudência consolidada dos TRTs
""",
            "legislacao_base": """
LEGISLAÇÃO FUNDAMENTAL:

- Consolidação das Leis do Trabalho (CLT)
- Constituição Federal de 1988
- Código de Processo Civil (aplicação subsidiária)
- Leis específicas (13.467/2017, etc.)
"""
        }
        
        # Salvar conhecimento base
        self.collection_estrutura.add(
            documents=[json.dumps(conhecimento_estrutura, ensure_ascii=False)],
            metadatas=[{
                "tipo": "conhecimento_base",
                "descricao": "Estrutura e regras para redação de sentenças",
                "criado_em": datetime.now().isoformat()
            }],
            ids=["estrutura_base"]
        )
        
        self.logger.info("Conhecimento base inicializado")
    
    def salvar_conhecimento_caso(
        self, 
        processo_estruturado: ProcessoEstruturado, 
        analise_audiencia: Optional[Dict[str, Any]], 
        case_id: str
    ):
        """
        Salva conhecimento do caso atual na base RAG
        
        Args:
            processo_estruturado: Informações estruturadas do processo
            analise_audiencia: Análise da audiência (se houver)
            case_id: ID do caso
        """
        
        try:
            # Preparar documento do conhecimento
            conhecimento_caso = {
                "case_id": case_id,
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
            texto_busca = self._criar_texto_busca(conhecimento_caso)
            
            # Salvar na coleção
            self.collection_casos.add(
                documents=[texto_busca],
                metadatas=[{
                    "case_id": case_id,
                    "tipo": "conhecimento_caso",
                    "numero_processo": processo_estruturado.numero_processo,
                    "total_pedidos": len(processo_estruturado.pedidos),
                    "tem_audiencia": analise_audiencia is not None,
                    "criado_em": datetime.now().isoformat()
                }],
                ids=[f"caso_{case_id}"]
            )
            
            # Também salvar o JSON completo em arquivo para backup
            caso_dir = Path(__file__).resolve().parent.parent / "storage" / case_id
            caso_dir.mkdir(exist_ok=True)
            
            conhecimento_path = caso_dir / "conhecimento_rag.json"
            conhecimento_path.write_text(
                json.dumps(conhecimento_caso, indent=2, ensure_ascii=False), 
                encoding='utf-8'
            )
            
            self.logger.info(f"[{case_id}] Conhecimento salvo no RAG")
            
        except Exception as e:
            self.logger.error(f"[{case_id}] Erro ao salvar conhecimento: {str(e)}")
            raise Exception(f"Erro ao salvar no RAG: {str(e)}")
    
    def _criar_texto_busca(self, conhecimento_caso: Dict[str, Any]) -> str:
        """Cria texto otimizado para busca semântica"""
        
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
            
            depoentes = ", ".join([
                f"{d.get('nome', 'N/A')} ({d.get('tipo', 'N/A')})" 
                for d in audiencia.get('depoentes', [])
            ])
            
            temas = ", ".join([
                t.get('tema', '') 
                for t in audiencia.get('pontos_controvertidos', [])
            ])
            
            texto_busca += f"""
Audiência - Depoentes: {depoentes}
Temas controvertidos: {temas}
"""
        
        return texto_busca.strip()
    
    def recuperar_conhecimento_caso(self, case_id: str) -> Dict[str, Any]:
        """
        Recupera conhecimento completo de um caso
        
        Args:
            case_id: ID do caso
            
        Returns:
            Dict com todo o conhecimento do caso
        """
        
        try:
            # Recuperar da coleção RAG
            result = self.collection_casos.get(
                ids=[f"caso_{case_id}"],
                include=["metadatas", "documents"]
            )
            
            if not result['ids']:
                raise ValueError(f"Conhecimento do caso {case_id} não encontrado no RAG")
            
            # Recuperar também do arquivo JSON backup
            caso_dir = Path(__file__).resolve().parent.parent / "storage" / case_id
            conhecimento_path = caso_dir / "conhecimento_rag.json"
            
            if conhecimento_path.exists():
                conhecimento_completo = json.loads(conhecimento_path.read_text(encoding='utf-8'))
            else:
                # Fallback: criar conhecimento básico dos metadados
                metadata = result['metadatas'][0]
                conhecimento_completo = {
                    "case_id": case_id,
                    "metadata": metadata,
                    "documento_busca": result['documents'][0]
                }
            
            # Adicionar conhecimento sobre estrutura de sentenças
            estrutura_result = self.collection_estrutura.get(ids=["estrutura_base"])
            if estrutura_result['ids']:
                conhecimento_estrutura = json.loads(estrutura_result['documents'][0])
                conhecimento_completo["estrutura_sentenca"] = conhecimento_estrutura
            
            self.logger.info(f"[{case_id}] Conhecimento recuperado do RAG")
            return conhecimento_completo
            
        except Exception as e:
            self.logger.error(f"[{case_id}] Erro ao recuperar conhecimento: {str(e)}")
            raise Exception(f"Erro ao recuperar do RAG: {str(e)}")
    
    def buscar_casos_similares(self, case_id: str, limite: int = 3) -> List[Dict[str, Any]]:
        """
        Busca casos similares para referência
        
        Args:
            case_id: ID do caso atual
            limite: Número máximo de casos similares
            
        Returns:
            Lista de casos similares
        """
        
        try:
            # Recuperar documento do caso atual
            result = self.collection_casos.get(
                ids=[f"caso_{case_id}"],
                include=["documents"]
            )
            
            if not result['ids']:
                return []
            
            documento_atual = result['documents'][0]
            
            # Buscar casos similares
            similar_results = self.collection_casos.query(
                query_texts=[documento_atual],
                n_results=limite + 1,  # +1 para excluir o próprio caso
                include=["metadatas", "documents", "distances"]
            )
            
            casos_similares = []
            for i, (doc, metadata, distance) in enumerate(zip(
                similar_results['documents'][0],
                similar_results['metadatas'][0],
                similar_results['distances'][0]
            )):
                # Pular o próprio caso
                if metadata.get('case_id') == case_id:
                    continue
                
                casos_similares.append({
                    "case_id": metadata.get('case_id'),
                    "numero_processo": metadata.get('numero_processo'),
                    "similaridade": 1 - distance,  # Converter distância em similaridade
                    "documento": doc[:500] + "..." if len(doc) > 500 else doc
                })
                
                if len(casos_similares) >= limite:
                    break
            
            self.logger.info(f"[{case_id}] Encontrados {len(casos_similares)} casos similares")
            return casos_similares
            
        except Exception as e:
            self.logger.error(f"[{case_id}] Erro ao buscar casos similares: {str(e)}")
            return []
