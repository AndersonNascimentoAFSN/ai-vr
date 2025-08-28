#!/usr/bin/env python3
"""
Demonstração completa do sistema de banco de dados VR/VA
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime

def demo_sistema_completo():
    """Demonstração completa do sistema"""
    print("🎯 DEMONSTRAÇÃO COMPLETA - SISTEMA DE BANCO DE DADOS VR/VA")
    print("=" * 80)
    
    # Verificar se o banco existe
    db_path = "ai_vr/db/vr_database.db"
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        print("💡 Execute primeiro: python3 create_database.py")
        return
    # Conectar ao banco
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("✅ Conectado ao banco de dados")
    
    # 1. Informações básicas
    print("\n📊 INFORMAÇÕES BÁSICAS")
    print("-" * 40)
    
    # Tamanho do banco
    file_size = os.path.getsize(db_path)
    print(f"📁 Arquivo: {db_path}")
    print(f"📏 Tamanho: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    
    # Contagem de registros
    tables = ['colaboradores', 'sindicatos', 'estados', 'cargos', 'empresas', 
              'ferias', 'afastamentos', 'desligamentos', 'admissoes', 'exclusoes', 'dias_uteis']
    
    total_records = 0
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        total_records += count
        print(f"  {table}: {count:,} registros")
        
    print(f"📈 Total de registros: {total_records:,}")
    
    # 2. Análise de dados
    print("\n📈 ANÁLISE DE DADOS")
    print("-" * 40)
    
    # Distribuição por sindicato
    query = """
    SELECT 
        s.nome_abreviado as sindicato,
        COUNT(c.id) as total_colaboradores,
        e.valor_vr_diario,
        du.dias_uteis
    FROM colaboradores c
    JOIN sindicatos s ON c.sindicato_id = s.id
    JOIN estados e ON s.estado_id = e.id
    JOIN dias_uteis du ON s.id = du.sindicato_id
    WHERE du.periodo_inicio = '2025-04-15' AND du.periodo_fim = '2025-05-15'
    GROUP BY s.id, s.nome_abreviado, e.valor_vr_diario, du.dias_uteis
    ORDER BY total_colaboradores DESC
    """
    
    df_sindicatos = pd.read_sql_query(query, conn)
    print("📊 Distribuição por Sindicato:")
    print(df_sindicatos.to_string(index=False))
    
    # 3. Cálculos de VR
    print("\n💰 CÁLCULOS DE VR")
    print("-" * 40)
    
    # Exemplo de cálculo para um colaborador
    query = """
    SELECT 
        c.matricula,
        car.titulo as cargo,
        s.nome_abreviado as sindicato,
        e.valor_vr_diario,
        du.dias_uteis as dias_uteis_sindicato,
        COALESCE(f.dias_ferias, 0) as dias_ferias,
        (du.dias_uteis - COALESCE(f.dias_ferias, 0)) as dias_vr_calculados,
        (du.dias_uteis - COALESCE(f.dias_ferias, 0)) * e.valor_vr_diario as valor_total,
        ((du.dias_uteis - COALESCE(f.dias_ferias, 0)) * e.valor_vr_diario) * 0.8 as custo_empresa,
        ((du.dias_uteis - COALESCE(f.dias_ferias, 0)) * e.valor_vr_diario) * 0.2 as desconto_colaborador
    FROM colaboradores c
    JOIN cargos car ON c.cargo_id = car.id
    JOIN sindicatos s ON c.sindicato_id = s.id
    JOIN estados e ON s.estado_id = e.id
    JOIN dias_uteis du ON s.id = du.sindicato_id
    LEFT JOIN ferias f ON c.id = f.colaborador_id
    WHERE c.id NOT IN (SELECT colaborador_id FROM exclusoes)
    AND c.situacao NOT IN ('Auxílio Doença', 'Licença Maternidade', 'Atestado')
    AND car.categoria = 'FUNCIONARIO'
    AND du.periodo_inicio = '2025-04-15' AND du.periodo_fim = '2025-05-15'
    LIMIT 3
    """
    
    df_calculos = pd.read_sql_query(query, conn)
    print("💡 Exemplos de Cálculo de VR:")
    print(df_calculos.to_string(index=False))
    
    # 4. Resumo financeiro
    print("\n💵 RESUMO FINANCEIRO")
    print("-" * 40)
    
    # Calcular totais
    query = """
    SELECT 
        COUNT(*) as total_colaboradores_elegiveis,
        SUM((du.dias_uteis - COALESCE(f.dias_ferias, 0)) * e.valor_vr_diario) as valor_total_vr,
        SUM(((du.dias_uteis - COALESCE(f.dias_ferias, 0)) * e.valor_vr_diario) * 0.8) as custo_total_empresa,
        SUM(((du.dias_uteis - COALESCE(f.dias_ferias, 0)) * e.valor_vr_diario) * 0.2) as desconto_total_colaborador
    FROM colaboradores c
    JOIN cargos car ON c.cargo_id = car.id
    JOIN sindicatos s ON c.sindicato_id = s.id
    JOIN estados e ON s.estado_id = e.id
    JOIN dias_uteis du ON s.id = du.sindicato_id
    LEFT JOIN ferias f ON c.id = f.colaborador_id
    WHERE c.id NOT IN (SELECT colaborador_id FROM exclusoes)
    AND c.situacao NOT IN ('Auxílio Doença', 'Licença Maternidade', 'Atestado')
    AND car.categoria = 'FUNCIONARIO'
    AND du.periodo_inicio = '2025-04-15' AND du.periodo_fim = '2025-05-15'
    """
    
    result = cursor.execute(query).fetchone()
    total_colab, valor_total, custo_empresa, desconto_colab = result
    
    print(f"👥 Colaboradores elegíveis: {total_colab:,}")
    print(f"💰 Valor total VR: R$ {valor_total:,.2f}")
    print(f"🏢 Custo empresa (80%): R$ {custo_empresa:,.2f}")
    print(f"👤 Desconto colaborador (20%): R$ {desconto_colab:,.2f}")
    
    # 5. Validações
    print("\n✅ VALIDAÇÕES")
    print("-" * 40)
    
    # Verificar integridade
    validacoes = [
        ("Colaboradores sem matrícula duplicada", 
         "SELECT COUNT(*) FROM colaboradores WHERE matricula IN (SELECT matricula FROM colaboradores GROUP BY matricula HAVING COUNT(*) > 1)"),
        ("Colaboradores sem sindicato", 
         "SELECT COUNT(*) FROM colaboradores WHERE sindicato_id IS NULL"),
        ("Colaboradores sem cargo", 
         "SELECT COUNT(*) FROM colaboradores WHERE cargo_id IS NULL"),
        ("Valores de VR válidos", 
         "SELECT COUNT(*) FROM estados WHERE valor_vr_diario <= 0 OR valor_vr_diario IS NULL"),
        ("Dias úteis válidos", 
         "SELECT COUNT(*) FROM dias_uteis WHERE dias_uteis <= 0 OR dias_uteis > 31")
    ]
    
    for descricao, query in validacoes:
        result = cursor.execute(query).fetchone()
        count = result[0]
        status = "✅ OK" if count == 0 else f"❌ {count} problemas"
        print(f"{descricao}: {status}")
    
    # 6. Performance
    print("\n⚡ PERFORMANCE")
    print("-" * 40)
    
    # Testar consulta complexa
    start_time = datetime.now()
    
    query = """
    SELECT COUNT(*) FROM colaboradores c
    JOIN cargos car ON c.cargo_id = car.id
    JOIN sindicatos s ON c.sindicato_id = s.id
    JOIN estados e ON s.estado_id = e.id
    WHERE c.id NOT IN (SELECT colaborador_id FROM exclusoes)
    AND c.situacao NOT IN ('Auxílio Doença', 'Licença Maternidade', 'Atestado')
    AND car.categoria = 'FUNCIONARIO'
    """
    
    cursor.execute(query)
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds() * 1000
    
    print(f"⏱️ Tempo de consulta complexa: {execution_time:.2f} ms")
    print(f"📊 Registros processados: {cursor.fetchone()[0]:,}")
    
    # 7. Próximos passos
    print("\n🚀 PRÓXIMOS PASSOS")
    print("-" * 40)
    
    print("1. 📊 Implementar algoritmo de cálculo completo")
    print("2. 🖥️ Criar interface de usuário")
    print("3. 📈 Gerar relatórios automáticos")
    print("4. 🔄 Implementar atualização automática de dados")
    print("5. 📋 Criar dashboard de monitoramento")
    print("6. 🔒 Implementar sistema de auditoria")
    
    # Fechar conexão
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    print("\n💡 Para mais informações:")
    print("  - Consulte: README_banco_dados.md")
    print("  - Execute: python3 database_connect.py")
    print("  - Backup: python3 database_backup.py --backup")

if __name__ == "__main__":
    demo_sistema_completo()
