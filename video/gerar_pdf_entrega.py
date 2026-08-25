"""Gera o PDF de entrega, com os links do repositorio e dos dois videos."""
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent.parent
REPO = "https://github.com/DougFel/fiap-fase5-farmtech-cloud"
VIDEO_1 = "https://youtu.be/gjgxBpAXDzs"
VIDEO_2 = "https://youtu.be/P23q50v1mWo"
VIDEO_3 = "https://youtu.be/4ov0sx2JYwo"
REPO_IR_ALEM = REPO + "/tree/main/ir-alem"

HTML = f"""
<!doctype html><meta charset="utf-8">
<style>
  @page {{ size: A4; margin: 20mm 18mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font: 11pt/1.55 -apple-system, "Helvetica Neue", Arial, sans-serif;
          color: #1a1d21; margin: 0; }}
  /* Sem ligaduras: "fi" viraria o caractere U+FB01 e o link, ao ser copiado
     do PDF, deixaria de funcionar. */
  a, code, .link {{ font-variant-ligatures: none; -webkit-font-feature-settings: "liga" 0; }}
  .capa {{ border-bottom: 3px solid #ed145b; padding-bottom: 14px; margin-bottom: 22px; }}
  .fase {{ color: #ed145b; font-size: 9.5pt; letter-spacing: .13em;
           text-transform: uppercase; font-weight: 700; }}
  h1 {{ font-size: 19pt; margin: 7px 0 4px; letter-spacing: -.3px; }}
  .sub {{ color: #5c6570; font-size: 10.5pt; }}
  .aluno {{ background: #f5f6f8; border-left: 3px solid #ed145b;
            padding: 11px 15px; margin: 20px 0; font-size: 10.5pt; }}
  h2 {{ font-size: 12.5pt; margin: 24px 0 9px; padding-bottom: 5px;
        border-bottom: 1px solid #dde1e6; }}
  .link {{ background: #f5f6f8; border: 1px solid #dde1e6; border-radius: 6px;
           padding: 12px 15px; margin: 9px 0; }}
  .link .rot {{ font-size: 8.5pt; text-transform: uppercase; letter-spacing: .09em;
                color: #5c6570; font-weight: 700; margin-bottom: 3px; }}
  .link a {{ color: #0b5cd5; font-size: 11pt; word-break: break-all;
             text-decoration: none; font-weight: 600; }}
  .link .obs {{ font-size: 9pt; color: #5c6570; margin-top: 3px; }}
  ul {{ margin: 7px 0 7px 17px; padding: 0; }}
  li {{ margin-bottom: 4px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 10pt; }}
  th, td {{ border: 1px solid #dde1e6; padding: 6px 10px; text-align: left; }}
  th {{ background: #f5f6f8; font-weight: 600; }}
  .destaque {{ background: #fff8e6; border-left: 3px solid #e8a317;
               padding: 10px 14px; margin: 12px 0; font-size: 10pt; }}
  .rodape {{ margin-top: 26px; padding-top: 11px; border-top: 1px solid #dde1e6;
             font-size: 8.5pt; color: #8b939c; }}
</style>

<div class="capa">
  <div class="fase">FIAP · Inteligência Artificial · Fase 5</div>
  <h1>Cap 1 — FarmTech na Era da Cloud Computing</h1>
  <div class="sub">Machine Learning na cabeça · Entregas 1 e 2</div>
</div>

<div class="aluno">
  <strong>Douglas Felicio da Silva</strong> — RM 572312<br>
  Turma 1TIAOA · 2026/1 · Grupo 56
</div>

<h2>Repositório da entrega</h2>
<div class="link">
  <div class="rot">GitHub — público</div>
  <a href="{REPO}">{REPO}</a>
  <div class="obs">Contém o notebook Jupyter, o README com as duas entregas,
  a base de dados e as imagens.</div>
</div>

<h2>Entrega 1 — Machine Learning</h2>
<p>Análise exploratória, clusterização e cinco modelos preditivos sobre a base
<code>crop_yield.csv</code>, para prever o rendimento de safra de quatro culturas.</p>

<ul>
  <li><strong>Notebook:</strong> <code>notebook/DouglasFelicioDaSilva_rm572312_pbl_fase4.ipynb</code>
      — 29 células de código executadas, 24 de markdown, 9 gráficos</li>
  <li><strong>Clusterização:</strong> K-Means (cotovelo e silhueta), DBSCAN e PCA</li>
  <li><strong>Outliers:</strong> três cenários discrepantes identificados e discutidos</li>
  <li><strong>Modelos:</strong> Regressão Linear, Árvore de Decisão, Random Forest,
      Gradient Boosting e SVR</li>
  <li><strong>Métricas:</strong> R², RMSE, MAE e MAPE, com validação cruzada de 5 partições</li>
</ul>

<div class="link">
  <div class="rot">Vídeo da Entrega 1 — não listado</div>
  <a href="{VIDEO_1}">{VIDEO_1}</a>
  <div class="obs">4min49s</div>
</div>

<div class="destaque">
  <strong>Principal achado.</strong> Um baseline que ignora o clima e prevê apenas a
  média histórica de cada cultura atinge R² = 0,9842 — superando os cinco modelos.
  A cultura plantada, sozinha, explica 98,76% da variância do rendimento. O relatório
  demonstra por que o R² global engana nesta base e propõe medir o acerto dentro de
  cada cultura.
</div>

<h2>Entrega 2 — Computação em Nuvem</h2>
<p>Estimativa de custos na calculadora da AWS, no modelo sob demanda (100%), para
uma máquina Linux com 2 vCPU, 1 GiB de memória, até 5 Gigabit de rede e 50 GB de
disco — instância <strong>t3.micro</strong> com volume EBS gp3.</p>

<table>
  <tr><th>Item</th><th>Virgínia do Norte</th><th>São Paulo</th></tr>
  <tr><td>EC2 t3.micro (730 h)</td><td>US$ 7,59</td><td>US$ 12,26</td></tr>
  <tr><td>EBS gp3 (50 GB)</td><td>US$ 4,00</td><td>US$ 7,60</td></tr>
  <tr><td><strong>Total mensal</strong></td><td><strong>US$ 11,59</strong></td>
      <td><strong>US$ 19,86</strong></td></tr>
</table>

<p><strong>Decisão: São Paulo (sa-east-1).</strong> Apesar de 71% mais cara, é a
opção correta diante das duas restrições do enunciado: a latência do Brasil cai de
~130 ms para ~15 ms, e manter os dados em território nacional elimina a
transferência internacional e as exigências do art. 33 da LGPD. A diferença de
US$ 8,27 por mês não compensa o risco jurídico nem a latência oito vezes maior.</p>

<div class="link">
  <div class="rot">Vídeo da Entrega 2 — não listado</div>
  <a href="{VIDEO_2}">{VIDEO_2}</a>
  <div class="obs">3min14s</div>
</div>

<h2>Ir Além — Opção 2: classificação da saúde da plantação</h2>
<p>Entrega extra, sem valor de nota. Um <strong>ESP32 classifica a saúde da
plantação sozinho</strong>: o modelo foi treinado em Python com scikit-learn e
<strong>transpilado para C++ puro</strong>, virando parte do firmware. A placa
não depende de servidor nem de conexão para decidir.</p>

<ul>
  <li><strong>Três sensores:</strong> DHT22 (temperatura e umidade do ar), sensor
      capacitivo de umidade do solo e LDR — os analógicos no ADC1, porque o ADC2
      é usado pelo rádio Wi-Fi</li>
  <li><strong>Saídas:</strong> LED local, página HTML servida pelo próprio ESP32
      e publicação MQTT</li>
  <li><strong>Modelo:</strong> árvore de decisão com 89 nós, acurácia 0,676 contra
      um teto teórico de Bayes de 0,779 — 86,8% do máximo possível</li>
  <li><strong>Verificação:</strong> o C++ embarcado reproduz o modelo Python em
      4.000 de 4.000 amostras; 9 testes automatizados cobrem o firmware</li>
</ul>

<p>Como também coleta dados com sensores distintos, conecta por Wi-Fi e publica
em MQTT e em página HTML, a solução cumpre igualmente os requisitos técnicos da
<strong>Opção 1</strong>.</p>

<div class="link">
  <div class="rot">Seção "Ir Além" no GitHub</div>
  <a href="{REPO_IR_ALEM}">{REPO_IR_ALEM}</a>
  <div class="obs">Firmware, modelo, testes, figura da arquitetura e documentação.</div>
</div>

<div class="link">
  <div class="rot">Vídeo do Ir Além — não listado</div>
  <a href="{VIDEO_3}">{VIDEO_3}</a>
  <div class="obs">4min49s</div>
</div>

<div class="rodape">
  Os três vídeos estão publicados no YouTube como <em>não listados</em> e seus links
  constam no README do repositório, conforme o enunciado. O Ir Além não houve
  execução em hardware físico — o que foi executado foram os testes automatizados.
</div>
"""


def gerar() -> Path:
    destino = BASE / "AgroFarmTech_Fase5_Cap1_Entrega_RM572312.pdf"
    origem = BASE / "video" / ".entrega.html"
    origem.write_text(HTML, encoding="utf-8")

    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page()
        pagina.goto(origem.as_uri())
        pagina.wait_for_timeout(1200)
        pagina.pdf(path=str(destino), format="A4", print_background=True)
        navegador.close()

    origem.unlink(missing_ok=True)
    return destino


if __name__ == "__main__":
    d = gerar()
    print(f"{d.name}: {d.stat().st_size / 1024:.0f} KB")
