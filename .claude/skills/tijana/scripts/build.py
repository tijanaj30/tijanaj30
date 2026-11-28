#!/usr/bin/env python3
"""Cut an unboxing EDL into a 1080x1920/30fps base video (no audio) + a stitched raw-audio track.
usage: build.py EDL.json RAW_DIR OUT_DIR"""
import json, sys, subprocess, os
edl = json.load(open(sys.argv[1])); RAW = sys.argv[2]; OUT = sys.argv[3]
os.makedirs(f'{OUT}/seg', exist_ok=True)
zoom = 0.035   # gentle push-in per shot, alternating direction for energy
# iPhone footage is HDR (HLG / BT.2020, 10-bit): tone-map to SDR BT.709 or colours look pale
# grade matched to Tijana's own iPhone photo of the same jackets (deep berry, steel blue, neutral cream - never pale, never neon)
TONEMAP = ("zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=100,format=gbrpf32le,"
           "zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
           "eq=gamma=0.75:saturation=0.82,colorbalance=rm=-0.02:gm=-0.01:bm=0.02,")
def is_hlg(src):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=color_transfer',
                        '-of', 'csv=p=0', src], capture_output=True, text=True).stdout
    return 'arib-std-b67' in r or 'smpte2084' in r
# durations: seconds, or beats when edl['unit'] == 'beats' (cut boundaries snapped to whole frames, no drift)
beat = 60 / edl.get('bpm', 120)
bounds = [0]
for c in edl['cuts']:
    bounds.append(bounds[-1] + (c[2] * beat if edl.get('unit') == 'beats' else c[2]))
frames = [round(b * 30) for b in bounds]
segs = []
for i, (clip, t0, _, note) in enumerate(edl['cuts']):
    n = frames[i + 1] - frames[i]; d = n / 30
    src = f'{RAW}/{clip}.MOV'
    z0, z1 = (1.0, 1.0 + zoom) if i % 2 == 0 else (1.0 + zoom, 1.0)
    vf = ((TONEMAP if is_hlg(src) else '') + f"fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
          f"scale=2160:3840,zoompan=z='{z0}+({z1}-{z0})*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
          f":d=1:s=1080x1920:fps=30,setsar=1")
    o = f'{OUT}/seg/{i:02d}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t0), '-i', src, '-t', str(d), '-vf', vf,
                    '-frames:v', str(n), '-an', '-c:v', 'libx264', '-crf', '14', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-preset', 'fast',
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
print('total', frames[-1] / 30)
