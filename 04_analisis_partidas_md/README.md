# 4. Analisis de mis partidas de Yu-Gi-Oh! Master Duel

Una cadena de datos completa sobre un caso propio: capturar cada partida, dejarla en un formato limpio, traducirla a texto legible y sacar estadisticas que se actualizan solas.

## Que resuelve

El juego muestra en pantalla un registro de cada duelo (quien jugo que carta, en que orden y con que respuesta), pero no deja exportarlo ni guarda estadisticas. Queria responder con datos preguntas concretas: como me va yendo primero y yendo segundo, que cartas jugue en las partidas que gane, en que cartas del rival cayeron mis cartas de interrupcion y como fue mi primer turno en cada partida.

## Como funciona

1. **Captura (componente privado, no se publica).** Un atajo de teclado guarda la partida en curso; desde ahi cada duelo se guarda solo al terminar, sin abrir ventanas y con un aviso sonoro. Se guarda solo lo que el propio juego muestra en su registro.
2. **Formato limpio.** Un JSON por partida en `datos/`: las listas del registro (jugadas, cadenas, fases, turnos), la vida final de cada jugador, cual de los dos soy yo y los nombres de las cartas.
3. **Traduccion.** `codigo/leer_registro.py` convierte cada JSON en texto turno por turno: quien juega, que carta, de que zona a que zona y como se arma cada cadena.
4. **Analisis.** `codigo/analisis.py` recorre todas las partidas y escribe `ESTADISTICAS.md`.
5. **Figura.** `codigo/figura.py` genera `capturas/04_partidas.png` para la ficha.

```
cd codigo
python analisis.py                                   # escribe ../ESTADISTICAS.md
python leer_registro.py --json ../datos/2026-11-23_15-54-44.json
python figura.py                                     # escribe ../capturas/04_partidas.png
```

Solo usa la biblioteca estandar de Python y matplotlib.

## Datos

9 partidas propias del 23 de noviembre de 2026 (la base crece con cada partida que juego): 1 456 registros en total. No hay datos personales: el registro del juego no trae nombres de rivales ni cuentas.

| Campo del JSON | Que guarda |
|---|---|
| `base` | El orden del registro: cada entrada dice de que tipo es (turno, fase, nombre de carta, jugada, cadena) y su posicion en su lista |
| `action` | Cada jugada: carta, zona de origen, zona de destino, dueno de la carta, tipo de jugada (invocacion, activacion, busqueda, descarte, etc.) y si fue material o coste |
| `chain` | Cada eslabon de cadena: carta, numero de eslabon, jugador y si se activa o se resuelve |
| `turn`, `phase` | Inicio de cada turno (jugador del turno y vida de ambos) y cambios de fase |
| `lp`, `rival` | Vida final de cada jugador y cual de los dos es el rival |
| `nombres` | Nombre de cada carta que aparece, tomado del propio juego |

## Resultados (23-nov-2026)

- 9 partidas: 6 ganadas y 3 perdidas.
- Yendo primero: 4 ganadas y 1 perdida. Yendo segundo: 2 ganadas y 2 perdidas.
- El detalle (cartas jugadas, cartas de interrupcion y sobre que cayeron, linea de cada primer turno) esta en `ESTADISTICAS.md`.

Con tan pocas partidas las cifras no son concluyentes; la idea es que la base crezca sola mientras juego.

## Calidad de datos

Tres reglas de atribucion se corrigieron al cruzarlas con partidas reales:

- **Dueno de cada jugada.** La marca de jugador que trae el nombre de la carta falla cuando el rival invoca durante mi turno. El dueno correcto sale de un campo propio de cada jugada. Con la regla vieja, una partida ganada aparecia como perdida.
- **Jugador del turno.** Sale del encabezado de cada turno, no de la primera carta que se juega en el.
- **Cartas ocultas.** Una carta colocada boca abajo no debe heredar el nombre de la carta anterior del registro.

## Limites y siguiente paso

- El arquetipo del rival se infiere de las cartas que mostro; si mostro una o dos, queda como "?".
- Siguiente paso: pasar los JSON a una base SQLite y, con unas 200 partidas, entrenar un modelo que prediga el mazo del rival con sus primeras cartas y estime la probabilidad de ganar segun la mesa al final de cada turno.
