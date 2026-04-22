#!/usr/bin/env python3
"""Ronda final - female_03 vs female_06 con Shakespeare."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lucy_alltalk import speak
import time

# Hamlet - "Ser o no ser" (fragmento)
shakespeare_1 = (
    "Ser o no ser, esa es la cuestión. "
    "¿Qué es más noble para el alma? ¿Sufrir los golpes y las flechas "
    "de la insultante fortuna, o tomar las armas contra un mar de adversidades "
    "y, enfrentándose a ellas, acabar con todo?"
)

# Romeo y Julieta - Balcón (fragmento adaptado)
shakespeare_2 = (
    "¿Qué hay en un nombre? Lo que llamamos rosa, "
    "con otro nombre conservaría su perfume. "
    "Así Romeo, aunque no se llamara Romeo, "
    "conservaría la adorable perfección que tiene, sin ese título."
)

print("=" * 50)
print(">>> RONDA 1: female_03 — Hamlet")
print("=" * 50)
speak(shakespeare_1, voice="female_03.wav", language="es")
time.sleep(2)

print("\n" + "=" * 50)
print(">>> RONDA 2: female_06 — Hamlet")
print("=" * 50)
speak(shakespeare_1, voice="female_06.wav", language="es")
time.sleep(2)

print("\n" + "=" * 50)
print(">>> RONDA 3: female_03 — Romeo y Julieta")
print("=" * 50)
speak(shakespeare_2, voice="female_03.wav", language="es")
time.sleep(2)

print("\n" + "=" * 50)
print(">>> RONDA 4: female_06 — Romeo y Julieta")
print("=" * 50)
speak(shakespeare_2, voice="female_06.wav", language="es")

print("\n>>> RONDA FINAL COMPLETADA")
