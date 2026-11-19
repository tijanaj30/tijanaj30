#!/usr/bin/env python3
"""Original upbeat, trendy instrumental (~118 BPM pop-house) synced to the reel's beats."""
import sys, json
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
TOTAL = float(sys.argv[1]); OUT = sys.argv[2]
d = json.load(open(sys.argv[3])); K = d['K']
TL = json.load(open(sys.argv[4])); BODY = TL['body']
BPM = 118; BEAT = 60/BPM; BAR = 4*BEAT
N = int((TOTAL+3)*SR)
L = np.zeros(N); R = np.zeros(N); DUCK = np.ones(N)
rng = np.random.default_rng(11)
def mtof(m): return 440*2**((m-69)/12)
def flt(x, f, kind): return sosfilt(butter(2, f, kind, fs=SR, output='sos'), x)
def add(x, t0, g=1.0, pan=0.5, buf=None):
    i = int(t0*SR)
    if i >= N or t0 < 0: return
    x = x[:N-i]
    L[i:i+len(x)] += x*g*np.sqrt(2*(1-pan))
    R[i:i+len(x)] += x*g*np.sqrt(2*pan)
def tt(dur): return np.arange(int(dur*SR))/SR

# grid: put the drop exactly on "Zato mi radimo drugačije"
DROP = K['zato']
start = DROP - round(DROP/BAR)*BAR           # phase so that a bar starts at DROP
bars = []
b0 = start
while b0 < TOTAL+BAR:
    bars.append(b0); b0 += BAR
END_STOP = BODY  # music hits final stab at end card

# Am  F  C  G
PROG = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 55, 60, 64], [55, 59, 62, 67]]
BASS = [45, 41, 36, 43]
MEL = [76, 74, 72, 74, 76, 79, 76, 72]   # catchy pluck motif (8ths, sparse)

def kick():
    t = tt(.32); f = 48 + 110*np.exp(-t*28)
    x = np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
    x[:int(.004*SR)] += flt(rng.standard_normal(int(.004*SR)), 3000, 'highpass')*.3
    return x
def clap():
    t = tt(.25); x = np.zeros(len(t))
    for o in (0, .011, .022):
        n = flt(rng.standard_normal(len(t)), [900, 3500], 'bandpass')
        e = np.where(t >= o, np.exp(-(t-o)*(60 if o < .02 else 18)), 0); x += n*e
    return x
def hat(open_=False):
    t = tt(.25 if open_ else .05); return flt(rng.standard_normal(len(t)), 7500, 'highpass')*np.exp(-t*(14 if open_ else 90))
def saw(f, t, det=0.0):
    ph = (f*(1+det)*t) % 1.0; return 2*ph-1
def stab(notes, dur=.32):
    t = tt(dur); x = np.zeros(len(t))
    for m in notes:
        for dt in (-.006, 0, .006): x += saw(mtof(m+12), t, dt)
    env = np.exp(-t*7)*np.minimum(1, t/.004)
    # filter env: bright to darker
    y = flt(x*env, 2600, 'lowpass')*.6 + flt(x*env, 900, 'lowpass')*.4
    return y/len(notes)
def pluck(m, dur=.35):
    t = tt(dur); x = np.sin(2*np.pi*mtof(m)*t)+.3*np.sin(2*np.pi*mtof(m)*2*t)+.12*np.sin(2*np.pi*mtof(m)*3*t)
    return x*np.exp(-t*9)*np.minimum(1, t/.003)
def bass(m, dur):
    t = tt(dur); x = saw(mtof(m), t)*.6 + np.sin(2*np.pi*mtof(m)*t)
    return flt(x*np.minimum(1, t/.005)*np.exp(-t*2.5), 420, 'lowpass')
def riser(dur):
    t = tt(dur); n = rng.standard_normal(len(t)); out = np.zeros(len(t)); seg = 1024
    cut = np.geomspace(400, 9000, len(t)//seg+1)
    for i in range(0, len(t), seg):
        out[i:i+seg] = flt(n[max(0, i-4096):i+seg], [cut[i//seg]*.7, min(cut[i//seg]*1.4, 20000)], 'bandpass')[-len(n[i:i+seg]):]
    return out*(t/dur)**2

for bi, b0 in enumerate(bars):
    if b0 >= END_STOP: break
    ci = bi % 4; prog = PROG[ci]
    section = 'intro' if b0 < bars[0]+2*BAR - 1e-6 else ('break' if DROP-BAR-1e-6 <= b0 < DROP-1e-6 else 'full')
    for q in range(4):
        tb = b0 + q*BEAT
        if tb >= END_STOP: break
        if section != 'break' and not (section == 'intro' and bi == 0):
            add(kick(), tb, .55)
            i = int(tb*SR); dl = int(.22*SR)
            env = 1-0.65*np.exp(-np.arange(dl)/SR*14)  # sidechain pump
            if i < N: DUCK[i:i+dl] = np.minimum(DUCK[i:i+dl], env[:N-i])
        if q in (1, 3) and section == 'full': add(clap(), tb, .16, .5)
        # hats
        for s16 in range(4):
            th = tb + s16*BEAT/4
            if th >= END_STOP: break
            if s16 == 2: add(hat(True), th, .05 if section == 'full' else .03, .62)
            elif section == 'full': add(hat(), th, .03 + .012*(s16 == 0), .4)
        # offbeat chord stabs (house) + bass
        if tb + BEAT/2 < END_STOP:
            add(stab(prog), tb + BEAT/2, .2 if section != 'intro' else .12, .45)
        if section != 'break':
            add(bass(BASS[ci], BEAT*.45), tb + BEAT/2, .32)
            if q == 3: add(bass(BASS[ci]+12, BEAT*.2), tb + 3*BEAT/4, .18)
    # pluck motif on every other bar in full sections
    if section == 'full' and bi % 2 == 0:
        for k, m in enumerate(MEL):
            tm = b0 + k*BEAT/2
            if k in (2, 5) or tm >= END_STOP: continue
            add(pluck(m), tm, .1, .55 + .1*np.sin(k))
# riser into the drop + impact
r = riser(BAR); add(r, DROP-BAR, .05)
t = tt(1.2); boom = np.sin(2*np.pi*np.cumsum(55+40*np.exp(-t*6))/SR)*np.exp(-t*3)
add(boom, DROP, .35)
# final stab + tail on end card
add(stab(PROG[0], 1.4), END_STOP, .3); add(kick(), END_STOP, .5)
for k, m in enumerate([72, 76, 79, 84]): add(pluck(m, .8), END_STOP + .12 + k*.09, .09, .5)

# apply sidechain pump to music (not to kick itself: approximation - pump whole mix lightly)
L *= 0.55+0.45*DUCK; R *= 0.55+0.45*DUCK
def ir(seed):
    r_ = np.random.default_rng(seed); t_ = tt(1.6); return r_.standard_normal(len(t_))*np.exp(-t_*3.5)*0.02
L = L + .35*flt(fftconvolve(L, ir(1))[:N], 6000, 'lowpass'); R = R + .35*flt(fftconvolve(R, ir(2))[:N], 6000, 'lowpass')
L = flt(L, 30, 'highpass'); R = flt(R, 30, 'highpass')
n = int(TOTAL*SR); L = L[:n]; R = R[:n]
fo = int(.6*SR); L[-fo:] *= np.linspace(1, 0, fo); R[-fo:] *= np.linspace(1, 0, fo)
st = np.stack([L, R], 1); st /= np.max(np.abs(st))+1e-9; st *= .8
wavfile.write(OUT, SR, (st*32767).astype(np.int16))
print('music2 ok; drop at', round(DROP, 2), 'bar', round(BAR, 3))
