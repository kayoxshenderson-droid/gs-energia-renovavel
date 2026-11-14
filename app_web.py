"""Citizen Assist AI - modulo de energia (interface web com Streamlit).

Uso:  pip install -r requirements.txt
      streamlit run app_web.py
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))
from energia import comparacao as cp  # noqa: E402
from energia.assistente import AssistenteEnergia, MENU, brl  # noqa: E402

st.set_page_config(page_title="Citizen Assist AI | Energia", page_icon="💡", layout="wide")

if "bot" not in st.session_state:
    st.session_state.bot = AssistenteEnergia()
    st.session_state.historico = [("assistant", "Ola! Sou o Citizen Assist AI.\n\n" + MENU)]
bot: AssistenteEnergia = st.session_state.bot

# ------------------------------------------------------------ barra lateral
with st.sidebar:
    st.header("Seu perfil")
    f, ch = bot.p["familia"], bot.p["chuveiro"]
    f["pessoas"] = st.number_input("Pessoas na casa", 1, 15, int(f["pessoas"]))
    f["duracao_banho_min"] = st.slider("Minutos de banho (por pessoa)", 2.0, 30.0, float(f["duracao_banho_min"]), 0.5)
    ch["potencia_inverno_w"] = st.select_slider("Potencia do chuveiro (W)", [4400, 5500, 6800, 7500, 7800],
                                                value=int(ch["potencia_inverno_w"]) if int(ch["potencia_inverno_w"]) in
                                                [4400, 5500, 6800, 7500, 7800] else 5500)
    f["consumo_total_casa_kwh_mes"] = st.number_input("Consumo da casa (kWh/mes, veja a conta)", 30, 2000,
                                                      int(f["consumo_total_casa_kwh_mes"]))
    usar_tarifa = st.checkbox("Informar minha tarifa (R$/kWh)")
    bot.tarifa_usuario = st.number_input("Tarifa R$/kWh (valor da conta / kWh)", 0.30, 2.50, 0.95, 0.01) if usar_tarifa else None
    bot.tarifa_social = st.checkbox("Tenho Tarifa Social", value=bot.tarifa_social)
    st.caption("Valores padrao: familia de 4 pessoas atendida pela Enel SP. Tudo e estimativa, nao garantia.")

st.title("💡 Citizen Assist AI — Energia no banho")
aba_chat, aba_comp = st.tabs(["Conversar", "Comparar alternativas"])

# --------------------------------------------------------------------- chat
with aba_chat:
    for papel, texto in st.session_state.historico:
        with st.chat_message(papel):
            st.text(texto)
    sugestoes = ["Quanto o chuveiro gasta?", "Como economizar no banho?", "Vale a pena aquecedor solar?",
                 "E placa solar?", "Compare as opcoes", "Tarifa social", "Impacto ambiental", "Quais os limites?"]
    cols = st.columns(4)
    clicada = None
    for i, s in enumerate(sugestoes):
        if cols[i % 4].button(s, width="stretch"):
            clicada = s
    pergunta = st.chat_input("Pergunte sobre energia do banho...") or clicada
    if pergunta:
        st.session_state.historico.append(("user", pergunta))
        st.session_state.historico.append(("assistant", bot.responder(pergunta)))
        st.rerun()

# --------------------------------------------------------------- comparacao
with aba_comp:
    r = cp.comparar(bot.p, bot.tarifa_social, bot.tarifa_usuario)
    st.markdown(f"**Necessidade:** agua quente do banho · **Periodo:** 12 meses · "
                f"**Horizonte financeiro:** {bot.p['financeiro']['horizonte_anos']} anos · "
                f"**Tarifa usada:** {brl(r['tarifa_r_kwh'])}/kWh")
    linhas = []
    for a in r["alternativas"]:
        linhas.append({
            "Opcao": f"{a.codigo} - {a.nome}", "Renovavel": "sim" if a.renovavel else "nao",
            "kWh/ano da rede": round(a.energia_rede_kwh_ano), "Economia 1o ano (R$)": round(a.economia_ano1, 2),
            "Investimento (R$)": round(a.investimento), "Retorno simples (anos)":
                (None if a.payback_simples is None else round(a.payback_simples, 1)),
            "VPL (R$)": round(a.vpl_horizonte), "CO2 evitado (kg/ano)": round(a.co2_evitado_kg_ano, 1),
            "Alivio no pico (kW)": round(a.reducao_pico_kw, 2), "Telhado (m2)": round(a.area_telhado_m2, 1),
        })
    df = pd.DataFrame(linhas)
    st.dataframe(df, width="stretch", hide_index=True)
    st.bar_chart(df.set_index("Opcao")[["kWh/ano da rede"]])
    st.info("Estimativas para o perfil da barra lateral. Fontes e premissas em data/premissas.json e docs/.")
