#!/usr/bin/env python3
"""Video 2 (window): pause/retake removal, gentle dissolves, discreet zoom; sequential uncut audio."""
import json, subprocess, os
import numpy as np
from scipy.io import wavfile
W = '/home/user/work/r9'; SRC = f'{W}/src/v2.mov'; FPS = 30

def run(c):
    r = subprocess.run(c, shell=True, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-2000:]); raise SystemExit(c)

sr, x = wavfile.read(f'{W}/audio/a16.wav'); x = x.astype(float) / 32768
fr = x[:len(x) // 160 * 160].reshape(-1, 160); DB = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
DB = np.convolve(DB, np.ones(3) / 3, 'same'); THR = np.percentile(DB, 10) + 12
def voiced(t): return DB[min(len(DB) - 1, int(t * 100))] > THR

EDL = [(9.82, 38.50, 1), (60.55, 70.15, 2), (76.62, 84.20, 2),
       (84.40, 90.85, 3), (91.30, 93.62, 3), (102.15, 105.35, 3)]
ZOOM = {1: (1.0, 1.08), 2: (1.08, 1.0), 3: (1.0, 1.08)}
FX, FY = 0.45, 0.28

def split_pauses(s, e, minpause=0.5, keep=0.22):
    out = []; cur = s; t = s; sil = None
    while t < e:
        v = voiced(t)
        if not v and sil is None: sil = t
        if v and sil is not None:
            if t - sil > minpause and sil - cur > 0.3: out.append((cur, sil + keep)); cur = t - keep
            sil = None
        t += 0.01
    out.append((cur, e)); return out

segs = []
WORDS_ONLY = os.environ.get('WO')
for s, e, beat in EDL:
    for a, b in split_pauses(s, e):
        f0, f1 = round(a * FPS), round(b * FPS)
        if f1 - f0 >= 6: segs.append(dict(s=f0 / FPS, e=f1 / FPS, n=f1 - f0, beat=beat))
last = None; k = 0
for g in segs:
    k = k + 1 if g['beat'] == last else 0; last = g['beat']; g['zoom'] = ZOOM[g['beat']][k % 2]
print(len(segs), 'segments', [(round(g['s'], 2), round(g['e'], 2)) for g in segs])
os.makedirs(f'{W}/build', exist_ok=True)
XF = 0.4; HH = XF / 2
offs = []; acc = 0.0
for g in segs: offs.append(acc); acc += g['n'] / FPS
BODY = acc
for i, g in enumerate([] if WORDS_ONLY else segs):
    z = g['zoom']; hs = 0 if i == 0 else HH; he = 0 if i == len(segs) - 1 else HH
    N = g['n'] + round((hs + he) * FPS)
    zz = f"{z}+0.012*on/{max(N - 1, 1)}"
    xx = f"max(0,min(iw-iw/zoom,{FX}*iw-iw/zoom/2))"; yy = f"max(0,min(ih-ih/zoom,{FY}*ih-ih/zoom/2))"
    run(f"ffmpeg -v error -y -ss {g['s'] - hs:.3f} -i {SRC} -frames:v {N} -an -vf \"fps={FPS},scale=2160:3840:flags=lanczos,zoompan=z='{zz}':x='{xx}':y='{yy}':d=1:s=1080x1920:fps={FPS},setsar=1\" "
        f"-c:v libx264 -preset fast -crf 14 -pix_fmt yuv420p -r {FPS} {W}/build/seg{i:02d}.mp4")
if not WORDS_ONLY:
    sr2, a = wavfile.read(f'{W}/audio/full.wav'); a = a.astype(np.float32) / 32768
    parts = []; fade = int(0.015 * sr2)
    for g in segs:
        i0 = int(round(g['s'] * sr2)); n = int(round(g['n'] / FPS * sr2)); p = a[i0:i0 + n].copy()
        r = np.linspace(0, 1, fade)[:, None]; p[:fade] *= r; p[-fade:] *= r[::-1]; parts.append(p)
    wavfile.write(f'{W}/build/speech.wav', sr2, (np.concatenate(parts) * 32767).astype(np.int16))
    ins = ' '.join(f'-i {W}/build/seg{i:02d}.mp4' for i in range(len(segs)))
    fc = []; prev = '[0:v]'
    for i in range(1, len(segs)):
        lab = f'[x{i}]'; fc.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={offs[i] - HH:.3f}{lab}"); prev = lab
    run(f"ffmpeg -v error -y {ins} -filter_complex \"{';'.join(fc)}\" -map \"{prev}\" -c:v libx264 -preset fast -crf 14 -pix_fmt yuv420p -r {FPS} {W}/build/body_raw.mp4")
    run(f"ffmpeg -v error -y -i {W}/build/body_raw.mp4 -i {W}/build/speech.wav -filter_complex "
        f"\"[1:a]highpass=f=80,afftdn=nf=-30,equalizer=f=320:t=q:w=1.2:g=-3,equalizer=f=4500:t=q:w=1.5:g=2,acompressor=threshold=0.1:ratio=2.5:attack=8:release=120,loudnorm=I=-15:TP=-1.5:LRA=8,aresample=48000[a]\" "
        f"-map 0:v -map [a] -c:v copy -c:a aac -b:a 192k {W}/build/body.mp4")
# words
WW = [w for w in json.load(open(f'{W}/audio/words.json')) if w['s'] < 100]
for w in WW:
    if w['w'] == 'ljudima.' and w['s'] < 6: w['e'] = 5.3
    if w['w'] == 'ali' and 75.9 < w['s'] < 76.1: w['s'], w['e'] = 76.74, 76.95
    if w['w'] == 'nas' and 65 < w['s'] < 66: w['w'] = 'na'
WW += [dict(s=102.35, e=102.55, w='Hvala'), dict(s=102.55, e=102.63, w='vam'), dict(s=102.63, e=102.79, w='što'),
       dict(s=102.79, e=103.01, w='mi'), dict(s=103.01, e=103.29, w='punim'), dict(s=103.29, e=103.69, w='srcem'),
       dict(s=103.69, e=104.39, w='poklanjate'), dict(s=104.39, e=104.63, w='svoje'), dict(s=104.63, e=105.21, w='poverenje.')]
FIX = {'najbollje': 'najbolje', 'razumejvanje,': 'razumevanje,', 'osečam': 'osećam', 'sorađujem': 'sarađujem', 'pacienti': 'pacijenti',
       'osjećati': 'osećati', 'sećete': 'sećate', 'sečete': 'sećate', 'osjećaja': 'osećaja', 'pointa': 'poenta', 'pripoznali': 'prepoznali.',
       'ali': 'Ali', 'prvom': 'prvom'}
words = []
for gi, g in enumerate(segs):
    for w in WW:
        mid = (w['s'] + w['e']) / 2
        if g['s'] - 0.02 <= mid <= g['e'] + 0.02:
            t = FIX.get(w['w'], w['w'])
            words.append(dict(s=offs[gi] + max(w['s'], g['s']) - g['s'], e=offs[gi] + min(w['e'], g['e']) - g['s'], w=t, beat=g['beat']))
json.dump(dict(words=words, segs=[dict(beat=g['beat'], dur=g['n'] / FPS) for g in segs], body=BODY),
          open(f'{W}/build/timeline.json', 'w'), ensure_ascii=False, indent=1)
print('body', round(BODY, 2)); print(' '.join(w['w'] for w in words))
