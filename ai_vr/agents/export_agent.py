from __future__ import annotations
from typing import Tuple
import pandas as pd
from ai_vr.scripts.generate_vr_planilha import (
	PeriodoReferencia,
	carregar_bases,
	montar_base_elegivel,
	calcular_dias_valores,
	salvar_planilha,
)
import sqlite3


class ExportAgent:
	"""Consolida cálculos e exporta a planilha utilizando o script existente."""

	def __init__(self, db_path: str):
		self.db_path = db_path

	def gerar_base(self, periodo: PeriodoReferencia) -> pd.DataFrame:
		conn = sqlite3.connect(self.db_path)
		try:
			conn.row_factory = sqlite3.Row
			bases = carregar_bases(conn, periodo)
			elegiveis = montar_base_elegivel(bases, periodo)
			df = calcular_dias_valores(elegiveis, bases, periodo)
			return df
		finally:
			conn.close()

	def exportar(self, df_saida: pd.DataFrame, output_path: str, competencia: str) -> None:
		if df_saida is None:
			print("[ERRO] DataFrame de saída está None! Nada será exportado.")
			raise ValueError("DataFrame de saída está None. Verifique o pipeline de geração de dados.")
		if df_saida.empty:
			print("[AVISO] DataFrame de saída está vazio! Nada será exportado.")
		else:
			print(f"[INFO] Exportando planilha: {output_path} | Linhas: {len(df_saida)} | Colunas: {len(df_saida.columns)}")
		# Sem a aba de validações, conforme edição do script
		salvar_planilha(df_saida, pd.DataFrame(), output_path, competencia)
