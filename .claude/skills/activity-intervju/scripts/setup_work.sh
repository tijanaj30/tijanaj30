#!/bin/bash
# Prepares /home/user/work/act (the paths all scripts use): fonts, logo, scripts, segmentation model.
set -e
K="$(cd "$(dirname "$0")/.." && pwd)"; W=/home/user/work/act
mkdir -p $W/{src,build,frames,masks,models,fonts,assets,audio}
cp $K/assets/fonts/* $W/fonts/; cp $K/assets/logo_t.png $W/assets/
cp $K/scripts/{build.py,seg.py,render.js,sfx.py,mix.sh,dumpA.js,overlay.html,overlay_v2_alt.html,denoise.py,music_hype.py} $W/
command -v ffmpeg >/dev/null || (apt-get update && apt-get install -y ffmpeg)
ldconfig -p | grep -q libEGL.so.1 || (apt-get update -q && apt-get install -y -q libegl1 libgles2)
pip install -q noisereduce openai-whisper scipy numpy pillow opencv-python-headless==4.10.0.84 mediapipe
[ -s $W/models/seg.tflite ] || curl -sSL -o $W/models/seg.tflite \
  https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite
echo "work dir ready: $W"
