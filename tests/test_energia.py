"""Testes automatizados (biblioteca padrao unittest).

Conferem formulas, coerencia fisica e coerencia entre a analise
(comparacao.py) e o que o assistente responde ao usuario.

Rodar:
  * No IDLE: abra este arquivo e aperte F5.
  * No terminal: python tests/test_energia.py   (ou: python -m unittest -v)
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from energia import calculos as c  # noqa: E402
from energia import comparacao as cp  # noqa: E402
from energia import premissas as pr  # noqa: E402
from energia.assistente import AssistenteEnergia, brl  # noqa: E402


def premissas_padrao():
    return pr.valores(pr.carregar())


class TestPremissas(unittest.TestCase):
    def test_toda_premissa_tem_origem_tipo_e_unidade(self):
        for grupo, itens in pr.carregar().items():
            for chave, v in itens.items():
                with self.subTest(premissa=f"{grupo}.{chave}"):
                    self.assertIn(v["tipo"], {"REAL", "PUBLICO", "ESTIMADO"})
                    self.assertTrue(v["fonte"].strip())
                    self.assertTrue(v["unidade"].strip())


class TestEnergia(unittest.TestCase):
    def setUp(self):
        self.p = premissas_padrao()

    def test_energia_igual_potencia_vezes_tempo(self):
        pot_media = (7 * 5500 + 5 * 3200) / 12          # W
        horas = 4 * 1 * 8 / 60 * 30                       # h/mes
        self.assertAlmostEqual(c.horas_banho_mes(self.p), 16.0)
        self.assertAlmostEqual(c.energia_chuveiro_kwh_mes(self.p), pot_media / 1000 * horas)

    def test_verificacao_termica_coerente_com_potencia(self):
        vt = c.verificacao_termica(self.p)
        # 5,5 kW a 4 L/min deve esquentar a agua entre 15 e 25 C
        self.assertTrue(15 < vt["elevacao_temp_c"] < 25)
        # Q = m c dT deve bater com P x t na posicao inverno
        self.assertAlmostEqual(vt["energia_eletrica_dia_kwh"], 5.5 * (4 * 8 / 60), places=6)


class TestTarifa(unittest.TestCase):
    def setUp(self):
        self.p = premissas_padrao()

    def test_tarifa_com_tributos_por_dentro(self):
        self.assertAlmostEqual(c.tarifa_final_r_kwh(self.p), 0.72518 * 1.0902 / (1 - 0.12 - 0.05))

    def test_tarifa_social_franquia_80kwh(self):
        for consumo, cobrado in [(60, 0), (80, 0), (100, 20), (200, 120)]:
            with self.subTest(consumo=consumo):
                self.assertEqual(c.kwh_cobrados(consumo, self.p, tarifa_social=True), cobrado)
                self.assertEqual(c.kwh_cobrados(consumo, self.p, tarifa_social=False), consumo)

    def test_economia_limitada_pela_franquia(self):
        self.p["familia"]["consumo_total_casa_kwh_mes"] = 100
        # evitar 50 kWh: so 20 kWh eram cobrados -> economia = 20 x tarifa
        self.assertAlmostEqual(c.economia_reais_mes(50, self.p, tarifa_social=True, tarifa=1.0), 20.0)


class TestFinanceiro(unittest.TestCase):
    def test_payback_e_vpl_caso_simples(self):
        p = premissas_padrao()
        p["financeiro"].update(aumento_tarifa_ano=0.0, horizonte_anos=10)
        fluxo = c.fluxo_caixa(1000, 250, 0, p)
        self.assertAlmostEqual(c.payback_anos(fluxo), 4.0)
        self.assertAlmostEqual(c.vpl(fluxo, 0.0), 1500.0)
        self.assertAlmostEqual(c.vpl(fluxo, 0.10), -1000 + 250 * (1 - 1.1 ** -10) / 0.1)


class TestSolar(unittest.TestCase):
    def setUp(self):
        self.p = premissas_padrao()

    def test_fracao_solar_respeita_limite_fisico(self):
        fs = c.fracao_solar_efetiva(self.p)
        self.assertTrue(0 < fs <= self.p["aquecedor_solar"]["fracao_solar"])
        self.assertGreaterEqual(c.potencial_coletor_kwh_ano(self.p), fs * c.demanda_termica_kwh_ano(self.p))

    def test_fracao_solar_cai_com_coletor_pequeno(self):
        self.p["aquecedor_solar"]["area_coletor_m2"] = 0.5
        self.assertLess(c.fracao_solar_efetiva(self.p), self.p["aquecedor_solar"]["fracao_solar"])

    def test_credito_fv_lei_14300(self):
        self.assertAlmostEqual(c.fator_valor_credito_fv(self.p), 1 - 0.60 * 0.28)

    def test_fv_dimensionada_gera_a_energia_do_banho(self):
        r = cp.por_codigo(cp.comparar(self.p))
        self.assertAlmostEqual(r["C"].detalhes["geracao_kwh_ano"], r["BASE"].energia_rede_kwh_ano)


class TestComparacao(unittest.TestCase):
    def test_mesma_necessidade_e_coerencia(self):
        r = cp.por_codigo(cp.comparar(premissas_padrao()))
        base = r["BASE"].energia_rede_kwh_ano
        for cod in ("A", "B", "A+B"):
            self.assertAlmostEqual(r[cod].energia_rede_kwh_ano + r[cod].kwh_evitados_ano, base)
        self.assertGreater(r["A+B"].kwh_evitados_ano, max(r["A"].kwh_evitados_ano, r["B"].kwh_evitados_ano))
        self.assertTrue(r["B"].renovavel and r["C"].renovavel and not r["A"].renovavel)
        # so o aquecedor solar alivia o pico noturno
        self.assertGreater(r["B"].reducao_pico_kw, 0)
        self.assertEqual(r["C"].reducao_pico_kw, 0)

    def test_sensibilidade_cenario_base_igual_comparacao(self):
        p = premissas_padrao()
        base = cp.sensibilidade(p)[0]
        r = cp.por_codigo(cp.comparar(p))
        self.assertAlmostEqual(base["payback_B"], r["B"].payback_simples)
        self.assertAlmostEqual(base["vpl_C"], r["C"].vpl_horizonte)


class TestAssistente(unittest.TestCase):
    def test_roteia_intencoes(self):
        casos = [
            ("Quanto o chuveiro gasta por mês?", "kWh por mês"),
            ("Como economizar no banho?", "banhos de 5 minutos"),
            ("Vale a pena um aquecedor solar?", "Aquecedor solar de água"),
            ("e placa solar?", "fotovoltaica"),
            ("compare as opções", "MESMA necessidade"),
            ("como funciona a tarifa social", "80 kWh"),
            ("qual o impacto ambiental", "CO₂"),
            ("quais as fontes", "[R1]"),
            ("isso é garantido?", "Limites das estimativas"),
        ]
        for pergunta, trecho in casos:
            with self.subTest(pergunta=pergunta):
                self.assertIn(trecho, AssistenteEnergia().responder(pergunta))

    def test_respostas_trazem_fontes_e_limites(self):
        bot = AssistenteEnergia()
        for q in ["quanto gasta o chuveiro", "aquecedor solar", "placa solar", "compare", "impacto ambiental"]:
            with self.subTest(pergunta=q):
                resp = bot.responder(q)
                self.assertIn("Fontes:", resp)
                self.assertIn("Atenção:", resp)

    def test_numeros_do_assistente_vem_da_analise(self):
        bot = AssistenteEnergia()
        b = cp.por_codigo(cp.comparar(bot.p))["B"]
        self.assertIn(brl(b.economia_ano1), bot.responder("vale a pena aquecedor solar?"))

    def test_perfil_do_usuario_muda_o_calculo(self):
        bot = AssistenteEnergia()
        antes = c.energia_chuveiro_kwh_mes(bot.p)
        bot.responder("somos 2 pessoas, banho de 6 minutos, tarifa R$ 1,10, tenho tarifa social")
        self.assertEqual(bot.p["familia"]["pessoas"], 2)
        self.assertEqual(bot.p["familia"]["duracao_banho_min"], 6)
        self.assertAlmostEqual(bot.tarifa_usuario, 1.10)
        self.assertTrue(bot.tarifa_social)
        self.assertLess(c.energia_chuveiro_kwh_mes(bot.p), antes)

    def test_alerta_quando_chuveiro_passa_do_total(self):
        bot = AssistenteEnergia()
        self.assertIn("Aviso", bot.responder("4 pessoas, banho de 20 minutos, consumo 90 kWh"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
