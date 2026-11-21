#!/usr/bin/env python3
"""Original energetic sports/hype track, synthesized (128 BPM, Am-F-C-G). Arrangement follows the video:
drop at the hook pullback, lighter under the questions, breakdown + riser into a second drop at the venue-owner answer,
final hit on the end card.  usage: music_hype.py <total_seconds> <out.wav> [drop2_time] [light ranges as a-b,a-b]"""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000; BPM = 128; BEAT = 60 / BPM; BAR = 4 * BEAT
TOT = float(sys.argv[1]); OUT = sys.argv[2]
DROP2 = float(sys.argv[3]) if len(sys.argv) > 3 else 52.5
LIGHT = [tuple(map(float, r.split('-'))) for r in sys.argv[4].split(',')] if len(sys.argv) > 4 else []
N = int((TOT + 2) * SR); rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
def bars(b): return b * BAR
DROP1 = bars(2); END_HIT = bars(int(TOT / BAR - 0.75))
def in_light(t): return any(a <= t < b for a, b in LIGHT)
def breakdown(t): return DROP2 - bars(4) <= t < DROP2
def lp(x, fc, o=2): return sosfilt(butter(o, fc, 'low', fs=SR, output='sos'), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x)
def add(t, s, g=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i < 0: return
    s = s[:N - i].copy(); f = min(len(s), int(0.008 * SR)); s[-f:] *= np.linspace(1, 0, f); s[:48] *= np.linspace(0, 1, 48)[:len(s[:48])]
    L[i:i + len(s)] += s * g * (1 - pan) ** .5 * 1.0; R[i:i + len(s)] += s * g * (1 + pan) ** .5 * 1.0
def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def nf(m): return 440 * 2 ** ((m - 69) / 12)
def saw(f, n, ph=0.0):
    t = np.arange(n) / SR; x = (t * f + ph) % 1; return 2 * x - 1
# ---- instruments ----
def kick():
    n = int(0.42 * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 32); ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7.5) * 1.0; s[:120] += rng.standard_normal(120) * .25 * np.linspace(1, 0, 120)
    return np.tanh(s * 1.6)
KICK = kick()
def clap():
    n = int(0.35 * SR); x = rng.standard_normal(n); e = np.zeros(n)
    for k, o in enumerate([0, .011, .022]):
        i = int(o * SR); m = int(0.012 * SR); e[i:i + m] += np.exp(-np.arange(m) / SR * 200)
    i = int(.03 * SR); e[i:] += np.exp(-np.arange(n - i) / SR * 18) * .7
    return bp(x * e, 900, 3500) * 1.4
CLAP = clap()
def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR); x = hp(rng.standard_normal(n), 7000, 4)
    return x * env(n, .001, .09 if open_ else .018) * (.5 if open_ else .4)
HC, HO = hat(), hat(True)
def supersaw(m_list, dur, cut=2600, voices=7, det=0.18):
    n = int(dur * SR); out = np.zeros(n)
    for m in m_list:
        for v in range(voices):
            d = (v - (voices - 1) / 2) / ((voices - 1) / 2) * det
            out += saw(nf(m + d), n, rng.random())
    out /= (len(m_list) * voices) ** .6
    return lp(out, cut, 2)
def pluck(m, dur=0.22):
    n = int(dur * SR); t = np.arange(n) / SR
    x = (saw(nf(m), n) * .6 + np.sign(np.sin(2 * np.pi * nf(m + 12) * t)) * .25)
    return lp(x, 3200, 2) * env(n, .002, .09)
def bass(m, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * nf(m) * t) * .9 + lp(saw(nf(m), n), 600) * .45
    return np.tanh(x * 1.3) * env(n, .004, dur * .9)
def riser(dur):
    n = int(dur * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n); seg = 2048
    for i in range(0, n, seg):
        k = i / n; fc = 400 + 9000 * k ** 2
        out[i:i + seg] = sosfilt(butter(2, [fc * .7, min(fc * 1.4, 20000)], 'band', fs=SR, output='sos'), x[i:i + seg])
    tone = np.sin(2 * np.pi * np.cumsum(200 * 2 ** (3 * t / dur)) / SR) * .15
    return (out / (np.abs(out).max() + 1e-9) * .6 + tone) * (t / dur) ** 2
def impact():
    n = int(2.0 * SR); t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(30 + 60 * np.exp(-t * 8)) / SR) * np.exp(-t * 2.2)
    crash = hp(rng.standard_normal(n), 4000, 2) * np.exp(-t * 2.4) * .35
    return boom * .9 + crash

PROG = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [55, 60, 64]), (55, [55, 59, 62])]  # Am F C G (root, chord)
ARP = [0, 2, 1, 2, 0, 2, 1, 3]
nb = int(TOT / BAR) + 2
sc = np.ones(N)  # sidechain gain curve from kicks
for b in range(nb):
    t0 = bars(b); root, ch = PROG[b % 4]
    if t0 > TOT + 1: break
    pre = t0 < DROP1; lightb = in_light(t0 + BAR / 2); bd = breakdown(t0); end = t0 >= END_HIT
    if end:
        if abs(t0 - END_HIT) < 1e-6:
            add(t0, impact(), .9); add(t0, KICK, 1.0)
            add(t0, supersaw([m + 12 for m in ch] + [ch[0]], 2.6, 3500) * env(int(2.6 * SR), .01, 1.0), .55, -.2)
            add(t0, bass(root - 12, 2.4), .5)
        continue
    # chords: pads in intro/breakdown, stabs in groove
    if pre or bd:
        pad = supersaw([m + 12 for m in ch], BAR, 900 if pre else 1500) * np.minimum(1, np.arange(int(BAR * SR)) / SR / .3)
        add(t0, pad, .32 if pre else .3, .15)
    else:
        for k in [1.5, 3.5] if lightb else [0.5, 1.5, 2.5, 3.0, 3.5]:
            st = supersaw([m + 12 for m in ch], BEAT * .45, 3800) * env(int(BEAT * .45 * SR), .003, .12)
            add(t0 + k * BEAT, st, .3 if not lightb else .22, -.2 if k % 1 else .2)
    for q in range(4):
        tb = t0 + q * BEAT
        if not pre and not bd:
            if not lightb or q in (0, 2):
                add(tb, KICK, .95 if not lightb else .6)
                i = int(tb * SR); m = int(.32 * SR); sc[i:i + m] = np.minimum(sc[i:i + m], 1 - .55 * np.exp(-np.arange(m) / SR * 9)[:N - i])
            if q in (1, 3) and not lightb: add(tb, CLAP, .55, .05)
            add(tb + BEAT / 2, HO if not lightb else HC, .3)
            for e in range(4):
                if e != 2: add(tb + e * BEAT / 4, HC, .2 if not lightb else .12, .3)
            # offbeat house bass
            add(tb + BEAT / 2, bass(root - 12, BEAT * .45), .55 if not lightb else .35)
        elif bd:
            add(tb + BEAT / 2, HC, .25, .3)
        # arp plucks (16ths) in groove, 8ths elsewhere
        step = BEAT / 4 if (not pre and not lightb and not bd) else BEAT / 2
        for e in range(int(BEAT / step)):
            idx = (q * 4 + e) % 8 if step < BEAT / 3 else (q * 2 + e) % 8
            nte = ch[ARP[idx] % 3] + 12 * (ARP[idx] // 3) + 12
            add(tb + e * step, pluck(nte), .16 if not pre else .1, .35 if e % 2 else -.35)
    if b == 1: add(DROP1 - 1.8, riser(1.8), .5)
# breakdown riser + snare roll into drop 2, impacts on drops
add(DROP2 - 3.6, riser(3.6), .55)
for k in range(16):
    tt = DROP2 - 1.875 + k * 1.875 / 16; add(tt, CLAP * (0.25 + 0.6 * k / 16), .6)
for d in [DROP1, DROP2]: add(d, impact(), .6)
# sidechain pump on everything except drums would be ideal; apply to the whole bus lightly
L *= .65 + .35 * sc; R *= .65 + .35 * sc
# reverb (stereo noise IR)
ir_n = int(1.6 * SR); t = np.arange(ir_n) / SR
irL = rng.standard_normal(ir_n) * np.exp(-t * 3.2); irR = rng.standard_normal(ir_n) * np.exp(-t * 3.2)
irL = lp(irL, 6000); irR = lp(irR, 6000); irL /= np.abs(irL).sum() ** .5 * 6; irR /= np.abs(irR).sum() ** .5 * 6
wetL = fftconvolve(hp(L, 300), irL)[:N]; wetR = fftconvolve(hp(R, 300), irR)[:N]
L = L + wetL * .25; R = R + wetR * .25
mix = np.stack([L, R], 1)[:int(TOT * SR)]
mix = np.tanh(mix / (np.abs(mix).max() + 1e-9) * 1.4) * .9
wavfile.write(OUT, SR, (mix * 32767).astype(np.int16)); print('wrote', OUT, mix.shape[0] / SR, 's')
