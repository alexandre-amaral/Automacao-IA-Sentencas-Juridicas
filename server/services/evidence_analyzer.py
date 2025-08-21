"""
Serviço Especializado em Análise de Provas e Contradições
Analisa depoimentos, documentos e identifica contradições probatórias
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import re

@dataclass
class ContradicaoProbatoria:
    """Estrutura para contradições encontradas"""
    tipo: str  # "testemunhal", "documental", "testemunha_vs_documento"
    descricao: str
    elementos_conflitantes: List[str]
    impacto_decisao: str
    peso_probatorio: int  # 1-10, onde 10 é mais relevante

@dataclass
class AnaliseTestemunha:
    """Análise detalhada de depoimento"""
    nome: str
    parte_convite: str
    credibilidade: int  # 1-10
    pontos_favoraveis: List[str]
    pontos_desfavoraveis: List[str]
    contradicoes_internas: List[str]
    corroboracao: List[str]

class EvidenceAnalyzer:
    """Analisador especializado em provas e contradições"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analisar_depoimentos_testemunhas(self, testemunhas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa depoimentos e identifica contradições entre testemunhas
        
        Args:
            testemunhas: Lista de depoimentos de testemunhas
            
        Returns:
            Análise completa dos depoimentos
        """
        
        analises_individuais = []
        contradicoes_encontradas = []
        
        for testemunha in testemunhas:
            analise = self._analisar_testemunha_individual(testemunha)
            analises_individuais.append(analise)
        
        # Comparar depoimentos para encontrar contradições
        contradicoes = self._identificar_contradicoes_testemunhais(testemunhas)
        
        return {
            "analises_individuais": analises_individuais,
            "contradicoes_encontradas": contradicoes,
            "sintese_probatoria": self._sintetizar_prova_oral(analises_individuais, contradicoes),
            "recomendacao_judicial": self._recomendar_decisao_probatoria(analises_individuais, contradicoes)
        }
    
    def _analisar_testemunha_individual(self, testemunha: Dict[str, Any]) -> AnaliseTestemunha:
        """Analisa depoimento individual de testemunha"""
        
        nome = testemunha.get("nome", "Não informado")
        parte = testemunha.get("parte_convite", "")
        depoimento = testemunha.get("depoimento", "")
        
        # Análise de credibilidade baseada em indicadores textuais
        credibilidade = self._calcular_credibilidade(depoimento)
        
        # Identificar pontos favoráveis e desfavoráveis
        pontos_fav, pontos_desfav = self._classificar_pontos_depoimento(depoimento, parte)
        
        # Identificar contradições internas
        contradicoes = self._identificar_contradicoes_internas(depoimento)
        
        return AnaliseTestemunha(
            nome=nome,
            parte_convite=parte,
            credibilidade=credibilidade,
            pontos_favoraveis=pontos_fav,
            pontos_desfavoraveis=pontos_desfav,
            contradicoes_internas=contradicoes,
            corroboracao=[]
        )
    
    def _calcular_credibilidade(self, depoimento: str) -> int:
        """Calcula score de credibilidade baseado em indicadores textuais"""
        
        score = 5  # Base neutra
        
        # Indicadores positivos
        indicadores_positivos = [
            "lembro claramente", "tenho certeza", "sempre", "todos os dias",
            "presenciei", "vi pessoalmente", "acompanhei", "participei"
        ]
        
        # Indicadores negativos
        indicadores_negativos = [
            "não lembro", "acho que", "talvez", "não tenho certeza",
            "ouvi dizer", "comentaram", "parece", "creio que"
        ]
        
        # Indicadores de contradição
        indicadores_contradicao = [
            "inicialmente", "depois", "na verdade", "corrigindo",
            "modificou", "mudou", "alterou a versão"
        ]
        
        for indicador in indicadores_positivos:
            score += depoimento.lower().count(indicador) * 0.5
        
        for indicador in indicadores_negativos:
            score -= depoimento.lower().count(indicador) * 0.7
        
        for indicador in indicadores_contradicao:
            score -= depoimento.lower().count(indicador) * 1.0
        
        return max(1, min(10, int(score)))
    
    def _classificar_pontos_depoimento(self, depoimento: str, parte: str) -> Tuple[List[str], List[str]]:
        """Classifica pontos do depoimento como favoráveis ou desfavoráveis"""
        
        pontos_favoraveis = []
        pontos_desfavoraveis = []
        
        # Análise baseada em padrões textuais
        if "confirmou" in depoimento.lower() or "corroborou" in depoimento.lower():
            if parte == "requerente":
                pontos_favoraveis.append("Confirmou alegações do autor")
            else:
                pontos_desfavoraveis.append("Confirmou versão da empresa")
        
        if "contraditório" in depoimento.lower() or "mudou" in depoimento.lower():
            pontos_desfavoraveis.append("Apresentou versões contraditórias")
        
        if "demonstrou incerteza" in depoimento.lower():
            pontos_desfavoraveis.append("Demonstrou incerteza sobre os fatos")
        
        return pontos_favoraveis, pontos_desfavoraveis
    
    def _identificar_contradicoes_internas(self, depoimento: str) -> List[str]:
        """Identifica contradições internas no mesmo depoimento"""
        
        contradicoes = []
        
        # Padrões que indicam contradição
        padroes_contradicao = [
            r"inicialmente afirmou.*depois.*modificou",
            r"primeiro disse.*posteriormente.*alterou",
            r"começou dizendo.*ao final.*mudou"
        ]
        
        for padrao in padroes_contradicao:
            if re.search(padrao, depoimento.lower()):
                contradicoes.append(f"Contradição identificada: {padrao}")
        
        return contradicoes
    
    def _identificar_contradicoes_testemunhais(self, testemunhas: List[Dict[str, Any]]) -> List[ContradicaoProbatoria]:
        """Identifica contradições entre diferentes testemunhas"""
        
        contradicoes = []
        
        if len(testemunhas) < 2:
            return contradicoes
        
        # Comparar testemunhas de partes diferentes
        testemunhas_autor = [t for t in testemunhas if t.get("parte_convite") == "requerente"]
        testemunhas_reu = [t for t in testemunhas if t.get("parte_convite") == "requerida"]
        
        if testemunhas_autor and testemunhas_reu:
            contradicao = ContradicaoProbatoria(
                tipo="testemunhal",
                descricao="Versões conflitantes entre testemunhas das partes",
                elementos_conflitantes=[
                    f"Testemunha do autor: {testemunhas_autor[0].get('resumo', '')}",
                    f"Testemunha da ré: {testemunhas_reu[0].get('resumo', '')}"
                ],
                impacto_decisao="Necessário análise de credibilidade",
                peso_probatorio=8
            )
            contradicoes.append(contradicao)
        
        return contradicoes
    
    def _sintetizar_prova_oral(self, analises: List[AnaliseTestemunha], 
                              contradicoes: List[ContradicaoProbatoria]) -> str:
        """Cria síntese da prova oral para fundamentação"""
        
        if not analises:
            return "Não foram ouvidas testemunhas."
        
        sintese = "ANÁLISE DA PROVA ORAL:\n\n"
        
        for analise in analises:
            sintese += f"Testemunha {analise.nome} (convite da {analise.parte_convite}):\n"
            
            if analise.pontos_favoraveis:
                sintese += f"- Pontos relevantes: {'; '.join(analise.pontos_favoraveis)}\n"
            
            if analise.contradicoes_internas:
                sintese += f"- Contradições: {'; '.join(analise.contradicoes_internas)}\n"
            
            sintese += f"- Credibilidade: {'Alta' if analise.credibilidade >= 7 else 'Média' if analise.credibilidade >= 4 else 'Baixa'}\n\n"
        
        if contradicoes:
            sintese += "CONTRADIÇÕES PROBATÓRIAS IDENTIFICADAS:\n"
            for contradicao in contradicoes:
                sintese += f"- {contradicao.descricao}\n"
        
        return sintese
    
    def _recomendar_decisao_probatoria(self, analises: List[AnaliseTestemunha], 
                                     contradicoes: List[ContradicaoProbatoria]) -> str:
        """Recomenda decisão baseada na análise probatória"""
        
        if not analises:
            return "Ausência de prova oral. Decidir com base em prova documental."
        
        # Calcular peso das provas
        peso_autor = sum(a.credibilidade for a in analises if a.parte_convite == "requerente")
        peso_reu = sum(a.credibilidade for a in analises if a.parte_convite == "requerida")
        
        if peso_autor > peso_reu:
            return "Prova oral favorável ao requerente. Testemunha apresenta maior credibilidade."
        elif peso_reu > peso_autor:
            return "Prova oral favorável à requerida. Versão empresarial mais consistente."
        else:
            return "Prova oral inconclusiva. Necessário decidir com base em outros elementos."
    
    def analisar_onus_proba(self, pedido: str, parte_interessada: str, 
                           provas_apresentadas: List[str]) -> Dict[str, str]:
        """
        Analisa ônus da prova para pedido específico
        
        Args:
            pedido: Tipo do pedido (ex: "horas_extras", "dano_moral")
            parte_interessada: Quem tem interesse na prova
            provas_apresentadas: Provas efetivamente apresentadas
            
        Returns:
            Análise do ônus probatório
        """
        
        regras_onus = {
            "horas_extras": "Autor deve provar jornada alegada (art. 818, I, CLT)",
            "intervalo_suprimido": "Autor deve provar supressão (art. 818, I, CLT)",
            "dano_moral": "Autor deve provar ato ilícito e dano (arts. 186 e 927, CC)",
            "despedida_discriminatoria": "Autor deve provar discriminação",
            "pagamento_verbas": "Empresa deve provar quitação (art. 818, II, CLT)",
            "controle_jornada": "Empresa com +20 empregados deve apresentar (Súmula 338, TST)"
        }
        
        cumprimento = "Sim" if provas_apresentadas else "Não"
        regra = regras_onus.get(pedido, "Regra geral do ônus da prova")
        
        return {
            "regra_aplicavel": regra,
            "parte_onerada": parte_interessada,
            "onus_cumprido": cumprimento,
            "provas_apresentadas": "; ".join(provas_apresentadas) if provas_apresentadas else "Nenhuma",
            "consequencia": "Presunção em favor da parte onerada" if not provas_apresentadas else "Ônus cumprido"
        }
    
    def gerar_fundamentacao_probatoria(self, analise_testemunhas: Dict[str, Any],
                                     analise_onus: Dict[str, Any]) -> str:
        """
        Gera fundamentação específica sobre questões probatórias
        
        Args:
            analise_testemunhas: Resultado da análise de testemunhas
            analise_onus: Resultado da análise de ônus
            
        Returns:
            Fundamentação formatada para sentença
        """
        
        fundamentacao = """
        ANÁLISE PROBATÓRIA
        
        {sintese_oral}
        
        ÔNUS DA PROVA
        {analise_onus_texto}
        
        CONCLUSÃO PROBATÓRIA
        {conclusao}
        """
        
        return fundamentacao.format(
            sintese_oral=analise_testemunhas.get("sintese_probatoria", ""),
            analise_onus_texto=self._formatar_analise_onus(analise_onus),
            conclusao=analise_testemunhas.get("recomendacao_judicial", "")
        )
    
    def _formatar_analise_onus(self, analise: Dict[str, Any]) -> str:
        """Formata análise de ônus da prova"""
        
        return f"""
        Regra aplicável: {analise.get('regra_aplicavel', '')}
        Parte onerada: {analise.get('parte_onerada', '')}
        Ônus cumprido: {analise.get('onus_cumprido', '')}
        Provas apresentadas: {analise.get('provas_apresentadas', '')}
        Consequência: {analise.get('consequencia', '')}
        """


