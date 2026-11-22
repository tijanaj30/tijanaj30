# keep only the low-pitched speaker: pYIN F0 tracking (80-220 Hz) + harmonic comb mask in the STFT;
# unvoiced consonants pass through attenuated so speech stays intelligible.
import sys, numpy as np, librosa
from scipy.io import wavfile
from scipy.ndimage import uniform_filter1d
inp, out, a, b = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
sr, x = wavfile.read(inp); x = x.astype(np.float32) / (32768 if x.dtype == np.int16 else 1)
seg = x[int(a * sr):int(b * sr)]
y16 = librosa.resample(seg, orig_sr=sr, target_sr=16000)
f0, vflag, vprob = librosa.pyin(y16, fmin=75, fmax=230, sr=16000, frame_length=1024, hop_length=160)
n_fft, hop = 2048, 480
S = librosa.stft(seg, n_fft=n_fft, hop_length=hop); freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
T = S.shape[1]; t_stft = np.arange(T) * hop / sr; t_f0 = np.arange(len(f0)) * 160 / 16000
idx = np.clip(np.round(t_stft * 16000 / 160).astype(int), 0, len(f0) - 1); f0i = np.nan_to_num(f0[idx], nan=0); vp = vflag[idx].astype(float)
M = np.zeros(S.shape, np.float32)
for j in range(T):
    if f0i[j] > 0 and vp[j] > 0:
        k = freqs / f0i[j]; dist = np.abs(k - np.round(k)) * f0i[j]          # Hz to nearest harmonic
        width = 18 + 0.02 * freqs                                             # widen at high freq
        m = np.exp(-(dist / width) ** 2); m[freqs < 70] = 0; m[freqs > 6000] = 0.35
        M[:, j] = np.maximum(m, 0.12)                                         # floor keeps a little air
    else:
        M[:, j] = 0.45                                                        # unvoiced: consonants / pauses
M = uniform_filter1d(M, 3, axis=1)
yo = librosa.istft(S * M, hop_length=hop, length=len(seg))
xo = x.copy(); xo[int(a * sr):int(a * sr) + len(yo)] = yo
wavfile.write(out, sr, xo.astype(np.float32)); print('voiced frames %.0f%%' % (100 * np.mean(vp > 0)))
