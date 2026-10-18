#!/usr/bin/env python3
"""Regenera las filas del calendario 26·27 de index.html a partir de calendario-26-27.json.

    python3 scripts/calendario.py          reescribe el bloque de filas de index.html
    python3 scripts/calendario.py --check  solo comprueba que index.html está al día (sale con 1 si no)

Única fuente del calendario: calendario-26-27.json (el formulario /comunidad lee el mismo
archivo en el navegador, así que con publicar esta web basta). Solo se toca lo que hay entre
<!-- calendario:inicio --> y <!-- calendario:fin -->; el resto de index.html no se mira.
Sin dependencias: Python 3 de serie.
Campos opcionales por plan (fila destacada en noche con una pastilla y un punto que late):
  "enVivo": true                 → la pastilla dice «En vivo» desde ya.
  "aviso": "Últimas plazas"      → la pastilla dice ese texto…
  "enVivoDesde": "AAAA-MM-DDTHH:MM:SS+01:00" → …y a partir de ese momento (hora de Madrid) el navegador la cambia
                                   solo a «En vivo», sin publicar nada (ver data-vivo-desde en el script de index.html).
"""
import json
import re
import sys
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
JSON = RAIZ / "calendario-26-27.json"
INDEX = RAIZ / "index.html"
ALIADOS = RAIZ / "img" / "aliados"
INICIO = "<!-- calendario:inicio"
FIN = "<!-- calendario:fin -->"

MESES = {
    "ENE": ("enero", 1), "FEB": ("febrero", 2), "MAR": ("marzo", 3), "ABR": ("abril", 4),
    "MAY": ("mayo", 5), "JUN": ("junio", 6), "JUL": ("julio", 7), "AGO": ("agosto", 8),
    "SEP": ("septiembre", 9), "OCT": ("octubre", 10), "NOV": ("noviembre", 11), "DIC": ("diciembre", 12),
}
ABREV = {nombre: abr.lower() for abr, (nombre, _) in MESES.items()}

# utm_medium de cada fila: cal_<sufijo>. Los planes de hoy van fijados a mano para no romper la
# serie de analítica; a un plan nuevo se le saca del id (ver sufijo_automatico).
UTM = {
    "2627-el-palmar": "palmar", "2627-kalma-fest": "kalma", "2627-marruecos": "marruecos",
    "2627-maldivas-abril": "maldivas_abr", "2627-maldivas-mayo": "maldivas_may",
    "2627-bali-junio": "bali_jun", "2627-bali-julio": "bali_jul",
}
# Globos recortados de la historia de Instagram (baja resolución): pedir el original al aliado.
PROVISIONALES = {"comunidaddelsol-madrid", "triangulosurfmorocco", "calaveritahotels"}

FLECHA = ('<span class="plan-flecha" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
          'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg></span>')


def sufijo_automatico(pid):
    """2627-maldivas-abril → maldivas_abr; 2627-el-palmar → palmar; 2627-kalma-fest → kalma."""
    s = re.sub(r"^\d{4}-", "", pid)
    s = re.sub(r"^(el|la|los|las)-", "", s)
    s = re.sub(r"-fest$", "", s)
    for nombre, abr in ABREV.items():
        s = re.sub(rf"-{nombre}$", f"-{abr}", s)
    return s.replace("-", "_")


def anio(temporada, mes_num):
    """Temporada «26·27»: de septiembre a diciembre es 2026; de enero a agosto, 2027."""
    primero = 2000 + int(re.match(r"\d{2}", temporada).group())
    return primero if mes_num >= 9 else primero + 1


def lista_con(aliados):
    aliados = [a.strip() for a in aliados if a.strip()]
    if not aliados:
        return ""
    if len(aliados) == 1:
        return aliados[0]
    return ", ".join(aliados[:-1]) + " y " + aliados[-1]


def validar(doc):
    errores = []
    ids = [p.get("id") for p in doc.get("planes", [])]
    if len(ids) != len(set(ids)):
        errores.append("hay ids repetidos (un id nunca se reutiliza para otro evento)")
    for p in doc.get("planes", []):
        pid = p.get("id", "¿sin id?")
        for k in ("id", "mes", "fecha", "titulo", "etiqueta", "linea", "meta", "valor", "con", "globos", "nota", "paginaPropia", "hasta", "reservable", "stripeUrl", "agotado"):
            if k not in p:
                errores.append(f"{pid}: falta la clave «{k}»")
        if p.get("mes", "").upper() not in MESES:
            errores.append(f"{pid}: mes «{p.get('mes')}» no es ENE…DIC")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.get("hasta", "")):
            errores.append(f"{pid}: «hasta» debe ser AAAA-MM-DD")
        if p.get("fecha") and not re.fullmatch(r"\d{1,2}([–-]\d{1,2})?", p["fecha"]):
            errores.append(f"{pid}: «fecha» debe ser un día («7»), un rango («2–8») o vacía")
        if p.get("enVivoDesde") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?[+-]\d{2}:\d{2}", p["enVivoDesde"]):
            errores.append(f"{pid}: «enVivoDesde» debe ser AAAA-MM-DDTHH:MM:SS+01:00 (hora de Madrid con su desfase)")
        for g in p.get("globos", []):
            if not (ALIADOS / f"{g}.webp").is_file():
                errores.append(f"{pid}: falta img/aliados/{g}.webp")
    return errores


def fecha_corta(p):
    """«7 nov», «2–8 dic» o, si el plan solo tiene mes, «junio» (sin día, la abreviatura confunde)."""
    nombre = MESES[p["mes"].upper()][0]
    dia = p["fecha"].strip()
    return f"{dia} {ABREV[nombre]}" if dia else nombre


def fila(p, temporada):
    mes = p["mes"].upper()
    nombre_mes, n = MESES[mes]
    a = anio(temporada, n)
    fecha = p["fecha"].strip()
    if fecha:
        partes = re.split(r"[–-]", fecha)
        rango = len(partes) == 2
        datetime_ = f"{a}-{n:02d}-{int(partes[0]):02d}"
        dia = (f'<span class="plan-dia{" rango" if rango else ""}">{escape(fecha)}</span>'
               f'<span class="plan-mes">{mes.lower()}</span>')
        legible = f"del {partes[0]} al {partes[1]} de {nombre_mes}" if rango else f"{fecha} de {nombre_mes}"
    else:
        datetime_ = f"{a}-{n:02d}"
        dia = f'<span class="plan-dia">{mes}</span>'
        legible = f"en {nombre_mes}"
    nota = p["nota"].strip()
    if nota:
        dia += f'<span class="plan-nota">{escape(nota)}</span>'
        legible += ", " + (re.sub(r"^\+\s*", "con ", nota) if nota.startswith("+") else nota)

    con = lista_con(p["con"])
    titulo, linea = p["titulo"].strip(), p["linea"].strip()
    titulo_html = escape(titulo).replace("Flow Fest", '<span class="ff">Flow Fest</span>')  # el nombre del festival, destacado

    if p["paginaPropia"]:
        href = p["paginaPropia"]
        evento = "clic_" + re.sub(r"[^a-z0-9]+", "_", href.lower()).strip("_")
        attr_evento = f' data-evento="{evento}"'
        cierre = f"Ver la página de {titulo}"
    else:
        href = f"/comunidad?utm_source=descubre-tu-clic&amp;utm_medium=cal_{UTM.get(p['id']) or sufijo_automatico(p['id'])}"
        attr_evento = ""
        cierre = "Entra a VIBRA para reservar plaza"
    if p["agotado"]:
        attr_evento += ' data-agotado="true"'
        cierre = "Plazas agotadas. " + cierre

    aviso_txt = p.get("aviso") or ""
    desde = p.get("enVivoDesde") or ""
    vivo = bool(p.get("enVivo") or aviso_txt or desde)  # fila destacada con pastilla (ver docstring)
    pastilla = "En vivo" if p.get("enVivo") or not aviso_txt else aviso_txt
    prefijo = "En vivo ahora. " if pastilla == "En vivo" else f"{pastilla.rstrip('.')}. "
    label = (prefijo if vivo else "") + f"{titulo}, {legible}: {linea.rstrip('.')}."
    attr_desde = f' data-vivo-desde="{escape(desde, quote=True)}"' if desde and pastilla != "En vivo" else ""
    if con:
        label += f" Con {con}."
    label += f" {cierre}"

    globos = []
    for g in p["globos"]:
        aviso = "<!-- globo provisional: pedir original -->" if g in PROVISIONALES else ""
        globos.append(f'          {aviso}<img class="disco" src="img/aliados/{g}.webp" srcset="img/aliados/{g}.webp 104w" '
                      f'sizes="(min-width: 600px) 52px, 36px" width="104" height="104" loading="lazy" decoding="async" alt="">')

    lineas = [
        f'    <li class="reveal{" en-vivo" if vivo else ""}" data-hasta="{p["hasta"]}">',
        f'      <a class="plan" href="{href}"{attr_evento} aria-label="{escape(label, quote=True)}">',
        f'        <p class="plan-fecha"><time datetime="{datetime_}">{dia}</time></p>',
        '        <div class="plan-cuerpo">',
        *([f'          <span class="plan-vivo" aria-hidden="true"{attr_desde}><span class="vivo-punto"></span><span class="vivo-txt">{escape(pastilla)}</span></span>'] if vivo else []),
        f'          <h3 class="plan-t">{titulo_html}</h3>',
        f'          <p class="plan-linea">{escape(linea)}</p>',
    ]
    if con:
        lineas.append(f'          <p class="plan-con">Con {escape(con)}</p>')
    lineas.append('        </div>')
    if globos:
        lineas += ['        <div class="plan-aliados" aria-hidden="true">', *globos, '        </div>']
    lineas += [f'        {FLECHA}', '      </a>', '    </li>']
    return "\n".join(lineas)


def main():
    doc = json.loads(JSON.read_text(encoding="utf-8"))
    errores = validar(doc)
    if errores:
        print("calendario-26-27.json tiene errores:\n  - " + "\n  - ".join(errores), file=sys.stderr)
        return 2
    bloque = "\n".join(fila(p, doc["temporada"]) for p in doc["planes"])

    pie = "\n".join(
        f'          <li data-hasta="{p["hasta"]}"><a href="/comunidad?utm_source=descubre-tu-clic&amp;utm_medium=pie_'
        f'{UTM.get(p["id"]) or sufijo_automatico(p["id"])}">{escape(p["titulo"])} · {escape(fecha_corta(p))}</a></li>'
        for p in doc["planes"])
    html = INDEX.read_text(encoding="utf-8")
    original = html
    a, b = html.find("<!-- pie-planes:inicio"), html.find("<!-- pie-planes:fin -->")
    if a >= 0 and b > a:
        a = html.index("-->", a) + 3
        html = html[:a] + "\n" + pie + "\n          " + html[b:]
    i, j = html.find(INICIO), html.find(FIN)
    if i < 0 or j < 0 or j < i:
        print("index.html no tiene los marcadores <!-- calendario:inicio … --> y <!-- calendario:fin -->", file=sys.stderr)
        return 2
    fin_marcador_inicio = html.index("-->", i) + len("-->")
    nuevo = html[:fin_marcador_inicio] + "\n" + bloque + "\n    " + html[j:]

    if "--check" in sys.argv[1:]:
        if nuevo == original:
            print("index.html está al día con calendario-26-27.json")
            return 0
        print("index.html NO está al día: ejecuta python3 scripts/calendario.py", file=sys.stderr)
        return 1
    if nuevo == original:
        print("index.html ya estaba al día (sin cambios)")
    else:
        INDEX.write_text(nuevo, encoding="utf-8")
        print(f"index.html: {len(doc['planes'])} filas del calendario regeneradas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
