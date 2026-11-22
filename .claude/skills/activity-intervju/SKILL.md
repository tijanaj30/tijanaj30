---
name: activity-intervju
description: Edit interview / testimonial reels for Activity školica sporta (Activity Centar – sportski rođendani) in the client's approved style — original iPhone colours (HDR tone-mapped), glass widgets with count-ups above the heads, big bottom captions, white full-screen cards with flat navy illustrations of what is being talked about, pullback reveals, logo end card, cleaned speech, original hype music; colours white + #1b263a. Use when the request concerns Activity / Activity školica sporta / Activity Centar video footage. Not for Laboratorija Olujić (that has its own skill).
---

# Activity školica sporta – interview reel style & pipeline

The user speaks Serbian; reply in Serbian (ekavica in all on-screen text).
Client: **Activity Centar – Školica sporta** (sportski rođendani za decu 3–12 god., animatori, poligoni, pena party).
Web/IG: `www.activitycentar.com`, `@activityskolica`. Offer PDF on Drive: "Activity - rođendanska ponuda.pdf"; logo "Novi logo ACTIVITY.pdf" (extracted to `assets/logo_t.png`).
Two audiences in every edit: **parents** (bez brige, deca uživaju) and **owners of other venues** (Activity preuzima organizaciju).

**First step:** `bash .claude/skills/activity-intervju/scripts/setup_work.sh` → `/home/user/work/act` (all scripts use that path).

## Approved look = "verzija 1" (+ client corrections, Nov 2026)
`scripts/overlay.html`. (`overlay_v2_alt.html` = the rejected editorial variant with small centred captions / text-behind-subject / cut-outs — only if the client asks for it.)
- **Colours of the footage must look exactly like the originals on Drive** (client is strict about this). iPhone clips are HDR (HEVC 10-bit, BT.2020, HLG `arib-std-b67`). Never convert naively (washed-out/"izbeljeno"). The client picked this conversion as "original": `zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p` (in `build.py`). Keep full 1080×1920, intermediate segments CRF 8, frames JPEG q1. If in doubt, show the client 2–3 stills side by side before rendering. Check `ffprobe ... color_transfer` on every new clip.
- Palette white + navy `#1b263a`; fonts Montserrat 500–800 + Playfair Display italic. **Italic must be bold and readable**: Playfair 800/900 italic everywhere; on video add a navy stroke behind the fill (`-webkit-text-stroke:12px rgba(27,38,58,.9); paint-order:stroke fill`) + soft shadow.
- **Bottom overlay**: soft navy gradient from the bottom at reduced opacity (client liked it) — stronger only on text-only moments (hook, "neće da idu kući.").
- **Captions**: bottom (`top:1395px`), Montserrat 700 54 px white with shadow, key word on its own line in big Playfair italic; questions in Playfair italic. Off during hook, text moments and cards.
- **Glass widgets** (light frosted glass, navy text) ABOVE the heads only (top 190–560 px), counting/animated: hook timer ring 0:00→2:30 + "☕ kafa na miru", name card, "3 školice fudbala" + check row, "Klasična igraonica ✕ → ✓ Sportski rođendan", checklist "na rođendanu", bar 0→2,5h "čistog uživanja", chips "🧃 pauza za sokiće? / ne stižu 😄", "Activity preuzima" checklist, "Utisci roditelja ★★★★★", "😊 svi su prezadovoljni", "Preporuka vlasnika".
- **NO labels above questions** ("PITANJE", "ZA VLASNIKE PROSTORA" pills were rejected). Questions must be heard **in full** (don't trim a question mid-sentence).
- **White full-screen cards** (`#f5f5f3` + faint 90 px grid): navy text (small Montserrat line → huge Montserrat 800 word → Playfair italic line) and a **flat navy illustration of the thing being talked about** (`assets/illustrations/`: classic playroom with ball pit/slide/blocks for "klasične igraonice su prevaziđene", clipboard checklist + calendar + balloons for the organisation card whose approved text is: **čitava** / **organizacija** (upright, big) / *u rukama* (italic, smaller) / *Activity tima* (italic, a bit bigger)). **Never cut out the people** for these cards. Draw new SVG illustrations in the same style (navy `#1b263a`, tints `#c9d1de #8f9bb3 #e3e7ee`, 6–9 px strokes, round caps) for new topics; inline them in the HTML so Montserrat applies. ~1.8–3 s, quick blur-scale in/out, elements pop/stagger, speech continues underneath.
- **Text on the floor** (client loved it, from ref2 "about perfectionism"): one key word lying on the turf in perspective (`#floor` → `rotateX(66deg)`, perspective 760px), white Montserrat small line + big Playfair 900 italic with a soft white glow, people's legs in FRONT of the letters (person cut-outs layer `#person` above it; `seg.py` masks → `cuts.py` RGBA PNGs for that frame range). Use a wide-ish framing (`flr` preset) so feet/floor are visible and the word fits the width. Used for "svi su *prezadovoljni*".
- **Illustrated moments**: e.g. on "kad sviramo kraj" a glass circle with a navy referee whistle (shake + sound waves) and pill "kraj igre!" + a whistle sound.
- **Camera**: framing presets per segment (`SHOT`: tight/own/own2/qwide/wide/c1/c2) with slow drift; **pullback reveal** from the tight hook into the wide two-shot (t 3.25→5.0 s). Nothing over faces.
- **End card**: video shrinks into a rounded card (pullback) and **fades out completely before the logo appears — no overlap** (video gone at E0+0.9 s, logo from E0+1.05 s); white card with logo, "Sportski rođendani / za decu od 3 do 12 godina", buttons "Roditelji · rezervišite termin" / "Vlasnici prostora · sarađujmo", `@activityskolica · activitycentar.com`.

## Content rules
- **Speech first**: owner and interviewer must be heard loud and clear — speech pushed to loudnorm −10.5 LUFS (`build/speech_loud.wav`), music bed 0.55 with light ducking (ratio 1.8), SFX only 0.12 — voices loudest, music clearly audible, effects subtle (final mix ≈ −11 LUFS).
- Remove filler/extra words the speaker says that are not in the caption (e.g. "vlasnik **u** prostora gde se **i** slave"): split the EDL segment around them; find the exact boundaries with a 20 ms spectral scan (fricatives have a high centroid) and re-check with Whisper — be careful not to clip the first consonant of the next word.
- Opening used: "prvi put sam se susreo sa vašom školicom kao roditelj" → "bukvalno 2,5 sata nisam osetio decu…"; the hook title/timer appear on "bukvalno" (`A.hk0`), captions run before it, pullback at the end of the hook (`A.hkEnd`).
- Keep ONLY the owner talking and the interviewer's questions; cut everything else (child running in, ball kicking, "Bravo!"…).
- Remove pauses/retakes, never cut inside a word; check that no start of the next word ("tako…") bleeds after a cut — mute the tail if needed. Verify by re-transcribing `build/speech.wav`.
- Spelling fixes in `build.py` `FIX` (ijekavica → ekavica; "i devojčice i dečaci", "bukvalno ništa"…).

## Sound
- **Background kids/voices must be gone — only the owner (and the interviewer's questions) + music.** Chain used for v7 (client-approved direction):
  1. `IMG_8640b` (wide shot, kids around): noisereduce *stationary* with a **noise profile from kids-only moments** (`y_noise` = before "Dobar dan" + pauses), prop 1.0, then non-stationary 0.7 → `src/<clip>_dn3.wav`; other clips `denoise.py`.
  2. `speech.py` assembles the speech from `build/timeline.json` with the clean sources.
  3. `harmonic.py` on every **owner** range (not on the female interviewer): pYIN F0 75–230 Hz + harmonic comb mask in the STFT (unvoiced frames ×0.45) — removes higher-pitched kids' voices under his speech without hurting intelligibility (check with Whisper avg_logprob).
  4. EQ/compressor/loudnorm −11, then a gate (−40 dB, 20 dB below speech p90, 220 ms hold) so pauses are silent. Final mix pushed to ≈ −11.5 LUFS.
  (RNNoise and an extra gate on the raw clip made speech choppy; DeepFilterNet/Demucs weights are not downloadable here.)
- **Background voices/noise must be reduced**: `denoise.py <clips>` → `src/<clip>_dn.wav` (noisereduce non-stationary, prop 0.8, thresh 2.2 + soft gate −14 dB between words; the stronger setting made speech watery). Then speech chain in `build.py` (HPF, light afftdn, EQ, compressor, loudnorm −16).
- **Music: dynamic, hype, sporty**, but under the speech. `music_hype.py <seconds> audio/music.wav <drop2_time> "<light ranges>" <drop1_bar>` composes an original 128 BPM house/pop track (Am–F–C–G: kick, claps, hats, offbeat bass, supersaw stabs, 16th arp, risers, impacts): drop on the hook pullback (bar 2), lighter under questions, breakdown + riser into a second drop on the venue-owner answer, final hit on the end card. Alternative: Higgsfield `elevenlabs_music_v2_5` if the client has credits (~0.145 credits/s; host `d8j0ntlcm91z4.cloudfront.net` allowed).
- `mix.sh`: speech + sidechain-ducked music (bed volume 0.42, rises on end card) + SFX at volume 0.6.
- **SFX must be crisp CapCut-style** (dull thuds were rejected): `sfx.py build/A.json build/timeline.json build/sfx.wav` synthesizes bright bell *ding*, high *ping*, bubbly *pop*, airy panned *whoosh*/*swoosh*, *sparkle* on the logo, rising star pings, referee *whistle* (2.9 kHz pea trill, short + long blast, kept moderate). Edit the event list per video.

## Pipeline (`/home/user/work/act`)
1. Download clips: `curl -L "https://drive.usercontent.google.com/download?id=ID&export=download&confirm=t"` (Drive connector refuses > 10 MB). `ffmpeg -i X.MOV -vn -ac 1 -ar 48000 src/X.wav`, then `python3 denoise.py X ...`.
2. Whisper medium `language='sr'`, word timestamps → `src/<clip>.MOV.json`.
3. `build.py` (edit `EDL`) → `build/base.mp4` (tone-mapped), `build/speech.wav`, `build/timeline.json`; `ffmpeg -i build/base.mp4 -q:v 2 frames/f%05d.jpg`.
4. `overlay.html`: timings anchored to words with `T('word', after)` (pass `after` when a word repeats). Test frames `node render.js 0 0 test 15 300 ...`, look at them, then render all frames (4 workers) into `out/`. Total frames = (body + 3.47 s) × 30.
5. `node dumpA.js > build/A.json`; `python3 sfx.py build/A.json build/timeline.json build/sfx.wav`; `python3 music_hype.py ...`; `bash mix.sh`.
6. Encode video and audio separately, then mux (`-c:v copy -shortest`). 1080×1920, 30 fps, CRF 18, AAC 192k.
Person masks for floor/behind text: `python3 seg.py a b` (frame range, 4 in parallel) → `python3 cuts.py`; `render.js` loads `cuts/cNNNNN.png` whenever `window.needMask(t)` is true.

## References (Drive ids)
ref1 `1z5oU3reZ3ibBtQXXxBm99WZANB-qKRxl`, ref2 `1vFsF1EgQ-1cXhAWPz-OXpPSxqao9qll4`, ref3 `1CqzV6kmLMzFhd-MmGUjGpuiVb4BnETMg`, ref4 `1yk9-dTDI_x0O4CMC1Wpw1sRLfmxFyQQy` — white cards with an object/illustration, stat pop-ups, italic-serif accents, outro search bar.
Raw interview (Sportski centar 7, Nemanja Ilić): Drive folder `1ql5txXBE4P39B2YzeD0Q-2Bjtrp7LX6y` (IMG_8640 = wide two-shot incl. all Q&A, IMG_8641 = interviewer, IMG_8642 = owner close-up).
