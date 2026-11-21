#!/usr/bin/env python3
"""Crisp CapCut-style SFX (ding, ping, pop, whoosh, swoosh, sparkle, referee whistle), stereo.
usage: sfx_cc.py <A.json> <timeline.json> <out.wav>"""
import sys, json, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR = 48000; rng = np.random.default_rng(11)
A = json.load(open(sys.argv[1])); BODY = json.load(open(sys.argv[2]))['body']; TOT = BODY + 3.5
N = int((TOT + 1) * SR); L = np.zeros(N); R = np.zeros(N)
def t_(d): return np.arange(int(d * SR)) / SR
def bp(x, a, b): return sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)
def hp(x, a): return sosfilt(butter(2, a, 'high', fs=SR, output='sos'), x)
def add(t, s, g=1.0, pan=0.0):
    i = int(t * SR)
    if i < 0 or i >= N: return
    s = s[:N - i]
    if s.ndim == 1: l, r = s * np.sqrt((1 - pan) / 2) * 1.414, s * np.sqrt((1 + pan) / 2) * 1.414
    else: l, r = s[:, 0], s[:, 1]
    L[i:i + len(l)] += l * g; R[i:i + len(r)] += r * g
def ding(f0=1568, d=1.1):          # bright bell (inharmonic partials)
    t = t_(d); y = np.zeros_like(t)
    for k, (m, a, dec) in enumerate([(1, 1, 2.6), (2.0, .45, 4), (2.76, .35, 5.5), (5.4, .18, 9), (8.93, .08, 14)]):
        y += a * np.sin(2 * np.pi * f0 * m * t + k) * np.exp(-t * dec)
    return y * np.minimum(1, t / .0015) * .5
def ping(f0=2200, d=.35):          # short high ping with a tiny upward chirp
    t = t_(d); f = f0 * (1 + .04 * (1 - np.exp(-t * 60)))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + .3 * np.sin(2 * np.pi * np.cumsum(2 * f) / SR)
    return y * np.exp(-t * 11) * np.minimum(1, t / .001) * .45
def pop(d=.12):                    # bubbly mouth pop
    t = t_(d); f = 380 + 1300 * (1 - np.exp(-t * 45))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 38)
    return y * np.minimum(1, t / .0008) * .8
def whoosh(d=.55, up=True, g=1.0): # airy whoosh with filter sweep and L->R pan
    n = int(d * SR); x = rng.standard_normal(n); out = np.zeros(n); seg = 1024
    for i in range(0, n, seg):
        k = i / n; k = k if up else 1 - k
        fc = 350 * (14 ** k); out[i:i + seg] = bp(x[i:i + seg], fc * .55, min(fc * 1.8, 20000))
    e = np.sin(np.pi * np.linspace(0, 1, n) ** (.6 if up else 1.6)) ** 2
    y = out / (np.abs(out).max() + 1e-9) * e * g
    p = np.linspace(-.8, .8, n) if up else np.linspace(.8, -.8, n)
    return np.stack([y * np.sqrt((1 - p) / 2) * 1.4, y * np.sqrt((1 + p) / 2) * 1.4], 1)
def swoosh(d=.32):                 # quick card swipe
    return whoosh(d, True, .9)
def sparkle():
    y = np.zeros(int(1.4 * SR))
    for j, f in enumerate([2093, 2637, 3136, 3951, 4186, 5274]):
        s = ping(f, .6) * .55; i = int(j * .07 * SR); y[i:i + len(s)] += s[:len(y) - i]
    return y
def whistle(d=1.0):                # referee pea whistle: ~2.9 kHz with fast trill + breath
    t = t_(d); trill = 1 + .5 * np.sin(2 * np.pi * 38 * t)
    f = 2850 + 140 * np.sin(2 * np.pi * 38 * t)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + .25 * np.sin(2 * np.pi * np.cumsum(2 * f) / SR)
    breath = bp(rng.standard_normal(len(t)), 2000, 6000) * .25
    env = np.minimum(1, t / .02) * np.minimum(1, (d - t) / .05)
    return (tone * (.6 + .4 * trill) + breath) * env * .35
fx = []
def ev(t, s, g=1.0, pan=0.0): add(t, s, g, pan)
# hook
ev(0.10, pop(), .7); ev(A['tKafu'] - .15, ping(2349), .8, .3)
ev(3.2, whoosh(1.2, True, 1.0), .8)
# widgets in
for t in [A['tNem'] - .3, A['tTri'] - .1, A['cardIgr'][1] - .1, A['tInter'] - .1, A['tBuk'] - .05, A['tPauz'] - .15, A['cardOrg'][1] - .1, A['tFeed'] - .15]:
    ev(t, pop(), .75); ev(t + .02, ping(2637, .25), .35)
# check rows / counters -> dings
for t in [A['tSvak'] - .1, A['tInter'], A['tUklj'] - .1, A['cardOrg'][1] + .15, A['cardOrg'][1] + .4, A['cardOrg'][1] + .65, A['cardIgr'][1] + .6]:
    ev(t, ding(1760, .7), .45, .2)
for j in range(5): ev(A['tFeed'] + .25 + j * .12, ping([2093, 2349, 2637, 3136, 3520][j], .3), .55, -.4 + .2 * j)
ev(A['tSav'] - .05, ding(2093), .55)
# white cards: swoosh in, soft whoosh out, ding on the strike / checks
for c in ['cardIgr', 'cardOrg']:
    ev(A[c][0] - .18, swoosh(), .9); ev(A[c][1] - .1, whoosh(.35, False, .6), .6)
ev(A['cardIgr'][0] + .75, whoosh(.25, True, .7), .6)
for j in range(3): ev(A['cardOrg'][0] + .7 + j * .28, ding(1976 + j * 220, .5), .4)
# whistle on "sviramo kraj" (short + long blast)
ev(A['tSvir'] - .05, whistle(.22), .5); ev(A['tSvir'] + .28, whistle(.75), .5)
# text moment + floor word
ev(A['tKuci'] - .1, ding(1318, 1.0), .5)
ev(A['tSvi'] - .25, whoosh(.5, True, .9), .7); ev(A['tPrez'] - .05, ding(1568, 1.0), .55)
# end card
ev(BODY - .3, whoosh(1.0, True, 1.0), .9); ev(BODY + .7, sparkle(), .6); ev(BODY + .75, ding(1318, 1.4), .5)
mix = np.stack([L, R], 1)[:int(TOT * SR)]
mix = mix / (np.abs(mix).max() + 1e-9) * .8
wavfile.write(sys.argv[3], SR, mix.astype(np.float32)); print('sfx ok', mix.shape[0] / SR)
