# masks/mNNNNN.png + frames/fNNNNN.jpg -> cuts/cNNNNN.png (RGBA person cut-outs used by the overlay's #person layer;
# CSS mask-image from file:// does not load in headless Chromium, so the alpha is baked in here)
import cv2, numpy as np, glob, os
os.makedirs('cuts', exist_ok=True)
for m in sorted(glob.glob('masks/m*.png')):
    n = os.path.basename(m)[1:6]; im = cv2.imread(f'frames/f{n}.jpg'); a = cv2.imread(m, 0)
    cv2.imwrite(f'cuts/c{n}.png', np.dstack([im, a]), [cv2.IMWRITE_PNG_COMPRESSION, 1])
