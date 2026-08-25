"""
Fonte unica dos blocos dos dois videos.

Cada bloco tem uma ancora (o texto que a tela precisa mostrar) e a fala
correspondente. As duracoes NAO sao escritas a mao: o produzir.py sintetiza cada
fala, mede quanto tempo ela ocupa e so entao define a janela de tela.

Foi a duplicacao dessas duracoes em dois arquivos que dessincronizou a primeira
versao — a narracao ficou mais longa que a captura e o ffmpeg cortou o final.
"""

# (ancora na pagina, fala)
VIDEO_1 = [
    ("FarmTech Solutions — Previsão de rendimento", """
Olá. Sou o Douglas Felicio, RM quinhentos e setenta e dois, trezentos e doze.
Essa é a entrega da Fase cinco da FarmTech Solutions.
A fazenda tem duzentos hectares e quatro culturas. A pergunta do cliente é
direta: dadas as condições de clima, quanto vamos colher?
Vou mostrar o que os dados respondem, e principalmente o que eles não respondem,
que acabou sendo a parte mais importante do trabalho.
"""),
    ("2.1 Quatro culturas em escalas muito diferentes", """
A base tem cento e cinquenta e seis registros, quatro variáveis climáticas e o
rendimento. Sem valores ausentes e sem duplicatas.
Olhando o rendimento por cultura, aparece a primeira coisa relevante: o óleo de
palma rende, em média, cento e setenta e cinco mil. A borracha, sete mil e
oitocentos. Vinte vezes menos.
Não é diferença de grau, é diferença de escala. E é isso que vai contaminar a
avaliação dos modelos.
"""),
    ("2.2 As quatro culturas compartilham", """
Conferindo linha a linha, descobri que as quatro culturas têm exatamente os
mesmos valores climáticos.
Não são cento e cinquenta e seis medições independentes. São trinta e nove,
repetidas quatro vezes.
E aqui está o número que organiza o trabalho inteiro: só saber qual é a cultura
plantada explica noventa e oito vírgula sete por cento da variação do
rendimento. Sobra um por cento para o clima disputar.
"""),
    ("2.3 Correlação: o que o agregado esconde", """
Repare na diferença entre os dois painéis. Na base inteira, a correlação com o
clima é praticamente zero. Medida dentro de cada cultura, ela aparece.
O arroz responde positivamente ao calor e à umidade. A borracha responde ao
contrário. Culturas diferentes reagem em direções opostas, e um modelo agregado
cancela os dois efeitos.
"""),
    ("2.4 Um alerta", """
Encontrei também um alerta importante. O rendimento do arroz tem correlação de
zero vírgula noventa e um com a posição no arquivo, e a umidade específica, zero
vírgula oitenta.
Duas séries que sobem juntas produzem correlação alta sem relação causal. Ou
seja: parte do efeito atribuído ao clima é, provavelmente, ganho tecnológico ao
longo dos anos.
"""),
    ("3. Clusterização: tendências", """
Na clusterização, o K-Means com quatro grupos não separa as culturas. Ele separa
condições climáticas.
Rodando só sobre o clima, os grupos ficam iguais para as quatro culturas, o que
era esperado. Esses quatro grupos são regimes climáticos recorrentes na região.
"""),
    ("3.1 Cenários discrepantes", """
Para os outliers, o DBSCAN se mostrou instável: marca quarenta por cento dos
pontos como ruído.
Usei então o desvio dentro de cada cultura, e encontrei três cenários
discrepantes: a melhor safra de cacau, que coincide com a maior precipitação da
série; a pior de óleo de palma; e a melhor de arroz.
Nenhum é erro de medição, então mantive todos na modelagem.
"""),
    ("4. Modelos preditivos", """
Agora os modelos. Cinco algoritmos diferentes: regressão linear, árvore de
decisão, random forest, gradient boosting e SVR.
Todos com o pré-processamento dentro do pipeline, para não vazar informação do
teste para o treino, e todos avaliados também por validação cruzada.
"""),
    ("4.1 O baseline que muda a leitura", """
Quatro deles passam de noventa e oito por cento de R dois. Parece excelente.
Mas comparei com um baseline que ignora o clima por completo e prevê apenas a
média histórica de cada cultura.
Esse baseline atinge zero vírgula nove oito quatro dois. Melhor que os cinco
modelos, sem exceção.
Isso prova que o R dois global, nesta base, mede só a capacidade de distinguir
as culturas.
"""),
    ("4.2 Medindo o que interessa", """
Medindo dentro de cada cultura, o quadro fica honesto: o R dois fica próximo de
zero, e frequentemente negativo.
Pelo MAPE, o melhor modelo erra onze vírgula três por cento contra doze vírgula
dois do baseline. O ganho existe, mas é de sete por cento.
"""),
    ("5. Conclusões", """
A conclusão honesta é essa: reportar R dois de noventa e oito seria tecnicamente
verdadeiro e materialmente enganoso.
O caminho para melhorar não passa por um algoritmo mais sofisticado. Passa por
coletar a data de cada safra, para separar clima de tendência tecnológica, e
variáveis de manejo.
Obrigado.
"""),
]

VIDEO_2 = [
    ("Entrega 2 — Onde hospedar o modelo", """
Olá. Douglas Felicio, RM quinhentos e setenta e dois, trezentos e doze. Essa é a
segunda entrega da Fase cinco.
A missão é estimar quanto custa hospedar essa solução na AWS, comparando São
Paulo e Virgínia do Norte, no modelo sob demanda.
A máquina precisa ter duas CPUs, um giga de memória, até cinco gigabits de rede
e cinquenta gigas de disco.
"""),
    ("A instância escolhida", """
Buscando na calculadora por instâncias que atendam a esses requisitos, o
t3.micro é a de menor custo, e atende à especificação exatamente: duas vCPUs, um
giga de memória e, literalmente, up to five gigabit de rede.
Vale registrar o que ficou de fora: o t2.micro tem só uma vCPU e não atende. O
t3.small tem dois gigas de memória e custaria o dobro, sem necessidade.
"""),
    ("Os números", """
Aqui estão os números. Em São Paulo, a instância custa doze dólares e vinte e
seis por mês, e o disco de cinquenta gigas, sete e sessenta. Total de dezenove
dólares e oitenta e seis.
Na Virgínia do Norte, sete e cinquenta e nove de computação e quatro dólares de
disco. Total de onze e cinquenta e nove.
São Paulo custa setenta e um por cento a mais. E vale notar onde está a
diferença: o disco é noventa por cento mais caro, enquanto o processamento é
sessenta e dois por cento. Em um ano, são noventa e nove dólares.
"""),
    ("Capturas da calculadora", """
Essas são as capturas da calculadora oficial, com as duas regiões configuradas.
Um detalhe que quase passou despercebido: a calculadora aplica, por padrão, o
Compute Savings Plan de três anos. Com ele, São Paulo sairia por treze e setenta
e três.
Mas o enunciado pede sob demanda, cem por cento. Trocando a estratégia em Other
purchasing options, o valor correto aparece.
"""),
    ("A decisão: São Paulo", """
A Virgínia é mais barata. Mesmo assim, a escolha é São Paulo, por dois motivos.
O primeiro é legal. O enunciado diz que há restrição de armazenamento no
exterior. Dados de sensores viram dados pessoais assim que se associam ao
produtor rural e à sua propriedade.
Manter tudo em São Paulo elimina a transferência internacional e, com ela, toda
a exigência do artigo trinta e três da LGPD.
"""),
    ("A latência confirma a escolha", """
O segundo motivo é latência. Do Brasil, São Paulo responde em cerca de quinze
milissegundos. A Virgínia, em cento e trinta. Oito vezes mais, por distância
física, que nenhuma otimização de software resolve.
E a diferença de custo é de oito dólares por mês. Para uma fazenda de duzentos
hectares, isso é ruído no orçamento.
A Virgínia continua fazendo sentido para retreinar o modelo sobre dados
anonimizados, onde latência não importa. Fica como arquitetura híbrida.
Obrigado.
"""),
]

from blocos_ir_alem import VIDEO_3

VIDEOS = {1: VIDEO_1, 2: VIDEO_2, 3: VIDEO_3}
PAGINA = {1: "previa.html", 2: "readme.html", 3: "readme_ir_alem.html"}
