"""Señales de prueba (48 kHz, float32)."""
import numpy as np, soundfile as sf, pathlib
from scipy import signal as sg
D = pathlib.Path(__file__).parent / "signals"; D.mkdir(exist_ok=True)
SR = 48000
def a(db): return 10 ** (db / 20)
def save(name, *ch): sf.write(D / name, np.stack(ch, 1).astype(np.float32), SR, subtype="FLOAT")
n = SR * 2; t = np.arange(n) / SR
s = lambda f, db, tt=t: a(db) * np.sin(2 * np.pi * f * tt)
save("s50_m6.wav", s(50, -6), s(50, -6))
# tonos para medir aliasing (frecuencias que no dividen 48 kHz: lo plegado no cae sobre un armonico)
for f in (997, 3001, 7019, 11987): save(f"s{f}_m6.wav", s(f, -6), s(f, -6))
rng = np.random.default_rng(7); nz = a(-30) * rng.standard_normal((SR * 4, 2))
save("noise.wav", nz[:, 0], nz[:, 1])
save("silence.wav", np.zeros(SR * 4), np.zeros(SR * 4))
# rafaga desde 1.0 s empezando en el pico (latencia): 1 kHz a -20
b = np.zeros(n); i0 = SR; b[i0:] = a(-20) * np.cos(2 * np.pi * 1000 * (t[i0:] - 1.0)); save("burst.wav", b, b)
# 808 reales de la libreria (F#1 46 Hz y A1 55 Hz), uno cada segundo, 8 s
L = pathlib.Path.home() / "Music/ClaudeBeats/libreria_urbana"
out = np.zeros((SR * 8, 2))
for k, p in enumerate(["Trap/07 808 y Bajos/trap_bajo_01_Fs1.wav", "Drill/07 808 y Bajos/drill_bajo_02_A1.wav"] * 4):
    x, sr = sf.read(L / p, always_2d=True)
    if sr != SR: x = sg.resample_poly(x, SR, sr, axis=0)
    x = x[:SR]
    if x.shape[1] == 1: x = np.repeat(x, 2, 1)
    out[k * SR:k * SR + len(x)] += x[:, :2]
out *= a(-3) / np.abs(out).max(); save("808.wav", out[:, 0], out[:, 1])
# musica real: 20 s del premaster de Nube baja
mp = pathlib.Path.home() / "Music/ClaudeBeats/Mezcla/nube_baja_mezcla_premaster_X20.wav"
if mp.exists():
    x, sr = sf.read(mp, start=int(40 * SR), frames=20 * SR)
    if sr == SR: sf.write(D / "music.wav", x.astype(np.float32), SR, subtype="FLOAT")
print("ok", sorted(p.name for p in D.iterdir()))
