#!/usr/bin/env python3
"""
Analisador de padrões de sentenças reais para melhorar o sistema
"""

def analisar_diferencias():
    """Analisa diferenças entre sentença gerada e sentença real"""
    
    # SENTENÇA GERADA ATUAL (93 linhas, 5576 caracteres)
    caracteristicas_atual = {
        "linhas": 93,
        "caracteres": 5576,
        "estrutura": [
            "RELATÓRIO (curto)",
            "PRELIMINARES (básicas)",
            "MÉRITO (superficial)",
            "DISPOSITIVO (simples)"
        ],
        "problemas": [
            "Análise probatória inexistente",
            "Sem análise detalhada de depoimentos",
            "Sem contradições entre testemunhas", 
            "Fundamentação jurídica rasa",
            "Ausência de citações específicas de TST",
            "Sem análise de Lei 13.103/2015 e ADI 5322",
            "Decisões sem fundamentação detalhada"
        ]
    }
    
    # SENTENÇA REAL ESPERADA (características)
    caracteristicas_esperada = {
        "linhas": "200+",
        "caracteres": "15000+", 
        "estrutura": [
            "RELATÓRIO detalhado com IDs específicos",
            "FUNDAMENTAÇÃO com análise jurisprudencial",
            "ANÁLISE PROBATÓRIA minuciosa",
            "CONTRADIÇÕES entre testemunhas",
            "CITAÇÕES específicas (TST, STF, ADI)",
            "CÁLCULOS detalhados",
            "DISPOSITIVO completo"
        ],
        "elementos_criticos": [
            "Análise de cada depoimento individualmente",
            "Identificação de contradições específicas", 
            "Aplicação de Lei 13.103/2015 com modulação STF",
            "Súmulas e OJs específicas do TST",
            "Fundamentação por pedido com 'Analisa-se.'",
            "Critérios de cálculo detalhados",
            "Reflexos em FGTS, férias, 13º",
            "Honorários com percentuais específicos"
        ]
    }
    
    print("🔍 ANÁLISE DE PADRÕES - SENTENÇAS REAIS vs GERADAS")
    print("=" * 60)
    
    print("\n📊 DIFERENÇAS CRÍTICAS:")
    print(f"Caracteres: {caracteristicas_atual['caracteres']} → {caracteristicas_esperada['caracteres']}")
    print(f"Profundidade: Superficial → Análise detalhada")
    print(f"Jurisprudência: Básica → TST/STF específicos")
    print(f"Provas: Ausente → Análise minuciosa")
    
    return caracteristicas_atual, caracteristicas_esperada

def criar_template_sentenca_robusta():
    """Cria template para sentença robusta baseada nos padrões reais"""
    
    template = """
ESTRUTURA OBRIGATÓRIA PARA SENTENÇA DETALHADA:

1. RELATÓRIO (300-500 palavras)
   - Qualificação completa das partes com IDs
   - Todos os pedidos específicos
   - Valor da causa correto
   - Menção a contestação com ID
   - Réplica com ID
   - Audiência com Ata ID
   - Prova emprestada se houver
   - Razões finais remissivas

2. FUNDAMENTAÇÃO
   A. LIMITAÇÃO DOS VALORES (IN 41/2018 TST)
   B. PROVIDÊNCIA SANEADORA (Lei 13.467/2017)
   C. CCT APLICÁVEL (análise detalhada)
   D. PARA CADA PEDIDO:
      - Título específico
      - Alegações do autor
      - Defesa da ré  
      - "Analisa-se."
      - Análise probatória DETALHADA
      - Contradições específicas entre testemunhas
      - Fundamentação jurídica com Súmulas/OJs
      - Conclusão fundamentada
   E. SEÇÕES FINAIS (FGTS, Honorários, etc.)

3. DISPOSITIVO
   - Fórmula específica
   - Lista de pedidos deferidos/indeferidos
   - Honorários com percentuais
   - Custas calculadas
   - "Intimem-se as partes. Nada mais."

ELEMENTOS CRÍTICOS:
- Mínimo 15.000 caracteres
- Análise individual de cada testemunha
- Citações específicas de TST/STF
- Lei 13.103/2015 com modulação ADI 5322
- Critérios de cálculo detalhados
- Contradições probatórias explícitas
"""
    
    return template

if __name__ == "__main__":
    analisar_diferencias()
    template = criar_template_sentenca_robusta()
    print("\n📋 TEMPLATE PARA IMPLEMENTAÇÃO:")
    print(template)


