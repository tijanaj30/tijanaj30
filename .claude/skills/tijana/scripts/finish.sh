#!/bin/bash
# usage: finish.sh BUILD_DIR OUT_PREFIX   (needs base.mp4, raw_audio.wav, music.wav, text.png in BUILD_DIR)
# Renders video and audio separately, then muxes (avoids A/V drift).
set -e
B=$1; O=$2
ffmpeg -v error -y -i $B/base.mp4 -loop 1 -i $B/text.png -filter_complex \
 "[0]tpad=stop_mode=clone:stop_duration=0.8[v];[1]format=rgba,fade=t=in:st=0:d=0.15:alpha=1[t];[v][t]overlay=0:0:shortest=1,format=yuv420p" \
 -an -c:v libx264 -crf 18 -preset medium -r 30 $B/video.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $B/video.mp4)
# music version: music + quiet original crinkle sound (ASMR texture)
ffmpeg -v error -y -i $B/music.wav -i $B/raw_audio.wav -filter_complex \
 "[1]highpass=f=120,volume=-14dB,apad[r];[0]volume=-1dB[m];[m][r]amix=inputs=2:normalize=0:duration=first,atrim=0:$D,afade=t=out:st=$(echo "$D-0.4"|bc):d=0.4,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.89" \
 -ar 48000 $B/mix_music.wav
# no-music version: original sound only (for adding a trending sound in TikTok/IG)
ffmpeg -v error -y -i $B/raw_audio.wav -af "highpass=f=80,apad,atrim=0:$D,loudnorm=I=-16:TP=-1.5" -ar 48000 $B/mix_raw.wav
ffmpeg -v error -y -i $B/video.mp4 -i $B/mix_music.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart ${O}_muzika.mp4
ffmpeg -v error -y -i $B/video.mp4 -i $B/mix_raw.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart ${O}_bez_muzike.mp4
echo done
