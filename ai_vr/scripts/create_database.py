#!/usr/bin/env python3
"""
Script para criar e popular o banco de dados SQLite3 do sistema de VR/VA
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime, date
from pathlib import Path

class VRDatabaseManager:
    def __init__(self, db_path="ai_vr/db/vr_database.db"):
        """Inicializa o gerenciador do banco de dados"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def create_database(self):
        """Cria o banco de dados SQLite3"""
        print(f"🗄️ Criando banco de dados: {self.db_path}")
        
        # Remover banco existente se houver
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            print(f"🗑️ Banco anterior removido: {self.db_path}")
        
        # Conectar ao banco
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Ativar foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        print("✅ Banco de dados criado com sucesso!")
        
    def create_schema(self):
        """Cria o schema do banco de dados"""
        print("📋 Criando schema do banco...")
        
    with open('ai_vr/db/database_schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
        
        self.cursor.executescript(schema)
        self.conn.commit()
        print("✅ Schema criado com sucesso")
        
    def populate_estados(self):
        """Popula a tabela de estados com valores de VR"""
        print("🏛️ Populando estados...")
        
        estados_data = [
            (1, 'Paraná', 'PR', 35.00),
            (2, 'Rio de Janeiro', 'RJ', 35.00),
            (3, 'Rio Grande do Sul', 'RS', 35.00),
            (4, 'São Paulo', 'SP', 37.50)
        ]
        
        self.cursor.executemany(
            "INSERT INTO estados (id, nome, uf, valor_vr_diario) VALUES (?, ?, ?, ?)",
            estados_data
        )
        self.conn.commit()
        print("✅ Estados populados")
        
    def populate_sindicatos(self):
        """Popula a tabela de sindicatos"""
        print("🏢 Populando sindicatos...")
        
        sindicatos_data = [
            (1, 'SITEPD PR - SIND DOS TRAB EM EMPR PRIVADAS DE PROC DE DADOS DE CURITIBA E REGIAO METROPOLITANA', 'SITEPD PR', 1),
            (2, 'SINDPPD RS - SINDICATO DOS TRAB. EM PROC. DE DADOS RIO GRANDE DO SUL', 'SINDPPD RS', 3),
            (3, 'SINDPD SP - SIND.TRAB.EM PROC DADOS E EMPR.EMPRESAS PROC DADOS ESTADO DE SP.', 'SINDPD SP', 4),
            (4, 'SINDPD RJ - SINDICATO PROFISSIONAIS DE PROC DADOS DO RIO DE JANEIRO', 'SINDPD RJ', 2)
        ]
        
        self.cursor.executemany(
            "INSERT INTO sindicatos (id, nome_completo, nome_abreviado, estado_id) VALUES (?, ?, ?, ?)",
            sindicatos_data
        )
        self.conn.commit()
        print("✅ Sindicatos populados")
        
    def populate_empresas(self):
        """Popula a tabela de empresas"""
        print("🏭 Populando empresas...")
        
        empresas_data = [(1, 'Empresa Principal', '00.000.000/0001-00')]
        
        self.cursor.executemany(
            "INSERT INTO empresas (id, nome, cnpj) VALUES (?, ?, ?)",
            empresas_data
        )
        self.conn.commit()
        print("✅ Empresas populadas")
        
    def populate_cargos(self):
        """Popula a tabela de cargos baseado nos dados das planilhas"""
        print("👔 Populando cargos...")
        
        # Ler cargos únicos de todas as planilhas
        cargos_set = set()
        
        # ATIVOS.xlsx
        ativos = pd.read_excel('data/ATIVOS.xlsx')
        cargos_set.update(ativos['TITULO DO CARGO'].dropna().unique())
        
        # ADMISSÃO ABRIL.xlsx
        admissoes = pd.read_excel('data/ADMISSÃO ABRIL.xlsx')
        cargos_set.update(admissoes['Cargo'].dropna().unique())
        
        # ESTÁGIO.xlsx
        estagiarios = pd.read_excel('data/ESTÁGIO.xlsx')
        cargos_set.update(estagiarios['TITULO DO CARGO'].dropna().unique())
        
        # APRENDIZ.xlsx
        aprendizes = pd.read_excel('data/APRENDIZ.xlsx')
        cargos_set.update(aprendizes['TITULO DO CARGO'].dropna().unique())
        
        # Converter para lista e categorizar
        cargos_data = []
        cargo_id = 1
        
        for cargo in sorted(cargos_set):
            categoria = 'FUNCIONARIO'
            if 'ESTAGIARIO' in str(cargo).upper():
                categoria = 'ESTAGIARIO'
            elif 'APRENDIZ' in str(cargo).upper():
                categoria = 'APRENDIZ'
            elif any(palavra in str(cargo).upper() for palavra in ['DIRETOR', 'DIRETORA', 'PRESIDENTE', 'CEO']):
                categoria = 'DIRETOR'
                
            cargos_data.append((cargo_id, cargo, categoria))
            cargo_id += 1
            
        self.cursor.executemany(
            "INSERT INTO cargos (id, titulo, categoria) VALUES (?, ?, ?)",
            cargos_data
        )
        self.conn.commit()
        print(f"✅ {len(cargos_data)} cargos populados")
        
    def populate_colaboradores(self):
        """Popula a tabela de colaboradores"""
        print("👥 Populando colaboradores...")
        
        # Ler dados da planilha ATIVOS.xlsx
        ativos = pd.read_excel('data/ATIVOS.xlsx')
        
        # Obter mapeamentos
        sindicatos_map = self._get_sindicatos_map()
        cargos_map = self._get_cargos_map()
        
        colaboradores_data = []
        
        for _, row in ativos.iterrows():
            matricula = int(row['MATRICULA'])
            cargo = row['TITULO DO CARGO']
            situacao = row['DESC. SITUACAO']
            sindicato = row['Sindicato']
            
            # Obter IDs
            cargo_id = cargos_map.get(cargo, 1)  # Default para primeiro cargo
            sindicato_id = sindicatos_map.get(sindicato, 1)  # Default para primeiro sindicato
            
            colaboradores_data.append((
                matricula,  # matricula
                None,  # nome (não disponível na planilha)
                1,  # empresa_id (sempre 1)
                cargo_id,
                sindicato_id,
                situacao,
                None,  # data_admissao
                None   # data_desligamento
            ))
            
        self.cursor.executemany(
            """INSERT INTO colaboradores 
               (matricula, nome, empresa_id, cargo_id, sindicato_id, situacao, data_admissao, data_desligamento) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            colaboradores_data
        )
        self.conn.commit()
        print(f"✅ {len(colaboradores_data)} colaboradores ativos populados")
        
    def populate_ferias(self):
        """Popula a tabela de férias"""
        print("🏖️ Populando férias...")
        
        ferias = pd.read_excel('data/FÉRIAS.xlsx')
        
        ferias_data = []
        for _, row in ferias.iterrows():
            matricula = int(row['MATRICULA'])
            dias_ferias = int(row['DIAS DE FÉRIAS'])
            
            # Obter colaborador_id
            self.cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (matricula,))
            result = self.cursor.fetchone()
            if result:
                colaborador_id = result[0]
                ferias_data.append((
                    colaborador_id,
                    date(2025, 4, 15),  # periodo_inicio (assumindo período de 15/04 a 15/05)
                    date(2025, 5, 15),  # periodo_fim
                    dias_ferias
                ))
                
        self.cursor.executemany(
            "INSERT INTO ferias (colaborador_id, periodo_inicio, periodo_fim, dias_ferias) VALUES (?, ?, ?, ?)",
            ferias_data
        )
        self.conn.commit()
        print(f"✅ {len(ferias_data)} registros de férias populados")
        
    def populate_afastamentos(self):
        """Popula a tabela de afastamentos"""
        print("🏥 Populando afastamentos...")
        
        afastamentos = pd.read_excel('data/AFASTAMENTOS.xlsx')
        
        afastamentos_data = []
        for _, row in afastamentos.iterrows():
            matricula = int(row['MATRICULA'])
            tipo_afastamento = row['DESC. SITUACAO']
            
            # Obter colaborador_id
            self.cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (matricula,))
            result = self.cursor.fetchone()
            if result:
                colaborador_id = result[0]
                afastamentos_data.append((
                    colaborador_id,
                    tipo_afastamento,
                    date(2025, 4, 1),  # data_inicio (assumindo início do mês)
                    None,  # data_fim
                    None   # observacoes
                ))
                
        self.cursor.executemany(
            "INSERT INTO afastamentos (colaborador_id, tipo_afastamento, data_inicio, data_fim, observacoes) VALUES (?, ?, ?, ?, ?)",
            afastamentos_data
        )
        self.conn.commit()
        print(f"✅ {len(afastamentos_data)} registros de afastamentos populados")
        
    def populate_desligamentos(self):
        """Popula a tabela de desligamentos"""
        print("👋 Populando desligamentos...")
        
        desligados = pd.read_excel('data/DESLIGADOS.xlsx')
        
        desligamentos_data = []
        for _, row in desligados.iterrows():
            matricula = int(row['MATRICULA '])  # Note o espaço
            data_demissao = pd.to_datetime(row['DATA DEMISSÃO']).date()
            comunicado_ok = row['COMUNICADO DE DESLIGAMENTO'] == 'OK'
            
            # Obter colaborador_id
            self.cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (matricula,))
            result = self.cursor.fetchone()
            if result:
                colaborador_id = result[0]
                desligamentos_data.append((
                    colaborador_id,
                    data_demissao,
                    comunicado_ok,
                    None  # observacoes
                ))
                
        self.cursor.executemany(
            "INSERT INTO desligamentos (colaborador_id, data_desligamento, comunicado_ok, observacoes) VALUES (?, ?, ?, ?)",
            desligamentos_data
        )
        self.conn.commit()
        print(f"✅ {len(desligamentos_data)} registros de desligamentos populados")
        
    def populate_admissoes(self):
        """Popula a tabela de admissões"""
        print("🎉 Populando admissões...")
        
        admissoes = pd.read_excel('data/ADMISSÃO ABRIL.xlsx')
        cargos_map = self._get_cargos_map()
        
        admissoes_data = []
        for _, row in admissoes.iterrows():
            matricula = int(row['MATRICULA'])
            data_admissao = pd.to_datetime(row['Admissão']).date()
            cargo = row['Cargo']
            
            # Obter colaborador_id e cargo_id
            self.cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (matricula,))
            result = self.cursor.fetchone()
            if result:
                colaborador_id = result[0]
                cargo_id = cargos_map.get(cargo, 1)
                
                admissoes_data.append((
                    colaborador_id,
                    data_admissao,
                    cargo_id,
                    None  # observacoes
                ))
                
        self.cursor.executemany(
            "INSERT INTO admissoes (colaborador_id, data_admissao, cargo_id, observacoes) VALUES (?, ?, ?, ?)",
            admissoes_data
        )
        self.conn.commit()
        print(f"✅ {len(admissoes_data)} registros de admissões populados")
        
        # Sincronizar data_admissao na tabela de colaboradores quando estiver nula
        self.cursor.execute(
            """
            UPDATE colaboradores
            SET data_admissao = (
                SELECT a.data_admissao FROM admissoes a
                WHERE a.colaborador_id = colaboradores.id
            )
            WHERE data_admissao IS NULL
            AND EXISTS (
                SELECT 1 FROM admissoes a WHERE a.colaborador_id = colaboradores.id
            )
            """
        )
        self.conn.commit()
        print("🔁 Sincronizada data_admissao em colaboradores a partir de admissoes")
        
    def populate_exclusoes(self):
        """Popula a tabela de exclusões (estagiários, aprendizes, exterior)"""
        print("❌ Populando exclusões...")
        
        exclusoes_data = []
        
        # Estagiários
        estagiarios = pd.read_excel('data/ESTÁGIO.xlsx')
        for _, row in estagiarios.iterrows():
            matricula = int(row['MATRICULA'])
            self.cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (matricula,))
            result = self.cursor.fetchone()
            if result:
                exclusoes_data.append((result[0], 'ESTAGIARIO', None, None))
                
        # Aprendizes
        aprendizes = pd.read_excel('data/APRENDIZ.xlsx')
        for _, row in aprendizes.iterrows():
            matricula = int(row['MATRICULA'])
            self.cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (matricula,))
            result = self.cursor.fetchone()
            if result:
                exclusoes_data.append((result[0], 'APRENDIZ', None, None))
                
        # Exterior
        exterior = pd.read_excel('data/EXTERIOR.xlsx')
        for _, row in exterior.iterrows():
            cadastro = int(row['Cadastro'])
            valor = row['Valor']
            observacoes = row['Unnamed: 2']
            
            self.cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (cadastro,))
            result = self.cursor.fetchone()
            if result:
                exclusoes_data.append((result[0], 'EXTERIOR', valor, observacoes))
                
        self.cursor.executemany(
            "INSERT INTO exclusoes (colaborador_id, tipo_exclusao, valor_especifico, observacoes) VALUES (?, ?, ?, ?)",
            exclusoes_data
        )
        self.conn.commit()
        print(f"✅ {len(exclusoes_data)} registros de exclusões populados")
        
    def populate_dias_uteis(self):
        """Popula a tabela de dias úteis"""
        print("📅 Populando dias úteis...")
        
        dias_uteis_data = [
            (1, date(2025, 4, 15), date(2025, 5, 15), 22),  # SITEPD PR
            (2, date(2025, 4, 15), date(2025, 5, 15), 21),  # SINDPPD RS
            (3, date(2025, 4, 15), date(2025, 5, 15), 22),  # SINDPD SP
            (4, date(2025, 4, 15), date(2025, 5, 15), 21)   # SINDPD RJ
        ]
        
        self.cursor.executemany(
            "INSERT INTO dias_uteis (sindicato_id, periodo_inicio, periodo_fim, dias_uteis) VALUES (?, ?, ?, ?)",
            dias_uteis_data
        )
        self.conn.commit()
        print("✅ Dias úteis populados")
        
    def _get_sindicatos_map(self):
        """Retorna mapeamento de nome do sindicato para ID"""
        self.cursor.execute("SELECT id, nome_completo FROM sindicatos")
        return {row[1]: row[0] for row in self.cursor.fetchall()}
        
    def _get_cargos_map(self):
        """Retorna mapeamento de título do cargo para ID"""
        self.cursor.execute("SELECT id, titulo FROM cargos")
        return {row[1]: row[0] for row in self.cursor.fetchall()}
        
    def populate_all(self):
        """Popula todas as tabelas do banco"""
        print("🚀 Iniciando população do banco de dados...")
        print("=" * 60)
        
        self.create_database()
        self.create_schema()
        self.populate_estados()
        self.populate_sindicatos()
        self.populate_empresas()
        self.populate_cargos()
        self.populate_colaboradores()
        self.populate_ferias()
        self.populate_afastamentos()
        self.populate_desligamentos()
        self.populate_admissoes()
        self.populate_exclusoes()
        self.populate_dias_uteis()
        
        print("=" * 60)
        print("✅ Banco de dados populado com sucesso!")
        
    def get_stats(self):
        """Retorna estatísticas do banco"""
        stats = {}
        
        tables = ['colaboradores', 'sindicatos', 'estados', 'cargos', 'empresas', 
                 'ferias', 'afastamentos', 'desligamentos', 'admissoes', 'exclusoes', 'dias_uteis']
        
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = self.cursor.fetchone()[0]
            
        return stats
        
    def close(self):
        """Fecha a conexão com o banco"""
        if self.conn:
            self.conn.close()
            print(f"🔒 Conexão com banco fechada: {self.db_path}")

def main():
    """Função principal"""
    print("🗄️ SISTEMA DE BANCO DE DADOS VR/VA")
    print("=" * 60)
    
    # Criar e popular o banco
    db_manager = VRDatabaseManager("ai_vr/db/vr_database.db")
    
    try:
        db_manager.populate_all()
        
        # Mostrar estatísticas
        stats = db_manager.get_stats()
        print("\n📊 ESTATÍSTICAS DO BANCO:")
        print("-" * 40)
        for table, count in stats.items():
            print(f"  {table}: {count} registros")
            
        print(f"\n💾 Banco de dados salvo em: {db_manager.db_path}")
        print(f"📏 Tamanho do arquivo: {os.path.getsize(db_manager.db_path)} bytes")
        
    except Exception as e:
        print(f"❌ Erro ao criar banco: {e}")
    finally:
        db_manager.close()

if __name__ == "__main__":
    main()
