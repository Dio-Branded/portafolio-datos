# 4. Match analytics for my own Yu-Gi-Oh! Master Duel games

An end-to-end data pipeline on a personal use case: capture every match, store it in a clean format, translate it into a readable play-by-play and keep a stats report that updates itself.

## Problem

The game shows a duel log on screen (who played which card, in what order and how the opponent responded), but it cannot be exported and the game keeps no statistics. I wanted data-backed answers to concrete questions: how do I do going first versus going second, which cards did I play in the games I won, which opponent cards did my interruption cards (hand traps) hit, and what did my first turn look like in each game.

## How it works

1. **Capture (private component, not published).** A keyboard shortcut starts a background recorder; from then on every duel is saved automatically when it ends, with no windows and an audio cue. It only stores what the game itself shows in its duel log.
2. **Clean format.** One JSON file per match in `datos/`: the log lists (plays, chains, phases, turns), final life points, which player is me, and card names.
3. **Translation.** `codigo/leer_registro.py` turns each JSON into a turn-by-turn text: who plays which card, from which zone to which zone, and how each chain is built.
4. **Analysis.** `codigo/analisis.py` walks all matches and writes `ESTADISTICAS.md`: results going first and second, opponent archetype inferred from the cards they showed, cards I played and their win record, hand traps and what they hit, and my full first-turn line.
5. **Figure.** `codigo/figura.py` renders `capturas/04_partidas.png`.

Standard library Python plus matplotlib.

## Data

9 of my own matches from 23 Nov 2026 (the dataset grows with every game I play), 1,456 log records in total. No personal data: the game log contains no opponent names or accounts.

## Data quality

Three attribution rules were corrected after checking them against real matches:

- **Owner of each play.** The "local player" flag attached to card names is wrong when the opponent summons during my turn; the true owner comes from a per-play field. With the old rule, a game I won showed up as a loss.
- **Turn player.** Read from each turn header, not inferred from the first card played in that turn.
- **Hidden cards.** A face-down card must not inherit the name of the previous card in the log.

## Results so far (23 Nov 2026)

9 matches: 6 wins, 3 losses. Going first 4-1, going second 2-2. Too few games to conclude anything yet; the point is that the dataset keeps growing on its own.

## Next step

Load the JSON files into SQLite and, at around 200 matches, train a model that predicts the opponent's deck from their first cards and estimates win probability from the board state at the end of each turn.
