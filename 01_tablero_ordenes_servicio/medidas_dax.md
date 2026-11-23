# Medidas DAX del tablero

Crea una tabla vacia llamada `Medidas` (Inicio > Especificar datos > nombre "Medidas", sin columnas) y agrega estas ocho medidas una por una (clic derecho en la tabla > Nueva medida). Al costado va el valor que debe salir en una tarjeta sin filtros; sale de `scripts/verificar_medidas.py`.

| N | Medida | DAX | Valor esperado sin filtros |
|---|---|---|---|
| 1 | Monto total | `Monto total = SUM ( ordenes[monto] )` | S/ 328 482 581,67 |
| 2 | N ordenes | `N ordenes = COUNTROWS ( ordenes )` | 48 949 |
| 3 | Ticket promedio | `Ticket promedio = DIVIDE ( [Monto total], [N ordenes] )` | S/ 6 710,71 |
| 4 | Mediana monto | `Mediana monto = MEDIAN ( ordenes[monto] )` | S/ 4 000,00 |
| 5 | % ordenes Lima | `% ordenes Lima = DIVIDE ( CALCULATE ( [N ordenes], ordenes[lima] = 1 ), [N ordenes] )` | 54,34 % |
| 6 | N entidades | `N entidades = DISTINCTCOUNT ( ordenes[ruc_entidad] )` | 1 510 |
| 7 | Monto mes anterior | `Monto mes anterior = CALCULATE ( [Monto total], DATEADD ( calendario[fecha], -1, MONTH ) )` | en una tabla por mes: junio muestra el monto de mayo, S/ 54 809 723,35 |
| 8 | Variacion mensual % | `Variacion mensual % = DIVIDE ( [Monto total] - [Monto mes anterior], [Monto mes anterior] )` | junio: -15,60 % |

Formato: medidas 1, 3, 4 y 7 en moneda con 2 decimales; 2 y 6 en numero entero con separador de miles; 5 y 8 en porcentaje con 2 decimales.

Las medidas 7 y 8 solo funcionan si `calendario` esta marcada como tabla de fechas y la relacion `calendario[fecha]` a `ordenes[fecha]` esta activa. Si la variacion sale en blanco, revisa eso primero.

## Valores de control por mes (tabla con calendario[anio_mes] en filas)

| Mes | Monto total | N ordenes | Variacion mensual % |
|---|---|---|---|
| 2026-01 | 6 384 164,94 | 1 328 | (en blanco) |
| 2026-02 | 16 074 464,77 | 3 213 | 151,79 % |
| 2026-03 | 52 625 889,71 | 8 033 | 227,39 % |
| 2026-04 | 54 895 824,25 | 7 966 | 4,31 % |
| 2026-05 | 54 809 723,35 | 7 715 | -0,16 % |
| 2026-06 | 46 258 939,86 | 6 891 | -15,60 % |
| 2026-07 | 64 079 438,58 | 8 307 | 38,52 % |
| 2026-08 | 32 123 101,81 | 5 298 | -49,87 % |
| 2026-09 | 1 231 034,40 | 198 | -96,17 % (setiembre esta incompleto en la fuente) |

## Mediana por categoria (matriz de la pagina 3)

| Categoria | N ordenes | Mediana |
|---|---|---|
| Hidrocarburos, energia y fiscalizacion | 17 637 | 3 500 |
| Seguimiento de expedientes y gestion documental | 12 121 | 3 400 |
| Bases de datos y sistematizacion | 10 667 | 4 200 |
| Analisis de datos y estadistica | 4 591 | 4 500 |
| Reportes e informes | 2 686 | 7 500 |
| Automatizacion y sistemas | 1 159 | 10 500 |
| Tableros y Power BI | 88 | 13 432,40 |

Una orden puede tener varias etiquetas en la fuente; aqui se le asigna una sola categoria por prioridad (tableros > automatizacion > analisis > reportes > bases de datos > expedientes > hidrocarburos). Por eso la de hidrocarburos, que es la mas amplia, va al final. Esta regla esta en `scripts/preparar_datos.py`.
