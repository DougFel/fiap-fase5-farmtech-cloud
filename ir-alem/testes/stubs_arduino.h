/*
 * Stubs minimos das APIs Arduino/ESP32 usadas pelo firmware.
 *
 * Servem para compilar o farmtech_esp32.ino num PC e exercitar a logica sem
 * placa e sem o toolchain xtensa. Nao substituem o teste no hardware — o que
 * eles pegam sao erros de tipo, de chamada e de logica, que sao justamente os
 * que aparecem tarde e custam caro quando descobertos so na gravacao.
 */
#ifndef STUBS_ARDUINO_H
#define STUBS_ARDUINO_H

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>

// ─────────────────────────────────────────── tipos e constantes
#define HEX 16
#define DEC 10

/*
 * String do Arduino.
 *
 * Herda de std::string para ganhar concatenacao, find() e npos de graca, e
 * acrescenta os construtores que o firmware usa: String(float, casas) e
 * String(uint32_t, base). E o mesmo contrato da classe real.
 */
class String : public std::string {
 public:
  String() = default;
  String(const char* s) : std::string(s ? s : "") {}
  String(const std::string& s) : std::string(s) {}

  String(float v, int casas) {
    char b[32];
    snprintf(b, sizeof(b), "%.*f", casas, v);
    assign(b);
  }
  String(uint32_t v, int base) {
    char b[32];
    snprintf(b, sizeof(b), base == HEX ? "%x" : "%u", v);
    assign(b);
  }
};

#define HIGH 1
#define LOW 0
#define OUTPUT 1
#define INPUT_PULLUP 2
#define FALLING 3
#define IRAM_ATTR
#define WIFI_STA 1
#define WL_CONNECTED 3
#define ADC_11db 3
#define F(x) (x)

// ─────────────────────────────────────────── relogio e GPIO
extern uint32_t _millis_simulado;
extern uint32_t _micros_simulado;
extern int _adc_solo;
extern int _adc_ldr;
extern float _dht_temp;
extern float _dht_umid;

inline uint32_t millis() { return _millis_simulado; }
inline uint32_t micros() { return _micros_simulado; }
inline void delay(uint32_t ms) { _millis_simulado += ms; }

inline void pinMode(int, int) {}
inline void digitalWrite(int, int) {}
inline int digitalPinToInterrupt(int p) { return p; }
inline void attachInterrupt(int, void (*)(), int) {}
inline void analogReadResolution(int) {}
inline void analogSetAttenuation(int) {}

// O pino decide qual leitura simulada devolver.
inline int analogRead(int pino) { return pino == 34 ? _adc_solo : _adc_ldr; }

inline long map(long x, long emin, long emax, long smin, long smax) {
  return (x - emin) * (smax - smin) / (emax - emin) + smin;
}

// No Arduino constrain e uma macro, e nao um template — por isso aceita
// argumentos de tipos diferentes. O stub reproduz esse comportamento para que
// o firmware compile aqui exatamente como compila la.
#define constrain(amt, low, high) \
  ((amt) < (low) ? (low) : ((amt) > (high) ? (high) : (amt)))

// ─────────────────────────────────────────── perifericos
class SerialStub {
 public:
  void begin(long) {}
  void println(const char* s = "") { printf("%s\n", s); }
  void println(const String& s) { printf("%s\n", s.c_str()); }
  void print(const char* s) { printf("%s", s); }
  template <typename... A> void printf(const char* f, A... a) { std::printf(f, a...); }
};
extern SerialStub Serial;

#define DHT22 22
class DHT {
 public:
  DHT(int, int) {}
  void begin() {}
  float readTemperature() { return _dht_temp; }
  float readHumidity() { return _dht_umid; }
};

class IPAddressStub {
 public:
  String toString() const { return "192.168.0.42"; }
};

class WiFiStub {
 public:
  void mode(int) {}
  void begin(const char*, const char*) {}
  int status() { return WL_CONNECTED; }
  IPAddressStub localIP() { return {}; }
};
extern WiFiStub WiFi;

class WiFiClient {};

class PubSubClient {
 public:
  explicit PubSubClient(WiFiClient&) {}
  void setServer(const char*, uint16_t) {}
  bool connect(const char*) { return true; }
  bool connected() { return true; }
  void loop() {}
  int state() { return 0; }
  bool publish(const char* topico, const char* carga) {
    printf("    [mqtt] %s <- %s\n", topico, carga);
    return true;
  }
};

class WebServer {
 public:
  explicit WebServer(int) {}
  void on(const char*, void (*)()) {}
  void begin() {}
  void handleClient() {}
  void send(int, const char*, const String&) {}
};

struct EspStub {
  uint64_t getEfuseMac() { return 0xA1B2C3D4ULL; }
};
extern EspStub ESP;

#endif  // STUBS_ARDUINO_H
