#!/usr/bin/env python3
"""
Gera a planilha no formato "VR MENSAL 05.2025.xlsx" baseada nos dados do banco
e nas regras descritas em doc/DOCUMENTACAO_VR_VA.md.

Uso:
  python3 generate_vr_planilha.py \
    --db ai_vr/db/vr_database.db \
    --inicio 2025-04-15 \
    --fim 2025-05-15 \
    --saida /home/andersonnascimento/develop/github/projects/ai_vr/data/VR_MENSAL_GERADO.xlsx
"""

import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")

import argparse
import os
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
import pandas as pd


@dataclass
class PeriodoReferencia:
    inicio: date
    fim: date

    @property
    def competencia(self) -> str:
        # Competência como MM/AAAA baseada no mês do fim do período
        return f"{self.fim.month:02d}/{self.fim.year}"

    @property
    def dias_periodo(self) -> int:
        return (self.fim - self.inicio).days + 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gerador da planilha VR mensal a partir do banco")
    parser.add_argument(
        "--db",
    default="ai_vr/db/vr_database.db",
    help="Caminho do arquivo SQLite do banco (ai_vr/db/vr_database.db)",
    )
    parser.add_argument(
        "--inicio",
        default="2025-04-15",
        help="Data de início do período (YYYY-MM-DD). Ex.: 2025-04-15",
    )
    parser.add_argument(
        "--fim",
        default="2025-05-15",
        help="Data de fim do período (YYYY-MM-DD). Ex.: 2025-05-15",
    )
    parser.add_argument(
        "--saida",
        default="/home/andersonnascimento/develop/github/projects/ai_vr/data/VR_MENSAL_GERADO.xlsx",
        help="Arquivo XLSX de saída",
    )
    return parser.parse_args()


def to_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def carregar_bases(conn: sqlite3.Connection, periodo: PeriodoReferencia):
    # Colaboradores + cargos + sindicatos + estados (valor diário)
    colaboradores = pd.read_sql_query(
        """
        SELECT 
            c.id as colaborador_id,
            c.matricula,
            c.situacao,
            c.data_admissao,
            c.data_desligamento,
            car.titulo as cargo,
            car.categoria as categoria_cargo,
            s.id as sindicato_id,
            s.nome_abreviado as sindicato,
            e.nome as estado,
            e.valor_vr_diario
        FROM colaboradores c
        JOIN cargos car ON c.cargo_id = car.id
        JOIN sindicatos s ON c.sindicato_id = s.id
        JOIN estados e ON s.estado_id = e.id
        """,
        conn,
    )

    # Dias úteis do período por sindicato
    dias_uteis = pd.read_sql_query(
        """
        SELECT sindicato_id, dias_uteis
        FROM dias_uteis
        WHERE periodo_inicio = ? AND periodo_fim = ?
        """,
        conn,
        params=(periodo.inicio.isoformat(), periodo.fim.isoformat()),
    )

    # Férias no período (o modelo atual grava uma linha com dias do período)
    ferias = pd.read_sql_query(
        """
        SELECT colaborador_id, SUM(dias_ferias) as dias_ferias
        FROM ferias
        WHERE periodo_inicio = ? AND periodo_fim = ?
        GROUP BY colaborador_id
        """,
        conn,
        params=(periodo.inicio.isoformat(), periodo.fim.isoformat()),
    )

    # Exclusões (estagiário, aprendiz, exterior)
    exclusoes = pd.read_sql_query(
        """
        SELECT colaborador_id, tipo_exclusao, valor_especifico, observacoes
        FROM exclusoes
        """,
        conn,
    )

    # Afastamentos (qualquer overlapping no período implica exclusão)
    afastamentos = pd.read_sql_query(
        """
        SELECT colaborador_id, tipo_afastamento, data_inicio, data_fim
        FROM afastamentos
        """,
        conn,
    )

    # Admissões (para proporcionalidade)
    admissoes = pd.read_sql_query(
        """
        SELECT colaborador_id, data_admissao
        FROM admissoes
        """,
        conn,
    )
    # Desligamentos (regras até dia 15 e proporcional após)
    desligamentos = pd.read_sql_query(
        """
        SELECT colaborador_id, data_desligamento, comunicado_ok
        FROM desligamentos
        """,
        conn,
    )

    return {
        "colaboradores": colaboradores,
        "dias_uteis": dias_uteis,
        "ferias": ferias,
        "exclusoes": exclusoes,
        "afastamentos": afastamentos,
        "admissoes": admissoes,
        "desligamentos": desligamentos,
    }


def periodo_overlap(inicio_a: date, fim_a: date, inicio_b, fim_b) -> bool:
    # Trata valores ausentes/NaT com segurança
    import pandas as pd  # import local para evitar dependência global aqui

    if inicio_b is None or (isinstance(inicio_b, float) and pd.isna(inicio_b)) or pd.isna(inicio_b):
        return False

    if isinstance(inicio_b, pd.Timestamp):
        inicio_b = inicio_b.date()

    if fim_b is None or (isinstance(fim_b, float) and pd.isna(fim_b)) or pd.isna(fim_b):
        fim_b_eff = date.max
    else:
        if isinstance(fim_b, pd.Timestamp):
            fim_b_eff = fim_b.date()
        else:
            fim_b_eff = fim_b

    return not (fim_a < inicio_b or fim_b_eff < inicio_a)


def montar_base_elegivel(bases: dict, periodo: PeriodoReferencia) -> pd.DataFrame:
    col = bases["colaboradores"].copy()

    # Juntar dias úteis por sindicato
    col = col.merge(bases["dias_uteis"], on="sindicato_id", how="left")

    # Férias
    col = col.merge(bases["ferias"], on="colaborador_id", how="left")
    col["dias_ferias"] = col["dias_ferias"].fillna(0).astype(int)

    # Flags de exclusão por tabela exclusoes
    if not bases["exclusoes"].empty:
        col = col.merge(
            bases["exclusoes"][['colaborador_id']].drop_duplicates().assign(flag_excluido=True),
            on="colaborador_id",
            how="left",
        )
    else:
        col["flag_excluido"] = False
    col["flag_excluido"] = col["flag_excluido"].fillna(False).infer_objects(copy=False)

    # Afastamentos: marcar quem tem overlap com o período
    afast = bases["afastamentos"].copy()
    afast["data_inicio"] = pd.to_datetime(afast["data_inicio"]).dt.date
    afast["data_fim"] = pd.to_datetime(afast["data_fim"]).dt.date
    # Garantir que data_inicio não seja NaT para cálculo de overlap
    afast["data_inicio"] = afast["data_inicio"].fillna(periodo.inicio)
    if not afast.empty:
        afast["overlap"] = afast.apply(
            lambda r: periodo_overlap(periodo.inicio, periodo.fim, r["data_inicio"], r["data_fim"]), axis=1
        )
        afast = afast[afast["overlap"]]
        col = col.merge(afast[["colaborador_id"]].drop_duplicates().assign(flag_afastado=True),
                        on="colaborador_id", how="left")
    else:
        col["flag_afastado"] = False
    col["flag_afastado"] = col["flag_afastado"].fillna(False).infer_objects(copy=False)

    # Regras de categoria de cargo (excluir estagiário/aprendiz/diretor)
    col["flag_categoria_excluida"] = col["categoria_cargo"].isin(["ESTAGIARIO", "APRENDIZ", "DIRETOR"]) \
        | col["situacao"].isin(["Auxílio Doença", "Licença Maternidade", "Atestado"])  # reforço

    # Filtrar elegíveis
    elegiveis = col[(~col["flag_excluido"]) & (~col["flag_afastado"]) & (~col["flag_categoria_excluida"])].copy()

    return elegiveis


def calcular_dias_valores(df: pd.DataFrame, bases: dict, periodo: PeriodoReferencia) -> pd.DataFrame:
    # Mapas auxiliares
    adm = bases["admissoes"].copy()
    des = bases["desligamentos"].copy()
    adm["data_admissao"] = pd.to_datetime(adm["data_admissao"]).dt.date
    des["data_desligamento"] = pd.to_datetime(des["data_desligamento"]).dt.date
    des["comunicado_ok"] = des["comunicado_ok"].astype(bool)

    adm_map = adm.set_index("colaborador_id")["data_admissao"].to_dict()
    des_map = des.set_index("colaborador_id")["data_desligamento"].to_dict()
    des_com_map = des.set_index("colaborador_id")["comunicado_ok"].to_dict()

    resultados = []

    for _, r in df.iterrows():
        dias_uteis = int(r.get("dias_uteis", 0) or 0)
        dias_ferias = int(r.get("dias_ferias", 0) or 0)
        valor_diario = float(r.get("valor_vr_diario", 0) or 0)

        # Base: dias úteis menos férias (não negativo)
        dias_base = max(dias_uteis - dias_ferias, 0)

        observacoes: list[str] = []

        # Admissão proporcional dentro do período
        data_adm = adm_map.get(r["colaborador_id"]) or r.get("data_admissao")
        if pd.notna(data_adm):
            data_adm_dt = data_adm if isinstance(data_adm, date) else pd.to_datetime(data_adm).date()
            if periodo.inicio <= data_adm_dt <= periodo.fim:
                dias_restantes = (periodo.fim - data_adm_dt).days + 1
                proporcao = max(min(dias_restantes / periodo.dias_periodo, 1.0), 0.0)
                dias_base = round(dias_base * proporcao)
                observacoes.append(f"Admissão em {data_adm_dt.strftime('%d/%m/%Y')}")

        # Desligamento: regra até dia 15 = 0 dias; após 15 proporcional
        data_des = des_map.get(r["colaborador_id"]) or r.get("data_desligamento")
        comunicado_ok = bool(des_com_map.get(r["colaborador_id"], False))
        if pd.notna(data_des):
            data_des_dt = data_des if isinstance(data_des, date) else pd.to_datetime(data_des).date()
            if periodo.inicio <= data_des_dt <= periodo.fim:
                if comunicado_ok and data_des_dt.day <= 15:
                    dias_base = 0
                    observacoes.append("Desligado c/ comunicado até dia 15")
                else:
                    dias_trabalhados = (data_des_dt - periodo.inicio).days + 1
                    proporcao = max(min(dias_trabalhados / periodo.dias_periodo, 1.0), 0.0)
                    dias_base = round(dias_base * proporcao)
                    observacoes.append(
                        f"Desligado em {data_des_dt.strftime('%d/%m/%Y')} (proporcional)"
                    )

        dias_vr = max(dias_base, 0)
        total = round(dias_vr * valor_diario, 2)
        custo_empresa = round(total * 0.8, 2)
        desconto_prof = round(total * 0.2, 2)

        resultados.append({
            "MATRICULA": int(r["matricula"]),
            "Admissão": "" if pd.isna(r.get("data_admissao")) else pd.to_datetime(r.get("data_admissao")).date().strftime("%d/%m/%Y"),
            "Sindicato do Colaborador": r["sindicato"],
            "Competência": periodo.competencia,
            "Dias": dias_vr,
            "VALOR DIÁRIO VR": round(valor_diario, 2),
            "TOTAL": total,
            "Custo empresa": custo_empresa,
            "Desconto profissional": desconto_prof,
            "OBS GERAL": "; ".join(observacoes),
        })

    return pd.DataFrame(resultados)


def gerar_validacoes(df_out: pd.DataFrame) -> pd.DataFrame:
    if df_out.empty:
        return pd.DataFrame({
            "Métrica": ["Total colaboradores", "Soma TOTAL", "Soma Custo empresa", "Soma Desconto profissional"],
            "Valor": [0, 0.0, 0.0, 0.0],
        })

    return pd.DataFrame({
        "Métrica": [
            "Total colaboradores",
            "Soma TOTAL",
            "Soma Custo empresa",
            "Soma Desconto profissional",
        ],
        "Valor": [
            int(len(df_out)),
            round(float(df_out["TOTAL"].sum()), 2),
            round(float(df_out["Custo empresa"].sum()), 2),
            round(float(df_out["Desconto profissional"].sum()), 2),
        ],
    })


def salvar_planilha(df_saida: pd.DataFrame, df_valid: pd.DataFrame, saida: str, competencia: str) -> None:
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    with pd.ExcelWriter(saida, engine="openpyxl") as writer:
        aba_vr = f"VR MENSAL {competencia.replace('/', '.')}"
        df_saida.to_excel(writer, sheet_name=aba_vr, index=False)

    print(f"✅ Planilha gerada: {saida}")


def main():
    args = parse_args()
    periodo = PeriodoReferencia(inicio=to_date(args.inicio), fim=to_date(args.fim))

    if not os.path.exists(args.db):
        raise FileNotFoundError(f"Banco de dados não encontrado: {args.db}")

    conn = sqlite3.connect(args.db)
    try:
        conn.row_factory = sqlite3.Row
        bases = carregar_bases(conn, periodo)
        elegiveis = montar_base_elegivel(bases, periodo)
        df_saida = calcular_dias_valores(elegiveis, bases, periodo)
        df_valid = gerar_validacoes(df_saida)
        salvar_planilha(df_saida, df_valid, args.saida, periodo.competencia)
    finally:
        conn.close()


if __name__ == "__main__":
    main()


