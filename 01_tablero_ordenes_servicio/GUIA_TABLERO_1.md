# Guia paso a paso: tablero "Ordenes de servicio del Estado a personas naturales, 2026"

Tu construyes el tablero en Power BI Desktop. Cada paso tiene una accion y un checkpoint: si el checkpoint no se cumple, no sigas, revisa el paso. Las capturas de los checkpoints van en `capturas/` (Win+Shift+S, pegar en Paint o guardar directo). Tiempo estimado: 4 a 5 horas.

Antes de empezar, corre `python scripts/verificar_medidas.py` y deja la ventana abierta: ahi estan los numeros contra los que vas a comparar.

## Paso 1. Configurar Power BI (10 min)

Accion: abre Power BI Desktop. Archivo > Opciones y configuracion > Opciones > Configuracion regional: idioma de la aplicacion y de los modelos en Espanol (Peru) si esta disponible, o Espanol (Espana). Cierra y vuelve a abrir.
Checkpoint: en Opciones, "Configuracion regional" muestra espanol.

## Paso 2. Cargar los tres CSV (15 min)

Accion: Inicio > Obtener datos > Texto/CSV. Carga `datos/ordenes_2026.csv`, y en la ventana de vista previa pulsa Transformar datos (no Cargar). Repite con `datos/calendario.csv` y `datos/dim_categoria.csv`.
En Power Query, para cada tabla revisa los tipos de columna:
- ordenes: `fecha` como Fecha; `monto` como Numero decimal; `id_orden`, `ruc_entidad`, `lima`, `dur_dias` y las siete banderas como Numero entero; el resto como Texto.
- calendario: `fecha` como Fecha; `anio`, `mes_num` como entero; `anio_mes`, `mes_nombre`, `trimestre` como texto.
- dim_categoria: ambas columnas texto.
Si una columna de fecha sale como texto, usa el icono de tipo a la izquierda del encabezado y elige Fecha (Usando configuracion regional: espanol o ingles segun corresponda; el archivo esta en formato AAAA-MM-DD, que no da problemas).
Checkpoint: `ordenes` muestra 48,949 filas (abajo a la izquierda en Power Query dice "48949 filas"; si no, activa Ver > Perfil de columna sobre todo el conjunto) y no existe ninguna columna llamada proveedor ni ruc_prov. Captura: `capturas/paso2_powerquery.png`.

## Paso 3. Crear dim_entidad por referencia (15 min)

Accion: en Power Query, clic derecho en la consulta `ordenes` > Referencia. Renombra la nueva consulta a `dim_entidad`. En ella: Inicio > Elegir columnas: deja solo `ruc_entidad`, `entidad`, `depto`, `tipo_entidad`. Luego Inicio > Quitar filas > Quitar duplicados con `ruc_entidad` seleccionada.
Checkpoint: `dim_entidad` tiene 1,510 filas. Si tiene mas, es porque una misma entidad aparece con dos nombres: vuelve a Quitar duplicados seleccionando SOLO la columna `ruc_entidad`.

## Paso 4. Cerrar y aplicar (5 min)

Accion: Inicio > Cerrar y aplicar. Ve a la vista Modelo (icono de la izquierda, tres cuadros).
Checkpoint: aparecen cuatro tablas: ordenes, calendario, dim_categoria, dim_entidad. Power BI puede haber creado relaciones automaticas; las revisamos en el paso 5.

## Paso 5. Relaciones y tabla de fechas (15 min)

Accion: en la vista Modelo, arrastra para crear (o verifica) estas tres relaciones, todas de uno a varios, filtro en una direccion:
- calendario[fecha] (1) a ordenes[fecha] (*)
- dim_entidad[ruc_entidad] (1) a ordenes[ruc_entidad] (*)
- dim_categoria[categoria] (1) a ordenes[categoria] (*)
Elimina cualquier otra relacion que Power BI haya creado sola. Luego, en la vista Datos, selecciona la tabla `calendario` > Herramientas de tabla > Marcar como tabla de fechas > columna `fecha`.
Checkpoint: el icono de `calendario` en el modelo muestra la marca de tabla de fechas y las tres lineas de relacion salen de las dimensiones hacia `ordenes`. Captura: `capturas/paso5_modelo.png`.

Pregunta de repaso (PL-300): por que la relacion va de la dimension (1) al hecho (*) y no al reves. Respuesta: porque cada fecha, entidad o categoria es unica en su dimension y se repite muchas veces en las ordenes; el filtro fluye de la dimension al hecho.

## Paso 6. Las ocho medidas (45 min)

Accion: Inicio > Especificar datos > nombre de tabla `Medidas` > Cargar (sin columnas). Clic derecho en `Medidas` > Nueva medida, y escribe una por una las ocho medidas de `medidas_dax.md`. Al terminar cada una, ponla en una tarjeta en el lienzo y compara con el valor esperado.
Formato: selecciona la medida y en Herramientas de medida pon moneda con 2 decimales (1, 3, 4, 7), entero con separador (2, 6) o porcentaje (5, 8).
Checkpoint: las tarjetas muestran Monto total S/ 328,482,581.67; N ordenes 48,949; Ticket promedio 6,710.71; Mediana 4,000.00; % Lima 54.34 %; N entidades 1,510. Para las medidas 7 y 8 arma una tabla con calendario[anio_mes], Monto total, Monto mes anterior y Variacion mensual %: junio debe mostrar 54,809,723.35 como mes anterior y -15.60 %. Captura: `capturas/paso6_medidas.png`.

Pregunta de repaso: que pasa con DATEADD si `calendario` no esta marcada como tabla de fechas. Respuesta: la medida devuelve en blanco o resultados raros; DATEADD exige una columna de fechas continua.

## Paso 7. Pagina Resumen (45 min)

Accion: renombra la pagina 1 a "Resumen". Coloca:
- Cuatro tarjetas arriba: Monto total, N ordenes, Ticket promedio, % ordenes Lima.
- Un grafico de columnas agrupadas y lineas: eje X calendario[anio_mes], columnas Monto total, linea Variacion mensual %.
- Dos segmentadores: calendario[anio_mes] (estilo lista desplegable) y dim_entidad[tipo_entidad] (estilo mosaico).
- Un cuadro de texto abajo con la fuente: "Fuente: CONOSCE, datos abiertos OSCE/OECE. Ordenes de servicio a personas naturales (RUC 10) emitidas de enero a setiembre de 2026 (setiembre incompleto). Sin datos de proveedores."
Checkpoint: al elegir 2026-06 en el segmentador, las tarjetas muestran 46,258,939.86; 6,891; 6,712.95; 54.98 %. Quita el filtro y vuelven a los totales. Captura final de la pagina: `capturas/01_resumen.png` (esta captura va en la ficha del portafolio).

## Paso 8. Pagina Por entidad (40 min)

Accion: nueva pagina "Por entidad". Coloca:
- Barras horizontales: eje Y dim_entidad[entidad], eje X Monto total; en Filtros del objeto visual, "N principales" 15 por Monto total.
- Barras agrupadas por departamento: eje Y dim_entidad[depto], eje X N ordenes, ordenado de mayor a menor.
- Tabla: entidad, N ordenes, Mediana monto, Ticket promedio, Monto total; ordenada por Monto total.
- Sincroniza los segmentadores de la pagina Resumen (Ver > Sincronizar segmentadores) para que apliquen tambien aqui.
Checkpoint: la primera barra es el Jurado Nacional de Elecciones con 38,374,447.32 y la segunda OEFA con 12,596,503.60. Captura: `capturas/02_por_entidad.png`.

Pregunta de repaso: diferencia entre filtrar con "N principales" en el visual y usar una medida con TOPN. Respuesta: el filtro del visual es dinamico y respeta los segmentadores; TOPN en DAX sirve cuando el ranking se necesita dentro de un calculo.

## Paso 9. Pagina Por categoria y perfil (40 min)

Accion: nueva pagina "Por categoria". Coloca:
- Matriz: filas dim_categoria[categoria], columnas ordenes[perfil], valores Mediana monto y N ordenes.
- Barras apiladas 100 %: eje Y dim_categoria[categoria], eje X N ordenes, leyenda ordenes[rango_monto].
- Segmentador de dim_categoria[categoria].
- Cuadro de texto: "Cada orden tiene una sola categoria, asignada por prioridad (tableros > automatizacion > analisis > reportes > bases de datos > expedientes > hidrocarburos)."
Checkpoint: la fila "Tableros y Power BI" muestra 88 ordenes y mediana 13,432.40; "Automatizacion y sistemas" 1,159 y 10,500. Captura: `capturas/03_por_categoria.png`.

## Paso 10. Tema y acabado (20 min)

Accion: Ver > Temas: elige uno sobrio (Ejecutivo o Clasico). Titulos de pagina con un cuadro de texto de 16 pt. Alinea los objetos (Formato > Alinear). Mismo tamano de tarjetas. Nada de colores chillones.
Checkpoint: las tres paginas se leen sin hacer zoom y los numeros tienen separador de miles.

## Paso 11. Guardar y capturas (10 min)

Accion: Archivo > Guardar como `tablero_ordenes_2026.pbix` en esta misma carpeta. Vuelve a tomar las tres capturas finales si cambiaste algo: `capturas/01_resumen.png`, `capturas/02_por_entidad.png`, `capturas/03_por_categoria.png`.
Checkpoint: el archivo pesa menos de 50 MB (si pesa mas, avisa: se excluye del repo y la ficha usa solo capturas).

## Paso 12. Repaso final (10 min)

Responde sin mirar:
1. Que hace DIVIDE que no hace el operador "/": evita el error de division entre cero y devuelve en blanco o un valor alternativo.
2. Que diferencia hay entre una columna calculada y una medida: la columna se calcula fila por fila al cargar y ocupa memoria; la medida se calcula en el momento segun los filtros.
3. Que hace CALCULATE en la medida % ordenes Lima: cambia el contexto de filtro para contar solo las ordenes con lima = 1.
4. Por que setiembre muestra una caida de 96 %: porque la fuente solo trae los primeros dias de setiembre; es un problema de datos, no del tablero. Conviene decirlo en la nota.
5. Como harias que el segmentador de mes afecte las tres paginas: Ver > Sincronizar segmentadores.

Si respondes las cinco, puedes explicar este tablero en una entrevista o ante un area usuaria.
