# Portafolio de datos

Marcelo Garcia Luyo. Ingeniero Petroquimico (UNI), CIP N.° 407508. Lima, Peru.

Trabajos cortos que muestran lo que ofrezco a entidades publicas y empresas: tableros de gestion, automatizacion de reportes, control de expedientes y captura y analisis de datos. Usan datos publicos, datos inventados o datos propios. Ninguno contiene informacion de clientes.

| Pieza | Que es | Herramientas | Carpeta |
|---|---|---|---|
| 1 | Tablero de ordenes de servicio del Estado a personas naturales, enero a setiembre 2026 | Power BI, Power Query, DAX, Python | [01_tablero_ordenes_servicio](01_tablero_ordenes_servicio/) |
| 2 | Reporte mensual automatizado de contrataciones de servicios en el sector energia (Excel y PDF generados con un comando) | Python: pandas, matplotlib, xlsxwriter, reportlab | [02_reporte_mensual_energia](02_reporte_mensual_energia/) |
| 3 | Libro de control de expedientes con plazos, semaforos y resumen por area | Excel, Power Query, tablas dinamicas | [03_control_expedientes_excel](03_control_expedientes_excel/) |
| 4 | Analisis de mis partidas de un juego de cartas en linea: captura automatica, formato limpio, traduccion a texto y estadisticas que se actualizan solas | Python: json, matplotlib | [04_analisis_partidas_md](04_analisis_partidas_md/) |

Las fichas de una pagina de cada pieza (PDF para adjuntar a cotizaciones) se comparten a pedido.

## 1. Tablero de ordenes de servicio del Estado (Power BI)

Que responde: cuanto contratan las entidades a personas naturales por orden de servicio, en que tipo de servicio, en que meses y a que montos. Tres paginas: resumen, por entidad y por categoria de servicio.

Datos: CONOSCE, datos abiertos del OSCE/OECE. Ordenes de servicio emitidas a personas naturales (RUC 10) de enero a setiembre de 2026, filtradas a servicios de datos, reportes, sistematizacion, gestion documental y energia (48 949 ordenes, 1 510 entidades). Setiembre esta incompleto en la fuente. Las columnas del proveedor (nombre y RUC) se eliminaron: solo quedan la entidad, la orden, la descripcion y el monto, que son informacion publica.

Como se construyo: `scripts/preparar_datos.py` limpia la fuente y deja tres tablas (`ordenes_2026.csv`, `calendario.csv`, `dim_categoria.csv`). El modelo en Power BI es una estrella con tabla de fechas y ocho medidas DAX (`medidas_dax.md`). `scripts/verificar_medidas.py` reproduce las medidas en pandas para comprobar el tablero.

Capturas: pendientes (el tablero esta en construccion).

## 2. Reporte mensual automatizado del sector energia (Python)

Que hace: con un comando genera el reporte del mes en Excel (resumen, por entidad, detalle con filtros y graficos) y en PDF (resumen, tres graficos y nota metodologica).

```
cd 02_reporte_mensual_energia
python generar_reporte.py --mes 2026-06
```

Datos: ordenes de servicio a personas naturales de OEFA, MINEM, Osinergmin, OSIPTEL, OSITRAN, Perupetro y Electroperu, marzo a agosto de 2026 (CONOSCE, 3 379 ordenes, sin datos del proveedor). El mismo script sirve con cualquier tabla que tenga entidad, descripcion, monto y fecha.

## 3. Control de expedientes (Excel con Power Query)

Que hace: carga un registro de expedientes, calcula los dias que faltan para el vencimiento segun una fecha de corte, pinta un semaforo (verde, ambar, rojo, gris para atendidos) y resume por area y responsable en una tabla dinamica con segmentadores.

Datos: 300 expedientes inventados con `generar_expedientes.py` (semilla 2026). Los nombres de responsables son ficticios. Cualquier cifra de esta pieza es sobre data sintetica, seed 2026.

## Reproducir

Requisitos: Python 3.11 con pandas, numpy, matplotlib, xlsxwriter, reportlab y python-docx; Power BI Desktop; Excel 2016 o superior.

1. `python 01_tablero_ordenes_servicio/scripts/preparar_datos.py <ruta del CSV de CONOSCE>`
2. Abrir `01_tablero_ordenes_servicio/tablero_ordenes_2026.pbix` o seguir `GUIA_TABLERO_1.md` para construirlo.
3. `python 02_reporte_mensual_energia/generar_reporte.py --mes 2026-06`
4. `python 03_control_expedientes_excel/generar_expedientes.py` y seguir `GUIA_EXCEL_3.md`.

## Licencia

MIT. Los datos de CONOSCE son datos abiertos del Estado peruano.

## 4. Analisis de mis partidas de un juego de cartas en linea (Python)

Que hace: guarda cada partida de Yu-Gi-Oh! Master Duel al terminar, la deja en un JSON limpio, la traduce a texto turno por turno y actualiza un reporte con resultados yendo primero y segundo, cartas jugadas, cartas de interrupcion y la linea de cada primer turno. Detalle, diccionario de datos y reglas de calidad en [04_analisis_partidas_md/README.md](04_analisis_partidas_md/README.md). El componente de captura es privado y no se publica.
