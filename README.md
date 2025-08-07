# Sistema de Automação de Sentenças Judiciais com IA

## 📋 Visão Geral

Sistema de Inteligência Artificial para automatizar a redação de minutas de sentenças judiciais, replicando o estilo de escrita e raciocínio jurídico de uma juíza de referência.

## 🏗️ Arquitetura

- **Frontend**: Next.js + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python
- **IA**: OpenAI Whisper + Google Gemini + Anthropic Claude
- **RAG**: ChromaDB + Sentence-Transformers
- **Web Scraping**: Selenium + BeautifulSoup

## 📁 Estrutura do Projeto

```
├── client/          # Frontend Next.js
├── server/          # Backend FastAPI
├── assets/          # Recursos e documentos
├── docs/           # Documentação
└── README.md
```

## 🚀 Como Executar

### Pré-requisitos

- Node.js 18+
- Python 3.11+
- Redis (para processamento assíncrono)

### Frontend (Next.js)

```bash
cd client
npm install
npm run dev
```

Acesse: http://localhost:3000

### Backend (FastAPI)

```bash
cd server
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
```

Acesse: http://localhost:8000

## ⚙️ Configuração

1. Copie `server/env.example` para `server/.env`
2. Configure as chaves de API necessárias:
   - OpenAI API Key
   - Anthropic API Key  
   - Google API Key

## 🔧 Desenvolvimento

### Status Atual: Configuração Inicial ✅

- [x] Estrutura do projeto
- [x] Setup Next.js + TypeScript
- [x] Setup FastAPI + Python
- [x] Configuração de ambiente
- [ ] Interface de upload
- [ ] Processamento de documentos
- [ ] Integração com APIs de IA
- [ ] Sistema RAG
- [ ] Web scraping
- [ ] Geração de sentenças

## 📝 Próximos Passos

1. Implementar interface de upload
2. Configurar parsing de documentos
3. Integrar APIs de IA
4. Desenvolver sistema RAG
5. Implementar geração de sentenças

## 🤝 Contribuição

Este projeto está em desenvolvimento ativo. Consulte as issues para tarefas pendentes.

## 📄 Licença

[Inserir licença apropriada]