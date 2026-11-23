"""Genera un registro SINTETICO de expedientes para el libro "Control de expedientes".

Todo es inventado: numeros de expediente, areas, responsables y fechas. Semilla fija (2026)
para que el archivo sea reproducible. Cualquier cifra absoluta que salga de aqui debe citarse
como "sobre data sintetica, seed 2026".

Uso: python generar_expedientes.py [--n 300] [--corte 2026-10-20]
"""
import argparse
import os

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "datos", "expedientes_sinteticos.csv")

TIPOS = {"Solicitud": 10, "Reclamo": 15, "Consulta": 7, "Recurso": 30, "Informe": 15}
AREAS = ["Logistica", "Administracion", "Asesoria Legal", "Planeamiento", "Mesa de Partes"]
ESTADOS = ["Atendido", "En proceso", "Observado", "Derivado"]
# Nombres ficticios (no corresponden a personas reales)
RESPONSABLES = ["A. Quispe", "B. Rojas", "C. Huaman", "D. Torres", "E. Flores", "F. Castro", "G. Mendoza", "H. Paredes"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--corte", default="2026-10-20", help="fecha de corte para los conteos de control")
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    n = args.n
    tipos = rng.choice(list(TIPOS), size=n, p=[0.35, 0.2, 0.2, 0.1, 0.15])
    plazo = np.array([TIPOS[t] for t in tipos])
    estado = rng.choice(ESTADOS, size=n, p=[0.55, 0.25, 0.12, 0.08])
    # Los atendidos se reparten en todo el periodo; los pendientes se concentran en las ultimas
    # semanas antes del corte, como en una mesa de partes real (asi hay verdes, ambar y rojos).
    corte = pd.Timestamp(args.corte)
    dias_atras = np.where(estado == "Atendido", rng.integers(20, 234, size=n), rng.integers(0, 40, size=n))
    ingreso = corte - pd.to_timedelta(dias_atras, unit="D")
    ingreso = pd.DatetimeIndex(np.busday_offset(ingreso.values.astype("datetime64[D]"), 0, roll="forward"))
    venc = pd.DatetimeIndex(np.busday_offset(ingreso.values.astype("datetime64[D]"), plazo, roll="forward"))
    # Fecha de atencion solo para los atendidos: casi siempre dentro del plazo, a veces tarde
    retraso = rng.integers(-plazo + 1, 1, size=n)
    tarde = rng.random(n) < 0.18
    retraso = np.where(tarde, rng.integers(1, 15, size=n), retraso)
    atencion = pd.DatetimeIndex(np.busday_offset(venc.values.astype("datetime64[D]"), retraso, roll="forward"))
    atencion = pd.Series(atencion).where(estado == "Atendido")

    d = pd.DataFrame({
        "numero": [f"EXP-2026-{i:04d}" for i in range(1, n + 1)],
        "tipo": tipos,
        "area": rng.choice(AREAS, size=n),
        "fecha_ingreso": ingreso.strftime("%Y-%m-%d"),
        "plazo_dias": plazo,
        "fecha_vencimiento": venc.strftime("%Y-%m-%d"),
        "estado": estado,
        "responsable": rng.choice(RESPONSABLES, size=n),
        "fecha_atencion": atencion.dt.strftime("%Y-%m-%d"),
        "asunto": [f"Expediente de prueba {i} (dato sintetico)" for i in range(1, n + 1)],
    }).sort_values("fecha_ingreso").reset_index(drop=True)

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    d.to_csv(SALIDA, index=False, encoding="utf-8-sig")
    print(f"{SALIDA}: {len(d)} expedientes, seed {args.seed}")

    # Conteos de control para el checkpoint de la guia (mismas reglas que el semaforo en Power Query)
    v = pd.to_datetime(d["fecha_vencimiento"])
    dias = (v - corte).dt.days
    sem = np.select(
        [d["estado"] == "Atendido", dias < 0, dias <= 5],
        ["Gris (atendido)", "Rojo (vencido)", "Ambar (0 a 5 dias)"], "Verde (mas de 5 dias)")
    d["semaforo"] = sem
    print(f"\nFecha de corte {args.corte}. Conteos esperados en Excel:")
    print(d["semaforo"].value_counts().to_string())
    print("\nPor area y semaforo:")
    print(pd.crosstab(d["area"], d["semaforo"], margins=True).to_string())
    print("\nAtendidos fuera de plazo:", int(((pd.to_datetime(d["fecha_atencion"]) > v) & (d["estado"] == "Atendido")).sum()))


if __name__ == "__main__":
    main()
