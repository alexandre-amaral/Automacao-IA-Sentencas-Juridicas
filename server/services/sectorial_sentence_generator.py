"""
Gerador de Sentenças Sectoriais - Solução Completa para Sentenças Detalhadas
"""
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .claude_service import ClaudeService
from .gemini_processor import GeminiProcessor, ProcessoEstruturado
from .enhanced_rag_service import EnhancedRAGService

logger = logging.getLogger(__name__)

@dataclass
class SecaoSentenca:
    """Representa uma seção da sentença"""
    titulo: str
    conteudo: str
    ordem: int
    tipo: str  # 'relatorio', 'preliminar', 'merito', 'dispositivo'

class SectorialSentenceGenerator:
    """
    Gerador de sentenças por seções especializadas - solução completa
    que supera limitações de contexto e gera sentenças detalhadas
    """
    
    def __init__(self, case_id: str = None):
        self.claude = ClaudeService()
        self.gemini = GeminiProcessor()
        self.case_id = case_id
        # RAG será inicializado quando necessário
        
    def gerar_sentenca_completa(self, case_id: str, dados_processo, 
                               transcricao_audiencia: str) -> str:
        """
        Gera sentença completa usando abordagem sectorial especializada
        """
        logger.info(f"[{case_id}] Iniciando geração sectorial de sentença")
        
        # Inicializar RAG com case_id específico
        self.case_id = case_id
        self.rag = EnhancedRAGService(case_id)
        
        try:
            # Converter dados para formato padronizado se necessário
            dados_normalizados = self._normalizar_dados_processo(dados_processo)
            
            # 1. ANÁLISE PROBATÓRIA DETALHADA
            analise_probatoria = self._analisar_provas_detalhadamente(
                dados_normalizados, transcricao_audiencia
            )
            
            # 2. GERAÇÃO POR SEÇÕES ESPECIALIZADAS
            secoes = []
            
            # Relatório
            secoes.append(self._gerar_relatorio(dados_normalizados))
            
            # Preliminares (se houver)
            preliminares = dados_normalizados.get('preliminares', [])
            if preliminares:
                secoes.extend(self._gerar_preliminares(dados_normalizados, analise_probatoria))
            
            # Mérito - cada pedido como seção específica
            secoes_merito = self._gerar_secoes_merito(dados_normalizados, analise_probatoria)
            secoes.extend(secoes_merito)
            
            # Seções finais (FGTS, honorários, etc.)
            secoes.extend(self._gerar_secoes_finais(dados_normalizados))
            
            # Dispositivo
            secoes.append(self._gerar_dispositivo(dados_normalizados, secoes_merito))
            
            # 3. MONTAGEM FINAL
            sentenca_completa = self._montar_sentenca_final(secoes)
            
            logger.info(f"[{case_id}] Sentença sectorial gerada: {len(sentenca_completa)} caracteres")
            return sentenca_completa
            
        except Exception as e:
            logger.error(f"[{case_id}] Erro na geração sectorial: {str(e)}")
            raise
    
    def _normalizar_dados_processo(self, dados_processo) -> Dict[str, Any]:
        """Normaliza dados do processo para formato padronizado"""
        
        if isinstance(dados_processo, dict):
            return dados_processo
        
        # Se for objeto ProcessoEstruturado, converter para dict
        return {
            'numero_processo': getattr(dados_processo, 'numero_processo', ''),
            'partes': [
                {
                    'nome': getattr(p, 'nome', ''),
                    'tipo': getattr(p, 'tipo', '')
                } for p in getattr(dados_processo, 'partes', [])
            ],
            'pedidos': [
                {
                    'descricao': getattr(p, 'descricao', ''),
                    'categoria': getattr(p, 'categoria', '')
                } for p in getattr(dados_processo, 'pedidos', [])
            ],
            'fatos_relevantes': [
                {
                    'descricao': getattr(f, 'descricao', ''),
                    'fonte': getattr(f, 'fonte', '')
                } for f in getattr(dados_processo, 'fatos_relevantes', [])
            ],
            'periodo_contratual': getattr(dados_processo, 'periodo_contratual', ''),
            'valor_causa': getattr(dados_processo, 'valor_causa', ''),
            'testemunhas': getattr(dados_processo, 'testemunhas', []),
            'funcao_cargo': getattr(dados_processo, 'funcao_cargo', ''),
            'salario_inicial': getattr(dados_processo, 'salario_inicial', ''),
            'salario_final': getattr(dados_processo, 'salario_final', ''),
            'jornada_contratual': getattr(dados_processo, 'jornada_contratual', '')
        }
    
    def _analisar_provas_detalhadamente(self, dados_processo: Dict[str, Any], 
                                      transcricao: str) -> Dict[str, Any]:
        """Análise probatória detalhada usando Claude especializado"""
        
        prompt_analise = f"""
Você é um juiz experiente analisando provas de um processo trabalhista.

DADOS DO PROCESSO:
- Pedidos: {[p.get('descricao', '') for p in dados_processo.get('pedidos', [])]}
- Testemunhas: {len(dados_processo.get('testemunhas', []))} testemunhas ouvidas
- Fatos Alegados: {[f.get('descricao', '') for f in dados_processo.get('fatos_relevantes', [])]}

TRANSCRIÇÃO DA AUDIÊNCIA:
{transcricao}

TAREFA: Faça uma análise probatória PROFUNDA e DETALHADA, identificando:

1. CONTRADIÇÕES ESPECÍFICAS entre depoimentos
2. PONTOS DE CONVERGÊNCIA e divergência
3. CREDIBILIDADE de cada testemunha
4. ÔNUS PROBATÓRIO para cada alegação
5. SUFICIÊNCIA das provas para cada pedido

Para cada pedido específico, analise:
- Quais provas existem A FAVOR
- Quais provas existem CONTRA
- Se as provas são SUFICIENTES para procedência
- Citações jurisprudenciais aplicáveis (TST Súmulas/OJs)

Seja EXTREMAMENTE DETALHADO - como um juiz real analisaria.
"""

        try:
            response = self.claude.gerar_resposta(prompt_analise)
            return {"analise_detalhada": response}
        except Exception as e:
            logger.error(f"Erro na análise probatória: {str(e)}")
            return {"analise_detalhada": "Análise probatória não disponível"}
    
    def _gerar_relatorio(self, dados_processo: Dict[str, Any]) -> SecaoSentenca:
        """Gera seção RELATÓRIO detalhada"""
        
        prompt_relatorio = f"""
Redija o RELATÓRIO de uma sentença trabalhista com base nos dados:

PROCESSO: {dados_processo.get('numero_processo', '')}
PARTES: {[(p.get('nome', ''), p.get('tipo', '')) for p in dados_processo.get('partes', [])]}
PERÍODO: {dados_processo.get('periodo_contratual', '')}
VALOR DA CAUSA: {dados_processo.get('valor_causa', '')}

PEDIDOS FORMULADOS:
{chr(10).join([f"- {p.get('descricao', '')}" for p in dados_processo.get('pedidos', [])])}

FATOS RELEVANTES:
{chr(10).join([f"- {f.get('descricao', '')}" for f in dados_processo.get('fatos_relevantes', [])])}

INSTRUÇÕES:
1. Siga o modelo clássico de relatório trabalhista
2. Use linguagem técnica e formal
3. Mencione todas as peças processuais principais
4. Inclua valor da causa
5. Use conectores adequados
6. Termine com "É o relatório. Decide-se."

Seja preciso e completo - este é o início da sentença.
"""

        conteudo = self.claude.gerar_resposta(prompt_relatorio)
        return SecaoSentenca(
            titulo="RELATÓRIO",
            conteudo=conteudo,
            ordem=1,
            tipo="relatorio"
        )
    
    def _gerar_preliminares(self, dados_processo: ProcessoEstruturado, 
                           analise_probatoria: Dict[str, Any]) -> List[SecaoSentenca]:
        """Gera seções de preliminares"""
        
        secoes = []
        for i, preliminar in enumerate(dados_processo.preliminares):
            prompt_preliminar = f"""
Analise e decida sobre a preliminar: "{preliminar}"

CONTEXTO DO PROCESSO:
{dados_processo.numero_processo}

ANÁLISE PROBATÓRIA:
{analise_probatoria.get('analise_detalhada', '')[:1000]}...

INSTRUÇÕES:
1. Analise tecnicamente a preliminar
2. Cite fundamentos legais específicos (CLT, CPC, CF/88)
3. Cite precedentes do TST quando aplicável
4. Decida fundamentadamente (acolhe/rejeita)
5. Use linguagem de sentença judicial
6. Seja técnico e preciso

Formate como seção de sentença com fundamentos robustos.
"""
            
            conteudo = self.claude.gerar_resposta(prompt_preliminar)
            secoes.append(SecaoSentenca(
                titulo=f"PRELIMINAR - {preliminar.upper()}",
                conteudo=conteudo,
                ordem=10 + i,
                tipo="preliminar"
            ))
        
        return secoes
    
    def _gerar_secoes_merito(self, dados_processo: ProcessoEstruturado, 
                            analise_probatoria: Dict[str, Any]) -> List[SecaoSentenca]:
        """Gera seções de mérito - cada pedido como seção especializada"""
        
        secoes = []
        
        for i, pedido in enumerate(dados_processo.pedidos):
            # Recupera contexto RAG específico para este pedido
            contexto_rag = self._recuperar_contexto_pedido(pedido.categoria)
            
            prompt_merito = f"""
Você é um JUIZ DO TRABALHO experiente analisando o pedido específico: "{pedido.descricao}"

CATEGORIA: {pedido.categoria}
VALOR ESTIMADO: {pedido.valor_estimado}

DADOS PROCESSUAIS RELEVANTES:
- Período contratual: {dados_processo.periodo_contratual}
- Função: {dados_processo.funcao_cargo}
- Salário: {dados_processo.salario_inicial} → {dados_processo.salario_final}
- Jornada: {dados_processo.jornada_contratual}

FATOS RELEVANTES:
{chr(10).join([f.descricao for f in dados_processo.fatos_relevantes if pedido.categoria.lower() in f.descricao.lower()])}

ANÁLISE PROBATÓRIA DETALHADA:
{analise_probatoria.get('analise_detalhada', '')}

CONTEXTO JURISPRUDENCIAL (RAG):
{contexto_rag}

TAREFA: Redija uma seção de sentença COMPLETA e DETALHADA para este pedido, incluindo:

1. **ALEGAÇÕES** - Síntese precisa do que alega o autor
2. **DEFESA** - Síntese da contestação da ré
3. **ANÁLISE PROBATÓRIA** - Análise detalhada das provas (como no exemplo real)
4. **FUNDAMENTAÇÃO JURÍDICA** - Citações de:
   - Artigos específicos da CLT
   - Súmulas do TST aplicáveis
   - Orientações Jurisprudenciais (OJs)
   - Precedentes do STF quando relevantes
5. **CONCLUSÃO** - Procedente/Improcedente fundamentada

ESTILO:
- Linguagem técnica de sentença judicial
- Análise aprofundada como no exemplo real
- Citar precedentes específicos
- Ser extremamente detalhado
- Mínimo 800 palavras por seção importante

EXEMPLO DE ESTRUTURA (para horas extras):
## DAS HORAS EXTRAS
O reclamante pleiteia... [alegações detalhadas]
A reclamada, por sua vez... [defesa detalhada]

Analisa-se.

[Análise probatória detalhada com contradições específicas]
[Fundamentação jurídica robusta]
[Conclusão fundamentada]

Seja preciso, técnico e completo como uma sentença real.
"""
            
            conteudo = self.claude.gerar_resposta(prompt_merito)
            secoes.append(SecaoSentenca(
                titulo=f"DO(A) {pedido.categoria.upper()}",
                conteudo=conteudo,
                ordem=100 + i,
                tipo="merito"
            ))
        
        return secoes
    
    def _recuperar_contexto_pedido(self, categoria_pedido: str) -> str:
        """Recupera contexto RAG específico para categoria do pedido"""
        try:
            # Verifica se RAG está disponível
            if not hasattr(self, 'rag') or not self.rag:
                return "Contexto jurisprudencial não disponível - RAG não inicializado"
            
            # Busca jurisprudência específica
            resultados = self.rag.query_knowledge(
                query=f"{categoria_pedido} TST Súmula Orientação Jurisprudencial",
                sources=["estilo_juiza", "dialogo_contexto"],
                top_k=5
            )
            
            contexto = ""
            if isinstance(resultados, list):
                for resultado in resultados:
                    if isinstance(resultado, dict):
                        content = resultado.get('content', resultado.get('text', ''))
                        contexto += f"- {content[:200]}...\n"
            
            return contexto if contexto else "Contexto jurisprudencial não encontrado"
        except Exception as e:
            return f"Contexto jurisprudencial não disponível - {str(e)}"
    
    def _gerar_secoes_finais(self, dados_processo: ProcessoEstruturado) -> List[SecaoSentenca]:
        """Gera seções finais (FGTS, Honorários, etc.)"""
        
        secoes_finais = [
            ("FGTS", "Análise de incidência de FGTS sobre parcelas deferidas"),
            ("HONORÁRIOS ADVOCATÍCIOS", "Análise de honorários de sucumbência"),
            ("CONTRIBUIÇÕES SOCIAIS E FISCAIS", "Análise de descontos"),
            ("CORREÇÃO MONETÁRIA E JUROS", "Análise de atualização monetária")
        ]
        
        secoes = []
        for i, (titulo, descricao) in enumerate(secoes_finais):
            prompt_secao = f"""
Redija a seção "{titulo}" de uma sentença trabalhista.

CONTEXTO:
{descricao}

PEDIDOS DEFERIDOS: (considere que alguns pedidos foram deferidos)
VALOR ESTIMADO: {dados_processo.valor_causa}

INSTRUÇÕES:
1. Use linguagem técnica de sentença
2. Cite fundamentos legais específicos
3. Seja preciso e completo
4. Siga padrão jurisprudencial do TST

Redija de forma técnica e robusta.
"""
            
            conteudo = self.claude.gerar_resposta(prompt_secao)
            secoes.append(SecaoSentenca(
                titulo=titulo,
                conteudo=conteudo,
                ordem=200 + i,
                tipo="finais"
            ))
        
        return secoes
    
    def _gerar_dispositivo(self, dados_processo: ProcessoEstruturado, 
                          secoes_merito: List[SecaoSentenca]) -> SecaoSentenca:
        """Gera seção DISPOSITIVO baseada nas decisões do mérito"""
        
        prompt_dispositivo = f"""
Redija o DISPOSITIVO final da sentença trabalhista.

PROCESSO: {dados_processo.numero_processo}
PARTES: {[(p.nome, p.tipo) for p in dados_processo.partes]}
VALOR DA CAUSA: {dados_processo.valor_causa}

PEDIDOS ANALISADOS:
{chr(10).join([f"- {p.descricao}" for p in dados_processo.pedidos])}

SEÇÕES DE MÉRITO GERADAS:
{chr(10).join([f"- {s.titulo}" for s in secoes_merito])}

INSTRUÇÕES:
1. Use fórmula clássica: "JULGO PROCEDENTES EM PARTE os pedidos..."
2. Liste especificamente os pedidos deferidos
3. Liste os pedidos julgados improcedentes
4. Fixe custas processuais
5. Defira honorários advocatícios
6. Conceda justiça gratuita se aplicável
7. Termine com "Intimem-se as partes. Nada mais."

Seja técnico, preciso e completo.
"""
        
        conteudo = self.claude.gerar_resposta(prompt_dispositivo)
        return SecaoSentenca(
            titulo="DISPOSITIVO",
            conteudo=conteudo,
            ordem=300,
            tipo="dispositivo"
        )
    
    def _montar_sentenca_final(self, secoes: List[SecaoSentenca]) -> str:
        """Monta a sentença final ordenando as seções"""
        
        # Ordena seções
        secoes_ordenadas = sorted(secoes, key=lambda x: x.ordem)
        
        # Cabeçalho padrão
        cabecalho = """PODER JUDICIÁRIO
JUSTIÇA DO TRABALHO
TRIBUNAL REGIONAL DO TRABALHO DA 9ª REGIÃO
1ª VARA DO TRABALHO DE CURITIBA/PR

SENTENÇA

"""
        
        # Monta sentença
        sentenca_completa = cabecalho
        
        for secao in secoes_ordenadas:
            sentenca_completa += f"\n{secao.titulo}\n\n"
            sentenca_completa += f"{secao.conteudo}\n\n"
        
        return sentenca_completa
