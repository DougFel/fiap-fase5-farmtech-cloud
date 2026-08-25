"""
Prova que o C++ gerado decide exatamente igual ao modelo Python.

Transpilar um modelo so tem valor se a versao embarcada for fiel a original.
Este script compila o header com um main de teste, roda as 4000 amostras do
dataset pelas duas implementacoes e exige 100% de concordancia — qualquer
divergencia derruba a execucao.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

BASE = Path(__file__).resolve().parent
FIRMWARE = BASE.parent / "firmware"
GRANDEZAS = ["umidade_solo", "temperatura", "umidade_ar", "luminosidade"]
SEMENTE = 42

df = pd.read_csv(BASE / "saude_plantacao.csv")
X, y = df[GRANDEZAS], df["saudavel"]
X_tr, _, y_tr, _ = train_test_split(X, y, test_size=0.25,
                                    random_state=SEMENTE, stratify=y)

info = json.loads((BASE / "metricas.json").read_text(encoding="utf-8"))
arvore = DecisionTreeClassifier(max_depth=info["profundidade"],
                                min_samples_leaf=25, random_state=SEMENTE)
arvore.fit(X_tr, y_tr)
esperado = arvore.predict(X)

# Programa C++ que le as amostras da entrada padrao e imprime a classe.
PROGRAMA = r'''
#include <cstdio>
#include "modelo_embarcado.h"

int main() {
  Leitura l;
  while (scanf("%f %f %f %f", &l.umidade_solo, &l.temperatura,
               &l.umidade_ar, &l.luminosidade) == 4) {
    printf("%d\n", (int) classificarSaude(l).classe);
  }
  return 0;
}
'''

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    (tmp / "teste.cpp").write_text(PROGRAMA, encoding="utf-8")

    compilar = subprocess.run(
        ["c++", "-std=c++17", "-O2", f"-I{FIRMWARE}",
         str(tmp / "teste.cpp"), "-o", str(tmp / "teste")],
        capture_output=True, text=True)
    if compilar.returncode != 0:
        sys.exit(f"o header nao compila:\n{compilar.stderr[-800:]}")
    print("Compilação do header: OK")

    entrada = "\n".join(
        f"{r.umidade_solo} {r.temperatura} {r.umidade_ar} {r.luminosidade}"
        for r in df.itertuples()
    )
    execucao = subprocess.run([str(tmp / "teste")], input=entrada,
                              capture_output=True, text=True)
    obtido = [int(v) for v in execucao.stdout.split()]

if len(obtido) != len(esperado):
    sys.exit(f"tamanhos diferentes: C++ {len(obtido)} x Python {len(esperado)}")

divergencias = [i for i, (a, b) in enumerate(zip(obtido, esperado)) if a != b]
print(f"Amostras testadas   : {len(esperado)}")
print(f"Divergências        : {len(divergencias)}")

if divergencias:
    print("\nPrimeiras divergências:")
    for i in divergencias[:5]:
        print(f"  linha {i}: C++={obtido[i]} Python={esperado[i]}  "
              f"{df.iloc[i][GRANDEZAS].to_dict()}")
    sys.exit("A versão embarcada NÃO é fiel ao modelo treinado.")

print("\nO C++ embarcado reproduz o modelo Python em 100% das amostras.")
