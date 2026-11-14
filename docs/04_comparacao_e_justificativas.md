# 4. Comparação das alternativas e justificativas

Os números vêm de [03_resultados_gerados.md](03_resultados_gerados.md), produzido pelo código a partir de [premissas](02_dados_e_premissas.md).

## Regras da comparação

- **Mesma necessidade:** aquecer a água do banho da família-tipo (872 kWh/ano de eletricidade na situação atual).
- **Mesmo período:** 12 meses para energia, custo e emissões; 15 anos para a análise financeira, a vida útil do aquecedor solar e a menor entre as tecnologias.
- **Mesma tarifa:** R$ 0,95/kWh (Enel SP 2026 com tributos estimados), com aumento de 5% ao ano e desconto de 8% ao ano no VPL.

## Conceitos aplicados

| Conceito | Onde aparece |
|---|---|
| **Potência × energia** | Um chuveiro de 5.500 W ligado 16 h/mês consome 88 kWh; potência é o “tamanho” do aparelho, energia é o que se paga (`E = P·t`). |
| **Calor sensível** | `Q = m·c·ΔT` confere que 5,5 kW aquecem 4 L/min em ~19 °C (água de 20 → ~39 °C). |
| **Eficiência** | O chuveiro converte ~95% da eletricidade em calor. O coletor solar térmico aproveita ~35–60% da luz como calor; o painel FV converte ~21% em eletricidade. Para *aquecer água*, a conversão direta sol → calor é a rota mais eficiente por m² (2 m² de coletor contra ~3,5 m² de painel para a mesma necessidade). |
| **Fonte renovável** | B (solar térmica) e C (solar fotovoltaica). |
| **Demanda de pico** | O banho ocorre entre 18h e 21h. B reduz a potência puxada nesse horário; C não, pois gera de dia. |
| **Sustentabilidade** | CO₂ evitado (fator do SIN), emissões de ciclo de vida da FV, água economizada, descarte de equipamentos. |

## Quadro comparativo

| Critério | A – Banho 5 min | B – Aquecedor solar | C – Fotovoltaica | A+B |
|---|---|---|---|---|
| Renovável | não (eficiência) | **sim** | **sim** | sim |
| Energia da rede no banho (kWh/ano) | 545 | 262 | 872 (compensada na conta) | **164** |
| Economia 1º ano | R$ 311 | R$ 581 | R$ 691 | R$ 675 |
| Investimento | **R$ 0** | R$ 4.500 | R$ 5.000 | R$ 4.500 |
| Retorno simples / descontado | imediato | 7,6 / 11,1 anos | 7,2 / 10,3 anos | **6,6 / 9,2 anos** |
| VPL em 15 anos | R$ 3.578 | R$ 1.323 | R$ 1.831 | R$ 2.397 |
| CO₂ evitado (kg/ano) | 12,6 | 23,5 | ≈ 0 (−2,2) | **27,3** |
| Alívio no pico | 0 kW (menos tempo ligado) | **até 3,8 kW** | 0 kW | **até 3,8 kW** |
| Água economizada | **17.520 L/ano** | — | — | 17.520 L/ano |
| Telhado | — | ~2 m² + reservatório (~250 kg) | ~3,5 m² | ~2 m² |

### Custos

- **A** não custa nada e tem o maior VPL, porque não exige investimento. É o primeiro passo em qualquer cenário.
- **B** e **C** têm investimento e retorno parecidos no cenário-base. A FV ganha um pouco no VPL porque o preço mínimo de um sistema pequeno foi estimado em R$ 5.000 e porque cada kWh compensado vale ~83% da tarifa (Fio B, Lei 14.300). O aquecedor perde parte do ganho por depender do chuveiro em ~30% do ano.
- A **sensibilidade** mostra que os dois resultados são frágeis: com o aquecedor a R$ 8.000 ou fração solar de 55%, o VPL de B fica negativo; com a FV a R$ 7.000 ou tarifa congelada, o de C também. Para famílias de 2 pessoas nenhuma das renováveis se paga em 15 anos; para 6 pessoas ou banhos de 12 min, ambas se pagam em ~5 anos.

### Viabilidade

| | B – Aquecedor solar | C – Fotovoltaica |
|---|---|---|
| Requisitos | Telhado com sol (face norte), estrutura para o reservatório, caixa-d’água, instalador | Telhado com sol, padrão de entrada regularizado, projeto e homologação na Enel |
| Barreiras para baixa renda | Custo inicial; casas com laje fraca ou sem caixa-d’água | Custo inicial; burocracia; sistemas pequenos ficam caros por watt |
| Caminhos possíveis | Programas habitacionais e de eficiência energética, compras coletivas, aquecedores de baixo custo (ASBC) | Financiamento verde; geração compartilhada (cooperativas) para quem não tem telhado |
| Aproveitamento | Atende exatamente a necessidade (água quente) | Gera energia para a casa toda; o banho continua elétrico |

### Impactos ambientais

- A eletricidade brasileira é muito renovável (~38,5 kg CO₂/MWh em 2023), então **o ganho em CO₂ é pequeno em qualquer opção**. Mostramos isso abertamente em vez de inflar o benefício.
- Na **FV**, a emissão de ciclo de vida (~41 g CO₂eq/kWh, IPCC) é praticamente igual ao fator da rede, e o saldo de CO₂ fica perto de zero. O benefício ambiental da FV aqui é diversificar a matriz e reduzir perdas na rede, não cortar CO₂.
- O **aquecedor solar** retira o chuveiro do **horário de pico**, quando o sistema mais aciona termelétricas a gás, que têm fator de emissão muito acima da média anual. Esse é o principal benefício ambiental e sistêmico desta necessidade.
- O **banho consciente** economiza também **água** (17,5 mil L/ano), um recurso crítico em São Paulo.
- Fim de vida: coletores (cobre, alumínio, vidro) e painéis (vidro, alumínio, silício) devem ir para reciclagem.

## Recomendação e justificativa

1. **Para todas as famílias, agora:** banho de 5 min, posição verão sempre que possível e evitar o pico. Custo zero, −38% de energia no banho e economia de água. *Justificativa:* maior VPL, nenhuma barreira e benefício imediato.
2. **Se houver telhado adequado e recursos ou apoio:** **aquecedor solar** (renovável), de preferência junto com o hábito (A+B: retorno de 6,6 anos e 81% menos energia da rede no banho). *Justificativa:* resolve a necessidade específica (água quente) pela rota mais eficiente, reduz a demanda de pico e tem custo semelhante à FV.
3. **Fotovoltaica** é indicada quando a família quer abater **o consumo da casa toda**, tem conta alta o bastante para que o sistema não fique pequeno demais, ou acessa geração compartilhada. *Justificativa:* retorno semelhante, mas não alivia o pico do banho e quase não reduz CO₂ no Brasil.
4. **Para famílias com Tarifa Social e consumo próximo de 80 kWh,** o assistente avisa que parte da economia não vira reais (a faixa já é gratuita). Nesses casos a economia em reais é pequena, e investir em equipamento dificilmente se paga; a recomendação fica nos hábitos.

Essas mesmas conclusões são as que o assistente apresenta (`r_comparar`, `r_solar_termico`, `r_fotovoltaico`, `r_tarifa_social`), e os testes automatizados conferem que os valores ditos ao usuário são os calculados.
