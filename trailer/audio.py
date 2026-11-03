#!/usr/bin/env python3
"""Synthesises the Wayyuh AI trailer score (48 s, 120 BPM, stereo 44.1 kHz) with numpy only.
Timeline (matches trailer.html):  0 pulse · 5 two forces · 12 impact · 19.5 UI · 27.5 features · 30.5 Indonesia · 33.5 words · 41 end card."""
import sys, wave
import numpy as np

SR = 44100
DUR = 48.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
BEAT = 0.5

main = np.zeros((2, N))
rev = np.zeros((2, N))


def put(sig, t0, gain=1.0, pan=0.0, send=0.0):
    """Mix a mono signal at time t0. pan -1..1, send = reverb amount."""
    i = int(t0 * SR)
    if i >= N or i + len(sig) <= 0:
        return
    a = max(0, -i)
    s = sig[a:]
    j = i + a
    s = s[: N - j]
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    main[0, j:j + len(s)] += s * gain * l
    main[1, j:j + len(s)] += s * gain * r
    if send:
        rev[0, j:j + len(s)] += s * gain * send * l
        rev[1, j:j + len(s)] += s * gain * send * r


def tax(d):
    return np.arange(int(d * SR)) / SR


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def adsr(t, a, d, s, r, dur):
    e = np.minimum(1, t / max(a, 1e-4))
    e = e * (1 - (1 - s) * np.clip((t - a) / max(d, 1e-4), 0, 1))
    e = e * np.clip((dur - t) / max(r, 1e-4), 0, 1)
    return e


def noise_shaped(dur, center, width, amp, seed=0):
    """Band noise whose centre frequency follows center(frac) (Hz); width in octaves. Block-wise FFT shaping."""
    g = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros(n + 4096)
    blk, hop = 2048, 1024
    win = np.hanning(blk)
    f = np.fft.rfftfreq(blk, 1 / SR)
    f[0] = 1
    for s in range(0, n, hop):
        x = g.standard_normal(blk) * win
        X = np.fft.rfft(x)
        fc = center(min(1, s / max(n, 1)))
        m = np.exp(-0.5 * (np.log2(f / fc) / width) ** 2)
        out[s:s + blk] += np.fft.irfft(X * m, blk) * win
    out = out[:n]
    return out / (np.abs(out).max() + 1e-9) * amp


def lowpass_fft(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** 4), len(x))


def highpass_diff(x, k=1):
    for _ in range(k):
        x = np.diff(x, prepend=0)
    return x


# ---------------------------------------------------------------- voices
def pluck(freq, dur=0.6, bright=1.0):
    t = tax(dur)
    s = np.zeros_like(t)
    for k in range(1, 8):
        s += np.sin(2 * np.pi * freq * k * t + k) * np.exp(-t * (5 + 7 * k / bright)) / k
    s += 0.3 * np.sin(2 * np.pi * freq * 2.005 * t) * np.exp(-t * 14)
    return s * np.minimum(1, t / 0.003)


def pad(freqs, dur, a=1.2, r=1.6, bright=1.0):
    t = tax(dur)
    s = np.zeros_like(t)
    for f in freqs:
        for det in (-0.07, 0.0, 0.08):
            ff = f * 2 ** (det / 12)
            for k in range(1, 11):
                if ff * k > 9000:
                    break
                s += np.sin(2 * np.pi * ff * k * t + k * 1.3 + det * 7) / (k ** (1.25 / bright))
    s *= adsr(t, a, 0.5, 0.9, r, dur)
    return s / (len(freqs) * 3)


def kick(dur=0.5):
    t = tax(dur)
    ph = 2 * np.pi * (45 * t + 105 * (1 - np.exp(-t * 38)) / 38)
    return (np.sin(ph) * np.exp(-t * 9) + 0.35 * np.sin(ph * 2) * np.exp(-t * 30)) * np.minimum(1, t / 0.002)


def taiko(freq=62, dur=1.6):
    t = tax(dur)
    ph = 2 * np.pi * (freq * t + 36 * (1 - np.exp(-t * 18)) / 18)
    body = np.sin(ph) * np.exp(-t * 3.2) + 0.5 * np.sin(ph * 1.5) * np.exp(-t * 6)
    skin = lowpass_fft(rng.standard_normal(len(t)), 900) * np.exp(-t * 18) * 3
    return (body + skin) * np.minimum(1, t / 0.002)


def clap(dur=0.35):
    t = tax(dur)
    n = highpass_diff(rng.standard_normal(len(t)), 1)
    n = lowpass_fft(n, 7000)
    e = np.exp(-t * 16) + 0.6 * np.exp(-np.clip(t - 0.012, 0, None) * 30) * (t > 0.012)
    return n * e * 0.5


def hat(dur=0.09, open_=False):
    t = tax(0.35 if open_ else dur)
    n = highpass_diff(rng.standard_normal(len(t)), 2)
    return n * np.exp(-t * (14 if open_ else 70)) * 0.35


def boom(dur=4.0):
    t = tax(dur)
    ph = 2 * np.pi * (34 * t + 70 * (1 - np.exp(-t * 3.2)) / 3.2)
    b = np.sin(ph) * np.exp(-t * 0.95)
    b += 0.5 * np.sin(2 * np.pi * 68 * t) * np.exp(-t * 1.6)
    crack = lowpass_fft(rng.standard_normal(len(t)), 2400) * np.exp(-t * 7)
    return (b + crack * 0.8) * np.minimum(1, t / 0.002)


def crash(dur=3.0):
    t = tax(dur)
    n = highpass_diff(rng.standard_normal(len(t)), 1)
    n = lowpass_fft(n, 11000)
    return n * np.exp(-t * 1.5) * 0.5


def bell(freq, dur=3.0):
    t = tax(dur)
    s = sum(np.sin(2 * np.pi * freq * r * t) * a * np.exp(-t * d) for r, a, d in ((1, 1, 1.4), (2.01, .6, 2.0), (2.99, .35, 2.8), (4.2, .2, 3.6)))
    return s * np.minimum(1, t / 0.004)


def whoosh(dur, up=True, amp=0.5, seed=1):
    f0, f1 = (500, 9000) if up else (9000, 500)
    s = noise_shaped(dur, lambda x: f0 * (f1 / f0) ** x, 0.9, amp, seed)
    t = tax(dur)
    e = (t / dur) ** 2.2 if up else (1 - t / dur) ** 2.2
    return s * e


# ---------------------------------------------------------------- score
CH = {  # chord name -> (root midi (bass), pad notes midi, arp notes midi)
    "Am": (33, [57, 60, 64, 67], [57, 60, 64, 69, 72, 76]),
    "F": (29, [53, 57, 60, 64], [53, 57, 60, 65, 69, 72]),
    "C": (36, [55, 60, 64, 67], [55, 60, 64, 67, 72, 76]),
    "G": (31, [55, 59, 62, 66], [55, 59, 62, 67, 71, 74]),
}
PROG = ["Am", "F", "C", "G"]


def chord_at(t):
    return PROG[int(max(0, t - 12) // 4) % 4]


def vol_curve(t):
    """overall pad level through the film"""
    v = np.interp(t, [0, 5, 12, 12.01, 33.5, 41, 47, 48], [.0, .10, .35, .75, .8, 1.0, .6, 0])
    return v


# 0–5.2: heartbeat + dark drone
for k in range(0, 6):
    t0 = 0.4 + k * 1.0
    put(kick(0.4) * 0.55, t0, pan=0, send=.15)
    put(kick(0.4) * 0.28, t0 + 0.28, pan=0, send=.15)
put(pad([33, 40], 13, a=4, r=1.0, bright=.7) * 0.5, 0.0, gain=0.55, send=.4)
put(noise_shaped(6, lambda x: 180 + 400 * x, 1.4, .06, 3), 0.0, gain=1, send=.5)

# 5–12: two forces, rising tension
put(pad([45, 52, 57, 60], 7.5, a=2.5, r=0.4, bright=.9) * 0.6, 5.0, gain=0.7, send=.45)
for k, (n, t0) in enumerate([(81, 5.5), (76, 6.5), (72, 7.5), (76, 8.5), (81, 9.5)]):
    put(bell(midi(n), 3.0) * 0.35, t0, pan=-.5 if k % 2 else .5, send=.6)
put(whoosh(6.0, True, 0.8, 5), 6.0, gain=.7, send=.4)
ticks = []
tt = 7.2
gap = 0.5
while tt < 11.95:
    ticks.append(tt)
    gap = max(0.07, gap * 0.9)
    tt += gap
for i, t0 in enumerate(ticks):
    put(pluck(midi(93) if i % 2 else midi(86), 0.12) * 0.25, t0, pan=(-1) ** i * .4, send=.25)
tr = tax(5.0)
put(np.sin(2 * np.pi * (110 * 2 ** (tr * 0.6) * tr)) * (tr / 5) ** 2 * 0.25, 7.0, gain=1, send=.3)
# the breath before the impact
t_mute = 11.88

# 12.0 impact
put(boom(4.5), 12.0, gain=1.0, send=.35)
put(crash(3.5), 12.0, gain=.55, send=.5)
put(taiko(55, 2.0), 12.0, gain=.7, send=.3)
put(whoosh(0.9, False, 0.7, 9), 12.0, gain=.5)

# 12–41 main score
for t0 in np.arange(12.0, 41.0, 4.0):
    ch = CH[chord_at(t0)]
    d = min(4.6, 41 + 1 - t0) if t0 < 40 else 8.0
    v = float(vol_curve(t0 + 2))
    put(pad([midi(n) for n in ch[1]], d, a=0.8, r=1.2) * 0.6, t0, gain=v * 0.8, send=.35)
    put(pad([midi(ch[0]), midi(ch[0] + 12)], d, a=0.2, r=0.6, bright=.5) * 0.7, t0, gain=v * 0.55, send=.1)

# arps (16ths) 14–33.5, then softer plucks to 41
t0 = 14.0
step = BEAT / 4
i = 0
while t0 < 41.0:
    ch = CH[chord_at(t0)]
    notes = ch[2]
    pat = [0, 2, 4, 5, 4, 2, 3, 1] if t0 < 33.5 else [0, 2, 4, 5]
    n = notes[pat[i % len(pat)]]
    spacing = step if t0 < 33.5 else BEAT / 2
    lvl = 0.5 if t0 < 19.5 else 0.7
    if t0 >= 33.5:
        lvl = 0.55
    put(pluck(midi(n), 0.55) * lvl, t0, gain=0.5, pan=np.sin(i * 0.9) * .55, send=.4)
    i += 1
    t0 += spacing

# drums
bars = np.arange(12.0, 41.0, 2.0)
for b in bars:
    put(taiko(58, 1.5) * 0.7, b, gain=.55, send=.35)                 # downbeat taiko
    if 12 <= b < 19.5:
        put(taiko(70, 1.0) * 0.5, b + 1.5, gain=.35, send=.3)
for t0 in np.arange(19.5, 33.5, BEAT):                               # full groove
    put(kick() * 0.8, t0, gain=.75, send=.08)
for t0 in np.arange(20.0, 33.5, 1.0):                                # backbeat on 2 & 4 (relative to 19.5)
    put(clap(), t0, gain=.5, pan=.1, send=.35)
for t0 in np.arange(19.5, 33.5, BEAT / 2):
    off = (round((t0 - 19.5) / (BEAT / 2)) % 2) == 1
    put(hat(0.07), t0, gain=.35 if off else .22, pan=.25, send=.1)
for t0 in np.arange(19.5, 33.5, 2.0):
    put(hat(0.35, True), t0 + 0.75, gain=.3, pan=-.2, send=.2)
for t0 in np.arange(33.5, 41.0, 2.0):                                # emotional section: just a soft pulse
    put(kick() * 0.5, t0, gain=.35, send=.2)

# sub bass eighths 19.5–33.5
t0 = 19.5
while t0 < 33.5:
    ch = CH[chord_at(t0)]
    f = midi(ch[0])
    t = tax(0.4)
    put(np.sin(2 * np.pi * f * t) * np.exp(-t * 3.2) * np.minimum(1, t / 0.004) * 0.9, t0, gain=.65)
    t0 += BEAT
# bass drone for the rest
for t0 in np.arange(12.0, 19.5, 4.0):
    ch = CH[chord_at(t0)]
    t = tax(4.0)
    put(np.sin(2 * np.pi * midi(ch[0]) * t) * adsr(t, .05, .5, .8, .6, 4.0) * 0.8, t0, gain=.5)

# transition hits + whooshes at every cut
for c in [19.5, 23.5, 27.5, 33.5, 41.0]:
    put(whoosh(0.7, True, 0.8, int(c)), c - 0.7, gain=.55, send=.2)
    put(boom(2.6), c, gain=.6 if c < 41 else .9, send=.3)
    put(crash(2.2), c, gain=.35 if c < 41 else .5, send=.4)
# feature words 27.5–30.5 (every 0.75 s) and Indonesia cuts 30.5–33.5 (every 0.5 s)
for i in range(4):
    t0 = 27.5 + 0.75 * i
    put(taiko(80 - i * 4, 0.8), t0, gain=.5, send=.25)
    put(pluck(midi([69, 72, 76, 81][i]), 1.0) * 0.7, t0, gain=.6, pan=(-1) ** i * .5, send=.4)
for i in range(6):
    t0 = 30.5 + 0.5 * i
    put(taiko(90 + i * 5, 0.5), t0, gain=.45, send=.2)
put(whoosh(3.0, True, 0.7, 77), 30.5, gain=.4, send=.3)

# 41: arrival
big = [midi(n) for n in (45, 52, 57, 61, 64, 69)]   # A major add
put(pad(big, 8.0, a=0.3, r=3.0) * 0.8, 41.0, gain=.8, send=.5)
put(pad([midi(33), midi(45)], 8.0, a=0.2, r=3.0, bright=.5) * 0.8, 41.0, gain=.55)
for k, n in enumerate((93, 88, 85, 81, 76)):
    put(bell(midi(n), 5.0) * 0.5, 41.3 + k * 0.45, gain=.5, pan=(-1) ** k * .6, send=.7)
put(taiko(50, 3.0), 41.0, gain=.8, send=.4)

# air / film bed
put(noise_shaped(DUR, lambda x: 2500, 2.2, .02, 99), 0, gain=1.0)

# ---------------------------------------------------------------- reverb bus (decorrelated stereo, 2.6 s)
ir_len = int(2.6 * SR)
tt = np.arange(ir_len) / SR
ir = np.stack([rng.standard_normal(ir_len) * np.exp(-tt * 2.4), rng.standard_normal(ir_len) * np.exp(-tt * 2.4)])
for c in range(2):
    ir[c] = lowpass_fft(ir[c], 5200) * (1 - np.exp(-tt * 60))
    ir[c] /= np.sqrt((ir[c] ** 2).sum())


def convolve(x, h):
    n = len(x) + len(h) - 1
    m = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(h, m), m)[:len(x)]


wet = np.stack([convolve(rev[0], ir[0]), convolve(rev[1], ir[1])])
mix = main + wet * 0.55

# the breath of silence just before the impact
t = np.arange(N) / SR
gate = np.ones(N)
m = (t >= 11.9) & (t < 12.0)
gate[m] = np.interp(t[m], [11.9, 11.96, 12.0], [1, 0.0, 1.0])
mix *= gate

# master
fade = np.clip(t / 0.8, 0, 1) * np.clip((DUR - t) / 1.6, 0, 1)
mix *= fade
mix = np.tanh(mix * 1.25) / np.tanh(1.25)
peak = np.abs(mix).max()
mix *= 0.89 / peak
out = (mix.T * 32767).astype(np.int16)
path = sys.argv[1] if len(sys.argv) > 1 else "trailer-score.wav"
with wave.open(path, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(out.tobytes())
print("wrote", path, "peak before norm", round(float(peak), 3))
