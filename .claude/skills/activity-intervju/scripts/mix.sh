#!/bin/bash
# speech + sidechain-ducked music (time-stretched to the video length) + SFX -> build/mix.wav
# run from /home/user/work/act after build.py, dumpA.js (> build/A.json) and sfx.py
DUR=$(python3 -c "import json;print(round(json.load(open('build/timeline.json'))['body']+3.47,2))")
MD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 audio/music.wav)
TEMPO=$(python3 -c "print(max(0.5,min(1.0,$MD/$DUR)))")   # stretch only if music is shorter (<=7% is inaudible)
BODY=$(python3 -c "import json;print(json.load(open('build/timeline.json'))['body'])")
ffmpeg -v error -y -i audio/music.wav -i build/speech.wav -i build/sfx.wav -filter_complex "
[0:a]aresample=48000,atempo=$TEMPO,loudnorm=I=-16:TP=-2,volume='0.42+0.30*min(max((t-($BODY-0.25))/0.9,0),1)':eval=frame,afade=t=out:st=$(python3 -c "print($DUR-1.3)"):d=1.3,apad=whole_dur=$DUR[m];
[1:a]apad=whole_dur=$DUR,asplit[s1][s2];
[m][s1]sidechaincompress=threshold=0.04:ratio=2.5:attack=40:release=400:makeup=1[md];
[2:a]volume=0.35[fx];
[s2][md][fx]amix=inputs=3:normalize=0:duration=longest,alimiter=limit=0.89,atrim=0:$DUR[a]" -map "[a]" -ar 48000 -c:a pcm_s16le build/mix.wav
echo "mix: $DUR s (music tempo $TEMPO)"
