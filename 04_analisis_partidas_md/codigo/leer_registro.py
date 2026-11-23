"""Traduce el registro de un duelo de Yu-Gi-Oh! Master Duel (un JSON por partida) a texto legible, turno por turno.

El JSON tiene las listas del registro que el propio juego muestra en pantalla (jugadas, cadenas, fases, turnos) y los nombres de
las cartas. El componente que captura ese registro desde el juego es privado y no se publica.

Uso:  python leer_registro.py --json ../datos/2026-11-23_15-54-44.json
"""
import argparse, json, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATOS = AQUI.parent / "datos"
OUT = DATOS
CARDS = {}   # en la version privada: tabla de cartas; aqui los nombres vienen dentro de cada JSON ("nombres")
LOGACTIONTYPE = {"ACTION_NONE": 0, "ACTION_DRAW": 1, "ACTION_SUMMON": 2, "ACTION_SPSUMMON": 3, "ACTION_SPSUMMON_RITUAL": 4, "ACTION_SPSUMMON_FUSION": 5, "ACTION_SPSUMMON_SYNC": 6, "ACTION_SPSUMMON_XYZ": 7, "ACTION_SPSUMMON_PENDULUM": 8, "ACTION_SPSUMMON_LINK": 9, "ACTION_ATTACK": 10, "ACTION_HAPPEN": 11, "ACTION_DISABLE": 12, "ACTION_SETH": 13, "ACTION_SETV": 14, "ACTION_RELEASE": 15, "ACTION_REVERSE": 16, "ACTION_CONFIRM": 17, "ACTION_EXCLUDE": 18, "ACTION_FLIPTOP": 19, "ACTION_EXPLOSION": 20, "ACTION_BREAK": 21, "ACTION_CTRCHANGE": 22, "ACTION_LOCKON": 23, "ACTION_SENDTOGRAVE": 24, "ACTION_DROP": 25, "ACTION_SEARCH": 26, "ACTION_ADDCARD": 27, "ACTION_MOVE": 28, "ACTION_VANISH": 29, "ACTION_EFFECTIMPL": 30, "ACTION_HANDOPEN": 31, "ACTION_REVERSESUMMON": 32, "ACTION_RETURN": 33, "ACTION_REVERSEBACK": 34, "ACTION_SPSUMMONDEF": 35, "ACTION_SPSUMMONSET": 36, "ACTION_ATKTODEFCHANGE": 37, "ACTION_DEFTOATKCHANGE": 38, "ACTION_PUT": 39, "ACTION_ZONESELECT": 40, "CARDCHEAT_ADD": 41, "CARDCHEAT_SET": 42, "CARDCHEAT_PUT": 43, "CARDCHEAT_APPLY": 44, "CARDCHEAT_SEND": 45, "COST_EXCLUDE": 46, "COST_RETURN": 47, "COST_MOVE": 48, "COST_SENDTOGRAVE": 49, "COST_RELEASE": 50, "COST_DROP": 51, "COST_VANISH": 52}
PHASE = {"Draw": 0, "Standby": 1, "Main1": 2, "Battle": 3, "Main2": 4, "End": 5, "Null": 7}
ACC = {v: k.replace("ACTION_", "").replace("CARDCHEAT_", "CHEAT_") for k, v in LOGACTIONTYPE.items()}
FASE = {v: k for k, v in PHASE.items()}

ZONA = {**{i: "M%d" % (i + 1) for i in range(5)}, 5: "EMZ izq", 6: "EMZ der", **{i: "M/T%d" % (i - 6) for i in range(7, 12)},
        12: "campo", 13: "mano", 14: "Extra", 15: "Deck", 16: "GY", 17: "desterrada"}
ES = {"HAPPEN": "activa", "SUMMON": "Invocacion Normal", "SPSUMMON": "Inv. Especial", "SPSUMMON_FUSION": "Fusion",
      "SPSUMMON_SYNC": "Sincronia", "SPSUMMON_XYZ": "Xyz", "SPSUMMON_PENDULUM": "Pendulo", "SPSUMMON_LINK": "Enlace",
      "SPSUMMON_RITUAL": "Ritual", "SPSUMMONDEF": "Inv. Especial en DEF", "SEARCH": "anade (busca)", "ADDCARD": "anade",
      "SENDTOGRAVE": "al GY", "DROP": "descarta", "EXCLUDE": "destierra", "BREAK": "destruida", "EXPLOSION": "destruida",
      "RELEASE": "sacrificada", "RETURN": "regresa", "MOVE": "mueve", "PUT": "coloca", "SETH": "coloca boca abajo",
      "SETV": "coloca", "DRAW": "roba", "ATTACK": "ataca", "DISABLE": "negada", "VANISH": "se va", "CONFIRM": "revela",
      "HANDOPEN": "revela", "COST_SENDTOGRAVE": "coste: al GY", "COST_DROP": "coste: descarta", "COST_EXCLUDE": "coste: destierra",
      "COST_RELEASE": "coste: sacrifica", "COST_RETURN": "coste: regresa", "COST_MOVE": "coste: mueve", "COST_VANISH": "coste"}


NOMBRES_JUEGO = {}   # (23-nov) nombres que da el propio juego (r["nombres"]): mandan sobre data/md_cards.json


def cargar_nombres(r):
    NOMBRES_JUEGO.clear(); NOMBRES_JUEGO.update(r.get("nombres") or {})


def nombre(cid):
    if str(cid) in NOMBRES_JUEGO:
        return NOMBRES_JUEGO[str(cid)]
    v = CARDS.get(str(cid))
    return v["name"] if v else ("carta %d" % cid if 0 < cid < 30000 else "carta oculta")


def quien_soy(r):
    """(23-nov) Tu numero de jugador en el motor. Con IsRival si esta; si no, el dueno (byte 3) de la primera jugada cuyo
    nombre lleva la marca de jugador local (team 1) y que es una activacion o Invocacion Normal (esas no fallan)."""
    yo = [k for k, x in enumerate(r.get("rival") or []) if x == 0]
    if yo:
        return yo[0]
    ult, prev = None, None
    for lab, i in r["base"]:
        antes, prev = prev, lab
        if lab == "ShowCardName":
            ult = r["cardname"][i]
        elif lab == "ShowAction" and ult and antes == "ShowCardName" and ult[1] == 1:
            a = r["action"][i]
            if ACC.get(a["c"][4]) in ("HAPPEN", "SUMMON", "DRAW"):
                return a["r"][3] if (a["r"][0] or a["r"][2]) else a["l"][3]
    return None


def dueno(a):
    """(23-nov) Dueno de la carta de una jugada = byte 3 del lado de destino (o de origen si no hay destino), numero de
    jugador del motor. El team de ShowCardName y el bit 5 del centro son 'jugador local' y fallan cuando el rival invoca
    durante tu turno (Dracotail Faimena -> Arthalion, Gaze of Timaeus -> Dragoon)."""
    return a["r"][3] if (a["r"][0] or a["r"][2]) else a["l"][3]


def traducir(r):
    cargar_nombres(r)
    L, jug = [], {}
    ult_nombre = None
    yo = quien_soy(r)
    def J(p):   # p = numero de jugador del motor
        if yo is None or p not in (0, 1): return "J%s" % p
        return "TU" if p == yo else "RIVAL"
    def JL(team):   # team de ShowChain = marca de jugador local (1 = tu)
        return "TU" if team == 1 else "RIVAL"
    prev = None
    for lab, i in r["base"]:
        antes, prev = prev, lab
        if lab == "ShowTurn":
            t = r["turn"][i]; tp = int(t[0]) & 0xFFFFFFFF; ult_nombre = None
            L.append("\n===== Turno %d (%s)   LP %s =====" % (i + 1, J(tp), ("TU %d / RIVAL %d" % ((t[2], t[3]) if yo == 0 else (t[3], t[2]))) if yo in (0, 1) else "p0 %d / p1 %d" % (t[2], t[3])))
        elif lab == "ShowPhase":
            L.append("  -- %s" % FASE.get(r["phase"][i], r["phase"][i]))
        elif lab == "ShowCardName":
            c = r["cardname"][i]; ult_nombre = c
        elif lab == "ShowAction":
            a = r["action"][i]; tipo = ACC.get(a["c"][4], a["c"][4]); cid = a["r"][0] if 0 < a["r"][0] < 30000 else (a["l"][0] if 0 < a["l"][0] < 30000 else (ult_nombre[0] if ult_nombre and antes == "ShowCardName" and 0 < ult_nombre[0] < 30000 else -1))
            if tipo == "NONE":
                continue
            de = ZONA.get(a["l"][2], a["l"][2]); a_ = ZONA.get(a["r"][2], a["r"][2])
            extra = " [material]" if a["l"][5] or a["r"][5] else ""
            txt = "  %s %s: %s (%s -> %s)%s" % (J(dueno(a)), nombre(cid), ES.get(tipo, tipo), de, a_ if a["r"][0] or a["r"][2] else "-", extra)
            L.append(txt)
        elif lab == "ShowChain":
            c = r["chain"][i]
            L.append("  %s eslabon %d: %s (%s)" % ("ACTIVA" if c[3] == 0 else "resuelve", c[1], nombre(c[0]), JL(c[2])))
        elif lab == "ShowTag":
            g = r["tag"][i]; L.append("    (%s)" % ("objetivo" if g[0] == 0 else "coste"))
        elif lab in ("CardMoveMulti", "CardMoveMultiHeader"):
            if lab == "CardMoveMulti":
                mm = r["movemulti"][i]; n = len(mm["acts"]); a = mm["acts"][0] if n else None
                if a: L.append("  (%d cartas: %s, %s -> %s)" % (n, ES.get(ACC.get(a["c"][4]), ACC.get(a["c"][4])), ZONA.get(a["l"][2]), ZONA.get(a["r"][2])))
        elif lab == "ShowText":
            L.append("  (texto %d)" % r["text"][i][0])
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--json", required=True); a = ap.parse_args()
    r = json.load(open(a.json, encoding="utf-8"))
    txt = traducir(r)
    salida = Path(a.json).with_suffix(".txt")
    salida.write_text(txt, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8"); print(txt); print()
    print("guardado:", salida)


if __name__ == "__main__":
    main()
