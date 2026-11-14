# Citizen Assist AI — Módulo de Energia: “Banho mais barato e sustentável”

> **Global Solution 2026.2 · Ciência da Computação (1CC)**
> **Contribuição da disciplina: Soluções em Energias Renováveis e Sustentáveis**

## Integrante

| Nome completo | RM |
|---|---|
| _[SEU NOME COMPLETO]_ | _[SEU RM]_ |

## O problema e o público

**Público:** famílias de baixa renda da Grande São Paulo (área da Enel SP), muitas delas inscritas no CadÚnico e com direito à Tarifa Social.

**Necessidade energética:** aquecer a água do banho. O chuveiro elétrico costuma ser o **maior consumidor isolado de uma casa** (cerca de 24% do consumo residencial no Brasil, segundo a PPH Eletrobras/Procel) e liga justamente no **horário de pico (18h–21h)**. Para a família-tipo deste estudo (4 pessoas, banhos de 8 min, chuveiro de 5.500 W), ele responde por **~73 kWh/mês, cerca de 36% da conta** e **~R$ 830 por ano**.

**Como o assistente ajuda:** o cidadão pergunta em linguagem simples (“quanto meu chuveiro gasta?”, “vale a pena aquecedor solar?”) e recebe uma orientação **calculada para o perfil dele**, com os números que a sustentam, as **fontes** e os **limites** da estimativa. Detalhes em [docs/01_contexto.md](docs/01_contexto.md).

## Funcionalidades de energia

1. **Diagnóstico do banho** — calcula kWh/mês, R$/mês e participação na conta (E = P × t), com conferência física pelo calor da água (Q = m·c·ΔT).
2. **Comparação de alternativas** para a mesma necessidade e o mesmo período (12 meses; finanças em 15 anos):
   - **A** – Banho consciente (5 min), sem custo;
   - **B** – **Aquecedor solar de água** (fonte renovável) com o chuveiro como apoio;
   - **C** – **Placas fotovoltaicas** (fonte renovável) dimensionadas para o banho;
   - **A+B** – combinação recomendada.
3. **Custos, viabilidade e impactos** — investimento, economia, retorno simples e descontado, VPL, CO₂ evitado, alívio no horário de pico, água economizada, área de telhado.
4. **Tarifa Social** — considera a gratuidade dos primeiros 80 kWh/mês (Lei 15.235/2025) no cálculo da economia.
5. **Personalização na conversa** — “somos 3 pessoas, banho de 10 minutos, chuveiro 7500 W, tarifa R$ 1,05, tenho tarifa social” atualiza todas as contas; o assistente avisa se os dados ficarem incoerentes.
6. **Fontes e limites em toda resposta** — nenhuma estimativa é apresentada como garantida.

## Principais resultados (perfil-base)

| Alternativa | kWh/ano da rede | Economia 1º ano | Investimento | Retorno simples | VPL 15 anos | Alívio no pico |
|---|---:|---:|---:|---:|---:|---:|
| Situação atual | 872 | — | — | — | — | — |
| A – Banho de 5 min | 545 | R$ 311 | R$ 0 | imediato | R$ 3.578 | 0 kW |
| B – Aquecedor solar | 262 | R$ 581 | R$ 4.500 | 7,6 anos | R$ 1.323 | 3,8 kW |
| C – Fotovoltaica | 872* | R$ 691 | R$ 5.000 | 7,2 anos | R$ 1.831 | 0 kW |
| **A+B – Recomendada** | **164** | **R$ 675** | **R$ 4.500** | **6,6 anos** | **R$ 2.397** | **3,8 kW** |

\* A FV gera ~872 kWh/ano de dia e compensa na conta, mas o chuveiro continua usando a rede à noite.

**Recomendação:** começar já pelo banho consciente (custo zero, −38% de energia e 17,5 mil litros de água/ano). Havendo telhado adequado e recursos ou programa de apoio, o **aquecedor solar** é a opção renovável que melhor resolve *esta* necessidade: tem retorno parecido com o da FV, mas também **tira o chuveiro do horário de pico**, enquanto a FV não alivia o pico noturno e quase não reduz CO₂ numa rede já limpa como a brasileira. Justificativa completa em [docs/04_comparacao_e_justificativas.md](docs/04_comparacao_e_justificativas.md).

![Energia da rede](docs/img/energia_rede.png)

## Como executar

Requisitos: Python 3.10+.

```bash
git clone <URL-DO-REPOSITORIO>
cd citizen-assist-energia
pip install -r requirements.txt

# 1) Assistente no terminal (só precisa da biblioteca padrão)
python app_cli.py
python app_cli.py "vale a pena aquecedor solar?"     # pergunta única

# 2) Assistente com interface web (chat + tabela comparativa)
streamlit run app_web.py

# 3) Recalcular tabelas, CSVs e gráficos a partir das premissas
python scripts/gerar_relatorio.py

# 4) Testes automatizados (fórmulas, física e coerência análise ↔ respostas)
python -m pytest -q
```

Perguntas para testar: “Quanto o chuveiro gasta por mês?”, “Como economizar no banho?”, “Vale a pena um aquecedor solar?”, “E placa solar?”, “Compare as opções”, “Como funciona a Tarifa Social?”, “Qual o impacto ambiental?”, “Quais as fontes?”, “Isso é garantido?”.

## Estrutura do repositório

```
├── app_cli.py                  # assistente no terminal
├── app_web.py                  # assistente web (Streamlit)
├── src/energia/
│   ├── premissas.py            # leitura das premissas
│   ├── calculos.py             # fórmulas de energia, tarifa, solar, finanças e CO2
│   ├── comparacao.py           # comparação das alternativas (mesma necessidade/período)
│   └── assistente.py           # intenções, respostas, fontes e limites
├── data/
│   ├── premissas.json          # TODOS os dados, com unidade, tipo (REAL/PÚBLICO/ESTIMADO) e fonte
│   ├── resultados_alternativas.csv
│   └── sensibilidade.csv
├── scripts/gerar_relatorio.py  # gera resultados, CSVs e gráficos
├── tests/test_energia.py       # 28 testes automatizados
└── docs/
    ├── 01_contexto.md                    # público, necessidade e papel do assistente
    ├── 02_dados_e_premissas.md           # origem, unidades, período e premissas
    ├── 03_resultados_gerados.md          # cálculos e tabelas (gerado por script)
    ├── 04_comparacao_e_justificativas.md # custos, viabilidade, impactos e recomendação
    ├── 05_referencias.md                 # fontes verificáveis com links
    ├── 06_limitacoes.md                  # condições e limites das estimativas
    ├── 07_testes_com_usuarios.md         # protocolo, registros e ajustes
    ├── 08_roteiro_video.md               # roteiro do vídeo de 3 minutos
    └── 09_uso_de_ia.md                   # declaração de uso de IA e verificação
```

## Integração com o Citizen Assist AI

O módulo é um pacote Python independente (`src/energia`). Qualquer front-end do Citizen Assist AI (chat web, WhatsApp, app) só precisa chamar:

```python
from energia.assistente import AssistenteEnergia
bot = AssistenteEnergia()
resposta = bot.responder("vale a pena aquecedor solar?")
```

As respostas são **geradas a partir da mesma análise** (`comparacao.comparar`) documentada em `docs/`; os testes garantem que o número dito ao usuário é o número calculado.

## Referências e limitações

Fontes em [docs/05_referencias.md](docs/05_referencias.md) e limites em [docs/06_limitacoes.md](docs/06_limitacoes.md). **Todos os valores são estimativas para um perfil típico, não resultados garantidos.**
