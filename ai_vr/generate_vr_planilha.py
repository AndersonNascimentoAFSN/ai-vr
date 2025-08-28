#!/usr/bin/env python3
"""
Gera a planilha no formato "VR MENSAL 05.2025.xlsx" baseada nos dados do banco
e nas regras descritas em doc/DOCUMENTACAO_VR_VA.md.

Uso:
  python3 generate_vr_planilha.py \
	--db /home/andersonnascimento/develop/github/projects/ai_vr/vr_database.db \
	--inicio 2025-04-15 \
	--fim 2025-05-15 \
	--saida /home/andersonnascimento/develop/github/projects/ai_vr/data/VR_MENSAL_GERADO.xlsx
"""

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

# ...restante do código igual ao generate_vr_planilha.py original...
