"""Genera capturas/04_partidas.png para la ficha: a la izquierda un tramo del registro ya traducido a texto (una partida real),
a la derecha los resultados yendo primero y yendo segundo calculados por analisis.py.

Uso:  python figura.py
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import analisis  # noqa: E402
from leer_registro import traducir  # noqa: E402

SUPERFICIE, TEXTO, TEXTO2, GRILLA = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
GANADAS, PERDIDAS = "#2a78d6", "#eb6834"   # paleta categorica validada (azul, naranja)
PARTIDA_MUESTRA = "2026-11-23_15-54-44.json"
LINEAS = (79, 91)   # tramo del registro: Kuriboh - Multiply! y la fusion de Artmage en el turno del rival


def main():
    datos = AQUI.parent / "datos"
    partidas = [a for a in (analisis.analizar(f) for f in sorted(datos.glob("*.json"))) if a and a["resultado"] in ("gana", "pierde")]
    grupos = [("Yendo primero", [p for p in partidas if p["primero"]]), ("Yendo segundo", [p for p in partidas if p["primero"] is False])]

    r = json.load(open(datos / PARTIDA_MUESTRA, encoding="utf-8"))
    tramo = traducir(r).split("\n")[LINEAS[0] - 1:LINEAS[1]]

    fig = plt.figure(figsize=(6.5, 3.1), dpi=220, facecolor=SUPERFICIE)
    # izquierda: registro traducido
    ax1 = fig.add_axes([0.01, 0.02, 0.56, 0.96]); ax1.axis("off")
    ax1.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax1.transAxes, facecolor="#f3f2ee", edgecolor=GRILLA, linewidth=0.8))
    ax1.text(0.03, 0.95, "Registro traducido (partida real, turno 1)", transform=ax1.transAxes, fontsize=7.5, fontweight="bold",
             color=TEXTO, va="top", family="DejaVu Sans")
    for k, linea in enumerate(tramo):
        ax1.text(0.03, 0.85 - k * 0.064, linea.strip(), transform=ax1.transAxes, fontsize=4.9, color=TEXTO2 if linea.strip().startswith(("ACTIVA", "resuelve", "(")) else TEXTO,
                 va="top", family="DejaVu Sans Mono")
    # derecha: resultados por turno de salida
    ax2 = fig.add_axes([0.66, 0.2, 0.31, 0.58], facecolor=SUPERFICIE)
    for y, (etq, ps) in enumerate(reversed(grupos)):
        g = sum(p["resultado"] == "gana" for p in ps); pe = sum(p["resultado"] == "pierde" for p in ps)
        ax2.barh(y, g, height=0.42, color=GANADAS, edgecolor=SUPERFICIE, linewidth=1.2)
        ax2.barh(y, pe, left=g, height=0.42, color=PERDIDAS, edgecolor=SUPERFICIE, linewidth=1.2)
        ax2.text(g + pe + 0.15, y, "%d-%d" % (g, pe), va="center", fontsize=7, color=TEXTO, family="DejaVu Sans")
    ax2.set_yticks(range(len(grupos))); ax2.set_yticklabels([e for e, _ in reversed(grupos)], fontsize=7, color=TEXTO, family="DejaVu Sans")
    ax2.set_xlim(0, max(len(ps) for _, ps in grupos) + 1.2)
    ax2.tick_params(axis="x", labelsize=6, colors=TEXTO2, length=0); ax2.tick_params(axis="y", length=0)
    ax2.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax2.grid(axis="x", color=GRILLA, linewidth=0.6); ax2.set_axisbelow(True)
    for s in ax2.spines.values(): s.set_visible(False)
    ax2.set_xlabel("partidas", fontsize=6, color=TEXTO2, family="DejaVu Sans")
    fig.text(0.66, 0.93, "Resultados por turno de salida", fontsize=7.5, fontweight="bold", color=TEXTO, family="DejaVu Sans")
    fig.text(0.66, 0.86, "%d partidas propias, 23-nov-2026" % len(partidas), fontsize=6, color=TEXTO2, family="DejaVu Sans")
    # leyenda con marcas (la identidad no depende solo del color: tambien el orden y el texto "G-P")
    fig.patches.extend([plt.Rectangle((0.66, 0.065), 0.014, 0.03, transform=fig.transFigure, facecolor=GANADAS),
                        plt.Rectangle((0.80, 0.065), 0.014, 0.03, transform=fig.transFigure, facecolor=PERDIDAS)])
    fig.text(0.678, 0.068, "ganadas", fontsize=6, color=TEXTO, family="DejaVu Sans")
    fig.text(0.818, 0.068, "perdidas", fontsize=6, color=TEXTO, family="DejaVu Sans")
    salida = AQUI.parent / "capturas" / "04_partidas.png"
    fig.savefig(salida, facecolor=SUPERFICIE)
    print("figura:", salida)


if __name__ == "__main__":
    main()
