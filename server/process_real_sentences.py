"""
Script para processar sentenças reais e integrar com o sistema RAG
Executa processamento completo das pastas de sentenças da juíza
"""

import logging
import sys
from pathlib import Path

# Adicionar pasta services ao path
sys.path.append(str(Path(__file__).parent / "services"))

from services.real_sentences_processor import RealSentencesProcessor
from services.enhanced_rag_service import EnhancedRAGService
from services.instance_manager import InstanceManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Processamento principal das sentenças reais"""
    logger.info("🚀 INICIANDO PROCESSAMENTO DE SENTENÇAS REAIS DA JUÍZA")
    logger.info("=" * 60)
    
    # Paths
    project_root = Path(__file__).parent.parent
    
    try:
        # 1. PROCESSAR SENTENÇAS REAIS
        logger.info("📝 ETAPA 1: Processando sentenças reais...")
        processor = RealSentencesProcessor(project_root)
        
        # Processar todas as sentenças
        processed_sentences = processor.process_all_sentences(force_reprocess=False)
        
        if not processed_sentences:
            logger.error("❌ Nenhuma sentença foi processada. Verifique se as pastas existem.")
            return False
        
        logger.info(f"✅ {len(processed_sentences)} sentenças processadas com sucesso")
        
        # Estatísticas
        stats = processor.get_processed_statistics()
        logger.info(f"📊 Estatísticas:")
        logger.info(f"   - Anos cobertos: {stats['years']}")
        logger.info(f"   - Tipos de arquivo: {stats['file_types']}")
        logger.info(f"   - Média de palavras: {stats['avg_word_count']:.0f}")
        logger.info(f"   - Cobertura de seções: {stats['sections_coverage']}")
        
        # 2. ANALISAR ESTILO DA JUÍZA
        logger.info("\\n🎨 ETAPA 2: Analisando estilo da juíza...")
        style_profile = processor.analyze_judge_style_from_real_sentences(processed_sentences)
        
        if style_profile:
            logger.info(f"✅ Perfil de estilo criado:")
            logger.info(f"   - Padrões linguísticos: {len(style_profile.linguistic_patterns)}")
            logger.info(f"   - Padrões estruturais: {len(style_profile.structural_patterns)}")
            logger.info(f"   - Expressões legais: {len(style_profile.legal_expressions)}")
        
        # 3. CRIAR TEMPLATES MASTER
        logger.info("\\n📋 ETAPA 3: Criando templates master...")
        master_template = processor.create_master_templates_from_real_data(processed_sentences)
        
        if master_template:
            logger.info(f"✅ Template master criado com dados reais")
            logger.info(f"   - Sentenças analisadas: {master_template['metadata']['total_sentences_analyzed']}")
            logger.info(f"   - Anos cobertos: {master_template['metadata']['years_covered']}")
        
        # 4. EXPORTAR PARA RAG
        logger.info("\\n📤 ETAPA 4: Exportando para integração RAG...")
        rag_export_file = project_root / "server" / "storage" / "processed_sentences" / "rag_integration_data.json"
        rag_data = processor.export_for_rag_integration(rag_export_file)
        
        if rag_data and "error" not in rag_data:
            logger.info(f"✅ Dados exportados para RAG:")
            logger.info(f"   - Sentenças para embeddings: {len(rag_data['sentences_for_embeddings'])}")
            logger.info(f"   - Padrões de estilo: {'Sim' if rag_data['style_patterns'] else 'Não'}")
            logger.info(f"   - Conhecimento jurídico: {len(rag_data['legal_knowledge']['frequent_citations'])} citações frequentes")
        
        # 5. INTEGRAR COM TEMPLATE MASTER ATUAL
        logger.info("\\n🔗 ETAPA 5: Integrando com template master atual...")
        
        # Atualizar template master do sistema
        template_master_path = project_root / "server" / "storage" / "rag_storage" / "template_master"
        
        # Salvar estilo da juíza real
        estilo_real_file = template_master_path / "estilo_juiza_real.json"
        if style_profile:
            import json
            from dataclasses import asdict
            with open(estilo_real_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(style_profile), f, ensure_ascii=False, indent=2)
            logger.info(f"✅ Estilo real salvo: {estilo_real_file}")
        
        # Salvar sentenças exemplo
        sentencas_exemplo_file = template_master_path / "sentencas_exemplo_reais.json"
        with open(sentencas_exemplo_file, 'w', encoding='utf-8') as f:
            # Selecionar melhores exemplos
            exemplos = []
            for sentence in processed_sentences[:10]:  # Top 10
                if len(sentence.content) > 1000:  # Sentenças completas
                    exemplos.append({
                        "case_number": sentence.case_number,
                        "year": sentence.year,
                        "content": sentence.content[:5000],  # Limitar tamanho
                        "sections": sentence.sections,
                        "legal_citations": sentence.legal_citations,
                        "word_count": sentence.word_count
                    })
            
            json.dump({
                "total_examples": len(exemplos),
                "created_from_real_data": True,
                "created_at": processed_sentences[0].processed_at if processed_sentences else "",
                "examples": exemplos
            }, f, ensure_ascii=False, indent=2)
            
        logger.info(f"✅ Sentenças exemplo salvas: {sentencas_exemplo_file}")
        
        # 6. TESTAR INTEGRAÇÃO
        logger.info("\\n🧪 ETAPA 6: Testando integração com RAG...")
        
        # Criar instância de teste
        test_case_id = "test_real_sentences_001"
        instance_manager = InstanceManager()
        instance_info = instance_manager.get_or_create_instance(test_case_id)
        
        # Testar RAG aprimorado
        rag = EnhancedRAGService(test_case_id)
        
        # Inicializar com sentenças reais
        sentences_content = [s.content for s in processed_sentences[:5]]  # Usar 5 primeiras
        rag.initialize_judge_style(sentences_content, force_reload=True)
        
        # Testar busca
        test_query = "Como fundamentar pedido de horas extras?"
        results = rag.query_knowledge(test_query, top_k=3)
        
        if results and results["total_results"] > 0:
            logger.info(f"✅ Teste de integração bem-sucedido:")
            logger.info(f"   - Query: {test_query}")
            logger.info(f"   - Resultados: {results['total_results']}")
            logger.info(f"   - Melhor score: {results['results'][0]['relevance_score']:.3f}")
        else:
            logger.warning("⚠️ Teste de integração retornou poucos resultados")
        
        # Estatísticas do RAG
        rag_stats = rag.get_statistics()
        logger.info(f"📊 Estatísticas do RAG:")
        for collection, stats in rag_stats["collections"].items():
            logger.info(f"   - {collection}: {stats['chunk_count']} chunks ({stats['status']})")
        
        logger.info("\\n🎉 PROCESSAMENTO COMPLETO!")
        logger.info("=" * 60)
        logger.info("✅ Sentenças reais processadas e integradas com sucesso")
        logger.info("✅ Sistema RAG agora usa dados reais da juíza")
        logger.info("✅ Templates master atualizados com padrões reais")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ERRO NO PROCESSAMENTO: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
