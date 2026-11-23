"""Prepara los datos del tablero "Ordenes de servicio del Estado a personas naturales, 2026".

Entrada: el CSV ya filtrado de CONOSCE (datos abiertos OSCE/OECE) con ordenes de servicio
emitidas a personas naturales (RUC 10) entre enero y setiembre de 2026.
Salida: tres CSV listos para Power BI en ../datos/ y una copia anonimizada del subconjunto
del sector energia para la pieza 2.

Privacidad: se eliminan las columnas proveedor y ruc_prov (personas naturales). Solo quedan
datos de la entidad contratante, la orden y el monto, que son informacion publica.

Uso: python preparar_datos.py [ruta_del_csv_fuente]
"""
import os
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, "..", "datos")
DATOS_ENERGIA = os.path.join(AQUI, "..", "..", "02_reporte_mensual_energia", "datos")
FUENTE = sys.argv[1] if len(sys.argv) > 1 else (
    r"C:\Codigos\career-ops\output\_KIT_ORDENES_SERVICIO\tarifas_datos\os_ruc10_relevantes_2026.csv")
FUENTE_ENERGIA = os.path.join(os.path.dirname(FUENTE), "os_ruc10_sector_energia_reguladores_2026.csv")

# Columnas que nunca deben salir de aqui (datos de personas naturales)
PRIVADAS = ["proveedor", "ruc_prov"]

# Prioridad para asignar UNA categoria por orden (las banderas son multietiqueta).
# La de hidrocarburos va al final porque es la mas amplia y absorberia a las demas.
PRIORIDAD_CATEGORIA = [
    ("power_bi_dashboard", "Tableros y Power BI"),
    ("automatizacion_sistemas", "Automatizacion y sistemas"),
    ("analisis_datos_estadistica", "Analisis de datos y estadistica"),
    ("reportes_informes", "Reportes e informes"),
    ("base_datos_sistematizacion", "Bases de datos y sistematizacion"),
    ("seguimiento_expedientes_gestdoc", "Seguimiento de expedientes y gestion documental"),
    ("hidrocarburos_energia_fiscalizacion", "Hidrocarburos, energia y fiscalizacion"),
]
BULLET_CV = {
    "Tableros y Power BI": "Tableros y reportes de gestion en Power BI y Excel",
    "Automatizacion y sistemas": "Automatizacion de reportes y tareas repetitivas",
    "Analisis de datos y estadistica": "Procesamiento de informacion",
    "Reportes e informes": "Tableros y reportes de gestion",
    "Bases de datos y sistematizacion": "Sistematizacion y depuracion de bases de datos",
    "Seguimiento de expedientes y gestion documental": "Seguimiento y control de expedientes",
    "Hidrocarburos, energia y fiscalizacion": "Apoyo tecnico en hidrocarburos, energia y fiscalizacion",
}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "setiembre", "octubre", "noviembre", "diciembre"]


def tipo_entidad(nombre):
    n = str(nombre).upper()
    if "MINISTERIO" in n:
        return "Ministerio"
    if "MUNICIPALIDAD" in n:
        return "Municipalidad"
    if "GOBIERNO REGIONAL" in n or "GOBIERNO REG." in n:
        return "Gobierno regional"
    if "UNIVERSIDAD" in n:
        return "Universidad"
    if any(k in n for k in ("HOSPITAL", "RED DE SALUD", "INSTITUTO", "DIRECCION REGIONAL DE SALUD", "ESSALUD")):
        return "Salud e institutos"
    return "Otros organismos"


def rango_monto(m):
    if m <= 2000:
        return "1. Hasta 2 000"
    if m <= 5000:
        return "2. De 2 001 a 5 000"
    if m <= 10000:
        return "3. De 5 001 a 10 000"
    if m <= 20000:
        return "4. De 10 001 a 20 000"
    return "5. Mas de 20 000"


def categoria(fila):
    for col, nombre in PRIORIDAD_CATEGORIA:
        if fila[col]:
            return nombre
    return "Sin clasificar"


def perfil(fila):
    if fila["especialista"]:
        return "Especialista"
    if fila["ingeniero"]:
        return "Ingeniero"
    if fila["apoyo"]:
        return "Apoyo"
    return "Sin dato"


def main():
    os.makedirs(DATOS, exist_ok=True)
    os.makedirs(DATOS_ENERGIA, exist_ok=True)

    d = pd.read_csv(FUENTE, encoding="utf-8-sig", low_memory=False)
    print(f"Fuente: {len(d):,} filas, {d.shape[1]} columnas")

    banderas = [c for c, _ in PRIORIDAD_CATEGORIA]
    for c in banderas + ["apoyo", "especialista", "ingeniero", "lima"]:
        d[c] = d[c].astype(str).str.lower().isin(["true", "1"])

    d["fecha"] = pd.to_datetime(d["fecha"], errors="coerce")
    d = d.dropna(subset=["fecha", "monto"]).copy()
    d["monto"] = d["monto"].astype(float)

    salida = pd.DataFrame({
        "id_orden": range(1, len(d) + 1),
        "entidad": d["entidad"].str.strip(),
        "ruc_entidad": d["ruc_entidad"].astype("int64"),
        "depto": d["depto"].str.strip().str.upper(),
        "tipo_entidad": d["entidad"].map(tipo_entidad),
        "orden": d["orden"].str.strip(),
        "descripcion": d["descripcion"].str.strip(),
        "estado": d["estado"].str.strip(),
        "tipocontratacion": d["tipocontratacion"].str.strip(),
        "monto": d["monto"].round(2),
        "rango_monto": d["monto"].map(rango_monto),
        "fecha": d["fecha"].dt.strftime("%Y-%m-%d"),
        "mes": d["fecha"].dt.strftime("%Y-%m"),
        "categoria": d.apply(categoria, axis=1),
        "perfil": d.apply(perfil, axis=1),
        "lima": d["lima"].astype(int),
        "dur_dias": d["dur_dias"],
    })
    for c in banderas:
        salida[c] = d[c].astype(int).values

    for c in PRIVADAS:
        assert c not in salida.columns, f"columna privada {c} en la salida"
    salida.to_csv(os.path.join(DATOS, "ordenes_2026.csv"), index=False, encoding="utf-8-sig")
    print(f"ordenes_2026.csv: {len(salida):,} filas")

    # Calendario del anio completo (tabla de fechas para Power BI)
    cal = pd.DataFrame({"fecha": pd.date_range("2026-01-01", "2026-12-31", freq="D")})
    cal["anio"] = cal["fecha"].dt.year
    cal["mes_num"] = cal["fecha"].dt.month
    cal["mes_nombre"] = cal["mes_num"].map(lambda m: MESES[m - 1])
    cal["trimestre"] = "T" + cal["fecha"].dt.quarter.astype(str)
    cal["anio_mes"] = cal["fecha"].dt.strftime("%Y-%m")
    cal["fecha"] = cal["fecha"].dt.strftime("%Y-%m-%d")
    cal.to_csv(os.path.join(DATOS, "calendario.csv"), index=False, encoding="utf-8-sig")

    dim = pd.DataFrame([(n, BULLET_CV[n]) for _, n in PRIORIDAD_CATEGORIA] + [("Sin clasificar", "")],
                       columns=["categoria", "servicio_relacionado"])
    dim.to_csv(os.path.join(DATOS, "dim_categoria.csv"), index=False, encoding="utf-8-sig")

    # Subconjunto del sector energia para la pieza 2 (ya viene sin proveedor; se vuelve a comprobar)
    e = pd.read_csv(FUENTE_ENERGIA, encoding="utf-8-sig")
    e = e.drop(columns=[c for c in PRIVADAS if c in e.columns])
    e["entidad"] = e["entidad"].str.strip()
    e["fecha_emision"] = pd.to_datetime(e["fecha_emision"]).dt.strftime("%Y-%m-%d")
    e["mes"] = e["fecha_emision"].str[:7]
    e.to_csv(os.path.join(DATOS_ENERGIA, "os_sector_energia_2026.csv"), index=False, encoding="utf-8-sig")
    print(f"os_sector_energia_2026.csv: {len(e):,} filas, meses {e['mes'].min()} a {e['mes'].max()}")

    print("\nControl rapido:")
    print(" categoria:", salida["categoria"].value_counts().to_dict())
    print(" tipo_entidad:", salida["tipo_entidad"].value_counts().to_dict())
    print(" perfil:", salida["perfil"].value_counts().to_dict())


if __name__ == "__main__":
    main()
