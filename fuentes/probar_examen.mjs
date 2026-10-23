// Prueba la calificación sin navegador: carga calificar.js y los hashes de index.html,
// y comprueba que las respuestas en claro (fuentes/respuestas_en_claro.json) dan 20/20,
// que una respuesta cambiada no pasa, y que el código de entrega se verifica.
//   node fuentes/probar_examen.mjs
import {readFileSync} from 'node:fs';
import {dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';

const RAIZ = dirname(dirname(fileURLToPath(import.meta.url)));
const ctx = {crypto: globalThis.crypto, TextEncoder, console};
vm.createContext(ctx);
vm.runInContext(readFileSync(join(RAIZ, 'examen-unidad1', 'calificar.js'), 'utf8'), ctx);
const C = ctx.Calificar;

const html = readFileSync(join(RAIZ, 'examen-unidad1', 'index.html'), 'utf8');
const EJ = JSON.parse(html.match(/const EJ = (\[.*?\]);\r?\n/s)[1]);
const claro = JSON.parse(readFileSync(join(RAIZ, 'fuentes', 'respuestas_en_claro.json'), 'utf8'));

let puntos = 0, total = 0, fallas = [];
for (const e of EJ) {
  const resp = Object.fromEntries(claro.find(x => x.n === e.n).campos.map(([id, , v]) => [id, v]));
  for (const c of e.campos) {
    total += c.puntos;
    const v = resp[c.id];
    const entrada = c.tipo === 'num' ? String(v[0]).replace('.', ',') : v;   // como lo escribiría un alumno, con coma
    const ok = await C.esCorrecto(e.n, c.id, c.tipo, entrada, c.hashes);
    if (ok) puntos += c.puntos; else fallas.push(`${e.n}${c.id} (${entrada})`);
    // y una respuesta equivocada no debe pasar
    const mal = c.tipo === 'num' ? String(Number(v[0]) + 0.37) : 'op9';
    if (await C.esCorrecto(e.n, c.id, c.tipo, mal, c.hashes)) fallas.push(`${e.n}${c.id} acepta ${mal}`);
  }
}
console.log(`puntos ${puntos.toFixed(2)} de ${total.toFixed(2)} · fallas: ${fallas.length ? fallas.join(', ') : 'ninguna'}`);
// variantes que deben aceptarse
const pruebas = [[7, 'a0', '1,72'], [8, 'b0', '5'], [9, 'a1', '3,55'], [2, 'a0', '0.2787'], [6, 'a0', '0,0668']];
for (const [n, id, v] of pruebas) {
  const c = EJ.find(e => e.n === n).campos.find(c => c.id === id);
  console.log(`${n}${id} "${v}" →`, await C.esCorrecto(n, id, 'num', v, c.hashes) ? 'acepta' : 'RECHAZA');
}
const cod = await C.codigoEntrega('Quispe Mamani, Rosa', '241234', 17.5, 1);
const cod2 = await C.codigoEntrega('quispe mamani, rosa ', ' 241234', 17.5, 1);
console.log('código', cod, cod === cod2 ? '· estable con mayúsculas y espacios' : '· INESTABLE');
if (fallas.length) process.exit(1);
