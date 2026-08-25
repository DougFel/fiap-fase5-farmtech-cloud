/*
 * FarmTech Solutions — Monitor de saude da plantacao
 * FIAP · Inteligencia Artificial · Fase 5 · Cap 1 — Ir Alem
 * Douglas Felicio da Silva — RM 572312
 *
 * O QUE ESTE FIRMWARE FAZ
 * -----------------------
 * Le tres sensores, decide sozinho se a plantacao esta saudavel e publica o
 * diagnostico por MQTT. A classificacao acontece DENTRO do ESP32: o modelo foi
 * treinado em Python e transpilado para C++ (modelo_embarcado.h), entao a placa
 * nao depende de servidor nem de conexao para decidir.
 *
 * Isso importa no campo. Se o Wi-Fi cair, o ESP32 continua diagnosticando e
 * acionando o alerta local; a nuvem recebe os dados quando a conexao voltar.
 *
 * SENSORES
 *   DHT22           GPIO 15  temperatura e umidade do ar (digital, 2 grandezas)
 *   Umidade do solo GPIO 34  analogico, ADC1
 *   LDR             GPIO 35  analogico, ADC1
 *
 * POR QUE OS ANALOGICOS ESTAO NO ADC1
 * -----------------------------------
 * O ESP32 tem dois conversores. O ADC2 e usado internamente pelo radio Wi-Fi e
 * fica indisponivel enquanto a conexao esta ativa. Como este projeto mantem o
 * Wi-Fi ligado o tempo todo, os dois sensores analogicos foram deliberadamente
 * ligados a pinos do ADC1 (GPIO 32-39). Ligar no ADC2 produziria leituras
 * erraticas ou travamento — e o sintoma seria dificil de diagnosticar.
 */
#include <DHT.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <WebServer.h>

#include "modelo_embarcado.h"

// ─────────────────────────────────────────────────────────── pinos
#define PINO_DHT       15
#define PINO_SOLO      34   // ADC1_CH6
#define PINO_LDR       35   // ADC1_CH7
#define PINO_LED_VERDE 26
#define PINO_LED_VERM  27
#define PINO_BOTAO     18   // leitura sob demanda, por interrupcao

#define TIPO_DHT DHT22

// ─────────────────────────────────────────────────────────── rede
const char* WIFI_SSID  = "Wokwi-GUEST";   // rede aberta do simulador
const char* WIFI_SENHA = "";
const char* MQTT_HOST  = "broker.hivemq.com";
const uint16_t MQTT_PORTA = 1883;

const char* TOPICO_LEITURA    = "farmtech/rm572312/leitura";
const char* TOPICO_DIAGNOSTICO = "farmtech/rm572312/diagnostico";
const char* TOPICO_ALERTA     = "farmtech/rm572312/alerta";

// ─────────────────────────────────────────────────────────── amostragem
const uint8_t JANELA_MEDIA = 10;    // amostras da media movel
const uint32_t INTERVALO_MS = 5000; // periodo entre ciclos
const uint32_t DEBOUNCE_MS = 250;   // tempo minimo entre acionamentos do botao

DHT dht(PINO_DHT, TIPO_DHT);
WiFiClient wifi;
PubSubClient mqtt(wifi);
WebServer servidor(80);

// Buffers circulares da media movel. Guardar as ultimas N leituras e trabalhar
// com a media elimina o ruido eletrico do ADC, que sozinho oscila varios por
// cento entre leituras consecutivas do mesmo valor fisico.
float bufSolo[JANELA_MEDIA];
float bufLuz[JANELA_MEDIA];
uint8_t posBuffer = 0;
bool bufferCheio = false;

// Compartilhadas com a rotina de interrupcao: `volatile` impede o compilador de
// manter o valor em registrador e perder a atualizacao feita pela ISR.
volatile bool leituraSolicitada = false;
volatile uint32_t ultimoAcionamento = 0;

uint32_t ultimoCiclo = 0;
Leitura ultimaLeitura = {0, 0, 0, 0};
Diagnostico ultimoDiagnostico = {SAUDAVEL, 0};

/*
 * Interrupcao do botao.
 *
 * IRAM_ATTR mantem a funcao na RAM interna: uma ISR nao pode depender de um
 * acesso a flash, que pode estar ocupada. O corpo faz o minimo possivel —
 * marcar uma flag — porque interrupcao longa trava o resto do sistema.
 *
 * O millis() aqui resolve o repique mecanico do botao: sem ele, um unico toque
 * geraria dezenas de acionamentos em poucos milissegundos.
 */
void IRAM_ATTR aoPressionarBotao() {
  uint32_t agora = millis();
  if (agora - ultimoAcionamento < DEBOUNCE_MS) return;
  ultimoAcionamento = agora;
  leituraSolicitada = true;
}

// ─────────────────────────────────────────────────────────── leitura
float mediaBuffer(const float* buf) {
  uint8_t n = bufferCheio ? JANELA_MEDIA : posBuffer;
  if (n == 0) return 0;
  float soma = 0;
  for (uint8_t i = 0; i < n; i++) soma += buf[i];
  return soma / n;
}

/*
 * Converte a leitura bruta do ADC para percentual.
 *
 * O ADC do ESP32 tem 12 bits (0 a 4095). O sensor capacitivo de umidade e
 * invertido: quanto mais seco o solo, maior a tensao. Por isso o mapeamento
 * abaixo espelha a escala.
 */
float lerUmidadeSolo() {
  int bruto = analogRead(PINO_SOLO);
  return constrain(map(bruto, 4095, 0, 0, 100), 0, 100);
}

float lerLuminosidade() {
  int bruto = analogRead(PINO_LDR);
  return constrain(map(bruto, 0, 4095, 0, 100), 0, 100);
}

/*
 * Explica o diagnostico: aponta a grandeza que mais pesou no resultado.
 *
 * Sem isso o operador recebe apenas "nao saudavel" e nao sabe o que fazer. Com
 * isso ele recebe "nao saudavel — umidade do solo abaixo da faixa ideal".
 *
 * O criterio combina DOIS fatores, e nao so o desvio:
 *
 *   desvio normalizado x importancia da grandeza no modelo
 *
 * A normalizacao pela largura da faixa torna grandezas de escalas diferentes
 * comparaveis. A importancia — exportada junto com a arvore — garante que a
 * explicacao aponte o que realmente moveu a decisao.
 *
 * Sem o peso, um caso como (solo 8%, ar 25%) culparia a umidade do ar, cujo
 * desvio relativo e maior; mas quem decide ali e o solo, que vale cinco vezes
 * mais para o modelo. Esse caso foi encontrado pelos testes automatizados.
 */
String causaProvavel(const Leitura& l) {
  float valores[] = {l.umidade_solo, l.temperatura, l.umidade_ar, l.luminosidade};
  float piorPontuacao = 0;
  int pior = -1;

  for (int i = 0; i < 4; i++) {
    float desvio = 0;
    if (valores[i] < FAIXAS[i].mmin) desvio = FAIXAS[i].mmin - valores[i];
    else if (valores[i] > FAIXAS[i].mmax) desvio = valores[i] - FAIXAS[i].mmax;

    desvio /= (FAIXAS[i].mmax - FAIXAS[i].mmin);   // comparavel entre escalas
    float pontuacao = desvio * FAIXAS[i].peso;      // ponderado pelo modelo

    if (pontuacao > piorPontuacao) { piorPontuacao = pontuacao; pior = i; }
  }

  if (pior < 0) return "todas as grandezas dentro da faixa";
  String lado = valores[pior] < FAIXAS[pior].mmin ? "abaixo" : "acima";
  return String(FAIXAS[pior].nome) + " " + lado + " da faixa ideal";
}

// ─────────────────────────────────────────────────────────── conectividade
void conectarWiFi() {
  Serial.printf("Wi-Fi: conectando a %s", WIFI_SSID);
  WiFi.mode(WIFI_STA);              // modo estacao: o ESP32 e cliente do roteador
  WiFi.begin(WIFI_SSID, WIFI_SENHA);

  uint8_t tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas++ < 40) {
    delay(250);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\nWi-Fi: conectado — IP %s\n", WiFi.localIP().toString().c_str());
  } else {
    // Sem rede o dispositivo continua util: diagnostica e alerta localmente.
    Serial.println("\nWi-Fi: indisponivel — operando em modo autonomo");
  }
}

void conectarMQTT() {
  if (WiFi.status() != WL_CONNECTED || mqtt.connected()) return;

  String id = "farmtech-rm572312-" + String((uint32_t) ESP.getEfuseMac(), HEX);
  Serial.printf("MQTT: conectando como %s... ", id.c_str());
  if (mqtt.connect(id.c_str())) {
    Serial.println("ok");
  } else {
    Serial.printf("falhou (estado %d)\n", mqtt.state());
  }
}

void publicar(const Leitura& l, const Diagnostico& d) {
  if (!mqtt.connected()) return;

  char json[240];
  snprintf(json, sizeof(json),
           "{\"rm\":\"572312\",\"umidade_solo\":%.1f,\"temperatura\":%.1f,"
           "\"umidade_ar\":%.1f,\"luminosidade\":%.1f}",
           l.umidade_solo, l.temperatura, l.umidade_ar, l.luminosidade);
  mqtt.publish(TOPICO_LEITURA, json);

  char diag[220];
  snprintf(diag, sizeof(diag),
           "{\"classe\":\"%s\",\"confianca\":%.3f,\"causa\":\"%s\"}",
           d.classe == SAUDAVEL ? "saudavel" : "nao_saudavel",
           d.confianca, causaProvavel(l).c_str());
  mqtt.publish(TOPICO_DIAGNOSTICO, diag);

  // Alerta so vai ao ar quando ha o que reportar — evita poluir o topico.
  if (d.classe == NAO_SAUDAVEL) {
    mqtt.publish(TOPICO_ALERTA, diag);
  }
}

// ─────────────────────────────────────────────────────────── pagina local
void paginaStatus() {
  const bool ok = ultimoDiagnostico.classe == SAUDAVEL;
  String cor = ok ? "#1f9d55" : "#c2410c";

  String html = F("<!doctype html><meta charset='utf-8'>"
                  "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                  "<meta http-equiv='refresh' content='5'>"
                  "<title>FarmTech — saude da plantacao</title><style>"
                  "body{font:15px/1.6 system-ui,sans-serif;margin:0;padding:26px;"
                  "background:#0f1720;color:#e6edf3}"
                  ".card{max-width:520px;margin:0 auto;background:#161f2b;"
                  "border-radius:12px;padding:24px}"
                  "h1{font-size:17px;margin:0 0 4px}"
                  ".sub{color:#8b98a5;font-size:13px;margin-bottom:20px}"
                  ".estado{font-size:26px;font-weight:700;margin:14px 0 6px}"
                  ".causa{color:#8b98a5;font-size:13px;margin-bottom:20px}"
                  "table{width:100%;border-collapse:collapse;font-size:14px}"
                  "td{padding:8px 0;border-bottom:1px solid #24303d}"
                  "td:last-child{text-align:right;font-weight:600}"
                  ".rod{color:#5c6b7a;font-size:11px;margin-top:18px}"
                  "</style><div class='card'>"
                  "<h1>FarmTech Solutions</h1>"
                  "<div class='sub'>Monitor de saude da plantacao · RM 572312</div>");

  html += "<div class='estado' style='color:" + cor + "'>";
  html += ok ? "SAUDAVEL" : "NAO SAUDAVEL";
  html += "</div><div class='causa'>";
  html += causaProvavel(ultimaLeitura);
  html += " · confianca " + String(ultimoDiagnostico.confianca * 100, 0) + "%</div>";

  html += "<table>";
  html += "<tr><td>Umidade do solo</td><td>" + String(ultimaLeitura.umidade_solo, 1) + " %</td></tr>";
  html += "<tr><td>Temperatura</td><td>" + String(ultimaLeitura.temperatura, 1) + " &deg;C</td></tr>";
  html += "<tr><td>Umidade do ar</td><td>" + String(ultimaLeitura.umidade_ar, 1) + " %</td></tr>";
  html += "<tr><td>Luminosidade</td><td>" + String(ultimaLeitura.luminosidade, 1) + " %</td></tr>";
  html += "</table>";

  html += "<div class='rod'>Classificacao executada no proprio ESP32 "
          "(arvore de decisao embarcada). MQTT: ";
  html += mqtt.connected() ? "conectado" : "offline";
  html += "</div></div>";

  servidor.send(200, "text/html; charset=utf-8", html);
}

// ─────────────────────────────────────────────────────────── ciclo
void executarCiclo() {
  float solo = lerUmidadeSolo();
  float luz = lerLuminosidade();

  bufSolo[posBuffer] = solo;
  bufLuz[posBuffer] = luz;
  posBuffer = (posBuffer + 1) % JANELA_MEDIA;
  if (posBuffer == 0) bufferCheio = true;

  float temperatura = dht.readTemperature();
  float umidadeAr = dht.readHumidity();
  // O DHT22 falha esporadicamente; nesse caso mantemos a ultima leitura valida
  // em vez de alimentar o modelo com NaN.
  if (isnan(temperatura)) temperatura = ultimaLeitura.temperatura;
  if (isnan(umidadeAr)) umidadeAr = ultimaLeitura.umidade_ar;

  ultimaLeitura = { mediaBuffer(bufSolo), temperatura, umidadeAr, mediaBuffer(bufLuz) };

  // A inferencia acontece aqui — no microcontrolador, sem rede.
  uint32_t t0 = micros();
  ultimoDiagnostico = classificarSaude(ultimaLeitura);
  uint32_t levou = micros() - t0;

  const bool ok = ultimoDiagnostico.classe == SAUDAVEL;
  digitalWrite(PINO_LED_VERDE, ok ? HIGH : LOW);
  digitalWrite(PINO_LED_VERM, ok ? LOW : HIGH);

  Serial.printf("solo %.1f%% | temp %.1fC | ar %.1f%% | luz %.1f%%  ->  %s "
                "(conf. %.0f%%, %luus) %s\n",
                ultimaLeitura.umidade_solo, ultimaLeitura.temperatura,
                ultimaLeitura.umidade_ar, ultimaLeitura.luminosidade,
                ok ? "SAUDAVEL" : "NAO SAUDAVEL",
                ultimoDiagnostico.confianca * 100, levou,
                ok ? "" : ("| " + causaProvavel(ultimaLeitura)).c_str());

  publicar(ultimaLeitura, ultimoDiagnostico);
}

void setup() {
  Serial.begin(115200);
  delay(400);
  Serial.println("\n=== FarmTech Solutions — monitor de saude da plantacao ===");
  Serial.println("Modelo embarcado: arvore de decisao, 89 nos, acuracia 0.676");

  pinMode(PINO_LED_VERDE, OUTPUT);
  pinMode(PINO_LED_VERM, OUTPUT);
  pinMode(PINO_BOTAO, INPUT_PULLUP);
  // FALLING: o botao com pull-up interno leva o pino a GND quando pressionado.
  attachInterrupt(digitalPinToInterrupt(PINO_BOTAO), aoPressionarBotao, FALLING);

  // 12 bits (0-4095) e 11 dB de atenuacao, que estende a faixa util ate ~3,3 V.
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);

  dht.begin();
  conectarWiFi();
  mqtt.setServer(MQTT_HOST, MQTT_PORTA);
  conectarMQTT();

  servidor.on("/", paginaStatus);
  servidor.begin();
  Serial.println("Servidor HTTP no ar na porta 80");

  // Preenche a janela da media movel antes do primeiro diagnostico, para nao
  // decidir com base em uma unica amostra ruidosa.
  for (uint8_t i = 0; i < JANELA_MEDIA; i++) {
    bufSolo[i] = lerUmidadeSolo();
    bufLuz[i] = lerLuminosidade();
    delay(40);
  }
  bufferCheio = true;
  executarCiclo();
}

void loop() {
  servidor.handleClient();
  if (mqtt.connected()) mqtt.loop(); else conectarMQTT();

  // Leitura sob demanda, disparada pela interrupcao do botao.
  if (leituraSolicitada) {
    leituraSolicitada = false;
    Serial.println("[botao] leitura solicitada pelo operador");
    executarCiclo();
    ultimoCiclo = millis();
  }

  // Ciclo periodico. Comparar millis() em vez de usar delay() mantem o servidor
  // HTTP e o MQTT responsivos entre uma leitura e outra.
  if (millis() - ultimoCiclo >= INTERVALO_MS) {
    ultimoCiclo = millis();
    executarCiclo();
  }
}
