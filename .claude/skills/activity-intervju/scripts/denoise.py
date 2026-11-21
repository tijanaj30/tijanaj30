# src/<clip>.wav -> src/<clip>_dn.wav : spectral noise reduction (non-stationary, for crowd/voice babble) + gentle gate between words
import sys, numpy as np, noisereduce as nr
from scipy.io import wavfile
from scipy.ndimage import maximum_filter1d, uniform_filter1d
for s in sys.argv[1:]:
    sr, x = wavfile.read(f'src/{s}.wav'); x = x.astype(np.float32) / 32768
    y = nr.reduce_noise(y=x, sr=sr, stationary=False, prop_decrease=0.8, n_fft=2048, time_mask_smooth_ms=80, freq_mask_smooth_hz=400, thresh_n_mult_nonstationary=2.2)
    # gate: envelope in 10 ms frames, open when > floor+10 dB, hold 150 ms, 40 ms smoothing, closed = -14 dB
    h = sr // 100; fr = y[:len(y) // h * h].reshape(-1, h); db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
    thr = np.percentile(db, 15) + 10; g = (db > thr).astype(float); g = maximum_filter1d(g, 15); g = uniform_filter1d(g, 4)
    g = 10 ** (-14 * (1 - g) / 20); g = np.repeat(g, h); g = np.pad(g, (0, len(y) - len(g)), mode='edge')
    y = y * g
    wavfile.write(f'src/{s}_dn.wav', sr, (np.clip(y, -1, 1) * 32767).astype(np.int16))
    def stats(z):
        fr = z[:len(z) // 4800 * 4800].reshape(-1, 4800); d = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9); return np.percentile(d, [10, 50, 90]).round()
    print(s, 'before', stats(x), 'after', stats(y))
