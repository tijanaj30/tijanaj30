#!/usr/bin/env python3
"""Original upbeat instrumental for fast unboxing cuts (120 BPM = cut every 2 beats).
usage: music.py TOTAL_SEC OUT.wav [bpm=120] [drop_sec=4.0]"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR = 48000
TOTAL = float(sys.argv[1]); OUT = sys.argv[2]
BPM = float(sys.argv[3]) if len(sys.argv) > 3 else 120
DROP = float(sys.argv[4]) if len(sys.argv) > 4 else 4.0
B = 60 / BPM
N = int((TOTAL + 1.5) * SR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)
def flt(x, f, k): return sosfilt(butter(2, f, k, fs=SR, output='sos'), x)
def tt(d): return np.arange(int(d * SR)) / SR
def add(x, t0, g=1.0, pan=0.5):
    i = int(t0 * SR)
    if i < 0 or i >= N: return
    x = x[:N - i]
    L[i:i + len(x)] += x * g * np.sqrt(2 * (1 - pan)); R[i:i + len(x)] += x * g * np.sqrt(2 * pan)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def kick():
    t = tt(.35); f = 48 + 110 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
def clap():
    t = tt(.22); n = rng.standard_normal(len(t))
    env = np.exp(-t * 22) + .6 * np.exp(-((t - .012) * 300) ** 2) + .5 * np.exp(-((t - .024) * 300) ** 2)
    return flt(n, [900, 6000], 'band') * env * .9
def hat(o=False):
    t = tt(.25 if o else .05); return flt(rng.standard_normal(len(t)), 7500, 'high') * np.exp(-t * (14 if o else 90)) * .35
def saw(f, t): return 2 * ((f * t) % 1) - 1
def stab(notes, d=.22):
    t = tt(d); x = sum(saw(mtof(m), t) + saw(mtof(m) * 1.006, t) for m in notes)
    return flt(x, 2600, 'low') * np.exp(-t * 9) * .07
def bass(m, d):
    t = tt(d); x = np.sin(2 * np.pi * mtof(m) * t) + .3 * np.sign(np.sin(2 * np.pi * mtof(m) * t))
    return flt(x, 600, 'low') * np.minimum(1, t * 200) * np.exp(-t * 3) * .45
def pluck(m):
    t = tt(.3); return (np.sin(2 * np.pi * mtof(m) * t) + .4 * np.sin(4 * np.pi * mtof(m) * t)) * np.exp(-t * 12) * .12
PROG = [[61, 64, 68], [59, 63, 66], [56, 59, 63], [57, 61, 64]]   # C#m B G#m A  (bright, trendy)
BASS = [37, 35, 32, 33]
MEL = [73, 75, 76, 75, 73, 71, 68, 71]
end = TOTAL
nb = int(end / B) + 1
for k in range(nb):
    t = k * B
    if t > end - 0.01: break
    bar = int(t / (4 * B)); ch = bar % 4; beat = k % 4
    full = t >= DROP - 1e-6
    if full:
        add(kick(), t, .9)
        if beat in (1, 3): add(clap(), t, .5)
        add(bass(BASS[ch], B * .45), t + B / 2, .9)
        add(hat(True), t + B / 2, .5, .6)
        add(stab(PROG[ch]), t + B / 2, 1.0, .45)
        if k % 2 == 0: add(pluck(MEL[(k // 2) % 8] + 12 * (bar % 2 == 1)), t + B * .75, 1, .7)
    else:
        add(stab(PROG[ch], .3), t, .7, .4)
        add(hat(), t + B / 2, .35, .6)
        if beat == 0: add(kick(), t, .45)
    add(hat(), t, .25, .4)
# riser + snare roll into drop
if DROP > 1.5:
    t = tt(1.0); r = flt(rng.standard_normal(len(t)), 3000, 'high') * (t / 1.0) ** 2 * .25
    add(r, DROP - 1.0)
    for j in range(8): add(clap(), DROP - 1.0 + j * B / 4, .15 + j * .04)
# ending: big stab and short tail
add(kick(), end, .9); add(stab(PROG[0], .9) * 2.2, end)
x = np.stack([L, R], 1)
x[int((end + 1.2) * SR):] = 0
fade = int(.3 * SR); i1 = int((end + 1.2) * SR)
x[i1 - fade:i1] *= np.linspace(1, 0, fade)[:, None]
x /= np.max(np.abs(x)) + 1e-9; x *= .89
wavfile.write(OUT, SR, (x * 32767).astype(np.int16))
