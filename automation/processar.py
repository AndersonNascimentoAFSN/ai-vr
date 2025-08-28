
from __future__ import annotations
from typing import Optional
from datetime import date
import json
import pandas as pd
import os
import subprocess

from generate_vr_planilha import PeriodoReferencia
from automation.agents.db_agent import DatabaseAgent
from automation.agents.convencao_agent import ConvencaoAgent
from automation.agents.export_agent import ExportAgent

def criar_banco_se_necessario(db_path: str):
    if not os.path.exists(db_path):
        print(f"[INFO] Banco '{db_path}' não encontrado. Criando schema...")
        if os.path.exists("create_database.py"):
            subprocess.run(["python3", "create_database.py"], check=True)
        elif os.path.exists("database_schema.sql"):
            subprocess.run(["sqlite3", db_path, "<", "database_schema.sql"], shell=True, check=True)
        else:
            raise RuntimeError("Não foi encontrado 'create_database.py' nem 'database_schema.sql' para criar o banco.")
        print("[INFO] Banco criado.")
    else:
        print(f"[INFO] Banco '{db_path}' já existe.")

def popular_banco(db_path: str):
    if os.path.exists("database_populate.py"):
        print("[INFO] Populando banco de dados a partir das planilhas...")
        subprocess.run(["python3", "database_populate.py"], check=True)
        print("[INFO] Banco populado.")
    else:
        raise RuntimeError("Não foi encontrado 'database_populate.py' para popular o banco.")

def processar_beneficios(db_path: str, convencao_json: str, output_planilha: str,
                         inicio: str = "2025-04-15", fim: str = "2025-05-15",
                         llm_model: str = "gpt-4o-mini") -> str:
    """Processa os benefícios VR/VA usando os agentes e exporta planilha.

    Retorna o caminho do arquivo gerado.
    """
    periodo = PeriodoReferencia(
        inicio=pd.to_datetime(inicio).date(),
        fim=pd.to_datetime(fim).date(),
    )

    # 1) Agente de DB (disponível para consultas auxiliares, se necessário)
    db_agent = DatabaseAgent(db_path=db_path, llm_model=llm_model)
    _ = db_agent.get_connection_uri()  # apenas para validar conexão

    # 2) Gerar base de cálculo com o export agent
    export_agent = ExportAgent(db_path=db_path)
    df_base = export_agent.gerar_base(periodo)

    # 3) Aplicar convenção coletiva
    conv_agent = ConvencaoAgent(convencao_json)
    df_final = conv_agent.aplicar(df_base)

    # 4) Exportar planilha
    export_agent.exportar(df_final, output_planilha, periodo.competencia)

    return output_planilha

if __name__ == "__main__":
    db_path = "vr_database.db"
    output_planilha = "data/VR_MENSAL_GERADO.xlsx"
    exemplo_convencao = json.dumps({
        "valor_vr_diario_padrao": 37.5,
        "percentual_desconto_colaborador": 0.2,
        "percentual_custo_empresa": 0.8,
        "limites": {"max_desconto": 400.0},
        "excecoes": {
            "por_categoria": {"ESTAGIARIO": {"excluir": True}},
            "por_sindicato": {"SINDPD SP": {"valor_vr_diario": 40.0}}
        }
    })

    criar_banco = not os.path.exists(db_path)
    criar_banco_se_necessario(db_path)
    popular_banco(db_path)

    caminho = processar_beneficios(
        db_path=db_path,
        convencao_json=exemplo_convencao,
        output_planilha=output_planilha,
    )
    print(f"Planilha gerada em: {caminho}")
