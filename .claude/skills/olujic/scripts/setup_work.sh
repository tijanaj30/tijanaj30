#!/bin/bash
# Restore fonts/logo to the paths the overlays expect (/home/user/work/...)
D=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p /home/user/work/v2/fonts /home/user/work/r6/fonts /home/user/work/scripts
cp "$D"/assets/fonts/Montserrat-* "$D"/assets/fonts/PlayfairDisplay-* /home/user/work/v2/fonts/
cp "$D"/assets/fonts/CormorantGaramond-* "$D"/assets/fonts/Jost-* /home/user/work/r6/fonts/
cp "$D"/assets/logo2_t.png /home/user/work/logo2_t.png
cp "$D"/scripts/sfx.py /home/user/work/scripts/sfx.py
echo "Olujić assets restored to /home/user/work"
