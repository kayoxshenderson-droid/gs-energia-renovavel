"""Comparacao das alternativas para a MESMA necessidade e o MESMO periodo.

Necessidade: aquecer a agua do banho de uma familia (perfil em premissas.json).
Periodo de referencia: 12 meses (energia e custo anual) + horizonte de 15 anos
(analise financeira).

Alternativas:
  BASE  - situacao atual: chuveiro eletrico.
  A     - Banho consciente: reduzir o banho para 5 min (sem custo).
  B     - Aquecedor solar termico (fonte RENOVAVEL) com o chuveiro como apoio.
  C     - Energia solar fotovoltaica (fonte RENOVAVEL) dimensionada para o chuveiro.
  A+B   - Combinacao: habito + aquecedor solar.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

from . import calculos as c


@dataclass
class Alternativa:
    codigo: str
    nome: str
    renovavel: bool
    energia_rede_kwh_ano: float          # energia que a rede ainda fornece ao banho
    kwh_evitados_ano: float              # energia da rede evitada/compensada
    economia_ano1: float                 # R$ no 1o ano
    investimento: float                  # R$
    manutencao_ano: float                # R$/ano
    payback_simples: float | None
    payback_descontado: float | None
    vpl_horizonte: float
    co2_evitado_kg_ano: float
    reducao_pico_kw: float               # potencia retirada do horario de pico (18h-21h)
    area_telhado_m2: float
    agua_economizada_l_ano: float
    detalhes: dict = field(default_factory=dict)

    def como_dict(self) -> dict:
        return asdict(self)


def _financeiro(investimento, economia_ano1, manutencao, p, degradacao=0.0):
    fluxo = c.fluxo_caixa(investimento, economia_ano1, manutencao, p, degradacao)
    taxa = p["financeiro"]["taxa_desconto"]
    return {
        "fluxo": fluxo,
        "payback_simples": c.payback_anos(fluxo) if investimento > 0 else 0.0,
        "payback_descontado": c.payback_anos(fluxo, taxa) if investimento > 0 else 0.0,
        "vpl": c.vpl(fluxo, taxa),
    }


def comparar(p: dict, tarifa_social: bool = False, tarifa: float | None = None) -> dict:
    T = c.tarifa_final_r_kwh(p) if tarifa is None else tarifa
    pot_inv_kw = p["chuveiro"]["potencia_inverno_w"] / 1000

    # ---------------- BASE
    e_base = c.energia_chuveiro_kwh_ano(p)
    base = Alternativa(
        "BASE", "Situação atual (chuveiro elétrico)", False,
        energia_rede_kwh_ano=e_base, kwh_evitados_ano=0, economia_ano1=0, investimento=0,
        manutencao_ano=0, payback_simples=None, payback_descontado=None, vpl_horizonte=0,
        co2_evitado_kg_ano=0, reducao_pico_kw=0, area_telhado_m2=0, agua_economizada_l_ano=0,
        detalhes={"custo_anual_banho": c.custo_energia_mes(e_base / 12, p, False, T) * 12,
                  "emissoes_kg_ano": c.emissoes_kg(e_base, p)},
    )

    def economia(kwh_ano: float) -> float:
        return c.economia_reais_mes(kwh_ano / 12, p, tarifa_social, T) * 12

    # ---------------- A: banho consciente
    meta = p["habitos"]["duracao_banho_meta_min"]
    e_a = c.energia_chuveiro_kwh_ano(p, duracao_min=meta)
    ev_a = e_base - e_a
    eco_a = economia(ev_a)
    fin_a = _financeiro(p["habitos"]["custo_implantacao"], eco_a, 0, p)
    f = p["familia"]
    agua_a = (f["pessoas"] * f["banhos_pessoa_dia"] * (f["duracao_banho_min"] - meta)
              * p["chuveiro"]["vazao_l_min"] * 365)
    alt_a = Alternativa(
        "A", f"Banho consciente ({meta:g} min)", False, e_a, ev_a, eco_a,
        p["habitos"]["custo_implantacao"], 0, fin_a["payback_simples"], fin_a["payback_descontado"],
        fin_a["vpl"], c.emissoes_kg(ev_a, p), 0.0, 0.0, agua_a,
        detalhes={"reducao_percentual": ev_a / e_base,
                  "obs": "A potencia no pico continua a mesma; o que cai e o tempo ligado."},
    )

    # ---------------- B: aquecedor solar termico
    fs = c.fracao_solar_efetiva(p)
    e_b = e_base * (1 - fs)
    ev_b = e_base - e_b
    eco_b = economia(ev_b)
    a = p["aquecedor_solar"]
    fin_b = _financeiro(a["custo_instalado"], eco_b, a["manutencao_ano"], p)
    alt_b = Alternativa(
        "B", "Aquecedor solar + chuveiro de apoio", True, e_b, ev_b, eco_b,
        a["custo_instalado"], a["manutencao_ano"], fin_b["payback_simples"],
        fin_b["payback_descontado"], fin_b["vpl"], c.emissoes_kg(ev_b, p),
        pot_inv_kw * fs, a["area_coletor_m2"], 0.0,
        detalhes={"fracao_solar": fs,
                  "potencial_coletor_kwh_ano": c.potencial_coletor_kwh_ano(p),
                  "demanda_termica_kwh_ano": c.demanda_termica_kwh_ano(p),
                  "obs": "Aquece a agua diretamente; tira o chuveiro do horario de pico na maior parte dos dias."},
    )

    # ---------------- C: fotovoltaico
    kwp = c.dimensionar_fv_kwp(e_base, p)
    ger = kwp * c.geracao_fv_kwh_ano_por_kwp(p)
    fator = c.fator_valor_credito_fv(p)
    eco_c = economia(ger * fator)
    fv = p["fotovoltaico"]
    inv_c = c.custo_fv(kwp, p)
    fin_c = _financeiro(inv_c, eco_c, fv["manutencao_ano"], p, fv["degradacao_ano"])
    co2_c = ger * (p["ambiental"]["fator_emissao_sin_kg_kwh"] - p["ambiental"]["fv_ciclo_vida_kg_kwh"])
    alt_c = Alternativa(
        "C", "Placas fotovoltaicas para o banho", True, e_base, ger, eco_c,
        inv_c, fv["manutencao_ano"], fin_c["payback_simples"], fin_c["payback_descontado"],
        fin_c["vpl"], co2_c, 0.0, kwp * fv["area_m2_por_kwp"], 0.0,
        detalhes={"kwp": kwp, "geracao_kwh_ano": ger, "valor_do_kwh_compensado": fator,
                  "obs": "Gera de dia e compensa a energia na conta; o chuveiro continua puxando a rede a noite."},
    )

    # ---------------- A + B
    pa = {**p, "familia": {**p["familia"], "duracao_banho_min": meta}}
    e_ab = c.energia_chuveiro_kwh_ano(pa) * (1 - c.fracao_solar_efetiva(pa))
    ev_ab = e_base - e_ab
    eco_ab = economia(ev_ab)
    fin_ab = _financeiro(a["custo_instalado"], eco_ab, a["manutencao_ano"], p)
    alt_ab = Alternativa(
        "A+B", "Banho consciente + aquecedor solar", True, e_ab, ev_ab, eco_ab,
        a["custo_instalado"], a["manutencao_ano"], fin_ab["payback_simples"],
        fin_ab["payback_descontado"], fin_ab["vpl"], c.emissoes_kg(ev_ab, p),
        pot_inv_kw * c.fracao_solar_efetiva(pa), a["area_coletor_m2"], agua_a,
        detalhes={"fracao_solar": c.fracao_solar_efetiva(pa)},
    )

    return {
        "tarifa_r_kwh": T,
        "tarifa_social": tarifa_social,
        "alternativas": [base, alt_a, alt_b, alt_c, alt_ab],
        "verificacao_termica": c.verificacao_termica(p),
        "participacao_chuveiro_na_conta": c.participacao_na_conta(p),
    }


def por_codigo(resultado: dict) -> dict:
    return {a.codigo: a for a in resultado["alternativas"]}


# Cenarios da analise de sensibilidade: (nome, tarifa fixa ou None, ajustes nas premissas)
CENARIOS_SENSIBILIDADE = [
    ("Tarifa R$ 0,80/kWh", 0.80, {}),
    ("Tarifa R$ 1,20/kWh", 1.20, {}),
    ("Aquecedor solar R$ 3.000", None, {"aquecedor_solar__custo_instalado": 3000}),
    ("Aquecedor solar R$ 8.000", None, {"aquecedor_solar__custo_instalado": 8000}),
    ("FV custo mínimo R$ 7.000", None, {"fotovoltaico__custo_minimo": 7000}),
    ("Fração solar 55%", None, {"aquecedor_solar__fracao_solar": 0.55}),
    ("Irradiação 4,0 kWh/m².dia", None, {"solar_recurso__irradiacao_kwh_m2_dia": 4.0}),
    ("2 pessoas", None, {"familia__pessoas": 2}),
    ("6 pessoas", None, {"familia__pessoas": 6}),
    ("Banho de 12 min", None, {"familia__duracao_banho_min": 12}),
    ("Tarifa sobe 0%/ano", None, {"financeiro__aumento_tarifa_ano": 0.0}),
]


def sensibilidade(p: dict, tarifa: float | None = None, tarifa_social: bool = False) -> list[dict]:
    """Recalcula as alternativas mudando uma premissa por vez (a partir do perfil atual)."""
    from . import premissas as pr
    linhas = []
    for nome, tarifa_cenario, ajustes in [("Cenário base", None, {})] + CENARIOS_SENSIBILIDADE:
        t = tarifa_cenario if tarifa_cenario is not None else tarifa
        d = por_codigo(comparar(pr.com_ajustes(p, **ajustes), tarifa_social, t))
        linhas.append({"cenario": nome, "economia_A": d["A"].economia_ano1,
                       "payback_B": d["B"].payback_simples, "vpl_B": d["B"].vpl_horizonte,
                       "payback_C": d["C"].payback_simples, "vpl_C": d["C"].vpl_horizonte,
                       "payback_AB": d["A+B"].payback_simples})
    return linhas
