#!/usr/bin/env python3
"""Cut an unboxing EDL into a 1080x1920/30fps base video (no audio) + a stitched raw-audio track.
usage: build.py EDL.json RAW_DIR OUT_DIR"""
import json, sys, subprocess, os
edl = json.load(open(sys.argv[1])); RAW = sys.argv[2]; OUT = sys.argv[3]
os.makedirs(f'{OUT}/seg', exist_ok=True)
zoom = 0.035   # gentle push-in per shot, alternating direction for energy
segs = []
for i, (clip, t0, d, note) in enumerate(edl['cuts']):
    src = f'{RAW}/{clip}.MOV'
    z0, z1 = (1.0, 1.0 + zoom) if i % 2 == 0 else (1.0 + zoom, 1.0)
    n = round(d * 30)
    vf = (f"fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
          f"scale=2160:3840,zoompan=z='{z0}+({z1}-{z0})*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
          f":d=1:s=1080x1920:fps=30,setsar=1")
    o = f'{OUT}/seg/{i:02d}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t0), '-i', src, '-t', str(d), '-vf', vf,
                    '-frames:v', str(n), '-an', '-c:v', 'libx264', '-crf', '14', '-preset', 'fast',
                    '-pix_fmt', 'yuv420p', o], check=True)
    a = f'{OUT}/seg/{i:02d}.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t0), '-i', src, '-t', str(d), '-vn',
                    '-af', f'aresample=48000,afade=t=in:d=0.02,afade=t=out:st={d-0.03}:d=0.03,apad=whole_dur={d}',
                    '-ac', '2', o.replace('.mp4', '.wav')], check=True)
    segs.append(o)
with open(f'{OUT}/list.txt', 'w') as f:
    for s in segs: f.write(f"file '{os.path.abspath(s)}'\n")
with open(f'{OUT}/alist.txt', 'w') as f:
    for s in segs: f.write(f"file '{os.path.abspath(s.replace('.mp4', '.wav'))}'\n")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt', '-c', 'copy', f'{OUT}/base.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/alist.txt', f'{OUT}/raw_audio.wav'], check=True)
print('total', sum(c[2] for c in edl['cuts']))
