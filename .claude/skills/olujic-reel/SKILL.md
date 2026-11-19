---
name: olujic-reel
description: Edit talking-head Instagram reels for Laboratorija Olujić (dental lab) in the client's approved style — multicam sync, silence/retake removal, 9:16 under 60 s, animated HTML motion-graphics overlay, big italic keyword captions, soft SFX, optional upbeat music. Use when the user asks for a reel/video edit "u mom stilu", for Olujić, or sends new raw videos to edit like before.
---

# Olujić reel – house style & pipeline

The user speaks Serbian; reply in Serbian. Brand: **Laboratorija Olujić** (NOT "Lujić"; the tooth in the logo is the "O").
Logo for the end card: `scripts/logo_end.png` (colour logo, black text, transparent; end card background #F2F2F2 with dark ink text). Older white-outline logo `scripts/logo_crop.png`, tooth-only icon `scripts/logo_tooth.png`.
In overlay.html the end-card logo path is `../logo2_t.png`: copy `logo_end.png` there (or edit the path).
Brand colours: teal `#2FCFB8` (dark `#0F8F7E`, light `#A6F5E8`), lilac `#A48AD0`, pink `#EFA3BD` (dark `#C9567E`), ink `#1C2633`, cream `#FBF7F1`.
Fonts (Google Fonts, latin-ext for č ć š ž đ): **Playfair Display** italic 400–700 + 600 regular, **Montserrat** 500–800.
Download TTFs with an old user agent (`curl -A "Mozilla/4.0" "https://fonts.googleapis.com/css2?family=..."`) into `v2/fonts/` next to overlay.html.

## Approved look (the client signed off on v7)
- **Captions**: bottom, low (`#cap bottom:270px`, 200px during the CTA). Small words = Montserrat 600 ~52px, white, **no outline**, soft shadow only. Key word of a phrase = its own line, **huge Playfair italic 700** (≈1750/len px, max 175), white→light-teal gradient, blur+scale pop-in. Multi-word keywords are merged (e.g. "završni rad" in one line, same size). Soft dark gradient at the bottom of the frame for readability.
- **Cards**: cream, rounded 34px, dark ink text, italic accents, enter with back-ease + blur exit. Each card appears **exactly on the word** it belongs to — never sits alone before the sentence is spoken (whole sentence at once).
- **Camera**: use ONLY the frontal shot (talking to camera). Keep the cut points; where another angle would go, use a tighter frontal framing (A3 medium, zoom ~1.15–1.2; A2 punch-in ~1.32) so cuts still read as cuts.
- **Placement rule**: NOTHING above or over the head/face/mouth. All cards sit below the face (top ≈1060px, scaled 0.78), above the captions; CTA "Pišite mi" button on the laptop line (~1392px); illustrations (e.g. crown) small, lower right beside the stepper. No brand tag at the top. Check with gridded frames before rendering.
- **Story beats used** (adapt to new scripts): hook card; "classic route" loop Vi → Stomatolog → Tehničar with counter PROBA 1…∞, broken up with interlude scenes (Prepravka + gear, tooth travelling back, calendar "Opet proba +1"), loop card returns with red ✕; full-screen brand-gradient wipe + letter-by-letter "drugačije." on the key turn; 3-step stepper with checkmarks; chat bubbles; Venn circles "zajedno" + check; illustration pop-ups for objects mentioned (e.g. porcelain crown on "krune", placed lower right, off the face); iOS-style notification card ("Laboratorija Olujić · Nova poruka") + "Pišite mi" gradient button on the laptop line below the face; logo end card with circle reveal + shimmer + "Pišite nam · tu smo za vas".
- **Sound**: discreet synthesized SFX (pop, tick, bubble, whoosh, ding, shimmer, notification), ~19 dB below speech. Music optional: original upbeat pop-house ~118 BPM (`music2.py`), drop placed on the key turn, sidechain-ducked under speech, volume −6 dB. Always offer a no-music version (client may add trending audio in Instagram).
- Output: 1080×1920, 30 fps, H.264 CRF 18, AAC 192k, ≤ 60 s (speed-up up to 1.06× with atempo if needed), speech loudnorm −14 LUFS.

## Pipeline (scripts/)
1. Download sources (Google Drive: `drive.usercontent.google.com/download?id=ID&export=download&confirm=t`; list IDs with gdown `download_folder(..., skip_download=True)`).
2. Audio: extract 16 kHz mono; find camera offset by cross-correlation (check several windows for drift). Use the **lavalier track** (better SNR) for the whole video.
3. `transcribe.py`: Whisper medium, `language='sr'`, word timestamps, script text as initial prompt.
4. `build.py`: EDL of (start, end, shot A/A2/B, correct script text); cuts snapped to silence from the lav envelope (snap only inward; check quiet word endings by hand); main angle ~75 %, profile ~25 %, punch-in A2 on key lines; slow zoom drift via zoompan from the 4K source; writes `build/timeline.json` + clean `base.mp4` (+ blurred end-card background). Verify by re-transcribing the output.
5. `overlay.html` + `render.js`: deterministic `render(t)` per frame, rendered with Playwright (transparent PNGs, 4 parallel workers), timings looked up from spoken words (`T('word', after)`).
6. `dump.js` → `sfx_events.json`; `sfx.py` → `sfx.wav`; `music2.py` → music.
7. ffmpeg: overlay PNG sequence on base, mix speech + SFX (+ ducked music), alimiter 0.89.

## Network hosts this needs (Default environment)
drive.google.com, drive.usercontent.google.com, www.instagram.com, scontent-ord5-1/2.cdninstagram.com (reference reels via yt-dlp), openaipublic.azureedge.net (Whisper model), fonts.googleapis.com / fonts.gstatic.com.
