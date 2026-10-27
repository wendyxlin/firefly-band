"""Synthesize a 66 s soundtrack for the Firefly promo: dark pad intro, riser, impact at the reveal,
a soft four-on-the-floor groove, and a resolving outro. Pure numpy, writes music.wav (44.1 kHz stereo)."""
import numpy as np, wave

SR = 44100; DUR = 66.0; BPM = 104.0; BEAT = 60 / BPM
N = int(SR * DUR); t = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)

def env_adsr(n, a=0.01, d=0.1, s=0.6, r=0.2):
    e = np.ones(n) * s
    ai, di, ri = int(a*SR), int(d*SR), int(r*SR)
    ai = min(ai, n); e[:ai] = np.linspace(0, 1, ai)
    di = min(di, n - ai); e[ai:ai+di] = np.linspace(1, s, di)
    ri = min(ri, n); e[n-ri:] *= np.linspace(1, 0, ri)
    return e

def note(f): return 440 * 2 ** ((f - 69) / 12)

def add(sig, start, gain=1.0, pan=0.0):
    i = int(start * SR); j = min(N, i + len(sig)); s = sig[:j-i] * gain
    L[i:j] += s * np.sqrt(0.5 * (1 - pan)); R[i:j] += s * np.sqrt(0.5 * (1 + pan))

# --- Pad: Am – F – C – G, detuned saws, low-passed by averaging ---
chords = [[57, 60, 64], [53, 57, 60], [48, 55, 60], [55, 59, 62]]
bar = BEAT * 4
def saw(f, n, det=0.0):
    ph = (np.arange(n) / SR * f * (1 + det)) % 1.0
    return 2 * ph - 1
def lowpass(x, k):
    c = np.cumsum(np.insert(x, 0, 0)); y = (c[k:] - c[:-k]) / k
    return np.concatenate([y, np.zeros(k - 1)])
pos = 0.0; ci = 0
while pos < DUR:
    n = int(bar * SR * 1.02)
    s = np.zeros(n)
    for m in chords[ci % 4]:
        for det in (-0.004, 0.0, 0.005):
            s += saw(note(m), n, det)
    s = lowpass(s, 60 if pos < 9 else 28)
    s *= env_adsr(n, a=0.8, d=0.5, s=0.8, r=0.6) * 0.035
    add(s, pos, 1.0, pan=0.0)
    pos += bar; ci += 1

# --- Sub bass on the chord roots from the reveal ---
pos = 9.0; ci = 2
while pos < DUR - 2:
    root = chords[ci % 4][0] - 24
    for k in range(8):
        n = int(BEAT / 2 * SR)
        s = np.sin(2 * np.pi * note(root) * np.arange(n) / SR) * env_adsr(n, 0.005, 0.12, 0.4, 0.08) * 0.22
        add(s, pos + k * BEAT / 2)
    pos += bar; ci += 1

# --- Kick (four on the floor) 9 s – 50 s, hats from 15 s ---
def kick():
    n = int(0.35 * SR); tt = np.arange(n) / SR
    f = 50 + 120 * np.exp(-tt * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9) * 0.55
def hat():
    n = int(0.06 * SR); x = np.random.default_rng(1).standard_normal(n)
    x = x - lowpass(x, 4); return x * np.exp(-np.arange(n) / SR * 70) * 0.06
k = kick(); h = hat()
b = 9.0
while b < DUR - 3:
    add(k, b)
    if b >= 15: add(h, b + BEAT / 2, pan=0.3)
    b += BEAT

# --- Pluck arpeggio (firefly sparkle) 15 – 44 s ---
rng = np.random.default_rng(7)
b = 15.0; ci = 0
while b < DUR - 9:
    ch = chords[ci % 4]
    for s16 in range(8):
        m = ch[s16 % 3] + 12 + (12 if s16 >= 4 else 0)
        n = int(0.25 * SR); tt = np.arange(n) / SR
        s = (np.sin(2*np.pi*note(m)*tt) + 0.3*np.sin(4*np.pi*note(m)*tt)) * np.exp(-tt * 14) * 0.05
        add(s, b + s16 * BEAT / 2, pan=float(rng.uniform(-0.6, 0.6)))
    b += bar; ci += 1

# --- Riser into the reveal (6.5 – 9 s) and impact at 9 s ---
n = int(2.5 * SR); tt = np.arange(n) / SR
noise = np.random.default_rng(3).standard_normal(n)
riser = (noise - lowpass(noise, 3)) * (tt / tt[-1]) ** 2 * 0.12
riser += np.sin(2 * np.pi * np.cumsum(200 + 900 * (tt / tt[-1]) ** 2) / SR) * (tt / tt[-1]) ** 2 * 0.05
add(riser, 6.5)
n = int(2.0 * SR); tt = np.arange(n) / SR
boom = np.sin(2 * np.pi * np.cumsum(40 + 60 * np.exp(-tt * 6)) / SR) * np.exp(-tt * 2.5) * 0.6
air = np.random.default_rng(4).standard_normal(n) * np.exp(-tt * 4) * 0.08
add(boom + lowpass(air, 8), 9.0)

# --- Soft ticks for the dying-phone intro ---
for i, tick in enumerate(np.arange(0.4, 4.4, 0.5)):
    n = int(0.04 * SR); tt = np.arange(n) / SR
    add(np.sin(2*np.pi*1800*tt) * np.exp(-tt*120) * 0.05, tick, pan=-0.2 if i % 2 else 0.2)


# --- Check-in chimes: three soft dings as friends receive "I'm okay" (28.6 s+), a resolve when everyone's home (37.0 s) ---
def ding(m, g=0.09):
    n = int(0.9 * SR); tt = np.arange(n) / SR
    return (np.sin(2*np.pi*note(m)*tt) + 0.25*np.sin(2*np.pi*note(m)*2.01*tt)) * np.exp(-tt * 5) * g
for i, m in enumerate((76, 79, 84)):
    add(ding(m), 28.6 + i * 0.55, pan=-0.3 + 0.3 * i)
for i, m in enumerate((72, 76, 79, 84)):
    add(ding(m, 0.07), 37.0 + i * 0.06, pan=-0.2 + 0.13 * i)

# --- Master: fade in/out, soft clip ---
fade = np.ones(N); fi = int(0.3 * SR); fo = int(2.5 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
mix = np.stack([L, R], 1) * fade[:, None]
mix = np.tanh(mix * 1.6) / np.tanh(1.6)
mix /= max(1e-9, np.abs(mix).max()) / 0.89
with wave.open('music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('wrote music.wav', DUR, 's')
