import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from correctif import calculate_gyro_bias_static

from fonction import epuration, load_csv_auto

# Charger les données depuis un fichier CSV
def load_data(filename,axe,vit,rota):
    df = load_csv_auto(filename)
    if "i" not in rota:
        dfa = epuration(df,axe,vit)
    else:
        dfa = df
    return dfa

# Estimer le facteur d'échelle en comparant avec une vitesse connue
def estimate_scale_factors(df, vitesse):
    measured_avg = np.array(df[["wx", "wy", "wz"]].abs().mean())  # Moyenne des valeurs absolues
    if np.any(measured_avg == 0):
        raise ValueError("Les vitesses mesurées contiennent des valeurs nulles.")
    scale_factors = vitesse / measured_avg  # Ratio entre la vitesse réelle et la mesure
    return scale_factors

# Estimer la matrice de correction (si nécessaire)
def estimate_correction_matrix(df, vitesse):
    measured_values = np.array(df[["wx", "wy", "wz"]])
    real_values = np.full_like(measured_values, vitesse)  

    # Trouver la matrice de correction qui ajuste les mesures
    print("Measured values shape:", measured_values.shape)
    print("Real values shape:", real_values.shape)
    correction_matrix, _, _, _ = np.linalg.lstsq(measured_values, real_values, rcond=None)
    return correction_matrix

# Appliquer la correction aux mesures
def apply_correction(df, bias, scale_factors, correction_matrix):
    corrected_data = (np.array(df[["wx", "wy", "wz"]]) - bias) * scale_factors
    correction_matrix_inv = np.linalg.pinv(correction_matrix)  
    corrected_data = corrected_data @ correction_matrix_inv
    return corrected_data

# Fonction principale
def calibrate_gyroscope(filename, df_static, vitesse,axe, rota):
    df = load_data(filename,axe,vitesse,rota)
    bias_T = calculate_gyro_bias_static(df_static)
    scale_factors_T = estimate_scale_factors(df, vitesse)
    correction_matrix = estimate_correction_matrix(df, vitesse)
    val = 0 if axe == "X" else 1 if axe == "Y" else 2 if axe == "Z" else None

    matrice_1x3 = np.array([1, 1, 1], dtype=float)
    matrice_1x3[val] = scale_factors_T[val]
    correction_matrix[:,val] = 0
    correction_matrix[val,:] = 0
    correction_matrix[val,val] = 1

    print("Biais estimé:", bias_T)
    print(scale_factors_T)
    print("Facteurs d'échelle:", matrice_1x3)
    print("Matrice de correction:\n", correction_matrix)

    # Appliquer les corrections
    corrected_data = apply_correction(df, bias_T, matrice_1x3, correction_matrix)
    
    # Sauvegarde des résultats
    corrected_df = df.copy()
    corrected_df[["wx_corr", "wy_corr", "wz_corr"]] = corrected_data
    corrected_df = corrected_df[["time","wx_corr", "wy_corr", "wz_corr"]]

    correction_list = np.array(correction_matrix)
    labels = ['X','Y','Z']
    bias = {"columns":labels, "data":bias_T.tolist()}
    scale_factors = {"columns":labels, "data":matrice_1x3.tolist()}
    correction = {"columns": labels, "rows": labels, "data":correction_list.tolist()}
    df_bias = pd.DataFrame([bias["data"]], columns=bias["columns"])
    df_scale_factors = pd.DataFrame([scale_factors["data"]], columns=scale_factors["columns"])
    df_correction = pd.DataFrame(correction["data"], columns=correction["columns"], index=correction["rows"])

    return corrected_df, df_bias, df_scale_factors, df_correction
    

