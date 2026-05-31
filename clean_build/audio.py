import pygame
import math
import struct
import wave
from io import BytesIO

def make_sound(wave_func, duration, freq, volume=0.5):
    sr = 22050
    n = int(sr * duration)
    samples = []
    for i in range(n):
        t = i / sr
        val = int(wave_func(t, freq) * volume * 32767)
        samples.append(max(-32768, min(32767, val)))
    buf = BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(struct.pack(f"<{n}h", *samples))
    buf.seek(0)
    return pygame.mixer.Sound(buf)

def sine(t, f):
    return math.sin(2 * math.pi * f * t)

# Inicialização atrasada para Web
snd_eat = None
snd_eat_gold = None
snd_powerup = None
snd_die = None
snd_move = None

def init_audio():
    global snd_eat, snd_eat_gold, snd_powerup, snd_die, snd_move
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=1)
        snd_eat      = make_sound(sine, 0.1, 600, 0.4)
        snd_eat_gold = make_sound(sine, 0.2, 800, 0.5)
        snd_powerup  = make_sound(sine, 0.25, 500, 0.4)
        snd_die      = make_sound(sine, 0.5, 180, 0.5)
        snd_move     = make_sound(sine, 0.03, 300, 0.12)
    except:
        # Se falhar (ex: sem hardware de som), cria objetos mudos
        class DummySound:
            def play(self): pass
        snd_eat = snd_eat_gold = snd_powerup = snd_die = snd_move = DummySound()
