// modelo_embarcado.h
//
// Classificador de saude da plantacao — GERADO AUTOMATICAMENTE por treinar.py.
// Nao edite a mao: rode `python modelo/treinar.py` para regerar.
//
// Origem     : DecisionTreeClassifier (scikit-learn), profundidade 6
// Estrutura  : 89 nos, 45 folhas
// Treino     : 3000 amostras | Teste: 1000 amostras
// Acuracia   : 0.6760 no teste (teto teorico de Bayes: 0.7788)
//
// A inferencia e uma cadeia de comparacoes de ponto flutuante: nao aloca
// memoria, nao depende de biblioteca e executa em poucos microssegundos no
// ESP32. E por isso que a classificacao acontece na borda, sem servidor.

#ifndef MODELO_EMBARCADO_H
#define MODELO_EMBARCADO_H

enum ClasseSaude { NAO_SAUDAVEL = 0, SAUDAVEL = 1 };

struct Leitura {
  float umidade_solo;   // % da capacidade de campo
  float temperatura;    // graus Celsius
  float umidade_ar;     // % de umidade relativa
  float luminosidade;   // % da escala do LDR
};

struct Diagnostico {
  ClasseSaude classe;
  float confianca;      // fracao da folha que pertence a classe escolhida
};

// Faixas fisiologicas otimas, usadas para explicar o diagnostico ao operador.
//
// O campo `peso` e a importancia que a arvore treinada atribuiu aquela grandeza.
// Sem ele, a explicacao apontaria a variavel proporcionalmente mais fora da
// faixa — que nem sempre e a que pesou na decisao. Exemplo real observado nos
// testes: com solo a 8% e ar a 25%, o desvio normalizado do ar e maior, mas
// quem determina o diagnostico e o solo, que vale 5x mais no modelo.
struct Faixa { const char* nome; float mmin; float mmax; float peso; };

static const Faixa FAIXAS[] = {
  { "umidade do solo", 45.0f, 75.0f, 0.5135f },
  { "temperatura", 18.0f, 28.0f, 0.3783f },
  { "umidade do ar", 60.0f, 85.0f, 0.0921f },
  { "luminosidade", 30.0f, 80.0f, 0.0161f },
};

inline Diagnostico classificarSaude(const Leitura& leitura) {
    if (leitura.umidade_solo <= 31.8232f) {
      if (leitura.temperatura <= 33.3238f) {
        if (leitura.temperatura <= 16.5778f) {
          if (leitura.umidade_solo <= 24.9395f) {
            if (leitura.temperatura <= 14.7296f) {
              if (leitura.umidade_solo <= 19.6671f) {
                return { NAO_SAUDAVEL, 0.9583f };
              } else {
                return { NAO_SAUDAVEL, 0.8462f };
              }
            } else {
              return { NAO_SAUDAVEL, 0.7692f };
            }
          } else {
            if (leitura.umidade_ar <= 62.0161f) {
              return { NAO_SAUDAVEL, 0.7143f };
            } else {
              return { NAO_SAUDAVEL, 0.5200f };
            }
          }
        } else {
          if (leitura.temperatura <= 24.6935f) {
            if (leitura.umidade_ar <= 46.1900f) {
              if (leitura.umidade_ar <= 34.3236f) {
                return { NAO_SAUDAVEL, 0.5769f };
              } else {
                return { NAO_SAUDAVEL, 0.8400f };
              }
            } else {
              if (leitura.umidade_solo <= 13.8206f) {
                return { NAO_SAUDAVEL, 0.6296f };
              } else {
                return { SAUDAVEL, 0.6633f };
              }
            }
          } else {
            if (leitura.umidade_solo <= 21.6698f) {
              if (leitura.umidade_solo <= 16.4217f) {
                return { NAO_SAUDAVEL, 0.8657f };
              } else {
                return { NAO_SAUDAVEL, 0.7234f };
              }
            } else {
              if (leitura.umidade_ar <= 44.2405f) {
                return { NAO_SAUDAVEL, 0.6800f };
              } else {
                return { NAO_SAUDAVEL, 0.5147f };
              }
            }
          }
        }
      } else {
        if (leitura.umidade_solo <= 19.4228f) {
          if (leitura.umidade_ar <= 82.6677f) {
            if (leitura.luminosidade <= 20.7410f) {
              return { NAO_SAUDAVEL, 0.9600f };
            } else {
              return { NAO_SAUDAVEL, 1.0000f };
            }
          } else {
            return { NAO_SAUDAVEL, 0.9200f };
          }
        } else {
          if (leitura.umidade_ar <= 34.3161f) {
            return { NAO_SAUDAVEL, 1.0000f };
          } else {
            if (leitura.temperatura <= 38.5113f) {
              if (leitura.umidade_solo <= 25.0372f) {
                return { NAO_SAUDAVEL, 0.8519f };
              } else {
                return { NAO_SAUDAVEL, 0.7188f };
              }
            } else {
              if (leitura.umidade_solo <= 25.4456f) {
                return { NAO_SAUDAVEL, 0.8400f };
              } else {
                return { NAO_SAUDAVEL, 0.9600f };
              }
            }
          }
        }
      }
    } else {
      if (leitura.temperatura <= 30.9338f) {
        if (leitura.temperatura <= 12.8934f) {
          if (leitura.temperatura <= 9.1086f) {
            if (leitura.luminosidade <= 55.0763f) {
              return { NAO_SAUDAVEL, 0.8421f };
            } else {
              return { NAO_SAUDAVEL, 0.5625f };
            }
          } else {
            if (leitura.umidade_solo <= 68.7825f) {
              if (leitura.umidade_ar <= 67.8953f) {
                return { SAUDAVEL, 0.5758f };
              } else {
                return { SAUDAVEL, 0.7778f };
              }
            } else {
              if (leitura.luminosidade <= 26.2236f) {
                return { NAO_SAUDAVEL, 0.7586f };
              } else {
                return { NAO_SAUDAVEL, 0.5147f };
              }
            }
          }
        } else {
          if (leitura.umidade_solo <= 85.9798f) {
            if (leitura.umidade_ar <= 49.4902f) {
              if (leitura.umidade_ar <= 30.5361f) {
                return { SAUDAVEL, 0.5630f };
              } else {
                return { SAUDAVEL, 0.7072f };
              }
            } else {
              if (leitura.umidade_ar <= 89.9654f) {
                return { SAUDAVEL, 0.8624f };
              } else {
                return { SAUDAVEL, 0.7477f };
              }
            }
          } else {
            if (leitura.temperatura <= 15.1482f) {
              return { NAO_SAUDAVEL, 0.7500f };
            } else {
              if (leitura.luminosidade <= 54.2471f) {
                return { SAUDAVEL, 0.6588f };
              } else {
                return { SAUDAVEL, 0.5057f };
              }
            }
          }
        }
      } else {
        if (leitura.umidade_solo <= 84.7577f) {
          if (leitura.umidade_solo <= 36.9184f) {
            if (leitura.temperatura <= 35.1760f) {
              return { NAO_SAUDAVEL, 0.5926f };
            } else {
              return { NAO_SAUDAVEL, 0.9111f };
            }
          } else {
            if (leitura.temperatura <= 38.8053f) {
              if (leitura.umidade_ar <= 47.3293f) {
                return { NAO_SAUDAVEL, 0.5000f };
              } else {
                return { SAUDAVEL, 0.6912f };
              }
            } else {
              if (leitura.temperatura <= 42.5866f) {
                return { NAO_SAUDAVEL, 0.5510f };
              } else {
                return { NAO_SAUDAVEL, 0.7593f };
              }
            }
          }
        } else {
          if (leitura.temperatura <= 38.8599f) {
            if (leitura.umidade_ar <= 76.7195f) {
              if (leitura.umidade_solo <= 91.4541f) {
                return { NAO_SAUDAVEL, 0.6389f };
              } else {
                return { NAO_SAUDAVEL, 0.9167f };
              }
            } else {
              return { NAO_SAUDAVEL, 0.5600f };
            }
          } else {
            if (leitura.umidade_solo <= 90.6039f) {
              return { NAO_SAUDAVEL, 0.8000f };
            } else {
              return { NAO_SAUDAVEL, 0.9744f };
            }
          }
        }
      }
    }
}

#endif  // MODELO_EMBARCADO_H
