---
name: activity-intervju
description: Edit interview / testimonial reels for Activity školica sporta (Activity Centar – sportski rođendani) in the client's editorial reference style — small centred word-by-word captions with one huge Inter Black word and Playfair italic accents, text BEHIND the subject (person segmentation), white full-screen cards with B&W cut-outs, glass widgets with count-ups, pullback reveals, white end card with a typing search bar; colours white + #1b263a. Use when the request concerns Activity / Activity školica sporta / Activity Centar video footage. Not for Laboratorija Olujić (that has its own skill).
---

# Activity školica sporta – interview reel style & pipeline

The user speaks Serbian; reply in Serbian (ekavica in all on-screen text).
Client: **Activity Centar – Školica sporta** (sportski rođendani za decu 3–12 god., animatori, poligoni, pena party).
Web/IG: `www.activitycentar.com`, `@activityskolica`. Offer PDF on Drive: "Activity - rođendanska ponuda.pdf"; logo: "Novi logo ACTIVITY.pdf" (already extracted to `assets/logo_t.png`, transparent).
Audiences of the interview reels: **parents** (bez brige, deca uživaju) and **owners of other venues** (Activity preuzima organizaciju) — every edit should speak to both.

**First step:** `bash .claude/skills/activity-intervju/scripts/setup_work.sh` → creates `/home/user/work/act` (all scripts use that path), fonts, logo, mediapipe + segmentation model (needs storage.googleapis.com, already reachable).

## Look (built from the 4 client reference edits, Drive ids below)
Colours: **white + navy `#1b263a`** only. Fonts: **Inter** (Light–Bold) + **Inter Display Black** (big words, letter-spacing −0.045em, line-height .85) + **Playfair Display italic** (accents). No Montserrat, no gradients-on-text, no Olujić-style bottom captions.
- **Captions**: centred, at chest height (`#cap top:1120px`), *small* (Inter 500, 46 px, white, soft drop shadow), 1–4 words at a time, each word fades/blur-rises in on its own timestamp. One **emphasis word** per phrase goes on its own line in huge Inter Display Black (≈ min(150, 960/(0.56·len)) px), small words stack tightly above/below it (ref1 "we / *actually* / have over"). Accent words (bukvalno, zaista, apsolutno, svakodnevno…) in Playfair italic 64 px. Edit the `EMPH` / `ACC` sets in `overlay.html` per video.
- **Text behind subject** (ref2 "the truth", ref3 "captions"): giant navy Inter Black / Playfair italic placed on the bright wall *behind* the person, person re-composited on top with a per-frame mask (`seg.py` → `masks/`). Used for: the hook ("bukvalno **2,5h**", attached to the wall so it moves with the pullback), the emotional punchline ("čak i kad sviramo kraj — neće da idu **kući.**", built up word by word across the whole sentence), and the closing line ("najbolja **preporuka**" behind both people). Letters must be partly covered by the head — check frames. Front subtitle below (white Playfair italic) is fine.
- **White full-screen cards** (ref1/ref4): `#f5f5f3` with a faint 90 px navy grid, navy type (small Inter line → huge Inter Black word → Playfair italic line), B&W cut-out of the speaker/duo (from masks, CLAHE, faded bottom) in the lower half. ~1.4–2.6 s, quick blur-scale in/out, speech keeps running underneath. Used for a key statement ("klasične **igraonice** ~~strike~~ *su prevaziđene.*") and for the section question for venue owners (pill "ZA VLASNIKE PROSTORA").
- **Glass widgets** (user request + ref4 "997,602 views" pop card): `rgba(255,255,255,.6)` + `backdrop-filter: blur(28px)` — this only works because the video frame is inside the same page (frames are composited in the browser, not as a transparent overlay). Navy text, small caps label, check rows with navy dots, **numbers count up** (3 školice, 0→2,5h bar, 0,0→5,0 + stars). Always placed ABOVE the heads (top 190–560 px), never over a face.
- **Bottom overlay**: soft navy gradient from the bottom at reduced opacity, ONLY on text-only moments (hook, "kući", "preporuka").
- **Camera**: framing per segment via `SHOT` presets (tight/own/own2/qwide/wide/c1/c2) with slow drift; **pullback reveal** from the tight hook into the wide two-shot across the first cut (t 3.3→5.1 s).
- **End card** (ref3/ref4 outro): video pulls back into a rounded card and fades, white card with logo, "sportski rođendani / **3–12 god.** / *bez brige za roditelje*", navy search bar typing `@activityskolica`, line "roditelji · vlasnici prostora — javite nam se".

## Content rules (from client feedback)
- Keep ONLY the owner talking and the interviewer's questions. **Cut everything else** — e.g. a child running into frame, kicking the ball, "Bravo!" etc. is never used.
- Remove pauses/retakes, never cut inside a word (12 ms fades), verify by re-transcribing `build/speech.wav`.
- Spelling fixes in `build.py` `FIX` (ijekavica → ekavica: osetio, ovde, dece, hteli; fudbalskom; Bežanijskoj; kafić…).
- Story order that worked (≈65 s + 3.5 s end card): hook punchline → name card → Q1 (zašto balon) → A1 (3 školice, drugačije/modernije, igraonice prevaziđene) → Q2 (po čemu se pristup razlikuje) → A2 (interakcija, 2,5h uživanja, pauza za sokiće, neće da idu kući) → Q3 venue owners → A3 (ništa ne radim oko organizacije, feedback roditelja savršen, prezadovoljni) → "najbolja preporuka" → end card.

## Music & sound
- Music: inspirational/sporty instrumental, **quiet** under speech (−6 dB bed, sidechain-ducked, rises on the end card). Generated with Higgsfield `elevenlabs_music_v2_5` (`force_instrumental:true`, ~0.145 credits/s) — download host `d8j0ntlcm91z4.cloudfront.net` is in the environment allow-list. `mix.sh` time-stretches it to the video length.
- SFX (`sfx.py`, synthesized): soft pops on widgets, ticks on check rows/stars, whooshes on cards/pullback, shimmer on the logo, typing ticks on the search bar. Edit the event list per video (times come from `build/A.json`).

## Pipeline (`/home/user/work/act`)
1. Download clips: `curl -L "https://drive.usercontent.google.com/download?id=ID&export=download&confirm=t"` (the Drive connector refuses files > 10 MB). Extract 48 kHz mono wavs to `src/`.
2. Whisper medium, `language='sr'`, word timestamps → `src/<clip>.MOV.json`.
3. `build.py`: edit `EDL` (src, start, end, beat, shot) → `build/base.mp4`, `build/speech.wav`, `build/timeline.json` (segments + corrected words in output time). Then `ffmpeg -i build/base.mp4 -q:v 2 frames/f%05d.jpg`.
4. `seg.py a b` (4 in parallel) → `masks/` for all frames; cut-outs for cards from frames+masks (see SKILL history: grayscale, CLAHE, alpha = mask, bottom fade) → `assets/cut_*.png`.
5. `overlay.html`: all timings anchored to spoken words with `T('word', after)`; `window.needMask(t)` says when the person layer is needed. Test single frames: `node render.js 0 0 test 15 300 ...`, look at them, fix, then render all frames with 4 workers → `out/`.
6. `node dumpA.js > build/A.json`, `python3 sfx.py`, `bash mix.sh`.
7. Encode video and audio separately and mux: `ffmpeg -framerate 30 -i out/f%05d.jpg -c:v libx264 -crf 18 -pix_fmt yuv420p v.mp4`, then `-map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest`. Output 1080×1920, 30 fps.

## References (Drive file ids)
- `1z5oU3reZ3ibBtQXXxBm99WZANB-qKRxl` ref1 – podcast, tiny white captions + huge bold word, red-accent words, white cards with object, mood b-roll.
- `1vFsF1EgQ-1cXhAWPz-OXpPSxqao9qll4` ref2 – giant text behind subject, small captions, white card with illustration + letter-by-letter bold word.
- `1CqzV6kmLMzFhd-MmGUjGpuiVb4BnETMg` ref3 – bold sans + italic serif mix, UI/screenshot pop-ins with spotlight, outro logo + search bar.
- `1yk9-dTDI_x0O4CMC1Wpw1sRLfmxFyQQy` ref4 – white bold + italic serif accent, stat widget count-up, coloured/white full-screen question cards with cut-out person, glitch transition.
Raw interview (Nov 2026, Sportski centar 7, Nemanja Ilić): Drive folder `1ql5txXBE4P39B2YzeD0Q-2Bjtrp7LX6y` (IMG_8640 = full wide two-shot incl. all Q&A, IMG_8641 = interviewer close, IMG_8642 = owner close-up).
