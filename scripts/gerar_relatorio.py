"""Gera os resultados da analise a partir de data/premissas.json:

  data/resultados_alternativas.csv   tabela da comparacao
  data/sensibilidade.csv             analise de sensibilidade
  docs/03_resultados_gerados.md      tabelas em Markdown (usadas no README/docs)
  docs/img/energia_rede.png          grafico de energia da rede por alternativa
  docs/img/fluxo_acumulado.png       grafico de retorno financeiro acumulado

Uso:  python scripts/gerar_relatorio.py
"""
import copy
import csv
import sys
from pathlib import Path

try:  # graficos sao opcionais: sem matplotlib o script gera so tabelas e CSVs
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from energia import calculos as c  # noqa: E402
from energia import comparacao as cp  # noqa: E402
from energia import premissas as pr  # noqa: E402
from energia.assistente import brl, num  # noqa: E402

DOC02_CABECALHO = """
# 2. Análise de consumo: dados, unidades, período e premissas

> Tabela gerada por `python scripts/gerar_relatorio.py` a partir de `data/premissas.json`.

## Período e unidades

- **Período de referência comum:** 12 meses (ano de 2026) para energia, custo e emissões de todas as alternativas.
- **Horizonte financeiro comum:** 15 anos (vida útil do aquecedor solar, a menor entre as tecnologias comparadas).
- **Unidades:** potência em W/kW; energia em kWh; tarifa em R$/kWh; irradiação em kWh/m²·dia; emissões em kg CO₂.

## Classificação dos dados

- **REAL** — valor oficial ou legal (ANEEL, leis, MCTI, IPCC).
- **PÚBLICO** — levantamento publicado ou de mercado (Procel, Greener, preços de varejo, fabricantes).
- **ESTIMADO** — suposição da equipe, justificada na própria linha. Todo valor estimado pode ser trocado pelo usuário no assistente ou no arquivo de premissas.

## Como o consumo é calculado

1. **Potência média anual** do chuveiro: `P_média = (7 × 5.500 W + 5 × 3.200 W) / 12 = 4.542 W`.
2. **Tempo de uso:** `t = 4 pessoas × 1 banho × 8 min ÷ 60 × 30 dias = 16 h/mês`.
3. **Energia:** `E = P × t = 4,542 kW × 16 h = 72,7 kWh/mês = 872 kWh/ano`.
4. **Conferência física:** na posição inverno, com vazão de 4 L/min, `ΔT = P·η / (ṁ·c) = 5,5 × 0,95 / (0,0667 × 4,186) ≈ 18,7 °C`, ou seja, a água sai a ~39 °C, temperatura coerente com um banho real. A energia térmica diária (`Q = m·c·ΔT`) bate com `P × t`.
5. **Tarifa com tributos (por dentro):** `T = 0,72518 × (1 + 0,0902) / (1 − 0,12 − 0,05) ≈ R$ 0,95/kWh`. Bandeiras e iluminação pública ficam de fora (ver limitações).
6. **Tarifa Social:** kWh cobrados = `máx(0, consumo − 80)`. A economia em reais é a diferença de custo antes/depois, o que trata corretamente o caso em que a redução cai dentro da faixa gratuita.

## Premissas
"""

DOC02_RODAPE = """
## Observação sobre a participação do chuveiro

O perfil-tipo resulta em 36% da conta, acima da média nacional de ~24% da PPH. A diferença é esperada: a família tem 4 pessoas, usa a posição inverno em 7 meses e, sendo de baixa renda, tem menos aparelhos que a média. O assistente avisa quando os dados informados levam o chuveiro a passar de 80% do consumo total, um sinal de dados incoerentes.
"""

AZUL, LARANJA, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TEXTO, TEXTO2, SUPERFICIE, GRADE = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"


def _estilo(ax):
    ax.set_facecolor(SUPERFICIE)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(GRADE)
    ax.tick_params(colors=TEXTO2, labelsize=9)
    ax.grid(axis="y", color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)


def pb(v):
    return "-" if v is None else ("0 (imediato)" if v == 0 else num(v, 1))


def main():
    p = pr.valores(pr.carregar())
    r = cp.comparar(p)
    alts = r["alternativas"]
    H = p["financeiro"]["horizonte_anos"]

    # ------------------------------------------------------------ CSV
    with open(RAIZ / "data" / "resultados_alternativas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["codigo", "alternativa", "renovavel", "energia_rede_kwh_ano", "kwh_evitados_ano",
                    "economia_ano1_rs", "investimento_rs", "manutencao_rs_ano", "payback_simples_anos",
                    "payback_descontado_anos", f"vpl_{H}anos_rs", "co2_evitado_kg_ano", "alivio_pico_kw",
                    "area_telhado_m2", "agua_economizada_l_ano"])
        for a in alts:
            w.writerow([a.codigo, a.nome, a.renovavel, round(a.energia_rede_kwh_ano, 1), round(a.kwh_evitados_ano, 1),
                        round(a.economia_ano1, 2), a.investimento, a.manutencao_ano,
                        None if a.payback_simples is None else round(a.payback_simples, 2),
                        None if a.payback_descontado is None else round(a.payback_descontado, 2),
                        round(a.vpl_horizonte, 2), round(a.co2_evitado_kg_ano, 2), round(a.reducao_pico_kw, 2),
                        round(a.area_telhado_m2, 2), round(a.agua_economizada_l_ano)])

    # ---------------------------------------------------- sensibilidade
    sens = [[x["cenario"], x["economia_A"], x["payback_B"], x["vpl_B"], x["payback_C"], x["vpl_C"],
             x["payback_AB"]] for x in cp.sensibilidade(p)]
    with open(RAIZ / "data" / "sensibilidade.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cenario", "economia_A_ano1", "payback_B", f"vpl_B_{H}a", "payback_C", f"vpl_C_{H}a", "payback_AB"])
        for row in sens:
            w.writerow([row[0]] + [None if v is None else round(v, 2) for v in row[1:]])

    # ---------------------------------------------------------- Markdown
    vt = r["verificacao_termica"]
    md = [
        "# Resultados gerados automaticamente",
        "",
        "> Arquivo gerado por `python scripts/gerar_relatorio.py` a partir de `data/premissas.json`. "
        "Não editar à mão: altere as premissas e rode o script de novo.",
        "",
        "## Consumo atual (alternativa BASE)",
        "",
        f"- Potência média anual do chuveiro: **{num(c.potencia_media_chuveiro_w(p))} W** "
        f"(7 meses a 5.500 W + 5 meses a 3.200 W)",
        f"- Tempo de banho: **{num(c.horas_banho_mes(p), 1)} h/mês**",
        f"- Energia do chuveiro: **{num(c.energia_chuveiro_kwh_mes(p), 1)} kWh/mês = "
        f"{num(c.energia_chuveiro_kwh_ano(p))} kWh/ano**",
        f"- Participação no consumo da casa: **{num(100 * r['participacao_chuveiro_na_conta'])}%**",
        f"- Tarifa estimada com tributos: **{brl(r['tarifa_r_kwh'])}/kWh**",
        f"- Custo anual do banho: **{brl(alts[0].detalhes['custo_anual_banho'])}**",
        f"- Emissões associadas: **{num(alts[0].detalhes['emissoes_kg_ano'], 1)} kg CO₂/ano**",
        f"- Verificação física (posição inverno, 4 L/min): elevação de **{num(vt['elevacao_temp_c'], 1)} °C**, "
        f"{num(vt['litros_agua_quente_dia'])} L/dia, {num(vt['energia_eletrica_dia_kwh'], 2)} kWh/dia",
        "",
        f"## Comparação das alternativas (mesma necessidade, 12 meses; finanças em {H} anos)",
        "",
        "| Alternativa | Renovável | kWh/ano da rede | Economia 1º ano | Investimento | Retorno simples (anos) "
        f"| Retorno descontado (anos) | VPL {H} anos | CO₂ evitado (kg/ano) | Alívio no pico (kW) | Telhado (m²) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for a in alts:
        md.append(f"| {a.codigo} – {a.nome} | {'sim' if a.renovavel else 'não'} | {num(a.energia_rede_kwh_ano)} | "
                  f"{brl(a.economia_ano1)} | {brl(a.investimento)} | {pb(a.payback_simples)} | "
                  f"{pb(a.payback_descontado)} | {brl(a.vpl_horizonte)} | {num(a.co2_evitado_kg_ano, 1)} | "
                  f"{num(a.reducao_pico_kw, 1)} | {num(a.area_telhado_m2, 1)} |")
    d = cp.por_codigo(r)
    md += [
        "",
        f"- Fração solar efetiva do aquecedor: {num(100 * d['B'].detalhes['fracao_solar'])}% "
        f"(potencial do coletor {num(d['B'].detalhes['potencial_coletor_kwh_ano'])} kWh/ano ≥ "
        f"demanda térmica {num(d['B'].detalhes['demanda_termica_kwh_ano'])} kWh/ano)",
        f"- Sistema FV dimensionado: {num(d['C'].detalhes['kwp'], 2)} kWp; cada kWh compensado vale "
        f"{num(100 * d['C'].detalhes['valor_do_kwh_compensado'])}% da tarifa (Lei 14.300/2022, Fio B 2026)",
        f"- Água economizada com banho de 5 min: {num(d['A'].agua_economizada_l_ano)} L/ano",
        "",
        "## Análise de sensibilidade",
        "",
        f"| Cenário | Economia A (R$/ano) | Retorno B (anos) | VPL B {H}a | Retorno C (anos) | VPL C {H}a | Retorno A+B (anos) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sens:
        md.append(f"| {row[0]} | {brl(row[1])} | {pb(row[2])} | {brl(row[3])} | {pb(row[4])} | {brl(row[5])} | {pb(row[6])} |")
    md += ["", "![Energia da rede](img/energia_rede.png)", "", "![Fluxo acumulado](img/fluxo_acumulado.png)", ""]
    (RAIZ / "docs" / "03_resultados_gerados.md").write_text("\n".join(md), encoding="utf-8")

    # ------------------------------------------------- tabela de premissas
    bruto = pr.carregar()
    nomes_grupo = {"familia": "Família", "chuveiro": "Chuveiro", "tarifa": "Tarifa", "solar_recurso": "Recurso solar",
                   "aquecedor_solar": "Aquecedor solar (B)", "fotovoltaico": "Fotovoltaico (C)",
                   "habitos": "Hábitos (A)", "financeiro": "Financeiro", "ambiental": "Ambiental"}
    linhas = [(DOC02_CABECALHO).strip(), "",
              "| Grupo | Premissa | Valor | Unidade | Tipo | Origem / justificativa | Ref. |",
              "|---|---|---:|---|---|---|---|"]
    for g, itens in bruto.items():
        for k, v in itens.items():
            val = v["valor"]
            val = num(val, 0) if float(val).is_integer() and abs(val) >= 1 else str(val).replace(".", ",")
            tipo = {"REAL": "**REAL**", "PUBLICO": "PÚBLICO", "ESTIMADO": "_ESTIMADO_"}[v["tipo"]]
            linhas.append(f"| {nomes_grupo.get(g, g)} | `{k}` | {val} | {v['unidade']} | {tipo} | {v['fonte']} | "
                          f"{', '.join(v['ref']) or '—'} |")
    linhas += ["", DOC02_RODAPE.strip(), ""]
    (RAIZ / "docs" / "02_dados_e_premissas.md").write_text("\n".join(linhas), encoding="utf-8")

    # ------------------------------------------------------------ graficos
    if plt is None:
        print("matplotlib nao instalado: tabelas e CSVs gerados, graficos ignorados.")
        return
    (RAIZ / "docs" / "img").mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4.2), facecolor=SUPERFICIE)
    _estilo(ax)
    curtos = {"BASE": "Chuveiro\n(atual)", "A": "Banho\n5 min", "B": "Aquecedor\nsolar",
              "C": "Placas\nfotovoltaicas", "A+B": "Banho 5 min\n+ aquecedor"}
    rotulos = [f"{a.codigo}\n{curtos[a.codigo]}" for a in alts]
    valores = [a.energia_rede_kwh_ano for a in alts]
    barras = ax.bar(rotulos, valores, color=AZUL, width=0.5)
    for b_, v in zip(barras, valores):
        ax.text(b_.get_x() + b_.get_width() / 2, v + 12, num(v), ha="center", color=TEXTO, fontsize=9)
    ax.set_title("Energia da rede usada no banho (kWh/ano)", loc="left", color=TEXTO, fontsize=11)
    ax.tick_params(axis="x", labelsize=8)
    fig.text(0.01, 0.01, "C gera a mesma energia de dia e a compensa na conta, mas o chuveiro segue puxando a rede à noite.",
             fontsize=7.5, color=TEXTO2)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(RAIZ / "docs" / "img" / "energia_rede.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.2), facecolor=SUPERFICIE)
    _estilo(ax)
    for cod, cor in (("B", AZUL), ("C", LARANJA), ("A+B", AQUA)):
        a = d[cod]
        pp = pr.com_ajustes(p)
        deg = p["fotovoltaico"]["degradacao_ano"] if cod == "C" else 0.0
        fluxo = c.fluxo_caixa(a.investimento, a.economia_ano1, a.manutencao_ano, pp, deg)
        acum, s = [], 0.0
        for v in fluxo:
            s += v
            acum.append(s)
        ax.plot(range(len(acum)), acum, color=cor, linewidth=2, label=f"{cod} – {a.nome}")
        ax.text(len(acum) - 0.8, acum[-1], cod, color=TEXTO, fontsize=9, va="center")
    ax.axhline(0, color=TEXTO2, linewidth=1)
    ax.set_xlabel("Ano", color=TEXTO2, fontsize=9)
    ax.set_title("Saldo acumulado do investimento (R$, sem desconto)", loc="left", color=TEXTO, fontsize=11)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(RAIZ / "docs" / "img" / "fluxo_acumulado.png", dpi=150)
    plt.close(fig)
    print("Resultados gerados em data/ e docs/.")


if __name__ == "__main__":
    main()
