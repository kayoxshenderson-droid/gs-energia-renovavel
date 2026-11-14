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

| Grupo | Premissa | Valor | Unidade | Tipo | Origem / justificativa | Ref. |
|---|---|---:|---|---|---|---|
| Família | `pessoas` | 4 | pessoas | _ESTIMADO_ | Perfil-alvo definido pela equipe (família de baixa renda típica) | — |
| Família | `banhos_pessoa_dia` | 1 | banhos/dia | _ESTIMADO_ | Hábito usual | — |
| Família | `duracao_banho_min` | 8 | min | PÚBLICO | PPH Procel/Eletrobras estimou banho médio entre 8 e 10 min; usado o limite inferior | R3 |
| Família | `dias_mes` | 30 | dias | _ESTIMADO_ | Mês comercial | — |
| Família | `consumo_total_casa_kwh_mes` | 200 | kWh/mês | _ESTIMADO_ | Ordem de grandeza do consumo residencial médio no Sudeste (EPE); o usuário pode informar o da própria conta | R10 |
| Chuveiro | `potencia_inverno_w` | 5.500 | W | PÚBLICO | Potência nominal comum de chuveiros 220 V vendidos no Brasil (etiqueta INMETRO) | R4 |
| Chuveiro | `potencia_verao_w` | 3.200 | W | PÚBLICO | Posição 'verão' típica de chuveiros de 5500 W | R4 |
| Chuveiro | `meses_posicao_inverno` | 7 | meses/ano | _ESTIMADO_ | Abril a outubro em São Paulo (meses mais frios) | — |
| Chuveiro | `vazao_l_min` | 4 | L/min | _ESTIMADO_ | Vazão típica de chuveiro elétrico na posição inverno; usada só na verificação física | — |
| Chuveiro | `temp_agua_fria_c` | 20 | °C | _ESTIMADO_ | Temperatura média anual da água da rede em SP | — |
| Chuveiro | `eficiencia_chuveiro` | 0,95 | - | PÚBLICO | Chuveiros elétricos convertem quase toda a energia em calor na água (classe A do PBE) | R4 |
| Tarifa | `tarifa_b1_2025_sem_impostos` | 0,72518 | R$/kWh | **REAL** | Tarifa B1 residencial Enel SP homologada pela ANEEL em 2025 (R$ 725,18/MWh) | R1 |
| Tarifa | `reajuste_b1_2026` | 0,0902 | fração | **REAL** | Reajuste residencial B1 Enel SP aprovado pela ANEEL em 30/06/2026, vigente desde 04/07/2026 | R2 |
| Tarifa | `icms` | 0,12 | fração | _ESTIMADO_ | Alíquota de ICMS residencial em SP na faixa de consumo do perfil; conferir na conta | R11 |
| Tarifa | `pis_cofins` | 0,05 | fração | _ESTIMADO_ | PIS/COFINS variam mês a mês; valor médio aproximado | R11 |
| Tarifa | `franquia_tarifa_social_kwh` | 80 | kWh/mês | **REAL** | Lei 15.235/2025: desconto de 100% até 80 kWh/mês e 0% acima para a Tarifa Social | R5 |
| Recurso solar | `irradiacao_kwh_m2_dia` | 4,5 | kWh/m²·dia | PÚBLICO | Média anual no plano inclinado para a cidade de São Paulo (ordem de grandeza CRESESB/SunData e Atlas Brasileiro de Energia Solar) | R6 |
| Aquecedor solar (B) | `custo_instalado` | 4.500 | R$ | PÚBLICO | Kit 200 L com coletor ~R$ 4.180 no varejo e caso instalado de R$ 4.180 (UFRJ); faixa de mercado R$ 3.000 a R$ 8.000 | R7 |
| Aquecedor solar (B) | `area_coletor_m2` | 2 | m² | PÚBLICO | Kit compacto residencial 200 L com 1 a 2 coletores | R7 |
| Aquecedor solar (B) | `volume_reservatorio_l` | 200 | L | PÚBLICO | Reservatório de 200 L é a referência de mercado para 3-4 pessoas | R7 |
| Aquecedor solar (B) | `eficiencia_sistema` | 0,35 | - | _ESTIMADO_ | Rendimento médio anual coletor plano + perdas no reservatório (conservador) | R8 |
| Aquecedor solar (B) | `fracao_solar` | 0,7 | - | _ESTIMADO_ | Parcela anual da água quente atendida pelo sol em SP; o chuveiro elétrico cobre dias nublados | R8 |
| Aquecedor solar (B) | `manutencao_ano` | 100 | R$/ano | _ESTIMADO_ | Limpeza do coletor e revisão básica | — |
| Aquecedor solar (B) | `vida_util_anos` | 15 | anos | _ESTIMADO_ | Vida útil típica informada por fabricantes | — |
| Fotovoltaico (C) | `custo_wp` | 4 | R$/Wp | _ESTIMADO_ | Greener: sistema residencial de 4 kWp ~R$ 2,84/Wp (jun/2025), alta de 7% no 1o sem/2026; sistemas menores custam mais por Wp | R9 |
| Fotovoltaico (C) | `custo_minimo` | 5.000 | R$ | _ESTIMADO_ | Custo mínimo de um sistema conectado (inversor/microinversor, projeto, homologação, mão de obra) | R9 |
| Fotovoltaico (C) | `performance_ratio` | 0,75 | - | _ESTIMADO_ | Perdas por temperatura, sujeira, cabos e inversor | R6 |
| Fotovoltaico (C) | `degradacao_ano` | 0,005 | fração/ano | PÚBLICO | Garantia típica de módulos (~0,5%/ano) | — |
| Fotovoltaico (C) | `fio_b_parcela_tarifa` | 0,28 | fração | _ESTIMADO_ | Participação aproximada da TUSD Fio B na tarifa | R12 |
| Fotovoltaico (C) | `fio_b_cobrado_2026` | 0,6 | fração | **REAL** | Lei 14.300/2022: novos sistemas pagam 60% do Fio B sobre a energia compensada em 2026 | R12 |
| Fotovoltaico (C) | `manutencao_ano` | 100 | R$/ano | _ESTIMADO_ | Limpeza dos módulos | — |
| Fotovoltaico (C) | `area_m2_por_kwp` | 5 | m²/kWp | PÚBLICO | Módulos de ~21% de eficiência | — |
| Hábitos (A) | `duracao_banho_meta_min` | 5 | min | _ESTIMADO_ | Meta de banho curto recomendada em campanhas de uso consciente | R3 |
| Hábitos (A) | `custo_implantacao` | 0 | R$ | _ESTIMADO_ | Mudança de hábito, sem compra | — |
| Financeiro | `horizonte_anos` | 15 | anos | _ESTIMADO_ | Horizonte comum = menor vida útil entre as tecnologias comparadas (aquecedor solar ~15 anos); a FV dura mais (~25 anos), o que favorece a FV fora desse horizonte | — |
| Financeiro | `taxa_desconto` | 0,08 | fração/ano | _ESTIMADO_ | Custo de oportunidade aproximado para uma família (próximo de aplicações conservadoras) | — |
| Financeiro | `aumento_tarifa_ano` | 0,05 | fração/ano | _ESTIMADO_ | Aumento médio anual de tarifa assumido (cenário base) | — |
| Ambiental | `fator_emissao_sin_kg_kwh` | 0,0385 | kg CO₂/kWh | **REAL** | Fator médio anual do SIN em 2023 (38,5 kgCO2/MWh), MCTI/SIRENE; meses de 2025 ficaram entre 21,5 e 28,9 kg/MWh | R13 |
| Ambiental | `fv_ciclo_vida_kg_kwh` | 0,041 | kg CO₂eq/kWh | **REAL** | Mediana de emissões de ciclo de vida da FV em telhado (IPCC AR5, Anexo III) | R14 |
| Ambiental | `horario_pico_inicio_h` | 18 | h | PÚBLICO | Pico residencial 18h-21h com forte participação do chuveiro | R3 |

## Observação sobre a participação do chuveiro

O perfil-tipo resulta em 36% da conta, acima da média nacional de ~24% da PPH. A diferença é esperada: a família tem 4 pessoas, usa a posição inverno em 7 meses e, sendo de baixa renda, tem menos aparelhos que a média. O assistente avisa quando os dados informados levam o chuveiro a passar de 80% do consumo total, um sinal de dados incoerentes.
