#!/usr/bin/env bash
# usage: EPISODE=p11 [HOOK=a|b] ./build.sh   -> delivery/<name>.mp4 + captions
set -e
cd "$(dirname "$0")"
EP=${EPISODE:-p11}
python3 audio.py
ffmpeg -v error -i raw_audio.wav -af "loudnorm=I=-14:TP=-1.5:LRA=9:linear=true" -ar 44100 audio.wav -y
python3 video.py "delivery/artista_misterioso_${EP}${HOOK:+_hook$HOOK}.mp4"
python3 captions.py "$EP" >/dev/null
