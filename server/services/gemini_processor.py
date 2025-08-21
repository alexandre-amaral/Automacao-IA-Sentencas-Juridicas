"""
Módulo para processamento de processos jurídicos com Google Gemini
Extrai informações estruturadas de processos trabalhistas usando prompting otimizado
"""

import google.generativeai as genai
from typing import Dict, List, Optional, Any
import json
import os
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass
class ParteProcesso:
    """Informações de uma parte do processo"""
    nome: str
    tipo: str  # "requerente" ou "requerida"
    qualificacao: Optional[str] = None
    endereco: Optional[str] = None

@dataclass
class PedidoProcesso:
    """Pedido formulado no processo"""
    descricao: str
    categoria: str  # ex: "verbas_rescisórias", "horas_extras", "dano_moral"
    valor_estimado: Optional[str] = None
    deferido: Optional[bool] = None
    fundamentacao_decisao: Optional[str] = None
    criterios_calculo: Optional[str] = None
    periodo_aplicacao: Optional[str] = None

@dataclass
class FatoRelevante:
    """Fato relevante para o julgamento"""
    descricao: str
    fonte: str  # "inicial", "defesa", "testemunha", "perícia"
    impacto_decisao: Optional[str] = None
    detalhes_prova: Optional[str] = None
    contradições: Optional[str] = None

@dataclass
class TestemunhaDepoimento:
    """Depoimento de testemunha"""
    nome: str
    parte_convite: str  # "requerente" ou "requerida"
    resumo_depoimento: str
    pontos_relevantes: List[str]
    contradições: Optional[str] = None

@dataclass
class NormaColetiva:
    """Norma coletiva aplicável"""
    sindicato: str
    vigencia: str
    clausulas_relevantes: List[str]
    valores_previstos: Dict[str, str]

@dataclass
class ProcessoEstruturado:
    """Estrutura completa das informações extraídas do processo"""
    numero_processo: Optional[str]
    partes: List[ParteProcesso]
    pedidos: List[PedidoProcesso]
    fatos_relevantes: List[FatoRelevante]
    testemunhas: List[TestemunhaDepoimento]
    normas_coletivas: List[NormaColetiva]
    periodo_contratual: Optional[str]
    valor_causa: Optional[str]
    competencia: Optional[str]
    jurisprudencias_citadas: List[str]
    decisao_final: Optional[str]
    fundamentacao_resumida: Optional[str]
    # Campos adicionais para melhor extração com valores padrão
    funcao_cargo: Optional[str] = None
    salario_inicial: Optional[str] = None
    salario_final: Optional[str] = None
    jornada_contratual: Optional[str] = None
    motivo_rescisao: Optional[str] = None
    afastamentos: Optional[List[str]] = None
    documentos_relevantes: Optional[List[str]] = None
    preliminares: Optional[List[str]] = None
    honorarios_fixados: Optional[str] = None
    custas_processuais: Optional[str] = None

class GeminiProcessor:
    """Processador de processos jurídicos usando Google Gemini"""
    
    def __init__(self):
        """Inicializa o processador com configurações do Gemini"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não encontrada nas variáveis de ambiente")
        
        genai.configure(api_key=api_key)
        
        # GEMINI 1.5 PRO com MÁXIMA JANELA DE CONTEXTO (2M tokens)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Configurações otimizadas para processos jurídicos longos
        self.generation_config = genai.GenerationConfig(
            temperature=0.1,  # Baixa para precisão jurídica
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,  # Aumentado para respostas mais completas
            candidate_count=1
        )
    
    def extrair_informacoes_processo(self, texto_processo: str) -> ProcessoEstruturado:
        """
        Extrai informações estruturadas do texto do processo
        
        Args:
            texto_processo: Texto completo do processo judicial
            
        Returns:
            ProcessoEstruturado: Informações organizadas do processo
        """
        
        # Prompt estruturado para extração de informações
        prompt = self._criar_prompt_extracao(texto_processo)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Parse da resposta JSON
            resultado_json = self._extrair_json_resposta(response.text)
            
            # Converter para objeto estruturado
            return self._converter_para_processo_estruturado(resultado_json)
            
        except Exception as e:
            raise Exception(f"Erro ao processar com Gemini: {str(e)}")
    
    def _criar_prompt_extracao(self, texto_processo: str) -> str:
        """Cria prompt estruturado para extração de informações"""
        
        prompt_base = """
TAREFA: Extrair informações estruturadas de um processo trabalhista brasileiro.

REGRAS IMPORTANTES:
- Use APENAS informações contidas no texto fornecido
- NÃO invente ou adicione informações externas
- Se uma informação não estiver clara, marque como null
- Seja preciso e objetivo
- Mantenha a terminologia jurídica correta

TEXTO DO PROCESSO:
"""
        
        prompt_instrucoes = """

INSTRUÇÕES DE EXTRAÇÃO DETALHADA:

1. IDENTIFIQUE AS PARTES:
   - Nome completo do requerente (trabalhador)
   - Nome completo da empresa requerida
   - Qualificações completas (endereço, CPF/CNPJ quando mencionados)
   - Função exercida e admissão/demissão

2. EXTRAIA TODOS OS PEDIDOS ESPECÍFICOS:
   - Horas extras e reflexos (percentual, período)
   - Intervalo intrajornada, interjornada, intersemanal
   - Tempo de espera/sobreaviso
   - Adicional noturno, insalubridade, periculosidade
   - Participação nos lucros/resultados (PLR/PPR)
   - Diferenças de diárias/ajuda de custo
   - Verbas rescisórias e reflexos
   - Multas convencionais específicas
   - Descontos questionados
   - Danos morais e valores
   - Reintegração/estabilidade
   - Reconhecimento de vínculo
   - FGTS e reflexos
   - Categorize cada pedido precisamente

3. MAPEIE FATOS PROBATÓRIOS DETALHADOS:
   - Alegações específicas da inicial com detalhes
   - Argumentos defensivos da empresa
   - Nomes e depoimentos completos de testemunhas
   - Resultados de perícias e laudos
   - Documentos apresentados pelas partes
   - Controles de ponto e jornada
   - Normas coletivas aplicáveis
   - Contradições probatórias importantes

4. EXTRAIA INFORMAÇÕES CONTRATUAIS COMPLETAS:
   - Data exata de admissão e demissão
   - Função/cargo detalhado
   - Salário e evolutivo salarial
   - Jornada contratual
   - Local de trabalho
   - Benefícios concedidos
   - Afastamentos e licenças

5. ANALISE JURISPRUDÊNCIA E LEGISLAÇÃO:
   - Súmulas do TST citadas
   - Orientações jurisprudenciais
   - Leis específicas (CLT, Lei 13.103/2015, etc.)
   - Decisões do STF (ADIs, ADCs)
   - Precedentes mencionados
   - Normas coletivas da categoria

6. DECISÃO E FUNDAMENTAÇÃO DETALHADA:
   - Resumo completo da fundamentação por tópico
   - Decisão específica para cada pedido
   - Valores deferidos quando mencionados
   - Critérios de cálculo estabelecidos
   - Honorários advocatícios fixados
   - Custas processuais

FORMATO DE RESPOSTA (JSON):
{
    "numero_processo": "NUMERO_DO_PROCESSO",
    "partes": [
        {
            "nome": "NOME_DA_PARTE",
            "tipo": "requerente",
            "qualificacao": "QUALIFICACAO"
        }
    ],
    "pedidos": [
        {
            "descricao": "DESCRICAO_DO_PEDIDO",
            "categoria": "CATEGORIA", 
            "valor_estimado": "VALOR",
            "deferido": false
        }
    ],
    "fatos_relevantes": [
        {
            "descricao": "FATO_RELEVANTE",
            "fonte": "inicial",
            "impacto_decisao": "IMPACTO"
        }
    ],
    "periodo_contratual": "PERIODO",
    "valor_causa": "VALOR_DA_CAUSA", 
    "jurisprudencias_citadas": ["JURISPRUDENCIA"],
    "decisao_final": "DECISAO",
    "fundamentacao_resumida": "FUNDAMENTACAO"
}

Responda APENAS com o JSON estruturado, sem texto adicional.
"""
        
        return prompt_base + texto_processo + prompt_instrucoes

    def _extrair_json_resposta(self, resposta_texto: str) -> Dict[str, Any]:
        """Extrai JSON da resposta do Gemini"""
        
        # Procurar por JSON na resposta
        json_match = re.search(r'```json\s*(.*?)\s*```', resposta_texto, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Tentar encontrar JSON sem marcadores
            json_str = resposta_texto.strip()
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # Fallback: tentar limpeza adicional
            json_limpo = self._limpar_json(json_str)
            try:
                return json.loads(json_limpo)
            except json.JSONDecodeError:
                raise Exception(f"Não foi possível extrair JSON válido da resposta: {str(e)}")
    
    def _limpar_json(self, json_str: str) -> str:
        """Limpa string JSON para melhorar parsing"""
        
        # Remover comentários e texto extra
        json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        # Encontrar início e fim do objeto JSON
        inicio = json_str.find('{')
        fim = json_str.rfind('}')
        
        if inicio != -1 and fim != -1:
            return json_str[inicio:fim+1]
        
        return json_str
    
    def _converter_para_processo_estruturado(self, dados_json: Dict[str, Any]) -> ProcessoEstruturado:
        """Converte dados JSON para objeto ProcessoEstruturado"""
        
        # Converter partes
        partes = []
        for parte_data in dados_json.get('partes', []):
            parte = ParteProcesso(
                nome=parte_data.get('nome', ''),
                tipo=parte_data.get('tipo', ''),
                qualificacao=parte_data.get('qualificacao')
            )
            partes.append(parte)
        
        # Converter pedidos
        pedidos = []
        for pedido_data in dados_json.get('pedidos', []):
            pedido = PedidoProcesso(
                descricao=pedido_data.get('descricao', ''),
                categoria=pedido_data.get('categoria', ''),
                valor_estimado=pedido_data.get('valor_estimado'),
                deferido=pedido_data.get('deferido')
            )
            pedidos.append(pedido)
        
        # Converter fatos relevantes
        fatos_relevantes = []
        for fato_data in dados_json.get('fatos_relevantes', []):
            fato = FatoRelevante(
                descricao=fato_data.get('descricao', ''),
                fonte=fato_data.get('fonte', ''),
                impacto_decisao=fato_data.get('impacto_decisao')
            )
            fatos_relevantes.append(fato)
        
        # Converter testemunhas (com valores padrão)
        testemunhas = []
        for testemunha_data in dados_json.get('testemunhas', []):
            if isinstance(testemunha_data, dict):
                testemunha = TestemunhaDepoimento(
                    nome=testemunha_data.get('nome', ''),
                    parte_convite=testemunha_data.get('parte_convite', ''),
                    resumo_depoimento=testemunha_data.get('resumo_depoimento', ''),
                    pontos_relevantes=testemunha_data.get('pontos_relevantes', []),
                    contradições=testemunha_data.get('contradições')
                )
                testemunhas.append(testemunha)
        
        # Converter normas coletivas (com valores padrão)
        normas_coletivas = []
        for norma_data in dados_json.get('normas_coletivas', []):
            if isinstance(norma_data, dict):
                norma = NormaColetiva(
                    sindicato=norma_data.get('sindicato', ''),
                    vigencia=norma_data.get('vigencia', ''),
                    clausulas_relevantes=norma_data.get('clausulas_relevantes', []),
                    valores_previstos=norma_data.get('valores_previstos', {})
                )
                normas_coletivas.append(norma)
        
        return ProcessoEstruturado(
            numero_processo=dados_json.get('numero_processo'),
            partes=partes,
            pedidos=pedidos,
            fatos_relevantes=fatos_relevantes,
            testemunhas=testemunhas,
            normas_coletivas=normas_coletivas,
            periodo_contratual=dados_json.get('periodo_contratual'),
            valor_causa=dados_json.get('valor_causa'),
            competencia=dados_json.get('competencia'),
            jurisprudencias_citadas=dados_json.get('jurisprudencias_citadas', []),
            decisao_final=dados_json.get('decisao_final'),
            fundamentacao_resumida=dados_json.get('fundamentacao_resumida'),
            # Campos adicionais com valores padrão
            funcao_cargo=dados_json.get('funcao_cargo'),
            salario_inicial=dados_json.get('salario_inicial'),
            salario_final=dados_json.get('salario_final'),
            jornada_contratual=dados_json.get('jornada_contratual'),
            motivo_rescisao=dados_json.get('motivo_rescisao'),
            afastamentos=dados_json.get('afastamentos'),
            documentos_relevantes=dados_json.get('documentos_relevantes'),
            preliminares=dados_json.get('preliminares'),
            honorarios_fixados=dados_json.get('honorarios_fixados'),
            custas_processuais=dados_json.get('custas_processuais')
        )
    
    def gerar_termos_jurisprudencia(self, processo: ProcessoEstruturado) -> List[str]:
        """
        Gera termos de busca para jurisprudência com base no processo
        
        Args:
            processo: Processo estruturado
            
        Returns:
            Lista de termos para busca de jurisprudência
        """
        
        # Criar prompt para geração de termos
        prompt = f"""
Com base nas informações do processo abaixo, gere termos de busca específicos para encontrar jurisprudência relevante.

INFORMAÇÕES DO PROCESSO:
Pedidos principais: {[p.categoria for p in processo.pedidos]}
Fatos relevantes: {[f.descricao[:100] for f in processo.fatos_relevantes[:3]]}
Fundamentação: {processo.fundamentacao_resumida[:300] if processo.fundamentacao_resumida else 'N/A'}

INSTRUÇÕES:
- Gere 5-8 termos de busca específicos e relevantes
- Use terminologia jurídica precisa
- Foque nos temas centrais do processo
- Combine conceitos quando apropriado

FORMATO: Lista de termos separados por vírgula

Exemplo: "justa causa configuração", "dano moral trabalhista", "horas extras supressão intervalo"
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            termos_texto = response.text.strip()
            # Dividir por vírgula e limpar
            termos = [termo.strip().strip('"\'') for termo in termos_texto.split(',')]
            # Filtrar termos vazios
            termos = [termo for termo in termos if termo and len(termo) > 3]
            
            return termos[:8]  # Limitar a 8 termos
            
        except Exception as e:
            # Fallback com termos baseados nos pedidos
            termos_fallback = []
            for pedido in processo.pedidos:
                termos_fallback.append(pedido.categoria.replace('_', ' '))
            
            return termos_fallback[:5]

# Função de conveniência para uso direto
def processar_arquivo_processo(arquivo_path: str) -> ProcessoEstruturado:
    """
    Função de conveniência para processar um arquivo de processo
    
    Args:
        arquivo_path: Caminho para o arquivo do processo
        
    Returns:
        ProcessoEstruturado: Informações extraídas
    """
    
    # Importar função de extração de texto
    from pathlib import Path
    
    arquivo = Path(arquivo_path)
    
    # Extrair texto do arquivo
    if arquivo.suffix.lower() == '.docx':
        from docx import Document
        doc = Document(str(arquivo))
        texto_completo = '\n'.join([par.text for par in doc.paragraphs if par.text.strip()])
    else:
        # Para PDFs, usar PyMuPDF
        import fitz
        doc = fitz.open(str(arquivo))
        texto_completo = ""
        for page in doc:
            texto_completo += page.get_text("text") + "\n"
        doc.close()
    
    if len(texto_completo) < 100:
        raise ValueError("Arquivo muito pequeno ou não foi possível extrair texto")
    
    # Processar com Gemini
    processor = GeminiProcessor()
    return processor.extrair_informacoes_processo(texto_completo)
