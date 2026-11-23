"""Reporte mensual de contrataciones de servicios a personas naturales en el sector energia.

Con un comando genera, para el mes indicado:
  salida/Reporte_energia_AAAA-MM.xlsx  (hojas Resumen, Por entidad, Detalle; con graficos)
  salida/Reporte_energia_AAAA-MM.pdf   (resumen, tres graficos y nota metodologica)

Datos: datos/os_sector_energia_2026.csv (CONOSCE, datos abiertos OSCE/OECE; sin datos del proveedor).
El mismo script sirve con cualquier CSV que tenga las columnas entidad, descripcion, monto y fecha_emision.

Uso:
  python generar_reporte.py                 (ultimo mes con datos)
  python generar_reporte.py --mes 2026-06
  python generar_reporte.py --mes 2026-05 --datos otra_tabla.csv
"""
import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, "datos", "os_sector_energia_2026.csv")
SALIDA = os.path.join(AQUI, "salida")
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "setiembre", "octubre", "noviembre", "diciembre"]
# Nombres cortos para graficos y tablas
CORTO = {
    "ORGANISMO DE EVALUACION Y FISCALIZACION AMBIENTAL": "OEFA",
    "MINISTERIO DE ENERGIA Y MINAS": "MINEM",
    "ORGANISMO SUPERVISOR DE INVERSION PRIVADA EN TELECOMUNICACIONES": "OSIPTEL",
    "ORGANISMO SUPERVISOR DE LA INVERSION EN INFRAESTRUCTURA DE TRANSPORTE DE USO PUBLICO": "OSITRAN",
    "ORGANISMO SUPERVISOR DE LA INVERSION EN ENERGIA Y MINERIA": "Osinergmin",
    "PERUPETRO S.A.": "Perupetro",
    "EMPRESA DE ELECTRICIDAD DEL PERÚ S.A. - ELECTROPERU": "Electroperu",
}


def nombre_mes(m):
    a, n = m.split("-")
    return f"{MESES[int(n) - 1]} de {a}"


def soles(x):
    return f"S/ {x:,.0f}"


def cargar(ruta):
    d = pd.read_csv(ruta, encoding="utf-8-sig")
    faltan = {"entidad", "descripcion", "monto", "fecha_emision"} - set(d.columns)
    if faltan:
        sys.exit(f"Faltan columnas en {ruta}: {sorted(faltan)}")
    d["fecha_emision"] = pd.to_datetime(d["fecha_emision"])
    d["mes"] = d["fecha_emision"].dt.strftime("%Y-%m")
    d["entidad_corta"] = d["entidad"].map(lambda e: CORTO.get(e, e[:28]))
    d["monto"] = d["monto"].astype(float)
    return d


def calcular(d, mes):
    m = d[d["mes"] == mes]
    if m.empty:
        sys.exit(f"No hay ordenes en {mes}. Meses con datos: {', '.join(sorted(d['mes'].unique()))}")
    meses = sorted(d["mes"].unique())
    i = meses.index(mes)
    ant = d[d["mes"] == meses[i - 1]] if i > 0 else d.iloc[0:0]
    kpi = {
        "mes": mes,
        "n": len(m), "monto": m["monto"].sum(), "mediana": m["monto"].median(),
        "ticket": m["monto"].mean(), "entidades": m["entidad"].nunique(),
        "n_ant": len(ant), "monto_ant": ant["monto"].sum() if len(ant) else None,
        "mes_ant": meses[i - 1] if i > 0 else None,
    }
    por_entidad = (m.groupby("entidad_corta")["monto"].agg(n="count", monto="sum", mediana="median", maximo="max")
                   .sort_values("monto", ascending=False).reset_index())
    por_tipo = (m.groupby("tipocontratacion")["monto"].agg(n="count", monto="sum").sort_values("monto", ascending=False)
                .reset_index()) if "tipocontratacion" in m else None
    top = m.sort_values("monto", ascending=False).head(10)[["entidad_corta", "descripcion", "monto"]]
    serie = d.groupby("mes")["monto"].agg(n="count", monto="sum").reset_index()
    return kpi, por_entidad, por_tipo, top, serie, m


def graficos(kpi, por_entidad, serie, m, carpeta):
    mes = kpi["mes"]
    rutas = {}
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.barh(por_entidad["entidad_corta"][::-1], por_entidad["monto"][::-1] / 1000, color="#1f4e79")
    ax.set_xlabel("Monto contratado (miles de S/)")
    ax.set_title(f"Monto por entidad, {nombre_mes(mes)}")
    for y, v in enumerate(por_entidad["monto"][::-1] / 1000):
        ax.text(v, y, f" {v:,.0f}", va="center", fontsize=8)
    fig.tight_layout(); rutas["entidad"] = os.path.join(carpeta, f"g1_entidad_{mes}.png"); fig.savefig(rutas["entidad"], dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 3.2))
    col = ["#c00000" if x == mes else "#8eaadb" for x in serie["mes"]]
    ax.bar(serie["mes"], serie["monto"] / 1e6, color=col)
    ax.plot(serie["mes"], serie["monto"] / 1e6, color="#1f4e79", marker="o", linewidth=1)
    ax.set_ylabel("Millones de S/"); ax.set_title("Monto mensual (el mes del reporte en rojo)")
    fig.tight_layout(); rutas["serie"] = os.path.join(carpeta, f"g2_serie_{mes}.png"); fig.savefig(rutas["serie"], dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 3.4))
    orden = por_entidad["entidad_corta"].tolist()
    datos = [m.loc[m["entidad_corta"] == e, "monto"] / 1000 for e in orden]
    ax.boxplot(datos, tick_labels=orden, vert=True, showfliers=False)
    ax.set_ylabel("Monto por orden (miles de S/)"); ax.set_title("Distribucion de montos por entidad (sin valores extremos)")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    fig.tight_layout(); rutas["box"] = os.path.join(carpeta, f"g3_box_{mes}.png"); fig.savefig(rutas["box"], dpi=160); plt.close(fig)
    return rutas


def excel(kpi, por_entidad, por_tipo, top, serie, m, ruta):
    mes = kpi["mes"]
    with pd.ExcelWriter(ruta, engine="xlsxwriter") as w:
        wb = w.book
        titulo = wb.add_format({"bold": True, "font_size": 14})
        negrita = wb.add_format({"bold": True})
        dinero = wb.add_format({"num_format": "#,##0.00"})
        entero = wb.add_format({"num_format": "#,##0"})
        pct = wb.add_format({"num_format": "0.0%"})

        # Hoja Resumen
        r = wb.add_worksheet("Resumen"); w.sheets["Resumen"] = r
        r.set_column("A:A", 34); r.set_column("B:C", 18)
        r.write("A1", f"Contrataciones de servicios a personas naturales, sector energia: {nombre_mes(mes)}", titulo)
        r.write("A2", "Fuente: CONOSCE (datos abiertos OSCE/OECE). Ordenes de servicio a RUC 10. Sin datos del proveedor.")
        filas = [("Ordenes emitidas", kpi["n"], entero), ("Monto total (S/)", kpi["monto"], dinero),
                 ("Ticket promedio (S/)", kpi["ticket"], dinero), ("Mediana por orden (S/)", kpi["mediana"], dinero),
                 ("Entidades con ordenes", kpi["entidades"], entero)]
        if kpi["mes_ant"]:
            var = (kpi["monto"] - kpi["monto_ant"]) / kpi["monto_ant"] if kpi["monto_ant"] else 0
            filas += [(f"Monto del mes anterior ({kpi['mes_ant']})", kpi["monto_ant"], dinero), ("Variacion del monto vs. mes anterior", var, pct)]
        for i, (k, v, f) in enumerate(filas, start=4):
            r.write(i, 0, k, negrita); r.write(i, 1, v, f)
        fila = 4 + len(filas) + 2
        r.write(fila, 0, "Monto por mes (todos los meses con datos)", negrita)
        serie.to_excel(w, sheet_name="Resumen", startrow=fila + 1, index=False)
        r.set_column("B:C", 18, dinero)
        ch = wb.add_chart({"type": "column"})
        ch.add_series({"name": "Monto", "categories": ["Resumen", fila + 2, 0, fila + 1 + len(serie), 0],
                       "values": ["Resumen", fila + 2, 2, fila + 1 + len(serie), 2], "fill": {"color": "#1f4e79"}})
        ch.set_title({"name": "Monto mensual (S/)"}); ch.set_legend({"none": True}); ch.set_size({"width": 560, "height": 300})
        r.insert_chart("E4", ch)

        # Hoja Por entidad
        por_entidad.to_excel(w, sheet_name="Por entidad", index=False)
        e = w.sheets["Por entidad"]; e.set_column("A:A", 16); e.set_column("B:B", 8, entero); e.set_column("C:E", 16, dinero)
        ch2 = wb.add_chart({"type": "bar"})
        ch2.add_series({"name": "Monto", "categories": ["Por entidad", 1, 0, len(por_entidad), 0],
                        "values": ["Por entidad", 1, 2, len(por_entidad), 2], "fill": {"color": "#1f4e79"}})
        ch2.set_title({"name": f"Monto por entidad, {nombre_mes(mes)}"}); ch2.set_legend({"none": True}); ch2.set_size({"width": 560, "height": 320})
        e.insert_chart("G2", ch2)
        if por_tipo is not None:
            por_tipo.to_excel(w, sheet_name="Por entidad", startrow=len(por_entidad) + 3, index=False)
        top.to_excel(w, sheet_name="Por entidad", startrow=len(por_entidad) + (len(por_tipo) if por_tipo is not None else 0) + 7, index=False)

        # Hoja Detalle (tabla con filtros)
        cols = [c for c in ["fecha_emision", "entidad_corta", "orden", "descripcion", "tipocontratacion", "monto"] if c in m.columns]
        det = m[cols].sort_values("fecha_emision").copy()
        det["fecha_emision"] = det["fecha_emision"].dt.strftime("%Y-%m-%d")
        det.to_excel(w, sheet_name="Detalle", index=False)
        dsh = w.sheets["Detalle"]
        dsh.add_table(0, 0, len(det), len(cols) - 1, {"columns": [{"header": c} for c in cols], "style": "Table Style Medium 2"})
        dsh.set_column("A:A", 12); dsh.set_column("B:B", 14); dsh.set_column("C:C", 28); dsh.set_column("D:D", 70); dsh.set_column("E:E", 30); dsh.set_column("F:F", 14, dinero)
        dsh.freeze_panes(1, 0)


def pdf(kpi, por_entidad, top, rutas, ruta):
    mes = kpi["mes"]
    est = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=est["Title"], fontSize=15, spaceAfter=6, alignment=0)
    normal = ParagraphStyle("n", parent=est["Normal"], fontSize=9.5, leading=13)
    chico = ParagraphStyle("c", parent=normal, fontSize=8, textColor=colors.grey)
    doc = SimpleDocTemplate(ruta, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm)
    cuerpo = [Paragraph(f"Contrataciones de servicios a personas naturales en el sector energia", h1),
              Paragraph(f"Reporte de {nombre_mes(mes)}", est["Heading2"]),
              Paragraph("Fuente: CONOSCE, datos abiertos del OSCE/OECE. Ordenes de servicio emitidas a personas naturales (RUC 10) por OEFA, MINEM, Osinergmin, OSIPTEL, OSITRAN, Perupetro y Electroperu. No incluye datos del proveedor.", chico),
              Spacer(1, 8)]
    filas = [["Indicador", "Valor"], ["Ordenes emitidas", f"{kpi['n']:,}"], ["Monto total", soles(kpi["monto"])],
             ["Ticket promedio", soles(kpi["ticket"])], ["Mediana por orden", soles(kpi["mediana"])],
             ["Entidades con ordenes", str(kpi["entidades"])]]
    if kpi["mes_ant"]:
        var = (kpi["monto"] - kpi["monto_ant"]) / kpi["monto_ant"] * 100 if kpi["monto_ant"] else 0
        filas.append([f"Variacion vs. {nombre_mes(kpi['mes_ant'])}", f"{var:+.1f} % ({soles(kpi['monto_ant'])})"])
    t = Table(filas, colWidths=[8 * cm, 7 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                           ("FONTSIZE", (0, 0), (-1, -1), 9), ("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("ALIGN", (1, 1), (1, -1), "RIGHT")]))
    cuerpo += [t, Spacer(1, 10), Image(rutas["entidad"], width=16 * cm, height=7.8 * cm), Spacer(1, 6),
               Image(rutas["serie"], width=16 * cm, height=7.3 * cm), PageBreak(),
               Paragraph("Por entidad", est["Heading2"])]
    pe = [["Entidad", "Ordenes", "Monto", "Mediana", "Maximo"]] + [[r.entidad_corta, f"{r.n:,}", soles(r.monto), soles(r.mediana), soles(r.maximo)] for r in por_entidad.itertuples()]
    t2 = Table(pe, colWidths=[4 * cm, 2.2 * cm, 3.4 * cm, 3.2 * cm, 3.2 * cm])
    t2.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("FONTSIZE", (0, 0), (-1, -1), 8.5), ("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("ALIGN", (1, 1), (-1, -1), "RIGHT")]))
    cuerpo += [t2, Spacer(1, 10), Image(rutas["box"], width=16 * cm, height=7.8 * cm), Spacer(1, 8),
               Paragraph("Diez ordenes de mayor monto", est["Heading2"])]
    tt = [["Entidad", "Descripcion", "Monto"]] + [[r.entidad_corta, Paragraph(str(r.descripcion)[:160], chico), soles(r.monto)] for r in top.itertuples()]
    t3 = Table(tt, colWidths=[2.6 * cm, 10.6 * cm, 2.8 * cm])
    t3.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    cuerpo += [t3, Spacer(1, 10), Paragraph("Nota metodologica", est["Heading3"]),
               Paragraph("El monto es el valor de la orden de servicio en soles al momento de su emision; no refleja pagos efectivos. "
                         "La mediana describe mejor que el promedio el monto tipico de una orden. El boxplot omite valores extremos para "
                         "facilitar la lectura. Reporte generado automaticamente con Python (pandas, matplotlib, reportlab).", normal)]
    doc.build(cuerpo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mes", help="AAAA-MM; por defecto el ultimo mes con datos")
    ap.add_argument("--datos", default=DATOS)
    args = ap.parse_args()
    d = cargar(args.datos)
    mes = args.mes or d["mes"].max()
    os.makedirs(SALIDA, exist_ok=True)
    kpi, por_entidad, por_tipo, top, serie, m = calcular(d, mes)
    rutas = graficos(kpi, por_entidad, serie, m, SALIDA)
    xlsx = os.path.join(SALIDA, f"Reporte_energia_{mes}.xlsx")
    pdfp = os.path.join(SALIDA, f"Reporte_energia_{mes}.pdf")
    excel(kpi, por_entidad, por_tipo, top, serie, m, xlsx)
    pdf(kpi, por_entidad, top, rutas, pdfp)
    print(f"{nombre_mes(mes)}: {kpi['n']:,} ordenes, {soles(kpi['monto'])}, mediana {soles(kpi['mediana'])}, {kpi['entidades']} entidades")
    print("Excel:", xlsx); print("PDF:  ", pdfp)


if __name__ == "__main__":
    main()
