import numpy as np
import pandas as pd
from scipy.fft import fft, fftfreq
from scipy.signal import correlate

from fonction import load_csv_auto

# Fonction pour charger le fichier CSV et traiter les données
def load_data(file_path):
    df = load_csv_auto(file_path)
    time = df["time"].values
    wx = df["wx"].values
    wy = df["wy"].values
    wz = df["wz"].values
    return time, wx, wy, wz

# Fonction pour calculer la FFT, la fréquence dominante et le gain
def calculate_fft_and_dominant_frequency(signal, dt):
    N = len(signal)
    freqs = fftfreq(N, d=dt)
    fft_signal = np.abs(fft(signal))
    positive_freqs = freqs[freqs > 0]
    positive_fft_signal = fft_signal[freqs > 0]
    dominant_freq = positive_freqs[np.argmax(positive_fft_signal)]
    return positive_freqs, positive_fft_signal, dominant_freq

# Fonction pour calculer le gain en dB
def calculate_gain(vitesse_reel, vitesse):
    return 20 * np.log10(vitesse_reel / vitesse)

# Fonction pour calculer le déphasage en degrés
def calculate_phase(signal, dominant_freq, time, dt):
    ref_signal = np.sin(2 * np.pi * dominant_freq * time)
    corr = correlate(signal, ref_signal, mode="full")
    lag = np.argmax(corr) - (len(signal) - 1)
    phase_shift = (lag * dt) * dominant_freq * 360
    return phase_shift

# Fonction pour générer les données JSON
def generate_bode_data(time, signal, vitesse):
    freqs, fft_signal, dominant_freq = calculate_fft_and_dominant_frequency(signal, np.mean(np.diff(time)))
    gain_db = 20 * np.log10(fft_signal / np.max(fft_signal))
    phase_shift = calculate_phase(signal, dominant_freq, time, np.mean(np.diff(time)))

    # Créer un dictionnaire avec les données nécessaires
    data = {
        "frequencies": freqs.tolist(),
        "gain_db": gain_db.tolist(),
        "phase_shift": phase_shift
    }
    return data

def save_bode_data_to_json(file_path, vitesse):
    time, wx, wy, wz = load_data(file_path)

    # Calculs pour wx
    bode_data_x = generate_bode_data(time, wx, vitesse)

    # Calculs pour wy
    bode_data_y = generate_bode_data(time, wy, vitesse)

    # Calculs pour wz
    bode_data_z = generate_bode_data(time, wz, vitesse)

    # Enregistrer les données sous format JSON
    result = {
        "wx_axis": bode_data_x,
        "wy_axis": bode_data_y,
        "wz_axis": bode_data_z
    }
    return result