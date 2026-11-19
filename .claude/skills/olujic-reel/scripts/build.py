#!/usr/bin/env python3
"""Build the Lujić reel: multicam cut + lav audio + animated captions + logo end card."""
import json, subprocess, os, re
import numpy as np
from scipy.io import wavfile

W = '/home/user/work'
OFF = 0.599          # t_5300 = t_1127 - OFF
FPS = 30
SPEED = 1.06
END_CARD = 2.2

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:]); raise SystemExit(cmd)
    return r.stdout

# ---------- loudness envelope of lav mic (in 1127 time) ----------
sr16, x16 = wavfile.read(f'{W}/audio/MVI_5300_16k.wav')
x16 = x16.astype(float) / 32768
fr = x16[:len(x16)//160*160].reshape(-1, 160)
DB = 20*np.log10(np.sqrt((fr**2).mean(1)) + 1e-9)
def db_at(t): return DB[int(round((t-OFF)*100))]

def snap_start(t, lo=0.04, hi=0.5, thr=-30):
    """First loud frame within [t-lo, t+hi], minus small pre-roll."""
    for k in range(int((t-lo)*100), int((t+hi)*100)):
        if db_at(k/100) > thr: return max(k/100 - 0.07, t-lo)
    return t
def snap_end(t, lo=0.5, hi=0.04, thr=-30):
    last = None
    for k in range(int((t-lo)*100), int((t+hi)*100)):
        if db_at(k/100) > thr: last = k/100
    return min(last + 0.10, t + hi) if last else t

# ---------- edit decision list (times in MVI_1127 timeline) ----------
# shot: A = main angle, A2 = main punch-in, B = side angle
# (start, end, shot, text, snapS, snapE)
EDL = [
 (19.55, 24.70, 'A',  'Dobili ste nove zube, probate ih, ali nešto tu vam se ne dopada.', 1, 1),
 (24.72, 25.80, 'A2', 'I šta dalje?', 0, 0),
 (26.98, 30.00, 'B',  'Stomatolog uzima rad, vraća zubnom tehničaru,', 0, 0),
 (30.00, 37.10, 'A',  'zubni tehničar prepravlja rad, vraća stomatologu, opet probate, ali opet tu nešto nije kako treba.', 0, 1),
 (41.38, 43.30, 'B',  'I tako u krug.', 0, 0),
 (43.30, 50.28, 'A',  'Zapravo osoba koja vam je pravila zube nije tu da direktno od vas čuje šta se treba prepraviti.', 0, 0),
 (50.70, 53.20, 'A2', 'Zato mi radimo drugačije.', 1, 0),
 (53.40, 58.10, 'B',  'Ja sam tu pre početka rada, da popričamo, da se upoznamo.', 1, 1),
 (58.30, 61.00, 'A',  'Tu sam kada probamo privremene krune.', 1, 1),
 (87.10, 89.95, 'A2', 'Tu sam i kad isprobavate završni rad.', 1, 1),
 (90.28, 92.10, 'B',  'Ako vam se nešto ne dopada,', 1, 0),
 (93.27, 98.60, 'A',  'želim da to čujem direktno od vas. Šta čuvamo, šta menjamo ili ne menjamo ništa.', 0, 1),
 (117.74, 120.05, 'A', 'Jer kada smo svi zajedno uključeni u proces', 0, 0),
 (120.40, 124.30, 'B', 'i lepo iskomuniciramo, mnogo se lakše razumemo i dogovorimo.', 0, 1),
 (171.60, 176.40, 'A', 'Ako planirate nove zube i smatrate da je ovakav pristup za vas,', 1, 1),
 (177.10, 182.25, 'A2', 'pišite mi. Tu sam da se upoznamo, popričamo i napravimo dobar plan.', 1, 1),
]
EMPH = {'nove', 'zube,', 'zube', 'krug.', 'drugačije.', 'direktno', 'zajedno', 'pišite', 'mi.', 'dogovorimo.', 'plan.'}

segs = []
for s, e, shot, text, ss, se in EDL:
    if ss: s = snap_start(s)
    if se: e = snap_end(e)
    f0, f1 = round(s*FPS), round(e*FPS)
    segs.append(dict(s=f0/FPS, e=f1/FPS, n=f1-f0, shot=shot, text=text))
for g in segs:
    print(f"{g['s']:7.2f}-{g['e']:7.2f} {g['shot']:2} {g['n']/FPS:5.2f}s  {g['text'][:50]}")
total = sum(g['n'] for g in segs)/FPS
print('speech total', round(total, 2), '-> after speed', round(total/SPEED, 2), '+ end card', round(total/SPEED+END_CARD, 2))

# ---------- video segments ----------
os.makedirs(f'{W}/build', exist_ok=True)
FRAMING = {  # source, face centre (fx, fy) as fraction, zoom start->end
    'A':  ('MVI_1127', 0.445, 0.36, 1.00, 1.05),
    'A2': ('MVI_1127', 0.445, 0.33, 1.32, 1.38),
    'B':  ('MVI_5300', 0.56, 0.32, 1.04, 1.09),
}
for i, g in enumerate(segs):
    src, fx, fy, z0, z1 = FRAMING[g['shot']]
    t0 = g['s'] - (OFF if src == 'MVI_5300' else 0)
    N = g['n']
    z = f"{z0}+({z1-z0})*on/{max(N-1,1)}"
    x = f"max(0,min(iw-iw/zoom,{fx}*iw-iw/zoom/2))"
    y = f"max(0,min(ih-ih/zoom,{fy}*ih-ih/zoom/2))"
    vf = f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s=1080x1920:fps={FPS},setsar=1"
    out = f'{W}/build/seg{i:02d}.mp4'
    if not os.path.exists(out):
        run(f"ffmpeg -v error -y -ss {t0:.3f} -i {W}/src/{src}.mov -frames:v {N} -an -vf \"{vf}\" "
            f"-c:v libx264 -preset fast -crf 15 -pix_fmt yuv420p -r {FPS} {out}")
    print('video', i, 'ok')

# ---------- audio (lav mic, 5300) ----------
sr, a = wavfile.read(f'{W}/audio/MVI_5300_full.wav')
a = a.astype(np.float32) / 32768
parts = []
fade = int(0.012*sr)
for g in segs:
    i0 = int(round((g['s']-OFF)*sr)); n = int(round(g['n']/FPS*sr))
    p = a[i0:i0+n].copy()
    ramp = np.linspace(0, 1, fade)[:, None]
    p[:fade] *= ramp; p[-fade:] *= ramp[::-1]
    parts.append(p)
aud = np.concatenate(parts)
wavfile.write(f'{W}/build/speech.wav', sr, (aud*32767).astype(np.int16))

with open(f'{W}/build/list.txt', 'w') as f:
    for i in range(len(segs)): f.write(f"file 'seg{i:02d}.mp4'\n")
run(f"ffmpeg -v error -y -f concat -safe 0 -i {W}/build/list.txt -c copy {W}/build/body_raw.mp4")

# ---------- captions (word timings from whisper, text from script) ----------
wj = json.load(open(f'{W}/audio/transcript_1127.json'))
WW = [w for s in wj['segments'] for w in s['words']]
cap_words = []  # (out_start, out_end, word)
acc = 0.0
for g in segs:
    words = g['text'].split()
    ww = [w for w in WW if g['s']-0.05 <= (w['start']+w['end'])/2 <= g['e']+0.05]
    if len(ww) == len(words):
        times = [(max(w['start'], g['s']), min(w['end'], g['e'])) for w in ww]
    else:  # distribute by character length over voiced span
        a0 = ww[0]['start'] if ww else g['s']; a1 = ww[-1]['end'] if ww else g['e']
        a0 = max(a0, g['s']); a1 = min(a1, g['e'])
        L = np.cumsum([0]+[len(w)+1 for w in words]); L = L/L[-1]
        times = [(a0+(a1-a0)*L[k], a0+(a1-a0)*L[k+1]) for k in range(len(words))]
        print('  (distributed timing)', g['text'][:40], len(ww), len(words))
    for (ts, te), w in zip(times, words):
        cap_words.append(((acc+ts-g['s'])/SPEED, (acc+te-g['s'])/SPEED, w))
    acc += g['n']/FPS
body_len = acc/SPEED

# group into chunks of <=3 words, break after punctuation
chunks, cur = [], []
for cw in cap_words:
    cur.append(cw)
    if len(cur) == 3 or re.search(r'[.,?!]$', cw[2]) or (len(cur) == 2 and len(cw[2]) > 9):
        chunks.append(cur); cur = []
if cur: chunks.append(cur)

def ts(t):
    t = max(t, 0); h = int(t//3600); m = int(t % 3600//60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
TEAL = '&H00C4DB3E&'; WHITE = '&H00FFFFFF&'
ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 0", "",
       "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Cap,Montserrat ExtraBold,78,&H00FFFFFF,&H00FFFFFF,&H70141414,&H90000000,0,0,0,0,100,100,0,0,1,4,2,2,80,80,560,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
def word_tag(w, active):
    clean = w.upper()
    if w.lower() in EMPH:
        return r"{\fnPlayfair Display\i1\fs92\c" + TEAL + "}" + w.lower() + r"{\fnMontserrat ExtraBold\i0\fs78\c" + WHITE + "}"
    if active:
        return r"{\c" + TEAL + "}" + clean + r"{\c" + WHITE + "}"
    return clean
for ci, ch in enumerate(chunks):
    c_start = ch[0][0]
    c_end = chunks[ci+1][0][0] if ci+1 < len(chunks) and chunks[ci+1][0][0]-ch[-1][1] < 0.6 else ch[-1][1]+0.15
    c_end = min(c_end, body_len)
    for wi, (w0, w1, w) in enumerate(ch):
        st = c_start if wi == 0 else w0
        en = ch[wi+1][0] if wi+1 < len(ch) else c_end
        if en <= st: continue
        pop = r"{\fscx85\fscy85\t(0,90,\fscx100\fscy100)}" if wi == 0 else ""
        txt = " ".join(word_tag(x[2], k == wi) for k, x in enumerate(ch))
        ass.append(f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{pop}{txt}")
open(f'{W}/build/captions.ass', 'w').write("\n".join(ass)+"\n")

# ---------- body: speed + captions + audio ----------
run(f"ffmpeg -v error -y -i {W}/build/body_raw.mp4 -i {W}/build/speech.wav "
    f"-filter_complex \"[0:v]setpts=PTS/{SPEED},fps={FPS},ass={W}/build/captions.ass:fontsdir=/root/.fonts[v];"
    f"[1:a]atempo={SPEED},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]\" "
    f"-map [v] -map [a] -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 {W}/build/body.mp4")

# ---------- end card: blurred last frame + logo ----------
last = segs[-1]
run(f"ffmpeg -v error -y -ss {last['e']-0.1:.3f} -i {W}/src/MVI_1127.mov -frames:v 1 -vf scale=1080:1920 {W}/build/last.png")
D = END_CARD
run(f"ffmpeg -v error -y -loop 1 -t {D} -i {W}/build/last.png -loop 1 -t {D} -i {W}/logo_crop.png "
    f"-f lavfi -t {D} -i anullsrc=r=48000:cl=stereo -filter_complex "
    f"\"[0:v]gblur=sigma=40,eq=brightness=-0.18:saturation=0.8,format=yuv420p,fade=in:st=0:d=0.25[bg];"
    f"[1:v]scale=760:-1,format=rgba,fade=in:st=0.15:d=0.45:alpha=1[lg];"
    f"[bg][lg]overlay=(W-w)/2:(H-h)/2-80,"
    f"drawtext=fontfile=/root/.fonts/f3.ttf:text='Pišite nam — tu smo za vas':fontcolor=white:fontsize=56:"
    f"x=(w-tw)/2:y=h*0.5+330:alpha='if(lt(t,0.6),0,min(1,(t-0.6)/0.4))',fps={FPS}[v]\" "
    f"-map [v] -map 2:a -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 {W}/build/endcard.mp4")

with open(f'{W}/build/final_list.txt', 'w') as f:
    f.write("file 'body.mp4'\nfile 'endcard.mp4'\n")
run(f"ffmpeg -v error -y -f concat -safe 0 -i {W}/build/final_list.txt -c copy -movflags +faststart {W}/build/final.mp4")
print(run(f"ffprobe -v error -show_entries format=duration -of csv=p=0 {W}/build/final.mp4"))

# ---------- v2: clean base (no burned captions) + timeline for motion graphics ----------
acc = 0.0; seg_out = []
for g in segs:
    d = g['n']/FPS
    seg_out.append(dict(s=acc/SPEED, e=(acc+d)/SPEED, shot=g['shot'], text=g['text'])); acc += d
json.dump(dict(segs=seg_out, words=[dict(s=a, e=b, w=w) for a, b, w in cap_words],
               body=body_len, end=END_CARD, emph=sorted(EMPH)),
          open(f'{W}/build/timeline.json', 'w'), ensure_ascii=False, indent=1)
run(f"ffmpeg -v error -y -i {W}/build/body_raw.mp4 -i {W}/build/speech.wav "
    f"-filter_complex \"[0:v]setpts=PTS/{SPEED},fps={FPS}[v];"
    f"[1:a]atempo={SPEED},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]\" "
    f"-map [v] -map [a] -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 {W}/build/body_clean.mp4")
run(f"ffmpeg -v error -y -loop 1 -t {D} -i {W}/build/last.png -f lavfi -t {D} -i anullsrc=r=48000:cl=stereo "
    f"-filter_complex \"[0:v]gblur=sigma=40,eq=brightness=-0.22:saturation=0.75,format=yuv420p,fps={FPS}[v]\" "
    f"-map [v] -map 1:a -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 {W}/build/endbg.mp4")
with open(f'{W}/build/base_list.txt', 'w') as f:
    f.write("file 'body_clean.mp4'\nfile 'endbg.mp4'\n")
run(f"ffmpeg -v error -y -f concat -safe 0 -i {W}/build/base_list.txt -c copy {W}/build/base.mp4")
print('base', run(f"ffprobe -v error -show_entries format=duration -of csv=p=0 {W}/build/base.mp4"))
