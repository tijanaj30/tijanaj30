---
name: tijana
description: Edit Tijana's own TikTok/Instagram content — first format is fast "oprema / unboxing / haul" videos (sport gear hauls: bags, shoe boxes, packaged clothes dropped one by one onto a surface, ending in a flat-lay pile) with a centred meme text line and beat-synced cuts. Use when Tijana asks for her own unboxing / haul / oprema videos or says "Tijana skill". Do NOT use for client work (Laboratorija Olujić has its own skill).
---

# Tijana – unboxing / oprema house style

The user speaks Serbian; reply in Serbian. These are Tijana's own videos (not a client).

**Rule for editing this skill:** add or change anything here ONLY after Tijana explicitly confirms a result is what she wanted. Drafts, experiments and her corrections-in-progress stay out of the skill (keep them in the work folder or `plan/`). When she approves, write in only the final approved rules, not the history of fixes.

## Inspiration (what the format is)
Reference TikToks: Gymshark hauls (`vt.tiktok.com/ZSsAjW6Ny`, `vt.tiktok.com/ZSsA6h4BH`).
- Locked camera from above/at an angle on a clean surface (sofa, bed). Hands tear bags, items are **thrown/dropped into frame** one by one, the pile grows, last shot = full flat-lay.
- Very fast: a cut about every **1 s** (2 beats at 120 BPM), cuts land on the beat; no talking.
- One small white text line on screen for the whole video, plus a trending sound.

## Working rules – v1 draft (NOT yet approved by Tijana; replace with the approved version once she confirms)
- **Include ALL gear found in the raw footage** — every item must appear at least once (bag, box, shoes, each packaged piece, each unpacked piece, final pile). Make an inventory before cutting.
- Order = story: brand bag → box opened → shoes → packaged items dropping → unpacking each colour group → final pile build-up, end on the full pile with the shoes on top (hold ~2 s).
- Each cut starts with motion (item entering / landing), never on an empty sofa for more than a few frames. Check a start/mid/end contact sheet of every cut and shift in-points.
- Gentle alternating push-in/out (3.5 %) per cut for energy; 1080×1920, 30 fps.
- **Text**: centred in the middle of the frame (y ≈ 960), Montserrat 700 56 px, white, lowercase, soft dark shadow, visible from frame 0 for the whole video. Current line: "imala si stresan dan, / ali se setiš da imaš free will".
- **Sound**: two versions every time — `_muzika` (original 120 BPM pop beat from `music.py`, drop at ~4 s when the shoes come out, quiet original crinkle sound underneath −14 dB, −14 LUFS) and `_bez_muzike` (original sound only, for adding a trending TikTok/IG sound).

## Pipeline (scripts/)
1. Download raw clips from Drive: list the folder with the Drive connector, then `curl -L "https://drive.usercontent.google.com/download?id=ID&export=download&confirm=t"`. iPhone .MOV, portrait via rotation metadata (ffmpeg auto-rotates). Mixed 4K 29.97 and 1080p 30.
2. Contact sheets at 2 fps with timestamps to inventory gear and pick in-points.
3. EDL JSON (`edl_unboxing_ua.json` = first approved example): `[clip, in_sec, dur_sec, note]`, durations in beats (0.5 s multiples).
4. `build.py EDL RAW_DIR BUILD_DIR` → `base.mp4` (no audio) + `raw_audio.wav`.
5. `text_overlay.py "line1\nline2" BUILD_DIR/text.png [y] [size]`.
6. `music.py TOTAL BUILD_DIR/music.wav 120 4.0` (total = sum of EDL durations; drop time in seconds).
7. `finish.sh BUILD_DIR OUT_PREFIX` → `OUT_PREFIX_muzika.mp4` and `OUT_PREFIX_bez_muzike.mp4` (video and audio rendered separately, then muxed).

Fonts are in `assets/fonts/` (Montserrat 600/700/800).
