# 5. Referências

Acessadas em 14/11/2026. Os códigos [R#] são os mesmos usados em `data/premissas.json` e nas respostas do assistente.

| Código | Referência | Usada para | Link |
|---|---|---|---|
| R1 | ANEEL, Reajuste Tarifário Anual 2025 da Enel Distribuição São Paulo (tarifa B1 residencial R$ 725,18/MWh), via Exame, 01/07/2025 | Tarifa base | https://exame.com/economia/conta-de-luz-sp-aumento-enel-reajuste-tarifa-aneel-julho |
| R2 | ANEEL, Reajuste Tarifário Anual 2026 da Enel SP: +9,02% residencial (B1), efeito médio 10,18%, vigência 04/07/2026, via Cenário Energia, 30/06/2026 | Reajuste 2026 | https://cenarioenergia.com.br/2026/06/30/aneel-aprova-reajuste-da-enel-sao-paulo-com-efeito-medio-de-1018/ |
| R3 | Eletrobras/Procel, Pesquisa de Posse de Equipamentos e Hábitos de Uso (PPH): chuveiro ≈ 24% do consumo residencial; banho médio de 8 a 10 min; uso concentrado no pico (citada em CBENS e PUC-Rio) | Duração do banho, participação do chuveiro, horário de pico | https://anaiscbens.emnuvens.com.br/cbens/article/download/1443/1434/1437 · https://www.maxwell.vrac.puc-rio.br/25584/25584.PDF |
| R4 | INMETRO, Programa Brasileiro de Etiquetagem (PBE): chuveiros elétricos e coletores solares | Potências e eficiência do chuveiro | https://www.gov.br/inmetro |
| R5 | Lei nº 15.235, de 8/10/2025, que altera a Lei 12.212/2010 (Tarifa Social: 100% de desconto até 80 kWh/mês, 0% acima) | Tarifa Social | https://planalto.gov.br/ccivil_03/_ato2007-2010/2010/lei/l12212.htm · https://www2.camara.leg.br/legin/fed/lei/2025/lei-15235-8-outubro-2025-798121-publicacaooriginal-176682-pl.html |
| R6 | CRESESB/CEPEL, SunData (irradiação solar por localidade); INPE/LABREN, Atlas Brasileiro de Energia Solar, 2ª ed. | Irradiação em São Paulo | http://www.cresesb.cepel.br/sundata/ · http://labren.ccst.inpe.br/atlas_2017.html |
| R7 | Preços de mercado de aquecedor solar 200 L: SINAPI composição 103517 (kit compacto com instalação); varejo (kit 200 L com coletor R$ 4.180); Cronoshare (faixa R$ 3–8 mil); estudo UFRJ-Macaé (sistema instalado R$ 4.180) e dados ABRASOL 2026 | Custo do aquecedor solar | https://orcamentor.com/composicao/103517/ · https://www.cronoshare.com.br/quanto-custa/instalar-aquecedor-solar-agua-termossifao · https://clickpetroleoegas.com.br/adeus-chuveiro-eletrico-aquecedor-solar-placas-planas-26-milhoes-m2-davila/ |
| R8 | MATAJS, R. R. *Demanda, consumo e custo das alternativas ao chuveiro elétrico: o exemplo do Estado de São Paulo*. Dissertação, IEE-USP | Fração solar, alternativas ao chuveiro | https://teses.usp.br/teses/disponiveis/86/86131/tde-19012012-100032/publico/RobertoRamosMatajs.PDF |
| R9 | Greener, Estudo Estratégico de Geração Distribuída: sistema de 4 kWp ≈ R$ 2,84/Wp (jun/2025); alta de 7% nos preços no 1º sem/2026 | Custo da FV | https://olhardigital.com.br/curiosidades/?p=10663 · https://www.pv-magazine.com/2026/09/26/pv-system-costs-increase-7-percent-brazil-h1/ |
| R10 | EPE, Anuário Estatístico de Energia Elétrica (consumo médio residencial) | Consumo total da casa | https://www.epe.gov.br |
| R11 | Fatura de energia Enel SP (ICMS, PIS/COFINS) | Tributos (o usuário deve conferir na própria conta) | https://www.enel.com.br/pt-saopaulo.html |
| R12 | Lei nº 14.300, de 6/1/2022 (marco legal da micro e minigeração distribuída; cobrança escalonada do Fio B: 60% em 2026) | Valor do crédito da FV | https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2022/lei/l14300.htm |
| R13 | MCTI/SIRENE, fatores médios de emissão de CO₂ do SIN (38,5 kg/MWh em 2023; 21,5–28,9 kg/MWh em jan–abr/2025) | CO₂ evitado | https://eixos.com.br/brasil-tem-menor-taxa-de-emissao-de-carbono-na-geracao-eletrica-em-onze-anos/ · https://canalsolar.com.br/emissoes-de-co%e2%82%82-geracao-eletrica-mcti/ |
| R14 | IPCC AR5, WG III, Anexo III: emissões de ciclo de vida (FV em telhado, mediana ~41 g CO₂eq/kWh) | Ciclo de vida da FV | https://www.ipcc.ch/report/ar5/wg3/ |

Leitura complementar sobre as regras atuais da Tarifa Social e do Desconto Social: https://www.jb.com.br/editorias/?p=618

## Como conferir os números-chave

1. **Tarifa:** pegue a conta de luz, divida o valor da energia (sem iluminação pública e multas) pelos kWh consumidos e informe ao assistente (“tarifa R$ 1,02”).
2. **Irradiação:** no SunData (R6), digite as coordenadas do bairro e use a média anual no plano inclinado.
3. **Preços:** peça pelo menos 3 orçamentos locais; troque `custo_instalado` / `custo_minimo` em `data/premissas.json` e rode `python scripts/gerar_relatorio.py`.
