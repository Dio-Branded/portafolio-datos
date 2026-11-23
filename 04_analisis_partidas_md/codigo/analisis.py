"""Analisis de mis partidas de Yu-Gi-Oh! Master Duel (un JSON por partida en ../datos).
Saca: resultados yendo primero y segundo, arquetipo del rival, cartas que jugaste y con que resultado, en que cayo cada handtrap
(tuya y del rival) y tus lineas de turno 1 (para aprender el mazo de tus partidas reales).

    python analisis.py            # escribe ../ESTADISTICAS.md y lo muestra

Ignora los volcados "_en_curso" cuando ese duelo tambien se guardo al terminar, y los volcados sin dato de quien eres.
"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from leer_registro import ACC, nombre, OUT, quien_soy, dueno, cargar_nombres  # noqa: E402

GENERICAS = {"Ash Blossom & Joyous Spring", 'Maxx "C"', "Droll & Lock Bird", "Infinite Impermanence", "Effect Veiler",
             "Ghost Ogre & Snow Rabbit", "Ghost Belle & Haunted Mansion", "Nibiru, the Primal Being", "Mulcharmy Fuwalos",
             "Mulcharmy Purulia", "Mulcharmy Meowls", "Called by the Grave", "Crossout Designator", "Triple Tactics Talent",
             "Forbidden Droplet", "Dark Ruler No More", "Harpie's Feather Duster", "Lightning Storm", "Pot of Prosperity",
             "Linkuriboh", "Salamangreat Almiraj", "Crystron Halqifibrax Prism", "Baronne de Fleur", "Charmer Quartet in Bloom",
             "I:P Masquerena", "S:P Little Knight", "Knightmare Unicorn", "Accesscode Talker", "Apollousa, Bow of the Goddess",
             "Droplet", "Super Starslayer TY-PHON - Sky Crisis", "Bystial Druiswurm", "Bystial Magnamhut", "Piri Reis Map"}
JUEGO = {"SUMMON", "SPSUMMON", "SPSUMMON_FUSION", "SPSUMMON_SYNC", "SPSUMMON_XYZ", "SPSUMMON_PENDULUM", "SPSUMMON_LINK",
         "SPSUMMON_RITUAL", "SPSUMMONDEF", "HAPPEN", "SETH", "SETV"}
INV = {"SUMMON": "Normal", "SPSUMMON": "Especial", "SPSUMMONDEF": "Especial", "SPSUMMON_FUSION": "Fusion", "SPSUMMON_SYNC": "Sincronia",
       "SPSUMMON_XYZ": "Xyz", "SPSUMMON_PENDULUM": "Pendulo", "SPSUMMON_LINK": "Enlace", "SPSUMMON_RITUAL": "Ritual",
       "HAPPEN": "activa", "SEARCH": "busca", "ADDCARD": "anade", "SETH": "coloca", "SETV": "coloca"}


def eventos(r, yo):
    """Mismo criterio que traducir() de md_registro_leer, como lista de diccionarios. Jugadores = numero del motor."""
    ev, ult, prev, turno = [], None, None, 0
    for lab, i in r["base"]:
        antes, prev = prev, lab
        if lab == "ShowTurn":
            turno += 1; ult = None
            ev.append({"k": "turno", "turno": turno, "tp": int(r["turn"][i][0]) & 0xFFFFFFFF})
        elif lab == "ShowCardName":
            ult = r["cardname"][i]
        elif lab == "ShowAction":
            a = r["action"][i]; tipo = ACC.get(a["c"][4], a["c"][4])
            if tipo == "NONE":
                continue
            cid = a["r"][0] if 0 < a["r"][0] < 30000 else (a["l"][0] if 0 < a["l"][0] < 30000 else
                                                          (ult[0] if ult and antes == "ShowCardName" and 0 < ult[0] < 30000 else -1))
            ev.append({"k": "accion", "turno": turno, "quien": dueno(a), "tipo": tipo, "carta": cid, "de": a["l"][2],
                       "a": a["r"][2] if (a["r"][0] or a["r"][2]) else None, "material": bool(a["l"][5] or a["r"][5])})
        elif lab == "ShowChain":
            c = r["chain"][i]
            ev.append({"k": "cadena", "turno": turno, "quien": yo if c[2] == 1 else 1 - yo, "carta": c[0], "eslabon": c[1],
                       "activa": c[3] == 0})
    return ev


def arquetipo(cartas):
    c = Counter()
    for n in cartas:
        if n in GENERICAS:
            continue
        for w in set(re.findall(r"[A-Za-z][A-Za-z\-']{3,}", n)):
            if w.lower() not in {"the", "of", "and", "with", "from", "power", "dragon", "lord", "king", "queen"}:
                c[w] += 1
    if not c:
        return "?"
    w, n = c.most_common(1)[0]
    return w if n >= 2 else "?"


def analizar(f):
    r = json.load(open(f, encoding="utf-8"))
    if "lp" not in r:       # volcado parcial (sin fin de duelo)
        return None
    cargar_nombres(r)
    yo = quien_soy(r)
    if yo is None:
        return None
    riv = 1 - yo
    ev = eventos(r, yo)
    turnos = [e for e in ev if e["k"] == "turno"]
    primero = turnos[0].get("tp") == yo if turnos else None
    lp = r.get("lp") or [None, None]
    if "_en_curso" in f.name:
        res = "en curso"
    elif None in lp:
        res = "?"
    else:
        res = "gana" if lp[riv] <= 0 < lp[yo] else ("pierde" if lp[yo] <= 0 else "?")
    acc = [e for e in ev if e["k"] == "accion"]
    mias = [e for e in acc if e["quien"] == yo and e["carta"] > 0]
    suyas = [e for e in acc if e["quien"] == riv and e["carta"] > 0]
    jugadas = sorted({nombre(e["carta"]) for e in mias if e["tipo"] in JUEGO})
    vistas_rival = sorted({nombre(e["carta"]) for e in suyas})
    # handtraps / respuestas: eslabon >= 2 responde a la activacion anterior de la misma cadena
    resp, cadena = [], []
    for e in ev:
        if e["k"] == "accion" and e["tipo"] == "HAPPEN" and e["carta"] > 0:
            if not cadena or cadena[-1][0] != e["carta"]:
                cadena.append((e["carta"], e["quien"]))
        elif e["k"] == "cadena":
            if e["activa"] and e["eslabon"] >= 2:
                objetivo = cadena[-1] if cadena else (None, None)
                resp.append({"quien": e["quien"], "carta": nombre(e["carta"]), "contra": nombre(objetivo[0]) if objetivo[0] else "?",
                             "turno": e["turno"], "negada": False})
                cadena.append((e["carta"], e["quien"]))
            elif not e["activa"] and e["eslabon"] == 1:
                cadena = []
        elif e["k"] == "accion" and e["tipo"] == "DISABLE" and resp:
            if resp[-1]["contra"] == nombre(e["carta"]):
                resp[-1]["negada"] = True
    # tu primer turno: la linea (invocaciones y activaciones en orden)
    mi_turno = next((t["turno"] for t in turnos if t.get("tp") == yo), None)
    linea = []
    for e in mias:
        if e["turno"] == mi_turno and e["tipo"] in INV and not e["material"]:
            linea.append("%s (%s)" % (nombre(e["carta"]), INV[e["tipo"]]))
    return {"archivo": f.name, "yo": yo, "primero": primero, "resultado": res, "turnos": len(turnos), "rival": arquetipo(vistas_rival),
            "jugadas": jugadas, "vistas_rival": vistas_rival, "respuestas": resp, "linea": linea, "mi_turno": mi_turno}


def main(silencioso=False):
    if not silencioso:
        sys.stdout.reconfigure(encoding="utf-8")
    fs = sorted(OUT.glob("*.json"))
    completos = {f.name[:16] for f in fs if "_en_curso" not in f.name}
    P = []
    for f in fs:
        if "_en_curso" in f.name and any(f.name[:13] == c[:13] and abs(int(f.name[14:16]) - int(c[14:16])) <= 1 for c in completos):
            continue
        a = analizar(f)
        if a and a["resultado"] != "en curso":
            P.append(a)
    L = ["# Tus partidas de Master Duel", "", "Generado por codigo/analisis.py a partir de datos/ (%d partidas completas)." % len(P), ""]
    def marcador(xs):
        g = sum(1 for x in xs if x["resultado"] == "gana"); p = sum(1 for x in xs if x["resultado"] == "pierde")
        return "%d %s, %d %s%s" % (g, "ganada" if g == 1 else "ganadas", p, "perdida" if p == 1 else "perdidas",
                                    (" (%d%% ganadas)" % round(100 * g / (g + p))) if g + p else "")
    L += ["## Resultados", "",
          "- Total: %s" % marcador(P),
          "- Yendo primero: %s" % marcador([x for x in P if x["primero"]]),
          "- Yendo segundo: %s" % marcador([x for x in P if x["primero"] is False]), "",
          "| Partida | Fuiste | Rival | Turnos | Resultado |", "|---|---|---|---|---|"]
    for x in P:
        L.append("| %s | %s | %s | %d | %s |" % (x["archivo"][:16], "primero" if x["primero"] else "segundo", x["rival"], x["turnos"], x["resultado"]))
    uso = defaultdict(lambda: [0, 0])
    for x in P:
        for c in x["jugadas"]:
            uso[c][0] += 1; uso[c][1] += x["resultado"] == "gana"
    L += ["", "## Cartas que jugaste (en cuantas partidas y cuantas ganaste)", "", "| Carta | Partidas | Ganadas |", "|---|---|---|"]
    for c, (n, g) in sorted(uso.items(), key=lambda kv: -kv[1][0]):
        L.append("| %s | %d | %d |" % (c, n, g))
    L += ["", "## Handtraps y respuestas", "", "| Partida | Quien | Carta | Contra | La nego |", "|---|---|---|---|---|"]
    for x in P:
        for q in x["respuestas"]:
            L.append("| %s | %s | %s | %s | %s |" % (x["archivo"][11:16], "tu" if q["quien"] == x["yo"] else "rival", q["carta"], q["contra"], "si" if q["negada"] else ""))
    L += ["", "## Tu primer turno en cada partida", ""]
    for x in P:
        L.append("- %s (%s, vs %s, %s): %s" % (x["archivo"][:16], "primero" if x["primero"] else "segundo", x["rival"], x["resultado"],
                                               " -> ".join(x["linea"]) or "(nada)"))
    txt = "\n".join(L) + "\n"
    (OUT.parent / "ESTADISTICAS.md").write_text(txt, encoding="utf-8")
    if not silencioso:
        print(txt)


if __name__ == "__main__":
    main()
