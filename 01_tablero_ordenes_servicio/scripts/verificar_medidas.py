"""Calcula con pandas los mismos valores que las 8 medidas DAX del tablero.

Sirve como checkpoint: cada tarjeta o matriz de Power BI debe mostrar exactamente estos numeros.
Uso: python verificar_medidas.py [--mes 2026-06]
"""
import argparse
import os

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RUTA = os.path.join(AQUI, "..", "datos", "ordenes_2026.csv")


def resumen(d, titulo):
    n = len(d)
    monto = d["monto"].sum()
    print(f"\n== {titulo} ==")
    print(f"Monto total      : S/ {monto:,.2f}")
    print(f"N ordenes        : {n:,}")
    print(f"Ticket promedio  : S/ {monto / n:,.2f}" if n else "Ticket promedio  : sin datos")
    print(f"Mediana monto    : S/ {d['monto'].median():,.2f}" if n else "")
    print(f"% ordenes Lima   : {d['lima'].mean():.2%}" if n else "")
    print(f"N entidades      : {d['ruc_entidad'].nunique():,}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mes", help="AAAA-MM para ver el detalle de un mes")
    args = ap.parse_args()

    d = pd.read_csv(RUTA, encoding="utf-8-sig")
    resumen(d, "Total enero a setiembre 2026 (sin filtros)")

    print("\n== Monto por mes y variacion mensual ==")
    por_mes = d.groupby("mes")["monto"].agg(["sum", "count"]).rename(columns={"sum": "monto", "count": "n"})
    por_mes["mes_anterior"] = por_mes["monto"].shift(1)
    por_mes["variacion_%"] = (por_mes["monto"] - por_mes["mes_anterior"]) / por_mes["mes_anterior"] * 100
    with pd.option_context("display.float_format", "{:,.2f}".format):
        print(por_mes.to_string())

    print("\n== Mediana por categoria (matriz de la pagina 3) ==")
    cat = d.groupby("categoria")["monto"].agg(["count", "median", "sum"]).sort_values("count", ascending=False)
    with pd.option_context("display.float_format", "{:,.2f}".format):
        print(cat.to_string())

    print("\n== Top 15 entidades por monto (pagina 2) ==")
    top = d.groupby("entidad")["monto"].agg(["sum", "count", "median"]).sort_values("sum", ascending=False).head(15)
    with pd.option_context("display.float_format", "{:,.2f}".format):
        print(top.to_string())

    if args.mes:
        resumen(d[d["mes"] == args.mes], f"Mes {args.mes} (segmentador de mes)")


if __name__ == "__main__":
    main()
