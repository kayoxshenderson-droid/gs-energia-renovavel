# 6. Condições e limitações das estimativas

**Nada aqui é resultado garantido.** São projeções para um perfil típico, feitas para ajudar a decidir, e não substituem medição, orçamento ou projeto profissional.

## Condições em que as recomendações valem

- Casa na área da Enel SP, ligação residencial (B1), chuveiro elétrico como único aquecimento de água.
- Uso parecido com o perfil (ou ajustado pelo usuário na conversa).
- Para B e C: telhado próprio, ensolarado, voltado para o norte, sem sombra e com estrutura adequada.

## Limitações conhecidas

| Tema | Limitação | Efeito provável |
|---|---|---|
| Consumo | Não medimos a casa; tempo de banho e potência são declarados ou estimados | Erro proporcional aos dados informados |
| Estações | Usamos potência média anual (7 meses inverno, 5 verão), sem simulação mês a mês | Contas mensais variam bastante ao longo do ano |
| Tarifa | ICMS e PIS/COFINS estimados; **bandeiras tarifárias, CIP/COSIP e multas não entram** | Em bandeira vermelha a economia é maior que a estimada |
| Tarifa Social | Considera só a franquia de 80 kWh; não modela o Desconto Social (isenção da CDE) | Economia de quem tem Desconto Social pode diferir |
| Solar térmico | Fração solar fixa (70%) checada contra o potencial anual do coletor, sem simulação horária; perdas da tubulação simplificadas | Em casas com muita sombra ou tubulação longa, a fração é menor |
| Fotovoltaica | Geração pela média anual; sem sombreamento; custo mínimo estimado; troca do inversor (~10–15 anos) não incluída; Fio B aproximado; custo de disponibilidade não modelado | Retorno real pode ser maior |
| Finanças | Aumento de tarifa (5% a.a.) e taxa de desconto (8% a.a.) são cenários; sem financiamento nem inflação de manutenção | A sensibilidade mostra que o VPL das renováveis pode ficar negativo |
| Ambiental | Fator de emissão médio anual de 2023; não usamos fator marginal do horário de pico | O benefício do aquecedor solar no pico está subestimado |
| Preços | Referências de mercado de 2025/2026; variam por região e fornecedor | Peça orçamentos |
| Assistente | Perguntas livres são interpretadas por palavras-chave; frases muito diferentes podem não ser entendidas | O menu numerado cobre todas as funções; quando não entende, ele mostra as opções |

## Como o assistente comunica isso

- Toda resposta com números termina com **“Atenção:”** explicando que são estimativas.
- A pergunta “isso é garantido?” ou “quais os limites?” mostra esta lista em linguagem simples.
- O assistente avisa quando os dados informados ficam incoerentes (ex.: chuveiro maior que o consumo da casa).
- Ele lembra que instalação elétrica e hidráulica exige profissional e que não se deve trocar a resistência por uma mais potente.
