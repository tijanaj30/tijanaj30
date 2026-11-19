#!/usr/bin/env python3
"""Synthesize subtle UI sound effects and place them on the reel timeline."""
import json, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
rng = np.random.default_rng(7)
def t_(d): return np.arange(int(d*SR))/SR
def env_exp(d, tau): return np.exp(-t_(d)/tau)
def fade(x, a=0.003, b=0.01):
    na, nb = int(a*SR), int(b*SR)
    x[:na] *= np.linspace(0, 1, na); x[-nb:] *= np.linspace(1, 0, nb); return x
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'highpass', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, 'lowpass', fs=SR, output='sos'), x)
def norm(x, peak_db): return x/np.max(np.abs(x)+1e-9)*10**(peak_db/20)

def sweep(f0, f1, d):
    f = np.geomspace(f0, f1, int(d*SR)); return np.sin(2*np.pi*np.cumsum(f)/SR)
def bell(f, d=0.9, tau=0.25):
    tt = t_(d); x = sum(a*np.sin(2*np.pi*f*m*tt)*np.exp(-tt/(tau/m**0.5)) for m, a in [(1, 1), (2.76, .35), (5.4, .12)])
    return fade(x, .002, .05)
def whoosh(d, f0, f1, peak):
    n = rng.standard_normal(int(d*SR)); out = np.zeros_like(n); seg = 512
    cut = np.geomspace(f0, f1, len(n)//seg+1)
    for i in range(0, len(n), seg):
        c = cut[i//seg]; out[i:i+seg] = bp(n[max(0, i-2048):i+seg], c*0.6, min(c*1.6, 20000))[-len(n[i:i+seg]):]
    e = np.sin(np.pi*np.linspace(0, 1, len(n)))**1.6
    return norm(out*e, peak)

S = {}
S['pop'] = norm(fade(sweep(950, 420, .09)*env_exp(.09, .025)) + 0.15*hp(rng.standard_normal(int(.09*SR)), 3000)*env_exp(.09, .004), -24)
S['tick'] = norm(fade(np.sin(2*np.pi*2300*t_(.04))*env_exp(.04, .008)), -28)
S['bubble'] = norm(fade(sweep(380, 1100, .08)*env_exp(.08, .03)), -25)
S['click'] = norm(fade(hp(rng.standard_normal(int(.02*SR)), 2500)*env_exp(.02, .003)), -27)
S['swish'] = whoosh(.28, 1500, 5000, -31)
S['whoosh'] = whoosh(.42, 400, 4000, -27)
S['whoosh_s'] = whoosh(.32, 600, 3500, -30)
wb = whoosh(.85, 200, 6000, -24)
wb += norm(np.sin(2*np.pi*np.cumsum(np.geomspace(70, 140, len(wb)))/SR)*np.sin(np.pi*np.linspace(0, 1, len(wb))), -30)
S['whoosh_big'] = wb
sp = np.zeros(int(1.0*SR))
for i, (o, f0) in enumerate([(0, 500), (.22, 800), (.4, 1200), (.55, 1700)]):
    w = whoosh(.28, f0, f0*3, -30+i*1.0); sp[int(o*SR):int(o*SR)+len(w)] += w
S['spin'] = sp
def tone(f, d, tau):
    tt = t_(d); return fade(np.sin(2*np.pi*f*tt)*0.8 + 0.2*np.sin(2*np.pi*2*f*tt)) * np.exp(-tt/tau)
er = np.zeros(int(.35*SR)); a = tone(659, .16, .07); b = tone(523, .2, .08)
er[:len(a)] += a; er[int(.13*SR):int(.13*SR)+len(b)] += b
S['error'] = norm(er, -27)
S['low'] = norm(tone(220, .45, .15), -29)
for k, f in [('ding1', 1047), ('ding2', 1319), ('ding3', 1568)]: S[k] = norm(bell(f), -27)
sh = np.zeros(int(1.2*SR))
for i, f in enumerate([1568, 2093, 2637, 3136]):
    b_ = bell(f, .7, .18); o = int(i*.07*SR); sh[o:o+len(b_)] += b_*(0.9-i*0.12)
sh += 0.25*norm(hp(rng.standard_normal(len(sh)), 7000)*np.exp(-t_(1.2)/.25), 0)
S['shimmer'] = norm(sh, -27)
nt = np.zeros(int(.9*SR)); a = bell(1568, .5, .15); b = bell(2093, .7, .2)
nt[:len(a)] += a; nt[int(.12*SR):int(.12*SR)+len(b)] += b
S['notif'] = norm(nt, -25)

ev = json.load(open(sys.argv[1]))['SFX']; total = float(sys.argv[2])
track = np.zeros(int(total*SR)+SR)
for t0, name in ev:
    x = S[name]; i = int(max(0, t0)*SR); track[i:i+len(x)] += x[:len(track)-i]
track = track[:int(total*SR)]
print('sfx peak dBFS', round(20*np.log10(np.max(np.abs(track))+1e-9), 1), 'events', len(ev))
st = np.stack([track, track], 1)
wavfile.write(sys.argv[3], SR, (np.clip(st, -1, 1)*32767).astype(np.int16))
