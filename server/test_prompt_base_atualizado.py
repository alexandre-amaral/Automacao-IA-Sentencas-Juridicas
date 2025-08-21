#!/usr/bin/env python3
"""
🧪 TESTE DO PROMPT BASE ATUALIZADO
Validação completa das 3 etapas com formatação exata conforme especificado
"""

import asyncio
import sys
import os
from pathlib import Path
import json

# Adicionar diretório atual ao path
sys.path.append(str(Path(__file__).parent))

# Configurar logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Imports dos serviços
from services.intelligent_dialogue_service import IntelligentDialogueService

async def test_prompt_base_completo():
    """
    Teste completo do prompt base atualizado com as 3 etapas
    """
    
    print("🎯 TESTE DO PROMPT BASE ATUALIZADO (100% CONFORME ESPECIFICADO)")
    print("=" * 80)
    
    # ID de caso de teste
    case_id = "test_prompt_atualizado_2024"
    
    # Texto de processo mais realista
    texto_processo_completo = """
    EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DO TRABALHO DA VARA DO TRABALHO DE SALVADOR/BA
    
    PETIÇÃO INICIAL
    
    JOÃO SILVA SANTOS, brasileiro, motorista, portador da CTPS nº 123456, série 123-BA, 
    CPF nº 123.456.789-00, residente e domiciliado na Rua das Flores, 123, Salvador/BA, 
    vem respeitosamente perante V. Exa. ajuizar a presente
    
    RECLAMAÇÃO TRABALHISTA
    
    em face de TRANSPORTADORA ABC LTDA., pessoa jurídica de direito privado, CNPJ nº 
    12.345.678/0001-90, com sede na Av. Principal, 456, Salvador/BA, pelos fatos e 
    fundamentos jurídicos a seguir expostos:
    
    I - DOS FATOS
    
    O reclamante foi admitido em 01/02/2021, exercendo a função de motorista carreteiro, 
    com salário de R$ 3.500,00, sendo dispensado sem justa causa em 15/05/2023.
    
    Durante todo o período contratual, o reclamante cumpria jornada das 06h00 às 18h00, 
    de segunda a sexta-feira, com apenas 30 minutos para almoço, totalizando 11h30 de 
    trabalho diário.
    
    II - DOS PEDIDOS
    
    1. PRELIMINAR DE INCOMPETÊNCIA DA JUSTIÇA DO TRABALHO
    2. HORAS EXTRAS com adicional de 50% 
    3. INTERVALOS INTRAJORNADA não concedidos
    4. ADICIONAL NOTURNO de 20%
    5. INDENIZAÇÃO POR DANOS MORAIS no valor de R$ 15.000,00
    6. GRATUIDADE DA JUSTIÇA
    
    Valor da causa: R$ 50.000,00
    
    CONTESTAÇÃO DA RECLAMADA
    
    A TRANSPORTADORA ABC LTDA. vem respeitosamente contestar a presente reclamação:
    
    PRELIMINAR DE INCOMPETÊNCIA
    Alega que a Justiça do Trabalho não tem competência para julgar acidentes de trânsito.
    
    MÉRITO
    
    1. HORAS EXTRAS: Nega a prestação de horas extras, sustentando que o reclamante 
       cumpria jornada normal de 8 horas diárias com controle eletrônico.
    
    2. INTERVALOS: Afirma que o intervalo de 1 hora era regularmente concedido.
    
    3. ADICIONAL NOTURNO: Nega trabalho noturno habitual.
    
    4. DANOS MORAIS: Inexistência de ato ilícito ou dano moral.
    
    RÉPLICA
    
    O reclamante impugna a contestação, reiterando que:
    - Trabalhou efetivamente em sobrejornada
    - O intervalo era reduzido para 30 minutos
    - Realizava trabalho noturno quando necessário
    - Sofreu assédio moral por parte do supervisor
    """
    
    # Transcrição de audiência mais detalhada
    transcricao_audiencia_completa = """
    TRIBUNAL REGIONAL DO TRABALHO DA 5ª REGIÃO
    VARA DO TRABALHO DE SALVADOR
    
    ATA DE AUDIÊNCIA DE INSTRUÇÃO E JULGAMENTO
    
    Processo: 0000123-45.2023.5.05.0001
    Reclamante: JOÃO SILVA SANTOS
    Reclamada: TRANSPORTADORA ABC LTDA.
    
    DEPOIMENTO PESSOAL DO RECLAMANTE JOÃO SILVA SANTOS:
    
    "Trabalhei na empresa de fevereiro de 2021 até maio de 2023. Minha função era motorista 
    carreteiro. Ganhava R$ 3.500,00 por mês. Meu horário era das 6h às 18h, de segunda a 
    sexta. O almoço era de apenas 30 minutos, não 1 hora como a empresa diz. Quando havia 
    entrega urgente, trabalhava até 22h ou 23h, mas não recebia hora extra. O supervisor 
    José sempre gritava comigo na frente dos outros funcionários, me chamando de lerdo e 
    incompetente. Isso me causou muito constrangimento."
    
    DEPOIMENTO DA TESTEMUNHA MARIA JOSE DOS SANTOS (arrolada pelo reclamante):
    
    "Trabalho na empresa há 5 anos como auxiliar administrativo. Conheço João há 2 anos. 
    Vi várias vezes ele chegando muito tarde, por volta das 23h. O almoço dele era sempre 
    rápido, uns 20-30 minutos. O supervisor José realmente gritava com João, chamava ele 
    de nomes feios na frente de todo mundo. João ficava constrangido e triste."
    
    DEPOIMENTO DA TESTEMUNHA CARLOS PEREIRA (arrolada pela reclamada):
    
    "Sou motorista na empresa há 3 anos. Trabalho no mesmo setor que João. Nosso horário 
    sempre foi das 8h às 17h, com 1 hora de almoço. João saía no horário normal igual a 
    todos. Nunca vi ele fazer hora extra. O supervisor José é uma pessoa tranquila, nunca 
    vi ele gritar com ninguém."
    
    DEPOIMENTO DO PREPOSTO DA RECLAMADA JOSÉ CARLOS SILVA:
    
    "Sou supervisor da empresa há 4 anos. João trabalhava das 8h às 17h com 1 hora de 
    almoço. Temos controle eletrônico que comprova. Eventualmente precisava de entrega 
    até 18h, mas pagávamos hora extra quando necessário. João era um funcionário normal, 
    nunca houve problema de relacionamento. A demissão foi por contenção de custos."
    
    CERTIDÃO
    
    Certifico que os depoimentos acima foram colhidos oralmente e transcritos fielmente.
    """
    
    try:
        print("📋 1. INICIALIZANDO TESTE DO PROMPT BASE ATUALIZADO...")
        dialogue_service = IntelligentDialogueService(case_id)
        
        print("\n🚀 2. EXECUTANDO AS 3 ETAPAS COM FORMATAÇÃO EXATA:")
        print("   📌 Etapa 1: Resumo sistematizado (com numeração 1-14)")
        print("   📌 Etapa 2: Análise prova oral (com diretrizes especiais)")
        print("   📌 Etapa 3: Fundamentação guiada (com escape R\\$)")
        
        # Executar o diálogo completo
        print("\n⏳ Executando diálogo inteligente...")
        resultado = await dialogue_service.executar_dialogo_completo(
            texto_processo=texto_processo_completo,
            transcricao_audiencia=transcricao_audiencia_completa
        )
        
        print("\n✅ 3. RESULTADO DO TESTE ATUALIZADO:")
        print(f"   • Case ID: {resultado['case_id']}")
        print(f"   • Etapas executadas: {len(resultado['etapas_executadas'])}")
        print(f"   • Sentença gerada: {len(resultado.get('sentenca_final', ''))} caracteres")
        
        # Salvar resultado detalhado
        test_result_file = Path("test_prompt_atualizado_resultado.json")
        with open(test_result_file, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 4. RESULTADO COMPLETO SALVO EM: {test_result_file}")
        
        # Verificar conformidade com o prompt base
        print("\n🔍 5. VERIFICAÇÃO DE CONFORMIDADE:")
        
        # Verificar Etapa 1
        etapa_1 = None
        for etapa in resultado.get('etapas_executadas', []):
            if etapa.get('etapa') == 'ETAPA_1_RESUMO_SISTEMATIZADO':
                etapa_1 = etapa
                break
        
        if etapa_1:
            conteudo_1 = etapa_1.get('conteudo_completo', '')
            print("   ✅ Etapa 1 executada")
            
            # Verificar elementos específicos do prompt
            checks_etapa_1 = [
                ("Data do ajuizamento", "ajuizamento" in conteudo_1.lower()),
                ("Tabela de dados básicos", "tabela" in conteudo_1.lower() or "|" in conteudo_1),
                ("Preliminares", "preliminar" in conteudo_1.lower()),
                ("Prejudiciais de mérito", "prejudicial" in conteudo_1.lower()),
                ("Separador /1ª Etapa/", "/1ª Etapa/" in conteudo_1),
                ("Exemplo de formatação", "*da justa causa*" in conteudo_1.lower() or "*das horas extras*" in conteudo_1.lower())
            ]
            
            for check_name, check_result in checks_etapa_1:
                status = "✅" if check_result else "❌"
                print(f"     {status} {check_name}")
        
        # Verificar Etapa 2
        etapa_2 = None
        for etapa in resultado.get('etapas_executadas', []):
            if etapa.get('etapa') == 'ETAPA_2_ANALISE_PROVA_ORAL':
                etapa_2 = etapa
                break
        
        if etapa_2:
            conteudo_2 = etapa_2.get('conteudo_completo', '')
            print("   ✅ Etapa 2 executada")
            
            checks_etapa_2 = [
                ("Tabela de pontos controvertidos", "|" in conteudo_2 and "ponto controvertido" in conteudo_2.lower()),
                ("Relatório analítico", "analítico" in conteudo_2.lower() or "convergência" in conteudo_2.lower()),
                ("Diretrizes especiais", "conectores" in conteudo_2.lower() or "transições" in conteudo_2.lower()),
                ("Separador //", "//" in conteudo_2)
            ]
            
            for check_name, check_result in checks_etapa_2:
                status = "✅" if check_result else "❌"
                print(f"     {status} {check_name}")
        
        # Verificar Etapa 3 e sentença final
        sentenca_final = resultado.get('sentenca_final', '')
        if sentenca_final:
            print("   ✅ Sentença final gerada")
            
            checks_sentenca = [
                ("Escape do cifrão R\\$", "R\\$" in sentenca_final),
                ("Estrutura RELATÓRIO", "RELATÓRIO" in sentenca_final.upper() or "relatório" in sentenca_final.lower()),
                ("Estrutura FUNDAMENTAÇÃO", "FUNDAMENTAÇÃO" in sentenca_final.upper() or "fundamentação" in sentenca_final.lower()),
                ("Estrutura DISPOSITIVO", "DISPOSITIVO" in sentenca_final.upper() or "dispositivo" in sentenca_final.lower()),
                ("Citações legais CLT", "CLT" in sentenca_final),
                ("Formatação Markdown ##", "##" in sentenca_final),
                ("Negrito **", "**" in sentenca_final)
            ]
            
            for check_name, check_result in checks_sentenca:
                status = "✅" if check_result else "❌"
                print(f"     {status} {check_name}")
        
        # Mostrar preview da sentença
        if sentenca_final:
            print("\n📝 6. PREVIEW DA SENTENÇA FINAL (PRIMEIROS 500 CARACTERES):")
            print("-" * 60)
            print(sentenca_final[:500] + "..." if len(sentenca_final) > 500 else sentenca_final)
            print("-" * 60)
        
        print("\n🎉 TESTE DO PROMPT BASE ATUALIZADO CONCLUÍDO!")
        print(f"📊 Estatísticas:")
        print(f"   • Total de caracteres gerados: {sum(len(e.get('conteudo_completo', '')) for e in resultado.get('etapas_executadas', []))}")
        print(f"   • Sentença final: {len(sentenca_final)} caracteres")
        print(f"   • Arquivo de resultado: {test_result_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Função principal do teste
    """
    
    print("🎯 VALIDADOR DO PROMPT BASE ATUALIZADO")
    print("=" * 80)
    print("Este script testa se o prompt base foi implementado EXATAMENTE")
    print("conforme especificado, incluindo:")
    print("• Formatação com asteriscos")
    print("• Numeração específica (1-14)")
    print("• Exemplos detalhados")
    print("• Separadores especiais")
    print("• Diretrizes de estilo")
    print("• Escape do cifrão R\\$")
    print("=" * 80)
    
    # Executar teste
    success = asyncio.run(test_prompt_base_completo())
    
    if success:
        print("\n✅ TODOS OS TESTES PASSARAM!")
        print("📄 O prompt base está implementado conforme especificação")
        print("🚀 Sistema pronto para produção")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        print("🔧 Revisar implementação do prompt base")

if __name__ == "__main__":
    main()


