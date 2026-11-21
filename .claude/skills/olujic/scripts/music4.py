#!/usr/bin/env python3
"""Original uplifting, sentimental-cinematic bed (~92 BPM): piano pulse, warm strings, soft groove; drier mix."""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000; TOTAL = float(sys.argv[1]); OUT = sys.argv[2]; BW0, BW1 = float(sys.argv[3]), float(sys.argv[4]); END = float(sys.argv[5])
BPM = 92; BEAT = 60 / BPM; BAR = 4 * BEAT
N = int((TOTAL + 5) * SR); L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(9)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def flt(x, f, k): return sosfilt(butter(2, f, k, fs=SR, output='sos'), x)
def tt(d): return np.arange(int(d * SR)) / SR
def add(x, t0, g, pan=.5):
    i = int(t0 * SR)
    if i >= N or t0 < 0: return
    x = x[:N - i]; L[i:i + len(x)] += x * g * np.sqrt(2 * (1 - pan)); R[i:i + len(x)] += x * g * np.sqrt(2 * pan)
def piano(m, d=2.5, v=1.0):
    t = tt(d); f = mtof(m); x = np.zeros_like(t)
    for h, a in [(1, 1), (2, .45), (3, .18), (4, .08), (5, .04)]:
        x += a * np.sin(2 * np.pi * f * h * t * (1 + .0003 * h)) * np.exp(-t * (1.3 + .9 * h))
    return flt(x * np.minimum(1, t / .006) * v, 3200, 'lowpass')
def strings(ms, d):
    t = tt(d); x = np.zeros_like(t); y = np.zeros_like(t)
    for m in ms:
        for det, side in [(-.08, 0), (.08, 1)]:
            f = mtof(m) * 2 ** (det / 12); ph = rng.random() * 6.28
            w = sum(np.sin(2 * np.pi * f * h * t + ph) / h ** 1.4 for h in (1, 2, 3, 4, 5))
            (x if side == 0 else y)[:] += w
    e = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.0)
    return flt(x * e, 2200, 'lowpass'), flt(y * e, 2200, 'lowpass')
def kick():
    t = tt(.3); return np.sin(2 * np.pi * np.cumsum(45 + 70 * np.exp(-t * 30)) / SR) * np.exp(-t * 10)
def shaker():
    t = tt(.07); return flt(rng.standard_normal(len(t)), 7000, 'highpass') * np.exp(-t * 70)
def clap():
    t = tt(.2); return flt(rng.standard_normal(len(t)), [1000, 4000], 'bandpass') * np.exp(-t * 22)
# C | G | Am | F   (I-V-vi-IV), bridge in B/W: Am | F | Dm | E
CH = [[60, 64, 67], [59, 62, 67], [57, 60, 64], [57, 60, 65]]
BS = [48, 43, 45, 41]
BWCH = [[57, 60, 64], [57, 60, 65], [57, 62, 65], [56, 59, 64]]; BWBS = [45, 41, 38, 40]
MEL = [[79, None, 76, None, 74, 76, None, None], [74, None, 71, None, 74, None, 79, None], [76, None, 72, None, 71, 72, None, None], [72, None, 69, None, 72, None, 74, None]]
nb = int(np.ceil((END + 1) / BAR))
for b in range(nb):
    t0 = b * BAR
    if t0 >= END: break
    bw = BW0 - BAR * 0.5 <= t0 < BW1
    c = (BWCH if bw else CH)[b % 4]; bass = (BWBS if bw else BS)[b % 4]
    full = b >= 4 and not bw
    # bass (warm, sustained) and low octave piano
    t = tt(BAR); bs = (np.sin(2 * np.pi * mtof(bass) * t) + .3 * np.sin(2 * np.pi * mtof(bass) * 2 * t)) * np.minimum(1, t / .03) * np.exp(-t * .5)
    add(bs, t0, .11 if full else .07)
    # piano pulse: 8th-note chords, accents on 1 and the 'and' of 2
    for k in range(8):
        acc = 1.0 if k in (0, 3, 6) else .6
        if not full and k % 2: continue
        for j, m in enumerate(c):
            add(piano(m + 12, 1.6, acc * (.9 - .15 * j)), t0 + k * BEAT / 2 + rng.uniform(0, .006), .045, .3 + .2 * j)
    if full:
        for k, m in enumerate(MEL[b % 4]):
            if m: add(piano(m, 2.4, .9), t0 + k * BEAT / 2, .07, .6)
    # strings: present throughout, bigger in full sections and in the drama bridge
    g = .03 if full else (.034 if bw else .018)
    sl, sr_ = strings([c[0] - 12, c[0], c[1], c[2] + 12], BAR + 1.0); add(sl, t0 - .2, g, .2); add(sr_, t0 - .2, g, .8)
    # soft groove in full sections
    if full:
        for q in range(4):
            add(kick(), t0 + q * BEAT, .22 if q in (0, 2) else .12)
            if q in (1, 3): add(clap(), t0 + q * BEAT, .05)
        for k in range(8):
            if k % 2: add(shaker(), t0 + k * BEAT / 2, .035, .65)
# swell + resolve at the end
for m in [48, 55, 60, 64, 67, 72, 76]: add(piano(m, 5, .9), END + .05, .075)
sl, sr_ = strings([48, 55, 64, 72], 4.5); add(sl, END - .3, .04, .2); add(sr_, END - .3, .04, .8)
def ir(seed):
    r = np.random.default_rng(seed); t = tt(1.2); return r.standard_normal(len(t)) * np.exp(-t * 4.5) * .02
L = L + .25 * flt(fftconvolve(L, ir(1))[:N], 6000, 'lowpass'); R = R + .25 * flt(fftconvolve(R, ir(2))[:N], 6000, 'lowpass')
L = flt(L, 35, 'highpass'); R = flt(R, 35, 'highpass')
n = int(TOTAL * SR); L = L[:n]; R = R[:n]
fi = int(1.0 * SR); fo = int(1.8 * SR)
for ch in (L, R): ch[:fi] *= np.linspace(0, 1, fi); ch[-fo:] *= np.linspace(1, 0, fo)
st = np.stack([L, R], 1); st /= np.max(np.abs(st)) + 1e-9; st *= .85
wavfile.write(OUT, SR, (st * 32767).astype(np.int16)); print('music4 ok')
