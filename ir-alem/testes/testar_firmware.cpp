/*
 * Teste do firmware sem hardware.
 *
 * Compila o farmtech_esp32.ino contra os stubs e exercita o comportamento em
 * cenarios de campo, verificando que:
 *
 *   1. o setup() roda sem travar;
 *   2. a media movel suaviza ruido do ADC;
 *   3. o debounce da interrupcao descarta repique;
 *   4. a classificacao responde a mudanca real de condicao;
 *   5. a causa provavel aponta a grandeza correta.
 *
 * Compilar e rodar:
 *   c++ -std=c++17 -I../firmware -I. testar_firmware.cpp -o teste && ./teste
 */
#include "stubs_arduino.h"

// Instancias globais que os stubs declararam como extern.
uint32_t _millis_simulado = 0;
uint32_t _micros_simulado = 0;
int _adc_solo = 2048;
int _adc_ldr = 2048;
float _dht_temp = 24.0f;
float _dht_umid = 70.0f;
SerialStub Serial;
WiFiStub WiFi;
EspStub ESP;

// O firmware inteiro entra aqui — inclusive setup() e loop().
#include "farmtech_esp32.ino"

// ─────────────────────────────────────────── utilidades do teste
static int falhas = 0;

void checar(const char* descricao, bool condicao) {
  printf("  [%s] %s\n", condicao ? "ok  " : "FALHA", descricao);
  if (!condicao) falhas++;
}

// Converte percentual desejado de umidade do solo para o valor bruto do ADC.
// O sensor capacitivo e invertido: mais seco, maior a tensao.
int adcParaSolo(float pct) { return (int) (4095 - (pct / 100.0f) * 4095); }
int adcParaLuz(float pct) { return (int) ((pct / 100.0f) * 4095); }

void estabilizar() {
  // Preenche a janela da média móvel com a condição atual.
  for (int i = 0; i < JANELA_MEDIA + 2; i++) executarCiclo();
}

int main() {
  printf("=== Teste do firmware FarmTech (sem hardware) ===\n\n");

  printf("1. Inicialização\n");
  setup();
  checar("setup() executa sem travar", true);
  checar("média móvel preenchida no boot", bufferCheio);

  printf("\n2. Média móvel suaviza ruído do ADC\n");
  _adc_solo = adcParaSolo(60);
  estabilizar();
  float estavel = ultimaLeitura.umidade_solo;
  // Um único pico de ruído não deve deslocar a média de forma relevante.
  _adc_solo = adcParaSolo(5);
  executarCiclo();
  float aposPico = ultimaLeitura.umidade_solo;
  printf("    estável %.1f%% -> após um pico de ruído %.1f%%\n", estavel, aposPico);
  checar("um pico isolado desloca a média em menos de 8 pontos",
         fabsf(estavel - aposPico) < 8.0f);

  printf("\n3. Debounce da interrupção\n");
  _millis_simulado = 10000;
  ultimoAcionamento = 0;
  leituraSolicitada = false;
  aoPressionarBotao();
  bool primeiro = leituraSolicitada;
  leituraSolicitada = false;
  _millis_simulado += 40;           // repique mecânico, dentro da janela
  aoPressionarBotao();
  bool repique = leituraSolicitada;
  leituraSolicitada = false;
  _millis_simulado += DEBOUNCE_MS;  // toque legítimo, fora da janela
  aoPressionarBotao();
  bool segundo = leituraSolicitada;
  checar("primeiro toque é aceito", primeiro);
  checar("repique dentro de 250 ms é descartado", !repique);
  checar("novo toque após a janela é aceito", segundo);

  printf("\n4. Classificação responde à condição\n");
  // Cenário confortável: tudo dentro da faixa ótima.
  _adc_solo = adcParaSolo(60); _adc_ldr = adcParaLuz(55);
  _dht_temp = 23.0f; _dht_umid = 72.0f;
  estabilizar();
  bool bomEhSaudavel = ultimoDiagnostico.classe == SAUDAVEL;
  printf("    solo 60%%, 23C, ar 72%%, luz 55%% -> %s\n",
         bomEhSaudavel ? "SAUDAVEL" : "NAO SAUDAVEL");

  // Cenário de seca severa com calor.
  _adc_solo = adcParaSolo(8); _dht_temp = 39.0f; _dht_umid = 25.0f;
  estabilizar();
  bool secaEhDoente = ultimoDiagnostico.classe == NAO_SAUDAVEL;
  printf("    solo  8%%, 39C, ar 25%%, luz 55%% -> %s\n",
         secaEhDoente ? "NAO SAUDAVEL" : "SAUDAVEL");

  checar("condição ótima classifica como saudável", bomEhSaudavel);
  checar("seca severa com calor classifica como não saudável", secaEhDoente);
  checar("confiança fica no intervalo válido",
         ultimoDiagnostico.confianca >= 0.0f && ultimoDiagnostico.confianca <= 1.0f);

  printf("\n5. Explicação do diagnóstico\n");
  String causa = causaProvavel(ultimaLeitura);
  printf("    causa apontada: \"%s\"\n", causa.c_str());
  checar("na seca, aponta a umidade do solo",
         causa.find("umidade do solo") != String::npos);

  Leitura confortavel = {60.0f, 23.0f, 72.0f, 55.0f};
  String semProblema = causaProvavel(confortavel);
  printf("    em condição ótima: \"%s\"\n", semProblema.c_str());
  checar("em condição ótima, não aponta problema",
         semProblema.find("dentro da faixa") != String::npos);

  printf("\n=== %s ===\n", falhas == 0 ? "TODOS OS TESTES PASSARAM"
                                       : "HOUVE FALHAS");
  return falhas == 0 ? 0 : 1;
}
