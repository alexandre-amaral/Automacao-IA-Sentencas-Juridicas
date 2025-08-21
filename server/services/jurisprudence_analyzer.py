"""
Serviço Especializado em Análise Jurisprudencial
Analisa e aplica jurisprudência específica para casos trabalhistas
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class Jurisprudencia:
    """Estrutura para jurisprudência específica"""
    tipo: str  # "sumula", "orientacao", "adi", "precedente"
    numero: str
    tribunal: str  # "TST", "STF", "TRT"
    ementa: str
    data_publicacao: Optional[str] = None
    situacao: str = "vigente"  # "vigente", "cancelada", "superada"
    aplicabilidade: str = ""  # contexto de aplicação

@dataclass
class AnaliseConstitucional:
    """Análise de constitucionalidade de normas"""
    dispositivo: str
    adi_numero: Optional[str]
    decisao_stf: str
    modulacao_temporal: Optional[str]
    efeitos_praticos: str

class JurisprudenceAnalyzer:
    """Analisador especializado em jurisprudência trabalhista"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._carregar_jurisprudencia_base()
    
    def _carregar_jurisprudencia_base(self):
        """Carrega jurisprudência fundamental trabalhista"""
        
        self.jurisprudencia_base = {
            # Súmulas TST relevantes
            "sumula_338": Jurisprudencia(
                tipo="sumula",
                numero="338",
                tribunal="TST",
                ementa="JORNADA DE TRABALHO. CONTROLE DE FREQUÊNCIA. CARTÃO DE PONTO. REGISTRO DE HORÁRIOS...",
                aplicabilidade="controle_jornada"
            ),
            
            # Lei 13.103/2015 - Motoristas
            "lei_motoristas": {
                "artigo_235c": {
                    "tempo_espera": "§8º: São considerados tempo de espera as horas em que o motorista profissional...",
                    "adi_5322": AnaliseConstitucional(
                        dispositivo="Art. 235-C, §§1º, 8º e 9º",
                        adi_numero="5322",
                        decisao_stf="Parcialmente procedente com modulação temporal",
                        modulacao_temporal="12/07/2023 para tempo de espera; 30/08/2023 para fracionamento",
                        efeitos_praticos="Tempo de espera considera horas extras a partir de 12/07/2023"
                    )
                }
            },
            
            # Orientações Jurisprudenciais TST
            "oj_355": Jurisprudencia(
                tipo="orientacao",
                numero="355",
                tribunal="TST",
                ementa="INTERVALO INTERJORNADA. INOBSERVÂNCIA. HORAS EXTRAS. PERÍODO INTEGRAL...",
                aplicabilidade="intervalo_interjornada"
            )
        }
    
    def analisar_lei_motoristas(self, data_contrato_inicio: str, data_contrato_fim: str) -> Dict[str, Any]:
        """
        Analisa aplicabilidade da Lei 13.103/2015 considerando modulação temporal do STF
        
        Args:
            data_contrato_inicio: Data de início do contrato
            data_contrato_fim: Data de fim do contrato
            
        Returns:
            Análise completa da aplicabilidade
        """
        
        # Datas de referência da modulação do STF
        data_modulacao_tempo_espera = datetime(2023, 7, 12)
        data_modulacao_fracionamento = datetime(2023, 8, 30)
        
        try:
            inicio = datetime.strptime(data_contrato_fim, "%d/%m/%Y")
            fim = datetime.strptime(data_contrato_fim, "%d/%m/%Y")
        except:
            # Formato alternativo
            inicio = datetime.strptime(data_contrato_inicio, "%Y-%m-%d")
            fim = datetime.strptime(data_contrato_fim, "%Y-%m-%d")
        
        analise = {
            "tempo_espera": {
                "aplicavel": fim < data_modulacao_tempo_espera,
                "fundamentacao": "",
                "efeitos": ""
            },
            "fracionamento_intervalo": {
                "aplicavel": fim < data_modulacao_fracionamento,
                "fundamentacao": "",
                "efeitos": ""
            }
        }
        
        if analise["tempo_espera"]["aplicavel"]:
            analise["tempo_espera"]["fundamentacao"] = """
            Considerando que o contrato de trabalho encerrou em {fim}, portanto anterior à modulação 
            temporal fixada pelo STF (12/07/2023), permanece aplicável o disposto no art. 235-C, §8º, da CLT, 
            que expressamente excluía o tempo de espera da computação como jornada de trabalho.
            """.format(fim=data_contrato_fim)
            
            analise["tempo_espera"]["efeitos"] = "Tempo de espera NÃO gera horas extras"
        else:
            analise["tempo_espera"]["fundamentacao"] = """
            Em decorrência da decisão do STF na ADI 5322 com modulação temporal a partir de 12/07/2023,
            o tempo de espera deve ser considerado como tempo à disposição do empregador.
            """
            
            analise["tempo_espera"]["efeitos"] = "Tempo de espera GERA horas extras"
        
        if analise["fracionamento_intervalo"]["aplicavel"]:
            analise["fracionamento_intervalo"]["fundamentacao"] = """
            O fracionamento do intervalo interjornada era permitido à época da relação contratual,
            conforme art. 235-C, §3º da CLT, antes da modulação dos efeitos pelo STF (30/08/2023).
            """
        else:
            analise["fracionamento_intervalo"]["fundamentacao"] = """
            Após 30/08/2023, não é mais permitido o fracionamento do intervalo interjornada,
            devendo ser respeitado integralmente o período de 11 horas.
            """
        
        return analise
    
    def analisar_jornada_controle(self, tem_mais_20_empregados: bool, 
                                 controles_apresentados: bool,
                                 jornada_alegada: str) -> Dict[str, str]:
        """
        Analisa questões de controle de jornada baseado na Súmula 338 TST
        
        Args:
            tem_mais_20_empregados: Se empresa tem mais de 20 empregados
            controles_apresentados: Se controles foram apresentados
            jornada_alegada: Jornada alegada pelo trabalhador
            
        Returns:
            Análise da aplicação da Súmula 338
        """
        
        analise = {
            "obrigacao_controle": "",
            "ônus_prova": "",
            "presuncao": "",
            "fundamentacao": ""
        }
        
        if tem_mais_20_empregados:
            analise["obrigacao_controle"] = "Empresa obrigada a registrar jornada (Súmula 338, I, TST)"
            
            if not controles_apresentados:
                analise["ônus_prova"] = "Ônus da empresa"
                analise["presuncao"] = "Presunção relativa de veracidade da jornada alegada"
                analise["fundamentacao"] = """
                Conforme Súmula 338, I, do TST, é ônus do empregador que conta com mais de 20 empregados 
                o registro da jornada de trabalho. A não apresentação injustificada dos controles gera 
                presunção relativa de veracidade da jornada alegada na inicial.
                """
            else:
                analise["ônus_prova"] = "Trabalhador deve provar inveracidade"
                analise["presuncao"] = "Controles gozam de presunção relativa"
                analise["fundamentacao"] = """
                A empresa cumpriu sua obrigação ao apresentar os controles de jornada, 
                transferindo ao trabalhador o ônus de provar que tais registros não são fidedignos, 
                nos termos do art. 818, I, da CLT.
                """
        else:
            analise["obrigacao_controle"] = "Empresa não obrigada (menos de 20 empregados)"
            analise["ônus_prova"] = "Trabalhador deve provar jornada alegada"
            analise["fundamentacao"] = """
            Por não se enquadrar na obrigatoriedade da Súmula 338 do TST, 
            cabe ao trabalhador o ônus de provar a jornada alegada.
            """
        
        return analise
    
    def analisar_intervalo_interjornada(self, intervalos_registrados: List[str]) -> Dict[str, Any]:
        """
        Analisa violações de intervalo interjornada (11h) - OJ 355 TST
        
        Args:
            intervalos_registrados: Lista de intervalos entre jornadas
            
        Returns:
            Análise de violações e cálculos
        """
        
        violacoes = []
        
        for intervalo in intervalos_registrados:
            # Extrair horas do intervalo (formato esperado: "10h30min")
            match = re.search(r'(\d+)h?(\d*)', intervalo)
            if match:
                horas = int(match.group(1))
                minutos = int(match.group(2)) if match.group(2) else 0
                total_minutos = horas * 60 + minutos
                
                if total_minutos < 660:  # Menos de 11 horas
                    supressao = 660 - total_minutos
                    violacoes.append({
                        "intervalo_registrado": intervalo,
                        "tempo_suprimido_minutos": supressao,
                        "tempo_suprimido_horas": f"{supressao // 60}h{supressao % 60:02d}min"
                    })
        
        return {
            "violacoes_encontradas": len(violacoes),
            "detalhes_violacoes": violacoes,
            "fundamentacao": """
            Conforme art. 66 da CLT, entre duas jornadas deve ser observado intervalo mínimo de 11 horas. 
            A supressão, ainda que parcial, acarreta pagamento integral do período suprimido como horas extras, 
            nos termos da OJ 355 da SDI-1 do TST.
            """,
            "forma_pagamento": "Período suprimido pago integralmente como horas extras"
        }
    
    def obter_jurisprudencia_especifica(self, categoria: str) -> Optional[Jurisprudencia]:
        """
        Obtém jurisprudência específica por categoria
        
        Args:
            categoria: Categoria da jurisprudência buscada
            
        Returns:
            Jurisprudência aplicável ou None
        """
        
        mapeamento = {
            "controle_jornada": "sumula_338",
            "intervalo_interjornada": "oj_355",
            "tempo_espera": "lei_motoristas",
            "motorista_profissional": "lei_motoristas"
        }
        
        chave = mapeamento.get(categoria)
        if chave and chave in self.jurisprudencia_base:
            return self.jurisprudencia_base[chave]
        
        return None
    
    def gerar_fundamentacao_juridica(self, tipo_questao: str, dados_caso: Dict[str, Any]) -> str:
        """
        Gera fundamentação jurídica específica baseada no tipo de questão
        
        Args:
            tipo_questao: Tipo da questão jurídica
            dados_caso: Dados específicos do caso
            
        Returns:
            Fundamentação jurídica formatada
        """
        
        if tipo_questao == "tempo_espera_motorista":
            return self._fundamentacao_tempo_espera(dados_caso)
        elif tipo_questao == "intervalo_interjornada":
            return self._fundamentacao_intervalo_interjornada(dados_caso)
        elif tipo_questao == "controle_jornada":
            return self._fundamentacao_controle_jornada(dados_caso)
        
        return "Fundamentação específica não disponível para este tipo de questão."
    
    def _fundamentacao_tempo_espera(self, dados: Dict[str, Any]) -> str:
        """Gera fundamentação específica para tempo de espera de motorista"""
        
        template = """
        O reclamante trabalhava como motorista profissional empregado no transporte rodoviário de cargas, 
        aplicando-se o regramento da Seção IV-A da CLT (art. 235-A, II).
        
        O art. 235-C, §8º, da CLT estabelecia que o tempo de espera não seria computado como jornada 
        de trabalho nem como horas extraordinárias.
        
        Contudo, o STF na ADI 5322 declarou inconstitucional a expressão "e o tempo de espera", 
        modulando os efeitos da decisão para {data_modulacao}.
        
        {aplicacao_caso}
        
        Ante o exposto, {decisao}.
        """
        
        return template.format(
            data_modulacao=dados.get("data_modulacao", "12/07/2023"),
            aplicacao_caso=dados.get("aplicacao_especifica", ""),
            decisao=dados.get("decisao_final", "")
        )
    
    def _fundamentacao_intervalo_interjornada(self, dados: Dict[str, Any]) -> str:
        """Gera fundamentação para intervalo interjornada"""
        
        template = """
        Conforme art. 66 da CLT, entre duas jornadas deve ser observado intervalo mínimo de 11 horas. 
        A supressão, ainda que parcial, acarreta pagamento integral do período suprimido como horas extras, 
        nos termos da OJ 355 da SDI-1 do TST.
        
        {analise_especifica}
        
        {conclusao}
        """
        
        return template.format(
            analise_especifica=dados.get("analise_intervalos", ""),
            conclusao=dados.get("conclusao", "")
        )
    
    def _fundamentacao_controle_jornada(self, dados: Dict[str, Any]) -> str:
        """Gera fundamentação para controle de jornada"""
        
        template = """
        Conforme Súmula 338, I, do TST, é ônus do empregador que conta com mais de 20 empregados 
        o registro da jornada de trabalho. {situacao_especifica}
        
        {analise_controles}
        
        {conclusao_jornada}
        """
        
        return template.format(
            situacao_especifica=dados.get("situacao_empresa", ""),
            analise_controles=dados.get("analise_controles", ""),
            conclusao_jornada=dados.get("conclusao", "")
        )


