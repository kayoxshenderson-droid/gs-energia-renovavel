"""
CITIZEN ASSIST AI - Modulo de Energia: banho mais barato e sustentavel
Global Solution 2026.2 - Solucoes em Energias Renovaveis e Sustentaveis

COMO EXECUTAR
  * No IDLE: abra este arquivo (File > Open) e aperte F5.
  * No terminal:  python main.py

Usa somente a biblioteca padrao do Python (nada para instalar).
"""
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA / "src"))

from energia import calculos as c  # noqa: E402
from energia import comparacao as cp  # noqa: E402
from energia.assistente import AssistenteEnergia, brl, num  # noqa: E402

LINHA = "=" * 72


def titulo(texto):
    print("\n" + LINHA)
    print(" " + texto)
    print(LINHA)


def pausar():
    input("\n[Enter] para voltar ao menu...")


def perguntar_numero(rotulo, atual, minimo, maximo, inteiro=False):
    """Pergunta um numero; Enter mantem o valor atual."""
    while True:
        bruto = input(f"  {rotulo} [{num(atual, 0 if float(atual).is_integer() else 2)}]: ").strip()
        if not bruto:
            return atual
        try:
            valor = float(bruto.replace(",", "."))
        except ValueError:
            print("    Digite apenas um número (ex.: 8 ou 0,95).")
            continue
        if not minimo <= valor <= maximo:
            print(f"    Use um valor entre {num(minimo)} e {num(maximo)}.")
            continue
        return int(valor) if inteiro else valor


def perguntar_sim_nao(rotulo, atual):
    padrao = "s" if atual else "n"
    while True:
        r = input(f"  {rotulo} (s/n) [{padrao}]: ").strip().lower()
        if not r:
            return atual
        if r in ("s", "sim"):
            return True
        if r in ("n", "nao", "não"):
            return False
        print("    Responda s ou n.")


def mostrar_perfil(bot):
    f, ch = bot.p["familia"], bot.p["chuveiro"]
    tarifa = bot.tarifa_usuario or c.tarifa_final_r_kwh(bot.p)
    origem = "informada por você" if bot.tarifa_usuario else "estimada Enel SP 2026"
    print(f"  Pessoas na casa ........ {f['pessoas']}")
    print(f"  Minutos de banho ....... {num(f['duracao_banho_min'], 1)} por pessoa/dia")
    print(f"  Potência do chuveiro ... {num(ch['potencia_inverno_w'])} W (inverno) / {num(ch['potencia_verao_w'])} W (verão)")
    print(f"  Consumo da casa ........ {num(f['consumo_total_casa_kwh_mes'])} kWh/mês")
    print(f"  Tarifa ................. {brl(tarifa)}/kWh ({origem})")
    print(f"  Tarifa Social .......... {'sim' if bot.tarifa_social else 'não'}")


def editar_perfil(bot):
    titulo("MEU PERFIL  (aperte Enter para manter o valor entre colchetes)")
    f, ch = bot.p["familia"], bot.p["chuveiro"]
    f["pessoas"] = perguntar_numero("Quantas pessoas moram na casa", f["pessoas"], 1, 20, inteiro=True)
    f["duracao_banho_min"] = perguntar_numero("Minutos de cada banho", f["duracao_banho_min"], 1, 60)
    nova_pot = perguntar_numero("Potência do chuveiro em W (veja na etiqueta)", ch["potencia_inverno_w"], 2000, 9000)
    if nova_pot != ch["potencia_inverno_w"]:
        ch["potencia_verao_w"] = nova_pot * ch["potencia_verao_w"] / ch["potencia_inverno_w"]
        ch["potencia_inverno_w"] = nova_pot
    f["consumo_total_casa_kwh_mes"] = perguntar_numero("Consumo da casa em kWh/mês (veja na conta)",
                                                       f["consumo_total_casa_kwh_mes"], 20, 3000)
    tarifa_atual = bot.tarifa_usuario or round(c.tarifa_final_r_kwh(bot.p), 2)
    nova_tarifa = perguntar_numero("Tarifa em R$/kWh (valor da energia / kWh da conta)", tarifa_atual, 0.2, 3)
    if abs(nova_tarifa - tarifa_atual) > 1e-9:
        bot.tarifa_usuario = nova_tarifa
    bot.tarifa_social = perguntar_sim_nao("Você recebe Tarifa Social", bot.tarifa_social)
    print("\nPerfil atualizado:")
    mostrar_perfil(bot)
    aviso = bot.alerta_consistencia()
    if aviso:
        print("\n" + aviso)


def fmt_anos(v):
    if v is None:
        return "> horizonte"
    return "imediato" if v == 0 else f"{num(v, 1)} anos"


def relatorio_completo(bot):
    r = cp.comparar(bot.p, bot.tarifa_social, bot.tarifa_usuario)
    H = bot.p["financeiro"]["horizonte_anos"]
    titulo("RELATÓRIO COMPLETO - mesma necessidade (banho), mesmo período (12 meses)")
    print(f"Tarifa usada: {brl(r['tarifa_r_kwh'])}/kWh   |   Horizonte financeiro: {H} anos\n")
    cab = f"{'Alternativa':<44}{'kWh/ano rede':>13}{'Economia/ano':>14}{'Investimento':>14}{'Retorno':>12}"
    print(cab)
    print("-" * len(cab))
    for a in r["alternativas"]:
        ret = "-" if a.codigo == "BASE" else fmt_anos(a.payback_simples)
        print(f"{(a.codigo + ' ' + a.nome)[:43]:<44}{num(a.energia_rede_kwh_ano):>13}"
              f"{brl(a.economia_ano1):>14}{brl(a.investimento):>14}{ret:>12}")
    print()
    cab2 = f"{'Alternativa':<44}{'VPL ' + str(H) + ' anos':>14}{'CO₂ evit.kg':>12}{'Pico kW':>9}{'Telhado m²':>11}"
    print(cab2)
    print("-" * len(cab2))
    for a in r["alternativas"][1:]:
        print(f"{(a.codigo + ' ' + a.nome)[:43]:<44}{brl(a.vpl_horizonte):>14}"
              f"{num(a.co2_evitado_kg_ano, 1):>12}{num(a.reducao_pico_kw, 1):>9}{num(a.area_telhado_m2, 1):>11}")

    # grafico de barras em texto
    print("\nEnergia da rede usada no banho (kWh/ano):")
    maior = max(a.energia_rede_kwh_ano for a in r["alternativas"]) or 1
    for a in r["alternativas"]:
        barra = "#" * round(40 * a.energia_rede_kwh_ano / maior)
        print(f"  {a.codigo:<5}{barra:<41}{num(a.energia_rede_kwh_ano)}")
    print("  (C gera a mesma energia de dia e compensa na conta, mas o chuveiro segue usando a rede à noite)")

    print(f"\nANÁLISE DE SENSIBILIDADE (retorno simples em anos e VPL em {H} anos)")
    cab3 = f"{'Cenário':<28}{'Ret. B':>10}{'VPL B':>14}{'Ret. C':>10}{'VPL C':>14}{'Ret. A+B':>11}"
    print(cab3)
    print("-" * len(cab3))
    for s in cp.sensibilidade(bot.p, bot.tarifa_usuario, bot.tarifa_social):
        print(f"{s['cenario']:<28}{fmt_anos(s['payback_B']):>10}{brl(s['vpl_B']):>14}"
              f"{fmt_anos(s['payback_C']):>10}{brl(s['vpl_C']):>14}{fmt_anos(s['payback_AB']):>11}")
    print("\nObs.: a sensibilidade usa o perfil atual; os valores são estimativas, não garantias.")


def rodar_testes():
    """Roda os testes automaticos (unittest) e mostra o resultado."""
    import unittest
    titulo("TESTES AUTOMÁTICOS (fórmulas, física e coerência das respostas)")
    suite = unittest.defaultTestLoader.discover(str(PASTA / "tests"), top_level_dir=str(PASTA))
    resultado = unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)
    print("TODOS OS TESTES PASSARAM" if resultado.wasSuccessful() else "HÁ TESTES FALHANDO")


MENU = """
 1. Quanto o chuveiro gasta?            7. Impacto ambiental
 2. Dicas para economizar (sem custo)   8. Fontes dos dados
 3. Vale a pena aquecedor solar?        9. Limites das estimativas
 4. Vale a pena placa fotovoltaica?    10. Ajustar MEU PERFIL
 5. Comparar todas as opções           11. Relatório completo + sensibilidade
 6. Tarifa Social                      12. Ver meu perfil
 0. Sair                               13. Rodar os testes automáticos
 Ou digite uma pergunta (ex.: "somos 3 pessoas, banho de 10 minutos")"""


def main():
    bot = AssistenteEnergia()
    titulo("CITIZEN ASSIST AI  |  Energia no banho")
    print(" Ajudo você a entender e reduzir o gasto de energia do banho,")
    print(" o maior consumo isolado de muitas casas.")
    print(" Perfil padrão: família de 4 pessoas na Grande SP (Enel SP).")
    acoes = {
        "1": bot.r_consumo, "2": bot.r_dicas, "3": bot.r_solar_termico, "4": bot.r_fotovoltaico,
        "5": bot.r_comparar, "6": bot.r_tarifa_social, "7": bot.r_ambiental, "8": bot.r_fontes,
        "9": bot.r_limites,
    }
    while True:
        print(MENU)
        try:
            escolha = input("\nEscolha: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if escolha in ("0", "sair", "SAIR"):
            break
        if escolha in acoes:
            print()
            print(acoes[escolha]())
        elif escolha == "10":
            editar_perfil(bot)
        elif escolha == "11":
            relatorio_completo(bot)
        elif escolha == "13":
            rodar_testes()
        elif escolha == "12":
            titulo("MEU PERFIL")
            mostrar_perfil(bot)
        elif escolha:
            print("\n" + bot.responder(escolha))
        else:
            continue
        pausar()
    print("\nAté logo! Pequenas mudanças no banho já fazem diferença.")


if __name__ == "__main__":
    main()
