"""Gera as figuras da comparacao de custos usadas no README (Entrega 2)."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

BASE = Path(__file__).resolve().parent
SAIDA = BASE.parent / "imagens"
dados = json.loads((BASE / "precos_aws.json").read_text(encoding="utf-8"))
virginia, sao_paulo = dados

plt.rcParams.update({"figure.dpi": 130, "font.size": 10})
AZUL, LARANJA = "#4c72b0", "#dd8452"

# ─────────────────────────────────────────── 1. composicao do custo mensal
fig, eixos = plt.subplots(1, 2, figsize=(11, 4.2))

regioes = ["Virgínia do Norte\n(us-east-1)", "São Paulo\n(sa-east-1)"]
computacao = [virginia["computacao_mes"], sao_paulo["computacao_mes"]]
disco = [virginia["armazenamento_mes"], sao_paulo["armazenamento_mes"]]
x = np.arange(2)

eixos[0].bar(x, computacao, .55, label="EC2 t3.micro (730 h)", color=AZUL)
eixos[0].bar(x, disco, .55, bottom=computacao, label="EBS gp3 (50 GB)", color=LARANJA)
for i, (c, d) in enumerate(zip(computacao, disco)):
    eixos[0].text(i, c / 2, f"US$ {c:.2f}", ha="center", va="center",
                  color="white", fontweight="bold")
    eixos[0].text(i, c + d / 2, f"US$ {d:.2f}", ha="center", va="center",
                  color="white", fontweight="bold")
    eixos[0].text(i, c + d + .5, f"US$ {c + d:.2f}", ha="center", fontweight="bold")
eixos[0].set(title="Custo mensal — sob demanda (100%)", ylabel="US$ / mês",
             xticks=x, xticklabels=regioes, ylim=(0, 23))
eixos[0].legend(fontsize=8, loc="upper left")
eixos[0].grid(axis="y", alpha=.3)

# ─────────────────────────────────────────── 2. diferenca por item
itens = ["EC2\n(computação)", "EBS gp3\n(50 GB)", "TOTAL"]
va = [virginia["computacao_mes"], virginia["armazenamento_mes"], virginia["total_mes"]]
sp = [sao_paulo["computacao_mes"], sao_paulo["armazenamento_mes"], sao_paulo["total_mes"]]
larg = .36
xi = np.arange(3)

eixos[1].bar(xi - larg / 2, va, larg, label="Virgínia do Norte", color=AZUL)
eixos[1].bar(xi + larg / 2, sp, larg, label="São Paulo", color=LARANJA)
for i, (a, b) in enumerate(zip(va, sp)):
    eixos[1].text(i - larg / 2, a + .3, f"{a:.2f}", ha="center", fontsize=8)
    eixos[1].text(i + larg / 2, b + .3, f"{b:.2f}", ha="center", fontsize=8)
    eixos[1].text(i, max(a, b) + 1.6, f"+{(b - a) / a * 100:.0f}%",
                  ha="center", fontsize=9, fontweight="bold", color="#c44e52")
eixos[1].set(title="São Paulo x Virgínia do Norte, item a item",
             ylabel="US$ / mês", xticks=xi, xticklabels=itens, ylim=(0, 24))
eixos[1].legend(fontsize=8)
eixos[1].grid(axis="y", alpha=.3)

plt.tight_layout()
plt.savefig(SAIDA / "aws_custo_mensal.png", bbox_inches="tight")
print("aws_custo_mensal.png")

# ─────────────────────────────────────────── 3. projecao no tempo
fig, eixo = plt.subplots(figsize=(8, 4))
meses = np.arange(0, 37)
eixo.plot(meses, meses * virginia["total_mes"], lw=2.2, color=AZUL,
          label=f"Virgínia do Norte — US$ {virginia['total_mes']:.2f}/mês")
eixo.plot(meses, meses * sao_paulo["total_mes"], lw=2.2, color=LARANJA,
          label=f"São Paulo — US$ {sao_paulo['total_mes']:.2f}/mês")
eixo.fill_between(meses, meses * virginia["total_mes"], meses * sao_paulo["total_mes"],
                  alpha=.18, color=LARANJA)

for m in (12, 24, 36):
    dif = m * (sao_paulo["total_mes"] - virginia["total_mes"])
    eixo.annotate(f"+US$ {dif:.0f}", xy=(m, m * sao_paulo["total_mes"]),
                  xytext=(m - 3.2, m * sao_paulo["total_mes"] + 42),
                  fontsize=8.5, color="#c44e52", fontweight="bold")

eixo.set(title="Custo acumulado em três anos", xlabel="meses",
         ylabel="US$ acumulados", xlim=(0, 37))
eixo.legend(fontsize=9)
eixo.grid(alpha=.3)
plt.tight_layout()
plt.savefig(SAIDA / "aws_custo_acumulado.png", bbox_inches="tight")
print("aws_custo_acumulado.png")

# ─────────────────────────────────────────── 4. latencia x custo
fig, eixo = plt.subplots(figsize=(8, 4.2))
# Latencias tipicas medidas de um cliente no Brasil (ida e volta).
pontos = {
    "São Paulo\n(sa-east-1)": (sao_paulo["total_mes"], 15),
    "Virgínia do Norte\n(us-east-1)": (virginia["total_mes"], 130),
}
for nome, (custo, lat) in pontos.items():
    cor = LARANJA if "São Paulo" in nome else AZUL
    eixo.scatter(custo, lat, s=340, color=cor, zorder=3, edgecolors="white", lw=2)
    eixo.annotate(f"{nome}\nUS$ {custo:.2f}/mês · ~{lat} ms",
                  xy=(custo, lat), xytext=(custo - 3.6, lat + 16),
                  fontsize=9, fontweight="bold")

eixo.axhspan(0, 50, alpha=.09, color="green")
eixo.text(8.2, 26, "faixa adequada para ingestão de sensores em tempo real",
          fontsize=8.5, style="italic", color="darkgreen")
eixo.set(title="O trade-off real: custo mensal x latência para o cliente no Brasil",
         xlabel="custo mensal (US$)", ylabel="latência de ida e volta (ms)",
         xlim=(6, 24), ylim=(0, 175))
eixo.grid(alpha=.3)
plt.tight_layout()
plt.savefig(SAIDA / "aws_latencia_custo.png", bbox_inches="tight")
print("aws_latencia_custo.png")
