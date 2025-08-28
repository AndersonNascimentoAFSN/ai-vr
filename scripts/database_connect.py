#!/usr/bin/env python3
"""
Script para conectar e consultar o banco de dados SQLite3 do sistema de VR/VA
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime

class VRDatabaseConnection:
    def __init__(self, db_path="vr_database.db"):
        """Inicializa a conexão com o banco de dados"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Conecta ao banco de dados"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Banco de dados não encontrado: {self.db_path}")
            
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Ativar foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        print(f"✅ Conectado ao banco: {self.db_path}")
        
    def get_database_info(self):
        """Retorna informações sobre o banco de dados"""
        print("📊 INFORMAÇÕES DO BANCO DE DADOS")
        print("=" * 50)
        
        # Tamanho do arquivo
        file_size = os.path.getsize(self.db_path)
        print(f"📁 Arquivo: {self.db_path}")
        print(f"📏 Tamanho: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        
        # Data de modificação
        mod_time = os.path.getmtime(self.db_path)
        mod_date = datetime.fromtimestamp(mod_time)
        print(f"📅 Última modificação: {mod_date.strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Listar tabelas
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in self.cursor.fetchall()]
        print(f"📋 Tabelas: {len(tables)}")
        for table in sorted(tables):
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            print(f"  - {table}: {count:,} registros")
            
    def query_colaboradores_elegiveis(self, limit=10):
        """Consulta colaboradores elegíveis para VR"""
        print(f"\n👥 COLABORADORES ELEGÍVEIS PARA VR (limit: {limit})")
        print("=" * 70)
        
        query = """
        SELECT 
            c.matricula,
            c.situacao,
            car.titulo as cargo,
            car.categoria as categoria_cargo,
            s.nome_abreviado as sindicato,
            e.nome as estado,
            e.valor_vr_diario
        FROM colaboradores c
        JOIN cargos car ON c.cargo_id = car.id
        JOIN sindicatos s ON c.sindicato_id = s.id
        JOIN estados e ON s.estado_id = e.id
        WHERE c.id NOT IN (SELECT colaborador_id FROM exclusoes)
        AND c.situacao NOT IN ('Auxílio Doença', 'Licença Maternidade', 'Atestado')
        AND car.categoria = 'FUNCIONARIO'
        ORDER BY c.matricula
        LIMIT ?
        """
        
        df = pd.read_sql_query(query, self.conn, params=(limit,))
        print(f"Total de colaboradores elegíveis: {len(df)}")
        print(df.to_string(index=False))
        
    def query_resumo_por_sindicato(self):
        """Consulta resumo por sindicato"""
        print(f"\n📊 RESUMO POR SINDICATO")
        print("=" * 70)
        
        query = """
        SELECT 
            s.nome_abreviado as sindicato,
            e.nome as estado,
            e.valor_vr_diario,
            du.dias_uteis,
            COUNT(c.id) as total_colaboradores,
            SUM(CASE WHEN c.situacao = 'Trabalhando' THEN 1 ELSE 0 END) as trabalhando,
            SUM(CASE WHEN c.situacao = 'Férias' THEN 1 ELSE 0 END) as ferias,
            SUM(CASE WHEN c.situacao IN ('Auxílio Doença', 'Licença Maternidade', 'Atestado') THEN 1 ELSE 0 END) as afastados
        FROM colaboradores c
        JOIN sindicatos s ON c.sindicato_id = s.id
        JOIN estados e ON s.estado_id = e.id
        JOIN dias_uteis du ON s.id = du.sindicato_id
        WHERE du.periodo_inicio = '2025-04-15' AND du.periodo_fim = '2025-05-15'
        GROUP BY s.id, s.nome_abreviado, e.nome, e.valor_vr_diario, du.dias_uteis
        ORDER BY total_colaboradores DESC
        """
        
        df = pd.read_sql_query(query, self.conn)
        print(df.to_string(index=False))
        
    def query_colaboradores_ferias(self, limit=10):
        """Consulta colaboradores em férias"""
        print(f"\n🏖️ COLABORADORES EM FÉRIAS (limit: {limit})")
        print("=" * 70)
        
        query = """
        SELECT 
            c.matricula,
            car.titulo as cargo,
            s.nome_abreviado as sindicato,
            f.dias_ferias,
            f.periodo_inicio,
            f.periodo_fim
        FROM colaboradores c
        JOIN cargos car ON c.cargo_id = car.id
        JOIN sindicatos s ON c.sindicato_id = s.id
        JOIN ferias f ON c.id = f.colaborador_id
        ORDER BY f.dias_ferias DESC
        LIMIT ?
        """
        
        df = pd.read_sql_query(query, self.conn, params=(limit,))
        print(f"Total de colaboradores em férias: {len(df)}")
        print(df.to_string(index=False))
        
    def query_colaboradores_excluidos(self):
        """Consulta colaboradores excluídos"""
        print(f"\n❌ COLABORADORES EXCLUÍDOS DO VR")
        print("=" * 70)
        
        query = """
        SELECT 
            c.matricula,
            car.titulo as cargo,
            car.categoria as categoria_cargo,
            e.tipo_exclusao,
            e.valor_especifico,
            e.observacoes
        FROM colaboradores c
        JOIN cargos car ON c.cargo_id = car.id
        JOIN exclusoes e ON c.id = e.colaborador_id
        ORDER BY e.tipo_exclusao, c.matricula
        """
        
        df = pd.read_sql_query(query, self.conn)
        print(f"Total de colaboradores excluídos: {len(df)}")
        print(df.to_string(index=False))
        
    def query_exemplo_calculo_vr(self, limit=5):
        """Consulta exemplo de cálculo de VR"""
        print(f"\n💰 EXEMPLO DE CÁLCULO DE VR (limit: {limit})")
        print("=" * 70)
        
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
        LIMIT ?
        """
        
        df = pd.read_sql_query(query, self.conn, params=(limit,))
        print("Exemplos de cálculo de VR:")
        print(df.to_string(index=False))
        
    def query_estatisticas_gerais(self):
        """Consulta estatísticas gerais"""
        print(f"\n📈 ESTATÍSTICAS GERAIS")
        print("=" * 50)
        
        queries = [
            ("Total de colaboradores", "SELECT COUNT(*) FROM colaboradores"),
            ("Colaboradores elegíveis", """
                SELECT COUNT(*) FROM colaboradores c
                JOIN cargos car ON c.cargo_id = car.id
                WHERE c.id NOT IN (SELECT colaborador_id FROM exclusoes)
                AND c.situacao NOT IN ('Auxílio Doença', 'Licença Maternidade', 'Atestado')
                AND car.categoria = 'FUNCIONARIO'
            """),
            ("Colaboradores excluídos", "SELECT COUNT(*) FROM exclusoes"),
            ("Colaboradores em férias", "SELECT COUNT(*) FROM ferias"),
            ("Colaboradores afastados", "SELECT COUNT(*) FROM afastamentos"),
            ("Colaboradores desligados", "SELECT COUNT(*) FROM desligamentos"),
            ("Colaboradores admitidos em abril", "SELECT COUNT(*) FROM admissoes"),
            ("Estagiários", "SELECT COUNT(*) FROM exclusoes WHERE tipo_exclusao = 'ESTAGIARIO'"),
            ("Aprendizes", "SELECT COUNT(*) FROM exclusoes WHERE tipo_exclusao = 'APRENDIZ'"),
            ("Colaboradores no exterior", "SELECT COUNT(*) FROM exclusoes WHERE tipo_exclusao = 'EXTERIOR'")
        ]
        
        for descricao, query in queries:
            result = self.cursor.execute(query).fetchone()
            print(f"{descricao}: {result[0]:,}")
            
    def run_all_queries(self):
        """Executa todas as consultas de exemplo"""
        print("🔍 CONSULTANDO BANCO DE DADOS VR/VA")
        print("=" * 80)
        
        self.get_database_info()
        self.query_estatisticas_gerais()
        self.query_resumo_por_sindicato()
        self.query_colaboradores_elegiveis(5)
        self.query_colaboradores_ferias(5)
        self.query_colaboradores_excluidos()
        self.query_exemplo_calculo_vr(3)
        
        print("\n" + "=" * 80)
        print("✅ TODAS AS CONSULTAS EXECUTADAS COM SUCESSO!")
        print("=" * 80)
        
    def close(self):
        """Fecha a conexão com o banco"""
        if self.conn:
            self.conn.close()
            print(f"🔒 Conexão fechada: {self.db_path}")

def main():
    """Função principal"""
    print("🗄️ CONSULTA AO BANCO DE DADOS VR/VA")
    print("=" * 60)
    
    # Conectar ao banco
    db_conn = VRDatabaseConnection("vr_database.db")
    
    try:
        db_conn.connect()
        db_conn.run_all_queries()
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("💡 Execute primeiro: python3 create_database.py")
    except Exception as e:
        print(f"❌ Erro ao consultar banco: {e}")
    finally:
        db_conn.close()

if __name__ == "__main__":
    main()
