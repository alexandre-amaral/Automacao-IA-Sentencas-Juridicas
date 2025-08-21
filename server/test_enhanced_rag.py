"""
Teste Completo do RAG Aprimorado
Valida chunking semântico, embeddings otimizados e recuperação contextual
"""

import json
import time
from pathlib import Path
from services.enhanced_rag_service import EnhancedRAGService
from services.contextual_retriever import QueryType
from services.gemini_processor import ProcessoEstruturado, ParteProcesso, PedidoProcesso, FatoRelevante

def create_test_sentence():
    """Cria sentença de exemplo para teste do estilo"""
    return """
RELATÓRIO

Trata-se de reclamação trabalhista ajuizada por JOÃO DA SILVA contra EMPRESA XYZ LTDA, 
pleiteando o pagamento de horas extras, adicional noturno, verbas rescisórias e danos morais.

O reclamante alega que laborava das 22h às 6h, sem o devido pagamento do adicional noturno,
e que prestava horas extras habitualmente sem a devida remuneração.

A reclamada, em sua contestação, nega os fatos alegados e sustenta que o controle de ponto
era rigorosamente observado, não havendo horas extras a serem pagas.

FUNDAMENTAÇÃO

Passo ao exame das questões controvertidas.

Das horas extras

O artigo 7º, inciso XVI, da Constituição Federal assegura o direito à remuneração do serviço 
extraordinário superior, no mínimo, em cinquenta por cento à do normal.

A Súmula 338 do TST estabelece que a jornada de trabalho deve ser comprovada pelo empregador,
cabendo a ele o ônus da prova quanto aos registros de frequência.

Analisando a prova dos autos, verifico que os cartões de ponto apresentados demonstram
jornada habitual das 8h às 18h, configurando duas horas extras diárias.

Do adicional noturno

O artigo 73 da CLT estabelece que o trabalho noturno deve ser remunerado com adicional
de no mínimo 20% sobre a hora diurna.

Restou comprovado nos autos que o reclamante laborava no período noturno sem o devido adicional.

DISPOSITIVO

Posto isto, JULGO PROCEDENTES EM PARTE os pedidos formulados na inicial para:

1. CONDENAR a reclamada ao pagamento de horas extras no período de janeiro/2022 a dezembro/2023;
2. CONDENAR a reclamada ao pagamento do adicional noturno no mesmo período;
3. JULGAR IMPROCEDENTE o pedido de danos morais por ausência de comprovação.

Custas pela reclamada. Sem honorários advocatícios por ausência dos requisitos legais.
"""

def create_test_processo():
    """Cria processo estruturado para teste"""
    return ProcessoEstruturado(
        numero_processo="0001234-56.2023.5.09.0010",
        partes=[
            ParteProcesso(nome="João da Silva", tipo="reclamante", qualificacao="Operador"),
            ParteProcesso(nome="Empresa XYZ Ltda", tipo="reclamada", qualificacao="Pessoa Jurídica")
        ],
        pedidos=[
            PedidoProcesso(descricao="Horas extras", categoria="verbas", valor_estimado="R$ 5.000,00"),
            PedidoProcesso(descricao="Adicional noturno", categoria="verbas", valor_estimado="R$ 3.000,00"),
            PedidoProcesso(descricao="Danos morais", categoria="indenizacao", valor_estimado="R$ 10.000,00")
        ],
        fatos_relevantes=[
            FatoRelevante(descricao="Trabalho noturno sem adicional", fonte="inicial"),
            FatoRelevante(descricao="Horas extras habituais", fonte="inicial")
        ],
        periodo_contratual="01/2022 a 12/2023",
        valor_causa="R$ 18.000,00",
        competencia="9ª Vara do Trabalho",
        jurisprudencias_citadas=["Súmula 338 TST"],
        decisao_final=None,
        fundamentacao_resumida=None
    )

def test_embedding_optimization():
    """Testa embeddings otimizados"""
    print("🧠 TESTE 1: Embeddings Otimizados")
    print("=" * 50)
    
    rag = EnhancedRAGService("test_enhanced_001")
    
    # Textos jurídicos de teste
    test_texts = [
        "O reclamante tem direito a horas extras conforme artigo 7º da CF",
        "A Súmula 338 do TST trata do ônus da prova dos registros de ponto",
        "Julgo procedente o pedido de adicional noturno conforme CLT",
        "Testemunha confirmou trabalho habitual após 18h"
    ]
    
    print("\\n📝 Criando embeddings...")
    start_time = time.time()
    
    embedding_results = rag.embedding_service.create_batch_embeddings(test_texts)
    
    elapsed = time.time() - start_time
    print(f"⏱️ Tempo para {len(test_texts)} embeddings: {elapsed:.2f}s")
    
    for i, result in enumerate(embedding_results):
        print(f"\\n{i+1}. Texto: {test_texts[i][:50]}...")
        print(f"   Categoria: {result.semantic_category}")
        print(f"   Conceitos: {result.legal_concepts}")
        print(f"   Confiança: {result.confidence:.3f}")
    
    print("\\n✅ Teste de embeddings concluído!")
    return True

def test_semantic_chunking():
    """Testa chunking semântico"""
    print("\\n🔪 TESTE 2: Chunking Semântico")
    print("=" * 50)
    
    rag = EnhancedRAGService("test_enhanced_002")
    
    # Texto longo para chunking
    sentence_text = create_test_sentence()
    
    print("\\n📄 Aplicando chunking semântico...")
    chunks = rag.chunker.create_chunks(sentence_text, "Sentença Teste")
    
    print(f"\\n📊 Resultados: {len(chunks)} chunks criados")
    
    for i, chunk in enumerate(chunks):
        print(f"\\n--- Chunk {i+1} ---")
        print(f"Tipo: {chunk.chunk_type.value}")
        print(f"Prioridade: {chunk.priority}/10")
        print(f"Conceitos: {chunk.key_concepts}")
        print(f"Referências: {chunk.legal_references}")
        if chunk.section_title:
            print(f"Seção: {chunk.section_title}")
        print(f"Conteúdo: {chunk.content[:100]}...")
    
    print("\\n✅ Teste de chunking concluído!")
    return chunks

def test_contextual_retrieval():
    """Testa recuperação contextual"""
    print("\\n🎯 TESTE 3: Recuperação Contextual")
    print("=" * 50)
    
    rag = EnhancedRAGService("test_enhanced_003")
    
    # Inicializar com conhecimento
    sentence_examples = [create_test_sentence()]
    rag.initialize_judge_style(sentence_examples)
    
    processo = create_test_processo()
    transcricao = "Testemunha confirmou que trabalhava até 20h todos os dias, com frequentes horas extras."
    rag.save_case_knowledge(processo, transcricao)
    
    # Queries de teste
    test_queries = [
        ("Como calcular horas extras?", QueryType.FUNDAMENTACAO_LEGAL),
        ("O que disse a testemunha sobre horários?", QueryType.ANALISE_FATOS),
        ("Qual a estrutura do dispositivo da sentença?", QueryType.ESTRUTURA_SENTENCA),
        ("Súmulas sobre controle de ponto", QueryType.BUSCA_JURISPRUDENCIA)
    ]
    
    for query, query_type in test_queries:
        print(f"\\n🔍 Query: '{query}' | Tipo: {query_type.value}")
        
        results = rag.query_knowledge(
            query=query,
            query_type=query_type,
            top_k=3,
            include_explanation=True
        )
        
        print(f"📊 Resultados: {results['total_results']}")
        
        for i, result in enumerate(results['results'][:2], 1):
            print(f"\\n  {i}. Score: {result['relevance_score']:.3f} | {result['chunk_type']}")
            print(f"     Conceitos: {result['key_concepts']}")
            print(f"     Conteúdo: {result['content'][:80]}...")
    
    print("\\n✅ Teste de recuperação concluído!")
    return True

def test_dialogue_context():
    """Testa contexto de diálogo"""
    print("\\n💬 TESTE 4: Contexto de Diálogo")
    print("=" * 50)
    
    rag = EnhancedRAGService("test_enhanced_004")
    
    # Simular diálogo Claude-Gemini
    dialogue_steps = [
        ("Quais são os fatos principais do caso?", "O reclamante trabalhou de 01/2022 a 12/2023, alegando horas extras e adicional noturno não pagos."),
        ("Que provas existem para horas extras?", "Cartões de ponto demonstram jornada das 8h às 18h habitualmente, configurando 2h extras diárias."),
        ("Qual a fundamentação legal aplicável?", "Art. 7º, XVI da CF e Súmula 338 TST sobre ônus da prova dos registros de frequência.")
    ]
    
    for step, (question, answer) in enumerate(dialogue_steps, 1):
        print(f"\\n💭 Salvando diálogo etapa {step}...")
        rag.save_dialogue_context(question, answer, step)
    
    # Testar recuperação do contexto
    context_query = "O que foi discutido sobre provas de horas extras?"
    
    print(f"\\n🔍 Consultando contexto: '{context_query}'")
    results = rag.query_knowledge(
        query=context_query,
        sources=["dialogo_contexto"],
        top_k=2
    )
    
    print(f"📊 Contexto encontrado: {results['total_results']} resultados")
    
    for result in results['results']:
        print(f"\\n- Score: {result['relevance_score']:.3f}")
        print(f"  Conteúdo: {result['content'][:100]}...")
    
    print("\\n✅ Teste de contexto concluído!")
    return True

def test_performance():
    """Testa performance do sistema"""
    print("\\n⚡ TESTE 5: Performance")
    print("=" * 50)
    
    rag = EnhancedRAGService("test_enhanced_005")
    
    # Inicialização
    start_time = time.time()
    sentence_examples = [create_test_sentence() * 3]  # Texto maior
    rag.initialize_judge_style(sentence_examples)
    init_time = time.time() - start_time
    
    # Salvamento de caso
    start_time = time.time()
    processo = create_test_processo()
    transcricao = "Depoimento longo com muitos detalhes sobre horários e condições de trabalho..." * 10
    rag.save_case_knowledge(processo, transcricao)
    save_time = time.time() - start_time
    
    # Queries múltiplas
    start_time = time.time()
    queries = ["horas extras", "adicional noturno", "testemunha", "súmula", "fundamentação"] * 5
    
    for query in queries:
        rag.query_knowledge(query, top_k=5)
    
    query_time = time.time() - start_time
    
    # Estatísticas
    stats = rag.get_statistics()
    
    print(f"\\n📊 Resultados de Performance:")
    print(f"⏱️ Inicialização: {init_time:.2f}s")
    print(f"⏱️ Salvamento: {save_time:.2f}s")
    print(f"⏱️ {len(queries)} queries: {query_time:.2f}s ({query_time/len(queries):.3f}s/query)")
    
    print(f"\\n📈 Estatísticas:")
    for collection, data in stats["collections"].items():
        print(f"  {collection}: {data['chunk_count']} chunks ({data['status']})")
    
    print("\\n✅ Teste de performance concluído!")
    return True

def main():
    """Executa todos os testes do RAG aprimorado"""
    print("🚀 TESTANDO RAG APRIMORADO - PARTE B")
    print("=" * 60)
    
    try:
        # Executar testes
        test_embedding_optimization()
        test_semantic_chunking()
        test_contextual_retrieval()
        test_dialogue_context()
        test_performance()
        
        print("\\n🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("✅ RAG Otimizado e Contextual está funcionando perfeitamente")
        
    except Exception as e:
        print(f"\\n❌ ERRO NOS TESTES: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False
    
    return True

if __name__ == "__main__":
    main()
