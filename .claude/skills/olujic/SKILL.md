---
name: olujic
description: Edit Instagram reels and interview videos ONLY for Laboratorija Olujić (dental lab) in the client's approved styles — reel style (motion-graphics overlay, big keyword captions) and the "tirkizni" interview style (white hook overlay, editorial captions, bright gradient keywords, logo top-left). Use only when the request explicitly concerns Laboratorija Olujić / Olujić videos or raw footage from that client. Do NOT use for other clients (e.g. Activity školica sporta) or generic "u mom stilu" requests that do not mention Olujić.
---

# Olujić reel – house style & pipeline

**First step in every new session:** run `bash .claude/skills/olujic/scripts/setup_work.sh` — it copies the fonts (Playfair, Montserrat, Cormorant, Jost) and the logo from `assets/` to `/home/user/work/...`, the paths the overlay HTML files use. Python tools needed: ffmpeg, openai-whisper, scipy, numpy, gdown, pillow, opencv-python-headless==4.10.0.84; Playwright/Chromium is preinstalled.

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

## Interview style "tirkizni" (final approved Nov 2026: `olujic_deo1_v6`, `olujic_deo2_v12`)
For long talking-head interviews (sofa / window), split into separate reels. Scripts in `scripts/intervju/` (`overlay_editorial.html` = latest approved overlay).
- **Cut**: remove only pauses, stutters and retakes; every spoken sentence stays (if a sentence was said twice, keep the clean later take; drop a weak opening sentence if the client says it is "višak"). Verify by re-transcribing the cut. Audio strictly sequential, 15 ms edge fades, never cut inside a word. Gentle 0.4 s dissolves (`xfade`); zoom only discreetly (alternate 1.0 / 1.08, slow 0.012 drift). Never crop a tight close-up out of the raw — keep the normal framing.
- **Hook**: about 1–1.3 s, visible from frame 0 (works as the reel cover). White gradient overlay on the lower half, text low (`top:1330px`): thin "LABORATORIJA OLUJIĆ" small caps (Montserrat 700, 24 px, `#0F8F7E`, letter-spacing .34em) and below it a short title in **upright (not italic) Playfair 600 ~190 px with the brand gradient** `#0F8F7E→#2FCFB8→#7B5FB8→#C9567E`, split over lines with clear space between them (e.g. "IZVAN / OKVIRA"). Question variant: "Da li je svako **NE** loše za vas?". Under the hook only music — mute room tone/rustle.
- **Captions**: Cormorant Garamond 700, white, left-aligned bottom (`bottom:200px`) with a thin teal line above; words rise in on their own timestamps. Key words (novac, osmeh, protokoli, principi, struke, lekarima, sarađujem, pacijenti, poštovanje, razumevanje, timski duh, prijatno, ljudskost, poenta, srcem, poverenje…) end the phrase and sit alone on the last line in the **big colour font**: Playfair 600, a **bright, clearly coloured gradient** `#5FE8D2→#B5F5EC→#C4A9F7→#FFA6C6` drawn normally in the N layer (class `bg bright`), with the S layer (blurred dark copy) behind it for contrast. Do NOT use the exclusion blend for these: it goes dark on white clothes. Not all white — the gradient must stay visible.
- **Caption timing (important)**: each phrase starts exactly when its first word is spoken (`s − 0.15`). The big keyword appears **exactly when it is spoken** (`last.s − 0.05`, 0.3 s ease), never earlier. It holds ≥0.8 s after it is spoken; the next phrase may wait only for that hold — never let delays cascade. Check fast runs of keywords frame by frame.
- **Text never covers the face** — captions low (legs/lap height). If in doubt, lower.
- **Logo**: small colour logo (`logo2_t.png`, 190 px) top-left for the whole video; no chapter numbers or labels at the top. End card: light `#F2F5F5`, logo + "Prvo razumete. / *Tek onda odlučujete.*".
- **Elements**: the client ended with a clean look — **no boxes or line-art in the final cut** (the "Pristup sa srcem" heart card, laurel wreath, tooth→heart and white full-screen value cards were all removed at the end). Only keep a small number of white "second screen" cutaways if already approved (deo1: "mnogo koraka", "Ne."). Client photos: full-screen, slow cosine pan, show only the people meant to be seen, **max 2 s including fades**, placed on the matching words (e.g. "taj timski duh"). If proposing a new visual, send a still mock-up first and wait for approval; purple from the logo is `#9B88C2`.
- **Sound**: music = `music4.py` (original uplifting piano/strings ~92 BPM) at −12 dB (or −6 dB with sidechain ducking); soft "ka-ching" (`sfx.py kaching`) on "novac", quiet whooshes on cutaways.
- **Render rule**: always render video (`-an`) and audio separately and mux with `-c:v copy -shortest` — a single ffmpeg graph with PNG sequences + audio drifts out of lip sync.

## Instagram carousels (approved Nov 2026: `olujic/karusel_kruna`, `olujic/karusel_tihe_promene`, `olujic/karusel_najskuplji_zubi`)
- Style: cream paper slides (#F3ECE2 + paper grain), one continuous graphite pencil line running across all slides, Cormorant Garamond (300 display, italic accent) + Jost (spaced caps labels, 300 body), espresso #2E1A12 slide with copper #D2AE95 text for questions/quotes, bordo #5C1A1B only for details (dots, big numeral). Photos only crown/sand (`pozadine/01-okluzalni-pejzaz.png`, `pozadine/koncepti/01-okluzalni-pejzaz.png`) in full-bleed or arch frames. The client rejected ceramic vessels/objects as backgrounds ("nemaju smisla").
- Audience is older: body text Jost 400 ≈45px in dark ink #43342A, headlines ≥ 90px; small caps labels 26px.
- **Never put page numbers or numbered labels anywhere** (no "01 — 08", no "01 · Naslov") — in any deliverable.
- Small illustrations are drawn on the graphite line: dots growing in size ("sitnicu po sitnicu"), labelled points (Danas → Sutra), rising sun on the line (juče → danas).
- Headline typography (client's own inspiration, font = Playfair Display 400 + italic): all-serif statements — upright Playfair lines, the key phrase in larger italic (accent colour), then upright continuation, closed by a short thin rule. Avoid sans paragraphs in headline blocks.
- Second palette for service/info posts: white + light teal #A6F5E8 / dark teal #0F8F7E + light lilac / #6E54A8, tooth from the logo as a marker on every slide (`olujic/karusel_smestaj`).
- CTA: wide bordo pill button "Pišite mi" (Jost 300 light caps + thin arrow) with a bordo italic tagline under it.
- Source: `olujic/karusel_tihe_promene/izvor/karusel3.html` (render with `render3.js`, Playwright, 1080×1350).
