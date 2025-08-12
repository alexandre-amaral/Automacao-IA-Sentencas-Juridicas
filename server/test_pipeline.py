#!/usr/bin/env python3
"""
Script de teste para o pipeline completo
Testa cada etapa: Upload → Whisper → Gemini → RAG → Claude
"""

import requests
import json
import time
from pathlib import Path

# Configurações
BASE_URL = "http://localhost:8000"
TEST_FILES_DIR = Path("../Aut_PDFs inteiros")  # Ajuste conforme necessário

def test_health():
    """Testa se o servidor está funcionando"""
    print("🔍 Testando saúde do servidor...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Servidor funcionando!")
            return True
        else:
            print(f"❌ Servidor retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor. Certifique-se de que está rodando.")
        return False

def test_upload():
    """Testa upload de arquivos"""
    print("\n📤 Testando upload de arquivos...")
    
    # Procurar arquivos de teste
    pdf_files = list(Path("..").glob("**/*.pdf"))[:1]  # Pegar apenas 1 PDF
    mp4_files = list(Path("..").glob("**/*.mp4"))[:1]  # Pegar apenas 1 MP4
    
    if not pdf_files:
        print("⚠️  Nenhum arquivo PDF encontrado para teste")
        return None
    
    files = {}
    
    # Adicionar PDF
    if pdf_files:
        with open(pdf_files[0], 'rb') as f:
            files['processo'] = ('processo.pdf', f.read(), 'application/pdf')
        print(f"📄 Usando PDF: {pdf_files[0].name}")
    
    # Adicionar MP4 se disponível
    if mp4_files:
        with open(mp4_files[0], 'rb') as f:
            files['audiencia'] = ('audiencia.mp4', f.read(), 'video/mp4')
        print(f"🎥 Usando MP4: {mp4_files[0].name}")
    else:
        print("⚠️  Nenhum arquivo MP4 encontrado - testando apenas com PDF")
    
    try:
        response = requests.post(f"{BASE_URL}/upload-caso", files=files)
        
        if response.status_code == 201:
            result = response.json()
            case_id = result['case_id']
            print(f"✅ Upload realizado! Case ID: {case_id}")
            print(f"   Arquivos: {result['files']}")
            return case_id
        else:
            print(f"❌ Erro no upload: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição de upload: {e}")
        return None

def test_step1_transcribe(case_id):
    """Testa ETAPA 1: Transcrição com Whisper"""
    print(f"\n🎤 ETAPA 1: Testando transcrição para case {case_id}...")
    
    try:
        response = requests.post(f"{BASE_URL}/step1-transcribe/{case_id}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Transcrição concluída!")
            print(f"   Status: {result['status']}")
            print(f"   Mensagem: {result['message']}")
            return True
        else:
            print(f"❌ Erro na transcrição: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição de transcrição: {e}")
        return False

def test_step2_process(case_id):
    """Testa ETAPA 2: Processamento com Gemini"""
    print(f"\n🧠 ETAPA 2: Testando processamento Gemini para case {case_id}...")
    
    try:
        response = requests.post(f"{BASE_URL}/step2-process/{case_id}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Processamento Gemini concluído!")
            print(f"   Status: {result['status']}")
            print(f"   Mensagem: {result['message']}")
            return True
        else:
            print(f"❌ Erro no processamento: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição de processamento: {e}")
        return False

def test_step3_generate(case_id):
    """Testa ETAPA 3: Geração de sentença com Claude"""
    print(f"\n⚖️  ETAPA 3: Testando geração de sentença para case {case_id}...")
    
    try:
        response = requests.post(f"{BASE_URL}/step3-generate/{case_id}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sentença gerada com sucesso!")
            print(f"   Status: {result['status']}")
            print(f"   Mensagem: {result['message']}")
            return True
        else:
            print(f"❌ Erro na geração: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição de geração: {e}")
        return False

def test_download(case_id):
    """Testa download da sentença"""
    print(f"\n📥 Testando download da sentença para case {case_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/download/{case_id}/sentenca")
        
        if response.status_code == 200:
            # Salvar sentença
            sentenca_path = Path(f"sentenca_teste_{case_id}.txt")
            sentenca_path.write_text(response.text, encoding='utf-8')
            
            print(f"✅ Sentença baixada com sucesso!")
            print(f"   Arquivo salvo: {sentenca_path}")
            print(f"   Tamanho: {len(response.text)} caracteres")
            
            # Mostrar preview
            preview = response.text[:500] + "..." if len(response.text) > 500 else response.text
            print(f"\n📖 Preview da sentença:")
            print("-" * 50)
            print(preview)
            print("-" * 50)
            
            return True
        else:
            print(f"❌ Erro no download: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição de download: {e}")
        return False

def main():
    """Executa teste completo do pipeline"""
    print("🚀 TESTE COMPLETO DO PIPELINE DE SENTENÇAS")
    print("=" * 50)
    
    # Teste 1: Saúde do servidor
    if not test_health():
        print("\n❌ Teste falhou: Servidor não está funcionando")
        return
    
    # Teste 2: Upload
    case_id = test_upload()
    if not case_id:
        print("\n❌ Teste falhou: Não foi possível fazer upload")
        return
    
    # Dar um tempo para o sistema processar
    print("\n⏳ Aguardando 2 segundos...")
    time.sleep(2)
    
    # Teste 3: Transcrição (ETAPA 1)
    if not test_step1_transcribe(case_id):
        print("\n⚠️  ETAPA 1 falhou, mas continuando...")
    
    # Teste 4: Processamento Gemini (ETAPA 2)
    if not test_step2_process(case_id):
        print("\n❌ Teste falhou: Processamento Gemini falhou")
        return
    
    # Teste 5: Geração Claude (ETAPA 3)
    if not test_step3_generate(case_id):
        print("\n❌ Teste falhou: Geração Claude falhou")
        return
    
    # Teste 6: Download
    if not test_download(case_id):
        print("\n❌ Teste falhou: Download falhou")
        return
    
    print("\n🎉 TESTE COMPLETO CONCLUÍDO COM SUCESSO!")
    print(f"   Case ID testado: {case_id}")
    print("   Todas as etapas funcionaram corretamente")

if __name__ == "__main__":
    main()
