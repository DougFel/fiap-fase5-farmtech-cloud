"""
Produz um video completo: narracao, captura de tela e mixagem.

A ordem importa. Primeiro sintetiza cada fala e mede sua duracao real; so entao
define a janela de tela de cada bloco (fala + folga) e grava a captura com
exatamente essas janelas. Assim a tela nunca fica dessincronizada da narracao, e
o total e conhecido antes de gravar — o que permite abortar se passar dos cinco
minutos exigidos pelo enunciado.

Uso:
    python produzir.py 1
    python produzir.py 2 --ppm 182
    python produzir.py 1 --audio minha_voz.m4a    # substitui a sintese
"""
import argparse
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from blocos import PAGINA, VIDEOS

BASE = Path(__file__).resolve().parent
TRABALHO = BASE / ".trabalho"
CAPTURA = BASE / "captura"
LARGURA, ALTURA = 1600, 900
FOLGA = 2.2          # segundos de respiro entre o fim da fala e o proximo bloco
LIMITE = 300         # o enunciado exige video de ate 5 minutos


def executar(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        sys.exit(f"falhou: {' '.join(cmd[:4])}...\n{r.stderr.decode()[-500:]}")


def duracao(caminho: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(caminho)],
        capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def sintetizar(numero: int, voz: str, ppm: int) -> list[dict]:
    """Sintetiza cada bloco e devolve a duracao medida de cada fala."""
    TRABALHO.mkdir(exist_ok=True)
    print(f"Sintetizando com a voz {voz} a {ppm} ppm:")

    blocos, inicio = [], 0.0
    for i, (ancora, fala) in enumerate(VIDEOS[numero], 1):
        bruto = TRABALHO / f"v{numero}_b{i}.aiff"
        wav = TRABALHO / f"v{numero}_b{i}.wav"
        executar(["say", "-v", voz, "-r", str(ppm), "-o", str(bruto),
                  " ".join(fala.split())])
        executar(["ffmpeg", "-y", "-i", str(bruto), "-ar", "48000", "-ac", "2",
                  str(wav)])

        falado = duracao(wav)
        janela = falado + FOLGA
        blocos.append({"ancora": ancora, "audio": wav,
                       "inicio": inicio, "janela": janela})
        print(f"  {i:>2}. {falado:5.1f}s → janela {janela:5.1f}s  "
              f"@{inicio:6.1f}s  {ancora[:40]}")
        inicio += janela

    total = inicio
    print(f"\nTotal narrado: {int(total // 60)}min{int(total % 60):02d}s")
    if total > LIMITE:
        sys.exit(f"ACIMA do limite de 5 minutos ({total:.0f}s). "
                 f"Encurte os textos em blocos.py ou aumente --ppm.")
    print(f"Folga até o limite de 5min: {LIMITE - total:.0f}s\n")
    return blocos


def capturar(numero: int, blocos: list[dict]) -> Path:
    """Grava a tela parando em cada ancora pelo tempo da fala correspondente."""
    origem = (BASE.parent / PAGINA[numero]).as_uri()
    CAPTURA.mkdir(exist_ok=True)
    print("Capturando a tela:")

    with sync_playwright() as p:
        navegador = p.chromium.launch()
        contexto = navegador.new_context(
            viewport={"width": LARGURA, "height": ALTURA},
            record_video_dir=str(CAPTURA),
            record_video_size={"width": LARGURA, "height": ALTURA},
        )
        pagina = contexto.new_page()
        pagina.goto(origem)
        pagina.wait_for_timeout(2000)

        for i, bloco in enumerate(blocos, 1):
            destino = pagina.evaluate(
                """(alvo) => {
                    const norm = s => s.replace(/\\s+/g, ' ').trim();
                    const el = [...document.querySelectorAll('h1,h2,h3,h4,p,strong')]
                        .find(e => norm(e.textContent).includes(alvo));
                    if (!el) return null;
                    // Posicao calculada de uma vez: chamar scrollBy logo apos um
                    // scroll suave cancelaria a animacao e voltaria ao topo.
                    const y = el.getBoundingClientRect().top + window.scrollY - 60;
                    window.scrollTo({ top: y, behavior: 'smooth' });
                    return Math.round(y);
                }""",
                bloco["ancora"],
            )
            pagina.wait_for_timeout(1400)
            real = pagina.evaluate("Math.round(window.scrollY)")
            ok = destino is not None and abs(real - destino) < 90
            print(f"  {'ok' if ok else '!!'} {i:>2}. y={real:>6}  "
                  f"{bloco['janela']:5.1f}s  {bloco['ancora'][:40]}")
            if not ok:
                print(f"      ATENCAO: ancora nao encontrada ou scroll incorreto")
            pagina.wait_for_timeout(int(bloco["janela"] * 1000) - 1400)

        pagina.wait_for_timeout(1200)
        video = pagina.video
        contexto.close()          # o arquivo so e finalizado ao fechar o contexto
        bruto = Path(video.path())  # precisa ser lido antes de encerrar o Playwright
        navegador.close()

    destino = CAPTURA / f"video{numero}.webm"
    destino.unlink(missing_ok=True)
    bruto.rename(destino)
    print(f"\nCaptura: {duracao(destino):.1f}s\n")
    return destino


def montar_trilha(numero: int, blocos: list[dict], total: float) -> Path:
    """Posiciona cada fala no instante em que seu bloco aparece na tela."""
    entradas, filtros, rotulos = [], [], []
    for i, bloco in enumerate(blocos):
        entradas += ["-i", str(bloco["audio"])]
        ms = int(bloco["inicio"] * 1000)
        filtros.append(f"[{i}:a]adelay={ms}|{ms}[a{i}]")
        rotulos.append(f"[a{i}]")

    trilha = TRABALHO / f"trilha{numero}.wav"
    filtro = (";".join(filtros) + ";" + "".join(rotulos)
              + f"amix=inputs={len(blocos)}:dropout_transition=0:normalize=0[mix];"
              + f"[mix]apad,atrim=0:{total:.2f},"
              + "loudnorm=I=-16:TP=-1.5:LRA=11[out]")

    executar(["ffmpeg", "-y", *entradas, "-filter_complex", filtro,
              "-map", "[out]", "-ar", "48000", "-ac", "2", str(trilha)])
    return trilha


def main() -> None:
    p = argparse.ArgumentParser(description="Produz os vídeos da Fase 5")
    p.add_argument("numero", type=int, choices=[1, 2, 3])
    p.add_argument("--voz", default="Luciana")
    p.add_argument("--ppm", type=int, default=178)
    p.add_argument("--audio", type=Path, help="usa esta gravação em vez de sintetizar")
    args = p.parse_args()

    blocos = sintetizar(args.numero, args.voz, args.ppm)
    captura = capturar(args.numero, blocos)
    total = duracao(captura)

    trilha = args.audio if args.audio else montar_trilha(args.numero, blocos, total)
    if args.audio:
        print(f"Usando gravação: {args.audio.name}")

    saida = BASE.parent / f"FarmTech_Fase5_Entrega{args.numero}.mp4"
    print("Mixando...")
    executar([
        "ffmpeg", "-y", "-i", str(captura), "-i", str(trilha),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v:0", "-map", "1:a:0", str(saida),
    ])

    final = duracao(saida)
    print(f"\n{saida.name}")
    print(f"Duração: {int(final // 60)}min{int(final % 60):02d}s "
          f"({'dentro' if final <= LIMITE else 'ACIMA'} do limite de 5min)")


if __name__ == "__main__":
    main()
