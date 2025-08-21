"""
Serviço Claude para geração de sentenças judiciais
Consulta conhecimento RAG e gera sentenças estruturadas
"""

import anthropic
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import time

class ClaudeService:
    """Serviço para geração de sentenças usando Claude com consulta RAG"""
    
    def __init__(self):
        """Inicializa o serviço Claude"""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY não encontrada nas variáveis de ambiente")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        
        # Configurações de geração
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 8192
        self.temperature = 0.1
        
        # Carregar sistema few-shot se disponível
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Carrega prompt do sistema"""
        
        # Tentar carregar few-shot
        few_shot_path = Path(__file__).resolve().parent.parent / "fine_tuning" / "prompts" / "claude_few_shot_system.txt"
        
        if few_shot_path.exists():
            try:
                return few_shot_path.read_text(encoding='utf-8')
            except Exception as e:
                self.logger.warning(f"Erro ao carregar few-shot: {e}")
        
        # Prompt base
        return """
Você é um assistente especializado em redigir sentenças judiciais trabalhistas brasileiras.

INSTRUÇÕES PARA GERAÇÃO DE SENTENÇAS:

1. ESTRUTURA OBRIGATÓRIA:
   - RELATÓRIO (resumo do processo e das partes)
   - FUNDAMENTAÇÃO (análise jurídica detalhada com citação de leis)
   - DISPOSITIVO (decisão final clara e objetiva)

2. ESTILO DE REDAÇÃO:
   - Linguagem jurídica formal e precisa
   - Uso correto de terminologia trabalhista
   - Citação de dispositivos legais (CLT, CF/88)
   - Fundamentação clara e bem estruturada
   - Parágrafos organizados e conectados logicamente

3. ELEMENTOS ESSENCIAIS:
   - Identificação completa das partes
   - Resumo dos pedidos principais
   - Análise das provas (documentais e orais)
   - Fundamentação legal robusta
   - Conclusão motivada para cada pedido

4. FORMATAÇÃO:
   - Use **negrito** para realces importantes
   - Organize em seções claras e numeradas
   - Mantenha parágrafos bem estruturados
   - Use conectores lógicos adequados

IMPORTANTE: 
- Base-se EXCLUSIVAMENTE nas informações fornecidas
- Cite apenas leis e precedentes mencionados ou amplamente conhecidos
- Mantenha coerência técnica e jurídica
- Se informações estiverem incompletas, mencione explicitamente
"""
    
    def gerar_sentenca_com_rag(self, conhecimento_caso: Dict[str, Any], case_id: str) -> str:
        """
        Gera sentença consultando conhecimento RAG
        
        Args:
            conhecimento_caso: Conhecimento completo do caso do RAG
            case_id: ID do caso para logs
            
        Returns:
            str: Sentença judicial completa
        """
        
        self.logger.info(f"[{case_id}] Iniciando geração de sentença com Claude")
        
        try:
            # Construir prompt com conhecimento do RAG
            user_prompt = self._build_prompt_from_rag(conhecimento_caso)
            
            start_time = time.time()
            
            # Gerar sentença com Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )
            
            duration = time.time() - start_time
            sentenca = response.content[0].text
            
            self.logger.info(f"[{case_id}] Sentença gerada em {duration:.1f}s ({len(sentenca)} caracteres)")
            
            return sentenca
            
        except anthropic.APIError as e:
            self.logger.error(f"[{case_id}] Erro na API Claude: {str(e)}")
            raise Exception(f"Erro na API Claude: {str(e)}")
        except Exception as e:
            self.logger.error(f"[{case_id}] Erro inesperado na geração: {str(e)}")
            raise Exception(f"Erro na geração da sentença: {str(e)}")
    
    def _build_prompt_from_rag(self, conhecimento_caso: Dict[str, Any]) -> str:
        """Constrói prompt a partir do conhecimento RAG"""
        
        # Extrair informações do processo
        processo = conhecimento_caso.get("processo", {})
        audiencia = conhecimento_caso.get("audiencia")
        estrutura = conhecimento_caso.get("estrutura_sentenca", {})
        
        # Informações básicas
        numero_processo = processo.get("numero", "Não informado")
        periodo_contratual = processo.get("periodo_contratual", "Não informado")
        valor_causa = processo.get("valor_causa", "Não informado")
        
        # Partes
        partes_info = []
        for parte in processo.get("partes", []):
            info = f"- {parte.get('nome', 'N/A')} ({parte.get('tipo', 'N/A')})"
            if parte.get('qualificacao'):
                info += f" - {parte.get('qualificacao')}"
            partes_info.append(info)
        
        # Pedidos
        pedidos_info = []
        for pedido in processo.get("pedidos", []):
            info = f"- {pedido.get('categoria', 'N/A')}: {pedido.get('descricao', 'N/A')}"
            if pedido.get('valor_estimado'):
                info += f" (Valor: {pedido.get('valor_estimado')})"
            pedidos_info.append(info)
        
        # Fatos relevantes
        fatos_info = []
        for fato in processo.get("fatos_relevantes", []):
            fatos_info.append(f"- {fato.get('descricao', 'N/A')} (Fonte: {fato.get('fonte', 'N/A')})")
        
        # Informações da audiência
        audiencia_info = ""
        if audiencia:
            depoimentos = []
            for depoente in audiencia.get('depoentes', []):
                depoimentos.append(
                    f"- {depoente.get('nome', 'N/A')} ({depoente.get('tipo', 'N/A')}): "
                    f"{depoente.get('resumo_depoimento', 'N/A')[:200]}..."
                )
            
            pontos_controvertidos = []
            for ponto in audiencia.get('pontos_controvertidos', []):
                pontos_controvertidos.append(f"- {ponto.get('tema', 'N/A')}")
            
            decisoes = []
            for decisao in audiencia.get('decisoes_audiencia', []):
                decisoes.append(f"- {decisao.get('tipo', 'N/A')}: {decisao.get('descricao', 'N/A')}")
            
            audiencia_info = f"""
INFORMAÇÕES DA AUDIÊNCIA:

Depoimentos registrados:
{chr(10).join(depoimentos[:5])}

Pontos controvertidos discutidos:
{chr(10).join(pontos_controvertidos[:5])}

Decisões tomadas na audiência:
{chr(10).join(decisoes)}

Observações do juízo: {audiencia.get('observacoes_juiz', 'Nenhuma observação específica')}
"""
        
        # Orientações sobre estrutura
        orientacoes_estrutura = ""
        if estrutura:
            orientacoes_estrutura = f"""
ORIENTAÇÕES SOBRE ESTRUTURA (use como referência):

{estrutura.get('estrutura_sentenca', '')}

ESTILO DE REDAÇÃO:
{estrutura.get('estilo_redacao', '')}
"""
        
        # Construir prompt final
        prompt = f"""
Redija uma sentença judicial trabalhista completa baseada nas informações abaixo:

DADOS BÁSICOS DO PROCESSO:
- Número do processo: {numero_processo}
- Período contratual: {periodo_contratual}
- Valor da causa: {valor_causa}

PARTES DO PROCESSO:
{chr(10).join(partes_info) if partes_info else "- Não identificadas"}

PEDIDOS FORMULADOS:
{chr(10).join(pedidos_info) if pedidos_info else "- Nenhum pedido identificado"}

FATOS RELEVANTES DO PROCESSO:
{chr(10).join(fatos_info) if fatos_info else "- Nenhum fato específico identificado"}

{audiencia_info}

{orientacoes_estrutura}

INSTRUÇÕES ESPECÍFICAS:
1. Siga rigorosamente a estrutura: RELATÓRIO → FUNDAMENTAÇÃO → DISPOSITIVO
2. Use linguagem jurídica formal e adequada
3. Cite dispositivos legais pertinentes (CLT, CF/88)
4. Fundamente adequadamente cada decisão tomada
5. Seja preciso na análise das provas apresentadas
6. Mantenha coerência com os fatos do processo
7. Use formatação adequada (**negrito** para destaques importantes)
8. Para valores monetários, use R\\$ (com barra invertida)

ATENÇÃO CRÍTICA:
- Use EXCLUSIVAMENTE as informações fornecidas acima
- NÃO invente fatos, documentos ou provas não mencionados
- Se alguma informação estiver incompleta, mencione explicitamente
- Mantenha-se fiel aos dados extraídos do processo real
- Base suas conclusões apenas nos elementos probatórios apresentados

Redija a sentença completa agora:
"""
        
        return prompt

    def gerar_resposta(self, prompt: str) -> str:
        """Gera uma resposta livre do Claude usando o system prompt atual.

        Args:
            prompt: Prompt de usuário completo

        Returns:
            str: Texto de saída do modelo
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text
        except Exception as e:
            self.logger.error(f"Erro ao gerar resposta livre com Claude: {e}")
            raise
    
    def gerar_fundamentacao_especifica(
        self, 
        conhecimento_caso: Dict[str, Any], 
        pedido_especifico: str, 
        direcao: str,
        case_id: str
    ) -> str:
        """
        Gera fundamentação específica para um pedido
        
        Args:
            conhecimento_caso: Conhecimento do caso
            pedido_especifico: Pedido a ser fundamentado
            direcao: "procedente" ou "improcedente"
            case_id: ID do caso
            
        Returns:
            str: Fundamentação específica
        """
        
        prompt = f"""
Com base no conhecimento do caso, redija fundamentação jurídica específica para:

PEDIDO: {pedido_especifico}
DIREÇÃO: {direcao}

DADOS DO CASO:
{json.dumps(conhecimento_caso.get('processo', {}), indent=2, ensure_ascii=False)}

INSTRUÇÕES:
1. Foque especificamente neste pedido
2. Justifique tecnicamente a {direcao}
3. Cite dispositivos legais aplicáveis
4. Use precedentes quando relevantes
5. Seja objetivo e conclusivo

Estrutura: Alegações → Prova → Fundamentação Legal → Conclusão
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.1,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            self.logger.info(f"[{case_id}] Fundamentação específica gerada para: {pedido_especifico}")
            return response.content[0].text
            
        except Exception as e:
            self.logger.error(f"[{case_id}] Erro na fundamentação específica: {e}")
            raise
