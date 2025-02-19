import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt

from fonction import load_csv_auto

# Fonction pour charger les données depuis un fichier CSV
def load_data(file_path):
    df = load_csv_auto(file_path)
    df.columns = ["time", "ax", "ay", "az", "wx", "wy", "wz"]
    return df

# Fonction pour calculer le biais du gyroscope à partir des données statiques (fichier séparé)
def calculate_gyro_bias_static(static_file_path):
    # Charger les données statiques du fichier CSV (données où le gyroscope est supposé être au repos)
    df_static = load_csv_auto(static_file_path)
    df_static.columns = ["time", "wx", "wy", "wz"]
    
    # Sélectionner les lignes où les vitesses angulaires sont proches de zéro
    gyro_data_static = df_static[['wx', 'wy', 'wz']]
    
    # Calculer la moyenne des vitesses angulaires pour obtenir le biais (moyenne des valeurs autour de zéro)
    bias_x = gyro_data_static['wx'].mean()
    bias_y = gyro_data_static['wy'].mean()
    bias_z = gyro_data_static['wz'].mean()

    # Retourner les biais calculés
    return np.array([bias_x, bias_y, bias_z])

# Fonction pour appliquer un filtre passe-bas (utile pour filtrer les données du gyroscope)
def lowpass_filter(data, cutoff_freq, sample_rate):
    nyquist = 0.5 * sample_rate
    normal_cutoff = cutoff_freq / nyquist
    b, a = butter(1, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

# Fonction de filtrage de Kalman pour les vitesses angulaires du gyroscope
def kalman_filter(gyro_data, process_noise=1e-5, measurement_noise=1e-1):
    n = len(gyro_data)
    
    # Initialisation des variables
    estimate = np.zeros(n)
    estimate[0] = gyro_data[0]  # Initialisation de l'estimation avec la première valeur
    estimate_error = np.ones(n) * 1e-1  # Estimation de l'erreur initiale
    kalman_gain = np.zeros(n)
    
    # Application du filtre de Kalman
    for i in range(1, n):
        # Prédiction de l'état suivant
        estimate[i] = estimate[i-1]
        estimate_error[i] = estimate_error[i-1] + process_noise
        
        # Calcul du gain de Kalman
        kalman_gain[i] = estimate_error[i] / (estimate_error[i] + measurement_noise)
        
        # Mise à jour de l'estimation
        estimate[i] = estimate[i] + kalman_gain[i] * (gyro_data[i] - estimate[i])
        
        # Mise à jour de l'erreur d'estimation
        estimate_error[i] = (1 - kalman_gain[i]) * estimate_error[i]
    
    return estimate

# Fonction pour appliquer un filtre complémentaire et fusionner les données du gyroscope et de l'accéléromètre
def complementary_filter(gyro_data, accel_data, alpha=0.98, dt=0.01):
    # Initialisation de l'orientation (angle) du filtre complémentaire
    angle_x = 0.0
    angle_y = 0.0
    angles = []

    # On boucle à travers les mesures du gyroscope et de l'accéléromètre
    for i in range(1, len(gyro_data)):
        # Mesures du gyroscope en radians/s (wx, wy, wz)
        wx, wy, wz = gyro_data[i-1]

        # Mesures de l'accéléromètre (ax, ay, az) -> on calcule les angles de pitch et roll
        ax, ay, az = accel_data[i-1]
        
        # Calcul de l'angle d'accélération (accéléromètre)
        pitch_accel = np.arctan2(ay, az) * 180 / np.pi  # en degrés
        roll_accel = np.arctan2(-ax, np.sqrt(ay**2 + az**2)) * 180 / np.pi  # en degrés

        # Mise à jour des angles avec le filtre complémentaire
        angle_x = alpha * (angle_x + wx * dt) + (1 - alpha) * pitch_accel
        angle_y = alpha * (angle_y + wy * dt) + (1 - alpha) * roll_accel

        # Stocker les angles
        angles.append([angle_x, angle_y])

    return np.array(angles)

# Fonction pour corriger les données du gyroscope avec le biais et appliquer le filtre de Kalman
def correct_gyro_data(df, bias):
    # Correction des données en soustrayant le biais du gyroscope
    df['wx_corrected'] = df['wx'] - bias[0]
    df['wy_corrected'] = df['wy'] - bias[1]
    df['wz_corrected'] = df['wz'] - bias[2]
    
    # Application d'un filtre de Kalman sur les données corrigées
    df['wx_filtered'] = kalman_filter(df['wx_corrected'])
    df['wy_filtered'] = kalman_filter(df['wy_corrected'])
    df['wz_filtered'] = kalman_filter(df['wz_corrected'])



    return df[['time','wx_filtered', 'wy_filtered', 'wz_filtered']]

import numpy as np

# Fonction pour corriger les vitesses angulaires à partir des angles
def correct_ang_velo(df_corrected_2,bias):
    # Extraire les angles du DataFrame corrigé
    angle_x = df_corrected_2['angle_x_complementary'].values  # Pitch
    angle_y = df_corrected_2['angle_y_complementary'].values  # Roll
    wx = df_corrected_2['wx'].values  # Vitesse angulaire sur X
    wy = df_corrected_2['wy'].values  # Vitesse angulaire sur Y
    wz = df_corrected_2['wz'].values  # Vitesse angulaire sur Z

    # Correction du biais (soustraction du biais calculé)
    wx_corrected = wx - bias[0]
    wy_corrected = wy - bias[1]
    wz_corrected = wz - bias[2]

    # Correction géométrique des vitesses angulaires en utilisant les angles de pitch et roll
    corrected_wx = wx_corrected * np.cos(np.radians(angle_y)) - wy_corrected * np.sin(np.radians(angle_y))
    corrected_wy = wx_corrected * np.sin(np.radians(angle_y)) + wy_corrected * np.cos(np.radians(angle_y))
    corrected_wz = wz_corrected  # Aucune correction sur l'axe Z

    # Ajouter les vitesses angulaires corrigées dans le DataFrame
    df_corrected_2['wx_corrected'] = corrected_wx
    df_corrected_2['wy_corrected'] = corrected_wy
    df_corrected_2['wz_corrected'] = corrected_wz

    angular_data = df_corrected_2[['time','angle_x_complementary', 'angle_y_complementary']]
    df_corrected_2 = df_corrected_2[['time','wx_corrected', 'wy_corrected', 'wz_corrected']]
    
    return df_corrected_2, angular_data


# Fonction principale qui combine tout
def calibrate_gyro(file_path, static_file_path):
    # Charger les données du fichier principal
    df = load_data(file_path)
    
    # Charger les données de l'accéléromètre (exemples : ax, ay, az)
    accel_data = df[['ax', 'ay', 'az']].values

    # Calculer le biais du gyroscope à partir des données statiques
    bias = calculate_gyro_bias_static(static_file_path)
    
    # Correction des données avec la première méthode (biais + filtre de Kalman)
    df_corrected_1 = correct_gyro_data(df.copy(), bias)
    
    # Fusion des données du gyroscope et de l'accéléromètre avec le filtre complémentaire (deuxième méthode)
    gyro_data = df[['wx', 'wy', 'wz']].values
    angles = complementary_filter(gyro_data, accel_data)
    
    # Ajouter les angles calculés au DataFrame
    df_corrected_2 = df.copy()
    df_corrected_2 = df_corrected_2.iloc[1:].reset_index(drop=True)
    df_corrected_2['angle_x_complementary'] = angles[:, 0]
    df_corrected_2['angle_y_complementary'] = angles[:, 1]

    df_corrected_2, angular_data = correct_ang_velo(df_corrected_2,bias)

    # Retourner le biais, le DataFrame original, le DataFrame corrigé par la 1ère méthode, et le DataFrame corrigé par la 2ème méthode
    return bias, df, df_corrected_1, df_corrected_2, angular_data
