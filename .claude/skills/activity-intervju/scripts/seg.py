# usage: seg.py f0 f1  -> masks/mNNNNN.png (person alpha, same space as frames/fNNNNN.jpg; index = frame+1)
import sys, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
D='/home/user/work/act'
seg=vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=f'{D}/models/seg.tflite'),output_confidence_masks=True))
for f in range(int(sys.argv[1]),int(sys.argv[2])):
    im=cv2.imread(f'{D}/frames/f{f+1:05d}.jpg'); rgb=cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
    r=seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb))
    a=1-r.confidence_masks[0].numpy_view()
    a=cv2.resize(a,(im.shape[1],im.shape[0]),interpolation=cv2.INTER_LINEAR)
    # edge-aware refine
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)/255
    try: a=cv2.ximgproc.guidedFilter(g,a.astype(np.float32),8,1e-3)
    except Exception: a=cv2.GaussianBlur(a,(5,5),0)
    a=np.clip((a-0.35)/0.3,0,1)
    cv2.imwrite(f'{D}/masks/m{f+1:05d}.png',(a*255).astype(np.uint8))
