"""Compara los renders de tests/out con los JSFX originales, con el modelo en numpy (mismo algoritmo) y con la
teoria; mide el aliasing. Sale con codigo 1 si algo falla."""
import numpy as np, soundfile as sf, pathlib, sys
from scipy import signal as sg
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from proto import model, preset, saturate, NAMES, SR
D = pathlib.Path(__file__).parent / "out"; S = pathlib.Path(__file__).parent / "signals"
def a(db): return 10 ** (db / 20)
def db(x): return 20 * np.log10(np.abs(x) + 1e-15)
def load(name, d=D):
    x, sr = sf.read(d / f"{name}.wav", always_2d=True); assert sr == SR; return x
def has(name): return (D / f"{name}.wav").exists()
def sig(name): return load(name, S)
def tone(x, f, t0=0.5, t1=1.5):
    seg = x[int(t0 * SR):int(t1 * SR)]; tt = np.arange(int(t0 * SR), int(t1 * SR)) / SR
    M = np.stack([np.sin(2 * np.pi * f * tt), np.cos(2 * np.pi * f * tt)], 1)
    c, *_ = np.linalg.lstsq(M, seg, rcond=None); return db(np.hypot(*c))
def rel(e, r): return 10 * np.log10((e ** 2).mean() / (r ** 2).mean() + 1e-30)
def rms_db(x): return 10 * np.log10((x ** 2).mean() + 1e-30)
def lufs(x):
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1, -2, 1], [1, -1.99004745483398, 0.99007225036621]
    y = sg.lfilter(b2, a2, sg.lfilter(b1, a1, x, axis=0), axis=0)
    n, h = int(0.4 * SR), int(0.1 * SR)
    z = np.array([np.mean(y[i:i + n] ** 2, 0).sum() for i in range(0, len(y) - n + 1, h)])
    l = -0.691 + 10 * np.log10(z + 1e-20); z = z[l > -70]
    r_ = -0.691 + 10 * np.log10(z.mean()) - 10
    return -0.691 + 10 * np.log10(z[-0.691 + 10 * np.log10(z) > r_].mean())
def alias(x, f0):
    """energia que no es armonico de f0 (20 Hz - 20 kHz) relativa a la fundamental, en dB; y la linea mas alta"""
    seg = x[SR // 2:SR // 2 + SR, 0]; X = np.abs(np.fft.rfft(seg * np.blackman(SR))) ** 2; fr = np.fft.rfftfreq(SR, 1 / SR)
    harm = np.zeros(len(fr), bool)
    for k in range(1, 60): harm |= np.abs(fr - k * f0) < 4
    band = (fr > 20) & (fr < 20000) & ~harm; ref = X[np.abs(fr - f0) < 4].sum()
    return 10 * np.log10(X[band].sum() / ref + 1e-30), 10 * np.log10(X[band].max() / ref + 1e-30)

fails = 0
def scalar(name, got, want, tol):
    global fails
    ok = abs(got - want) <= tol; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:60s} {got:+9.2f}   (esperado {want:+.2f} ± {tol})")
def inrange(name, got, lo, hi):
    global fails
    ok = lo <= got <= hi; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:60s} {got:+9.2f}   (entre {lo:+.2f} y {hi:+.2f})")

for p in sorted(D.glob("*.wav")):
    if p.stem.startswith(("perf_", "_")): continue
    x = load(p.stem)
    if not np.all(np.isfinite(x)) or np.abs(x).max() > 4:
        fails += 1; print("MAL", p.stem, "tiene NaN o pasa de +12 dBFS")

print("\n-- igual que los JSFX originales (sin oversampling)")
for name, what in (("eq_sub", "claude_sub_sat por defecto, musica"), ("eq_sub808", "claude_sub_sat por defecto, 808")):
    if has(name): inrange(f"{what}: diferencia maxima (dB)", db(np.abs(load(name) - load(name + "_ref")).max()), -400, -120)
# radio: el original con estatica en -80 igual suma un ruido de -80 dB (Nube Satura en -80 la apaga): esa es toda la diferencia
for name, what in (("eq_radio", "claude_radio por defecto (desde 0)"), ("eq_x4", "claude_radio X4 de Nube baja"),
                   ("eq_lofi", "claude_radio lo-fi X8c + crujiente")):
    if not has(name): continue
    y, r = load(name), load(name + "_ref"); e = y - r
    inrange(f"{what}: diferencia maxima (dBFS)", db(np.abs(e).max()), -400, -70)
    print(f"    residuo {rel(e, r):.1f} dB bajo la senal (solo el ruido de -80 dB del original)")
if has("static"):
    y, r = load("static"), load("static_ref")
    scalar("estatica -40: mismo nivel que claude_radio (dB)", rms_db(y) - rms_db(r), 0, 0.3)
    f, py = sg.welch(y[:, 0], SR, nperseg=4096); _, pr = sg.welch(r[:, 0], SR, nperseg=4096); b = (f > 300) & (f < 5000)
    inrange("estatica: mismo espectro (desvio medio dB, 300 Hz-5 kHz)", np.mean(np.abs(10 * np.log10(py[b] / pr[b]))), 0, 0.6)

print("\n-- con oversampling, contra los originales (alineados: la latencia la compensa REAPER)")
for name, ref, what in (("os_sub", "eq_sub_ref", "preset 'Pies en la arena' 4x contra claude_sub_sat"),
                        ("os8_sub", "eq_sub808_ref", "sub 8x contra claude_sub_sat (808)"),
                        ("os_radio", "eq_radio_ref", "radio 4x contra claude_radio")):
    if has(name) and has(ref):
        y, r = load(name), load(ref); n = min(len(y), len(r)) - 100
        inrange(f"{what}: residuo (dB bajo la senal)", rel((y - r)[SR // 10:n], r[SR // 10:n]), -400, -60)

print("\n-- contra el modelo en numpy (mismo algoritmo, muestra a muestra)")
CASEP = {"eq_sub": ({22: 0}, "music"), "eq_sub808": ({22: 0}, "808"), "eq_radio": ({1: 2, 4: 0, 15: -80, 22: 0}, "music"),
         "os_sub": (preset(4), "music"), "os8_sub": ({22: 2}, "808"), "os_radio": ({1: 2, 4: 0, 15: -80}, "music"),
         "m_todo_off_valv": ({1: 1, 2: 2, 3: 9, 22: 0}, "music"), "m_todo8": ({1: 1, 2: 3, 3: 18, 22: 2}, "music"),
         "m_radio_os": ({1: 2, 15: -80, 4: 0.3, 2: 1}, "music"),
         "m_lofi_os8": ({1: 2, 15: -80, 22: 2, 18: 8, 19: 3.25, 20: -20, 12: 20, 13: 20000}, "music"),
         "m_amt50": ({1: 2, 15: -80, 11: 50}, "music"), "m_delta": ({23: 1, 7: 1, 3: 12}, "music"),
         "fund_24": ({3: 12, 4: 0.3, 5: 120, 6: 100, 7: 1}, "s50_m6")}
for t in range(4):
    CASEP[f"m_sub_t{t}"] = ({2: t, 7: 1, 3: 12}, "808"); CASEP[f"m_todo_t{t}"] = ({1: 1, 2: t, 3: 12}, "music")
    for o in range(3): CASEP[f"alias_7019_t{t}_os{o}"] = ({1: 1, 2: t, 3: 9, 4: 0, 22: o}, "s7019_m6")
for k in range(1, 24):
    if preset(k)[15] <= -79.9 or preset(k)[1] != 2: CASEP[f"preset{k}"] = (preset(k), "music")
worst, nm, wname = -400, 0, ""
for name, (p, src) in CASEP.items():
    if not has(name): continue
    y = load(name); m = model(sig(src), p); e = db(np.abs(y - m)[:-100].max()); nm += 1
    if e > worst: worst, wname = e, name
    if e > -100: fails += 1; print(f"MAL {name}: difiere del modelo {e:.1f} dB")
print(f"OK  {nm} renders contra el modelo: peor diferencia {worst:.1f} dB ({wname})" if worst <= -100 else "")

print("\n-- aliasing (tono de 7019 Hz a -6 dBFS, saturar todo; dB bajo la fundamental, 20 Hz-20 kHz)")
TN = ["suave", "cinta", "valvula", "duro"]
print(f"    {'':10s} {'sin OS':>16s} {'4x':>16s} {'8x':>16s}   {'+18 dB con 8x':>16s}")
for t in range(4):
    r = [alias(load(f"alias_7019_t{t}_os{o}"), 7019) if has(f"alias_7019_t{t}_os{o}") else (np.nan, np.nan) for o in range(3)]
    r18 = alias(load(f"alias18_7019_t{t}_os2"), 7019) if has(f"alias18_7019_t{t}_os2") else (np.nan, np.nan)
    print(f"    {TN[t]:10s}" + "".join(f" {v[0]:7.1f} ({v[1]:6.1f})" for v in r) + f"   {r18[0]:7.1f} ({r18[1]:6.1f})")
    inrange(f"{TN[t]}, +9 dB, 4x: aliasing total (dB)", r[1][0], -400, -80)
    inrange(f"{TN[t]}, +9 dB: el 4x lo baja (dB)", r[0][0] - r[1][0], 30, 400)
    inrange(f"{TN[t]}, +18 dB, 8x: aliasing total (dB)", r18[0], -400, -70)
    if has(f"alias_3001_t{t}_os1"): inrange(f"{TN[t]}, 3 kHz +9 dB, 4x: aliasing total (dB)", alias(load(f"alias_3001_t{t}_os1"), 3001)[0], -400, -90)
print("    (entre parentesis: la linea plegada mas alta; el umbral de audicion bajo un tono a -6 dBFS anda por -90 a -100 dB)")
if has("alias_music_os") and has("alias_music_off"):
    # referencia sin aliasing: el mismo algoritmo con oversampling 32x (8 s); la diferencia con el render es el aliasing
    x = sig("music")[:8 * SR]; g = a(12); ref = saturate(g * x, 3, 0.0, 32) / g
    ref = np.concatenate([ref[24:], np.zeros((24, 2))])
    b = sg.butter(8, 20000, fs=SR, output="sos")
    for name in ("alias_music_off", "alias_music_os"):
        y = load(name)[:8 * SR]; e = sg.sosfiltfilt(b, (y - ref)[SR // 10:-SR // 10], axis=0)
        print(f"    musica, duro +12 dB, {'sin OS' if name.endswith('off') else '4x    '}: aliasing {rel(e, ref[SR // 10:-SR // 10]):6.1f} dB bajo la senal")
    e = sg.sosfiltfilt(b, (load("alias_music_os")[:8 * SR] - ref)[SR // 10:-SR // 10], axis=0)
    inrange("musica, duro +12 dB, 4x: aliasing (dB bajo la senal)", rel(e, ref[SR // 10:-SR // 10]), -400, -80)

print("\n-- armonicos del sub: la fundamental no se toca")
x = sig("s50_m6")
for name, lim in (("fund_12", None), ("fund_24", 0.5)):
    if not has(name): continue
    y = load(name); df = tone(y[:, 0], 50) - tone(x[:, 0], 50)
    hs = "  ".join(f"{k}o {tone(y[:, 0], 50 * k) - tone(y[:, 0], 50):.1f}" for k in range(2, 7))
    print(f"    {name}: fundamental {df:+.2f} dB; armonicos (dB bajo la fundamental): {hs}")
    if lim: inrange("24 dB/oct: la fundamental cambia menos de 0.5 dB", df, -lim, lim)
if has("phone808"):
    x, y = sig("808"), load("phone808")
    hp = sg.butter(4, 150, "highpass", fs=SR, output="sos")   # parlante de celular: casi nada bajo 150 Hz
    gp = rms_db(sg.sosfilt(hp, y, axis=0)) - rms_db(sg.sosfilt(hp, x, axis=0)); gf = rms_db(y) - rms_db(x)
    lp = sg.butter(4, 80, fs=SR, output="sos"); g80 = rms_db(sg.sosfilt(lp, y, axis=0)) - rms_db(sg.sosfilt(lp, x, axis=0))
    print(f"    808 reales (F#1, A1), preset '808 - que se oiga en el celular': en un parlante de celular (>150 Hz) {gp:+.1f} dB; total {gf:+.1f} dB; bajo 80 Hz {g80:+.2f} dB")
    inrange("808: se oye mas en el celular (dB por encima de 150 Hz)", gp, 5, 60)
    inrange("808: el sub (bajo 80 Hz) casi igual (dB)", g80, -0.6, 0.6)

print("\n-- teoria")
for name in ("latency_os", "latency_off", "latency_radio"):
    if not has(name): continue
    # desfase contra la entrada por correlacion (con oversampling el filtro de fase lineal deja un pre-eco minimo
    # antes del borde: el primer valor no nulo no sirve para medir)
    y, x = load(name)[SR - 2000:SR + 4000, 0], sig("burst")[SR - 2000:SR + 4000, 0]
    lag = np.argmax(sg.correlate(y, x, "full", method="fft")) - (len(x) - 1)
    on = np.argmax(np.abs(load(name)[:, 0]) > 1e-3)
    print(f"    {name}: desfase {lag} muestras; supera -60 dBFS en la muestra {on} (la rafaga empieza en 48000)")
    if lag != 0 or on != 48000: fails += 1; print("MAL", name, "la latencia no se compensó")
if has("null_amt0"): inrange("radio con cantidad 0 = entrada (dB)", db(np.abs(load("null_amt0") - sig("music")).max()), -400, -140)
if has("null_mix0"): inrange("saturar todo con mezcla 0 = entrada (dB)", db(np.abs(load("null_mix0") - sig("music")).max()), -400, -140)

print("\n-- presets (musica)")
xm = sig("music"); lx = lufs(xm)
for k in range(1, 24):
    if not has(f"preset{k}"): continue
    y = load(f"preset{k}")
    print(f"    {k:2d} {NAMES[k - 1]:36s} pico {db(np.abs(y).max()):6.1f} dBFS   LUFS {lufs(y) - lx:+5.1f} (contra la entrada)")
    inrange(f"preset {k}: pico (dBFS)", db(np.abs(y).max()), -40, 0)
print("\nFALLAS:", fails)
sys.exit(1 if fails else 0)
