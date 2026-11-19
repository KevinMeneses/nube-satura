"""Modelo en numpy de Nube Satura (mismo algoritmo que el JSFX, muestra a muestra) y presets.
model(x, p) recibe la entrada (n x 2) y los sliders que cambian ({numero: valor}); devuelve la salida ya realineada
(como la deja REAPER al compensar la latencia). La estatica (ruido aleatorio) no se modela: los casos van sin ella."""
import numpy as np
from scipy.signal import lfilter

SR = 48000
DEF = {1: 0, 2: 0, 3: 6, 4: 0.4, 5: 150, 6: 90, 7: 0, 8: 0, 9: 100, 10: 0, 11: 100, 12: 450, 13: 3200, 14: 4,
       15: -40, 16: 12, 17: 30, 18: 0, 19: 1, 20: -80, 21: 3000, 22: 1, 23: 0}
VC = 0.35; VA = VC / np.sqrt(1 + VC * VC); VG = (1 + VC * VC) ** 1.5


def shp(x, ty):
    if ty == 0: return np.tanh(np.clip(x, -20, 20)) * (np.abs(x) <= 20) + np.sign(x) * (np.abs(x) > 20)
    if ty == 1: return x / np.sqrt(1 + x * x)
    if ty == 2: a = x + VC; return (a / np.sqrt(1 + a * a) - VA) * VG
    a = x * x; return x / (1 + a * a * a) ** (1 / 6)


# ------------------------------------------------------------------ oversampling (igual que os_design del JSFX)
def i0(x):
    s = 1.0; t = 1.0; k = 1
    while t > 1e-12 * s:
        t *= (x / (2 * k)) ** 2; s += t; k += 1
    return s


def os_design(L, beta=6.2):
    C = 12 * L; n = np.arange(2 * C + 1) - C
    w = np.array([i0(beta * np.sqrt(max(0.0, 1 - (k / C) ** 2))) for k in n]) / i0(beta)
    h = np.where(n == 0, 1 / L, np.sin(np.pi * n / L) / (np.pi * np.where(n == 0, 1, n))) * w
    h[(n % L == 0) & (n != 0)] = 0; h /= h.sum()
    up = np.zeros((L, 24))
    for p in range(1, L):
        taps = h[L * np.arange(24) + p]; up[p] = taps / taps.sum()
    return h, up


def saturate(v, ty, bias, L):
    """curva(v + bias) - curva(bias); con L > 1 por oversampling (residuo filtrado), con 24 muestras de retraso"""
    fb = shp(np.array(bias), ty)
    if not L: return shp(v + bias, ty) - fb
    h, up = os_design(L); n = len(v)
    U = np.zeros((n, L) + v.shape[1:])
    U[12:, 0] = v[:-12]
    for p in range(1, L): U[:, p] = lfilter(up[p], [1.0], v, axis=0)
    U = U.reshape((n * L,) + v.shape[1:])
    r = U - (shp(U + bias, ty) - fb)
    d = lfilter(h, [1.0], r, axis=0)[::L]
    vd = np.zeros_like(v); vd[24:] = v[:-24]
    return vd - d


def delay(x, k):
    if not k: return x
    y = np.zeros_like(x); y[k:] = x[:-k]; return y


# ------------------------------------------------------------------ filtros (mismas formulas que el JSFX)
def c_lp(f):
    w = 2 * np.pi * f / SR; c = np.cos(w); s = np.sin(w); al = s / (2 * 0.70710678); a0 = 1 + al
    return [(1 - c) / 2 / a0, (1 - c) / a0, (1 - c) / 2 / a0], [1, -2 * c / a0, (1 - al) / a0]


def c_hp(f, q):
    w = 2 * np.pi * f / SR; c = np.cos(w); s = np.sin(w); al = s / (2 * q); a0 = 1 + al
    return [(1 + c) / 2 / a0, -(1 + c) / a0, (1 + c) / 2 / a0], [1, -2 * c / a0, (1 - al) / a0]


def c_rad(kind, f, q, g):
    w = 2 * np.pi * min(f, SR * 0.45) / SR; c = np.cos(w); s = np.sin(w); al = s / (2 * q)
    if kind == 0: a0 = 1 + al; b = [(1 + c) / 2 / a0, -(1 + c) / a0, (1 + c) / 2 / a0]; a = [1, -2 * c / a0, (1 - al) / a0]
    elif kind == 1: a0 = 1 + al; b = [(1 - c) / 2 / a0, (1 - c) / a0, (1 - c) / 2 / a0]; a = [1, -2 * c / a0, (1 - al) / a0]
    else:
        A = 10 ** (g / 40); a0 = 1 + al / A
        b = [(1 + al * A) / a0, -2 * c / a0, (1 - al * A) / a0]; a = [1, -2 * c / a0, (1 - al / A) / a0]
    return b, a


def filt(ba, x): return lfilter(ba[0], ba[1], x, axis=0)


def model(x, p_):
    p = dict(DEF); p.update(p_)
    md, ty, bias = int(p[1]), int(p[2]), p[4]
    L = {0: 0, 1: 4, 2: 8}[int(p[22])]; K = 24 if L else 0
    n0 = len(x); x = np.concatenate([x, np.zeros((K, 2))]); n = len(x)
    asym = bias > 0 or ty == 2
    dcR = np.exp(-2 * np.pi * 10 / SR)
    if md in (0, 1):
        g = 10 ** (p[3] / 20)
        v = g * (filt(c_lp(p[5]), x) if md == 0 else x)
        s = saturate(v, ty, bias, L) * (1 / g)
        dry = delay(x, K); gout = 10 ** (p[10] / 20)
        if md == 0:
            if p[7]: hh = filt(c_hp(p[6], 1.3065630), filt(c_hp(p[6], 0.5411961), s))
            else: hh = filt(c_hp(p[6], 0.70710678), s)
            y = (dry + 10 ** (p[8] / 20) * hh) * gout
        else:
            if asym: s = lfilter([1, -1], [1, -dcR], s, axis=0)
            wm = p[9] / 100; y = (dry * (1 - wm) + s * wm) * gout
        G = gout
    else:
        amt = p[11] / 100; ka = np.exp(-1 / (0.03 * SR))
        as_ = lfilter([1 - ka], [1, -ka], np.full(n, amt))        # as = amt + (as - amt) * ka, desde 0
        drive = 10 ** (p[3] * as_ / 20); wid = 1 - (1 - p[17] / 100) * as_
        post = (1 + (drive - 1) * 0.35) / drive
        # vaiven: retardo modulado (fase acumulada como en el JSFX)
        inc = 2 * np.pi * 4.5 / SR; ph = np.empty(n); q = 0.0
        for i in range(n):
            q += inc
            if q > 2 * np.pi: q -= 2 * np.pi
            ph[i] = q
        depmax = p[16] / 1200 * SR / (2 * np.pi * 4.5)
        rp = np.arange(n) - depmax * as_ * (1 + np.sin(ph)); i0_ = np.floor(rp).astype(int); fr = (rp - i0_)[:, None]
        xp = np.concatenate([np.zeros((4096, 2)), x, np.zeros((1, 2))])
        xx = xp[i0_ + 4096] * (1 - fr) + xp[i0_ + 4097] * fr
        m = (xx[:, 0] + xx[:, 1]) / 2; sd = (xx[:, 0] - xx[:, 1]) / 2 * wid; xx = np.stack([m + sd, m - sd], 1)
        fh = 20 * (p[12] / 20) ** amt; fl = 20000 * (p[13] / 20000) ** amt
        if p[12] > 20: xx = filt(c_rad(0, fh, 0.707, 0), filt(c_rad(0, fh, 0.707, 0), xx))
        if p[13] < 20000: xx = filt(c_rad(1, fl, 0.707, 0), filt(c_rad(1, fl, 0.707, 0), xx))
        if p[14] > 0: xx = filt(c_rad(2, 1600, 1.0, p[14] * amt), xx)
        v = xx * drive[:, None]
        s = saturate(v, ty, bias, L) * delay(post[:, None], K)
        if K: s[:K] = 0
        asd = delay(as_, K)
        if asym: s = lfilter([1, -1], [1, -dcR], s, axis=0)
        if p[19] > 1:
            hc = 0.0; h0 = np.zeros(2); N = p[19]
            for i in range(n):
                hc += 1
                if hc >= N: hc -= N; h0 = s[i].copy()
                s[i] = h0
        if p[18] > 0: qq = 2 ** (p[18] - 1); s = np.floor(s * qq + 0.5) / qq
        if p[20] > -79:
            e = filt(c_rad(0, p[21], 0.707, 0), s); s = s + np.tanh(e * 16) / 16 * 10 ** (p[20] / 20)
        G = 10 ** (p[10] * asd / 20)[:, None]
        dry = delay(x, K)
        y = (dry * (1 - asd[:, None]) + s * asd[:, None]) * G
    if p[23]: y = y - dry * G
    return y[K:K + n0]


# ------------------------------------------------------------------ presets (mismos que load_preset del JSFX)
def preset(n):
    p = dict(DEF)
    def pc(m, t, e, a, o): p.update({1: m, 2: t, 3: e, 4: a, 10: o})
    def psub(c, h, s, x): p.update({5: c, 6: h, 7: s, 8: x})
    def prad(g, a, nn, e, v, w): p.update({12: g, 13: a, 14: nn, 15: e, 16: v, 17: w})
    def plo(b, m, c, d): p.update({18: b, 19: m, 20: c, 21: d})
    T = {1: lambda: (pc(2, 0, 6, 0, 1), prad(450, 3200, 4, -40, 12, 30)),
         2: lambda: (pc(2, 0, 2, 0, 0.7), prad(100, 8000, 1, -55, 4, 75)),
         3: lambda: (pc(2, 0, 0, 0, 0), prad(20, 20000, 0, -52.5, 0, 100), plo(9.5, 2.5, -80, 3000)),
         4: lambda: (pc(0, 0, 6, 0.4, 0), psub(150, 90, 0, 0)),
         5: lambda: (pc(0, 2, 12, 0.2, 0), psub(120, 100, 1, 6)),
         6: lambda: (pc(0, 3, 12, 0.2, 0), psub(150, 110, 1, 6)),
         7: lambda: (pc(0, 2, 9, 0.2, 0), psub(140, 90, 1, -2)),
         8: lambda: (pc(0, 1, 9, 0.4, 0), psub(250, 150, 1, 0)),
         9: lambda: (pc(0, 1, 8, 0.3, 0), psub(130, 100, 1, -1)),
         10: lambda: (pc(1, 1, 3, 0.1, 0), p.update({9: 100})),
         11: lambda: (pc(1, 1, 8, 0.2, -1), p.update({9: 60})),
         12: lambda: (pc(1, 2, 6, 0, 0), p.update({9: 40})),
         13: lambda: (pc(1, 3, 12, 0, -1), p.update({9: 30})),
         14: lambda: (pc(1, 1, 6, 0.1, -1), p.update({9: 70})),
         15: lambda: (pc(1, 3, 9, 0, -1), p.update({9: 50})),
         16: lambda: (pc(1, 3, 18, 0.2, -3), p.update({9: 100})),
         17: lambda: (pc(1, 2, 4, 0, 0), p.update({9: 100})),
         18: lambda: (pc(2, 0, 9, 0, 1), prad(500, 3000, 5, -38, 15, 0)),
         19: lambda: (pc(2, 3, 12, 0, 2), prad(300, 3400, 6, -80, 0, 0)),
         20: lambda: (pc(2, 1, 4, 0.1, 0), prad(20, 9000, 0, -55, 8, 80)),
         21: lambda: (pc(2, 0, 3, 0, 0), prad(20, 20000, 0, -80, 0, 100), plo(12, 1.75, -80, 3000)),
         22: lambda: (pc(2, 0, 0, 0, 0), prad(20, 20000, 0, -52, 0, 100), plo(0, 1, -10, 3000)),
         23: lambda: None}
    T[n](); return p


NAMES = ["Nube baja - radio Outro 2 (X2)", "Nube baja - radio sutil (X4)", "Nube baja - lo-fi Outro 2 (X8c)",
         "Pies en la arena - kick largo", "808 - que se oiga en el celular", "808 drill - armonicos fuertes",
         "808 reggaeton / dembow - calido", "Bajo / reese - presencia", "Bus de bajos (kick + 808)",
         "Master - cinta suave", "Master lo-fi / chill", "Voz rap - valvula", "Voz drill - agresiva",
         "Bus de bateria - cinta", "Snare / clap - crunch", "808 rage - distorsion total", "Melodia - calidez",
         "Radio vieja (AM)", "Telefono", "Lo-fi - cassette", "Lo-fi - sampler 12 bits", "Lo-fi - crujiente", "Por defecto"]
