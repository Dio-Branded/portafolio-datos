# Reporte mensual automatizado: contrataciones de servicios en el sector energia

Con un solo comando se genera el reporte del mes en dos formatos:

- `salida/Reporte_energia_AAAA-MM.xlsx`: hoja Resumen (indicadores, monto por mes y grafico), hoja Por entidad (tabla, grafico, por tipo de contratacion y las diez ordenes de mayor monto) y hoja Detalle (tabla con filtros, lista para revisar orden por orden).
- `salida/Reporte_energia_AAAA-MM.pdf`: dos paginas con el resumen, tres graficos (monto por entidad, serie mensual, distribucion de montos) y una nota metodologica.

## Como correrlo

```
python generar_reporte.py                 # ultimo mes con datos
python generar_reporte.py --mes 2026-06   # un mes especifico
python generar_reporte.py --mes 2026-05 --datos otra_tabla.csv
```

Si el mes no tiene datos, el script se detiene y lista los meses disponibles.

## Datos

`datos/os_sector_energia_2026.csv`: ordenes de servicio emitidas a personas naturales (RUC 10) por OEFA, MINEM, Osinergmin, OSIPTEL, OSITRAN, Perupetro y Electroperu entre marzo y agosto de 2026. Fuente: CONOSCE, datos abiertos del OSCE/OECE. No contiene el nombre ni el RUC del proveedor.

Para usar el script con otra tabla basta que tenga las columnas `entidad`, `descripcion`, `monto` y `fecha_emision` (la columna `tipocontratacion` es opcional).

## Que muestra el reporte

- Ordenes emitidas, monto total, ticket promedio, mediana y numero de entidades del mes, con la variacion frente al mes anterior.
- Monto por entidad y distribucion de montos por entidad.
- Serie mensual completa con el mes del reporte resaltado.
- Las diez ordenes de mayor monto, con su descripcion.

## Herramientas

Python 3.11: pandas (calculo), matplotlib (graficos), xlsxwriter (Excel con formato, tabla y graficos nativos), reportlab (PDF).
