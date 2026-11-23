# Guia paso a paso: libro "Control de expedientes" (Excel 2021 con Power Query)

Tu construyes el libro. Cada paso tiene una accion y un checkpoint. Tiempo estimado: 2,5 horas. Antes de empezar corre `python generar_expedientes.py` y deja abierta la ventana con los conteos esperados (fecha de corte 2026-10-20).

Reglas del semaforo (misma logica en Power Query y en el generador):
- Gris (atendido): estado = Atendido.
- Rojo (vencido): fecha de vencimiento anterior a la fecha de corte.
- Ambar (0 a 5 dias): faltan entre 0 y 5 dias.
- Verde (mas de 5 dias): faltan mas de 5 dias.

Conteos esperados con corte 2026-10-20: Gris 165, Rojo 72, Verde 45, Ambar 18 (total 300). Atendidos fuera de plazo: 28.

## Paso 1. Libro y hoja de parametros (10 min)

Accion: libro nuevo, guardar como `control_expedientes.xlsx` en esta carpeta. Renombra la hoja a `Parametros`. En A1 escribe "Fecha de corte", en B1 escribe 20/10/2026 (formato Fecha). Selecciona A1:B1 > Insertar > Tabla (con encabezados) y en Diseno de tabla ponle el nombre `tParametros`.
Checkpoint: la celda B1 esta dentro de una tabla llamada tParametros.

## Paso 2. Cargar el parametro a Power Query (10 min)

Accion: con el cursor dentro de tParametros, Datos > Desde una tabla o rango. En Power Query: clic derecho en la celda del valor (la fecha) > Obtener detalles. Renombra la consulta a `FechaCorte`. Cambia el tipo a Fecha si hace falta (Transformar > Tipo de datos > Fecha). Inicio > Cerrar y cargar en > Solo crear conexion.
Checkpoint: en el panel Consultas y conexiones aparece `FechaCorte` como "Solo conexion".

## Paso 3. Cargar el CSV y limpiar (20 min)

Accion: Datos > Obtener datos > Desde archivo > Desde texto/CSV > `datos/expedientes_sinteticos.csv` > Transformar datos. En Power Query:
- Verifica tipos: fecha_ingreso, fecha_vencimiento y fecha_atencion como Fecha; plazo_dias como Numero entero; el resto Texto.
- Transformar > Formato > Recortar sobre las columnas de texto (quita espacios).
- Renombra la consulta a `tExpedientes`.
Checkpoint: abajo dice 300 filas y fecha_atencion tiene vacios (null) en los no atendidos.

## Paso 4. Columnas dias_restantes y semaforo (25 min)

Accion: en la consulta tExpedientes, Agregar columna > Columna personalizada:
- Nombre `dias_restantes`, formula: `Duration.Days([fecha_vencimiento] - FechaCorte)`. Tipo: Numero entero.
- Nombre `semaforo`, formula:
```
if [estado] = "Atendido" then "Gris (atendido)"
else if [dias_restantes] < 0 then "Rojo (vencido)"
else if [dias_restantes] <= 5 then "Ambar (0 a 5 dias)"
else "Verde (mas de 5 dias)"
```
- Nombre `atendido_fuera_de_plazo`, formula: `if [estado] = "Atendido" and [fecha_atencion] <> null and [fecha_atencion] > [fecha_vencimiento] then "Si" else "No"`.
Checkpoint: Transformar > Agrupar por `semaforo` (en una consulta de referencia temporal, o mirando el filtro de columna) da Gris 165, Rojo 72, Verde 45, Ambar 18. Si no cuadra, revisa que FechaCorte sea 20/10/2026 y de tipo Fecha. Captura: `capturas/paso4_powerquery.png`.

## Paso 5. Cargar como tabla y dar formato (20 min)

Accion: Inicio > Cerrar y cargar en > Tabla, en una hoja nueva llamada `Expedientes`. Luego:
- Inicio > Formato condicional sobre la columna semaforo: Resaltar reglas de celdas > Texto que contiene: "Rojo" relleno rojo claro, "Ambar" relleno amarillo, "Verde" relleno verde claro, "Gris" relleno gris.
- Sobre dias_restantes: Formato condicional > Barras de datos.
- Ancho de columnas ajustado, encabezado fijo (Vista > Inmovilizar fila superior).
Checkpoint: cambia la fecha de corte en Parametros!B1 a 05/11/2026, Datos > Actualizar todo: los semaforos cambian (mas rojos). Vuelve a 20/10/2026 y actualiza. Captura: `capturas/03_control.png` (esta captura va en la ficha del portafolio).

## Paso 6. Tabla dinamica Resumen (25 min)

Accion: con el cursor en la tabla, Insertar > Tabla dinamica > hoja nueva `Resumen`. Filas: area. Columnas: semaforo. Valores: Cuenta de numero. Agrega una segunda tabla dinamica debajo con Filas: responsable, Valores: Cuenta de numero y, como segundo valor, Cuenta de numero mostrada como "% del total de fila" filtrando solo Rojo (o usa la columna atendido_fuera_de_plazo en columnas). Inserta segmentadores (Analizar > Insertar segmentacion de datos) para estado y tipo, conectados a ambas dinamicas.
Checkpoint: la fila Logistica muestra Gris 25, Rojo 18, Verde 15, Ambar 0 y total 58. Captura: `capturas/paso6_resumen.png`.

## Paso 7. Portada (15 min)

Accion: hoja `Portada` al inicio: titulo "Control de expedientes", fecha de corte (formula `=Parametros!B1`), totales por semaforo con `=CONTAR.SI(tExpedientes[semaforo];"Rojo*")` y similares, y la nota "Datos sinteticos generados con generar_expedientes.py (seed 2026). Nombres y expedientes ficticios."
Checkpoint: los cuatro totales de la portada suman 300.

## Paso 8. Verificacion y capturas (10 min)

Accion: Datos > Actualizar todo una vez mas. Guarda. Toma las capturas que falten.
Checkpoint: `capturas/03_control.png` y `capturas/paso6_resumen.png` existen; el libro abre sin advertencias de conexion.

Preguntas de repaso:
1. Por que la fecha de corte va en una tabla y no escrita en la formula: para que cualquiera la cambie sin abrir Power Query.
2. Que ventaja tiene Power Query sobre formulas en la hoja: la transformacion se repite igual cada vez que llega un CSV nuevo; solo hay que actualizar.
3. Como cargarias el registro real de una entidad: reemplazando el CSV por su exportacion (mismas columnas) o conectando Power Query a su carpeta.
