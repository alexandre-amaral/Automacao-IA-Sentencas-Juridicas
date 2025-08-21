#!/usr/bin/env python3
"""
Teste direto do diálogo inteligente sem servidor
Usa arquivos já extraídos para testar rapidamente
"""

import os
import sys
import json
from pathlib import Path

# Adicionar o diretório atual ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_dialogue_direct(case_id: str):
    """Testa o diálogo inteligente diretamente"""
    
    print(f"🧪 TESTANDO DIÁLOGO DIRETO - Case ID: {case_id}")
    print("=" * 60)
    
    try:
        from services.intelligent_dialogue_service import IntelligentDialogueService
        
        # Verificar se os arquivos existem
        case_dir = Path(f"storage/{case_id}")
        processo_path = case_dir / "processo_extraido.txt"
        transcricao_path = case_dir / "audiencia_transcricao.txt"
        
        if not processo_path.exists():
            print(f"❌ Arquivo não encontrado: {processo_path}")
            return False
            
        if not transcricao_path.exists():
            print(f"⚠️  Transcrição não encontrada: {transcricao_path}")
            transcricao_audiencia = None
        else:
            transcricao_audiencia = transcricao_path.read_text(encoding='utf-8')
            print(f"✅ Transcrição carregada: {len(transcricao_audiencia)} caracteres")
        
        # Carregar processo
        texto_processo = processo_path.read_text(encoding='utf-8')
        print(f"✅ Processo carregado: {len(texto_processo)} caracteres")
        
        # Inicializar serviço de diálogo
        print("\n🤖 Iniciando serviço de diálogo inteligente...")
        dialogue_service = IntelligentDialogueService(case_id)
        
        # Executar diálogo completo
        print("🎯 Executando diálogo completo...")
        resultado_completo = dialogue_service.executar_dialogo_completo(
            texto_processo=texto_processo,
            transcricao_audiencia=transcricao_audiencia
        )
        
        # Salvar resultado
        resultado_path = case_dir / "dialogo_resultado_completo.json"
        resultado_path.write_text(
            json.dumps(resultado_completo, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        # Salvar sentença final
        sentenca_final = resultado_completo.get("sentenca_final", "")
        if sentenca_final:
            sentenca_path = case_dir / "sentenca_gerada.txt"
            sentenca_path.write_text(sentenca_final, encoding='utf-8')
            print(f"✅ Sentença gerada: {len(sentenca_final)} caracteres")
            print(f"📝 Salva em: {sentenca_path}")
        else:
            print("❌ Nenhuma sentença foi gerada")
            
        print(f"\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        print(f"📊 Etapas executadas: {len(resultado_completo.get('etapas_executadas', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO no teste: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    
    # Casos disponíveis para teste
    casos_disponiveis = [
        "2af646f2",  # Novo caso de teste
        "d8bdc3ea-3f93-4dc6-bdd5-eaba37d14e20",  # Caso original
    ]
    
    if len(sys.argv) > 1:
        case_id = sys.argv[1]
        print(f"🎯 Testando case específico: {case_id}")
        test_dialogue_direct(case_id)
    else:
        print("📋 Casos disponíveis para teste:")
        for case_id in casos_disponiveis:
            case_dir = Path(f"storage/{case_id}")
            if case_dir.exists():
                processo_exists = (case_dir / "processo_extraido.txt").exists()
                transcricao_exists = (case_dir / "audiencia_transcricao.txt").exists()
                sentenca_exists = (case_dir / "sentenca_gerada.txt").exists()
                
                print(f"\n📁 {case_id}")
                print(f"   📄 Processo: {'✅' if processo_exists else '❌'}")
                print(f"   🎤 Transcrição: {'✅' if transcricao_exists else '❌'}")
                print(f"   ⚖️  Sentença: {'✅' if sentenca_exists else '❌'}")
                
                if processo_exists:
                    print(f"   🚀 Pronto para teste!")
        
        print(f"\n💡 Para testar um caso específico:")
        print(f"   python3 test_dialogue_direct.py {casos_disponiveis[0]}")

if __name__ == "__main__":
    main()

