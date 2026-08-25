"""Gera a figura de arquitetura exigida pelo enunciado do Ir Alem."""
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent.parent
SAIDA = BASE.parent / "imagens" / "ir_alem_arquitetura.png"

HTML = """
<!doctype html><meta charset="utf-8">
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font:13px/1.45 -apple-system,"Segoe UI",Roboto,sans-serif;
       background:#0d1319;color:#e6edf3;padding:30px;width:1180px}
  h1{font-size:17px;margin-bottom:2px}
  .sub{color:#7d8b99;font-size:12px;margin-bottom:24px}
  .fluxo{display:flex;align-items:stretch;gap:14px}
  .col{display:flex;flex-direction:column;gap:10px;justify-content:center}
  .bloco{background:#151e28;border:1px solid #243240;border-radius:9px;
         padding:12px 14px;min-width:158px}
  .bloco .rot{font-size:9.5px;text-transform:uppercase;letter-spacing:.1em;
              color:#7d8b99;font-weight:700;margin-bottom:5px}
  .bloco .nome{font-size:13.5px;font-weight:600;margin-bottom:3px}
  .bloco .det{font-size:11px;color:#8f9ead;line-height:1.4}
  .sensor{border-left:3px solid #3fb950}
  .placa{border-left:3px solid #d29922;min-width:236px}
  .saida{border-left:3px solid #58a6ff}
  .modelo{border-left:3px solid #bc8cff;min-width:236px}
  .seta{display:flex;align-items:center;color:#3d4d5c;font-size:22px}
  .destaque{background:#1a2430;border-color:#bc8cff}
  .badge{display:inline-block;background:#2d1f45;color:#d2a8ff;font-size:9.5px;
         padding:2px 7px;border-radius:20px;margin-top:6px;font-weight:600}
  .nota{margin-top:22px;padding:11px 14px;background:#151e28;
        border-left:3px solid #d29922;border-radius:0 8px 8px 0;
        font-size:11.5px;color:#8f9ead}
  .nota b{color:#e6edf3}
  .pino{font-family:ui-monospace,monospace;color:#d29922;font-size:10.5px}
</style>

<h1>FarmTech Solutions — classificação da saúde da plantação na borda</h1>
<div class="sub">FIAP · Fase 5 · Cap 1 — Ir Além · Douglas Felicio da Silva — RM 572312</div>

<div class="fluxo">
  <div class="col">
    <div class="bloco sensor">
      <div class="rot">Sensor · digital</div>
      <div class="nome">DHT22</div>
      <div class="det">temperatura + umidade do ar<br><span class="pino">GPIO 15</span></div>
    </div>
    <div class="bloco sensor">
      <div class="rot">Sensor · analógico</div>
      <div class="nome">Umidade do solo</div>
      <div class="det">capacitivo, % cap. de campo<br><span class="pino">GPIO 34 · ADC1</span></div>
    </div>
    <div class="bloco sensor">
      <div class="rot">Sensor · analógico</div>
      <div class="nome">LDR</div>
      <div class="det">luminosidade<br><span class="pino">GPIO 35 · ADC1</span></div>
    </div>
  </div>

  <div class="seta">&#10142;</div>

  <div class="col">
    <div class="bloco placa">
      <div class="rot">Aquisição</div>
      <div class="nome">ESP32 — pré-processamento</div>
      <div class="det">
        ADC de 12 bits, atenuação 11 dB<br>
        média móvel de 10 amostras<br>
        botão por interrupção + debounce
      </div>
    </div>
    <div class="bloco modelo destaque">
      <div class="rot">Inferência na borda</div>
      <div class="nome">Árvore de decisão embarcada</div>
      <div class="det">
        treinada em Python (scikit-learn)<br>
        transpilada para C++ · 89 nós<br>
        acurácia 0,676 · teto de Bayes 0,779
      </div>
      <span class="badge">roda sem servidor · microssegundos</span>
    </div>
  </div>

  <div class="seta">&#10142;</div>

  <div class="col">
    <div class="bloco saida">
      <div class="rot">Local</div>
      <div class="nome">LED verde / vermelho</div>
      <div class="det">alerta imediato no campo,<br>independe de rede</div>
    </div>
    <div class="bloco saida">
      <div class="rot">Local</div>
      <div class="nome">Página HTML</div>
      <div class="det">servidor HTTP no ESP32<br>porta 80, atualiza a cada 5 s</div>
    </div>
    <div class="bloco saida">
      <div class="rot">Nuvem</div>
      <div class="nome">MQTT</div>
      <div class="det">broker.hivemq.com<br>leitura · diagnóstico · alerta</div>
    </div>
  </div>
</div>

<div class="nota">
  <b>Por que os sensores analógicos estão no ADC1:</b> o ADC2 do ESP32 é usado
  internamente pelo rádio Wi-Fi e fica indisponível com a conexão ativa. Como o
  Wi-Fi permanece ligado, os dois analógicos foram ligados a pinos do ADC1
  (GPIO 32–39) — caso contrário as leituras seriam erráticas.
</div>
"""


def gerar() -> Path:
    origem = BASE / "modelo" / ".arquitetura.html"
    origem.write_text(HTML, encoding="utf-8")
    SAIDA.parent.mkdir(exist_ok=True)

    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": 1180, "height": 640},
                           device_scale_factor=2)
        pag.goto(origem.as_uri())
        pag.wait_for_timeout(900)
        pag.screenshot(path=str(SAIDA), full_page=True)
        nav.close()

    origem.unlink(missing_ok=True)
    return SAIDA


if __name__ == "__main__":
    d = gerar()
    print(f"{d.name}: {d.stat().st_size / 1024:.0f} KB")
