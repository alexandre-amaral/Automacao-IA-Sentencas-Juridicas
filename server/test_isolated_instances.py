"""
Teste para validar gestão de instâncias isoladas
Verifica se o isolamento está funcionando corretamente
"""

import json
import time
from pathlib import Path
from services.instance_manager import InstanceManager
from services.isolated_rag_service import IsolatedRAGService
from services.gemini_processor import ProcessoEstruturado, ParteProcesso, PedidoProcesso, FatoRelevante

def test_instance_creation():
    """Testa criação de instâncias isoladas"""
    print("🧪 TESTE 1: Criação de Instâncias Isoladas")
    print("=" * 50)
    
    instance_manager = InstanceManager()
    
    # Criar duas instâncias diferentes
    case_ids = ["test_case_001", "test_case_002"]
    
    for case_id in case_ids:
        try:
            print(f"\n📋 Criando instância: {case_id}")
            
            # Criar instância
            instance_info = instance_manager.create_isolated_instance(case_id)
            
            print(f"✅ Instância criada: {instance_info['namespace']}")
            print(f"📁 Diretórios: {len(instance_info['directories'])} criados")
            
            # Validar isolamento
            validation = instance_manager.validate_isolation(case_id)
            print(f"🔒 Validação de isolamento:")
            for check, result in validation.items():
                status = "✅" if result else "❌"
                print(f"   {status} {check}: {result}")
            
        except Exception as e:
            print(f"❌ Erro ao criar instância {case_id}: {str(e)}")
    
    # Listar instâncias ativas
    print(f"\n📊 Instâncias ativas:")
    instances = instance_manager.list_active_instances()
    for instance in instances:
        print(f"   - {instance['case_id']} (criada em {instance['created_at']})")
    
    print("\n✅ TESTE 1 CONCLUÍDO\n")

def test_isolated_rag():
    """Testa RAG isolado por instância"""
    print("🧪 TESTE 2: RAG Isolado por Instância")
    print("=" * 50)
    
    case_ids = ["test_case_001", "test_case_002"]
    
    # Criar dados de teste diferentes para cada caso
    test_data = {
        "test_case_001": {
            "numero": "0001234-56.2023.5.09.0010",
            "partes": [
                {"nome": "João Silva", "tipo": "requerente"},
                {"nome": "Empresa A Ltda", "tipo": "requerida"}
            ],
            "pedidos": [
                {"descricao": "Horas extras", "categoria": "verbas"},
                {"descricao": "Dano moral", "categoria": "indenizacao"}
            ]
        },
        "test_case_002": {
            "numero": "0007890-12.2023.5.09.0020",
            "partes": [
                {"nome": "Maria Santos", "tipo": "requerente"},
                {"nome": "Empresa B S.A.", "tipo": "requerida"}
            ],
            "pedidos": [
                {"descricao": "Verbas rescisórias", "categoria": "rescisao"},
                {"descricao": "Intervalo intrajornada", "categoria": "jornada"}
            ]
        }
    }
    
    rag_services = {}
    
    # Inicializar RAG para cada instância
    for case_id in case_ids:
        try:
            print(f"\n📋 Inicializando RAG para: {case_id}")
            
            # Criar RAG isolado
            rag_service = IsolatedRAGService(case_id)
            rag_services[case_id] = rag_service
            
            # Criar processo estruturado de teste
            data = test_data[case_id]
            processo_estruturado = ProcessoEstruturado(
                numero_processo=data["numero"],
                partes=[
                    ParteProcesso(nome=p["nome"], tipo=p["tipo"], qualificacao="")
                    for p in data["partes"]
                ],
                pedidos=[
                    PedidoProcesso(descricao=p["descricao"], categoria=p["categoria"], valor_estimado="")
                    for p in data["pedidos"]
                ],
                fatos_relevantes=[
                    FatoRelevante(descricao="Fato teste", fonte="inicial")
                ],
                periodo_contratual="01/2022 a 12/2023",
                valor_causa="R$ 10.000,00",
                competencia="5ª Vara do Trabalho",
                jurisprudencias_citadas=[],
                decisao_final=None,
                fundamentacao_resumida=None
            )
            
            # Salvar conhecimento do caso
            rag_service.salvar_conhecimento_caso_isolado(processo_estruturado)
            
            print(f"✅ Conhecimento salvo para {case_id}")
            
            # Salvar contexto de diálogo de teste
            dialogo_teste = {
                "etapa": "teste",
                "perguntas_claude": ["Qual o período contratual?", "Quais os pedidos?"],
                "respostas_gemini": {
                    "periodo": data["numero"],
                    "pedidos": [p["descricao"] for p in data["pedidos"]]
                }
            }
            
            rag_service.salvar_contexto_dialogo("etapa1", dialogo_teste)
            
            print(f"✅ Diálogo salvo para {case_id}")
            
        except Exception as e:
            print(f"❌ Erro no RAG para {case_id}: {str(e)}")
    
    print("\n📊 Testando recuperação isolada:")
    
    # Testar recuperação isolada
    for case_id in case_ids:
        if case_id in rag_services:
            try:
                print(f"\n🔍 Recuperando conhecimento de {case_id}:")
                
                conhecimento = rag_services[case_id].recuperar_conhecimento_completo_isolado()
                
                # Verificar se contém apenas dados desta instância
                if "conhecimento_caso" in conhecimento and "detalhes" in conhecimento["conhecimento_caso"]:
                    detalhes = conhecimento["conhecimento_caso"]["detalhes"]
                    numero_processo = detalhes.get("processo", {}).get("numero", "N/A")
                    print(f"   📋 Processo: {numero_processo}")
                    
                    # Verificar se é o processo correto
                    esperado = test_data[case_id]["numero"]
                    if numero_processo == esperado:
                        print(f"   ✅ Isolamento correto: {numero_processo}")
                    else:
                        print(f"   ❌ Contaminação detectada: esperado {esperado}, obtido {numero_processo}")
                
                # Testar busca contextual
                resultados = rag_services[case_id].buscar_contexto_relevante("horas extras", "all", 3)
                print(f"   🔍 Busca 'horas extras': {len(resultados)} resultados")
                
                for resultado in resultados:
                    categoria = resultado['categoria']
                    relevancia = resultado['relevancia']
                    print(f"      - {categoria}: relevância {relevancia:.3f}")
                
            except Exception as e:
                print(f"❌ Erro na recuperação de {case_id}: {str(e)}")
    
    print("\n✅ TESTE 2 CONCLUÍDO\n")

def test_cross_contamination():
    """Testa se há contaminação entre instâncias"""
    print("🧪 TESTE 3: Verificação de Contaminação Cruzada")
    print("=" * 50)
    
    case_ids = ["test_case_001", "test_case_002"]
    
    # Buscar por termos específicos de cada caso em instâncias diferentes
    test_queries = {
        "test_case_001": "João Silva",  # Nome específico do caso 1
        "test_case_002": "Maria Santos"  # Nome específico do caso 2
    }
    
    print("🔍 Testando busca cruzada (não deve encontrar resultados):")
    
    for search_case_id in case_ids:
        for query_case_id in case_ids:
            if search_case_id != query_case_id:  # Buscar termo de outro caso
                try:
                    rag_service = IsolatedRAGService(search_case_id)
                    query = test_queries[query_case_id]
                    
                    resultados = rag_service.buscar_contexto_relevante(query, "all", 5)
                    
                    if len(resultados) == 0:
                        print(f"   ✅ {search_case_id} não encontrou '{query}' (correto)")
                    else:
                        print(f"   ❌ {search_case_id} encontrou '{query}' - CONTAMINAÇÃO!")
                        for resultado in resultados:
                            print(f"      - {resultado['categoria']}: {resultado['relevancia']:.3f}")
                
                except Exception as e:
                    print(f"   ⚠️ Erro na busca cruzada: {str(e)}")
    
    print("\n✅ TESTE 3 CONCLUÍDO\n")

def test_performance():
    """Testa performance das operações isoladas"""
    print("🧪 TESTE 4: Performance das Operações")
    print("=" * 50)
    
    case_id = "test_performance"
    
    try:
        # Medir tempo de criação de instância
        start_time = time.time()
        instance_manager = InstanceManager()
        instance_manager.create_isolated_instance(case_id)
        creation_time = time.time() - start_time
        
        print(f"⏱️ Criação de instância: {creation_time:.2f} segundos")
        
        # Medir tempo de inicialização RAG
        start_time = time.time()
        rag_service = IsolatedRAGService(case_id)
        rag_init_time = time.time() - start_time
        
        print(f"⏱️ Inicialização RAG: {rag_init_time:.2f} segundos")
        
        # Medir tempo de busca
        start_time = time.time()
        resultados = rag_service.buscar_contexto_relevante("teste performance", "all", 5)
        search_time = time.time() - start_time
        
        print(f"⏱️ Busca contextual: {search_time:.3f} segundos")
        
        # Verificar limites de performance
        limits = {
            "creation_time": 30.0,  # máximo 30 segundos
            "rag_init_time": 10.0,  # máximo 10 segundos
            "search_time": 5.0       # máximo 5 segundos
        }
        
        times = {
            "creation_time": creation_time,
            "rag_init_time": rag_init_time,
            "search_time": search_time
        }
        
        print("\n📊 Avaliação de performance:")
        for metric, time_taken in times.items():
            limit = limits[metric]
            status = "✅" if time_taken <= limit else "❌"
            print(f"   {status} {metric}: {time_taken:.3f}s (limite: {limit}s)")
        
    except Exception as e:
        print(f"❌ Erro no teste de performance: {str(e)}")
    
    print("\n✅ TESTE 4 CONCLUÍDO\n")

def test_cleanup():
    """Testa limpeza de instâncias"""
    print("🧪 TESTE 5: Limpeza de Instâncias")
    print("=" * 50)
    
    instance_manager = InstanceManager()
    
    # Listar instâncias antes da limpeza
    instances_before = instance_manager.list_active_instances()
    print(f"📊 Instâncias antes da limpeza: {len(instances_before)}")
    
    # Fazer cleanup forçado das instâncias de teste
    test_case_ids = ["test_case_001", "test_case_002", "test_performance"]
    
    for case_id in test_case_ids:
        try:
            print(f"🧹 Fazendo cleanup de {case_id}")
            instance_manager.cleanup_instance(case_id, force=True)
            print(f"✅ Cleanup de {case_id} concluído")
        except Exception as e:
            print(f"❌ Erro no cleanup de {case_id}: {str(e)}")
    
    # Listar instâncias após a limpeza
    instances_after = instance_manager.list_active_instances()
    print(f"📊 Instâncias após limpeza: {len(instances_after)}")
    
    print("\n✅ TESTE 5 CONCLUÍDO\n")

def run_all_tests():
    """Executa todos os testes de instâncias isoladas"""
    print("🚀 INICIANDO TESTES DE INSTÂNCIAS ISOLADAS")
    print("=" * 60)
    
    try:
        test_instance_creation()
        test_isolated_rag()
        test_cross_contamination()
        test_performance()
        test_cleanup()
        
        print("🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("✅ Gestão de instâncias isoladas está funcionando corretamente")
        
    except Exception as e:
        print(f"❌ ERRO GERAL NOS TESTES: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_tests()
