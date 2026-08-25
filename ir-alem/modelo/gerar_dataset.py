"""
Gera o dataset de saude da plantacao usado para treinar o classificador
embarcado no ESP32.

POR QUE NAO USAR UMA REGRA DIRETA
---------------------------------
O caminho obvio seria rotular "saudavel" com um if/else sobre as leituras. O
problema e que o modelo treinado nesse dado apenas reaprende — pior — a regra
que o gerou, e a acuracia alta vira ilusao.

Aqui o rotulo sai de um processo probabilistico:

  1. cada grandeza contribui com um estresse continuo, medido pela distancia a
     sua faixa fisiologica otima;
  2. os estresses se somam em um log-odds, e nao em uma decisao binaria;
  3. entra um fator de vigor da planta que o ESP32 NAO mede — e por isso o
     modelo nunca podera explicar tudo (erro irredutivel);
  4. o desfecho e sorteado de uma Bernoulli.

O resultado e uma fronteira difusa: leituras identicas podem gerar rotulos
diferentes, exatamente como no campo.

Cultura de referencia: cafe arabica em estagio vegetativo, cujas faixas otimas
estao documentadas na literatura agronomica e sao compativeis com as condicoes
do dataset crop_yield usado na Entrega 1.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

SEMENTE = 42
N = 4000
BASE = Path(__file__).resolve().parent

# Faixas otimas por grandeza: (minimo, maximo) em que a planta nao sofre.
FAIXA_OTIMA = {
    "umidade_solo": (45.0, 75.0),      # % de capacidade de campo
    "temperatura": (18.0, 28.0),       # °C
    "umidade_ar": (60.0, 85.0),        # % de umidade relativa
    "luminosidade": (30.0, 80.0),      # % da escala do LDR
}

# Quanto cada grandeza pesa no estresse total. A umidade do solo domina: e o
# primeiro fator limitante em cultura de sequeiro.
PESO = {
    "umidade_solo": 2.6,
    "temperatura": 1.7,
    "umidade_ar": 1.0,
    "luminosidade": 0.9,
}

INTERCEPTO = -2.35   # calibra a prevalencia de plantas nao saudaveis
ESCALA_VIGOR = 1.15  # forca do fator nao observado


def estresse(valor: np.ndarray, faixa: tuple[float, float]) -> np.ndarray:
    """Distancia relativa ate a faixa otima, zero dentro dela.

    Cresce de forma suave para fora dos limites, normalizada pela largura da
    propria faixa — assim grandezas de escalas diferentes ficam comparaveis.
    """
    minimo, maximo = faixa
    largura = maximo - minimo
    abaixo = np.clip(minimo - valor, 0, None) / largura
    acima = np.clip(valor - maximo, 0, None) / largura
    return abaixo + acima


def gerar() -> pd.DataFrame:
    rng = np.random.default_rng(SEMENTE)

    # As leituras cobrem uma faixa bem mais larga que a otima, para o dataset
    # conter tanto situacoes confortaveis quanto extremos de seca e calor.
    dados = pd.DataFrame({
        "umidade_solo": rng.uniform(8, 98, N),
        "temperatura": rng.uniform(8, 44, N),
        "umidade_ar": rng.uniform(20, 99, N),
        "luminosidade": rng.uniform(2, 100, N),
    })

    # Soma ponderada dos estresses de cada grandeza.
    total = sum(
        PESO[grandeza] * estresse(dados[grandeza].to_numpy(), faixa)
        for grandeza, faixa in FAIXA_OTIMA.items()
    )

    # Interacao: solo seco com calor alto castiga mais do que a soma dos dois.
    seca = estresse(dados["umidade_solo"].to_numpy(), FAIXA_OTIMA["umidade_solo"])
    calor = estresse(dados["temperatura"].to_numpy(), FAIXA_OTIMA["temperatura"])
    total += 1.5 * seca * calor

    # Vigor da planta: idade, cultivar, historico de adubacao. O ESP32 nao tem
    # sensor para isso, entao vira erro irredutivel do modelo.
    vigor = rng.normal(0, ESCALA_VIGOR, N)

    log_odds = INTERCEPTO + total - vigor
    prob = 1 / (1 + np.exp(-log_odds))

    dados["prob_nao_saudavel"] = prob
    dados["saudavel"] = (rng.random(N) > prob).astype(int)
    return dados


if __name__ == "__main__":
    df = gerar()
    destino = BASE / "saude_plantacao.csv"
    df.drop(columns="prob_nao_saudavel").to_csv(destino, index=False)

    saudaveis = int(df["saudavel"].sum())
    print(f"{destino.name}: {len(df)} amostras")
    print(f"  saudáveis     : {saudaveis} ({saudaveis / len(df):.1%})")
    print(f"  não saudáveis : {len(df) - saudaveis} ({1 - saudaveis / len(df):.1%})")
    print(f"\n  probabilidade média de não saudável: {df['prob_nao_saudavel'].mean():.3f}")

    # Quanto do rótulo é, em princípio, previsível? O melhor classificador
    # possível é o que segue a própria probabilidade que gerou o dado.
    otimo = np.maximum(df["prob_nao_saudavel"], 1 - df["prob_nao_saudavel"]).mean()
    print(f"  teto teórico de acurácia (Bayes)  : {otimo:.3f}")

    (BASE / "dataset_info.json").write_text(json.dumps({
        "amostras": len(df),
        "saudaveis": saudaveis,
        "proporcao_saudavel": round(saudaveis / len(df), 4),
        "teto_bayes": round(float(otimo), 4),
        "faixas_otimas": FAIXA_OTIMA,
        "pesos": PESO,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
