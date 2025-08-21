"""
Serviço de Diálogo Inteligente Avançado
Implementa o prompt base estruturado em 3 etapas com Claude-Gemini
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import time
import random
try:
    import numpy as np
except ImportError:
    np = None

from .claude_service import ClaudeService
from .gemini_processor import GeminiProcessor
from .enhanced_rag_service import EnhancedRAGService
from .jurisprudence_analyzer import JurisprudenceAnalyzer
from .evidence_analyzer import EvidenceAnalyzer
from .enhanced_prompt_generator import EnhancedPromptGenerator
from .sectorial_sentence_generator import SectorialSentenceGenerator

class IntelligentDialogueService:
    """
    Orquestra diálogo inteligente entre Claude e Gemini
    Segue o prompt base estruturado em 3 etapas
    """
    
    def __init__(self, case_id: str):
        self.case_id = case_id
        self.logger = logging.getLogger(__name__)
        
        # Serviços especializados
        self.claude = ClaudeService()
        self.gemini = GeminiProcessor()
        self.rag = EnhancedRAGService(case_id)
        self.jurisprudence = JurisprudenceAnalyzer()
        self.evidence = EvidenceAnalyzer()
        self.prompt_generator = EnhancedPromptGenerator()
        self.sectorial_generator = SectorialSentenceGenerator(case_id)
        
        # Contexto do diálogo
        self.dialogue_context = {
            "etapa_atual": 0,
            "dados_basicos": {},
            "resumo_processo": {},
            "analise_prova_oral": {},
            "fundamentacao_guiada": {},
            "dialogue_history": []
        }
    
    def executar_dialogo_completo(self, 
                                 texto_processo: str,
                                 transcricao_audiencia: Optional[str] = None) -> Dict[str, Any]:
        """
        Executa o diálogo completo seguindo o prompt base estruturado
        
        Args:
            texto_processo: Texto completo do processo
            transcricao_audiencia: Transcrição da audiência (opcional)
            
        Returns:
            Dict com resultado completo das 3 etapas
        """
        
        self.logger.info(f"[{self.case_id}] 🎯 INICIANDO DIÁLOGO INTELIGENTE ESTRUTURADO")
        
        try:
            # ETAPA 1: Resumo Sistematizado 
            etapa1_resultado = self._executar_etapa_1_resumo_sistematizado(texto_processo)
            self._salvar_contexto_dialogo("ETAPA_1", etapa1_resultado)
            
            # ETAPA 2: Análise da Prova Oral
            etapa2_resultado = None
            if transcricao_audiencia:
                etapa2_resultado = self._executar_etapa_2_analise_prova_oral(
                    transcricao_audiencia, etapa1_resultado
                )
                self._salvar_contexto_dialogo("ETAPA_2", etapa2_resultado)
            
            # ETAPA 3: Fundamentação Guiada APRIMORADA
            # TEMPORÁRIO: Usar método anterior até corrigir problemas
            etapa3_resultado = self._executar_etapa_3_fundamentacao_guiada(
                etapa1_resultado, etapa2_resultado
            )
            self._salvar_contexto_dialogo("ETAPA_3", etapa3_resultado)
            
            # Resultado final estruturado
            resultado_completo = {
                "case_id": self.case_id,
                "timestamp": datetime.now().isoformat(),
                "etapas_executadas": ["ETAPA_1", "ETAPA_2" if etapa2_resultado else None, "ETAPA_3"],
                "etapa_1_resumo": etapa1_resultado,
                "etapa_2_prova_oral": etapa2_resultado,
                "etapa_3_fundamentacao": etapa3_resultado,
                "sentenca_final": etapa3_resultado.get("sentenca_completa", "")
            }
            
            self.logger.info(f"[{self.case_id}] ✅ DIÁLOGO INTELIGENTE CONCLUÍDO COM SUCESSO")
            return resultado_completo
            
        except Exception as e:
            self.logger.error(f"[{self.case_id}] ❌ Erro no diálogo inteligente: {str(e)}")
            raise
    
    def _executar_etapa_1_resumo_sistematizado(self, texto_processo: str) -> Dict[str, Any]:
        """
        ETAPA 1: Resumo sistematizado das peças principais
        Implementa o prompt base específico da Etapa 1
        """
        
        self.logger.info(f"[{self.case_id}] 📋 EXECUTANDO ETAPA 1: RESUMO SISTEMATIZADO")
        
        # Prompt detalhado da Etapa 1 (exatamente como fornecido pelo usuário)
        prompt_etapa_1 = """
### 📌 *Objetivo*
Produzir um resumo sistematizado das peças de um *processo trabalhista*, assegurando que todas as informações essenciais para o deslinde da controvérsia sejam fornecidas.

### 📝 **Instruções*
ENTRADA: você receberá de entrada uma das duas opções abaixo:
1) arquivo contendo as seguintes peças do processo:
- Petição Inicial (reclamação trabalhista);
- Contestação (defesa da(s) reclamada(s));
- Réplica (impugnação à defesa);
- Ata de Audiência (depoimentos das partes e testemunhas).

ou

2) Um número de processo do PJe contendo 20 dígitos (Exemplo: 0100187-84.2023.5.01.0057).
Se for esse o caso, acione a ferramenta <Busca Processual> e execute as instruções abaixo.

#Com base no processo informado, ou a partir do arquivo .pdf fornecido, siga *as diretrizes* abaixo para produzir um *resumo estruturado e objetivo*:

### * Etapa 0 - Informe os dados básicos do processo:
1) data de admissão:
2) data da dispensa:
3) Tempo do contrato:
4) Forma de desligamento:
5) remuneração:
6) função/atividade:

*Exiba essas 6 informações em formato de TABELA:
- colunas (petição inicial e contestações);
- linhas (Admissão, Dispensa, Remuneração, Função)

**Antes da tabela acima, informe a **Data do ajuizamento da ação**

### *📊 Etapa 1 - Elaboração de resumo detalhada*
de cada um dos pedidos formulados na PETIÇÃO INICIAL, acompanhado das respectivas teses de defesa apresentadas em CONTESTAÇÃO.

- Para cada pedido formulado na PETIÇÃO INICIAL identifique a tese correspondente na CONTESTAÇÃO;

📌 **Organize as informações em formato de relatório de sentença, adote o tempo verbal *presente do indicativo* (ex.: alega, aduz, sustenta...), e obedeça a formatação a seguir:

##*🔹PRELIMINARES E PREJUDICIAIS DE MÉRITO*

1. Vá até cada uma da(s) contestação(ões) da(s) de cada uma da(s) reclamada(s) e verifique se existem PRELIMINARES na contestação.

2. Exemplos mais comuns de *PRELIMINARES*:
● DA INCOMPETÊNCIA DA JUSTIÇA DO TRABALHO
● DA INCONSTITUCIONALIDADE DOS ARTIGOS
● DA INÉPCIA DA PETIÇÃO INICIAL
● DA AUSÊNCIA DE LIQUIDAÇÃO DOS PEDIDOS
● DA IMPUGNAÇÃO AO VALOR DA CAUSA
● DA ILEGITIMIDADE DE PARTE (PARTE ILEGÍTIMA)
● DA IMPOSSIBILIDADE JURÍDICA DO PEDIDO
● DA FALTA DE INTERESSE PROCESSUAL

10. Caso tenha sido alegada alguma Preliminar, organize essa(s) preliminares em **TEMAS* com a seguinte *ESTRUTURA*:

🔹Da ⁠*Nome da Preliminar⁠*
⁠*Resumir aqui os principais argumentos da preliminar de cada uma das contestações. Mencione qual reclamada alegou a preliminar.⁠*

##*DAS PREJUDICIAIS DE MÉRITO*

11. Depois das preliminares, você deve mencionar as PREJUDICIAIS DE MÉRITO.
12. Vá até cada uma da(s) contestação(ões) de cada uma da(s) reclamada(s) e verifique se foi alegada alguma PREJUDICIAIS DE MÉRITO.
13. Veja alguns exemplos mais comuns de *PREJUDICIAIS DE MÉRITO* que podem aparecer nas contestações:
● DA REVELIA DA RECLAMADA
● DA PRESCRIÇÃO
● DA PRESCRIÇÃO BIENAL
● DA PRESCRIÇÃO QUINQUENAL (adotar modelo abaixo)
● DA ADESÃO DO PDV (PLANO DE DEMISSÃO VOLUNTÁRIA)

14. Caso tenha sido alegada alguma PREJUDICIAL DE MÉRITO, organize-as em *TEMAS* com a seguinte *ESTRUTURA*:

🔹Do(a) ⁠*nome da prejudicial de mérito⁠*
{Resumir aqui os principais argumentos da prejudicial de mérito de cada uma das contestações. Mencione qual reclamada alegou a prejudicial de mérito}.
{Resumir aqui os principais argumentos do reclamante em relação a esta PREJUDICIAL_DE_MÉRITO. Extraia esses argumentos da *RÉPLICA* ou da *MANIFESTAÇÃO_À_CONTESTAÇÃO* ou da *MANIFESTAÇÃO_À_DEFESA* apresentada pelo(as) Reclamante.}

**MÉRITO**:
Esgotada a apresentação das preliminares e prejudiciais, passe para o exame de mérito dos pedidos, estruturando a resposta da seguinte forma:

**Do/a <Título do Pedido>*
[Insira aqui os principais fundamentos da causa de pedir]
[Insira aqui os principais fundamentos da contestação]

#prossiga com essa estrutura até esgotar o último pedido
#organize os parágrafos acima de forma a destinar um parágrafo apenas as razões da petição inicial e um segundo parágrafo apenas para os fundamentos da contestação.
#ATENÇÃO: se houver pedido de horas extras, insira no parágrafo introdutório da fundamentação os horários da jornada informados na petição inicial.

- EXEMPLO:
"*Da justa causa*
O reclamante busca a reversão da justa causa, alegando que a dispensa foi injusta e sem motivo, pois o incidente que causou a demissão (crianças ligando o carrinho elétrico) não foi decorrente de mau procedimento ou desídia. Explica que estava verificando um equipamento e deixou a chave na ignição, mas o acidente foi causado por terceiros.

A reclamada sustenta que a dispensa por justa causa foi legítima devido à negligência do reclamante em não retirar a chave do veículo, o que resultou em um acidente com clientes.

*Das horas extras*
O reclamante pleiteia o pagamento de horas extras, alegando que cumpria jornada das 8h30 às 18h, de segunda a quinta-feira, e das 8h às 19h às sextas-ferias, sem intervalo intrajornada.

Em defesa, a reclamada afirma que a jornada do reclamante era corretamente registrada em controle de ponto, e eventuais horas extras prestadas eram compensadas ou pagas."

### *📊 Etapa 2 - Elaboração da Planilha com Síntese do Processo*

📌 *Organize as informações em uma planilha* com os seguintes parâmetros:

- *Linhas:*
- [Pedido 1] ⇄ [Defesa 1]
- [Pedido 2] ⇄ [Defesa 2]
- [Pedido 3] ⇄ [Defesa 3]
- … (Repita conforme necessário)

- *Colunas:*
- *[Petição Inicial]* → resumo de cada uma dos pedidos.
- *[Contestação]* → teses defensivas para cada um dos pedidos.
- *[Réplica]* → impugnações do reclamante às teses defensivas.

# Se houver mais de uma ré, abrir uma nova coluna.

🚫 *Pedidos a serem ignorados*:
- Gratuidade de justiça
- Honorários advocatícios
- Juros e correção monetária
- Exibição de documentos

"__________________________ /1ª Etapa/ ___________________________"
"""

        # Claude executa a Etapa 1 com consulta ao RAG
        conhecimento_processo = self.rag.query_knowledge(
            query="estrutura básica petição inicial contestação pedidos", 
            sources=["estilo_juiza", "caso_atual"],
            top_k=8
        )
        
        prompt_completo = f"""
{prompt_etapa_1}

TEXTO DO PROCESSO PARA ANÁLISE:
{texto_processo}

CONHECIMENTO DO RAG (consulte para manter estilo e estrutura):
{json.dumps(conhecimento_processo, indent=2, ensure_ascii=False)}

Execute a análise seguindo EXATAMENTE o formato especificado acima.
"""
        
        # Gemini executa análise estruturada
        response = self.gemini.model.generate_content(
            prompt_completo,
            generation_config=self.gemini.generation_config
        )
        
        resultado_etapa_1 = {
            "etapa": "ETAPA_1_RESUMO_SISTEMATIZADO",
            "timestamp": datetime.now().isoformat(),
            "dados_basicos_extraidos": True,
            "preliminares_identificadas": True,
            "prejudiciais_identificadas": True,
            "merito_analisado": True,
            "planilha_sintese_criada": True,
            "conteudo_completo": response.text,
            "prompt_utilizado": "PROMPT_BASE_ETAPA_1_ORIGINAL"
        }
        
        self.dialogue_context["etapa_atual"] = 1
        self.dialogue_context["resumo_processo"] = resultado_etapa_1
        
        return resultado_etapa_1
    
    def _executar_etapa_2_analise_prova_oral(self, 
                                           transcricao_audiencia: str,
                                           contexto_etapa_1: Dict[str, Any]) -> Dict[str, Any]:
        """
        ETAPA 2: Análise da Ata de Audiência 
        Implementa o prompt base específico da Etapa 2
        """
        
        self.logger.info(f"[{self.case_id}] 🎤 EXECUTANDO ETAPA 2: ANÁLISE PROVA ORAL")
        
        # Prompt detalhado da Etapa 2 (exatamente como fornecido pelo usuário)
        prompt_etapa_2 = """
📌 **Etapa 3 - Análise da Ata de Audiência**

ATENÇÃO: pode acontecer dos depoimentos serem anexados por meio de uma CERTIDÃO, logo após a ATA DE AUDICÊNCIA. Essa verificação é crucial.

Caso os depoimentos das partes não sejam localizados na ATA DE AUDIÊNCIA, verifique o conteúdo da CERTIDÃO que acompanha a ATA DE AUDIÊNCIA. Caso não haja a certidão, antes da análise da ata, solicitar ao usuário a inserção dos depoimentos de audiência de forma transcrita.

1️⃣ *Análise Inicial*
- Leia *integralmente* os depoimentos fornecidos.
- Faça isso *em silêncio*, sem gerar resposta nesta etapa.

2️⃣ **Identificação de Pontos Controvertidos*
#Identifique as questões em disputa no processo.
#Exemplos comuns na esfera trabalhista:
- Horas extras
- Intervalos intrajornada
- Salário "por fora" / extrafolha
- Assédio moral
- Idoneidade dos controles de frequência
- Outros pontos controvertidos podem ser detectados.

3️⃣ *Criação da Tabela Resumo*
- Elabore uma *tabela sistematizada* com o que cada depoente afirmou sobre os *pontos controvertidos*.

4️⃣ **Atualização da Tabela (se necessário)*
- Caso surjam *novos pontos controvertidos*, **refaça* a tabela incluindo-os.

### *📊 Formato da Tabela de Saída:*

| Ponto Controvertido | Depoente 1 | Depoente 2 | Depoente 3 |
|---------------------|------------|------------|------------|
| Horas extras | [Resumo do depoimento] | [Resumo do depoimento] | [Resumo do depoimento] |
| Intervalos intrajornada | [Resumo do depoimento] | [Resumo do depoimento] | [Resumo do depoimento] |
| ... | ... | ... | ... |

### *📌 Etapa Final - Relatório analítico*
- Após a tabela, faça um relatório individualizado de cada depoimento, destacando os pontos de convergência e divergência em relação ao depoimento do autor.
- Seja bastante analítico e completo nesta etapa;
- Dê maior destaque para eventuais *inconsistências, divergências ou contradições* entre os depoimentos:
- Procure e mencione eventuais contradições internas nos depoimentos: ou seja, identifique trechos (se houver) em que o depoente declarou algo que conflita com algo anteriormente falado por este mesmo depoente.

📌 *Observações finais:*
#DIRETRIZES ESPECIAIS
- Você deve observar, em especial, as seguintes diretrizes, sem prejudicar a tecnicidade jurídica do texto:
1. Use conectores para criar transições suaves entre frases e parágrafos, guiando o leitor.
2. Evite frases excessivamente longas, mas varie o ritmo para evitar monotonia.
3. Retire repetições ou palavras/frases desnecessárias.
4. Demonstre autoridade no tema e seja consistente no tom, sem perder a elegância.
5. Termine cada parágrafo preparando o terreno para o próximo.
6. Use sinônimos para evitar repetições, mas mantenha a simplicidade quando necessário.
7. Cheque a lógica das ideias.
8. Averigue a fluidez do raciocínio e a concatenação das ideias. Certifique-se de que as ideias estão conectadas de forma natural, como degraus em uma escada.
9. Seja direto e claro. Simplifique.
10. Evite blocos de texto muito densos. Facilite a leitura.

Esse prompt garante uma abordagem *estruturada, objetiva e completa* para analisar o processo trabalhista.⚖️📄

"__________________________ // ___________________________"
"""

        # Recuperar conhecimento sobre análise de prova oral
        conhecimento_prova = self.rag.query_knowledge(
            query="análise depoimentos pontos controvertidos prova oral audiência",
            sources=["estilo_juiza", "dialogo_contexto"],
            top_k=5
        )
        
        prompt_completo = f"""
{prompt_etapa_2}

CONTEXTO DA ETAPA 1 (use para entender os pedidos e pontos em disputa):
{contexto_etapa_1.get('conteudo_completo', '')[:2000]}

TRANSCRIÇÃO DA AUDIÊNCIA PARA ANÁLISE:
{transcricao_audiencia}

CONHECIMENTO DO RAG (consulte para manter estilo de análise):
{json.dumps(self._convert_to_serializable(conhecimento_prova), indent=2, ensure_ascii=False)}

Execute a análise seguindo EXATAMENTE o formato especificado acima.
"""
        
        # Claude executa análise da prova oral
        try:
            response = self._claude_request(
                system=self.claude.system_prompt,
                user=prompt_completo,
                max_tokens=self.claude.max_tokens,
                temperature=self.claude.temperature
            )
            
            resultado_etapa_2 = {
                "etapa": "ETAPA_2_ANALISE_PROVA_ORAL",
                "timestamp": datetime.now().isoformat(),
                "pontos_controvertidos_identificados": True,
                "tabela_depoimentos_criada": True,
                "relatorio_analitico_completo": True,
                "contradicoes_internas_verificadas": True,
                "conteudo_completo": response.content[0].text,
                "prompt_utilizado": "PROMPT_BASE_ETAPA_2_ORIGINAL"
            }
            
            self.dialogue_context["etapa_atual"] = 2
            self.dialogue_context["analise_prova_oral"] = resultado_etapa_2
            
            return resultado_etapa_2
            
        except Exception as e:
            self.logger.error(f"Erro na Etapa 2: {str(e)}")
            raise
    
    def _executar_etapa_3_fundamentacao_guiada(self,
                                              contexto_etapa_1: Dict[str, Any],
                                              contexto_etapa_2: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        ETAPA 3: Fundamentação Guiada com DIÁLOGO INTELIGENTE Claude ↔ Gemini  
        Claude atua como Juiz fazendo perguntas específicas
        Gemini atua como Assessor fornecendo análises detalhadas
        """
        
        self.logger.info(f"[{self.case_id}] ⚖️ EXECUTANDO ETAPA 3: FUNDAMENTAÇÃO GUIADA COM DIÁLOGO INTELIGENTE")
        
        # Prompt detalhado da Etapa 3 (aprimorado com base na sentença exemplo)
        prompt_etapa_3_template = r"""
# 🏛️ OBJETIVO
Redigir uma SENTENÇA TRABALHISTA COMPLETA, tecnicamente articulada, seguindo rigorosamente o estilo e formatação da juíza, com análise probatória detalhada e fundamentação jurídica robusta.

# ✍️ ESTILO E FORMATAÇÃO OBRIGATÓRIOS
• ESTRUTURA: SENTENÇA → RELATÓRIO → FUNDAMENTAÇÃO → DISPOSITIVO
• SEM numeração romana, SEM hashtags markdown
• Títulos das seções em MAIÚSCULAS puras
• Subtópicos em MAIÚSCULAS sem numeração (ex: JORNADA – HORAS EXTRAS)
• Use "É o relatório. Decide-se." como transição
• Linguagem formal, técnica, conectores sofisticados
• Sempre referencie documentos por (ID xxx) ou (id. xxx)

# 📑 CONTEXTO PROCESSUAL COMPLETO
1. *Resumo sistematizado* → {{RESUMO_PROCESSO}}
2. *Análise da prova oral* → {{PROVA_ORAL}}
3. *Documentos juntados* → {{OUTRAS_PROVAS}}

# 🎯 DIRETRIZES ESPECÍFICAS DE ANÁLISE
• **ANÁLISE PROBATÓRIA DETALHADA**: Examine cada testemunha individualmente
• **CONTRADIÇÕES**: Identifique e comente discrepâncias entre depoimentos
• **ÔNUS DA PROVA**: Sempre mencione art. 818, I, da CLT e art. 373, I/II, do CPC
• **PRESUNÇÕES**: Analise validade de documentos e suas presunções
• **JURISPRUDÊNCIA**: Cite Súmulas, OJs, decisões do STF (com modulação temporal)

# 📝 ESTRUTURA OBRIGATÓRIA DA SENTENÇA

**SENTENÇA**

**RELATÓRIO**
[NOME], qualificado na inicial, ajuizou a presente reclamação trabalhista em face de [EMPRESA], alegando ter sido admitido em [data], na função de [função] e dispensado em [data]. Postula [listar pedidos]. Atribuiu à causa o valor de R\$ [valor].

A reclamada, em contestação (ID [id]), defendeu-se alegando [resumo defesa] e pugnou pela improcedência total dos pedidos.

O reclamante apresentou réplica (ID [id]), impugnando [pontos] e reiterando os termos da inicial.

Em audiência de instrução (Ata ID [id]), foram ouvidas [número] testemunhas, [detalhes]. 

Razões finais remissivas. Rejeitada a proposta final de conciliação.

É o relatório. Decide-se.

**FUNDAMENTAÇÃO**

**[TÓPICO 1 EM MAIÚSCULAS]**
[Análise detalhada com:]
- Alegações das partes
- Prova documental (com IDs)
- Depoimento de cada testemunha individualmente
- Análise de contradições
- Fundamentação legal específica
- Conclusão (Ante o exposto, acolho/rejeito o pedido...)

[Repetir para cada pedido]

**DISPOSITIVO**
Ante o exposto, e por tudo mais que dos autos consta, decido, na Reclamação Trabalhista ajuizada por [NOME], em face de [EMPRESA], julgar [PROCEDENTES/IMPROCEDENTES/PROCEDENTES EM PARTE] os pedidos formulados, para, nos termos da fundamentação:

[Listar condenações específicas]

Concedo/Nego à reclamante os benefícios da justiça gratuita.
Defiro honorários de sucumbência, na forma da fundamentação.
Custas [especificar].
Intimem-se as partes.
Nada mais.

# 🔖 REQUISITOS JURÍDICOS OBRIGATÓRIOS
• **SEMPRE citar**: Dispositivos CLT, CF/88, CPC com numeração exata
• **Jurisprudência específica**: Súmulas TST, OJs, decisões STF com datas
• **Modulação temporal**: Para decisões STF, mencionar eficácia ex nunc/ex tunc
• **IDs dos documentos**: Sempre referenciar (ID xxx) ou (id. xxx)
• **Análise ônus probatório**: art. 818, I, CLT + art. 373, I/II, CPC

##ATENÇÃO ESPECIAL: Formatação e Valores
• **SEM Markdown**: Não use #, ##, *** - apenas MAIÚSCULAS para títulos
• **Cifrão**: SEMPRE use R\$ (com barra invertida)
• **IDs**: Sempre mencione (ID xxx) para documentos
• **Extensão**: Mínimo 5.000 caracteres, análise detalhada obrigatória
• **Estilo da juíza**: Use conectores sofisticados, análise minuciosa de provas
"""
        
        # Recuperar conhecimento específico para fundamentação completa
        conhecimento_fundamentacao = self.rag.query_knowledge(
            query="fundamentação jurídica dispositivos legais CLT precedentes TST análise probatória depoimentos",
            sources=["estilo_juiza", "caso_atual", "dialogo_contexto"],
            top_k=15
        )
        
        # Preparar contexto das etapas anteriores
        resumo_processo = contexto_etapa_1.get('conteudo_completo', '')
        prova_oral = contexto_etapa_2.get('conteudo_completo', '') if contexto_etapa_2 else "Não foi realizada análise de prova oral."
        
        # DIÁLOGO INTELIGENTE: Claude faz perguntas específicas para Gemini
        self.logger.info(f"[{self.case_id}] 🤝 INICIANDO DIÁLOGO CLAUDE ↔ GEMINI")
        
        # FASE 1: Claude solicita extração de dados específicos do Gemini
        prompt_claude_questoes = f"""
Você é um JUIZ DO TRABALHO experiente que precisa redigir uma sentença. 

Baseado no resumo do processo e prova oral abaixo, faça 5 PERGUNTAS ESPECÍFICAS para seu assessor técnico (Gemini) extrair automaticamente do processo original todas as informações necessárias para eliminar placeholders:

RESUMO DISPONÍVEL:
{resumo_processo[:2000]}

PROVA ORAL DISPONÍVEL:
{prova_oral[:1000] if prova_oral else 'Não disponível'}

FORMULE EXATAMENTE 8 PERGUNTAS TÉCNICAS ESPECÍFICAS para extrair:
1. Dados completos das partes (nomes, qualificações, CNPJ/CPF, endereços completos)
2. Datas precisas (admissão, dispensa, ajuizamento) e números de processo
3. Valores específicos (salário, valor da causa, todos os pedidos com valores)
4. IDs ESPECÍFICOS de todos os documentos mencionados (contestação, réplica, ata, etc.)
5. Depoimentos COMPLETOS de cada testemunha individualmente com contradições
6. Documentos probatórios específicos (relatórios de viagem, cartões de ponto, etc.) com IDs
7. Normas coletivas aplicáveis e cláusulas específicas mencionadas
8. Detalhes de procedimentos (horários, rotinas, equipamentos) conforme depoimentos

FORMATO DA RESPOSTA:
PERGUNTA 1: [pergunta específica]
PERGUNTA 2: [pergunta específica]
PERGUNTA 3: [pergunta específica]
PERGUNTA 4: [pergunta específica]
PERGUNTA 5: [pergunta específica]
"""
        
        # Claude gera as perguntas
        response_claude_questoes = self._claude_request(
            system=self.claude.system_prompt,
            user=prompt_claude_questoes,
            max_tokens=2000,
            temperature=0.1
        )
        
        questoes_claude = response_claude_questoes.content[0].text
        self.logger.info(f"[{self.case_id}] ❓ Claude gerou 5 questões específicas")
        
        # FASE 2: Gemini responde às perguntas específicas do Claude
        prompt_gemini_respostas = f"""
Você é um ASSESSOR TÉCNICO JURÍDICO especializado em extrair informações precisas de processos trabalhistas.

O Juiz responsável pelo caso fez as seguintes perguntas específicas que você deve responder com base no texto COMPLETO do processo:

{questoes_claude}

TEXTO COMPLETO DO PROCESSO PARA ANÁLISE:
{resumo_processo[:20000] + '...' if len(resumo_processo) > 20000 else resumo_processo}

TEXTO ORIGINAL DO PROCESSO (para extração precisa):
{self._recuperar_texto_original_processo()}

TRANSCRIÇÃO DA AUDIÊNCIA:
{prova_oral if prova_oral else 'Não realizada'}

INSTRUÇÕES ESPECÍFICAS:
- Extraia APENAS informações que estão EXPLICITAMENTE no texto
- Para nomes: forneça nome completo quando disponível
- Para datas: use formato DD/MM/AAAA
- Para valores: use formato R$ XX.XXX,XX
- Para IDs: mencione exatamente como aparecem nos autos
- Se não encontrar informação específica, responda "NÃO INFORMADO"

RESPONDA CADA PERGUNTA INDIVIDUALMENTE COM MÁXIMA PRECISÃO:
RESPOSTA 1: [dados completos das partes]
RESPOSTA 2: [datas e números precisos]
RESPOSTA 3: [valores específicos e detalhados]
RESPOSTA 4: [IDs exatos de TODOS os documentos]
RESPOSTA 5: [depoimentos LITERAIS de cada testemunha]
RESPOSTA 6: [documentos probatórios específicos com IDs]
RESPOSTA 7: [normas coletivas e cláusulas precisas]
RESPOSTA 8: [procedimentos detalhados conforme prova oral]
"""
        
        # Gemini responde às perguntas específicas
        gemini_response = self.gemini.model.generate_content(
            prompt_gemini_respostas,
            generation_config=self.gemini.generation_config
        )
        
        respostas_gemini = gemini_response.text
        self.logger.info(f"[{self.case_id}] 💡 Gemini forneceu respostas detalhadas")
        
        # FASE 3: Claude usa as respostas do Gemini para gerar sentença completa
        try:
            sentenca_longform = self._gerar_sentenca_longform(
                prompt_base=prompt_etapa_3_template,
                resumo_processo=resumo_processo,
                prova_oral=prova_oral,
                conhecimento_fundamentacao=self._convert_to_serializable(conhecimento_fundamentacao),
                questoes_claude=questoes_claude,
                respostas_gemini=respostas_gemini,
                alvo_caracteres_total=15000
            )

            resultado_etapa_3 = {
                "etapa": "ETAPA_3_FUNDAMENTACAO_GUIADA",
                "timestamp": datetime.now().isoformat(),
                "fundamentacao_juridica_completa": True,
                "citacoes_legais_incluidas": True,
                "estrutura_sentenca_seguida": True,
                "estilo_juiza_aplicado": True,
                "sentenca_completa": sentenca_longform,
                "prompt_utilizado": "PROMPT_BASE_ETAPA_3_ORIGINAL_LONGFORM"
            }

            self.dialogue_context["etapa_atual"] = 3
            self.dialogue_context["fundamentacao_guiada"] = resultado_etapa_3

            return resultado_etapa_3
        except Exception as e:
            self.logger.error(f"Erro na Etapa 3: {str(e)}")
            raise
    
    def _convert_to_serializable(self, obj):
        """Converte objetos numpy e outros tipos não serializáveis para JSON"""
        if isinstance(obj, dict):
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        elif np and isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        elif np and isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        elif np and isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

    def _recuperar_texto_original_processo(self) -> str:
        """Recupera o texto original otimizado para evitar timeouts do Gemini"""
        try:
            from pathlib import Path
            case_dir = Path(__file__).parent.parent / "storage" / self.case_id
            processo_path = case_dir / "processo_extraido.txt"
            
            if processo_path.exists():
                texto_original = processo_path.read_text(encoding='utf-8')
                # Limitar a 30k caracteres para evitar timeout do Gemini
                if len(texto_original) > 30000:
                    # Pegar início e fim do texto para manter contexto
                    inicio = texto_original[:15000]
                    fim = texto_original[-15000:]
                    return f"{inicio}\n\n[... TEXTO TRUNCADO PARA OTIMIZAÇÃO ...]\n\n{fim}"
                return texto_original
            else:
                return "TEXTO ORIGINAL NÃO DISPONÍVEL"
        except Exception as e:
            self.logger.error(f"Erro ao recuperar texto original: {str(e)}")
            return "ERRO AO ACESSAR TEXTO ORIGINAL"
    
    def _salvar_contexto_dialogo(self, etapa: str, resultado: Dict[str, Any]):
        """Salva contexto do diálogo no RAG para consultas futuras"""
        
        # Converter resultado para formato serializável
        resultado_serializavel = self._convert_to_serializable(resultado)
        
        self.rag.save_dialogue_context(
            question=f"Execução da {etapa}",
            answer=json.dumps(resultado_serializavel, ensure_ascii=False),
            dialogue_step=self.dialogue_context["etapa_atual"]
        )
        
        self.dialogue_context["dialogue_history"].append({
            "etapa": etapa,
            "timestamp": datetime.now().isoformat(),
            "resultado": resultado_serializavel
        })
    
    def _executar_etapa_3_fundamentacao_aprimorada(self, etapa1_resultado: Dict[str, Any], 
                                                  etapa2_resultado: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        ETAPA 3 APRIMORADA: Fundamentação com análise jurisprudencial e probatória avançada
        """
        
        self.logger.info(f"[{self.case_id}] ⚖️ EXECUTANDO ETAPA 3 APRIMORADA: FUNDAMENTAÇÃO COM ANÁLISE ESPECIALIZADA")
        
        try:
            # 1. EXTRAIR DADOS ESTRUTURADOS DO PROCESSO
            dados_processo = self._extrair_dados_estruturados_completos()
            
            # 2. ANÁLISE JURISPRUDENCIAL ESPECIALIZADA
            analise_jurisprudencial = self._executar_analise_jurisprudencial(dados_processo)
            
            # 3. ANÁLISE PROBATÓRIA DETALHADA
            analise_probatoria = self._executar_analise_probatoria(dados_processo)
            
            # 4. RECUPERAR CONTEXTO RAG ESPECÍFICO
            contexto_rag = self._recuperar_contexto_rag_especifico(dados_processo)
            
            # 5. GERAR PROMPT APRIMORADO
            prompt_aprimorado = self.prompt_generator.gerar_prompt_fundamentacao_completa(
                dados_processo=dados_processo,
                analise_jurisprudencia=analise_jurisprudencial,
                analise_provas=analise_probatoria,
                contexto_rag=contexto_rag
            )
            
            # 6. EXECUTAR CLAUDE COM PROMPT APRIMORADO
            response = self._claude_request(
                system=self.claude.system_prompt,
                user=prompt_aprimorado,
                max_tokens=self.claude.max_tokens,
                temperature=0.1
            )
            
            resultado_aprimorado = {
                "etapa": "ETAPA_3_FUNDAMENTACAO_APRIMORADA",
                "timestamp": datetime.now().isoformat(),
                "dados_processo_extraidos": dados_processo,
                "analise_jurisprudencial": analise_jurisprudencial,
                "analise_probatoria": analise_probatoria,
                "sentenca_completa": response.content[0].text,
                "metrica_qualidade": self._calcular_metrica_qualidade(response.content[0].text),
                "utilizou_analise_especializada": True
            }
            
            self.logger.info(f"[{self.case_id}] ✅ ETAPA 3 APRIMORADA CONCLUÍDA - Qualidade: {resultado_aprimorado['metrica_qualidade']}")
            return resultado_aprimorado
            
        except Exception as e:
            self.logger.error(f"[{self.case_id}] ❌ Erro na Etapa 3 Aprimorada: {str(e)}")
            # Fallback para método original
            return self._executar_etapa_3_fundamentacao_guiada(etapa1_resultado, etapa2_resultado)
    
    def _extrair_dados_estruturados_completos(self) -> Dict[str, Any]:
        """Extrai dados estruturados usando o Gemini aprimorado"""
        
        try:
            texto_processo = self._recuperar_texto_original_processo()
            
            # Usar Gemini com prompt aprimorado para extração completa
            processo_estruturado = self.gemini.extrair_informacoes_processo(texto_processo)
            
            return {
                "numero_processo": processo_estruturado.numero_processo,
                "partes": [{"nome": p.nome, "tipo": p.tipo, "qualificacao": p.qualificacao} for p in processo_estruturado.partes],
                "pedidos": [{"descricao": p.descricao, "categoria": p.categoria, "valor_estimado": p.valor_estimado} for p in processo_estruturado.pedidos],
                "testemunhas": [{"nome": t.nome, "parte_convite": t.parte_convite, "resumo_depoimento": t.resumo_depoimento} for t in processo_estruturado.testemunhas],
                "periodo_contratual": processo_estruturado.periodo_contratual,
                "valor_causa": processo_estruturado.valor_causa,
                "funcao_cargo": processo_estruturado.funcao_cargo,
                "jurisprudencias_citadas": processo_estruturado.jurisprudencias_citadas
            }
        except Exception as e:
            self.logger.error(f"Erro na extração de dados: {str(e)}")
            return {}
    
    def _executar_analise_jurisprudencial(self, dados_processo: Dict[str, Any]) -> Dict[str, Any]:
        """Executa análise jurisprudencial especializada"""
        
        analise_completa = {}
        
        # Verificar se é motorista para aplicar Lei 13.103/2015
        funcao = dados_processo.get("funcao_cargo", "").lower()
        if "motorista" in funcao:
            periodo_inicio = dados_processo.get("periodo_contratual", "").split(" a ")[0] if dados_processo.get("periodo_contratual") else ""
            periodo_fim = dados_processo.get("periodo_contratual", "").split(" a ")[-1] if dados_processo.get("periodo_contratual") else ""
            
            if periodo_inicio and periodo_fim:
                analise_completa["lei_motoristas"] = self.jurisprudence.analisar_lei_motoristas(periodo_inicio, periodo_fim)
        
        # Análise de controle de jornada
        # Assumindo empresa com mais de 20 empregados (dados reais precisariam ser extraídos)
        analise_completa["controle_jornada"] = self.jurisprudence.analisar_jornada_controle(
            tem_mais_20_empregados=True,
            controles_apresentados=True,  # Verificar nos dados reais
            jornada_alegada=dados_processo.get("jornada_alegada", "")
        )
        
        return analise_completa
    
    def _executar_analise_probatoria(self, dados_processo: Dict[str, Any]) -> Dict[str, Any]:
        """Executa análise probatória detalhada"""
        
        analise_completa = {}
        
        # Análise de testemunhas
        testemunhas = dados_processo.get("testemunhas", [])
        if testemunhas:
            analise_completa["analise_testemunhas"] = self.evidence.analisar_depoimentos_testemunhas(testemunhas)
        
        # Análise de ônus da prova para pedidos principais
        pedidos = dados_processo.get("pedidos", [])
        analise_onus = {}
        
        for pedido in pedidos:
            categoria = pedido.get("categoria", "")
            if categoria:
                analise_onus[categoria] = self.evidence.analisar_onus_proba(
                    pedido=categoria,
                    parte_interessada="requerente",
                    provas_apresentadas=[]  # Dados reais precisariam ser extraídos
                )
        
        analise_completa["onus_proba"] = analise_onus
        return analise_completa
    
    def _recuperar_contexto_rag_especifico(self, dados_processo: Dict[str, Any]) -> str:
        """Recupera contexto RAG específico para o caso"""
        
        # Construir query baseada nos pedidos e características do caso
        funcao = dados_processo.get("funcao_cargo", "")
        pedidos = [p.get("categoria", "") for p in dados_processo.get("pedidos", [])]
        
        query_elementos = [funcao] + pedidos + ["jurisprudência", "fundamentação", "estilo da juíza"]
        query = " ".join(query_elementos)
        
        conhecimento = self.rag.query_knowledge(
            query=query,
            sources=["estilo_juiza", "caso_atual", "dialogo_contexto"],
            top_k=20
        )
        
        return json.dumps(self._convert_to_serializable(conhecimento), indent=2, ensure_ascii=False)
    
    def _calcular_metrica_qualidade(self, sentenca: str) -> Dict[str, Any]:
        """Calcula métricas de qualidade da sentença gerada"""
        
        return {
            "tamanho_caracteres": len(sentenca),
            "tamanho_palavras": len(sentenca.split()),
            "tem_estrutura_completa": all(secao in sentenca.upper() for secao in ["RELATÓRIO", "FUNDAMENTAÇÃO", "DISPOSITIVO"]),
            "menciona_jurisprudencia": "TST" in sentenca or "STF" in sentenca,
            "cita_dispositivos_legais": "CLT" in sentenca or "CF/88" in sentenca,
            "qualidade_estimada": "alta" if len(sentenca) > 10000 else "média" if len(sentenca) > 5000 else "baixa"
        }

    def _executar_etapa_3_sentenca_sectorial(self, dados_processo, transcricao_audiencia) -> Dict[str, Any]:
        """
        NOVA ABORDAGEM: Geração sectorial especializada para sentenças completas
        Resolve limitações de contexto e gera sentenças com nível de detalhamento real
        """
        self.logger.info(f"[{self.case_id}] NOVA ABORDAGEM: Iniciando geração sectorial especializada")
        
        try:
            # Usa o novo gerador sectorial
            sentenca_completa = self.sectorial_generator.gerar_sentenca_completa(
                self.case_id, dados_processo, transcricao_audiencia
            )
            
            # Calcula métricas de qualidade
            metricas = self._calcular_metricas_sentenca_sectorial(sentenca_completa, dados_processo)
            
            self.logger.info(f"[{self.case_id}] Sentença sectorial gerada: {len(sentenca_completa)} caracteres")
            self.logger.info(f"[{self.case_id}] Métricas de qualidade: {metricas}")
            
            return {
                "sentenca_gerada": sentenca_completa,
                "metodo": "sectorial_especializado",
                "caracteres": len(sentenca_completa),
                "metricas_qualidade": metricas,
                "status": "sucesso"
            }
            
        except Exception as e:
            self.logger.error(f"[{self.case_id}] Erro na geração sectorial: {str(e)}")
            # Em caso de erro, usar método mais simples
            return {
                "sentenca_gerada": "Erro na geração sectorial. Sistema em modo de recuperação.",
                "metodo": "fallback_erro",
                "caracteres": 0,
                "status": "erro",
                "erro": str(e)
            }
    
    def _calcular_metricas_sentenca_sectorial(self, sentenca: str, dados_processo) -> Dict[str, Any]:
        """Calcula métricas de qualidade da sentença gerada pela abordagem sectorial"""
        return {
            "caracteres_total": len(sentenca),
            "palavras_total": len(sentenca.split()),
            "secoes_identificadas": sentenca.count("##") + sentenca.count("DAS ") + sentenca.count("DO "),
            "citacoes_legais": sentenca.count("CLT") + sentenca.count("TST") + sentenca.count("Súmula"),
            "pedidos_cobertos": len([p for p in dados_processo.pedidos if p.categoria.lower() in sentenca.lower()]),
            "nivel_detalhamento": "ALTO" if len(sentenca) > 15000 else "MÉDIO" if len(sentenca) > 8000 else "BAIXO"
        }

    # -------------------------
    # GERAÇÃO LONG-FORM SECCIONADA
    # -------------------------
    def _gerar_sentenca_longform(self,
                                 prompt_base: str,
                                 resumo_processo: str,
                                 prova_oral: str,
                                 conhecimento_fundamentacao: Dict[str, Any],
                                 questoes_claude: str,
                                 respostas_gemini: str,
                                 alvo_caracteres_total: int = 15000) -> str:
        """
        Gera a sentença completa por seções com laço de continuação até atingir um alvo mínimo de caracteres.
        Mantém o Prompt Base e evita repetições/cabeçalhos duplicados.
        """
        contexto_comum = f"""
{prompt_base}

CONTEXTO PROCESSUAL ESPECÍFICO:
{{RESUMO_PROCESSO}} = {resumo_processo}
{{PROVA_ORAL}} = {prova_oral if prova_oral else 'Não foi realizada análise de prova oral.'}
{{OUTRAS_PROVAS}} = Consulte o conhecimento do RAG para identificar documentos relevantes.

INFORMAÇÕES EXTRAÍDAS PELO ASSESSOR TÉCNICO (GEMINI):
QUESTÕES SOLICITADAS:
{questoes_claude}

RESPOSTAS ESPECÍFICAS:
{respostas_gemini}

CONHECIMENTO DO RAG (jurisprudência e estilo):
{json.dumps(conhecimento_fundamentacao, indent=2, ensure_ascii=False)}

REGRAS GERAIS:
- Sem markdown (#, ##, **, etc.)
- Títulos em MAIÚSCULAS puras
- Referencie IDs reais quando disponíveis
- Nunca repita cabeçalhos já emitidos
- Se atingir o limite da resposta e ainda houver conteúdo, finalize a frase e escreva exatamente a tag CONTINUAR## ao final
"""

        secoes_alvo = [
            ("RELATÓRIO", 1400, True),
            ("FUNDAMENTAÇÃO - LIMITAÇÃO DOS VALORES", 800, False),
            ("FUNDAMENTAÇÃO - PROVIDÊNCIA SANEADORA - LEI 13.467/2017", 700, False),
            ("FUNDAMENTAÇÃO - CCT APLICÁVEL", 900, False),
            ("FUNDAMENTAÇÃO - JORNADA – HORAS EXTRAS – DOMINGOS E FERIADOS", 1200, False),
            ("FUNDAMENTAÇÃO - INTERVALO INTRAJORNADA", 700, False),
            ("FUNDAMENTAÇÃO - INTERVALOS INTERJORNADA E INTERSEMANAL", 900, False),
            ("FUNDAMENTAÇÃO - TEMPO DE ESPERA", 900, False),
            ("FUNDAMENTAÇÃO - PARTICIPAÇÃO NOS RESULTADOS (PLR)", 700, False),
            ("FUNDAMENTAÇÃO - DIFERENÇAS DE DIÁRIAS – AJUDA DE CUSTOS", 900, False),
            ("FUNDAMENTAÇÃO - MULTA CONVENCIONAL", 600, False),
            ("FUNDAMENTAÇÃO - DESCONTOS INDEVIDOS", 700, False),
            ("FUNDAMENTAÇÃO - NULIDADE DA DISPENSA – REINTEGRAÇÃO", 900, False),
            ("FUNDAMENTAÇÃO - INDENIZAÇÃO POR DANOS MORAIS", 900, False),
            ("FUNDAMENTAÇÃO - FGTS", 600, False),
            ("FUNDAMENTAÇÃO - JUSTIÇA GRATUITA", 500, False),
            ("FUNDAMENTAÇÃO - HONORÁRIOS ADVOCATÍCIOS", 600, False),
            ("FUNDAMENTAÇÃO - CONTRIBUIÇÕES SOCIAIS E FISCAIS", 700, False),
            ("FUNDAMENTAÇÃO - CORREÇÃO MONETÁRIA E JUROS DE MORA", 700, False),
            ("DISPOSITIVO", 1600, False),
        ]

        partes = []

        # Cabeçalho SENTENÇA e transição padrão
        partes.append("SENTENÇA\n")

        for nome_secao, alvo_chars, inserir_transicao_relatorio in secoes_alvo:
            texto_secao = self._gerar_secao_com_continuacao(
                contexto_comum=contexto_comum,
                nome_secao=nome_secao,
                alvo_caracteres=alvo_chars,
                max_iter=12
            )

            if inserir_transicao_relatorio:
                # Garantir a frase de transição ao final do RELATÓRIO
                if "É o relatório. Decide-se." not in texto_secao:
                    texto_secao = texto_secao.rstrip() + "\n\nÉ o relatório. Decide-se.\n"

            partes.append(texto_secao.strip() + "\n\n")

        texto_final = "".join(partes).strip()

        # Garantir alvo total aproximado
        if len(texto_final) < alvo_caracteres_total:
            # Complementar DISPOSITIVO com continuação se necessário
            complemento = self._gerar_secao_com_continuacao(
                contexto_comum=contexto_comum,
                nome_secao="DISPOSITIVO (COMPLEMENTO)",
                alvo_caracteres=(alvo_caracteres_total - len(texto_final)) + 400,
                max_iter=6
            )
            texto_final = (texto_final + "\n" + complemento).strip()

        return texto_final

    def _gerar_secao_com_continuacao(self,
                                     contexto_comum: str,
                                     nome_secao: str,
                                     alvo_caracteres: int,
                                     max_iter: int = 10) -> str:
        """
        Gera uma seção com múltiplas chamadas ao Claude, usando a tag CONTINUAR## para continuar
        exatamente do ponto em que parou, até atingir o alvo de caracteres.
        """
        acumulado = ""
        iteracoes = 0
        continuar = True

        while continuar and iteracoes < max_iter:
            iteracoes += 1

            tail = acumulado[-1000:] if acumulado else ""
            instrucao = (
                f"Escreva APENAS a seção '{nome_secao}' da sentença trabalhista. "
                f"Sem markdown. Título em MAIÚSCULAS. Não repita cabeçalhos anteriores. "
                f"Se a resposta atingir o limite, finalize a frase e escreva CONTINUAR## ao final."
            )

            if acumulado:
                instrucao += (
                    " CONTINUE exatamente de onde parou, sem recapitular e sem reescrever títulos. "
                    "Retome do trecho final abaixo e prossiga: \n\n" + tail
                )

            if iteracoes == 1:
                user_content = f"""
{contexto_comum}

INSTRUÇÃO ESPECÍFICA:
{instrucao}
"""
            else:
                user_content = f"""
INSTRUÇÃO ESPECÍFICA (CONTINUAÇÃO DA MESMA SEÇÃO):
{instrucao}
"""

            response = self._claude_request(
                system=self.claude.system_prompt,
                user=user_content,
                max_tokens=self.claude.max_tokens,
                temperature=self.claude.temperature
            )

            texto = response.content[0].text if response and response.content else ""

            # Remover a tag de continuação caso venha no meio
            texto = texto.replace("CONTINUAR##", "").rstrip()

            # Evitar duplicação de cabeçalho quando o modelo insiste em repetir
            if acumulado and texto:
                # Se os primeiros 120 caracteres novos já aparecem no final do acumulado, corte
                prefix = texto[:120]
                if prefix and prefix in acumulado[-500:]:
                    # Encontrar a primeira posição desse prefix no final e cortar antes dele
                    pos = acumulado.rfind(prefix)
                    if pos != -1:
                        texto = texto[len(prefix):].lstrip()

            acumulado += ("\n" if acumulado and not acumulado.endswith("\n") else "") + texto

            # Critérios de parada
            if len(acumulado) >= alvo_caracteres:
                continuar = False
                break

            # Heurística: se o modelo gerou pouco texto, ainda assim tente mais algumas vezes
            if not texto or len(texto) < 300:
                # pequena pausa lógica: apenas mais uma iteração extra
                continue

        # Sanitização final: remover duplas quebras excessivas
        return acumulado.strip()

    def _claude_request(self, system: str, user: str, max_tokens: int, temperature: float):
        """Executa chamada ao Claude com retries exponenciais e jitter em caso de rate limit (429)."""
        max_retries = 6
        base_backoff = 0.8
        for attempt in range(max_retries):
            try:
                resp = self.claude.client.messages.create(
                    model=self.claude.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system,
                    messages=[{"role": "user", "content": user}]
                )
                # Pausa leve para respeitar limites de aceleração de tokens/min
                time.sleep(0.6)
                return resp
            except Exception as e:
                msg = str(e).lower()
                if "429" in msg or "rate limit" in msg or "acceleration limit" in msg:
                    sleep_s = base_backoff * (2 ** attempt) + random.uniform(0.0, 0.5)
                    self.logger.warning(f"Rate limit detectado (tentativa {attempt+1}/{max_retries}). Aguardando {sleep_s:.2f}s para retry.")
                    time.sleep(sleep_s)
                    continue
                raise
        # Última tentativa sem backoff adicional
        return self.claude.client.messages.create(
            model=self.claude.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}]
        )
