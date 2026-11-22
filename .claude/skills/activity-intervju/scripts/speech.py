# assemble speech from timeline segments (clean sources), loudness chain, then gate pauses to silence
import json, subprocess, numpy as np
from scipy.io import wavfile
from scipy.ndimage import maximum_filter1d, uniform_filter1d
tl=json.load(open('build/timeline.json')); FPS=30; SR=48000
SRC={'IMG_8640b':'src/IMG_8640b_dn3.wav','IMG_8641':'src/IMG_8641_dnb.wav','IMG_8642':'src/IMG_8642_dnb.wav'}
A={k:wavfile.read(v)[1].astype(np.float32)/32768 for k,v in SRC.items()}
parts=[]; f=int(.012*SR)
for g in tl['segs']:
    a=A[g['src']]; i0=int(round(g['s']*SR)); n=int(round(g['n']/FPS*SR)); p=a[i0:i0+n].copy()
    if len(p)<n: p=np.pad(p,(0,n-len(p)))
    r=np.linspace(0,1,f); p[:f]*=r; p[-f:]*=r[::-1]; parts.append(p)
x=np.concatenate(parts); x[int((tl['body']-0.08)*SR):]=0
wavfile.write('build/sp7_raw.wav',SR,x)
import os, sys
RAW = sys.argv[1] if len(sys.argv) > 1 else 'build/sp7_raw.wav'
subprocess.run(f'ffmpeg -v error -y -i {RAW} -af "highpass=f=90,equalizer=f=300:t=q:w=1.2:g=-2.5,equalizer=f=3500:t=q:w=1.5:g=2.5,acompressor=threshold=0.08:ratio=3:attack=5:release=100,loudnorm=I=-11:TP=-1:LRA=5,alimiter=limit=0.93" -ar 48000 build/sp7_proc.wav',shell=True,check=True)
_,y=wavfile.read('build/sp7_proc.wav'); y=y.astype(np.float32)/(32768 if y.dtype==np.int16 else 1)
h=SR//100; fr=y[:len(y)//h*h].reshape(-1,h); db=20*np.log10(np.sqrt((fr**2).mean(1))+1e-9)
g=(db>np.percentile(db,90)-20).astype(float); g=maximum_filter1d(g,22); g=uniform_filter1d(g,4)
g=10**(-40*(1-g)/20); g=np.repeat(g,h); g=np.pad(g,(0,len(y)-len(g)),mode='edge')
y=y*g; wavfile.write('build/speech_v7.wav',SR,y.astype(np.float32))
d=20*np.log10(np.sqrt((y[:len(y)//h*h].reshape(-1,h)**2).mean(1))+1e-9)
print('first10s q10/med/q90', np.percentile(d[:1000],[10,50,90]).round(), 'all', np.percentile(d,[10,50,90]).round())
