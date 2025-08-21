"""
Validador de Qualidade de Sentenças
Sistema para validar e melhorar a qualidade das sentenças geradas
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class QualityMetric:
    """Métrica individual de qualidade"""
    nome: str
    valor: float  # 0-100
    peso: float   # Importância da métrica
    descricao: str
    passou: bool

@dataclass
class QualityReport:
    """Relatório completo de qualidade"""
    score_geral: float
    score_por_categoria: Dict[str, float]
    metricas: List[QualityMetric]
    recomendacoes: List[str]
    problemas_identificados: List[str]
    aprovado: bool

class QualityValidator:
    """Validador de qualidade de sentenças judiciais"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.score_minimo_aprovacao = 75.0
    
    def validar_sentenca_completa(self, sentenca: str, dados_processo: Dict[str, Any]) -> QualityReport:
        """
        Valida qualidade completa da sentença gerada
        
        Args:
            sentenca: Texto da sentença
            dados_processo: Dados do processo para validação
            
        Returns:
            Relatório completo de qualidade
        """
        
        metricas = []
        
        # 1. VALIDAÇÃO ESTRUTURAL
        metricas.extend(self._validar_estrutura(sentenca))
        
        # 2. VALIDAÇÃO DE CONTEÚDO
        metricas.extend(self._validar_conteudo(sentenca, dados_processo))
        
        # 3. VALIDAÇÃO JURÍDICA
        metricas.extend(self._validar_aspetos_juridicos(sentenca))
        
        # 4. VALIDAÇÃO DE COMPLETUDE
        metricas.extend(self._validar_completude(sentenca, dados_processo))
        
        # 5. VALIDAÇÃO DE ESTILO
        metricas.extend(self._validar_estilo_judicial(sentenca))
        
        # Calcular scores
        score_geral = self._calcular_score_geral(metricas)
        score_por_categoria = self._calcular_scores_por_categoria(metricas)
        
        # Gerar recomendações
        recomendacoes = self._gerar_recomendacoes(metricas)
        problemas = self._identificar_problemas(metricas)
        
        aprovado = score_geral >= self.score_minimo_aprovacao
        
        return QualityReport(
            score_geral=score_geral,
            score_por_categoria=score_por_categoria,
            metricas=metricas,
            recomendacoes=recomendacoes,
            problemas_identificados=problemas,
            aprovado=aprovado
        )
    
    def _validar_estrutura(self, sentenca: str) -> List[QualityMetric]:
        """Valida estrutura obrigatória da sentença"""
        
        metricas = []
        
        # Seções obrigatórias
        secoes_obrigatorias = ["SENTENÇA", "RELATÓRIO", "FUNDAMENTAÇÃO", "DISPOSITIVO"]
        
        for secao in secoes_obrigatorias:
            tem_secao = secao in sentenca.upper()
            metricas.append(QualityMetric(
                nome=f"tem_secao_{secao.lower()}",
                valor=100.0 if tem_secao else 0.0,
                peso=0.2,
                descricao=f"Presença da seção {secao}",
                passou=tem_secao
            ))
        
        # Transição "É o relatório. Decide-se."
        tem_transicao = "É o relatório. Decide-se." in sentenca
        metricas.append(QualityMetric(
            nome="tem_transicao_padrao",
            valor=100.0 if tem_transicao else 0.0,
            peso=0.1,
            descricao="Presença da transição padrão",
            passou=tem_transicao
        ))
        
        # Tamanho adequado
        tamanho_adequado = len(sentenca) >= 10000  # Mínimo 10k caracteres
        metricas.append(QualityMetric(
            nome="tamanho_adequado",
            valor=min(100.0, (len(sentenca) / 10000) * 100),
            peso=0.1,
            descricao="Tamanho adequado da sentença",
            passou=tamanho_adequado
        ))
        
        return metricas
    
    def _validar_conteudo(self, sentenca: str, dados_processo: Dict[str, Any]) -> List[QualityMetric]:
        """Valida conteúdo específico da sentença"""
        
        metricas = []
        
        # Presença de dados das partes
        partes = dados_processo.get("partes", [])
        if partes:
            for parte in partes:
                nome = parte.get("nome", "")
                if nome:
                    tem_nome = nome.upper() in sentenca.upper()
                    metricas.append(QualityMetric(
                        nome=f"menciona_parte_{parte.get('tipo', '')}",
                        valor=100.0 if tem_nome else 0.0,
                        peso=0.15,
                        descricao=f"Menciona parte {parte.get('tipo', '')}",
                        passou=tem_nome
                    ))
        
        # Análise de pedidos
        pedidos = dados_processo.get("pedidos", [])
        pedidos_mencionados = 0
        for pedido in pedidos:
            categoria = pedido.get("categoria", "").replace("_", " ")
            if categoria and categoria.lower() in sentenca.lower():
                pedidos_mencionados += 1
        
        if pedidos:
            percentual_pedidos = (pedidos_mencionados / len(pedidos)) * 100
            metricas.append(QualityMetric(
                nome="cobertura_pedidos",
                valor=percentual_pedidos,
                peso=0.25,
                descricao="Cobertura dos pedidos formulados",
                passou=percentual_pedidos >= 80
            ))
        
        # Presença de IDs de documentos
        ids_encontrados = len(re.findall(r'\(ID\s+[a-f0-9]+\)', sentenca, re.IGNORECASE))
        tem_ids_adequados = ids_encontrados >= 3
        metricas.append(QualityMetric(
            nome="referencias_documentos",
            valor=min(100.0, (ids_encontrados / 5) * 100),
            peso=0.1,
            descricao="Referências a documentos com IDs",
            passou=tem_ids_adequados
        ))
        
        return metricas
    
    def _validar_aspetos_juridicos(self, sentenca: str) -> List[QualityMetric]:
        """Valida aspectos jurídicos da sentença"""
        
        metricas = []
        
        # Citações de dispositivos legais
        dispositivos_clt = len(re.findall(r'art\.\s*\d+.*CLT', sentenca, re.IGNORECASE))
        dispositivos_cf = len(re.findall(r'art\.\s*\d+.*CF', sentenca, re.IGNORECASE))
        
        tem_dispositivos_adequados = (dispositivos_clt + dispositivos_cf) >= 5
        metricas.append(QualityMetric(
            nome="citacoes_dispositivos_legais",
            valor=min(100.0, ((dispositivos_clt + dispositivos_cf) / 10) * 100),
            peso=0.2,
            descricao="Citações de dispositivos legais",
            passou=tem_dispositivos_adequados
        ))
        
        # Jurisprudência
        sumulas_tst = len(re.findall(r'Súmula\s+\d+.*TST', sentenca, re.IGNORECASE))
        decisoes_stf = len(re.findall(r'STF|Supremo', sentenca, re.IGNORECASE))
        
        tem_jurisprudencia = (sumulas_tst + decisoes_stf) >= 2
        metricas.append(QualityMetric(
            nome="jurisprudencia_citada",
            valor=min(100.0, ((sumulas_tst + decisoes_stf) / 5) * 100),
            peso=0.2,
            descricao="Citações de jurisprudência",
            passou=tem_jurisprudencia
        ))
        
        # Ônus da prova
        menciona_onus = any(termo in sentenca.lower() for termo in ["ônus", "art. 818", "art. 373"])
        metricas.append(QualityMetric(
            nome="analise_onus_prova",
            valor=100.0 if menciona_onus else 0.0,
            peso=0.15,
            descricao="Análise do ônus da prova",
            passou=menciona_onus
        ))
        
        return metricas
    
    def _validar_completude(self, sentenca: str, dados_processo: Dict[str, Any]) -> List[QualityMetric]:
        """Valida completude da análise"""
        
        metricas = []
        
        # Análise de testemunhas
        testemunhas = dados_processo.get("testemunhas", [])
        if testemunhas:
            testemunhas_analisadas = 0
            for testemunha in testemunhas:
                nome = testemunha.get("nome", "")
                if nome and nome.upper() in sentenca.upper():
                    testemunhas_analisadas += 1
            
            percentual_testemunhas = (testemunhas_analisadas / len(testemunhas)) * 100 if testemunhas else 100
            metricas.append(QualityMetric(
                nome="analise_testemunhas",
                valor=percentual_testemunhas,
                peso=0.2,
                descricao="Análise individual de testemunhas",
                passou=percentual_testemunhas >= 80
            ))
        
        # Seções técnicas obrigatórias
        secoes_tecnicas = [
            "honorários", "custas", "correção monetária", 
            "juros", "contribuições", "fgts"
        ]
        
        secoes_presentes = sum(1 for secao in secoes_tecnicas if secao.lower() in sentenca.lower())
        percentual_secoes = (secoes_presentes / len(secoes_tecnicas)) * 100
        
        metricas.append(QualityMetric(
            nome="secoes_tecnicas_completas",
            valor=percentual_secoes,
            peso=0.15,
            descricao="Presença de seções técnicas obrigatórias",
            passou=percentual_secoes >= 70
        ))
        
        return metricas
    
    def _validar_estilo_judicial(self, sentenca: str) -> List[QualityMetric]:
        """Valida estilo e linguagem judicial"""
        
        metricas = []
        
        # Conectores jurídicos
        conectores = [
            "ante o exposto", "considerando", "tendo em vista",
            "conforme", "nos termos", "com base"
        ]
        
        conectores_encontrados = sum(1 for conector in conectores if conector.lower() in sentenca.lower())
        tem_conectores_adequados = conectores_encontrados >= 5
        
        metricas.append(QualityMetric(
            nome="linguagem_judicial_adequada",
            valor=min(100.0, (conectores_encontrados / 10) * 100),
            peso=0.1,
            descricao="Uso de linguagem judicial adequada",
            passou=tem_conectores_adequados
        ))
        
        # Formatação adequada
        tem_maiusculas_titulos = len(re.findall(r'^[A-Z\s]+$', sentenca, re.MULTILINE)) >= 5
        nao_tem_markdown = '#' not in sentenca and '**' not in sentenca
        
        metricas.append(QualityMetric(
            nome="formatacao_adequada",
            valor=100.0 if (tem_maiusculas_titulos and nao_tem_markdown) else 50.0,
            peso=0.1,
            descricao="Formatação adequada sem markdown",
            passou=tem_maiusculas_titulos and nao_tem_markdown
        ))
        
        return metricas
    
    def _calcular_score_geral(self, metricas: List[QualityMetric]) -> float:
        """Calcula score geral ponderado"""
        
        if not metricas:
            return 0.0
        
        peso_total = sum(m.peso for m in metricas)
        if peso_total == 0:
            return 0.0
        
        score_ponderado = sum(m.valor * m.peso for m in metricas)
        return score_ponderado / peso_total
    
    def _calcular_scores_por_categoria(self, metricas: List[QualityMetric]) -> Dict[str, float]:
        """Calcula scores por categoria"""
        
        categorias = {
            "estrutura": ["tem_secao_", "tem_transicao", "tamanho_"],
            "conteudo": ["menciona_", "cobertura_", "referencias_"],
            "juridico": ["citacoes_", "jurisprudencia_", "analise_onus"],
            "completude": ["analise_testemunhas", "secoes_tecnicas"],
            "estilo": ["linguagem_", "formatacao_"]
        }
        
        scores = {}
        
        for categoria, prefixos in categorias.items():
            metricas_categoria = [m for m in metricas if any(m.nome.startswith(p) for p in prefixos)]
            if metricas_categoria:
                scores[categoria] = self._calcular_score_geral(metricas_categoria)
            else:
                scores[categoria] = 0.0
        
        return scores
    
    def _gerar_recomendacoes(self, metricas: List[QualityMetric]) -> List[str]:
        """Gera recomendações baseadas nas métricas"""
        
        recomendacoes = []
        
        for metrica in metricas:
            if not metrica.passou:
                if "secao" in metrica.nome:
                    recomendacoes.append(f"Incluir seção obrigatória: {metrica.descricao}")
                elif "pedidos" in metrica.nome:
                    recomendacoes.append("Analisar TODOS os pedidos formulados individualmente")
                elif "testemunhas" in metrica.nome:
                    recomendacoes.append("Incluir análise detalhada de CADA testemunha")
                elif "dispositivos" in metrica.nome:
                    recomendacoes.append("Aumentar citações de dispositivos legais (CLT, CF/88)")
                elif "jurisprudencia" in metrica.nome:
                    recomendacoes.append("Incluir mais súmulas do TST e decisões do STF")
        
        return list(set(recomendacoes))  # Remove duplicatas
    
    def _identificar_problemas(self, metricas: List[QualityMetric]) -> List[str]:
        """Identifica problemas críticos"""
        
        problemas = []
        
        metricas_criticas = [m for m in metricas if m.peso >= 0.2 and not m.passou]
        
        for metrica in metricas_criticas:
            problemas.append(f"CRÍTICO: {metrica.descricao} - Score: {metrica.valor:.1f}")
        
        return problemas
    
    def sugerir_melhorias(self, relatorio: QualityReport) -> Dict[str, str]:
        """Sugere melhorias específicas baseadas no relatório"""
        
        melhorias = {}
        
        if relatorio.score_por_categoria.get("estrutura", 0) < 80:
            melhorias["estrutura"] = """
            - Incluir TODAS as seções obrigatórias: SENTENÇA, RELATÓRIO, FUNDAMENTAÇÃO, DISPOSITIVO
            - Usar a transição padrão: "É o relatório. Decide-se."
            - Garantir tamanho mínimo de 10.000 caracteres
            """
        
        if relatorio.score_por_categoria.get("juridico", 0) < 80:
            melhorias["juridico"] = """
            - Citar mais dispositivos legais específicos (art. X da CLT, art. Y da CF/88)
            - Incluir súmulas do TST e orientações jurisprudenciais
            - Mencionar decisões do STF quando aplicáveis (com modulação temporal)
            - Sempre analisar ônus da prova (art. 818 CLT, art. 373 CPC)
            """
        
        if relatorio.score_por_categoria.get("completude", 0) < 80:
            melhorias["completude"] = """
            - Analisar CADA testemunha individualmente
            - Incluir todas as seções técnicas: honorários, custas, correção monetária, etc.
            - Abordar TODOS os pedidos formulados
            - Mencionar todos os documentos com IDs específicos
            """
        
        return melhorias


