"""
Consulta a API publica de precos da AWS e monta a comparacao pedida na
Entrega 2: uma maquina Linux com 2 vCPU, 1 GiB de memoria, ate 5 Gbps de rede e
50 GB de disco, em Sao Paulo e na Virginia do Norte, no modelo sob demanda.

A API usada e a mesma que alimenta a calculadora oficial
(https://calculator.aws), entao os valores conferem com ela.
"""
import json
import ssl
import urllib.request
from pathlib import Path

import certifi

# O Python instalado nesta maquina nao encontra o bundle de CAs do sistema.
CONTEXTO_SSL = ssl.create_default_context(cafile=certifi.where())

BASE = "https://pricing.us-east-1.amazonaws.com"
REGIOES = {"us-east-1": "Virgínia do Norte (EUA)", "sa-east-1": "São Paulo (BR)"}
INSTANCIA = "t3.micro"
DISCO_GB = 50
HORAS_MES = 730  # padrao adotado pela calculadora da AWS


def baixar(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300, context=CONTEXTO_SSL) as resp:
        return json.load(resp)


def preco_sob_demanda(oferta: dict, sku: str) -> float | None:
    for termo in oferta["terms"]["OnDemand"].get(sku, {}).values():
        for dim in termo["priceDimensions"].values():
            return float(dim["pricePerUnit"]["USD"])
    return None


def coletar(regiao: str) -> dict:
    indice = baixar(f"{BASE}/offers/v1.0/aws/AmazonEC2/current/region_index.json")
    oferta = baixar(BASE + indice["regions"][regiao]["currentVersionUrl"])

    resultado = {"regiao": regiao, "nome": REGIOES[regiao]}

    for sku, p in oferta["products"].items():
        a = p.get("attributes", {})

        # A instancia: Linux, sob demanda, sem licenca e tenancy compartilhado.
        if (p.get("productFamily") == "Compute Instance"
                and a.get("instanceType") == INSTANCIA
                and a.get("operatingSystem") == "Linux"
                and a.get("tenancy") == "Shared"
                and a.get("preInstalledSw") == "NA"
                and a.get("capacitystatus") == "Used"
                and a.get("licenseModel") == "No License required"):
            valor = preco_sob_demanda(oferta, sku)
            if valor:
                resultado.update({
                    "hora_usd": valor,
                    "vcpu": a.get("vcpu"),
                    "memoria": a.get("memory"),
                    "rede": a.get("networkPerformance"),
                    "processador": a.get("physicalProcessor"),
                })

        # O disco: EBS gp3.
        if (p.get("productFamily") == "Storage"
                and a.get("volumeApiName") == "gp3"):
            valor = preco_sob_demanda(oferta, sku)
            if valor:
                resultado["disco_gb_mes_usd"] = valor

    return resultado


if __name__ == "__main__":
    linhas = []
    for regiao in REGIOES:
        r = coletar(regiao)
        r["computacao_mes"] = r["hora_usd"] * HORAS_MES
        r["armazenamento_mes"] = r["disco_gb_mes_usd"] * DISCO_GB
        r["total_mes"] = r["computacao_mes"] + r["armazenamento_mes"]
        r["total_ano"] = r["total_mes"] * 12
        linhas.append(r)

    for r in linhas:
        print(f"\n=== {r['nome']} ({r['regiao']}) ===")
        print(f"  {INSTANCIA}: {r['vcpu']} vCPU | {r['memoria']} | {r['rede']}")
        print(f"  processador          : {r['processador']}")
        print(f"  computação           : US$ {r['hora_usd']:.5f}/h "
              f"x {HORAS_MES}h = US$ {r['computacao_mes']:.2f}/mês")
        print(f"  disco gp3 {DISCO_GB} GB     : US$ {r['disco_gb_mes_usd']:.4f}/GB-mês "
              f"= US$ {r['armazenamento_mes']:.2f}/mês")
        print(f"  TOTAL                : US$ {r['total_mes']:.2f}/mês "
              f"| US$ {r['total_ano']:.2f}/ano")

    virginia, sao_paulo = linhas[0], linhas[1]
    dif = sao_paulo["total_mes"] - virginia["total_mes"]
    print(f"\n=== COMPARAÇÃO ===")
    print(f"  São Paulo custa US$ {dif:.2f}/mês a mais "
          f"({dif / virginia['total_mes'] * 100:.1f}% acima da Virgínia)")
    print(f"  Diferença anual: US$ {dif * 12:.2f}")

    destino = Path(__file__).parent / "precos_aws.json"
    destino.write_text(json.dumps(linhas, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSalvo em {destino.name}")
