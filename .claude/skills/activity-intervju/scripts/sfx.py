import json, numpy as np, subprocess
from scipy.io import wavfile
SR=48000; A=json.load(open('build/A.json')); BODY=json.load(open('build/timeline.json'))['body']; TOT=BODY+3.47
N=int(TOT*SR)+SR
def pop(f0=900,f1=520,d=0.09,v=1.0):
    t=np.arange(int(d*SR))/SR; f=np.geomspace(f0,f1,len(t)); ph=2*np.pi*np.cumsum(f)/SR
    return v*np.sin(ph)*np.exp(-t*38)*np.minimum(1,t*800)
def tick(v=1.0):
    t=np.arange(int(0.05*SR))/SR; return v*(np.sin(2*np.pi*2400*t)*.6+np.sin(2*np.pi*3600*t)*.3)*np.exp(-t*90)
def whoosh(d=0.6,v=1.0,rise=True):
    n=int(d*SR); x=np.random.default_rng(3).standard_normal(n)
    from scipy.signal import butter, sosfilt
    out=np.zeros(n); seg=2048
    for i in range(0,n,seg):
        k=i/n; fc=300+2500*(k if rise else 1-k)
        sos=butter(2,[fc*0.6,fc*1.6],'bandpass',fs=SR,output='sos'); out[i:i+seg]=sosfilt(sos,x[i:i+seg])
    env=np.sin(np.pi*np.linspace(0,1,n))**2; return v*out*env/np.abs(out).max()
def shimmer(v=1.0):
    t=np.arange(int(1.2*SR))/SR; y=sum(np.sin(2*np.pi*f*t)*np.exp(-t*(3+i)) for i,f in enumerate([1568,2093,2637,3136]))
    return v*y*np.minimum(1,t*60)/4
fx=np.zeros(N)
def add(t,s):
    i=int(t*SR); fx[i:i+len(s)]+=s[:max(0,N-i)]
P=lambda: pop()
for t in [0.15,A['tKafu']-0.15,A['tNem']-0.3,A['tTri']-.1,A['cardIgr'][1]-.1,A['tInter']-.1,A['tBuk']-.05,
          A['tPauz']-.15,A['cardOrg'][1]-.1,A['tFeed']-.15,A['tPrez']-.1]: add(t,pop())
for t in [A['tSvak']-.1,A['cardIgr'][1]+.6,A['tInter'],A['tUklj']-.1,A['cardOrg'][1]+.15,A['cardOrg'][1]+.4,A['cardOrg'][1]+.65,A['tSav']-.05,
          A['cardIgr'][0]+.75,A['cardOrg'][0]+.7,A['cardOrg'][0]+.98,A['cardOrg'][0]+1.26]: add(t,tick(.8))
for j in range(5): add(A['tFeed']+.25+j*.12,pop(1300+j*120,900+j*100,0.06,.6))
for c in ['cardIgr','cardOrg']: add(A[c][0]-.2,whoosh(0.45,.8)); add(A[c][1]-.1,whoosh(0.4,.5,False))
add(3.2,whoosh(1.4,.9)); add(A['tCak']-.35,whoosh(0.7,.8)); add(BODY-0.25,whoosh(1.2,.9)); add(BODY+0.6,shimmer(.8))
fx=fx/np.abs(fx).max()*0.5
wavfile.write('build/sfx.wav',SR,fx.astype(np.float32))
