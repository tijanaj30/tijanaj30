import sys,numpy as np
from PIL import Image,ImageFilter
for v in sys.argv[1:]:
    im=Image.open(f'raw{v}.png').convert('RGB'); W,H=im.size
    a=np.asarray(im).astype(np.float32)
    b1=np.asarray(im.filter(ImageFilter.GaussianBlur(5))).astype(np.float32)
    b2=np.asarray(im.filter(ImageFilter.GaussianBlur(2.2))).astype(np.float32)
    y=np.linspace(0,1,H)[:,None,None]
    far=np.clip(1-np.abs(y-0.42)/0.16,0,1)**1.2          # horizon band blur
    near=np.clip((y-0.9)/0.1,0,1)                          # bottom foreground blur
    out=a*(1-far)+b1*far; out=out*(1-near)+b2*near
    rng=np.random.default_rng(int(v)); g=rng.normal(0,1,(H,W)); 
    g=np.asarray(Image.fromarray(((g*40)+128).clip(0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.6))).astype(np.float32)-128
    yy,xx=np.mgrid[0:H,0:W]; vig=1-0.10*(((xx/W-.5)**2+(yy/H-.55)**2)*2.2)
    out=out*vig[...,None]
    lum=out.mean(axis=2,keepdims=True); m=np.percentile(lum,55)
    k=float(sys.argv[0] and 1.75)
    out=out+(lum-m)*(k-1)*1.0  # luminance contrast around mid
    out=out*np.array([1.0,0.985,0.955])  # warm
    out=out+g[...,None]*0.07
    Image.fromarray(out.clip(0,255).astype(np.uint8)).save(f'bg{v}.png')
