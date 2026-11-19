#!/usr/bin/env python3
"""Original soft, elegant music bed: felt-piano arpeggios, warm pad, sub, light groove."""
import sys, json
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
TOTAL = float(sys.argv[1]); OUT = sys.argv[2]
K = json.load(open(sys.argv[3]))['K'] if len(sys.argv) > 3 else {}
BPM = 86; BEAT = 60/BPM; BAR = 4*BEAT
N = int(TOTAL*SR) + SR*3
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(3)
def mtof(m): return 440*2**((m-69)/12)
def lp(x, f): return sosfilt(butter(2, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'highpass', fs=SR, output='sos'), x)
def add(buf, x, t0, gain=1.0):
    i = int(t0*SR)
    if i >= len(buf): return
    x = x[:len(buf)-i]; buf[i:i+len(x)] += x*gain

# progression (G major): Gmaj7 | Em9 | Cmaj7 | D6sus
CH = [[55, 59, 62, 66, 69], [52, 55, 59, 62, 66], [48, 55, 59, 62, 64], [50, 54, 57, 59, 64]]
ROOT = [43, 40, 36, 38]

def piano(f, d=2.2, vel=1.0):
    t = np.arange(int(d*SR))/SR
    x = np.zeros_like(t)
    for h, a in [(1, 1), (2, .45), (3, .18), (4, .08), (5, .04)]:
        x += a*np.sin(2*np.pi*f*h*t*(1+0.0004*h))*np.exp(-t*(1.6+0.9*h))
    att = np.minimum(1, t/0.006)
    x *= att*vel
    return lp(x, 3200)

def pad(freqs, d):
    t = np.arange(int(d*SR))/SR
    xl = np.zeros_like(t); xr = np.zeros_like(t)
    for f in freqs:
        for det, side in [(-0.12, 0), (0.12, 1), (0, 2)]:
            ff = f*2**(det/100*10)
            w = sum(np.sin(2*np.pi*ff*h*t)/h**1.4 for h in (1, 2, 3))
            if side == 0: xl += w
            elif side == 1: xr += w
            else: xl += .6*w; xr += .6*w
    e = np.minimum(1, t/0.9)*np.minimum(1, (d-t)/0.9)
    return lp(xl*e, 900), lp(xr*e, 900)

nbars = int(np.ceil((TOTAL+2)/BAR))
arp = [0, 2, 1, 3, 4, 3, 2, 1]
for b in range(nbars):
    t0 = b*BAR; c = CH[b % 4]
    pl, pr = pad([mtof(m) for m in c[:4]], BAR+1.0)
    add(L, pl, t0, .028); add(R, pr, t0, .028)
    # sub bass
    t = np.arange(int(BAR*SR))/SR
    sub = np.sin(2*np.pi*mtof(ROOT[b % 4])*t)*np.minimum(1, t/0.05)*np.exp(-t*0.35)
    add(L, sub, t0, .10); add(R, sub, t0, .10)
    # felt piano arpeggio in 8ths (starts bar 0, fuller from bar 2)
    for k in range(8):
        if b < 1 and k % 2: continue
        m = c[arp[k]] + 12
        vel = (0.9 if k == 0 else 0.55 + 0.15*((k*5) % 3)/2)
        x = piano(mtof(m), vel=vel)
        pan = 0.5 + 0.25*np.sin(k)
        add(L, x, t0 + k*BEAT/2 + rng.uniform(0, 0.008), .085*(1-pan)*2)
        add(R, x, t0 + k*BEAT/2 + rng.uniform(0, 0.008), .085*pan*2)
    # light groove from bar 2: soft kick on 1 & 3, shaker on off-beats
    if b >= 2:
        for q in (0, 2):
            t = np.arange(int(.35*SR))/SR
            kick = np.sin(2*np.pi*np.cumsum(np.geomspace(110, 45, len(t)))/SR)*np.exp(-t*11)
            add(L, kick, t0+q*BEAT, .16); add(R, kick, t0+q*BEAT, .16)
        for q in range(8):
            if q % 2 == 1:
                t = np.arange(int(.08*SR))/SR
                sh = hp(rng.standard_normal(len(t)), 6000)*np.exp(-t*60)
                add(L, sh, t0+q*BEAT/2, .022); add(R, sh, t0+q*BEAT/2+0.004, .022)
        if b % 2 == 1:  # soft snap on beat 4
            t = np.arange(int(.15*SR))/SR
            sn = hp(rng.standard_normal(len(t)), 1800)*np.exp(-t*30)
            add(L, sn, t0+3*BEAT, .03); add(R, sn, t0+3*BEAT, .03)

# final ringing chord for the end card
if 'zato' in K:
    pass
endT = TOTAL - 2.0
for m in CH[0]:
    x = piano(mtof(m+12), d=3.0, vel=.8)
    add(L, x, endT, .09); add(R, x, endT+0.01, .09)

# reverb
def ir(seed):
    r = np.random.default_rng(seed); t = np.arange(int(2.2*SR))/SR
    return r.standard_normal(len(t))*np.exp(-t*2.6)*0.02
wetL = fftconvolve(L, ir(1))[:N]; wetR = fftconvolve(R, ir(2))[:N]
L = L + 0.55*lp(wetL, 5000); R = R + 0.55*lp(wetR, 5000)
L = L[:int(TOTAL*SR)]; R = R[:int(TOTAL*SR)]
# gentle fade in/out
n = len(L); fi = int(1.2*SR); fo = int(1.5*SR)
for ch in (L, R):
    ch[:fi] *= np.linspace(0, 1, fi); ch[-fo:] *= np.linspace(1, 0, fo)
st = np.stack([L, R], 1); st /= np.max(np.abs(st))+1e-9; st *= 0.7
wavfile.write(OUT, SR, (st*32767).astype(np.int16))
print('music written', round(TOTAL, 2), 's')
