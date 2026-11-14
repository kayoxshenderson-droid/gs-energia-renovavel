# 8. Roteiro do vídeo técnico (máx. 3 minutos)

**Formato:** gravação de tela com sua voz, mostrando o IDLE/terminal (OBS Studio ou o gravador do Windows, `Win + Alt + R`). Suba no YouTube como **Não listado** e confira se o link abre numa aba anônima.

**Antes de gravar:** abra o `main.py` no IDLE (aumente a fonte em *Options → Configure IDLE → Fonts*, tamanho 14+), deixe abertos o README no GitHub e o gráfico `docs/img/energia_rede.png`. Ensaie uma vez com cronômetro.

| Tempo | Na tela | O que falar (sugestão) |
|---|---|---|
| 0:00–0:20 | README no GitHub | “Sou [nome], RM [número]. Esta é a contribuição de Energias Renováveis ao Citizen Assist AI. O público são famílias de baixa renda da Grande São Paulo, e a necessidade é aquecer a água do banho, o maior gasto isolado da conta e que pesa no horário de pico.” |
| 0:20–0:55 | `docs/02_dados_e_premissas.md` e `03_resultados_gerados.md` | “Família de 4 pessoas, banho de 8 minutos, chuveiro de 5.500 watts. Energia é potência vezes tempo: 4,5 kW de média vezes 16 horas por mês dá 73 kWh, cerca de 36% da conta e uns R$ 830 por ano, com a tarifa da Enel de 2026 homologada pela ANEEL. Conferi pela física: Q = m c ΔT mostra que a água sobe uns 19 graus. Cada dado está marcado como real, público ou estimado, com a fonte.” |
| 0:55–1:35 | Gráfico + tabela comparativa | “Comparei para a mesma necessidade e o mesmo período: banho de 5 minutos, aquecedor solar de água e placas fotovoltaicas, as duas renováveis. O banho curto economiza 38% sem custo. Aquecedor e placa custam de 4,5 a 5 mil reais e se pagam em cerca de 7 anos. A diferença está no impacto: o aquecedor tira o chuveiro do pico, e a placa gera de dia, então não alivia o pico, e na rede brasileira, que já é limpa, o saldo de CO₂ dela fica perto de zero.” |
| 1:35–2:25 | IDLE rodando `main.py` (F5) | Escolha **1** (quanto gasta), depois **10** e informe *3 pessoas, 10 minutos, Tarifa Social: s*, depois **3** (aquecedor solar) e **11** (relatório completo). Fale: “As respostas saem da mesma análise, mudam com o perfil do usuário e sempre mostram as fontes e um aviso de que são estimativas.” |
| 2:25–2:50 | `docs/04` (recomendação) e `docs/06` | “Recomendação: começar pelo banho consciente; havendo telhado e recursos, o aquecedor solar junto com o hábito, que se paga em 6,6 anos. Limitações: são estimativas, sem bandeiras tarifárias, com preços que variam, e a análise de sensibilidade mostra quando o investimento não compensa, como numa casa com 2 pessoas.” |
| 2:50–3:00 | `docs/07` + opção **13** do menu (testes passando) | “Testei com usuários e registrei os ajustes no repositório, e 18 testes automáticos garantem que o assistente fala exatamente o que foi calculado. Obrigado!” |

**Dicas:** fale devagar e com a tela ampliada (Ctrl + `+`). Não passe de 3:00, porque o enunciado põe esse limite. Se precisar cortar, encurte o trecho de 0:55–1:35.
