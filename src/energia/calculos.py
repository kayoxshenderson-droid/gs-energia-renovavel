"""Calculos de energia, custo e impacto do banho com chuveiro eletrico.

Conceitos usados (todos com unidade explicita):
  * Potencia P [W]  -> taxa de uso de energia.
  * Energia E [kWh] = P [kW] x t [h].
  * Calor sensivel Q [kJ] = m [kg] x c [kJ/kg.C] x dT [C]  (verificacao fisica).
  * Eficiencia = energia util / energia consumida.
  * Emissoes [kgCO2] = E [kWh] x fator de emissao [kgCO2/kWh].

Todas as funcoes recebem `p`, o dicionario de valores de premissas.valores().
"""
from __future__ import annotations

C_AGUA_KJ_KG_C = 4.186     # calor especifico da agua
KJ_POR_KWH = 3600.0
MESES = 12


# ----------------------------------------------------------------- consumo
def potencia_media_chuveiro_w(p: dict) -> float:
    """Potencia media anual ponderada pelos meses em cada posicao (W)."""
    ch = p["chuveiro"]
    m_inv = ch["meses_posicao_inverno"]
    return (m_inv * ch["potencia_inverno_w"] + (MESES - m_inv) * ch["potencia_verao_w"]) / MESES


def horas_banho_mes(p: dict, duracao_min: float | None = None) -> float:
    f = p["familia"]
    dur = f["duracao_banho_min"] if duracao_min is None else duracao_min
    return f["pessoas"] * f["banhos_pessoa_dia"] * dur / 60 * f["dias_mes"]


def energia_chuveiro_kwh_mes(p: dict, duracao_min: float | None = None,
                             potencia_w: float | None = None) -> float:
    """E = P x t  -> energia eletrica media mensal do chuveiro (kWh/mes)."""
    pot = potencia_media_chuveiro_w(p) if potencia_w is None else potencia_w
    return pot / 1000 * horas_banho_mes(p, duracao_min)


def energia_chuveiro_kwh_ano(p: dict, duracao_min: float | None = None) -> float:
    return energia_chuveiro_kwh_mes(p, duracao_min) * MESES


def verificacao_termica(p: dict) -> dict:
    """Confere E = P x t com a fisica do aquecimento da agua (Q = m c dT).

    Retorna a elevacao de temperatura que o chuveiro consegue na vazao
    considerada e a energia termica diaria correspondente.
    """
    ch = p["chuveiro"]
    vazao_kg_s = ch["vazao_l_min"] / 60            # 1 L de agua ~ 1 kg
    pot_util_kw = ch["potencia_inverno_w"] / 1000 * ch["eficiencia_chuveiro"]
    dT = pot_util_kw / (vazao_kg_s * C_AGUA_KJ_KG_C)   # kW / (kg/s * kJ/kg.C) = C
    f = p["familia"]
    litros_dia = f["pessoas"] * f["banhos_pessoa_dia"] * f["duracao_banho_min"] * ch["vazao_l_min"]
    q_dia_kwh = litros_dia * C_AGUA_KJ_KG_C * dT / KJ_POR_KWH
    return {
        "elevacao_temp_c": dT,
        "temp_saida_c": ch["temp_agua_fria_c"] + dT,
        "litros_agua_quente_dia": litros_dia,
        "energia_termica_dia_kwh": q_dia_kwh,
        "energia_eletrica_dia_kwh": q_dia_kwh / ch["eficiencia_chuveiro"],
    }


def participacao_na_conta(p: dict) -> float:
    return energia_chuveiro_kwh_mes(p) / p["familia"]["consumo_total_casa_kwh_mes"]


# ------------------------------------------------------------------ tarifa
def tarifa_final_r_kwh(p: dict) -> float:
    """Tarifa com tributos 'por dentro': T_final = T / (1 - ICMS - PIS/COFINS)."""
    t = p["tarifa"]
    sem_impostos = t["tarifa_b1_2025_sem_impostos"] * (1 + t["reajuste_b1_2026"])
    return sem_impostos / (1 - t["icms"] - t["pis_cofins"])


def kwh_cobrados(consumo_kwh_mes: float, p: dict, tarifa_social: bool) -> float:
    """Tarifa Social (Lei 15.235/2025): os primeiros 80 kWh/mes nao sao cobrados."""
    if not tarifa_social:
        return consumo_kwh_mes
    return max(0.0, consumo_kwh_mes - p["tarifa"]["franquia_tarifa_social_kwh"])


def custo_energia_mes(consumo_kwh_mes: float, p: dict, tarifa_social: bool = False,
                      tarifa: float | None = None) -> float:
    t = tarifa_final_r_kwh(p) if tarifa is None else tarifa
    return kwh_cobrados(consumo_kwh_mes, p, tarifa_social) * t


def economia_reais_mes(kwh_evitados_mes: float, p: dict, tarifa_social: bool = False,
                       tarifa: float | None = None) -> float:
    """Economia na conta = custo(antes) - custo(depois).

    Com Tarifa Social, so a parte acima de 80 kWh e cobrada; se a reducao levar
    o consumo abaixo da franquia, a economia em reais e menor que kWh x tarifa.
    """
    total = p["familia"]["consumo_total_casa_kwh_mes"]
    depois = max(0.0, total - kwh_evitados_mes)
    return (custo_energia_mes(total, p, tarifa_social, tarifa)
            - custo_energia_mes(depois, p, tarifa_social, tarifa))


# ------------------------------------------------------------ solar termico
def potencial_coletor_kwh_ano(p: dict) -> float:
    a = p["aquecedor_solar"]
    return a["area_coletor_m2"] * p["solar_recurso"]["irradiacao_kwh_m2_dia"] * 365 * a["eficiencia_sistema"]


def demanda_termica_kwh_ano(p: dict) -> float:
    return energia_chuveiro_kwh_ano(p) * p["chuveiro"]["eficiencia_chuveiro"]


def fracao_solar_efetiva(p: dict) -> float:
    """Fracao solar limitada pelo que o coletor consegue produzir."""
    limite_fisico = potencial_coletor_kwh_ano(p) / demanda_termica_kwh_ano(p)
    return min(p["aquecedor_solar"]["fracao_solar"], limite_fisico)


# -------------------------------------------------------------- fotovoltaico
def geracao_fv_kwh_ano_por_kwp(p: dict) -> float:
    """Geracao = Potencia pico x HSP x 365 x PR (HSP = irradiacao em kWh/m2.dia)."""
    return p["solar_recurso"]["irradiacao_kwh_m2_dia"] * 365 * p["fotovoltaico"]["performance_ratio"]


def dimensionar_fv_kwp(energia_alvo_kwh_ano: float, p: dict) -> float:
    return energia_alvo_kwh_ano / geracao_fv_kwh_ano_por_kwp(p)


def custo_fv(kwp: float, p: dict) -> float:
    fv = p["fotovoltaico"]
    return max(fv["custo_minimo"], kwp * 1000 * fv["custo_wp"])


def fator_valor_credito_fv(p: dict) -> float:
    """Lei 14.300/2022: parte do Fio B e paga sobre a energia compensada.

    Cada kWh gerado e compensado vale T x (1 - %FioB_cobrado x participacao_FioB).
    """
    fv = p["fotovoltaico"]
    return 1 - fv["fio_b_cobrado_2026"] * fv["fio_b_parcela_tarifa"]


# --------------------------------------------------------------- financeiro
def fluxo_caixa(investimento: float, economia_ano1: float, manutencao_ano: float,
                p: dict, degradacao: float = 0.0) -> list[float]:
    """Fluxo anual: ano 0 = -investimento; anos 1..N = economia - manutencao.

    A economia cresce com o aumento de tarifa e cai com a degradacao (FV).
    """
    fin = p["financeiro"]
    fluxo = [-investimento]
    for ano in range(1, fin["horizonte_anos"] + 1):
        fator = (1 + fin["aumento_tarifa_ano"]) ** (ano - 1) * (1 - degradacao) ** (ano - 1)
        fluxo.append(economia_ano1 * fator - manutencao_ano)
    return fluxo


def vpl(fluxo: list[float], taxa: float) -> float:
    return sum(v / (1 + taxa) ** i for i, v in enumerate(fluxo))


def payback_anos(fluxo: list[float], taxa: float = 0.0) -> float | None:
    """Payback (simples se taxa=0, descontado se taxa>0), com interpolacao."""
    acumulado = 0.0
    for i, v in enumerate(fluxo):
        vd = v / (1 + taxa) ** i
        if acumulado + vd >= 0 and i > 0:
            return i - 1 + (-acumulado / vd if vd else 0)
        acumulado += vd
    return None if fluxo[0] < 0 else 0.0


def emissoes_kg(kwh: float, p: dict) -> float:
    return kwh * p["ambiental"]["fator_emissao_sin_kg_kwh"]
