# Roteiro dos vídeos — Fase 5, Cap 1

Dois vídeos separados, como pede o enunciado, cada um abaixo de 5 minutos.

---

## Vídeo 1 — Entrega 1: Machine Learning (4min10)

| Bloco | Início | Duração | Tela |
|---|---|---|---|
| 1. Abertura e o problema | 0:00 | 35 s | capa do notebook |
| 2. A base e o primeiro achado | 0:35 | 55 s | seção 1 e 2.1, boxplots |
| 3. O clima é compartilhado | 1:30 | 50 s | seção 2.2 e 2.3, heatmaps |
| 4. Clusterização e outliers | 2:20 | 45 s | seção 3, PCA e outliers |
| 5. Os cinco modelos e o baseline | 3:05 | 45 s | seção 4, tabelas |
| 6. Conclusão | 3:50 | 20 s | seção 5 |

### Bloco 1 — Abertura (0:00 – 0:35)

> Olá. Sou o Douglas Felicio, RM 572312, e essa é a entrega da Fase 5 da
> FarmTech Solutions.
> A fazenda tem duzentos hectares e quatro culturas. A pergunta do cliente é
> direta: dadas as condições de clima, quanto vamos colher?
> Vou mostrar o que os dados respondem — e, principalmente, o que eles não
> respondem, que acabou sendo a parte mais importante do trabalho.

### Bloco 2 — A base (0:35 – 1:30)

> A base tem cento e cinquenta e seis registros, quatro variáveis climáticas e o
> rendimento. Sem valores ausentes, sem duplicatas.
> Olhando o rendimento por cultura, aparece a primeira coisa relevante: o óleo de
> palma rende, em média, cento e setenta e cinco mil. A borracha, sete mil e
> oitocentos. Vinte vezes menos.
> Não é diferença de grau, é diferença de escala. E é isso que vai contaminar a
> avaliação dos modelos mais adiante.

### Bloco 3 — O clima compartilhado (1:30 – 2:20)

> Ao conferir linha a linha, descobri que as quatro culturas têm exatamente os
> mesmos valores climáticos.
> Ou seja: não são cento e cinquenta e seis medições independentes. São trinta e
> nove, repetidas quatro vezes.
> E aqui está o número que organiza o trabalho inteiro: só saber qual é a cultura
> plantada explica noventa e oito vírgula sete por cento da variação do
> rendimento. Sobra um por cento para o clima disputar.
> Repare na diferença entre os dois painéis. Na base inteira, a correlação com o
> clima é zero. Medida dentro de cada cultura, ela aparece: o arroz responde
> positivamente ao calor e à umidade; a borracha responde ao contrário.
> Um modelo que ignore a cultura simplesmente cancela os dois efeitos.

### Bloco 4 — Clusterização e outliers (2:20 – 3:05)

> Na clusterização, o K-Means com quatro grupos não separa as culturas: ele
> separa condições climáticas. As três culturas de escala menor se distribuem de
> forma idêntica pelos clusters.
> Rodando só sobre o clima, os grupos ficam iguais para as quatro culturas — o
> que era esperado, já que o clima é o mesmo. Esses quatro grupos são regimes
> climáticos recorrentes na região.
> Para os outliers, o DBSCAN se mostrou instável: marca quarenta por cento dos
> pontos como ruído. Usei então o desvio dentro de cada cultura, e encontrei três
> cenários discrepantes — a melhor safra de cacau, na maior precipitação da
> série; a pior de óleo de palma; e a melhor de arroz.
> Nenhum deles é erro de medição, então mantive todos na modelagem.

### Bloco 5 — Os modelos (3:05 – 3:50)

> Cinco algoritmos: regressão linear, árvore de decisão, random forest, gradient
> boosting e SVR. Todos com pré-processamento dentro do pipeline, para não
> vazar dado do teste para o treino, e com validação cruzada.
> Quatro deles passam de noventa e oito por cento de R dois. Parece ótimo.
> Mas eu comparei com um baseline que ignora o clima por completo e prevê só a
> média histórica da cultura. Esse baseline atinge zero vírgula nove oito quatro
> dois — melhor que os cinco modelos.
> Medindo dentro de cada cultura, o R dois dos modelos fica perto de zero, e
> muitas vezes negativo. Pelo MAPE, o melhor modelo erra onze por cento contra
> doze do baseline. O ganho existe, mas é de sete por cento.

### Bloco 6 — Conclusão (3:50 – 4:10)

> A conclusão honesta é essa: reportar R dois de noventa e oito seria verdadeiro
> e enganoso ao mesmo tempo.
> O caminho para melhorar não é um algoritmo mais sofisticado. É coletar a data de
> cada safra, para separar clima de tendência tecnológica, e variáveis de manejo.
> Obrigado.

---

## Vídeo 2 — Entrega 2: Computação em Nuvem (3min30)

| Bloco | Início | Duração | Tela |
|---|---|---|---|
| 1. O que foi pedido | 0:00 | 30 s | README, seção Entrega 2 |
| 2. A instância escolhida | 0:30 | 40 s | tabela t3.micro |
| 3. Calculadora — São Paulo | 1:10 | 50 s | captura São Paulo |
| 4. Calculadora — Virgínia | 2:00 | 40 s | captura Virgínia |
| 5. A decisão e a justificativa | 2:40 | 50 s | tabelas de decisão |

### Bloco 1 — O que foi pedido (0:00 – 0:30)

> Na segunda entrega, a missão é estimar quanto custa hospedar essa solução na
> AWS, comparando São Paulo e Virgínia do Norte, no modelo sob demanda.
> A máquina precisa ter duas CPUs, um giga de memória, até cinco gigabits de rede
> e cinquenta gigas de disco.

### Bloco 2 — A instância (0:30 – 1:10)

> Buscando na calculadora por instâncias que atendam a esses requisitos, o
> t3.micro é a de menor custo, e atende à especificação exatamente: duas vCPUs,
> um giga de memória e, literalmente, up to five gigabit de rede.
> Vale dizer o que ficou de fora: o t2.micro tem só uma vCPU e não atende. O
> t3.small tem dois gigas de memória e custaria o dobro sem necessidade.

### Bloco 3 — São Paulo (1:10 – 2:00)

> Configurando para São Paulo: Linux, tenancy compartilhado, uso constante.
> Um detalhe importante que quase passou despercebido: a calculadora aplica, por
> padrão, o Compute Savings Plan de três anos. Com ele, o valor sai treze
> setenta e três — mas o enunciado pede sob demanda, cem por cento.
> Trocando a estratégia para On-Demand, o valor correto aparece: doze e vinte e
> seis de computação, mais sete e sessenta de disco. Total de dezenove dólares e
> oitenta e seis por mês.

### Bloco 4 — Virgínia do Norte (2:00 – 2:40)

> A mesma configuração na Virgínia do Norte: sete e cinquenta e nove de
> computação, quatro dólares de disco, total de onze e cinquenta e nove.
> São Paulo custa setenta e um por cento a mais. E vale notar onde está a
> diferença: o disco é noventa por cento mais caro, enquanto o processamento é
> sessenta e dois por cento.
> Em um ano, a diferença é de noventa e nove dólares.

### Bloco 5 — A decisão (2:40 – 3:30)

> A Virgínia é mais barata. Mesmo assim, a escolha é São Paulo, por dois motivos.
> O primeiro é legal. O enunciado diz que há restrição de armazenamento no
> exterior. Dados de sensores viram dados pessoais assim que se associam ao
> produtor e à propriedade. Manter tudo em São Paulo elimina a transferência
> internacional e, com ela, toda a exigência do artigo trinta e três da LGPD.
> O segundo é latência. Do Brasil, São Paulo responde em cerca de quinze
> milissegundos. A Virgínia, em cento e trinta. Oito vezes mais, por distância
> física, que nenhuma otimização resolve. Para sensores enviando leituras
> continuamente, isso pesa.
> E a diferença de custo é de oito dólares por mês. Para uma fazenda de duzentos
> hectares, é ruído no orçamento. Não compensa trocar isso por risco jurídico e
> latência oito vezes maior.
> A Virgínia continua fazendo sentido para uma coisa: retreinar o modelo
> periodicamente sobre dados já anonimizados, onde a latência não importa. Fica
> como arquitetura híbrida.
> Obrigado.
