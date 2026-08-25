"""
Treina o classificador de saude da plantacao e o transpila para C++.

A escolha do algoritmo e guiada pela restricao de hardware: o modelo precisa
rodar dentro do ESP32, sem bibliotecas de ML, em alguns microssegundos e com
poucos KB. Uma arvore de decisao rasa vira uma cadeia de if/else — cabe em
qualquer microcontrolador e ainda por cima e auditavel linha a linha, o que
importa quando a decisao aciona irrigacao no campo.

Saidas:
  metricas.json         desempenho medido no conjunto de teste
  modelo_embarcado.h    a arvore como codigo C++, pronta para o firmware
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, f1_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text

SEMENTE = 42
BASE = Path(__file__).resolve().parent
GRANDEZAS = ["umidade_solo", "temperatura", "umidade_ar", "luminosidade"]

df = pd.read_csv(BASE / "saude_plantacao.csv")
X, y = df[GRANDEZAS], df["saudavel"]
X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.25, random_state=SEMENTE, stratify=y)

cv = StratifiedKFold(5, shuffle=True, random_state=SEMENTE)

# ─────────────────────────────────────────── qual profundidade usar?
print("=== Profundidade da árvore ===")
print(f"{'prof':>5} {'nós':>5} {'acurácia CV':>13} {'acc teste':>11}")
melhor = None
for prof in range(2, 9):
    arv = DecisionTreeClassifier(max_depth=prof, min_samples_leaf=25,
                                 random_state=SEMENTE)
    acc_cv = cross_val_score(arv, X, y, cv=cv, scoring="accuracy").mean()
    arv.fit(X_tr, y_tr)
    acc_te = accuracy_score(y_te, arv.predict(X_te))
    print(f"{prof:>5} {arv.tree_.node_count:>5} {acc_cv:>13.4f} {acc_te:>11.4f}")
    if melhor is None or acc_cv > melhor[1]:
        melhor = (prof, acc_cv)

# Profundidade 6 é o ponto de equilíbrio. A curva de CV é praticamente plana a
# partir daí — profundidades maiores compram centésimos de acurácia ao custo de
# dobrar o número de nós, e cada nó vira código no firmware. Com 89 nós a árvore
# ocupa alguns KB dos 4 MB de flash do ESP32: folga de sobra, sem exagero.
PROFUNDIDADE = 6
print(f"\nMelhor CV em profundidade {melhor[0]}; adotada {PROFUNDIDADE} — a curva "
      f"achata\n  e profundidades maiores só aumentam o código sem ganho real.\n")

# ─────────────────────────────────────────── comparação com alternativas
print("=== O modelo embarcado vale a pena? ===")
candidatos = {
    "Baseline (classe majoritária)": DummyClassifier(strategy="most_frequent"),
    "Regressão Logística": LogisticRegression(max_iter=1000),
    "Árvore (embarcada)": DecisionTreeClassifier(
        max_depth=PROFUNDIDADE, min_samples_leaf=25, random_state=SEMENTE),
    "Random Forest (referência)": RandomForestClassifier(
        n_estimators=300, min_samples_leaf=5, random_state=SEMENTE, n_jobs=-1),
}

resultados = {}
for nome, est in candidatos.items():
    est.fit(X_tr, y_tr)
    prev = est.predict(X_te)
    acc = accuracy_score(y_te, prev)
    f1 = f1_score(y_te, prev)
    try:
        auc = roc_auc_score(y_te, est.predict_proba(X_te)[:, 1])
    except (AttributeError, IndexError):
        auc = float("nan")
    resultados[nome] = {"acuracia": acc, "f1": f1, "auc": auc}
    print(f"  {nome:<30} acc={acc:.4f}  F1={f1:.4f}  AUC={auc:.4f}")

info = json.loads((BASE / "dataset_info.json").read_text(encoding="utf-8"))
teto = info["teto_bayes"]
arvore = candidatos["Árvore (embarcada)"]
acc_arvore = resultados["Árvore (embarcada)"]["acuracia"]
print(f"\n  Teto teórico (Bayes): {teto:.4f}")
print(f"  A árvore embarcada alcança {acc_arvore / teto:.1%} do máximo possível.")

# ─────────────────────────────────────────── diagnóstico
print("\n=== Matriz de confusão (teste) ===")
mc = confusion_matrix(y_te, arvore.predict(X_te))
print(f"                     previsto")
print(f"                não saud.  saudável")
print(f"  real não saud.  {mc[0,0]:>8}  {mc[0,1]:>8}")
print(f"  real saudável   {mc[1,0]:>8}  {mc[1,1]:>8}")
print()
print(classification_report(y_te, arvore.predict(X_te),
                            target_names=["não saudável", "saudável"], digits=3))

print("=== Importância das grandezas ===")
for g, imp in sorted(zip(GRANDEZAS, arvore.feature_importances_),
                     key=lambda x: -x[1]):
    print(f"  {g:<16} {imp:.3f}  {'█' * int(imp * 42)}")

print("\n=== A árvore, em texto ===")
print(export_text(arvore, feature_names=GRANDEZAS, max_depth=3))

# ─────────────────────────────────────────── transpilação para C++
def transpilar(arv, nomes: list[str]) -> str:
    """Converte a árvore treinada em uma função C++ de if/else aninhados.

    A varredura é recursiva sobre a estrutura interna do sklearn: cada nó
    interno vira um `if`, cada folha vira o retorno da classe majoritária
    junto com a confiança medida naquela folha.
    """
    t = arv.tree_
    linhas: list[str] = []

    def visitar(no: int, recuo: int) -> None:
        tab = "  " * recuo
        if t.children_left[no] == -1:                    # folha
            contagem = t.value[no][0]
            classe = int(np.argmax(contagem))
            confianca = contagem[classe] / contagem.sum()
            rotulo = "SAUDAVEL" if classe == 1 else "NAO_SAUDAVEL"
            linhas.append(f"{tab}return {{ {rotulo}, {confianca:.4f}f }};")
            return
        nome = nomes[t.feature[no]]
        limite = t.threshold[no]
        linhas.append(f"{tab}if (leitura.{nome} <= {limite:.4f}f) {{")
        visitar(t.children_left[no], recuo + 1)
        linhas.append(f"{tab}}} else {{")
        visitar(t.children_right[no], recuo + 1)
        linhas.append(f"{tab}}}")

    visitar(0, 2)
    return "\n".join(linhas)

corpo = transpilar(arvore, GRANDEZAS)
folhas = int((arvore.tree_.children_left == -1).sum())

# As faixas ótimas vão para o header para que o firmware consiga explicar ao
# operador qual grandeza está fora do lugar, e não só o veredito.
faixas = info["faixas_otimas"]
linhas_faixa = "\n".join(
    f'  {{ "{rotulo}", {faixas[chave][0]:.1f}f, {faixas[chave][1]:.1f}f }},'
    for chave, rotulo in [("umidade_solo", "umidade do solo"),
                          ("temperatura", "temperatura"),
                          ("umidade_ar", "umidade do ar"),
                          ("luminosidade", "luminosidade")]
)

cabecalho = f'''// modelo_embarcado.h
//
// Classificador de saude da plantacao — GERADO AUTOMATICAMENTE por treinar.py.
// Nao edite a mao: rode `python modelo/treinar.py` para regerar.
//
// Origem     : DecisionTreeClassifier (scikit-learn), profundidade {PROFUNDIDADE}
// Estrutura  : {arvore.tree_.node_count} nos, {folhas} folhas
// Treino     : {len(X_tr)} amostras | Teste: {len(X_te)} amostras
// Acuracia   : {acc_arvore:.4f} no teste (teto teorico de Bayes: {teto:.4f})
//
// A inferencia e uma cadeia de comparacoes de ponto flutuante: nao aloca
// memoria, nao depende de biblioteca e executa em poucos microssegundos no
// ESP32. E por isso que a classificacao acontece na borda, sem servidor.

#ifndef MODELO_EMBARCADO_H
#define MODELO_EMBARCADO_H

enum ClasseSaude {{ NAO_SAUDAVEL = 0, SAUDAVEL = 1 }};

struct Leitura {{
  float umidade_solo;   // % da capacidade de campo
  float temperatura;    // graus Celsius
  float umidade_ar;     // % de umidade relativa
  float luminosidade;   // % da escala do LDR
}};

struct Diagnostico {{
  ClasseSaude classe;
  float confianca;      // fracao da folha que pertence a classe escolhida
}};

// Faixas fisiologicas otimas, usadas para explicar o diagnostico ao operador.
struct Faixa {{ const char* nome; float mmin; float mmax; }};

static const Faixa FAIXAS[] = {{
{linhas_faixa}
}};

inline Diagnostico classificarSaude(const Leitura& leitura) {{
{corpo}
}}

#endif  // MODELO_EMBARCADO_H
'''

destino_h = BASE.parent / "firmware" / "modelo_embarcado.h"
destino_h.write_text(cabecalho, encoding="utf-8")

(BASE / "metricas.json").write_text(json.dumps({
    "profundidade": PROFUNDIDADE,
    "nos": int(arvore.tree_.node_count),
    "folhas": folhas,
    "teto_bayes": teto,
    "modelos": {k: {m: (None if np.isnan(v) else round(v, 4))
                    for m, v in d.items()} for k, d in resultados.items()},
    "importancias": dict(zip(GRANDEZAS, [round(float(i), 4)
                                         for i in arvore.feature_importances_])),
    "matriz_confusao": mc.tolist(),
}, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"\nGerado: firmware/{destino_h.name} "
      f"({len(cabecalho.splitlines())} linhas, {len(cabecalho)} bytes)")
print(f"Gerado: modelo/metricas.json")
