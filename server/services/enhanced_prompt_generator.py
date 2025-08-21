"""
Gerador de Prompts Aprimorados para Claude
Cria prompts estruturados com análise jurisprudencial e probatória detalhada
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

class EnhancedPromptGenerator:
    """Gerador de prompts aprimorados para Claude"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def gerar_prompt_fundamentacao_completa(self, 
                                          dados_processo: Dict[str, Any],
                                          analise_jurisprudencia: Dict[str, Any],
                                          analise_provas: Dict[str, Any],
                                          contexto_rag: str) -> str:
        """
        Gera prompt completo para fundamentação detalhada da sentença
        
        Args:
            dados_processo: Dados estruturados do processo
            analise_jurisprudencia: Análise jurisprudencial específica
            analise_provas: Análise de provas e contradições
            contexto_rag: Contexto recuperado do RAG
            
        Returns:
            Prompt estruturado para Claude
        """
        
        prompt_base = """
        Você é uma JUÍZA DO TRABALHO especializada em direito trabalhista brasileiro, com vasta experiência em redação de sentenças técnicas e fundamentadas.

        TAREFA: Redigir uma SENTENÇA TRABALHISTA COMPLETA seguindo rigorosamente o estilo jurisprudencial brasileiro.

        INSTRUÇÕES CRÍTICAS:
        1. Use EXCLUSIVAMENTE as informações fornecidas - NÃO invente fatos
        2. Mantenha linguagem jurídica formal e técnica
        3. Cite jurisprudência específica fornecida
        4. Analise CADA PEDIDO individualmente
        5. Fundamente TODAS as decisões com base legal sólida
        6. Identifique e trate contradições probatórias
        7. Aplique ônus da prova corretamente

        ESTRUTURA OBRIGATÓRIA:
        """
        
        estrutura_sentenca = """
        SENTENÇA

        RELATÓRIO
        [Identificação das partes, resumo da inicial, contestação e instrução]

        FUNDAMENTAÇÃO
        [Para CADA pedido, seguir esta estrutura:]

        PRELIMINARES (se aplicável)
        - DA JUSTIÇA GRATUITA
        - DA ILEGITIMIDADE/INCOMPETÊNCIA

        MÉRITO
        - DO [NOME DO PEDIDO]
        [Para cada pedido:]
        1. Alegações das partes
        2. Análise da prova (documental e oral)
        3. Aplicação da jurisprudência específica
        4. Ônus da prova e seu cumprimento
        5. Fundamentação legal detalhada
        6. Conclusão motivada

        DISPOSITIVO
        [Decisão clara e objetiva para cada pedido]

        """
        
        secao_dados = f"""
        DADOS DO PROCESSO:
        {self._formatar_dados_processo(dados_processo)}
        """
        
        secao_jurisprudencia = f"""
        JURISPRUDÊNCIA APLICÁVEL:
        {self._formatar_analise_jurisprudencia(analise_jurisprudencia)}
        """
        
        secao_provas = f"""
        ANÁLISE PROBATÓRIA:
        {self._formatar_analise_provas(analise_provas)}
        """
        
        secao_contexto = f"""
        CONTEXTO JURÍDICO ESPECÍFICO:
        {contexto_rag}
        """
        
        orientacoes_especificas = """
        ORIENTAÇÕES ESPECÍFICAS PARA REDAÇÃO:

        1. RELATÓRIO:
        - Identifique partes com qualificação completa
        - Resuma petição inicial com TODOS os pedidos
        - Mencione contestação e argumentos defensivos
        - Relate instrução probatória (testemunhas, documentos)

        2. FUNDAMENTAÇÃO:
        - Analise CADA pedido em seção específica
        - Use títulos em CAIXA ALTA para cada tema
        - Cite artigos de lei específicos (CLT, CF/88)
        - Mencione súmulas e orientações jurisprudenciais
        - Analise contradições probatórias quando existirem
        - Aplique ônus da prova corretamente
        - Fundamente decisões com base legal sólida

        3. DISPOSITIVO:
        - Decisão clara para cada pedido
        - Valores quando determinados
        - Honorários advocatícios
        - Custas processuais

        4. ESTILO ESPECÍFICO:
        - Use "Ante o exposto" para conclusões
        - "Julgar PROCEDENTE/IMPROCEDENTE"
        - "Condenar a reclamada" quando procedente
        - Citações específicas: "nos termos do art. X da CLT"
        - "Conforme entendimento consolidado na Súmula X do TST"
        """
        
        return prompt_base + estrutura_sentenca + secao_dados + secao_jurisprudencia + secao_provas + secao_contexto + orientacoes_especificas
    
    def _formatar_dados_processo(self, dados: Dict[str, Any]) -> str:
        """Formata dados do processo para o prompt"""
        
        formatacao = f"""
        Número: {dados.get('numero_processo', 'Não informado')}
        
        PARTES:
        """
        
        partes = dados.get('partes', [])
        for parte in partes:
            formatacao += f"- {parte.get('nome', '')} ({parte.get('tipo', '')})\n"
        
        formatacao += "\nPEDIDOS FORMULADOS:\n"
        pedidos = dados.get('pedidos', [])
        for i, pedido in enumerate(pedidos, 1):
            formatacao += f"{i}. {pedido.get('descricao', '')} - Categoria: {pedido.get('categoria', '')}\n"
            if pedido.get('valor_estimado'):
                formatacao += f"   Valor estimado: {pedido.get('valor_estimado')}\n"
        
        formatacao += f"\nPERÍODO CONTRATUAL: {dados.get('periodo_contratual', 'Não informado')}\n"
        formatacao += f"VALOR DA CAUSA: {dados.get('valor_causa', 'Não informado')}\n"
        formatacao += f"FUNÇÃO: {dados.get('funcao_cargo', 'Não informada')}\n"
        
        if dados.get('testemunhas'):
            formatacao += "\nTESTEMUNHAS OUVIDAS:\n"
            for testemunha in dados.get('testemunhas', []):
                formatacao += f"- {testemunha.get('nome', '')} (convite: {testemunha.get('parte_convite', '')})\n"
                formatacao += f"  Resumo: {testemunha.get('resumo_depoimento', '')}\n"
        
        return formatacao
    
    def _formatar_analise_jurisprudencia(self, analise: Dict[str, Any]) -> str:
        """Formata análise jurisprudencial para o prompt"""
        
        if not analise:
            return "Nenhuma análise jurisprudencial específica disponível."
        
        formatacao = ""
        
        # Análise da Lei 13.103/2015 se aplicável
        if 'lei_motoristas' in analise:
            lei_data = analise['lei_motoristas']
            formatacao += f"""
            LEI 13.103/2015 (MOTORISTAS):
            
            Tempo de Espera:
            - Aplicável: {'Sim' if lei_data.get('tempo_espera', {}).get('aplicavel') else 'Não'}
            - Fundamentação: {lei_data.get('tempo_espera', {}).get('fundamentacao', '')}
            - Efeitos: {lei_data.get('tempo_espera', {}).get('efeitos', '')}
            
            Fracionamento de Intervalo:
            - Aplicável: {'Sim' if lei_data.get('fracionamento_intervalo', {}).get('aplicavel') else 'Não'}
            - Fundamentação: {lei_data.get('fracionamento_intervalo', {}).get('fundamentacao', '')}
            """
        
        # Análise de controle de jornada
        if 'controle_jornada' in analise:
            controle = analise['controle_jornada']
            formatacao += f"""
            CONTROLE DE JORNADA (SÚMULA 338 TST):
            - Obrigação: {controle.get('obrigacao_controle', '')}
            - Ônus da prova: {controle.get('ônus_prova', '')}
            - Presunção: {controle.get('presuncao', '')}
            - Fundamentação: {controle.get('fundamentacao', '')}
            """
        
        # Análise de intervalos
        if 'intervalo_interjornada' in analise:
            intervalo = analise['intervalo_interjornada']
            formatacao += f"""
            INTERVALO INTERJORNADA (OJ 355 TST):
            - Violações encontradas: {intervalo.get('violacoes_encontradas', 0)}
            - Fundamentação: {intervalo.get('fundamentacao', '')}
            - Forma de pagamento: {intervalo.get('forma_pagamento', '')}
            """
        
        return formatacao
    
    def _formatar_analise_provas(self, analise: Dict[str, Any]) -> str:
        """Formata análise de provas para o prompt"""
        
        if not analise:
            return "Nenhuma análise probatória específica disponível."
        
        formatacao = ""
        
        # Análise de testemunhas
        if 'analise_testemunhas' in analise:
            testemunhas = analise['analise_testemunhas']
            formatacao += f"""
            ANÁLISE DE TESTEMUNHAS:
            {testemunhas.get('sintese_probatoria', '')}
            
            Recomendação: {testemunhas.get('recomendacao_judicial', '')}
            """
            
            if testemunhas.get('contradicoes_encontradas'):
                formatacao += "\nCONTRADIÇÕES PROBATÓRIAS:\n"
                for contradicao in testemunhas['contradicoes_encontradas']:
                    formatacao += f"- {contradicao.get('descricao', '')}\n"
                    formatacao += f"  Impacto: {contradicao.get('impacto_decisao', '')}\n"
        
        # Análise de ônus da prova
        if 'onus_proba' in analise:
            onus = analise['onus_proba']
            formatacao += f"""
            ÔNUS DA PROVA:
            - Regra aplicável: {onus.get('regra_aplicavel', '')}
            - Parte onerada: {onus.get('parte_onerada', '')}
            - Ônus cumprido: {onus.get('onus_cumprido', '')}
            - Consequência: {onus.get('consequencia', '')}
            """
        
        return formatacao
    
    def gerar_prompt_pedido_especifico(self, 
                                     tipo_pedido: str, 
                                     dados_especificos: Dict[str, Any]) -> str:
        """
        Gera prompt específico para análise de pedido individual
        
        Args:
            tipo_pedido: Tipo do pedido (horas_extras, dano_moral, etc.)
            dados_especificos: Dados específicos do pedido
            
        Returns:
            Prompt específico para o pedido
        """
        
        prompts_especificos = {
            "horas_extras": self._prompt_horas_extras,
            "intervalo_intrajornada": self._prompt_intervalo_intrajornada,
            "tempo_espera": self._prompt_tempo_espera,
            "dano_moral": self._prompt_dano_moral,
            "plr_ppr": self._prompt_plr,
            "diferenca_diarias": self._prompt_diarias
        }
        
        gerador = prompts_especificos.get(tipo_pedido, self._prompt_generico)
        return gerador(dados_especificos)
    
    def _prompt_horas_extras(self, dados: Dict[str, Any]) -> str:
        """Prompt específico para horas extras"""
        
        return f"""
        ANÁLISE DE HORAS EXTRAS:
        
        Jornada alegada: {dados.get('jornada_alegada', '')}
        Controles apresentados: {dados.get('controles_apresentados', '')}
        Prova testemunhal: {dados.get('prova_testemunhal', '')}
        
        PONTOS A ANALISAR:
        1. Ônus da prova (Súmula 338 TST se aplicável)
        2. Validade dos controles de ponto
        3. Credibilidade da prova testemunhal
        4. Jornada efetivamente laborada
        5. Cálculo de horas extras (50% dias úteis, 100% domingos/feriados)
        6. Reflexos em DSR, férias, 13º salário, aviso prévio
        
        Base legal: Arts. 7º, XVI, CF/88; 59, 60, 61 CLT; Súmula 338 TST
        """
    
    def _prompt_tempo_espera(self, dados: Dict[str, Any]) -> str:
        """Prompt específico para tempo de espera"""
        
        return f"""
        ANÁLISE DE TEMPO DE ESPERA:
        
        Função: {dados.get('funcao', '')}
        Período contratual: {dados.get('periodo_contratual', '')}
        Tempo alegado: {dados.get('tempo_espera_alegado', '')}
        
        PONTOS ESPECÍFICOS:
        1. Enquadramento na Lei 13.103/2015
        2. Aplicação do art. 235-C, §8º CLT
        3. Efeitos da ADI 5322 STF
        4. Modulação temporal (12/07/2023)
        5. Natureza indenizatória vs. tempo à disposição
        
        Decisão STF: Declaração de inconstitucionalidade com modulação temporal
        Data crítica: 12/07/2023 para tempo de espera
        """
    
    def _prompt_dano_moral(self, dados: Dict[str, Any]) -> str:
        """Prompt específico para dano moral"""
        
        return f"""
        ANÁLISE DE DANO MORAL:
        
        Fatos alegados: {dados.get('fatos_alegados', '')}
        Prova produzida: {dados.get('prova_produzida', '')}
        
        ELEMENTOS ESSENCIAIS:
        1. Ato ilícito praticado pelo empregador
        2. Dano efetivamente sofrido
        3. Nexo de causalidade
        4. Prova robusta dos fatos alegados
        
        Ônus da prova: Autor (art. 818, I, CLT c/c art. 373, I, CPC)
        Base legal: Arts. 186, 927 CC; 5º, X, CF/88
        """
    
    def _prompt_plr(self, dados: Dict[str, Any]) -> str:
        """Prompt específico para PLR/PPR"""
        
        return f"""
        ANÁLISE DE PLR/PPR:
        
        Período laborado: {dados.get('periodo_laborado', '')}
        Data da dispensa: {dados.get('data_dispensa', '')}
        Pagamentos comprovados: {dados.get('pagamentos_comprovados', '')}
        
        PONTOS A VERIFICAR:
        1. Período de apuração dos resultados
        2. Proporcionalidade ao tempo laborado
        3. Direito independente de estar na empresa no pagamento
        4. Normas coletivas aplicáveis
        
        Princípio: Direito vinculado ao período laborado
        """
    
    def _prompt_diarias(self, dados: Dict[str, Any]) -> str:
        """Prompt específico para diferenças de diárias"""
        
        return f"""
        ANÁLISE DE DIFERENÇAS DE DIÁRIAS:
        
        Valor pago: {dados.get('valor_pago', '')}
        Valor previsto em norma coletiva: {dados.get('valor_norma_coletiva', '')}
        Número de viagens: {dados.get('numero_viagens', '')}
        
        PONTOS A ANALISAR:
        1. Norma coletiva aplicável
        2. Valor por diária estabelecido
        3. Número efetivo de viagens/dias
        4. Diferenças apuradas
        5. Finalidade das diárias (alimentação, hospedagem)
        
        Base: Normas coletivas da categoria profissional
        """
    
    def _prompt_generico(self, dados: Dict[str, Any]) -> str:
        """Prompt genérico para outros pedidos"""
        
        return f"""
        ANÁLISE DO PEDIDO:
        
        Dados específicos: {dados}
        
        ESTRUTURA DE ANÁLISE:
        1. Alegações das partes
        2. Prova produzida
        3. Ônus probatório
        4. Base legal aplicável
        5. Jurisprudência pertinente
        6. Conclusão fundamentada
        """


