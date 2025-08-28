from __future__ import annotations
from typing import Dict, Any
import json
import pandas as pd


class ConvencaoAgent:
    """Aplica regras de convenção coletiva sobre um DataFrame base.

    Espera um JSON com campos como:
    - valor_vr_diario_padrao: float
    - percentual_desconto_colaborador: float (0-1)
    - percentual_custo_empresa: float (0-1)
    - limites: {"max_desconto": float} (opcional)
    - excecoes: {
        "por_categoria": {"ESTAGIARIO": {"excluir": true}},
        "por_sindicato": {"SINDPD SP": {"valor_vr_diario": 40.0}}
      }
    """

    def __init__(self, convencao_json: str):
        if convencao_json.strip().startswith("{"):
            self.convencao = json.loads(convencao_json)
        else:
            # pode ser caminho para arquivo
            with open(convencao_json, "r", encoding="utf-8") as f:
                self.convencao = json.load(f)

    def aplicar(self, df_base: pd.DataFrame) -> pd.DataFrame:
        if df_base.empty:
            return df_base.copy()

        df = df_base.copy()

        valor_padrao = float(self.convencao.get("valor_vr_diario_padrao", 0.0))
        pct_desc = float(self.convencao.get("percentual_desconto_colaborador", 0.2))
        pct_empresa = float(self.convencao.get("percentual_custo_empresa", 0.8))
        limites = self.convencao.get("limites", {})
        excecoes = self.convencao.get("excecoes", {})

        # Ajuste de valor por sindicato, se houver
        mapa_por_sindicato = (excecoes.get("por_sindicato", {}) or {})
        df["VALOR DIÁRIO VR"] = df.get("VALOR DIÁRIO VR", pd.Series([valor_padrao] * len(df)))
        df["VALOR DIÁRIO VR"] = df.apply(
            lambda r: mapa_por_sindicato.get(str(r.get("Sindicato do Colaborador")), {}).get(
                "valor_vr_diario", r["VALOR DIÁRIO VR"]
            ), axis=1
        )
        # Substituir zeros pelo padrão
        df["VALOR DIÁRIO VR"] = df["VALOR DIÁRIO VR"].fillna(0).astype(float)
        df.loc[df["VALOR DIÁRIO VR"] <= 0, "VALOR DIÁRIO VR"] = valor_padrao

        # Aplicar exclusões por categoria
        mapa_por_categoria = (excecoes.get("por_categoria", {}) or {})
        categorias_excluir = [k for k, v in mapa_por_categoria.items() if v.get("excluir")]
        if categorias_excluir and "categoria_cargo" in df.columns:
            df = df[~df["categoria_cargo"].isin(categorias_excluir)].copy()

        # Cálculos finais conforme percentuais e limites
        df["TOTAL"] = (df["Dias"].fillna(0).astype(int) * df["VALOR DIÁRIO VR"].astype(float)).round(2)
        df["Desconto profissional"] = (df["TOTAL"] * pct_desc).round(2)
        df["Custo empresa"] = (df["TOTAL"] * pct_empresa).round(2)

        # Limites opcionais (ex.: máximo de desconto)
        max_desc = limites.get("max_desconto")
        if max_desc is not None:
            df.loc[df["Desconto profissional"] > max_desc, "Desconto profissional"] = max_desc
            df["Custo empresa"] = (df["TOTAL"] - df["Desconto profissional"]).round(2)

        return df
