"""Renderiza o README em HTML, so para servir de tela na gravacao do video 2."""
from pathlib import Path

import markdown

BASE = Path(__file__).resolve().parent.parent

ESTILO = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  font: 16px/1.65 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #1f2328; background: #fff;
  max-width: 980px; margin: 0 auto; padding: 42px 56px 200px;
}
h1 { font-size: 2em; border-bottom: 1px solid #d8dee4; padding-bottom: .3em; margin-top: 1.4em; }
h2 { font-size: 1.5em; border-bottom: 1px solid #d8dee4; padding-bottom: .3em; margin-top: 1.8em; }
h3 { font-size: 1.22em; margin-top: 1.5em; }
h1:first-child { margin-top: 0; }
table { border-collapse: collapse; margin: 1.1em 0; width: 100%; font-size: .94em; }
th, td { border: 1px solid #d0d7de; padding: 7px 13px; text-align: left; }
th { background: #f6f8fa; font-weight: 600; }
tr:nth-child(2n) td { background: #f6f8fa; }
code { background: #eff1f3; padding: .2em .4em; border-radius: 6px; font-size: .88em; }
pre { background: #f6f8fa; padding: 16px; border-radius: 8px; overflow-x: auto; }
pre code { background: none; padding: 0; }
img { max-width: 100%; border: 1px solid #d0d7de; border-radius: 8px; margin: .6em 0; }
blockquote { border-left: 4px solid #d0d7de; margin: 1em 0; padding: .2em 1em; color: #59636e; }
hr { border: 0; border-top: 1px solid #d8dee4; margin: 2.4em 0; }
a { color: #0969da; text-decoration: none; }
"""


def montar() -> Path:
    texto = (BASE / "README.md").read_text(encoding="utf-8")
    corpo = markdown.markdown(texto, extensions=["tables", "fenced_code", "toc"])
    html = (f"<!doctype html><meta charset='utf-8'>"
            f"<title>FarmTech Solutions — Fase 5</title>"
            f"<style>{ESTILO}</style>{corpo}")
    destino = BASE / "readme.html"
    destino.write_text(html, encoding="utf-8")
    return destino


if __name__ == "__main__":
    d = montar()
    print(f"{d.name}: {d.stat().st_size / 1024:.0f} KB")
