"""
Serviço de transcrição de áudio usando OpenAI Whisper
Transcreve gravações de audiências (MP4) para texto
"""

import openai
import os
from pathlib import Path
from typing import Dict, Optional, Any
import json
import logging
from dataclasses import dataclass
import time

@dataclass
class TranscricaoAudiencia:
    """Resultado da transcrição de audiência"""
    texto_completo: str
    duracao_segundos: Optional[float]
    idioma_detectado: Optional[str]
    confianca: Optional[float]
    segmentos: Optional[list]
    metadados: Dict[str, Any]

class WhisperService:
    """Serviço para transcrição de áudio com OpenAI Whisper"""
    
    def __init__(self):
        """Inicializa o serviço Whisper"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        
        # Configurações do Whisper
        self.model = "whisper-1"
        self.max_file_size = 25 * 1024 * 1024  # 25MB limite da API
    
    def transcrever_audiencia(self, arquivo_audio: Path, case_id: str) -> TranscricaoAudiencia:
        """
        Transcreve arquivo de áudio de audiência
        
        Args:
            arquivo_audio: Caminho para o arquivo de áudio
            case_id: ID do caso para logs
            
        Returns:
            TranscricaoAudiencia: Resultado da transcrição
        """
        
        if not arquivo_audio.exists():
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {arquivo_audio}")
        
        # Validar tamanho
        tamanho_arquivo = arquivo_audio.stat().st_size
        if tamanho_arquivo > self.max_file_size:
            raise ValueError(f"Arquivo muito grande ({tamanho_arquivo / 1024 / 1024:.1f}MB). Máximo: 25MB")
        
        self.logger.info(f"[{case_id}] Iniciando transcrição do arquivo: {arquivo_audio.name}")
        
        try:
            inicio = time.time()
            
            # Realizar transcrição
            with open(arquivo_audio, 'rb') as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language="pt",  # Português brasileiro
                    response_format="verbose_json",
                    temperature=0.0,  # Mais determinístico
                    prompt="Esta é uma gravação de audiência trabalhista no Brasil. Transcreva com precisão termos jurídicos, nomes das partes, depoimentos de testemunhas e decisões judiciais."
                )
            
            duracao_transcricao = time.time() - inicio
            
            # Processar resposta
            texto_completo = response.text
            duracao_audio = getattr(response, 'duration', None)
            idioma = getattr(response, 'language', 'pt')
            
            # Extrair segmentos se disponíveis
            segmentos = []
            if hasattr(response, 'segments') and response.segments:
                segmentos = [
                    {
                        'inicio': getattr(seg, 'start', 0),
                        'fim': getattr(seg, 'end', 0),
                        'texto': getattr(seg, 'text', ''),
                        'confianca': getattr(seg, 'avg_logprob', 0)
                    }
                    for seg in response.segments
                ]
            
            # Metadados
            metadados = {
                'arquivo_original': arquivo_audio.name,
                'tamanho_arquivo_mb': tamanho_arquivo / 1024 / 1024,
                'duracao_transcricao_segundos': duracao_transcricao,
                'modelo_usado': self.model,
                'timestamp_transcricao': time.time(),
                'case_id': case_id
            }
            
            # Calcular confiança média
            confianca = None
            if segmentos:
                confiancas = [seg.get('confianca', 0) for seg in segmentos if seg.get('confianca')]
                if confiancas:
                    confianca = sum(confiancas) / len(confiancas)
            
            self.logger.info(f"[{case_id}] Transcrição concluída em {duracao_transcricao:.1f}s")
            
            return TranscricaoAudiencia(
                texto_completo=texto_completo,
                duracao_segundos=duracao_audio,
                idioma_detectado=idioma,
                confianca=confianca,
                segmentos=segmentos,
                metadados=metadados
            )
            
        except openai.OpenAIError as e:
            self.logger.error(f"[{case_id}] Erro na API Whisper: {str(e)}")
            raise Exception(f"Erro na transcrição: {str(e)}")
        except Exception as e:
            self.logger.error(f"[{case_id}] Erro inesperado na transcrição: {str(e)}")
            raise Exception(f"Erro inesperado na transcrição: {str(e)}")
    
    def salvar_transcricao(self, transcricao: TranscricaoAudiencia, diretorio_caso: Path) -> Path:
        """
        Salva transcrição em arquivo
        
        Args:
            transcricao: Resultado da transcrição
            diretorio_caso: Diretório do caso
            
        Returns:
            Path: Caminho do arquivo salvo
        """
        
        # Salvar texto completo
        arquivo_texto = diretorio_caso / "audiencia_transcricao.txt"
        arquivo_texto.write_text(transcricao.texto_completo, encoding='utf-8')
        
        # Salvar dados estruturados
        arquivo_json = diretorio_caso / "audiencia_transcricao.json"
        dados_estruturados = {
            'texto_completo': transcricao.texto_completo,
            'duracao_segundos': transcricao.duracao_segundos,
            'idioma_detectado': transcricao.idioma_detectado,
            'confianca': transcricao.confianca,
            'total_segmentos': len(transcricao.segmentos) if transcricao.segmentos else 0,
            'metadados': transcricao.metadados
        }
        
        arquivo_json.write_text(json.dumps(dados_estruturados, indent=2, ensure_ascii=False), encoding='utf-8')
        
        self.logger.info(f"Transcrição salva em: {arquivo_texto}")
        return arquivo_texto
    
    def processar_audiencia_com_gemini(self, transcricao: TranscricaoAudiencia, case_id: str) -> Dict[str, Any]:
        """
        Processa transcrição da audiência usando Gemini para extrair informações estruturadas
        
        Args:
            transcricao: Resultado da transcrição
            case_id: ID do caso
            
        Returns:
            Dict com informações estruturadas da audiência
        """
        
        # Importar Gemini processor
        from .gemini_processor import GeminiProcessor
        
        try:
            processor = GeminiProcessor()
            
            # Prompt específico para análise de audiência
            prompt_audiencia = f"""
TAREFA: Analisar transcrição de audiência trabalhista e extrair informações estruturadas.

TRANSCRIÇÃO DA AUDIÊNCIA:
{transcricao.texto_completo}

INSTRUÇÕES:
1. IDENTIFIQUE OS DEPOENTES:
   - Autor/Reclamante
   - Reclamada(s)
   - Testemunhas (identificar de qual parte)
   - Juiz/Magistrado

2. EXTRAIA DEPOIMENTOS:
   - Resumo do depoimento de cada parte
   - Pontos controvertidos mencionados
   - Contradições ou inconsistências
   - Fatos relevantes para julgamento

3. DECISÕES TOMADAS:
   - Julgamento antecipado
   - Designação de perícia
   - Encerramento da instrução
   - Outras determinações

FORMATO DE RESPOSTA (JSON):
```json
{{
    "depoentes": [
        {{
            "nome": "string",
            "tipo": "autor/reclamada/testemunha_autor/testemunha_reclamada/juiz",
            "resumo_depoimento": "string"
        }}
    ],
    "pontos_controvertidos": [
        {{
            "tema": "string",
            "posicao_autor": "string",
            "posicao_reclamada": "string"
        }}
    ],
    "decisoes_audiencia": [
        {{
            "tipo": "string",
            "descricao": "string"
        }}
    ],
    "observacoes_juiz": "string",
    "fase_processual": "string"
}}
```

Responda APENAS com o JSON estruturado.
"""

            response = processor.model.generate_content(
                prompt_audiencia,
                generation_config=processor.generation_config
            )
            
            # Parse da resposta
            resultado_json = processor._extrair_json_resposta(response.text)
            
            self.logger.info(f"[{case_id}] Análise da audiência concluída")
            return resultado_json
            
        except Exception as e:
            self.logger.error(f"[{case_id}] Erro na análise da audiência: {str(e)}")
            # Retornar estrutura básica em caso de erro
            return {
                "depoentes": [],
                "pontos_controvertidos": [],
                "decisoes_audiencia": [],
                "observacoes_juiz": "Erro na análise automática",
                "fase_processual": "Não identificada",
                "erro": str(e)
            }
