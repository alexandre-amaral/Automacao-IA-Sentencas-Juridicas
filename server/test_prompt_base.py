#!/usr/bin/env python3
"""
Script de teste direto do prompt base estruturado
Demonstra onde está implementado e como testar
"""

import asyncio
import sys
import os
from pathlib import Path

# Adicionar diretório atual ao path
sys.path.append(str(Path(__file__).parent))

# Imports dos serviços
from services.intelligent_dialogue_service import IntelligentDialogueService
import json

async def test_prompt_base():
    """
    Teste direto do prompt base estruturado
    """
    
    print("🧪 TESTE DO PROMPT BASE ESTRUTURADO")
    print("=" * 60)
    
    # ID de caso de teste
    case_id = "test_prompt_base_2024"
    
    # Texto de teste do processo (simulado)
    texto_processo_teste = """
    TRIBUNAL REGIONAL DO TRABALHO
    
    PETIÇÃO INICIAL
    
    João Silva, motorista, vem respeitosamente perante V. Exa. requerer:
    
    1. Horas extras com adicional de 50%
    2. Adicional noturno de 20%
    3. Intervalos intrajornada não concedidos
    4. Indenização por danos morais no valor de R$ 10.000,00
    
    CONTESTAÇÃO
    
    A empresa ABC Transportes contesta alegando:
    
    1. Inexistência de horas extras extraordinárias
    2. Correto pagamento do adicional noturno
    3. Concessão regular dos intervalos
    4. Ausência de dano moral
    
    DOCUMENTOS:
    - Cartão de ponto eletrônico
    - Recibos de pagamento
    - Contratos de trabalho
    """
    
    # Transcrição da audiência (simulada)
    transcricao_audiencia_teste = """
    AUDIÊNCIA DE INSTRUÇÃO
    
    DEPOIMENTO DO RECLAMANTE João Silva:
    "Trabalhava das 6h às 18h, com 1 hora de almoço. Sempre fazia horas extras até 22h, 
    mas não recebia o adicional correto. O intervalo de almoço às vezes era reduzido para 30 minutos."
    
    DEPOIMENTO DA TESTEMUNHA Maria Santos:
    "Confirmou que João trabalhava além do horário normal e que o intervalo nem sempre era respeitado."
    
    DEPOIMENTO DO PREPOSTO DA EMPRESA:
    "A empresa sempre pagou todas as horas extras conforme a lei. O controle de ponto estava funcionando corretamente."
    """
    
    try:
        print("📋 1. INICIALIZANDO DIÁLOGO INTELIGENTE...")
        dialogue_service = IntelligentDialogueService(case_id)
        
        print("🚀 2. EXECUTANDO AS 3 ETAPAS DO PROMPT BASE...")
        print("   • Etapa 1: Resumo sistematizado")
        print("   • Etapa 2: Análise da prova oral") 
        print("   • Etapa 3: Fundamentação guiada")
        
        # Executar o diálogo completo
        resultado = dialogue_service.executar_dialogo_completo(
            texto_processo=texto_processo_teste,
            transcricao_audiencia=transcricao_audiencia_teste
        )
        
        print("\n✅ 3. RESULTADO DO TESTE:")
        print(f"   • Case ID: {resultado['case_id']}")
        print(f"   • Etapas executadas: {len(resultado['etapas_executadas'])}")
        print(f"   • Sentença gerada: {len(resultado.get('sentenca_final', ''))} caracteres")
        
        # Salvar resultado do teste
        test_result_file = Path("test_prompt_base_resultado.json")
        with open(test_result_file, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 4. RESULTADO SALVO EM: {test_result_file}")
        
        # Mostrar trecho da sentença
        sentenca = resultado.get('sentenca_final', '')
        if sentenca:
            print("\n📝 5. PREVIEW DA SENTENÇA GERADA:")
            print("-" * 40)
            print(sentenca[:500] + "..." if len(sentenca) > 500 else sentenca)
            print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {str(e)}")
        return False

def show_prompt_locations():
    """
    Mostra onde estão localizados os prompts no código
    """
    
    print("\n📍 LOCALIZAÇÃO DOS PROMPTS BASE:")
    print("=" * 60)
    
    locations = [
        {
            "arquivo": "server/services/intelligent_dialogue_service.py",
            "linhas": "107-196",
            "conteudo": "ETAPA 1: Resumo sistematizado com tabelas",
            "detalhes": "Prompt completo da Etapa 1 com dados básicos, preliminares, prejudiciais e mérito"
        },
        {
            "arquivo": "server/services/intelligent_dialogue_service.py", 
            "linhas": "251-292",
            "conteudo": "ETAPA 2: Análise da prova oral",
            "detalhes": "Prompt para análise de depoimentos com tabela de pontos controvertidos"
        },
        {
            "arquivo": "server/services/intelligent_dialogue_service.py",
            "linhas": "357-396", 
            "conteudo": "ETAPA 3: Fundamentação guiada",
            "detalhes": "Prompt para geração da sentença final com citações legais e estrutura"
        },
        {
            "arquivo": "server/main.py",
            "linhas": "273-328",
            "conteudo": "Pipeline automático",
            "detalhes": "Integração que chama o IntelligentDialogueService automaticamente"
        }
    ]
    
    for i, loc in enumerate(locations, 1):
        print(f"\n{i}. {loc['conteudo']}")
        print(f"   📁 Arquivo: {loc['arquivo']}")
        print(f"   📍 Linhas: {loc['linhas']}")
        print(f"   ℹ️  Detalhes: {loc['detalhes']}")

def show_test_instructions():
    """
    Mostra instruções de como testar o sistema
    """
    
    print("\n🧪 COMO TESTAR O SISTEMA:")
    print("=" * 60)
    
    tests = [
        {
            "metodo": "1. Teste via Frontend",
            "comando": "Acesse http://localhost:3000",
            "descricao": "Faça upload de PDF (processo) + MP4 (audiência) e veja o pipeline automático"
        },
        {
            "metodo": "2. Teste via Script",
            "comando": "python test_prompt_base.py",
            "descricao": "Execute este script para testar diretamente o prompt base"
        },
        {
            "metodo": "3. Teste Manual via API",
            "comando": "curl -X POST http://localhost:8000/upload-caso",
            "descricao": "Use a API diretamente com arquivos via FormData"
        },
        {
            "metodo": "4. Teste de Caso Anterior",
            "comando": "ls storage/58f6f2e9-337a-428a-88a1-f85c2ecd1305/",
            "descricao": "Veja arquivos do caso já processado com sucesso"
        }
    ]
    
    for test in tests:
        print(f"\n{test['metodo']}")
        print(f"   💻 Comando: {test['comando']}")
        print(f"   📝 Descrição: {test['descricao']}")

if __name__ == "__main__":
    print("🎯 TESTE E DEMONSTRAÇÃO DO PROMPT BASE")
    print("=" * 60)
    
    # Mostrar localizações
    show_prompt_locations()
    
    # Mostrar instruções de teste
    show_test_instructions()
    
    # Perguntar se quer executar o teste
    print("\n" + "=" * 60)
    response = input("🚀 Deseja executar o teste do prompt base agora? (s/n): ").lower().strip()
    
    if response in ['s', 'sim', 'y', 'yes']:
        print("\n🏃‍♂️ EXECUTANDO TESTE...")
        success = asyncio.run(test_prompt_base())
        
        if success:
            print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
            print("📄 Verifique o arquivo 'test_prompt_base_resultado.json' para detalhes completos")
        else:
            print("\n❌ TESTE FALHOU - Verifique os logs acima")
    else:
        print("\n👍 Ok! Execute 'python test_prompt_base.py' quando quiser testar")


