"""Blocos do video do Ir Alem — mesma estrutura de blocos.py."""

VIDEO_3 = [
    ("Ir Além — Classificação da saúde da plantação", """
Olá. Douglas Felicio, RM quinhentos e setenta e dois, trezentos e doze. Esse é o
Ir Além da Fase cinco.
A proposta é classificar a saúde de uma plantação com Machine Learning e ESP32.
E o diferencial do que eu fiz é onde a classificação acontece: dentro do próprio
microcontrolador.
O modelo foi treinado em Python e transpilado para C++ puro. A placa não manda
dado para um servidor decidir. Ela já decide sozinha.
"""),
    ("Por que isso importa no campo", """
Isso não é firula técnica. Uma lavoura raramente tem Wi-Fi confiável.
Se a classificação dependesse da nuvem, uma queda de conexão deixaria o produtor
sem diagnóstico justamente quando o sensor detecta estresse hídrico.
Com o modelo embarcado, o diagnóstico continua funcionando offline, a latência é
de microssegundos em vez de centenas de milissegundos, e só o resultado trafega
pela rede, não o fluxo bruto de leituras.
"""),
    ("Arquitetura", """
São três sensores: um DHT22, que dá temperatura e umidade do ar, um sensor
capacitivo de umidade do solo e um LDR.
E aqui tem uma decisão que evita um bug difícil: os dois analógicos estão no
ADC1, nos pinos trinta e quatro e trinta e cinco.
O ESP32 tem dois conversores, e o ADC2 é usado pelo rádio Wi-Fi. Como o projeto
mantém o Wi-Fi ligado, ligar um sensor no ADC2 daria leitura errática — e o
sintoma só apareceria depois que a rede conectasse.
"""),
    ("O dataset não veio de uma regra", """
Sobre o modelo: o caminho fácil seria rotular saudável com um if sobre as
leituras. Mas aí o modelo só reaprende a regra que gerou o dado, e a acurácia
alta vira ilusão.
Então o rótulo sai de um processo probabilístico, com um fator de vigor da
planta que o ESP32 não mede e um desfecho sorteado.
A consequência é que existe um teto: o melhor classificador concebível acerta
setenta e sete vírgula nove por cento. Nenhum modelo passa disso.
"""),
    ("Desempenho", """
A árvore embarcada chega a sessenta e sete vírgula seis por cento de acurácia.
Sozinho esse número parece modesto. Ao lado do teto de setenta e sete vírgula
nove, ele significa oitenta e seis vírgula oito por cento de tudo que esses
sensores permitem extrair.
E ela fica a apenas dois pontos do Random Forest, que precisaria de trezentas
árvores e não caberia confortavelmente no microcontrolador.
As importâncias reproduzem a agronomia sozinhas: umidade do solo em primeiro,
temperatura em segundo. São os fatores limitantes primários.
"""),
    ("Da árvore ao firmware", """
A transpilação percorre a estrutura interna do scikit-learn e emite C++. Cada nó
vira um if, cada folha vira o retorno da classe com a confiança daquela folha.
São oitenta e nove nós em duzentas e vinte e duas linhas. Alguns kilobytes dos
quatro megabytes de flash.
E isso foi verificado, não presumido: um script compila o header, passa as quatro
mil amostras do dataset pelas duas implementações e exige concordância total.
Zero divergências.
"""),
    ("Testes automatizados", """
O firmware também é testado sem hardware. Ele compila num PC contra stubs das
APIs do Arduino, e nove verificações exercitam cenários de campo.
E um desses testes encontrou um defeito real. A explicação do diagnóstico
apontava a variável proporcionalmente mais fora da faixa. Com solo a oito por
cento e ar a vinte e cinco, ela culpava a umidade do ar.
Só que quem decide ali é o solo, que vale cinco vezes mais no modelo. A correção
foi ponderar o desvio pela importância que a árvore atribui a cada grandeza.
Agora a explicação aponta o que de fato moveu a decisão.
"""),
    ("Limitações — e elas são reais", """
Sobre limitações, sendo honesto: não houve execução em placa física. No Wokwi o
circuito monta, mas as duas tentativas de compilar caíram na fila dos servidores
gratuitos. O que foi executado de verdade foram os testes automatizados.
O dataset é sintético, com faixas vindas da literatura agronômica, mas continua
sendo um modelo do mundo e não o mundo.
E o teto de setenta e sete por cento não é limitação do algoritmo: é o vigor da
planta, que nenhum dos três sensores mede. Para subir esse teto seria preciso
outro sensor, e não outro modelo.
Obrigado.
"""),
]
