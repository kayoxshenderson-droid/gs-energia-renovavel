"""Carrega as premissas de data/premissas.json.

Cada premissa tem valor, unidade, tipo (REAL / PUBLICO / ESTIMADO), fonte e
referencias. O codigo usa so o valor; o restante e exibido pelo assistente e
pelos relatorios para deixar a origem de cada numero rastreavel.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

ARQUIVO_PADRAO = Path(__file__).resolve().parents[2] / "data" / "premissas.json"


def carregar(caminho: Path | str = ARQUIVO_PADRAO) -> dict:
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)
    dados.pop("_sobre", None)
    return dados


def valores(premissas: dict) -> dict:
    """Converte {grupo: {chave: {valor,...}}} em {grupo: {chave: valor}}."""
    return {g: {k: v["valor"] for k, v in itens.items()} for g, itens in premissas.items()}


def com_ajustes(p: dict, **ajustes) -> dict:
    """Copia de valores() com ajustes no formato grupo__chave=valor.

    Ex.: com_ajustes(p, familia__pessoas=3, chuveiro__potencia_inverno_w=7500)
    """
    novo = copy.deepcopy(p)
    for nome, v in ajustes.items():
        grupo, chave = nome.split("__", 1)
        if grupo not in novo or chave not in novo[grupo]:
            raise KeyError(f"Premissa desconhecida: {grupo}.{chave}")
        novo[grupo][chave] = v
    return novo
