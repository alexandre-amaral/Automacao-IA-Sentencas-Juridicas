#!/usr/bin/env python3
"""
Sistema de teste rápido para geração de sentenças
Usa dados já processados para testar sem APIs
"""

import json
import sys
from pathlib import Path

def carregar_dados_existentes(case_id: str):
    """Carrega dados de processo já existente"""
    case_dir = Path(f"storage/{case_id}")
    
    # Carregar transcrição
    transcricao_file = case_dir / "audiencia_transcricao.json"
    if transcricao_file.exists():
        with open(transcricao_file, 'r', encoding='utf-8') as f:
            transcricao_data = json.load(f)
            transcricao = transcricao_data.get('texto_completo', '')
    else:
        transcricao = "Transcrição não disponível"
    
    # Carregar processo extraído
    processo_file = case_dir / "processo_extraido.txt"
    if processo_file.exists():
        with open(processo_file, 'r', encoding='utf-8') as f:
            texto_processo = f.read()
    else:
        texto_processo = "Processo não disponível"
    
    return transcricao, texto_processo

def testar_geracoes_rapidas():
    """Testa diferentes abordagens rapidamente"""
    
    # Casos existentes para teste
    cases_disponiveis = [
        "d8bdc3ea-3f93-4dc6-bdd5-eaba37d14e20",
        "153c469a-c954-4cbb-825d-bf0e894f4e5b", 
        "e8b9c0ca-3ad4-42da-8aca-0abb83c059bc"
    ]
    
    print("🧪 SISTEMA DE TESTE RÁPIDO DE SENTENÇAS")
    print("=" * 50)
    
    for case_id in cases_disponiveis:
        case_dir = Path(f"storage/{case_id}")
        if case_dir.exists():
            print(f"\n📁 Case ID: {case_id}")
            
            # Verificar arquivos existentes
            transcricao_exists = (case_dir / "audiencia_transcricao.json").exists()
            processo_exists = (case_dir / "processo_extraido.txt").exists()
            sentenca_exists = (case_dir / "sentenca_gerada.txt").exists()
            
            print(f"   📄 Transcrição: {'✅' if transcricao_exists else '❌'}")
            print(f"   📋 Processo: {'✅' if processo_exists else '❌'}")
            print(f"   ⚖️ Sentença: {'✅' if sentenca_exists else '❌'}")
            
            if sentenca_exists:
                sentenca_file = case_dir / "sentenca_gerada.txt"
                with open(sentenca_file, 'r', encoding='utf-8') as f:
                    sentenca_atual = f.read()
                print(f"   📏 Caracteres atual: {len(sentenca_atual)}")
            
            if transcricao_exists and processo_exists:
                print(f"   🚀 Pronto para teste rápido!")
    
    return cases_disponiveis

def main():
    if len(sys.argv) > 1:
        case_id = sys.argv[1]
        print(f"🎯 Testando case: {case_id}")
        
        transcricao, texto_processo = carregar_dados_existentes(case_id)
        print(f"📊 Transcrição: {len(transcricao)} caracteres")
        print(f"📊 Processo: {len(texto_processo)} caracteres")
        
        # Aqui implementaremos os testes rápidos
        print("🔧 Sistema de teste implementado - pronto para melhorias!")
        
    else:
        testar_geracoes_rapidas()

if __name__ == "__main__":
    main()


