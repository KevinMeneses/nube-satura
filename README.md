<!-- en -->
# Nube Satura

A free saturator for [REAPER](https://www.reaper.fm), written as a JSFX (macOS / Windows / Linux), part of the
[Nube plugins](https://github.com/KevinMeneses/nube-plugins).

Three modes: **sub harmonics** (saturates only the low end and adds the harmonics in parallel without the
fundamental, so an 808 is heard on phone and laptop speakers while the sub stays untouched), **saturate all**
(with dry/wet mix) and **old radio / lo-fi** (band-pass, nasal, saturation, static, wow, width, bit depth, sample-rate
reduction and a crunchy exciter, with an automatable amount). Four curves: soft (tanh), tape, tube (asymmetric, even
harmonics) and hard, with 4x or 8x internal oversampling (24 samples of latency). 23 presets for trap, drill,
reggaeton and dancehall. ~5.5 % CPU at 4x, ~12 % at 8x.

It reproduces the two JSFX it replaces with oversampling off: `claude_sub_sat` (long kick of "Pies en la arena") to
−175 dB, and `claude_radio` (Outro 2 tests of "Nube baja") except for the −80 dB static the original adds even at its
minimum.

**Install** — with [ReaPack](https://reapack.com): *Extensions → ReaPack → Import repositories*, paste
`https://github.com/KevinMeneses/nube-plugins/raw/main/index.xml`, then install **Nube Satura**. Or copy
`nube_satura.jsfx` into `REAPER/Effects/Nube Satura/` (on macOS `./install.sh` links it). It shows up as
**JS: Nube Satura**. The interface is in Spanish.

**How it was made** — designed and built with [Claude Code](https://claude.com/claude-code). Since an AI can't
listen, every feature is verified by rendering test cases inside REAPER and comparing them with the original JSFX,
with a numpy model of the same algorithm and with theory, and the aliasing is measured (`tests/run.sh`).

**License** — GPL-3.0-or-later (see `LICENSE`).

---

## Español
Saturador para REAPER (JSFX, macOS/Windows/Linux), hermano de [Nube Clip](https://github.com/KevinMeneses/nube-clip)
y los demás Nube. Une dos JSFX que usé en mis canciones: `claude_sub_sat` (armónicos del sub en paralelo, en el kick
largo de "Pies en la arena") y `claude_radio` (radio vieja / lo-fi, en las pruebas del Outro 2 de "Nube baja"). Con el
oversampling apagado da **exactamente** lo mismo que ellos.

### Modos
- **Armónicos del sub**: toma lo de abajo del *Corte* (pasa-bajos Butterworth), lo satura, le quita la fundamental con un
  *Pasa-altos* (12 dB/oct como el original, o 24 dB/oct Butterworth de 4º orden) y suma esos armónicos a la señal
  original con el volumen de *Armónicos*. La señal original no se toca: el sub queda igual y se le agrega lo que un
  parlante chico sí puede reproducir. Ojo: la saturación se normaliza por el empuje (como en `claude_sub_sat`), así
  que el *Empuje* cambia el carácter (más armónicos altos) y el volumen de los armónicos se ajusta con *Armónicos*.
- **Saturar todo**: toda la señal pasa por la curva, con *Mezcla* seca/saturada (saturación en paralelo). El nivel bajo
  queda igual (pendiente 1); los picos se redondean. Las curvas asimétricas llevan un quita-continua de 10 Hz.
- **Radio vieja**: la cadena de `claude_radio` (vaivén de afinación a 4.5 Hz, ancho, pasa-banda de 4º orden, nasal en
  1.6 kHz, saturación, lo-fi de bits y retención de muestras, "crujiente" y estática filtrada). La *Cantidad* reemplaza a
  "Desde / Rampa" del original: automatízala para que la canción se aleje de a poco (0 = señal original exacta).

### Curvas (pendiente 1 en el centro, satura en ±1)
| Tipo | Curva | Carácter |
|---|---|---|
| Suave | tanh | la de los originales; impares, la *Asimetría* agrega pares |
| Cinta | x / √(1 + x²) | comprime antes y redondea más suave |
| Válvula | la de cinta corrida 0.35 | asimétrica de por sí: 2º armónico desde poco empuje |
| Duro | x / (1 + x⁶)^(1/6) | recorte casi duro, sin esquina |

El "duro" no tiene esquina a propósito: un recorte duro de verdad genera armónicos que bajan tan lento que aunque se
sature a 4x u 8x vuelven plegados (medido en el prototipo: −47 dB a 7 kHz con +9 dB y 4x, contra −107 dB con esta curva).

### Oversampling
4x u 8x propio (sinc con ventana de Kaiser, 97 / 193 coeficientes: plano hasta 20 kHz, −64 dB desde 28 kHz). La parte
lineal de la señal pasa intacta y solo el residuo de la curva se filtra y se baja. Latencia 24 muestras en los dos
(REAPER la compensa). El lo-fi de muestreo y bits va después, sin oversampling: su aliasing es a propósito.

## Instalar

```sh
./install.sh
```

Crea un enlace en `~/Library/Application Support/REAPER/Effects/Nube Satura/`. En REAPER aparece como **JS: Nube Satura**.

## Cómo se usa

Elige el modo y el tipo, sube el **Empuje** y escucha con **Escuchar cambios** (suena solo lo que el plugin agrega).
En un 808: modo *Armónicos del sub*, Pasa-altos un poco arriba de la nota más grave del 808, 24 dB/oct, y sube
*Armónicos* hasta que se oiga en el celular.

| Acción | Cómo |
|---|---|
| Empuje | Perilla o **arrastra arriba/abajo en la gráfica** |
| Perillas | Arrastra arriba/abajo o usa la rueda; **Shift** = fino; **doble clic** = valor por defecto |
| Oversampling | Botón de arriba: sin / 4x / 8x |
| Presets | Botón *Presets* o clic derecho en la gráfica |
| Reiniciar máximos | Clic en los medidores |

## Presets

| Preset | Qué hace |
|---|---|
| Nube baja - radio Outro 2 (X2) | Radio 450 Hz–3.2 kHz, nasal +4, empuje 6, estática −40, vaivén 12 ct, ancho 30 %, salida +1 (la prueba X2) |
| Nube baja - radio sutil (X4) | 100 Hz–8 kHz, nasal +1, empuje 2, estática −55, vaivén 4 ct, ancho 75 %, salida +0.7 (X4) |
| Nube baja - lo-fi Outro 2 (X8c) | Sin banda, 9.5 bits, muestreo /2.5, estática −52.5 (X8c, sin la cinta de vinilo, que era otra pista) |
| Pies en la arena - kick largo | Exactamente `claude_sub_sat` como está en el kick largo (150 Hz, +6, asimetría 0.4, 90 Hz) |
| 808 - que se oiga en el celular | Válvula +12, corte 120, pasa-altos 100 Hz 24 dB/oct, armónicos +6 |
| 808 drill - armonicos fuertes | Duro +12, corte 150, pasa-altos 110, armónicos +6 |
| 808 reggaeton / dembow - calido | Válvula +9, corte 140, pasa-altos 90, armónicos −2 |
| Bajo / reese - presencia | Cinta +9, corte 250, pasa-altos 150 |
| Bus de bajos (kick + 808) | Cinta +8, corte 130, pasa-altos 100, armónicos −1 |
| Master - cinta suave | Saturar todo, cinta +3 |
| Master lo-fi / chill | Cinta +8, mezcla 60 % |
| Voz rap - valvula | Válvula +6, mezcla 40 % |
| Voz drill - agresiva | Duro +12, mezcla 30 % |
| Bus de bateria - cinta | Cinta +6, mezcla 70 % |
| Snare / clap - crunch | Duro +9, mezcla 50 % |
| 808 rage - distorsion total | Duro +18, todo saturado, salida −3 |
| Melodia - calidez | Válvula +4 |
| Radio vieja (AM) | 500 Hz–3 kHz, nasal +5, empuje 9, estática −38, vaivén 15 ct, mono |
| Telefono | 300 Hz–3.4 kHz, duro +12, mono, sin estática |
| Lo-fi - cassette | Agudos hasta 9 kHz, cinta +4, estática −55, vaivén 8 ct |
| Lo-fi - sampler 12 bits | 12 bits, muestreo /1.75 (27 kHz) |
| Lo-fi - crujiente | El excitador de X6b: agudos desde 3 kHz saturados y sumados a −10, estática −52 |
| Por defecto | Los valores por defecto de `claude_sub_sat` (y de `claude_radio` en el modo radio), 4x |

## Pruebas

`tests/run.sh` (REAPER + Python con numpy, scipy y soundfile):

- **Igual a los JSFX originales** (sin oversampling): `claude_sub_sat` por defecto da un archivo idéntico con 808 reales
  y −175 dB de diferencia máxima con música (redondeo); `claude_radio` (por defecto, X4 y lo-fi X8c + crujiente) difiere solo en el ruido de −80 dB que el
  original suma con la estática al mínimo (Nube Satura ahí la apaga); la estática a −40 tiene el mismo nivel (±0.3 dB)
  y espectro.
- **Con oversampling, contra los originales**: preset "Pies en la arena" a 4x −121 dB, sub a 8x −123 dB, radio a 4x
  −65 dB (otra vez el ruido de −80 dB del original).
- **Contra un modelo en numpy** del mismo algoritmo (`tests/proto.py`): 50 renders (los cuatro tipos en los tres modos,
  4x y 8x, lo-fi, cantidad parcial, escuchar cambios y los presets sin estática), peor diferencia −105 dB.
- **Aliasing** (tono de 7019 Hz a −6 dBFS en *Saturar todo*, energía que no es armónico entre 20 Hz y 20 kHz, bajo la
  fundamental):

  | +9 dB | sin OS | 4x | 8x | +18 dB con 8x |
  |---|---|---|---|---|
  | Suave | −35.8 | −120.5 | −118.2 | −91.4 |
  | Cinta | −32.0 | −113.7 | −111.8 | −91.0 |
  | Válvula | −27.2 | −103.0 | −102.4 | −90.4 |
  | Duro | −39.3 | −106.9 | −107.3 | −87.7 |

  En música (premaster de Nube baja, duro +12 dB) contra el mismo algoritmo a 32x: aliasing −81 dB bajo la señal sin
  oversampling, −127 dB con 4x. Con 3 kHz y 4x, todas las curvas bajo −90 dB.
- **La fundamental no se toca**: seno de 50 Hz con +12 dB de empuje: la fundamental cambia −0.11 dB (24 dB/oct);
  armónicos 2º −27, 3º −22 dB. Con 808 reales (F#1 y A1) y el preset "808 - que se oiga en el celular": +6.4 dB por
  encima de 150 Hz (lo que suena en un celular), −0.2 dB bajo 80 Hz.
- Latencia compensada en los tres modos (muestra 48000 exacta), radio con cantidad 0 y mezcla 0 = entrada exacta,
  picos y LUFS de los 23 presets.
- `tests/perf.lua`: CPU (10 instancias, 60 s): 0.3 % sin oversampling, 5.5–5.8 % con 4x, 11.7–13 % con 8x.
- `tests/ui_test.py`: pruebas de la interfaz con el mouse (modos, tipos, perillas, gráfica, botones, menú de presets).

Los casos con música usan grabaciones propias que no están en el repo (`tests/signals/`, las crea
`tests/make_signals.py` desde el premaster de Nube baja y la librería de 808); sin ellas esos casos no se pueden correr.

## Detalles técnicos

- Cadena: [sub: pasa-bajos → empuje] / [todo: empuje] / [radio: vaivén → ancho → pasa-banda → nasal → empuje] →
  curva (directa o a 4x/8x) → [sub: pasa-altos → suma a la original] / [todo: mezcla] / [radio: bits, retención,
  crujiente, estática, cantidad] → salida.
- Oversampling: r = u − curva(u) con u = la señal subida a L x (fase 0 = la muestra misma; las demás fases con 24
  coeficientes); r se filtra y se baja y la salida es la señal retrasada 24 muestras menos r.
- REAPER vuelve a correr `@init` al dar play o renderizar sin borrar las variables: el estado del audio se pone a cero
  ahí, como en `claude_radio`.
- La retención del lo-fi con factores que no son exactos en binario (2.3, 3.3) depende del redondeo en los empates:
  igual que el original; en las pruebas se usan factores exactos (2.5, 3.25, 1.75).
- La gráfica corre en otro hilo: el audio y la interfaz tienen sus propias copias de la curva (`shp` / `shp_ui`).
