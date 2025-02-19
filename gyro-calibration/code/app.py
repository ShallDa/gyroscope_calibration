## Déclaration des bibliothèques
from flask import Flask,render_template,request,jsonify
import time, os
import pandas as pd
import serial

## Import des fonctions
from fonction import rotation, epuration, stat, calcul_stat, track_path, conversion, load_csv_auto
from correctif import calibrate_gyro

## Initialisation de l'objet Flask
app = Flask(__name__)

## Initialisation des différentes pages du site internet
@app.route("/") ## Accès à la Home Page
def home():
    return render_template("Site.html")

@app.route("/angle", methods=['POST','GET']) ## Accès discret à la fonction angle
def angle():
    ## Initialisation de l'objet Arduino
    portcom = request.form.get('COM')
    print(portcom)
    arduino = serial.Serial(port=portcom, baudrate=9600, timeout=1)
    time.sleep(2)
    commande = request.form.get('angle')
    print(commande)
    arduino.write(str(commande).encode())  # Encode la commande en bytes
    time.sleep(1)  # Attends un peu pour s'assurer que l'Arduino a reçu la commande
    while not arduino.in_waiting:
        time.sleep(0.1)
    print(arduino.readline().decode().strip())  # Lire la réponse
    return "donnée envoyée"

# Chemin du répertoire principal contenant les dossiers
base_directory_path = os.path.join(app.static_folder, 'DataCenter')

# Endpoint pour obtenir la liste des dossiers du répertoire principal
@app.route('/basefolders')
def get_base_folders():
    ## On récupère les dossiers
    base_folders = [folder for folder in os.listdir(base_directory_path) if os.path.isdir(os.path.join(base_directory_path, folder))]
    return jsonify(base_folders)

# Endpoint pour obtenir la liste des dossiers dans un sous-répertoire spécifique
@app.route('/subfolders', methods=['POST'])
def get_sub_folders():
    base_folder = request.json['base_folder'] # On récupère le chemin de base
    sub_directory_path = os.path.join(base_directory_path, base_folder) # On créé le nouveau chemin
    ## On récupère les dossiers
    sub_folders = [folder for folder in os.listdir(sub_directory_path) if os.path.isdir(os.path.join(sub_directory_path, folder)) and folder != "Statique"]
    return jsonify(sub_folders)

# Endpoint pour obtenir les fichiers présents dans le dossier
@app.route('/filesData', methods=['POST'])
def get_tierce_folders():
    base_folder = request.json['base_folder'] # On récupère le chemin de base
    sub_folder = request.json['sub_folder'] # On récupère le chemin du sous dossier
    tierce_directory_path = os.path.join(base_directory_path, base_folder, sub_folder) # On créé le chemin
    ## On récupère les fichiers
    tierce_files = [folder for folder in os.listdir(tierce_directory_path) if os.path.isdir(os.path.join(tierce_directory_path, folder))]
    return jsonify(tierce_files)

# Endpoint pour obtenir les fichiers présents dans le dossier
@app.route('/csvfiles', methods=['POST'])
def get_csv_files():
    base_folder = request.json['base_folder'] # On récupère le chemin de base
    sub_folder = request.json['sub_folder'] # On récupère le chemin du sous dossier
    tierce_folder = request.json['tierce_folder']
    forth_directory_path = os.path.join(base_directory_path, base_folder, sub_folder, tierce_folder) # On créé le chemin
    ## On récupère les fichiers
    csv_files = [folder for folder in os.listdir(forth_directory_path) if os.path.isdir(os.path.join(forth_directory_path, folder))]
    return jsonify(csv_files)

# Endpoint pour obtenir les fichiers présents dans le dossier
@app.route('/modelo', methods=['POST'])
def get_modelo_files():
    base_folder = request.json['base_folder'] # On récupère le chemin de base
    sub_folder = request.json['sub_folder'] # On récupère le chemin du sous dossier
    tierce_folder = request.json['tierce_folder']
    forth_folder = request.json['forth_folder']
    final_directory_path = os.path.join(base_directory_path, base_folder, sub_folder, tierce_folder, forth_folder) # On créé le chemin
    ## On récupère les fichiers
    modele = [file for file in os.listdir(final_directory_path) if file.endswith('.csv')]
    return jsonify(modele)


@app.route('/affichage', methods=['POST'])
def get_data():
    #Récupère le chemin
    acc={}
    baseFold = request.json['baseFold']
    subFold = request.json['subFold']
    tierFold = request.json['tierFold']
    excel = request.json['excel']
    final = request.json['fin']
    fichier = os.path.join(base_directory_path, baseFold, subFold, tierFold, excel, final)
    #Récupère les élements indicateurs du nom du fichier
    axe_pre = str(final.split("_")[1])
    axe = axe_pre[0]
    module = axe_pre[1]
    vitesse = float(final.split("_")[2])
    print(vitesse)
    yValue = final.split("_")[3]
    #Lecture du fichier
    df = load_csv_auto(fichier)
    if vitesse != 0 and module=="G":
        df.columns = ["time", "wx", "wy", "wz"]
        data_traite = epuration(df,axe,vitesse)
    else :
        data_traite = df
    data = data_traite.to_dict(orient="records")
    if module!="A":
        if module !="G":
            df.columns = ["time", "ax", "ay", "az", "wx", "wy", "wz"]
            df['time'] = df['time'].apply(conversion)
            data_acc = df.iloc[:,[0, 1, 2, 3]]
            data_traite = df.iloc[:, [0, 4, 5, 6]]
            data = data_traite.to_dict(orient="records")
            acc = data_acc.to_dict(orient="records")
            data_acc.columns = ["time", "ax", "ay", "az"]
        data_traite.columns = ["time", "wx", "wy", "wz"]
        data_rotation = rotation(data_traite)
        rotat = data_rotation.to_dict(orient="records")
        moy, std, var, max = stat(data_traite, data_rotation, axe, vitesse)
    else:
        data_traite.columns = ["time", "ax", "ay", "az"]
        val = 1 if axe == "X" else 2 if axe == "Y" else 3 if axe == "Z" else None
        colonne = data_traite.columns[val]
        moy = data_traite[colonne].mean()
        std = data_traite[colonne].std()
        var = data_traite[colonne].var()
        max = data_traite[colonne].max()
        rotat = {}
    return jsonify({"data_rotation": rotat, "data": data, "yValue": yValue, 
                    "moy":moy, "std":std, "var":var, "max":max, "vit":vitesse, "module":module, "acc":acc})

@app.route('/statistiques', methods=['POST'])
def get_statistiques():
    all_stats= {}
    all_docs= []
    baseFolder = request.json['baseFold']
    all_stats = calcul_stat(base_directory_path, baseFolder)
    for nom, access_path in all_stats.items():
        m=0
        axe_pre = nom.split("_")[1]
        axe = axe_pre[0]
        module = axe_pre[1]
        vitesse = float(nom.split("_")[2])
        yValue = nom.split("_")[3]
        correct_path = os.path.normpath(access_path)
        new_path = correct_path.split(os.sep)[-4]
        df = load_csv_auto(access_path)
        if vitesse != 0 and module=="G":
            df.columns = ["time", "wx", "wy", "wz"]
            data_traite = epuration(df,axe,vitesse)
        else :
            data_traite = df
        if module!="A":
            if module !="G":
                df.columns = ["time", "ax", "ay", "az", "wx", "wy", "wz"]
                df['time'] = df['time'].apply(conversion)
                data_acc = df.iloc[:,[0, 1, 2, 3]]
                data_traite = df.iloc[:, [0, 4, 5, 6]]
                data_acc.columns = ["time", "ax", "ay", "az"]
                val = 1 if axe == "X" else 2 if axe == "Y" else 3 if axe == "Z" else None
                colonne = data_acc.columns[val]
                moy = data_acc[colonne].mean()
                std = data_acc[colonne].std()
                var = data_acc[colonne].var()
                m = 1
                all_docs.append({'path':new_path, 'axe':axe, 'vit':vitesse, 'obj':yValue, 'moy':moy, 'std':std, 'var':var, 'module':'A', 'M':m})
                module = "G"
            data_traite.columns = ["time", "wx", "wy", "wz"]
            data_rotation = rotation(data_traite)
            moy, std, var, max = stat(data_traite, data_rotation, axe, vitesse)
        else:
            data_traite.columns = ["time", "ax", "ay", "az"]
            val = 1 if axe == "X" else 2 if axe == "Y" else 3 if axe == "Z" else None
            colonne = data_traite.columns[val]
            moy = data_traite[colonne].mean()
            std = data_traite[colonne].std()
            var = data_traite[colonne].var()
        all_docs.append({'path':new_path, 'axe':axe, 'vit':vitesse, 'obj':yValue, 'moy':moy, 'std':std, 'var':var, 'module':module, 'M':m})
    return jsonify(all_docs)

@app.route('/register', methods=['POST'])
def enregistrement():
    test = request.form.get("type")
    files = request.files.getlist('files[]')
    for file in files:
        resultat = track_path(file,test,base_directory_path)
    return resultat

@app.route('/doubleFiles', methods=['POST'])
def load_M():
    pre_dico = {}
    dicoM = {}
    folder = request.json["phone"]
    pre_dico = calcul_stat(base_directory_path,folder)
    for nom, access_path in pre_dico.items():
        newn = nom.split('_')[1]
        if "M" in newn:
            dicoM[nom] = access_path
    file_list = list(dicoM.items())
    return jsonify(file_list)           
    
@app.route('/correction', methods=['POST'])
def correction():
    file_path = request.json['chemin']
    new_path = os.path.normpath(file_path)
    segments = new_path.split(os.sep)
    segfile = segments[-1].split('_')
    nom = segfile[0] + "_G_0_0.csv"
    static_file_path = os.path.join(base_directory_path,segments[-5],"Statique","0","0",nom )
    gyro_bias, df, df_corrected_1, df_corrected_2, angular_data = calibrate_gyro(new_path, static_file_path)
    #Correction du temps
    df['time'] = df['time'].apply(conversion)
    df_corrected_1['time'] = df_corrected_1['time'].apply(conversion)
    df_corrected_2['time'] = df_corrected_2['time'].apply(conversion)
    angular_data['time'] = angular_data['time'].apply(conversion)
    #Recupération data gyro
    dfGD = df[['time','wx','wy','wz']]
    #Rotation
    dfGRD = rotation(dfGD)
    dfbiaisRD = rotation(df_corrected_1)
    dffusionRD = rotation(df_corrected_2)
    #Dictionnaire / liste
    biais = gyro_bias.tolist()
    dfG = dfGD.to_dict(orient="records")
    dfbiais = df_corrected_1.to_dict(orient="records")
    dffusion = df_corrected_2.to_dict(orient="records")
    dfang = angular_data.to_dict(orient="records")
    dfGR = dfGRD.to_dict(orient="records")
    dfbiaisR = dfbiaisRD.to_dict(orient="records")
    dffusionR = dffusionRD.to_dict(orient="records")
    print(biais)
    print("Données originales :\n", dfGD.head())
    print("Données corrigées Kalman :\n", df_corrected_1.head())
    print("Données corrigées géométriquement :\n", df_corrected_2.head())
    return jsonify({"biais":biais, "dfG":dfG, "dfbiais":dfbiais, "dffusion":dffusion, "dfang":dfang,
                        "dfGR":dfGR, "dfbiaisR":dfbiaisR, "dffusionR":dffusionR })
