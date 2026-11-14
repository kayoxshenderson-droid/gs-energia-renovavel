# 7. Testes com usuários

> ⚠️ **PARA PREENCHER:** as seções 7.4 e 7.5 devem ser preenchidas com testes **reais**, feitos com pessoas reais. Não invente respostas: a banca avalia as evidências e o enunciado exige registrar comentários e ajustes de verdade. Sugestão: 3 a 5 pessoas (familiares, vizinhos, colegas), 10 a 15 minutos cada.

## 7.1 Objetivo

Verificar se as orientações do assistente sobre energia do banho são **compreendidas** e **úteis** para o público (famílias de baixa renda) e ajustar o que não estiver claro.

## 7.2 Protocolo

1. **Consentimento verbal** (ler para o participante): *“Vou testar um assistente sobre economia de energia no banho. Não vou gravar seu nome nem dados pessoais; anoto só suas opiniões. Pode parar quando quiser. Tudo bem?”*
2. **Perfil mínimo**, sem dados pessoais: faixa etária (18–29 / 30–49 / 50+), nº de moradores, se tem Tarifa Social (sim/não/não sabe), familiaridade com tecnologia (baixa/média/alta). Identificar só como **P1, P2, P3…**
3. **Tarefas** no `main.py` (o participante usa o menu ou digita; você pode digitar por ele):
   - T1. Descobrir quanto o chuveiro gasta por mês.
   - T2. Pedir dicas para economizar.
   - T3. Informar o próprio caso (pessoas, minutos de banho, se tem Tarifa Social).
   - T4. Perguntar se vale a pena aquecedor solar ou placa solar.
   - T5. Pedir a comparação das opções.
   - T6. Perguntar se os números são garantidos.
4. **Perguntas após cada tarefa:** “Com suas palavras, o que o assistente disse?” (compreensão) e “Isso ajuda você a decidir algo?” (utilidade).
5. **Questionário final** (escala 1 = discordo totalmente, 5 = concordo totalmente):
   - Q1. Entendi as respostas sem ajuda.
   - Q2. Os números (kWh, R$) fizeram sentido para mim.
   - Q3. Entendi que os valores são estimativas, não garantia.
   - Q4. As fontes passam confiança.
   - Q5. Eu mudaria algum hábito depois da conversa.
   - Q6. Recomendaria o assistente a alguém.
   - Aberta: “O que foi mais confuso?” e “O que você mudaria?”
6. **Critério de sucesso:** tarefa concluída sem ajuda e explicação correta pelo participante. Meta: ≥ 80% das tarefas e média ≥ 4 em Q1–Q3.

## 7.3 Privacidade

Nada de nome, endereço, telefone, CPF, número de cliente ou foto da conta de luz. Se o participante quiser usar a própria conta, ele mesmo informa só o kWh e o R$/kWh. Prints usados como evidência não podem mostrar dados pessoais.

## 7.4 Registro dos testes (preencher)

| Participante | Perfil (faixa etária · moradores · Tarifa Social · tecnologia) | Tarefas concluídas sem ajuda (T1–T6) | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Comentários principais |
|---|---|---|---|---|---|---|---|---|---|
| P1 | | | | | | | | | |
| P2 | | | | | | | | | |
| P3 | | | | | | | | | |
| P4 | | | | | | | | | |
| P5 | | | | | | | | | |
| **Média** | | | | | | | | | |

## 7.5 Problemas encontrados e ajustes realizados (preencher)

| # | Problema observado (quem, em qual tarefa) | Ajuste feito | Arquivo/commit | Verificado com |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

Exemplos do tipo de ajuste esperado: trocar um termo técnico (“kWp”, “VPL”) por explicação simples; reordenar a resposta para começar pela conclusão; aceitar outra forma de perguntar (nova palavra-chave em `INTENCOES`); deixar mais visível o aviso de estimativa.

## 7.6 Testes internos de desenvolvimento (já realizados)

Antes dos testes com usuários, o próprio desenvolvedor testou o assistente com perguntas variadas. Estes registros **não substituem** os testes com usuários; mostram ajustes já feitos no código:

| # | Situação testada | Problema | Ajuste |
|---|---|---|---|
| D1 | “preciso economizar, me dá dicas” | A palavra “preciso” acionava a resposta sobre limites (“precisão”) | Padrão da intenção `limites` restringido |
| D2 | “3 pessoas, banho de 12 minutos, chuveiro 7500 W, consumo 110 kWh” | O chuveiro calculado passava do consumo total da casa sem nenhum aviso | Criado `alerta_consistencia()`, que avisa o usuário para conferir os dados |
| D3 | Informar “chuveiro 7500 W” | Só a potência de inverno mudava; a de verão continuava 3.200 W | A posição verão passou a ser proporcional à potência informada |
| D4 | Tabela de comparação no terminal | Colunas de valores grudadas | Larguras das colunas aumentadas |
| D5 | Gráfico de energia por alternativa | Nomes longos se sobrepunham no eixo | Rótulos curtos |
| D6 | Textos sem acentuação | Leitura mais difícil para o público | Respostas reescritas com acentuação correta |
| D7 | Primeira versão tinha interface web (link local) | Para o público e para a avaliação, rodar direto no IDLE/terminal é mais simples | Interface única em terminal (`main.py`) com menu numerado e formulário de perfil |
| D8 | Relatório com tarifa informada pelo usuário | A sensibilidade ignorava a tarifa do usuário e o “cenário base” não batia com a tabela | `sensibilidade()` passou a usar o perfil e a tarifa atuais; teste adicionado |

Os 18 testes automáticos (`python tests/test_energia.py` ou opção 13 do menu) garantem também que cada resposta traga **fontes e limites** e que os números ditos ao usuário sejam os calculados.
