from __future__ import annotations
from typing import Optional
from datetime import date
import json
import pandas as pd

from generate_vr_planilha import PeriodoReferencia
from automation.agents.db_agent import DatabaseAgent
from automation.agents.convencao_agent import ConvencaoAgent
from automation.agents.export_agent import ExportAgent


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
    # Exemplo rápido de execução
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
    caminho = processar_beneficios(
        db_path="/home/andersonnascimento/develop/github/projects/ai_vr/vr_database.db",
        convencao_json=exemplo_convencao,
        output_planilha="/home/andersonnascimento/develop/github/projects/ai_vr/data/VR_MENSAL_GERADO.xlsx",
    )
    print(f"Planilha gerada em: {caminho}")
