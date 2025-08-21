"""
Gerenciador de Conhecimento Jurídico Geral
Base consolidada de dispositivos legais, jurisprudência e precedentes
"""

import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class LegalDevice:
    """Dispositivo legal estruturado"""
    type: str  # artigo, paragrafo, inciso
    number: str
    law: str  # CLT, CF, CPC, etc.
    title: str
    content: str
    keywords: List[str]
    related_devices: List[str]
    last_updated: str

@dataclass
class Jurisprudence:
    """Jurisprudência estruturada"""
    type: str  # sumula, oj, acordao
    number: str
    court: str  # TST, STF, STJ, TRT
    title: str
    content: str
    keywords: List[str]
    precedent_value: float  # 0-1, sendo 1 = vinculante
    last_updated: str
    related_articles: List[str]

@dataclass
class LegalTemplate:
    """Template de fundamentação por tipo de pedido"""
    request_type: str  # horas_extras, adicional_noturno, etc.
    title: str
    legal_foundation: List[str]  # Artigos aplicáveis
    jurisprudence: List[str]  # Súmulas/OJs aplicáveis
    argumentation_template: str
    decision_templates: Dict[str, str]  # procedente, improcedente
    keywords: List[str]

class LegalKnowledgeManager:
    """Gerenciador da base de conhecimento jurídico geral"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.logger = logging.getLogger(__name__)
        
        # Estrutura de armazenamento
        self.devices_path = storage_path / "dispositivos_legais"
        self.jurisprudence_path = storage_path / "jurisprudencia"
        self.templates_path = storage_path / "templates_fundamentacao"
        
        # Criar estrutura
        for path in [self.devices_path, self.jurisprudence_path, self.templates_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Cache em memória
        self._devices_cache = {}
        self._jurisprudence_cache = {}
        self._templates_cache = {}
        
        # Inicializar conhecimento base
        self._initialize_base_knowledge()
    
    def _initialize_base_knowledge(self):
        """Inicializa conhecimento jurídico fundamental"""
        self.logger.info("Inicializando base de conhecimento jurídico...")
        
        # CLT - Artigos fundamentais
        self._create_clt_articles()
        
        # Constituição Federal
        self._create_cf_articles()
        
        # Súmulas TST essenciais
        self._create_tst_sumulas()
        
        # Templates de fundamentação
        self._create_argumentation_templates()
        
        self.logger.info("Base de conhecimento jurídico inicializada")
    
    def _create_clt_articles(self):
        """Cria artigos fundamentais da CLT"""
        clt_articles = [
            {
                "number": "7",
                "title": "Duração do trabalho",
                "content": "A duração normal do trabalho, para os empregados em qualquer atividade privada, não excederá de 8 (oito) horas diárias, desde que não seja fixado expressamente outro limite.",
                "keywords": ["jornada", "duração", "trabalho", "8 horas", "limite"]
            },
            {
                "number": "59",
                "title": "Horas extraordinárias",
                "content": "A duração diária do trabalho poderá ser acrescida de horas suplementares, em número não excedente de duas, mediante acordo escrito entre empregador e empregado, ou mediante contrato coletivo de trabalho.",
                "keywords": ["horas extras", "suplementares", "acordo", "duas horas", "limite"]
            },
            {
                "number": "73",
                "title": "Trabalho noturno",
                "content": "Salvo nos casos de revezamento semanal ou quinzenal, o trabalho noturno terá remuneração superior à do diurno e, para esse efeito, sua remuneração terá um acréscimo de 20% (vinte por cento), pelo menos, sobre a hora diurna.",
                "keywords": ["trabalho noturno", "adicional", "20%", "remuneração", "diurno"]
            },
            {
                "number": "482",
                "title": "Justa causa",
                "content": "Constituem justa causa para rescisão do contrato de trabalho pelo empregador: a) ato de improbidade; b) incontinência de conduta ou mau procedimento; c) negociação habitual por conta própria ou alheia sem permissão do empregador...",
                "keywords": ["justa causa", "rescisão", "improbidade", "mau procedimento", "falta grave"]
            },
            {
                "number": "477",
                "title": "Verbas rescisórias",
                "content": "É assegurado a todo empregado, não existindo prazo estipulado para a terminação do respectivo contrato, e quando não haja ele dado motivo para cessação das relações de trabalho, o direito de haver do empregador uma indenização...",
                "keywords": ["verbas rescisórias", "indenização", "aviso prévio", "terminação", "contrato"]
            }
        ]
        
        for article_data in clt_articles:
            device = LegalDevice(
                type="artigo",
                number=article_data["number"],
                law="CLT",
                title=article_data["title"],
                content=article_data["content"],
                keywords=article_data["keywords"],
                related_devices=[],
                last_updated=datetime.now().isoformat()
            )
            self.save_legal_device(device)
    
    def _create_cf_articles(self):
        """Cria artigos fundamentais da Constituição Federal"""
        cf_articles = [
            {
                "number": "7",
                "inciso": "XVI",
                "title": "Direitos dos trabalhadores - Horas extras",
                "content": "São direitos dos trabalhadores urbanos e rurais, além de outros que visem à melhoria de sua condição social: XVI - remuneração do serviço extraordinário superior, no mínimo, em cinquenta por cento à do normal",
                "keywords": ["direitos trabalhadores", "horas extras", "50%", "remuneração", "extraordinário"]
            },
            {
                "number": "7",
                "inciso": "XXXIII",
                "title": "Direitos dos trabalhadores - Trabalho noturno",
                "content": "São direitos dos trabalhadores urbanos e rurais: XXXIII - proibição de trabalho noturno, perigoso ou insalubre a menores de dezoito e de qualquer trabalho a menores de dezesseis anos, salvo na condição de aprendiz, a partir de quatorze anos",
                "keywords": ["trabalho noturno", "menores", "proibição", "insalubre", "perigoso"]
            },
            {
                "number": "5",
                "inciso": "XXXV",
                "title": "Princípio da inafastabilidade da jurisdição",
                "content": "A lei não excluirá da apreciação do Poder Judiciário lesão ou ameaça a direito",
                "keywords": ["acesso justiça", "jurisdição", "direito", "lesão", "judiciário"]
            }
        ]
        
        for article_data in cf_articles:
            device = LegalDevice(
                type="artigo",
                number=f"{article_data['number']}, {article_data['inciso']}",
                law="CF/88",
                title=article_data["title"],
                content=article_data["content"],
                keywords=article_data["keywords"],
                related_devices=[],
                last_updated=datetime.now().isoformat()
            )
            self.save_legal_device(device)
    
    def _create_tst_sumulas(self):
        """Cria súmulas essenciais do TST"""
        tst_sumulas = [
            {
                "number": "338",
                "title": "Jornada de trabalho. Ônus da prova",
                "content": "É ônus do empregador que conta com mais de 10 (dez) empregados o registro da jornada de trabalho na forma do art. 74, § 2º da CLT. A não-apresentação injustificada dos controles de frequência gera presunção relativa de veracidade da jornada de trabalho, a qual pode ser elidida por prova em contrário.",
                "keywords": ["jornada trabalho", "ônus prova", "registro", "controle frequência", "presunção"],
                "precedent_value": 0.9
            },
            {
                "number": "437",
                "title": "Intervalo intrajornada para repouso e alimentação",
                "content": "É válida, em caráter excepcional, a redução do intervalo intrajornada, desde que prevista em norma coletiva de trabalho e garantidas integralmente a saúde e a segurança do trabalhador.",
                "keywords": ["intervalo", "repouso", "alimentação", "norma coletiva", "saúde"],
                "precedent_value": 0.9
            },
            {
                "number": "126",
                "title": "Bancário. Horas extras",
                "content": "O bancário sujeito à jornada de seis horas tem direito ao pagamento da sétima e oitava horas, como extras, observado o art. 224, § 1º, da CLT.",
                "keywords": ["bancário", "6 horas", "sétima oitava", "horas extras", "CLT 224"],
                "precedent_value": 0.9
            }
        ]
        
        for sumula_data in tst_sumulas:
            jurisprudence = Jurisprudence(
                type="sumula",
                number=sumula_data["number"],
                court="TST",
                title=sumula_data["title"],
                content=sumula_data["content"],
                keywords=sumula_data["keywords"],
                precedent_value=sumula_data["precedent_value"],
                last_updated=datetime.now().isoformat(),
                related_articles=[]
            )
            self.save_jurisprudence(jurisprudence)
    
    def _create_argumentation_templates(self):
        """Cria templates de argumentação por tipo de pedido"""
        templates = [
            {
                "request_type": "horas_extras",
                "title": "Template para fundamentação de horas extras",
                "legal_foundation": ["Art. 7º, XVI, CF/88", "Art. 59, CLT"],
                "jurisprudence": ["Súmula 338, TST"],
                "argumentation_template": """
Das horas extras

O artigo 7º, inciso XVI, da Constituição Federal assegura o direito à remuneração do serviço extraordinário superior, no mínimo, em cinquenta por cento à do normal.

A Consolidação das Leis do Trabalho, em seu artigo 59, estabelece que a duração diária do trabalho poderá ser acrescida de horas suplementares, mediante acordo entre as partes.

A Súmula 338 do TST estabelece que é ônus do empregador que conta com mais de 10 empregados o registro da jornada de trabalho na forma do art. 74, § 2º da CLT.

{analise_fatos}

{conclusao}
""",
                "decision_templates": {
                    "procedente": "Diante do exposto, JULGO PROCEDENTE o pedido de horas extras, condenando a reclamada ao pagamento das horas extraordinárias no período de {periodo}, com adicional de 50%.",
                    "improcedente": "Diante do exposto, JULGO IMPROCEDENTE o pedido de horas extras, por ausência de comprovação da prestação habitual de serviço extraordinário."
                },
                "keywords": ["horas extras", "extraordinário", "50%", "registro", "jornada"]
            },
            {
                "request_type": "adicional_noturno",
                "title": "Template para fundamentação de adicional noturno",
                "legal_foundation": ["Art. 73, CLT"],
                "jurisprudence": [],
                "argumentation_template": """
Do adicional noturno

O artigo 73 da CLT estabelece que o trabalho noturno terá remuneração superior à do diurno e, para esse efeito, sua remuneração terá um acréscimo de 20%, pelo menos, sobre a hora diurna.

Considera-se noturno, para os efeitos desta consolidação, o trabalho executado entre as 22 horas de um dia e as 5 horas do dia seguinte.

{analise_fatos}

{conclusao}
""",
                "decision_templates": {
                    "procedente": "Diante do exposto, JULGO PROCEDENTE o pedido de adicional noturno, condenando a reclamada ao pagamento do adicional de 20% sobre as horas trabalhadas no período noturno.",
                    "improcedente": "Diante do exposto, JULGO IMPROCEDENTE o pedido de adicional noturno, por ausência de comprovação do trabalho no período noturno."
                },
                "keywords": ["adicional noturno", "20%", "22h às 5h", "remuneração", "CLT 73"]
            },
            {
                "request_type": "justa_causa",
                "title": "Template para fundamentação de justa causa",
                "legal_foundation": ["Art. 482, CLT"],
                "jurisprudence": [],
                "argumentation_template": """
Da justa causa

O artigo 482 da CLT estabelece as hipóteses de justa causa para rescisão do contrato de trabalho pelo empregador, exigindo-se a configuração de falta grave que torne incompatível a continuidade da relação de emprego.

A justa causa deve ser atual, grave, relacionada ao contrato de trabalho e comprovada de forma inequívoca, observando-se os princípios da proporcionalidade e da imediatidade.

{analise_fatos}

{conclusao}
""",
                "decision_templates": {
                    "procedente": "Diante do exposto, JULGO PROCEDENTE o pedido de reversão da justa causa, por ausência de comprovação da falta grave imputada ao reclamante.",
                    "improcedente": "Diante do exposto, JULGO IMPROCEDENTE o pedido de reversão da justa causa, mantendo-se a dispensa por justa causa aplicada pela reclamada."
                },
                "keywords": ["justa causa", "falta grave", "482 CLT", "proporcionalidade", "imediatidade"]
            }
        ]
        
        for template_data in templates:
            template = LegalTemplate(
                request_type=template_data["request_type"],
                title=template_data["title"],
                legal_foundation=template_data["legal_foundation"],
                jurisprudence=template_data["jurisprudence"],
                argumentation_template=template_data["argumentation_template"],
                decision_templates=template_data["decision_templates"],
                keywords=template_data["keywords"]
            )
            self.save_legal_template(template)
    
    def save_legal_device(self, device: LegalDevice):
        """Salva dispositivo legal"""
        file_path = self.devices_path / f"{device.law}_{device.number.replace(',', '_').replace(' ', '_')}.json"
        
        device_dict = {
            "type": device.type,
            "number": device.number,
            "law": device.law,
            "title": device.title,
            "content": device.content,
            "keywords": device.keywords,
            "related_devices": device.related_devices,
            "last_updated": device.last_updated
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(device_dict, f, ensure_ascii=False, indent=2)
        
        # Cache
        cache_key = f"{device.law}_{device.number}"
        self._devices_cache[cache_key] = device
    
    def save_jurisprudence(self, jurisprudence: Jurisprudence):
        """Salva jurisprudência"""
        file_path = self.jurisprudence_path / f"{jurisprudence.court}_{jurisprudence.type}_{jurisprudence.number}.json"
        
        juris_dict = {
            "type": jurisprudence.type,
            "number": jurisprudence.number,
            "court": jurisprudence.court,
            "title": jurisprudence.title,
            "content": jurisprudence.content,
            "keywords": jurisprudence.keywords,
            "precedent_value": jurisprudence.precedent_value,
            "last_updated": jurisprudence.last_updated,
            "related_articles": jurisprudence.related_articles
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(juris_dict, f, ensure_ascii=False, indent=2)
        
        # Cache
        cache_key = f"{jurisprudence.court}_{jurisprudence.type}_{jurisprudence.number}"
        self._jurisprudence_cache[cache_key] = jurisprudence
    
    def save_legal_template(self, template: LegalTemplate):
        """Salva template de fundamentação"""
        file_path = self.templates_path / f"template_{template.request_type}.json"
        
        template_dict = {
            "request_type": template.request_type,
            "title": template.title,
            "legal_foundation": template.legal_foundation,
            "jurisprudence": template.jurisprudence,
            "argumentation_template": template.argumentation_template,
            "decision_templates": template.decision_templates,
            "keywords": template.keywords
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(template_dict, f, ensure_ascii=False, indent=2)
        
        # Cache
        self._templates_cache[template.request_type] = template
    
    def search_legal_devices(self, query: str, law: Optional[str] = None) -> List[LegalDevice]:
        """Busca dispositivos legais por query"""
        results = []
        query_lower = query.lower()
        
        # Buscar em cache primeiro
        for key, device in self._devices_cache.items():
            if law and device.law != law:
                continue
                
            # Buscar em keywords, title e content
            if (any(keyword.lower() in query_lower for keyword in device.keywords) or
                query_lower in device.title.lower() or
                query_lower in device.content.lower()):
                results.append(device)
        
        # Se cache vazio, carregar do disco
        if not self._devices_cache:
            self._load_devices_cache()
            return self.search_legal_devices(query, law)  # Recursão
        
        return sorted(results, key=lambda x: len(x.keywords), reverse=True)
    
    def search_jurisprudence(self, query: str, court: Optional[str] = None, min_precedent_value: float = 0.0) -> List[Jurisprudence]:
        """Busca jurisprudência por query"""
        results = []
        query_lower = query.lower()
        
        for key, juris in self._jurisprudence_cache.items():
            if court and juris.court != court:
                continue
                
            if juris.precedent_value < min_precedent_value:
                continue
                
            # Buscar em keywords, title e content
            if (any(keyword.lower() in query_lower for keyword in juris.keywords) or
                query_lower in juris.title.lower() or
                query_lower in juris.content.lower()):
                results.append(juris)
        
        # Se cache vazio, carregar do disco
        if not self._jurisprudence_cache:
            self._load_jurisprudence_cache()
            return self.search_jurisprudence(query, court, min_precedent_value)
        
        return sorted(results, key=lambda x: x.precedent_value, reverse=True)
    
    def get_template_for_request(self, request_type: str) -> Optional[LegalTemplate]:
        """Obtém template de fundamentação para tipo de pedido"""
        if request_type in self._templates_cache:
            return self._templates_cache[request_type]
        
        # Carregar do disco se não estiver em cache
        file_path = self.templates_path / f"template_{request_type}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                template = LegalTemplate(**data)
                self._templates_cache[request_type] = template
                return template
        
        return None
    
    def _load_devices_cache(self):
        """Carrega dispositivos legais em cache"""
        for file_path in self.devices_path.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    device = LegalDevice(**data)
                    cache_key = f"{device.law}_{device.number}"
                    self._devices_cache[cache_key] = device
            except Exception as e:
                self.logger.error(f"Erro ao carregar dispositivo {file_path}: {e}")
    
    def _load_jurisprudence_cache(self):
        """Carrega jurisprudência em cache"""
        for file_path in self.jurisprudence_path.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    juris = Jurisprudence(**data)
                    cache_key = f"{juris.court}_{juris.type}_{juris.number}"
                    self._jurisprudence_cache[cache_key] = juris
            except Exception as e:
                self.logger.error(f"Erro ao carregar jurisprudência {file_path}: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas da base de conhecimento"""
        if not self._devices_cache:
            self._load_devices_cache()
        if not self._jurisprudence_cache:
            self._load_jurisprudence_cache()
        
        return {
            "legal_devices": {
                "total": len(self._devices_cache),
                "by_law": self._count_by_field(self._devices_cache.values(), "law")
            },
            "jurisprudence": {
                "total": len(self._jurisprudence_cache),
                "by_court": self._count_by_field(self._jurisprudence_cache.values(), "court"),
                "by_type": self._count_by_field(self._jurisprudence_cache.values(), "type"),
                "high_precedent": len([j for j in self._jurisprudence_cache.values() if j.precedent_value >= 0.8])
            },
            "templates": {
                "total": len(self._templates_cache),
                "available_types": list(self._templates_cache.keys())
            }
        }
    
    def _count_by_field(self, items, field: str) -> Dict[str, int]:
        """Conta itens por campo"""
        counts = {}
        for item in items:
            value = getattr(item, field, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts
