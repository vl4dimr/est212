/* Calificación del examen en el navegador, sin clave a la vista.
   La página solo trae los sha-256 de las respuestas normalizadas; se compara el hash de
   lo que escribe el estudiante. El código de entrega mezcla nombre, código de alumno,
   nota e intento, y el profesor lo verifica en verificar.html con la misma función. */
(function (raiz) {
  const SAL = "est212-unidad1-2026";

  // Un número escrito como lo escriben aquí ("0,2787") → el texto que se hashea.
  // Probabilidades (|x| < 1) con tres decimales; lo demás con dos.
  function normalizar(texto) {
    const limpio = String(texto).trim().replace(",", ".").replace(/[^0-9.+-]/g, "");
    if (!limpio) return null;
    const x = Number(limpio);
    if (!Number.isFinite(x)) return null;
    const d = Math.abs(x) < 1 ? 3 : 2;
    const m = Math.pow(10, d);
    return (Math.round(x * m) / m).toFixed(d);
  }

  async function sha256(texto) {
    const datos = new TextEncoder().encode(texto);
    const buf = await crypto.subtle.digest("SHA-256", datos);
    return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, "0")).join("");
  }

  // El hash de un campo: la sal, el ejercicio, el campo y el valor normalizado.
  function hashCampo(ejercicio, campo, valor) {
    return sha256(SAL + "|" + ejercicio + "|" + campo + "|" + valor);
  }

  async function esCorrecto(ejercicio, campo, tipo, respuesta, hashes) {
    const valor = tipo === "num" ? normalizar(respuesta) : String(respuesta || "").trim();
    if (valor === null || valor === "") return false;
    const h = await hashCampo(ejercicio, campo, valor);
    return hashes.includes(h);
  }

  function limpiarNombre(nombre) {
    return String(nombre).trim().toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/\s+/g, " ");
  }

  // El código de entrega: NOTA-INTENTO-HASH8. El hash depende del nombre y del código del alumno.
  async function codigoEntrega(nombre, codigo, nota, intento) {
    const h = await sha256(SAL + "|" + limpiarNombre(nombre) + "|" + String(codigo).trim() + "|" + nota + "|" + intento);
    return nota + "-" + intento + "-" + h.slice(0, 8);
  }

  raiz.Calificar = { normalizar, sha256, hashCampo, esCorrecto, codigoEntrega, limpiarNombre, SAL };
})(typeof window !== "undefined" ? window : globalThis);
