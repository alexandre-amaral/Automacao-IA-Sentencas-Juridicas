#!/usr/bin/env python3
"""
Script manual para gerar sentença do caso atual
Corrige problemas de serialização e variáveis de ambiente
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Verificar se as chaves estão carregadas
print("🔑 Verificando chaves da API...")
openai_key = os.getenv('OPENAI_API_KEY', '')
anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
google_key = os.getenv('GOOGLE_API_KEY', '')

print(f"   OPENAI: {'✅' if openai_key.startswith('sk-') else '❌'} ({openai_key[:15]}...)")
print(f"   ANTHROPIC: {'✅' if anthropic_key.startswith('sk-ant-') else '❌'} ({anthropic_key[:15]}...)")
print(f"   GOOGLE: {'✅' if google_key.startswith('AIza') else '❌'} ({google_key[:15]}...)")

if not all([openai_key, anthropic_key, google_key]):
    print("❌ ERRO: Chaves da API não encontradas!")
    sys.exit(1)

# Adicionar path dos serviços
sys.path.append(str(Path(__file__).parent))

from services.intelligent_dialogue_service import IntelligentDialogueService

async def gerar_sentenca_caso():
    """
    Gera sentença para o caso específico
    """
    
    case_id = '88f72098-98e3-49eb-9cbd-d1782d2f594b'
    case_dir = Path('storage') / case_id
    
    print(f"\n📁 Processando caso: {case_id}")
    print(f"📂 Diretório: {case_dir}")
    
    # Verificar arquivos necessários
    processo_path = case_dir / 'processo_extraido.txt'
    transcricao_path = case_dir / 'audiencia_transcricao.txt'
    
    if not processo_path.exists():
        print(f"❌ ERRO: {processo_path} não encontrado!")
        return False
    
    if not transcricao_path.exists():
        print(f"⚠️ AVISO: {transcricao_path} não encontrado - continuando sem transcrição")
    
    # Carregar dados
    print("\n📄 Carregando dados...")
    texto_processo = processo_path.read_text(encoding='utf-8')
    transcricao_audiencia = None
    
    if transcricao_path.exists():
        transcricao_audiencia = transcricao_path.read_text(encoding='utf-8')
    
    print(f"   📝 Processo: {len(texto_processo):,} caracteres")
    print(f"   🎤 Transcrição: {len(transcricao_audiencia):,} caracteres" if transcricao_audiencia else "   🎤 Transcrição: Não disponível")
    
    # Executar diálogo inteligente
    print("\n🧠 Iniciando diálogo inteligente...")
    try:
        dialogue_service = IntelligentDialogueService(case_id)
        
        print("   ⏳ Executando as 3 etapas do prompt base...")
        resultado = dialogue_service.executar_dialogo_completo(
            texto_processo=texto_processo,
            transcricao_audiencia=transcricao_audiencia
        )
        
        # Salvar resultado completo
        resultado_path = case_dir / 'dialogo_resultado_completo.json'
        with open(resultado_path, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Resultado salvo: {resultado_path}")
        
        # Salvar sentença final
        sentenca_final = resultado.get('sentenca_final', '')
        if sentenca_final:
            sentenca_path = case_dir / 'sentenca_gerada.txt'
            sentenca_path.write_text(sentenca_final, encoding='utf-8')
            
            print(f"\n✅ SENTENÇA GERADA COM SUCESSO!")
            print(f"   📝 Arquivo: {sentenca_path}")
            print(f"   📊 Tamanho: {len(sentenca_final):,} caracteres")
            
            # Mostrar preview
            print(f"\n📖 PREVIEW (primeiros 300 caracteres):")
            print("-" * 50)
            print(sentenca_final[:300] + "..." if len(sentenca_final) > 300 else sentenca_final)
            print("-" * 50)
            
            return True
        else:
            print("❌ ERRO: Sentença final não foi gerada")
            return False
            
    except Exception as e:
        print(f"❌ ERRO durante execução: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Função principal
    """
    
    print("🎯 GERADOR MANUAL DE SENTENÇA")
    print("=" * 50)
    
    # Executar geração
    success = asyncio.run(gerar_sentenca_caso())
    
    if success:
        print("\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        print("📁 Verifique o arquivo 'sentenca_gerada.txt' no diretório do caso")
    else:
        print("\n💥 PROCESSO FALHOU!")
        print("🔧 Verifique os logs de erro acima")

if __name__ == "__main__":
    main()


