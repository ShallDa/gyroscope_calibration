import numpy as np
import pandas as pd
import os

def rotation(df):
    # Extrait les entetes
    entetes = df.columns.tolist()
    gyro_data = df[[entetes[1], entetes[2], entetes[3]]].to_numpy()
    time = df[entetes[0]].to_numpy()
    # Calculer l'intervalle de temps (dt)
    dt = np.diff(time).mean()  # Moyenne des intervalles de temps
    # Intégration des vitesses angulaires pour obtenir les angles
    angles = np.cumsum(gyro_data, axis=0) * dt  # θx, θy, θz
    # Rotation en degré de X
    rotation_x = np.degrees(angles[:, 0])  # Convertir en degrés
    # Rotation en degré de Y
    rotation_y = np.degrees(angles[:, 1])  # Convertir en degrés
    # Rotation en degré de Z
    rotation_z = np.degrees(angles[:, 2])  # Convertir en degrés
    rotations_df = pd.DataFrame({
        'time': time,  
        'rotation_X': rotation_x,
        'rotation_Y': rotation_y,
        'rotation_Z': rotation_z
    })
    
    return rotations_df

def epuration(df, axe, vitesse):
    # Nombre de lignes à ajouter autour des blocs
    n_lignes_ajouter = 20
    # Sélectionner la colonne en fonction de l'axe
    val = 1 if axe == "X" else 2 if axe == "Y" else 3 if axe == "Z" else None
    colonne = df.columns[val]
    # Créer une nouvelle colonne "dessus" qui est True si la valeur absolue est au-dessus du seuil
    df['dessus'] = df[colonne] > (vitesse * 0.2)
    # Liste des indices où les valeurs sont au-dessus du seuil
    dessus_seuil = df[df['dessus']].index.tolist()
    # Liste pour stocker les séquences valides
    sequences_valides = []
    i = 0
    # Parcourir les indices pour identifier les blocs de données consécutives au-dessus du seuil
    while i < len(dessus_seuil):
        start = dessus_seuil[i]
        end = start
        # Trouver la fin de la séquence consécutive au-dessus du seuil
        while i < len(dessus_seuil) - 1 and dessus_seuil[i + 1] == dessus_seuil[i] + 1:
            end = dessus_seuil[i + 1]
            i += 1
        # Ajouter la séquence trouvée à la liste des séquences valides
        sequence = df.iloc[start:end + 1]
        sequences_valides.append(sequence)
        i += 1
    # Fusionner les séries proches si au moins 5 séries sont détectées
    # ------------------------------------
    if vitesse < 0.5 :
        if len(sequences_valides) >= 5:
            merged_sequences = []
            i = 0
            while i < len(sequences_valides):
                current_sequence = sequences_valides[i]
                start_idx = current_sequence.index[0]
                end_idx = current_sequence.index[-1]
                # Fusionner avec les séquences suivantes si elles sont proches
                while i < len(sequences_valides) - 1 and \
                        sequences_valides[i + 1].index[0] - end_idx <= 30:
                    next_sequence = sequences_valides[i + 1]
                    end_idx = next_sequence.index[-1]
                    current_sequence = pd.concat([current_sequence, next_sequence])
                    i += 1
                merged_sequences.append(current_sequence)
                i += 1
            sequences_valides = merged_sequences
    #-------------------------------------------
    # Si des séquences valides ont été trouvées
    if sequences_valides:
        # Trier les séquences valides par longueur et garder la plus longue
        sequences_valides.sort(key=lambda x: len(x), reverse=True)
        # Récupérer la plus grande séquence
        df_clean = sequences_valides[0]
        # Ajouter des lignes avant et après le plus grand bloc
        start_idx = df_clean.index[0]
        end_idx = df_clean.index[-1]
        # Ajouter n_lignes_ajouter autour du bloc (respecter les bords du DataFrame)
        indices_a_conserver = range(max(start_idx - n_lignes_ajouter, 0), min(end_idx + n_lignes_ajouter, len(df) - 1) + 1)
        df_clean = df.iloc[indices_a_conserver]
    else:
        # Si aucune séquence valide n'est trouvée, retourner un DataFrame vide
        df_clean = pd.DataFrame()
    # Supprimer la colonne temporaire 'dessus'
    df_clean = df_clean.copy()
    df_clean.drop(columns=['dessus'], inplace=True)
    # Retourner le DataFrame filtré
    return df_clean

def stat(df_vit,df_ang,axe,vitesse):
    
    val = 1 if axe == "X" else 2 if axe == "Y" else 3 if axe == "Z" else None
    # Sélectionner la colonne correspondant à l'axe
    colonne = df_vit.columns[val]
    colonne2 = df_ang.columns[val]
    # Créer une nouvelle colonne "dessus" qui est True si la valeur est au-dessus du seuil
    df_vit = df_vit.copy()
    df_vit['dessus'] = df_vit[colonne] > (vitesse * 0.2)
    moyenne_vit = df_vit.loc[df_vit['dessus'],df_vit.columns[val]].mean()
    ecart_vit = df_vit.loc[df_vit['dessus'],df_vit.columns[val]].std()
    variance_vit = df_vit.loc[df_vit['dessus'],df_vit.columns[val]].var()
    max_angle = df_ang[colonne2].max() 

    return moyenne_vit, ecart_vit, variance_vit, max_angle

def calcul_stat(directory_path,base_folder):
    if base_folder != "":
        dico = {}
        first_path = os.path.join(directory_path, base_folder) # On créé le chemin de base 
        first_folders = [folder for folder in os.listdir(first_path) if os.path.isdir(os.path.join(first_path, folder))] # On récupère les dossiers
        for first_folder in first_folders: # Pour chaque dossier 
            if(first_folder != "Statique"):
                second_path = os.path.join(directory_path, base_folder, first_folder) # Créé un nouveau chemin 
            else :
                continue
            if not os.path.exists(second_path): continue
            second_folders = [folder for folder in os.listdir(second_path) if os.path.isdir(os.path.join(second_path, folder))] # On récupère les dossiers
            for second_folder in second_folders:
                third_path = os.path.join(directory_path, base_folder, first_folder, second_folder) # Créé un nouveau chemin 
                if not os.path.exists(third_path): continue
                third_folders = [folder for folder in os.listdir(third_path) if os.path.isdir(os.path.join(third_path, folder))] # On récupère les dossiers
                for third_folder in third_folders:
                    fourth_path = os.path.join(directory_path, base_folder, first_folder, second_folder, third_folder) # Créé un nouveau chemin 
                    if not os.path.exists(fourth_path): continue
                    documents = [file for file in os.listdir(fourth_path) if file.endswith('.csv')]
                    for document in documents:
                        final_path =  os.path.join(directory_path, base_folder, first_folder, second_folder, third_folder, fourth_path, document)
                        dico.update({document:final_path})  
        return dico
    else :
        return "erreur"
    
def track_path(file,test,directory):
    nom = file.filename
    modele = nom.split("_")[0]
    vitesse = nom.split("_")[2]
    distance = nom.split("_")[3]
    if test == "Statique":
        distance = distance.split(".")[0]
    ultimate_path = os.path.join(directory,modele,test,vitesse,distance)
    if not os.path.exists(ultimate_path):
        os.makedirs(ultimate_path)
    final_path = os.path.join(directory,modele,test,vitesse,distance,nom)
    if os.path.exists(final_path):
        existe = "Un document portant le même nom est déjà présent dans la BDD."
        return existe
    file.save(final_path)
    existe = "Document déposé"
    if not os.path.exists(final_path):
        existe = "Dépôt échoué"
    return existe

def conversion(ts):
    dt = pd.to_datetime(ts)
    return float(f"{dt.second}.{dt.microsecond // 1000}")  # Convertir en float

def load_csv_auto(filepath):
    # Ouvrir le fichier pour lire la première ligne et détecter le séparateur
    with open(filepath, "r") as f:
        first_line = f.readline()

    # Détecter si le fichier contient plus de ";" ou ","
    sep = ";" if first_line.count(";") > first_line.count(",") else ","

    # Si le séparateur est ";", remplacer les virgules par des points dans le fichier
    if sep == ";":
        # Lire tout le fichier et remplacer les virgules par des points
        with open(filepath, "r") as f:
            content = f.read()
        content = content.replace(",", ".")

        # Sauvegarder dans un fichier temporaire pour que pandas puisse le lire correctement
        temp_filepath = "temp_file.csv"
        with open(temp_filepath, "w") as f:
            f.write(content)

        # Charger le fichier avec le bon séparateur
        df = pd.read_csv(temp_filepath, delimiter=sep)
    else:
        # Si le séparateur est ",", on charge directement le fichier
        df = pd.read_csv(filepath, delimiter=sep)
    df.columns = [col.split()[0] for col in df.columns]    

    return df
