"""Modulo de energia do Citizen Assist AI.

Assistente de conversa por regras (intencoes por palavras-chave) que responde
com numeros calculados em `comparacao.comparar()`. Assim, toda orientacao dada
ao usuario sai da mesma analise documentada em docs/ e nunca de texto fixo.

Cada resposta traz: (1) a orientacao em linguagem simples, (2) os numeros que a
sustentam, (3) as fontes e (4) os limites da estimativa.
"""
from __future__ import annotations

import re
import unicodedata

from . import calculos as c
from . import comparacao as cp
from . import premissas as pr

# ------------------------------------------------------------------ fontes
REFERENCIAS = {
    "R1": "ANEEL - Reajuste Tarifário Enel SP 2025 (tarifa B1 R$ 725,18/MWh)",
    "R2": "ANEEL - Reajuste Tarifário Enel SP 2026 (+9,02% residencial, desde 04/07/2026)",
    "R3": "Eletrobras/Procel - Pesquisa de Posse e Hábitos de Uso (PPH)",
    "R4": "INMETRO - Programa Brasileiro de Etiquetagem (chuveiros)",
    "R5": "Lei 15.235/2025 - Tarifa Social (100% de desconto até 80 kWh/mês)",
    "R6": "CRESESB/CEPEL - SunData; INPE - Atlas Brasileiro de Energia Solar",
    "R7": "Preços de mercado de kits de aquecedor solar 200 L (2026)",
    "R8": "ABRASOL/ABRAVA e literatura sobre aquecimento solar residencial",
    "R9": "Greener - Estudo Estratégico de Geração Distribuída (2025/2026)",
    "R10": "EPE - Anuário Estatístico de Energia Elétrica",
    "R11": "Conta de luz Enel SP (tributos: ICMS, PIS/COFINS)",
    "R12": "Lei 14.300/2022 - Marco legal da micro e minigeração distribuída",
    "R13": "MCTI/SIRENE - Fatores de emissão de CO₂ do SIN",
    "R14": "IPCC AR5 - Anexo III (emissões de ciclo de vida)",
}

LIMITE_PADRAO = ("Estes números são ESTIMATIVAS para o perfil informado, não valores garantidos. "
                 "A economia real depende do seu chuveiro, do tempo de banho, da tarifa do mês "
                 "(bandeiras) e, no caso solar, do clima e da instalação.")

MENU = (
    "Posso ajudar com a energia do banho, que costuma ser o maior gasto de luz da casa. Pergunte, por exemplo:\n"
    "  1. Quanto o chuveiro gasta por mês?\n"
    "  2. Como economizar no banho?\n"
    "  3. Vale a pena um aquecedor solar?\n"
    "  4. E placa solar (fotovoltaica)?\n"
    "  5. Compare as opções\n"
    "  6. Como funciona a Tarifa Social?\n"
    "  7. Qual é o impacto ambiental?\n"
    "  8. Quais são as fontes? / Quais os limites dessas contas?\n"
    "Para ajustar ao seu caso, diga algo como: '3 pessoas, banho de 10 minutos, chuveiro 7500 W, "
    "tarifa R$ 1,05, consumo 150 kWh, tenho tarifa social'."
)


def _norm(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto.lower())
    return "".join(ch for ch in t if not unicodedata.combining(ch))


def brl(v: float) -> str:
    s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"-R$ {s}" if v < 0 else f"R$ {s}"


def num(v: float, casas: int = 0) -> str:
    s = f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def anos(v: float | None) -> str:
    if v is None:
        return "mais que o horizonte analisado"
    if v == 0:
        return "imediato (sem custo)"
    return f"cerca de {num(v, 1)} anos"


class AssistenteEnergia:
    def __init__(self, caminho_premissas=pr.ARQUIVO_PADRAO):
        self.bruto = pr.carregar(caminho_premissas)
        self.p = pr.valores(self.bruto)
        self.tarifa_social = False
        self.tarifa_usuario: float | None = None

    # -------------------------------------------------------------- perfil
    def atualizar_perfil(self, texto: str) -> list[str]:
        """Extrai dados do texto do usuário e atualiza o perfil. Retorna o que mudou."""
        t = _norm(texto)
        mudou = []
        regras = [
            (r"(\d+)\s*(?:pessoas|moradores|pessoa)", "familia", "pessoas", int, "pessoas"),
            (r"(\d+(?:[.,]\d+)?)\s*(?:minutos|min)\b", "familia", "duracao_banho_min", float, "minutos de banho"),
            (r"(\d{3,5})\s*(?:w|watts?)\b", "chuveiro", "potencia_inverno_w", float, "W no chuveiro"),
            (r"(\d+(?:[.,]\d+)?)\s*kwh", "familia", "consumo_total_casa_kwh_mes", float, "kWh/mês na casa"),
        ]
        for padrao, grupo, chave, tipo, rotulo in regras:
            m = re.search(padrao, t)
            if m:
                v = tipo(float(m.group(1).replace(",", ".")))
                if v > 0:
                    if chave == "potencia_inverno_w":
                        ch = self.p["chuveiro"]
                        ch["potencia_verao_w"] = v * ch["potencia_verao_w"] / ch["potencia_inverno_w"]
                    self.p[grupo][chave] = v
                    mudou.append(f"{num(v, 0 if float(v).is_integer() else 1)} {rotulo}")
        m = re.search(r"(?:r\$|tarifa(?: de)?)\s*(\d+[.,]\d+)", t)
        if m:
            v = float(m.group(1).replace(",", "."))
            if 0.2 < v < 3:
                self.tarifa_usuario = v
                mudou.append(f"tarifa de {brl(v)}/kWh")
        if re.search(r"(nao tenho|sem) tarifa social", t):
            self.tarifa_social = False
            mudou.append("sem Tarifa Social")
        elif re.search(r"(tenho|com|recebo) (a )?tarifa social|sou (do )?cadunico|tenho cadunico", t):
            self.tarifa_social = True
            mudou.append("com Tarifa Social")
        return mudou

    def alerta_consistencia(self) -> str:
        """Avisa se o chuveiro calculado passa do consumo total informado da casa."""
        chuveiro = c.energia_chuveiro_kwh_mes(self.p)
        total = self.p["familia"]["consumo_total_casa_kwh_mes"]
        if chuveiro > 0.8 * total:
            return (f"Aviso: pelo perfil, só o chuveiro daria ~{num(chuveiro)} kWh/mês, perto ou acima do total "
                    f"da casa ({num(total)} kWh). Confira os minutos de banho, a potência e o consumo da conta.\n")
        return ""

    def _resultado(self) -> dict:
        return cp.comparar(self.p, self.tarifa_social, self.tarifa_usuario)

    def _tarifa(self) -> float:
        return self.tarifa_usuario or c.tarifa_final_r_kwh(self.p)

    def _rodape(self, refs: list[str], limite: str = LIMITE_PADRAO) -> str:
        fontes = "; ".join(f"[{r}] {REFERENCIAS[r]}" for r in refs)
        return f"\n\nFontes: {fontes}\nAtenção: {limite}"

    # ------------------------------------------------------------ respostas
    def r_consumo(self) -> str:
        r = self._resultado()
        b = cp.por_codigo(r)["BASE"]
        f = self.p["familia"]
        pot = c.potencia_media_chuveiro_w(self.p)
        kwh_mes = b.energia_rede_kwh_ano / 12
        custo_mes = c.custo_energia_mes(kwh_mes, self.p, False, self._tarifa())
        vt = r["verificacao_termica"]
        return (
            f"Para {f['pessoas']} pessoas com banho de {num(f['duracao_banho_min'], 1)} min, o chuveiro usa cerca de "
            f"{num(kwh_mes)} kWh por mês ({num(b.energia_rede_kwh_ano)} kWh por ano).\n"
            f"Conta: potência média {num(pot)} W x {num(c.horas_banho_mes(self.p), 1)} h de banho por mês = "
            f"{num(kwh_mes, 1)} kWh.\n"
            f"Na sua tarifa ({brl(self._tarifa())}/kWh) isso custa perto de {brl(custo_mes)} por mês, "
            f"cerca de {num(100 * r['participacao_chuveiro_na_conta'])}% do consumo da casa.\n"
            f"Conferência física: na posição inverno o chuveiro esquenta a água em ~{num(vt['elevacao_temp_c'])} C "
            f"(de {num(self.p['chuveiro']['temp_agua_fria_c'])} para ~{num(vt['temp_saida_c'])} C)."
            + self._rodape(["R1", "R2", "R3", "R4"])
        )

    def r_dicas(self) -> str:
        a = cp.por_codigo(self._resultado())["A"]
        meta = self.p["habitos"]["duracao_banho_meta_min"]
        return (
            f"O jeito mais rápido e sem custo: banhos de {num(meta)} minutos.\n"
            f"- Economia estimada: {num(a.kwh_evitados_ano)} kWh/ano (-{num(100 * a.detalhes['reducao_percentual'])}%), "
            f"cerca de {brl(a.economia_ano1 / 12)} por mês e {num(a.agua_economizada_l_ano / 1000)} mil litros de água por ano.\n"
            "- Use a posição 'verão' sempre que o dia permitir: ela usa ~40% menos potência.\n"
            "- Desligue o chuveiro ao se ensaboar e evite banhos entre 18h e 21h quando puder (horário de pico da rede).\n"
            "- Não troque a resistência por uma mais potente nem use 'gambiarra' na fiação: além de gastar mais, há risco de choque e incêndio."
            + self._rodape(["R3", "R4"])
        )

    def r_solar_termico(self) -> str:
        r = self._resultado()
        b = cp.por_codigo(r)["B"]
        ab = cp.por_codigo(r)["A+B"]
        return (
            "Aquecedor solar de água (fonte renovável): placas no telhado esquentam a água com o sol e "
            "ela fica guardada num reservatório (boiler). O chuveiro elétrico fica só como apoio em dias nublados.\n"
            f"- O sol deve cobrir ~{num(100 * b.detalhes['fracao_solar'])}% da água quente do ano.\n"
            f"- Economia estimada: {num(b.kwh_evitados_ano)} kWh/ano, ~{brl(b.economia_ano1)} no 1o ano.\n"
            f"- Investimento de referência: {brl(b.investimento)} (kit 200 L instalado; mercado varia de R$ 3 mil a R$ 8 mil).\n"
            f"- Retorno simples: {anos(b.payback_simples)}; valor presente líquido em "
            f"{self.p['financeiro']['horizonte_anos']} anos: {brl(b.vpl_horizonte)}.\n"
            f"- Junto com banhos curtos, o retorno cai para {anos(ab.payback_simples)}.\n"
            "- Vantagem extra: tira o chuveiro do horário de pico na maior parte dos dias.\n"
            "Precisa de: telhado com sol (face norte, sem sombra), ~2 m² de área, estrutura que aguente o "
            "reservatório cheio (~250 kg) e instalador qualificado."
            + self._rodape(["R6", "R7", "R8"],
                           LIMITE_PADRAO + " O preço muda muito por região e tipo de telhado; peça 3 orçamentos.")
        )

    def r_fotovoltaico(self) -> str:
        cc = cp.por_codigo(self._resultado())["C"]
        d = cc.detalhes
        return (
            "Placa solar fotovoltaica (fonte renovável): gera eletricidade de dia, injeta na rede e vira "
            "crédito na conta (Lei 14.300/2022).\n"
            f"- Para cobrir o banho seriam ~{num(d['kwp'], 2)} kWp (~{num(cc.area_telhado_m2, 1)} m² de telhado), "
            f"gerando ~{num(d['geracao_kwh_ano'])} kWh/ano.\n"
            f"- Cada kWh compensado vale ~{num(100 * d['valor_do_kwh_compensado'])}% da tarifa, porque em 2026 novos "
            "sistemas pagam parte do 'Fio B'.\n"
            f"- Economia estimada: ~{brl(cc.economia_ano1)} no 1o ano; investimento {brl(cc.investimento)} "
            "(sistemas pequenos custam mais por watt).\n"
            f"- Retorno simples: {anos(cc.payback_simples)}; VPL em {self.p['financeiro']['horizonte_anos']} anos: {brl(cc.vpl_horizonte)}.\n"
            "- Limite importante: o banho acontece à noite, então o chuveiro continua puxando a rede no horário de pico. "
            "A placa reduz a conta, mas não a sobrecarga da rede.\n"
            "Faz mais sentido quando a ideia é abater o consumo da casa toda, não só do chuveiro."
            + self._rodape(["R6", "R9", "R12"],
                           LIMITE_PADRAO + " As regras de compensação e o Fio B mudam até 2029.")
        )

    def r_comparar(self) -> str:
        r = self._resultado()
        linhas = ["Comparação para a MESMA necessidade (água quente do banho) e o MESMO período (1 ano):",
                  f"{'Opção':<44}{'kWh/ano rede':>13}{'Economia/ano':>15}{'Investimento':>15}{'Retorno':>10}"]
        for a in r["alternativas"]:
            ret = "-" if a.codigo == "BASE" else ("imediato" if a.payback_simples == 0 else
                                                   (f"{num(a.payback_simples, 1)} a" if a.payback_simples else "> horiz."))
            rede = a.energia_rede_kwh_ano
            linhas.append(f"{(a.codigo + ' ' + a.nome)[:43]:<44}{num(rede):>13}{brl(a.economia_ano1):>15}"
                          f"{brl(a.investimento):>15}{ret:>10}")
        linhas.append(
            "\nRecomendação: comece já pelo banho consciente (custo zero). Se houver telhado adequado e "
            "dinheiro ou programa de apoio, o aquecedor solar é a opção renovável que melhor resolve o "
            "banho, porque também alivia o horário de pico. A placa fotovoltaica tem retorno parecido, "
            "mas não tira o chuveiro do pico e compensa mais para quem quer abater a conta inteira."
        )
        return "\n".join(linhas) + self._rodape(["R1", "R2", "R7", "R9", "R12"])

    def r_tarifa_social(self) -> str:
        total = self.p["familia"]["consumo_total_casa_kwh_mes"]
        franquia = self.p["tarifa"]["franquia_tarifa_social_kwh"]
        a = cp.por_codigo(cp.comparar(self.p, True, self.tarifa_usuario))["A"]
        msg = (
            f"Desde julho de 2025, quem tem Tarifa Social não paga a energia dos primeiros {franquia} kWh do mês; "
            "o que passar disso é cobrado normalmente.\n"
            "Quem pode: famílias no CadÚnico com renda de até meio salário mínimo por pessoa, beneficiários do BPC, "
            "entre outros casos. A conta precisa estar no nome de alguém da família e o cadastro, atualizado.\n"
            f"Para a sua casa ({num(total)} kWh/mês), economizar no banho reduz a parte acima de {franquia} kWh: "
            f"com banhos de {num(self.p['habitos']['duracao_banho_meta_min'])} min a economia fica perto de {brl(a.economia_ano1 / 12)}/mês."
        )
        if total - a.kwh_evitados_ano / 12 < franquia:
            msg += (f"\nComo seu consumo ficaria abaixo de {franquia} kWh, parte da economia não aparece em reais, "
                    "mas continua valendo para o meio ambiente e para a rede.")
        return msg + self._rodape(["R5"], "As regras do benefício podem mudar; confirme no CRAS ou com a distribuidora.")

    def r_ambiental(self) -> str:
        r = self._resultado()
        d = cp.por_codigo(r)
        fe = self.p["ambiental"]["fator_emissao_sin_kg_kwh"]
        return (
            f"A eletricidade brasileira é bem limpa (~{num(fe * 1000, 1)} kg de CO₂ por MWh), então o ganho em CO₂ é pequeno:\n"
            f"- Banho consciente: evita ~{num(d['A'].co2_evitado_kg_ano, 1)} kg CO₂/ano e {num(d['A'].agua_economizada_l_ano / 1000)} mil litros de água.\n"
            f"- Aquecedor solar: evita ~{num(d['B'].co2_evitado_kg_ano, 1)} kg CO₂/ano e retira ate ~{num(d['B'].reducao_pico_kw, 1)} kW "
            "do horário de pico, quando o país mais aciona termelétricas.\n"
            f"- Placa fotovoltaica: saldo de ~{num(d['C'].co2_evitado_kg_ano, 1)} kg CO₂/ano, praticamente neutro, porque as emissões "
            "de fabricar os painéis são parecidas com as da rede brasileira.\n"
            "Conclusão: aqui o maior benefício ambiental vem de gastar menos água e energia e de aliviar o pico, "
            "mais do que do CO₂. Painéis e coletores devem ir para reciclagem no fim da vida útil."
            + self._rodape(["R13", "R14", "R3"], "Os fatores de emissão variam mês a mês com as chuvas e o uso de termelétricas.")
        )

    def r_fontes(self) -> str:
        linhas = ["Fontes usadas nas contas (detalhes e links em docs/05_referencias.md):"]
        linhas += [f"[{k}] {v}" for k, v in REFERENCIAS.items()]
        estimados = [f"{g}.{k}" for g, itens in self.bruto.items() for k, v in itens.items() if v["tipo"] == "ESTIMADO"]
        linhas.append(f"\nValores ESTIMADOS pela equipe (identificados em data/premissas.json): {', '.join(estimados)}.")
        return "\n".join(linhas)

    def r_limites(self) -> str:
        return (
            "Limites das estimativas:\n"
            "- Não medimos sua casa: usamos um perfil típico e os dados que voce informar.\n"
            "- A tarifa é calculada a partir dos valores homologados pela ANEEL com tributos estimados; bandeiras "
            "tarifárias e a taxa de iluminação pública não entram.\n"
            "- A produção solar varia com o clima, sombra, inclinação e limpeza; usamos a média anual de São Paulo.\n"
            "- Preços de equipamentos mudam muito; os valores são referências de mercado de 2026.\n"
            "- Economia, geração e retorno são projeções, não promessas. Antes de comprar, peça orçamentos e um projeto de profissional habilitado.\n"
            "- O assistente não substitui eletricista: instalação elétrica e hidráulica exige profissional."
        )

    def r_perfil(self, mudou: list[str]) -> str:
        r = self._resultado()
        b, a, s = (cp.por_codigo(r)[k] for k in ("BASE", "A", "B"))
        return (
            f"Anotei: {', '.join(mudou)}.\n" + self.alerta_consistencia() +
            f""
            f"Com isso, o banho usa ~{num(b.energia_rede_kwh_ano / 12)} kWh/mês. Banho curto economizaria ~{brl(a.economia_ano1 / 12)}/mês; "
            f"aquecedor solar, ~{brl(s.economia_ano1 / 12)}/mês. Pergunte 'compare as opções' para ver tudo."
        )

    # ------------------------------------------------------------- roteador
    INTENCOES = [
        ("limites", r"limit|garant|confiav|certeza|margem de erro|e confiavel"),
        ("fontes", r"fonte|referencia|de onde|origem dos dados"),
        ("tarifa_social", r"tarifa social|baixa renda|cadunico|luz do povo|desconto"),
        ("ambiental", r"ambient|co2|carbono|emiss|sustentab|planeta|poluic"),
        ("comparar", r"compar|melhor opcao|qual (e )?(a )?melhor|qual escolher|vale mais|opcoes"),
        ("fotovoltaico", r"fotovolt|placa solar|painel|paineis|placas solares|gerar energia|energia solar"),
        ("solar_termico", r"aquecedor solar|solar termic|boiler|coletor|aquecer .*sol|agua .*sol"),
        ("dicas", r"econom|reduz|diminu|dica|gastar menos|baixar a conta"),
        ("consumo", r"quanto .*(gast|consum|custa)|consumo|gasta|kwh do chuveiro|chuveiro"),
        ("ajuda", r"^(oi|ola|bom dia|boa tarde|boa noite|ajuda|menu|inicio)\b|o que voce faz"),
    ]

    def responder(self, texto: str) -> str:
        mudou = self.atualizar_perfil(texto)
        t = _norm(texto)
        for nome, padrao in self.INTENCOES:
            if re.search(padrao, t):
                resposta = getattr(self, f"r_{nome}")() if nome != "ajuda" else MENU
                if mudou and nome != "ajuda":
                    resposta = (f"(Perfil atualizado: {', '.join(mudou)}.)\n" + self.alerta_consistencia()
                                + resposta)
                return resposta
        if mudou:
            return self.r_perfil(mudou)
        return "Não entendi bem. " + MENU
