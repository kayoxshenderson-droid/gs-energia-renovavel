"""Testes automatizados: conferem formulas, coerencia fisica e coerencia entre
a analise (comparacao.py) e o que o assistente responde ao usuario.

Rodar:  python -m pytest -q
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from energia import calculos as c  # noqa: E402
from energia import comparacao as cp  # noqa: E402
from energia import premissas as pr  # noqa: E402
from energia.assistente import AssistenteEnergia, brl  # noqa: E402


@pytest.fixture
def p():
    return pr.valores(pr.carregar())


# ------------------------------------------------------------ premissas
def test_toda_premissa_tem_origem_e_tipo():
    for grupo, itens in pr.carregar().items():
        for chave, v in itens.items():
            assert v["tipo"] in {"REAL", "PUBLICO", "ESTIMADO"}, f"{grupo}.{chave}"
            assert v["fonte"].strip(), f"{grupo}.{chave} sem fonte"
            assert v["unidade"].strip(), f"{grupo}.{chave} sem unidade"


# ------------------------------------------------------------- energia
def test_energia_igual_potencia_vezes_tempo(p):
    pot_media = (7 * 5500 + 5 * 3200) / 12            # W
    horas = 4 * 1 * 8 / 60 * 30                         # h/mes
    assert c.horas_banho_mes(p) == pytest.approx(16.0)
    assert c.energia_chuveiro_kwh_mes(p) == pytest.approx(pot_media / 1000 * horas)


def test_verificacao_termica_coerente_com_potencia(p):
    vt = c.verificacao_termica(p)
    # Chuveiro de 5,5 kW a 4 L/min deve esquentar a agua entre 15 e 25 C (banho morno/quente)
    assert 15 < vt["elevacao_temp_c"] < 25
    # Q = m c dT deve bater com P x t na posicao inverno (mesma energia por outro caminho)
    e_inverno_dia = 5.5 * (4 * 8 / 60)
    assert vt["energia_eletrica_dia_kwh"] == pytest.approx(e_inverno_dia, rel=1e-6)


# -------------------------------------------------------------- tarifa
def test_tarifa_com_tributos_por_dentro(p):
    t = 0.72518 * 1.0902 / (1 - 0.12 - 0.05)
    assert c.tarifa_final_r_kwh(p) == pytest.approx(t)


@pytest.mark.parametrize("consumo,cobrado", [(60, 0), (80, 0), (100, 20), (200, 120)])
def test_tarifa_social_franquia_80kwh(p, consumo, cobrado):
    assert c.kwh_cobrados(consumo, p, tarifa_social=True) == cobrado
    assert c.kwh_cobrados(consumo, p, tarifa_social=False) == consumo


def test_economia_limitada_pela_franquia(p):
    p["familia"]["consumo_total_casa_kwh_mes"] = 100
    # Evitar 50 kWh: so 20 kWh eram cobrados, entao a economia e 20 x tarifa
    eco = c.economia_reais_mes(50, p, tarifa_social=True, tarifa=1.0)
    assert eco == pytest.approx(20.0)


# ---------------------------------------------------------- financeiro
def test_payback_e_vpl_caso_simples(p):
    p["financeiro"].update(aumento_tarifa_ano=0.0, horizonte_anos=10)
    fluxo = c.fluxo_caixa(1000, 250, 0, p)
    assert c.payback_anos(fluxo) == pytest.approx(4.0)
    assert c.vpl(fluxo, 0.0) == pytest.approx(1500.0)
    assert c.vpl(fluxo, 0.10) == pytest.approx(-1000 + 250 * (1 - 1.1 ** -10) / 0.1)


# --------------------------------------------------------------- solar
def test_fracao_solar_respeita_limite_fisico(p):
    fs = c.fracao_solar_efetiva(p)
    assert 0 < fs <= p["aquecedor_solar"]["fracao_solar"]
    assert c.potencial_coletor_kwh_ano(p) >= fs * c.demanda_termica_kwh_ano(p)


def test_fracao_solar_cai_com_coletor_pequeno(p):
    p["aquecedor_solar"]["area_coletor_m2"] = 0.5
    assert c.fracao_solar_efetiva(p) < p["aquecedor_solar"]["fracao_solar"]


def test_credito_fv_lei_14300(p):
    assert c.fator_valor_credito_fv(p) == pytest.approx(1 - 0.60 * 0.28)


def test_fv_dimensionada_gera_a_energia_do_banho(p):
    r = cp.por_codigo(cp.comparar(p))
    assert r["C"].detalhes["geracao_kwh_ano"] == pytest.approx(r["BASE"].energia_rede_kwh_ano)


# ------------------------------------------------------------ comparacao
def test_mesma_necessidade_e_coerencia_entre_alternativas(p):
    r = cp.por_codigo(cp.comparar(p))
    base = r["BASE"].energia_rede_kwh_ano
    for cod in ("A", "B", "A+B"):
        assert r[cod].energia_rede_kwh_ano + r[cod].kwh_evitados_ano == pytest.approx(base)
    assert r["A+B"].kwh_evitados_ano > max(r["A"].kwh_evitados_ano, r["B"].kwh_evitados_ano)
    assert r["B"].renovavel and r["C"].renovavel and not r["A"].renovavel
    # So o aquecedor solar tira carga do pico; a FV gera de dia e nao alivia o pico noturno
    assert r["B"].reducao_pico_kw > 0 and r["C"].reducao_pico_kw == 0


# -------------------------------------------------------------- assistente
@pytest.mark.parametrize("pergunta,trecho", [
    ("Quanto o chuveiro gasta por mês?", "kWh por mês"),
    ("Como economizar no banho?", "banhos de 5 minutos"),
    ("Vale a pena um aquecedor solar?", "Aquecedor solar de água"),
    ("e placa solar?", "fotovoltaica"),
    ("compare as opções", "MESMA necessidade"),
    ("como funciona a tarifa social", "80 kWh"),
    ("qual o impacto ambiental", "CO₂"),
    ("quais as fontes", "[R1]"),
    ("isso é garantido?", "Limites das estimativas"),
])
def test_assistente_roteia_intencoes(pergunta, trecho):
    assert trecho in AssistenteEnergia().responder(pergunta)


def test_respostas_trazem_fontes_e_limites():
    bot = AssistenteEnergia()
    for q in ["quanto gasta o chuveiro", "aquecedor solar", "placa solar", "compare", "impacto ambiental"]:
        resp = bot.responder(q)
        assert "Fontes:" in resp and "Atenção:" in resp, q


def test_numeros_do_assistente_vem_da_analise():
    bot = AssistenteEnergia()
    b = cp.por_codigo(cp.comparar(bot.p))["B"]
    assert brl(b.economia_ano1) in bot.responder("vale a pena aquecedor solar?")


def test_perfil_do_usuario_muda_o_calculo():
    bot = AssistenteEnergia()
    antes = c.energia_chuveiro_kwh_mes(bot.p)
    bot.responder("somos 2 pessoas, banho de 6 minutos, tarifa R$ 1,10, tenho tarifa social")
    assert bot.p["familia"]["pessoas"] == 2
    assert bot.p["familia"]["duracao_banho_min"] == 6
    assert bot.tarifa_usuario == pytest.approx(1.10) and bot.tarifa_social
    assert c.energia_chuveiro_kwh_mes(bot.p) < antes


def test_alerta_quando_chuveiro_passa_do_total():
    bot = AssistenteEnergia()
    assert "Aviso" in bot.responder("4 pessoas, banho de 20 minutos, consumo 90 kWh")
