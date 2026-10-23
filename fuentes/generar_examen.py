# -*- coding: utf-8 -*-
"""El examen de la Unidad I como página autocalificada para GitHub Pages.

    python fuentes/generar_examen.py      →  examen-unidad1/index.html

Los enunciados salen de Arquitectura/practica_unidad1/generar.py (la misma práctica en
Word). La página no lleva la clave: lleva los sha-256 de cada respuesta normalizada
(ver examen-unidad1/calificar.js) y compara. Al final da la nota sobre 20 y un código de
entrega NOTA-INTENTO-HASH que el estudiante pega en el aula virtual; el profesor lo
comprueba en examen-unidad1/verificar.html.
"""
import hashlib
import html
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ.parent / "practica_unidad1"))
import generar as g  # noqa: E402  (las respuestas numéricas viven ahí)

SAL = "est212-unidad1-2026"
CIERRE_ISO = "2026-10-23T08:50:00-05:00"      # hora de Lima
CIERRE_TXT = "8:50 a. m. del viernes 23"


def normalizar(x):
    """Igual que calificar.js: tres decimales si |x| < 1, dos si no; redondeo hacia arriba en .5."""
    d = 3 if abs(x) < 1 else 2
    q = Decimal(1).scaleb(-d)
    return str(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))


def hash_campo(ej, campo, valor):
    return hashlib.sha256(("%s|%s|%s|%s" % (SAL, ej, campo, valor)).encode("utf-8")).hexdigest()


def num(rotulo, *valores, unidad=""):
    return {"tipo": "num", "rotulo": rotulo, "unidad": unidad, "vals": list(valores)}


def mc(rotulo, opciones, correcta):
    return {"tipo": "mc", "rotulo": rotulo, "opciones": opciones, "correcta": correcta}


# Los campos que se califican, por ejercicio e inciso. Cada ejercicio vale 2 puntos,
# repartidos por igual entre sus campos. Los valores alternativos también se aceptan.
CAMPOS = [
    [("a", [mc("¿Por qué es una distribución de probabilidad?",
               ["Todas las probabilidades son ≥ 0 y suman 1", "Porque hay cuatro valores de X", "Porque la media sale entera"], 0)]),
     ("b", [num("P(X ≥ 2)", 0.7)]),
     ("c", [num("E(X)", g.e1), num("Var(X)", g.v1)])],
    [("a", [num("P(X = 5)", g.b2[5])]),
     ("b", [num("P(X ≥ 6)", sum(g.b2[6:]))]),
     ("c", [num("E(X)", 4.8, unidad="viviendas")])],
    [("a", [num("P(Y = 3)", g.g3)]),
     ("b", [num("P(Y ≤ 3)", g.g3a)]),
     ("c", [num("E(Y)", 4, unidad="lotes")])],
    [("a", [mc("¿Por qué no es binomial?",
               ["La población es chica y se saca sin reemplazo", "Porque hay más de dos resultados posibles", "Porque n es menor que 30"], 0)]),
     ("b", [num("P(X = 2)", g.h4)]),
     ("c", [num("P(X ≥ 1)", g.h4b), num("E(X)", 1.6)])],
    [("a", [num("P(2 adobe, 2 ladrillo, 1 otro)", g.m5)]),
     ("b", [num("Esperadas de adobe", 2.5), num("de ladrillo", 2.0), num("de otro material", 0.5)]),
     ("c", [mc("¿Qué se comprueba antes de usar la multinomial?",
               ["Que las p sumen 1 y las x sumen n", "Que n sea mayor que 30", "Que todas las p sean iguales"], 0)])],
    [("a", [num("P(X < 130)", g.n6a)]),
     ("b", [num("P(X > 200)", g.n6b)]),
     ("c", [num("P(150 < X < 180)", g.n6c)])],
    [("a", [num("Percentil 90", g.e7, 1.72, 1.7225, unidad="m")]),
     ("b", [num("Altura libre propuesta", 1.82, 1.8225, unidad="m")]),
     ("c", [num("P(X > 1,80)", g.p7c)])],
    [("a", [num("P(T < 4 °C)", g.t8a)]),
     ("b", [num("Noches del invierno bajo 4 °C", 90 * g.t8a, 5, 4.9, unidad="noches")]),
     ("c", [num("Temperatura de diseño", g.t8c, 4.8, unidad="°C")])],
    [("a", [num("μ", 18), num("σ", g.sg9, 3.55, 3.5)]),
     ("b", [num("P(X ≤ 24) con corrección", g.a9, 0.966, 0.967)]),
     ("c", [num("Kits para el 95 %", 24, unidad="kits")])],
    [("a", [mc("¿Qué distribución es?", ["Hipergeométrica", "Binomial", "Geométrica"], 0)]),
     ("b", [num("P(X = 2)", g.h10)]),
     ("c", [mc("Con 2 000 estudiantes, ¿qué distribución usaría?", ["Binomial", "Hipergeométrica", "Multinomial"], 0),
            num("P(X = 2) con esa distribución", g.b10)])],
]


def construir():
    ejercicios = []
    for i, ((rotulo, enunciado, preguntas, _), incisos) in enumerate(zip(g.EJERCICIOS, CAMPOS), start=1):
        campos = []
        n_campos = sum(len(c) for _, c in incisos)
        puntos = round(2.0 / n_campos, 4)
        for letra, lista in incisos:
            for k, c in enumerate(lista):
                nombre = "%s%d" % (letra, k)
                if c["tipo"] == "num":
                    hashes = sorted({hash_campo(i, nombre, normalizar(v)) for v in c["vals"]})
                    campos.append({"id": nombre, "inciso": letra, "tipo": "num", "rotulo": c["rotulo"],
                                   "unidad": c["unidad"], "puntos": puntos, "hashes": hashes})
                else:
                    hashes = [hash_campo(i, nombre, "op%d" % c["correcta"])]
                    campos.append({"id": nombre, "inciso": letra, "tipo": "mc", "rotulo": c["rotulo"],
                                   "opciones": c["opciones"], "puntos": puntos, "hashes": hashes})
        ejercicios.append({"n": i, "rotulo": rotulo, "enunciado": enunciado,
                           "preguntas": dict(zip("abc", preguntas)), "campos": campos})
    return ejercicios


PLANTILLA = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Examen de la Unidad I · Estadística Inferencial · Arquitectura</title>
<style>
  :root { --tinta:#1B1D21; --gris:#6B6E75; --linea:#DCD9D2; --papel:#F4F2ED; --ladrillo:#B4552F; --azul:#2E6F8F; --ambar:#D9A441; --ok:#2E7D5B; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:"Segoe UI", Arial, sans-serif; color:var(--tinta); background:var(--papel); font-size:16px; line-height:1.45; }
  header { background:#1E2A3D; color:#F0EEE8; padding:18px 16px; }
  header .in { max-width:900px; margin:0 auto; display:flex; gap:16px; align-items:center; }
  header img { width:46px; height:46px; }
  header .k { font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:var(--ambar); }
  header h1 { font-family:Georgia, serif; font-size:24px; margin:2px 0 0; font-weight:700; }
  main { max-width:900px; margin:0 auto; padding:16px; }
  .aviso { background:#fff; border:1px solid var(--linea); border-left:5px solid var(--ladrillo); padding:12px 16px; border-radius:6px; font-size:15px; color:var(--gris); }
  .datos { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:16px 0; }
  .datos label { font-size:13px; font-weight:600; display:block; margin-bottom:4px; }
  input[type=text] { width:100%; font:inherit; padding:9px 10px; border:1px solid var(--linea); border-radius:6px; background:#fff; }
  input[type=text]:focus { outline:2px solid var(--azul); border-color:transparent; }
  .ej { background:#fff; border:1px solid var(--linea); border-radius:8px; padding:16px 18px; margin:14px 0; }
  .ej h2 { font-family:Georgia, serif; font-size:18px; margin:0 0 6px; color:var(--ladrillo); }
  .ej p.en { margin:0 0 10px; }
  .inciso { padding:8px 0 4px; border-top:1px dashed var(--linea); }
  .inciso .q { font-size:15px; margin:0 0 8px; } .inciso .q b { color:var(--tinta); }
  .campo { display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin:6px 0; }
  .campo span.r { min-width:190px; font-size:14px; color:var(--gris); }
  .campo input[type=text] { width:150px; }
  .campo .u { font-size:13px; color:var(--gris); }
  .mc label { display:block; font-size:15px; padding:4px 0; cursor:pointer; }
  .mc input { margin-right:8px; }
  .campo.bien input, .mc.bien label { background:#E6F4EC; }
  .campo.mal input, .mc.mal label { background:#FBE9E2; }
  .marca { font-size:13px; margin-left:4px; font-weight:700; }
  .marca.bien { color:var(--ok); } .marca.mal { color:var(--ladrillo); }
  button { font:inherit; font-weight:700; background:var(--ladrillo); color:#fff; border:0; border-radius:8px; padding:13px 22px; cursor:pointer; font-size:17px; }
  button[disabled] { background:#aaa; cursor:not-allowed; }
  #resultado { display:none; background:#1E2A3D; color:#F0EEE8; border-radius:8px; padding:18px 20px; margin:16px 0; }
  #resultado .nota { font-family:Georgia, serif; font-size:40px; line-height:1; }
  #resultado code { display:inline-block; font-size:22px; background:#0f1826; padding:8px 14px; border-radius:6px; letter-spacing:.06em; margin:8px 0; }
  #resultado .copiar { background:var(--azul); font-size:15px; padding:9px 14px; margin-left:8px; }
  #resultado small { color:#C9CFDA; display:block; margin-top:8px; }
  footer { max-width:900px; margin:20px auto; padding:0 16px 30px; color:var(--gris); font-size:13px; }
  @media (max-width:600px) { .datos { grid-template-columns:1fr; } .campo span.r { min-width:100%; } }
</style>
</head>
<body>
<header><div class="in">
  <img src="../marca.png" alt="">
  <div><div class="k">Estadística Inferencial · Arquitectura y Urbanismo · UNA Puno · 2026-II</div>
  <h1>Examen de la Unidad I · distribuciones discretas y normal</h1></div>
</div></header>
<main>
  <div class="aviso">
    Diez ejercicios, 2 puntos cada uno, nota sobre 20. Los datos son ilustrativos. Resuelvan en el cuaderno o en Excel
    y escriban aquí solo el resultado: los números con coma o con punto (0,2787 o 0.2787), las probabilidades con
    cuatro decimales. <b>Hay un solo intento</b> y el examen <b>cierra a las __CIERRE_TXT__</b>: revisen todo antes de apretar <b>Calificar</b>. La página les da la nota y un
    <b>código de entrega</b> que mandan al profesor junto con la foto de su resolución. Sin la resolución, el código no vale.
  </div>
  <div class="datos">
    <div><label for="nombre">Apellidos y nombres</label><input type="text" id="nombre" autocomplete="name" placeholder="Quispe Mamani, Rosa"></div>
    <div><label for="codigo">Código de estudiante</label><input type="text" id="codigo" inputmode="numeric" placeholder="241234"></div>
  </div>
  <form id="examen" autocomplete="off">__EJERCICIOS__
    <p><button type="submit" id="btn">Calificar y generar mi código</button></p>
  </form>
  <div id="resultado"></div>
</main>
<footer>Los resultados se comparan sin mostrar la clave. Un solo intento por código de estudiante. Docente: M. V. Mamani Calisaya.</footer>
<script src="calificar.js"></script>
<script>
  const EJ = __DATOS__;
  const CIERRE = new Date("__CIERRE__");
  const cerrado = () => Date.now() >= CIERRE.getTime();
  const form = document.getElementById("examen");
  const btn = document.getElementById("btn");
  const campoNombre = document.getElementById("nombre");
  const campoCodigo = document.getElementById("codigo");
  const claveDe = (codigo) => "est212u1_" + codigo.trim();

  function leerGuardado(codigo) {
    try { const t = localStorage.getItem(claveDe(codigo)); return t ? JSON.parse(t) : null; } catch (e) { return null; }
  }

  function bloquear() {
    for (const el of form.querySelectorAll("input")) el.disabled = true;
    campoNombre.disabled = true; campoCodigo.disabled = true;
    btn.disabled = true; btn.textContent = "Examen entregado";
  }

  function mostrar(g, nuevo) {
    const r = document.getElementById("resultado");
    const linea = g.nombre + " · " + g.codigo + " · " + String(g.nota).replace(".", ",") + "/20 · " + g.cod;
    r.style.display = "block";
    r.innerHTML = '<div class="nota">' + String(g.nota).replace(".", ",") + ' <span style="font-size:18px">/ 20</span></div>' +
      '<div>' + g.nombre + ' · ' + g.codigo + ' · entregado el ' + g.fecha + '</div>' +
      '<div>Su código de entrega: <code id="cod">' + g.cod + '</code></div>' +
      '<div style="margin-top:8px"><button type="button" class="copiar" id="copiar">Copiar la línea</button> <a class="copiar" id="wa" style="display:inline-block;color:#fff;text-decoration:none;border-radius:8px;font-weight:700" target="_blank" rel="noopener">Enviar por WhatsApp</a></div>' +
      '<small>' + (nuevo ? "Este fue su único intento. " : "Este código ya se entregó con este código de estudiante. ") +
      'Manden la línea al profesor por WhatsApp o péguenla en la tarea del aula virtual, con la foto de su resolución.</small>';
    document.getElementById("copiar").onclick = () => { navigator.clipboard.writeText(linea).then(() => alert("Copiado.")); };
    document.getElementById("wa").href = "https://wa.me/?text=" + encodeURIComponent("Examen Unidad I · " + linea);
    if (g.marcas) for (const [id, ok] of Object.entries(g.marcas)) pintar(id, ok);
    bloquear();
    r.scrollIntoView({ behavior: "smooth" });
  }

  function pintar(id, ok) {
    const caja = document.getElementById(id);
    if (!caja) return;
    caja.classList.remove("bien", "mal"); caja.classList.add(ok ? "bien" : "mal");
    let m = caja.querySelector(".marca"); if (!m) { m = document.createElement("span"); m.className = "marca"; caja.appendChild(m); }
    m.className = "marca " + (ok ? "bien" : "mal"); m.textContent = ok ? "✓" : "✗";
  }

  if (cerrado()) { bloquear(); btn.textContent = "Examen cerrado a las __CIERRE_TXT__"; }
  setInterval(() => { if (cerrado() && !btn.disabled) { bloquear(); btn.textContent = "Examen cerrado a las __CIERRE_TXT__"; } }, 15000);

  // Si ya entregó con ese código en este navegador, se le muestra su resultado y no puede volver a intentar.
  campoCodigo.addEventListener("change", () => {
    const g = leerGuardado(campoCodigo.value);
    if (g) { campoNombre.value = g.nombre; mostrar(g, false); }
  });

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    if (cerrado()) { alert("El examen cerró a las __CIERRE_TXT__. Ya no se reciben entregas."); bloquear(); btn.textContent = "Examen cerrado"; return; }
    const nombre = campoNombre.value.trim();
    const codigo = campoCodigo.value.trim();
    if (nombre.length < 5 || codigo.length < 4) { alert("Escriban sus apellidos y nombres y su código de estudiante."); return; }
    const previo = leerGuardado(codigo);
    if (previo) { mostrar(previo, false); return; }
    const vacios = EJ.reduce((n, e) => n + e.campos.filter((c) => {
      if (c.tipo === "num") return !((form.elements["e" + e.n + "_" + c.id] || {}).value || "").trim();
      return !form.querySelector('input[name="e' + e.n + '_' + c.id + '"]:checked');
    }).length, 0);
    const aviso = "Solo hay UN intento. Después de calificar no se puede cambiar nada." + (vacios ? " Tienen " + vacios + " casilla(s) en blanco." : "") + " ¿Entregan ahora?";
    if (!confirm(aviso)) return;
    btn.disabled = true;
    let puntos = 0; const marcas = {};
    for (const e of EJ) {
      for (const c of e.campos) {
        let resp = "";
        if (c.tipo === "num") resp = (form.elements["e" + e.n + "_" + c.id] || {}).value || "";
        else { const el = form.querySelector('input[name="e' + e.n + '_' + c.id + '"]:checked'); resp = el ? el.value : ""; }
        const ok = await Calificar.esCorrecto(e.n, c.id, c.tipo, resp, c.hashes);
        if (ok) puntos += c.puntos;
        marcas["c_" + e.n + "_" + c.id] = ok;
      }
    }
    const nota = Math.round(puntos * 2) / 2;      // a medio punto
    const cod = await Calificar.codigoEntrega(nombre, codigo, nota, 1);
    const g = { nombre, codigo, nota, cod, fecha: new Date().toLocaleString("es-PE"), marcas };
    try { localStorage.setItem(claveDe(codigo), JSON.stringify(g)); } catch (e) {}
    mostrar(g, true);
  });
</script>
</body>
</html>
"""


def html_ejercicios(ejercicios):
    partes = []
    for e in ejercicios:
        partes.append('\n    <section class="ej"><h2>%d · %s</h2><p class="en">%s</p>' % (e["n"], html.escape(e["rotulo"]), html.escape(e["enunciado"])))
        for letra in "abc":
            campos = [c for c in e["campos"] if c["inciso"] == letra]
            partes.append('<div class="inciso"><p class="q"><b>%s)</b> %s</p>' % (letra, html.escape(e["preguntas"][letra])))
            for c in campos:
                nombre = "e%d_%s" % (e["n"], c["id"])
                if c["tipo"] == "num":
                    partes.append('<div class="campo" id="c_%d_%s"><span class="r">%s</span><input type="text" name="%s" inputmode="decimal">'
                                  '<span class="u">%s</span></div>' % (e["n"], c["id"], html.escape(c["rotulo"]), nombre, html.escape(c["unidad"])))
                else:
                    ops = "".join('<label><input type="radio" name="%s" value="op%d">%s</label>' % (nombre, k, html.escape(o)) for k, o in enumerate(c["opciones"]))
                    partes.append('<div class="mc" id="c_%d_%s">%s</div>' % (e["n"], c["id"], ops))
            partes.append("</div>")
        partes.append("</section>")
    return "".join(partes)


def main():
    ejercicios = construir()
    publico = [{"n": e["n"], "campos": [{"id": c["id"], "tipo": c["tipo"], "puntos": c["puntos"], "hashes": c["hashes"]} for c in e["campos"]]}
               for e in ejercicios]
    pagina = PLANTILLA.replace("__EJERCICIOS__", html_ejercicios(ejercicios)).replace("__DATOS__", json.dumps(publico, ensure_ascii=False)).replace("__CIERRE__", CIERRE_ISO).replace("__CIERRE_TXT__", CIERRE_TXT)
    destino = RAIZ / "examen-unidad1" / "index.html"
    destino.write_text(pagina, encoding="utf-8")
    # Las respuestas en claro, solo para el docente: no se publican (está en .gitignore).
    claro = [{"n": e["n"], "campos": [{"id": c["id"], "rotulo": c["rotulo"], "vals": c.get("vals")} for c in e["campos"]]} for e in ejercicios]
    (RAIZ / "fuentes" / "respuestas_en_claro.json").write_text(json.dumps(
        [{"n": e["n"], "campos": [(c["id"], c["rotulo"], [normalizar(v) for v in CAMPOS[e["n"] - 1][["abc".index(c["inciso"])][0]][1][int(c["id"][1:])]["vals"]] if c["tipo"] == "num" else "op%d" % CAMPOS[e["n"] - 1]["abc".index(c["inciso"])][1][int(c["id"][1:])]["correcta"]) for c in e["campos"]]} for e in ejercicios],
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(destino.name, "·", sum(len(e["campos"]) for e in ejercicios), "campos")


if __name__ == "__main__":
    main()
