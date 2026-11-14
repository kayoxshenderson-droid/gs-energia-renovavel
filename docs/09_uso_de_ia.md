# 9. Uso de IA generativa e verificação

O enunciado permite o uso criterioso de IA generativa, desde que a equipe verifique dados, cálculos, referências e recomendações e demonstre compreensão das decisões.

## Como a IA foi usada

- Apoio na pesquisa inicial de fontes, na estruturação do código e na redação da documentação.

## Como o trabalho foi verificado

- [ ] Abri cada link de `05_referencias.md` e confirmei que o número citado está lá.
- [ ] Refiz à mão (ou na calculadora) a conta da energia: 4,542 kW × 16 h = 72,7 kWh/mês.
- [ ] Refiz a tarifa: 0,72518 × 1,0902 / (1 − 0,12 − 0,05) ≈ R$ 0,95/kWh e comparei com a minha conta de luz.
- [ ] Conferi a irradiação de São Paulo no SunData (CRESESB).
- [ ] Rodei `python -m pytest -q` (28 testes passando) e `python scripts/gerar_relatorio.py`.
- [ ] Sei explicar: E = P·t, Q = m·c·ΔT, fração solar, Fio B (Lei 14.300), Tarifa Social de 80 kWh, payback e VPL, e por que o CO₂ da FV fica perto de zero no Brasil.

> Marque os itens à medida que fizer cada verificação. Se algum valor não bater com a fonte, ajuste `data/premissas.json` e rode o script de novo: tudo é recalculado.
