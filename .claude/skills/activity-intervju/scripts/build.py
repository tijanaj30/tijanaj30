#!/usr/bin/env python3
"""Activity školica sporta – interview reel: EDL -> base.mp4 (no zoom), speech.wav, timeline.json (segments + words)."""
import json, subprocess, os, re
import numpy as np
from scipy.io import wavfile

W = '/home/user/work/act'; FPS = 30
def run(c):
    r = subprocess.run(c, shell=True, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-2000:]); raise SystemExit(c)

B, Q, C = 'IMG_8640b', 'IMG_8641', 'IMG_8642'
# (src, start, end, beat, shot)  shot = framing preset used in the overlay
EDL = [
    (B, 64.86, 68.95, 'hook', 'tight'),
    (B, 4.62, 8.55, 'intro', 'wide'),
    (B, 10.16, 15.36, 'q1', 'qwide'),
    (B, 15.46, 20.22, 'a1', 'own'),
    (B, 20.88, 25.30, 'a1', 'own2'),
    (Q, 2.10, 9.02, 'q2', 'ask'),
    (C, 6.68, 11.86, 'a2', 'c1'),
    (C, 11.94, 14.02, 'a2', 'c2'),
    (C, 14.58, 19.56, 'a2', 'c1'),
    (C, 20.08, 24.82, 'a2', 'c2'),
    (B, 74.18, 80.32, 'q3', 'qwide'),
    (B, 80.26, 86.16, 'a3', 'own'),
    (B, 86.18, 93.86, 'a3', 'own2'),
    (B, 69.50, 72.06, 'end', 'wide'),
]

AUD = {}
for s in {e[0] for e in EDL}:
    sr, x = wavfile.read(f'{W}/src/{s}_dn.wav'); AUD[s] = x.astype(np.float32) / 32768
SR = 48000
def env(s):
    x = AUD[s]; fr = x[:len(x) // 480 * 480].reshape(-1, 480)
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9); return np.convolve(db, np.ones(5) / 5, 'same')
ENV = {s: env(s) for s in AUD}

def split_pauses(src, s, e, minpause=0.42, keep=0.14):
    db = ENV[src]; seg = db[int(s * 100):int(e * 100)]; thr = np.percentile(seg, 20) + 6
    out = []; cur = s; sil = None; t = s
    while t < e:
        v = db[min(len(db) - 1, int(t * 100))] > thr
        if not v and sil is None: sil = t
        if v and sil is not None:
            if t - sil > minpause and sil - cur > 0.3: out.append((cur, sil + keep)); cur = t - keep
            sil = None
        t += 0.01
    out.append((cur, e)); return out

segs = []
for src, s, e, beat, shot in EDL:
    for a, b in split_pauses(src, s, e):
        f0, f1 = round(a * FPS), round(b * FPS)
        if f1 - f0 >= 5: segs.append(dict(src=src, s=f0 / FPS, e=f1 / FPS, n=f1 - f0, beat=beat, shot=shot))
t = 0
for g in segs: g['t0'] = t; t += g['n'] / FPS; g['t1'] = t
BODY = t
print(len(segs), 'segments, body', round(BODY, 2))
for g in segs: print(f"  {g['beat']:5s} {g['shot']:5s} {g['src']} {g['s']:.2f}-{g['e']:.2f} -> {g['t0']:.2f}")

# words -> output timeline, with spelling fixes
FIX = {'Čava,': 'Ćao,', 'Bežaninskoj': 'Bežanijskoj', 'futbolskom': 'fudbalskom', 'futbala': 'fudbala', 'ovdje': 'ovde',
       'deca': 'dece', 'teli': 'hteli', 'bukva': 'bukvalno', 'osjetio': 'osetio', 'Iskrimno,': 'Iskreno,', 'sustrao': 'susreo',
       'vlasnik': 'vlasnik', 'prostorak': 'prostora', 'islave': 'slave', 'sporski': 'sportski', 'rođenjanje,': 'rođendani,',
       'absolutno': 'apsolutno', 'najveša': 'najviše', 'Bukvomno': 'Bukvalno', 'dječaci': 'devojčice i dečaci', 'uđe': 'uđu', 'kafeć,': 'kafić,',
       'naprava': 'naprave', 'rođan,': 'rođendan,', 'završe': 'završi', 'sadržave': 'sadržaje', 'odličnije.': 'odlično.'}
words = []
for g in segs:
    J = json.load(open(f"{W}/src/{g['src']}.MOV.json"))
    for sg in J['segments']:
        for w in sg['words']:
            m = (w['start'] + w['end']) / 2
            if g['s'] - 0.02 <= m < g['e']:
                txt = w['word'].strip(); txt = FIX.get(txt, txt)
                words.append(dict(w=txt, s=round(w['start'] - g['s'] + g['t0'], 3), e=round(min(w['end'], g['e']) - g['s'] + g['t0'], 3), beat=g['beat']))
# merge "2" ",5" -> "2,5"
out = []
for w in words:
    if out and (w['w'].startswith(',5') or w['w'].startswith('.5')): out[-1]['w'] += ',5'; out[-1]['w'] = out[-1]['w'].replace('2,5,5','2,5'); out[-1]['e'] = w['e']; continue
    out.append(w)
words = out
for w in words:
    if w['w'] == 'vlasnik' and w['beat'] == 'q3': w['w'] = 'vlasniku'
    if w['w'] in ('A', 'u') and w['beat'] == 'q3': w['w'] = ''
    if w['w'] == 'sa' and w['beat'] == 'a1': w['w'] = 's'
    if w['w'] == 'ništa' and w['beat'] == 'a3': w['w'] = 'bukvalno ništa'
    if w['w'] == 'i' and w['beat'] == 'a2' and 31 < w['s'] < 31.2: pass
words = [w for w in words if w['w']]
os.makedirs(f'{W}/build', exist_ok=True)
json.dump(dict(segs=segs, words=words, body=BODY), open(f'{W}/build/timeline.json', 'w'), ensure_ascii=False, indent=0)
print(' '.join(f"{w['w']}@{w['s']:.2f}" for w in words))
if os.environ.get('WO'): raise SystemExit

# video: native frames, no zoom (framing is done in the overlay page)
lst = []
for i, g in enumerate(segs):
    run(f"ffmpeg -v error -y -ss {g['s']:.3f} -i {W}/src/{g['src']}.MOV -frames:v {g['n']} -an -vf \"zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,fps={FPS},scale=1080:1920,setsar=1\" "
        f"-c:v libx264 -preset fast -crf 8 -pix_fmt yuv420p -r {FPS} {W}/build/seg{i:02d}.mp4")
    lst.append(f"file 'seg{i:02d}.mp4'")
open(f'{W}/build/list.txt', 'w').write('\n'.join(lst))
run(f"ffmpeg -v error -y -f concat -safe 0 -i {W}/build/list.txt -c copy {W}/build/base.mp4")
# speech: per-source level matching, sequential, 12 ms fades
parts = []; fade = int(0.012 * SR)
for g in segs:
    a = AUD[g['src']]; i0 = int(round(g['s'] * SR)); n = int(round(g['n'] / FPS * SR)); p = a[i0:i0 + n].copy()
    if len(p) < n: p = np.pad(p, (0, n - len(p)))
    r = np.linspace(0, 1, fade); p[:fade] *= r; p[-fade:] *= r[::-1]
    p *= {B: 1.0, Q: 1.0, C: 1.0}[g['src']]; parts.append(p)
wavfile.write(f'{W}/build/speech_raw.wav', SR, np.concatenate(parts))
run(f"ffmpeg -v error -y -i {W}/build/speech_raw.wav -af \"highpass=f=90,afftdn=nf=-28,equalizer=f=300:t=q:w=1.2:g=-2.5,equalizer=f=4000:t=q:w=1.5:g=2,"
    f"acompressor=threshold=0.08:ratio=3:attack=6:release=120,loudnorm=I=-16:TP=-1.5:LRA=7\" -ar 48000 {W}/build/speech.wav")
print('done')
