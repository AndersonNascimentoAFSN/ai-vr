#!/usr/bin/env python3
import sqlite3
import pandas as pd
from database_populate import VRDatabase

class VRQueries:
    def __init__(self, db_path=":memory:"):
        """Inicializa o sistema de consultas"""
        self.db = VRDatabase(db_path)
        self.db.populate_all()
        
    def query_1_colaboradores_elegiveis(self):
        """Consulta 1: Colaboradores elegíveis para VR"""
        print("=" * 60)
        print("CONSULTA 1: COLABORADORES ELEGÍVEIS PARA VR")
        print("=" * 60)
        
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
        LIMIT 10
        """
        
        df = pd.read_sql_query(query, self.db.conn)
        print(f"Total de colaboradores elegíveis: {len(df)}")
        print(df.to_string(index=False))
        
    def query_2_colaboradores_excluidos(self):
        """Consulta 2: Colaboradores excluídos do VR"""
        print("\n" + "=" * 60)
        print("CONSULTA 2: COLABORADORES EXCLUÍDOS DO VR")
        print("=" * 60)
        
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
        
        df = pd.read_sql_query(query, self.db.conn)
        print(f"Total de colaboradores excluídos: {len(df)}")
        print(df.to_string(index=False))
        
    def query_3_colaboradores_ferias(self):
        """Consulta 3: Colaboradores em férias"""
        print("\n" + "=" * 60)
        print("CONSULTA 3: COLABORADORES EM FÉRIAS")
        print("=" * 60)
        
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
        LIMIT 10
        """
        
        df = pd.read_sql_query(query, self.db.conn)
        print(f"Total de colaboradores em férias: {len(df)}")
        print(df.to_string(index=False))
        
    def query_4_colaboradores_desligados(self):
        """Consulta 4: Colaboradores desligados"""
        print("\n" + "=" * 60)
        print("CONSULTA 4: COLABORADORES DESLIGADOS")
        print("=" * 60)
        
        query = """
        SELECT 
            c.matricula,
            car.titulo as cargo,
            d.data_desligamento,
            d.comunicado_ok,
            CASE 
                WHEN d.comunicado_ok = 1 THEN 'Recebe VR proporcional'
                ELSE 'Não recebe VR'
            END as regra_vr
        FROM colaboradores c
        JOIN cargos car ON c.cargo_id = car.id
        JOIN desligamentos d ON c.id = d.colaborador_id
        ORDER BY d.data_desligamento
        LIMIT 10
        """
        
        df = pd.read_sql_query(query, self.db.conn)
        print(f"Total de colaboradores desligados: {len(df)}")
        print(df.to_string(index=False))
        
    def query_5_distribuicao_por_sindicato(self):
        """Consulta 5: Distribuição de colaboradores por sindicato"""
        print("\n" + "=" * 60)
        print("CONSULTA 5: DISTRIBUIÇÃO POR SINDICATO")
        print("=" * 60)
        
        query = """
        SELECT 
            s.nome_abreviado as sindicato,
            e.nome as estado,
            e.valor_vr_diario,
            du.dias_uteis,
            COUNT(c.id) as total_colaboradores,
            SUM(CASE WHEN c.situacao = 'Trabalhando' THEN 1 ELSE 0 END) as trabalhando,
            SUM(CASE WHEN c.situacao = 'Férias' THEN 1 ELSE 0 END) as ferias
        FROM colaboradores c
        JOIN sindicatos s ON c.sindicato_id = s.id
        JOIN estados e ON s.estado_id = e.id
        JOIN dias_uteis du ON s.id = du.sindicato_id
        WHERE du.periodo_inicio = '2025-04-15' AND du.periodo_fim = '2025-05-15'
        GROUP BY s.id, s.nome_abreviado, e.nome, e.valor_vr_diario, du.dias_uteis
        ORDER BY total_colaboradores DESC
        """
        
        df = pd.read_sql_query(query, self.db.conn)
        print(df.to_string(index=False))
        
    def query_6_colaboradores_admitidos_abril(self):
        """Consulta 6: Colaboradores admitidos em abril"""
        print("\n" + "=" * 60)
        print("CONSULTA 6: COLABORADORES ADMITIDOS EM ABRIL")
        print("=" * 60)
        
        query = """
        SELECT 
            c.matricula,
            car.titulo as cargo,
            a.data_admissao,
            s.nome_abreviado as sindicato,
            e.valor_vr_diario
        FROM colaboradores c
        JOIN cargos car ON c.cargo_id = car.id
        JOIN admissoes a ON c.id = a.colaborador_id
        JOIN sindicatos s ON c.sindicato_id = s.id
        JOIN estados e ON s.estado_id = e.id
        WHERE a.data_admissao >= '2025-04-01' AND a.data_admissao <= '2025-04-30'
        ORDER BY a.data_admissao
        LIMIT 10
        """
        
        df = pd.read_sql_query(query, self.db.conn)
        print(f"Total de colaboradores admitidos em abril: {len(df)}")
        print(df.to_string(index=False))
        
    def query_7_resumo_geral(self):
        """Consulta 7: Resumo geral do sistema"""
        print("\n" + "=" * 60)
        print("CONSULTA 7: RESUMO GERAL DO SISTEMA")
        print("=" * 60)
        
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
            ("Colaboradores desligados", "SELECT COUNT(*) FROM desligamentos"),
            ("Colaboradores admitidos em abril", "SELECT COUNT(*) FROM admissoes"),
            ("Estagiários", "SELECT COUNT(*) FROM exclusoes WHERE tipo_exclusao = 'ESTAGIARIO'"),
            ("Aprendizes", "SELECT COUNT(*) FROM exclusoes WHERE tipo_exclusao = 'APRENDIZ'"),
            ("Colaboradores no exterior", "SELECT COUNT(*) FROM exclusoes WHERE tipo_exclusao = 'EXTERIOR'")
        ]
        
        for descricao, query in queries:
            result = self.db.cursor.execute(query).fetchone()
            print(f"{descricao}: {result[0]}")
            
    def query_8_exemplo_calculo_vr(self):
        """Consulta 8: Exemplo de cálculo de VR para um colaborador"""
        print("\n" + "=" * 60)
        print("CONSULTA 8: EXEMPLO DE CÁLCULO DE VR")
        print("=" * 60)
        
        # Pegar um colaborador elegível como exemplo
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
        LIMIT 5
        """
        
        df = pd.read_sql_query(query, self.db.conn)
        print("Exemplos de cálculo de VR:")
        print(df.to_string(index=False))
        
    def run_all_queries(self):
        """Executa todas as consultas de exemplo"""
        print("🔍 EXECUTANDO CONSULTAS DE VALIDAÇÃO DO BANCO DE DADOS")
        print("=" * 80)
        
        self.query_1_colaboradores_elegiveis()
        self.query_2_colaboradores_excluidos()
        self.query_3_colaboradores_ferias()
        self.query_4_colaboradores_desligados()
        self.query_5_distribuicao_por_sindicato()
        self.query_6_colaboradores_admitidos_abril()
        self.query_7_resumo_geral()
        self.query_8_exemplo_calculo_vr()
        
        print("\n" + "=" * 80)
        print("✅ TODAS AS CONSULTAS EXECUTADAS COM SUCESSO!")
        print("=" * 80)
        
    def close(self):
        """Fecha a conexão com o banco"""
        self.db.close()

if __name__ == "__main__":
    # Executar todas as consultas
    queries = VRQueries()
    queries.run_all_queries()
    queries.close()
