Chart.register(ChartZoom);

//---------------------------- Fonction pour bouton -------------------------------

function setActive(button, contentId) {
    // Retirer la classe active de tous les boutons
    document.querySelectorAll('.sidebar button').forEach(function(btn) {
        btn.classList.remove('active');
    });
    // Ajouter la classe active au bouton cliqué
    button.classList.add('active');

    // Rendre tous les contenus invisibles
    document.querySelectorAll('.button-content').forEach(function(content) {
        content.style.display = 'none';
    });
    // Rendre le contenu du bouton correspondant visible
    document.getElementById(contentId).style.display = 'block';
}

document.addEventListener('DOMContentLoaded',function() {
    document.getElementById('data_affichage').style.display = 'none';
    document.getElementById('graphiques').style.display = 'none';
    document.getElementById('test').style.display = 'block';
    document.getElementById('envoie').style.display = 'none';
    data_com();
    loadselect1();
});

//---------------------------- Fonction pour remplir menus déroulants -------------------------------

function loadselect1(){
    const baseFoldersSelect = document.getElementById('baseFoldersSelect'); // On récupère nos select par leur ID
    const subFoldersSelect = document.getElementById('subFoldersSelect');
    const tierceFoldersSelect = document.getElementById('precision');
    const finalFoldersSelect = document.getElementById('fichierData');
    const modeleSelect = document.getElementById('modele');
    const baseFoldersSelect2 = document.getElementById('baseFoldersSelect2'); // On récupère nos select par leur ID
    const baseFoldersSelectM = document.getElementById('mFiles');
    while (baseFoldersSelect.options.length > 1) { // Remet a zéro pour éviter les problèmes (select 1 & 1 pop up)
        baseFoldersSelect.remove(baseFoldersSelect.options.length - 1);
    }      
    while (subFoldersSelect.options.length > 1) { // Remet a zéro pour éviter les problèmes (select 2 & 2 pop up)
        subFoldersSelect.remove(subFoldersSelect.options.length - 1);
    } 
    while (tierceFoldersSelect.options.length > 1) { // Remet a zéro pour éviter les problèmes (select 3 & 3 pop up)
        tierceFoldersSelect.remove(tierceFoldersSelect.options.length - 1);
    } 
    while (finalFoldersSelect.options.length > 1) { // Remet a zéro pour éviter les problèmes (select 3 & 3 pop up)
        finalFoldersSelect.remove(finalFoldersSelect.options.length - 1);
    }   
    while (modeleSelect.options.length > 1) { // Remet a zéro pour éviter les problèmes (select 3 & 3 pop up)
        modeleSelect.remove(modeleSelect.options.length - 1);
    }   
    fetch('/basefolders') // On appelle la fonction correspondante à la route indiquée
        .then(response => response.json()) // On récupère la réponse
        .then(baseFolders => {
            baseFoldersSelect.innerHTML = '<option value="">Choix modele</option>';
            baseFolders.forEach(folder => { // Pour chaque dossier
                const option = document.createElement('option'); // On créé une option
                const option2 = document.createElement('option'); // On créé une option
                const option3 = document.createElement('option'); // On créé une option
                option.value = folder; // La valeur de l'option sera le nom du dossier
                option.textContent = folder; // La valeur affichée dans le select sera le nom du dossier
                option2.value = folder; // La valeur de l'option sera le nom du dossier
                option2.textContent = folder; // La valeur affichée dans le select sera le nom du dossier
                option3.value = folder; // La valeur de l'option sera le nom du dossier
                option3.textContent = folder; // La valeur affichée dans le select sera le nom du dossier
                baseFoldersSelect.appendChild(option); // On ajoute l'option au select
                baseFoldersSelect2.appendChild(option2);
                baseFoldersSelectM.appendChild(option3);
            });
        })
    .catch(error => console.error('Erreur lors de la récupération des dossiers principaux :', error)); // Si erreur
}

function select2remplissage(selectedBaseFolder, subFoldersSelect, tierceFolderSelect, finalFoldersSelect,modeleSelect){
    while (subFoldersSelect.options.length > 1) { // Remet a zéro pour éviter les problèmes
        subFoldersSelect.remove(subFoldersSelect.options.length - 1);
    }       
    while (tierceFolderSelect.options.length > 1) { // Remet a zéro pour éviter les problèmes
        tierceFolderSelect.remove(tierceFolderSelect.options.length - 1);
    }   
    while (finalFoldersSelect.options.length > 1) { // Remet a zéro pour éviter les problèmes (select 3 & 3 pop up)
        finalFoldersSelect.remove(finalFoldersSelect.options.length - 1);
    }    
    while (modeleSelect.options.length > 1) { // Remet a zéro pour éviter les problèmes (select 3 & 3 pop up)
        modeleSelect.remove(modeleSelect.options.length - 1);
    }   
    erase_graph();
    // Réinitialiser l'objet chartInstances
    chartInstances = {};
    fetch('/subfolders', { // On appelle la fonction correspondante à la route indiquée
        method: 'POST', // On utilise la méthode post pour y envoyer des données supplémentaire
        headers: { // Header qui indique le type du contenu 
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ base_folder: selectedBaseFolder }) // Variable à envoyer
    })
    .then(response => response.json()) // On récupère notre réponse
    .then(subFolders => { 
        subFoldersSelect.innerHTML = '<option value="">Choix Test</option>'; // Option par défaut
        subFolders.forEach(folder => { // Pour chaque dossier
            const option = document.createElement('option'); // On créé l'option
            option.value = folder; // La valeur attribuée sera le nom du dossier
            option.textContent = folder; // L'option affichée sera le nom du dossier
            subFoldersSelect.appendChild(option); // On ajoute l'option au select
        });
    })
    .catch(error => console.error('Erreur lors de la récupération des sous-dossiers :', error));
}

function select3remplissage(selectedBaseFolder,selectedSubFolder,actionSelect,finalFoldersSelect,modeleSelect){
    while (actionSelect.options.length > 1) { // Remet a zéro pour éviter les problèmes
        actionSelect.remove(actionSelect.options.length - 1);
    }
    while (finalFoldersSelect.options.length > 1) { // Remet a zéro pour éviter les problèmes (select 3 & 3 pop up)
        finalFoldersSelect.remove(finalFoldersSelect.options.length - 1);
    }   
    while (modeleSelect.options.length > 1) { // Remet a zéro pour éviter les problèmes (select 3 & 3 pop up)
        modeleSelect.remove(modeleSelect.options.length - 1);
    }   
    erase_graph();
    fetch('/filesData', { // On exécute la fonction du chemin indiquée
        method: 'POST', // Methode POST pour envoyer des variables 
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ base_folder: selectedBaseFolder, sub_folder: selectedSubFolder }) // Variables à envoyer
    })
    .then(response => response.json()) // On récupère la réponse
    .then(precise => {
        actionSelect.innerHTML = '<option value="">Choix Vitesse</option>'; // Valeur par défaut  
        precise.forEach(folder => { // Pour chaque fichier
            const option = document.createElement('option'); // On créé une option
            option.value = folder; // La valeur de l'option est le nom avec extension du fichier
            option.textContent = folder; // L'option affichée portera le nom du fichier sans l'extension
            actionSelect.appendChild(option); // On ajoute l'option
        });
    })
    .catch(error => console.error('Erreur lors de la récupération des fichiers .txt :', error)); // Si erreur
}

function select4remplissage(selectedBaseFolder,selectedSubFolder,actionSelect,finalFoldersSelect,modeleSelect){
    while (finalFoldersSelect.options.length > 1) { // Remet a zéro pour éviter les problèmes (select 3 & 3 pop up)
        finalFoldersSelect.remove(finalFoldersSelect.options.length - 1);
    }   
    while (modeleSelect.options.length > 1) { // Remet a zéro pour éviter les problèmes (select 3 & 3 pop up)
        modeleSelect.remove(modeleSelect.options.length - 1);
    }   
    erase_graph();
    fetch('/csvfiles', { // On exécute la fonction du chemin indiquée
        method: 'POST', // Methode POST pour envoyer des variables 
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ base_folder: selectedBaseFolder, sub_folder: selectedSubFolder, tierce_folder : actionSelect }) // Variables à envoyer
    })
    .then(response => response.json()) // On récupère la réponse
    .then(csvfiles => {
        finalFoldersSelect.innerHTML = '<option value="">Choix Rotation</option>'; // Option par défaut
        csvfiles.forEach(folder => { // Pour chaque dossier
            const option = document.createElement('option'); // On créé l'option
            option.value = folder; // La valeur attribuée sera le nom du dossier
            option.textContent = folder; // L'option affichée sera le nom du dossier
            finalFoldersSelect.appendChild(option); // On ajoute l'option au select
        });
    })
    .catch(error => console.error('Erreur lors de la récupération des fichiers .txt :', error)); // Si erreur
}

function select5remplissage(selectedBaseFolder,selectedSubFolder,actionSelect,finalFoldersSelect,modeleSelect){ 
    while (modeleSelect.options.length > 1) { // Remet a zéro pour éviter les problèmes (select 3 & 3 pop up)
        modeleSelect.remove(modeleSelect.options.length - 1);
    }   
    erase_graph();
    fetch('/modelo', { // On exécute la fonction du chemin indiquée
        method: 'POST', // Methode POST pour envoyer des variables 
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ base_folder: selectedBaseFolder, sub_folder: selectedSubFolder, tierce_folder : actionSelect, forth_folder : finalFoldersSelect }) // Variables à envoyer
    })
    .then(response => response.json()) // On récupère la réponse
    .then(mod => {
        modeleSelect.innerHTML = '<option value="">Choix Fichier</option>'; // Valeur par défaut  
        mod.forEach(file => { // Pour chaque fichier
            const option = document.createElement('option'); // On créé une option
            option.value = file; // La valeur de l'option est le nom avec extension du fichier
            option.textContent = file.split('.').slice(0, -1).join("."); // L'option affichée portera le nom du fichier sans l'extension
            modeleSelect.appendChild(option); // On ajoute l'option
        });
    })
    .catch(error => console.error('Erreur lors de la récupération des fichiers .txt :', error)); // Si erreur
}

//--------------------- Files M ------------------

function loadMFiles(phone){
    const Mf = document.getElementById('mfiles2'); 
    while (Mf.options.length > 1) { // Remet a zéro pour éviter les problèmes (select 3 & 3 pop up)
        Mf.remove(Mf.options.length - 1);
    }
    fetch("/doubleFiles", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ phone: phone})
    })
    .then(response => response.json()) // On récupère la réponse
    .then(fil => {
        Mf.innerHTML = '<option value="">Choix modele</option>';
        fil.forEach(([nom, access_path]) => { // Déstructure les éléments de chaque tuple
            const option = document.createElement('option');
            option.value = access_path; // Utilisez le nom du fichier (premier élément du tuple)
            option.textContent = nom.split('.').slice(0, -1).join("."); // Affichage sans l'extension
            Mf.appendChild(option);
        });
    })
    .catch(error => console.error('Erreur lors de la récupération des dossiers principaux :', error)); // Si erreur
}
//--------------------- Port COM -----------------

function data_com(){
    const port_com = document.getElementById('comcom');
    for (let i=0;i<16;i++){
        const option = document.createElement('option');
        option.value = `COM${i}`;
        option.textContent = `COM${i}`;
        port_com.appendChild(option);
    }
}

//---------------- Remettre Data dans l'ordre -------------------

function reorderData(data) {
    return data.map(row => {
        return {
            time: row.time,  
            ax: row.ax,     
            ay: row.ay,   
            az: row.az     
        };
    });
}

//-------------------- Affichage

function addbeau(){
    document.getElementById('data_affichage').style.display = 'none';
    document.getElementById('graphiques').style.display = 'none';
	document.getElementById('rotchart').style.display = 'none';
	document.getElementById('chart_XYZ_second').style.display = 'none';
	document.getElementById('dataTable2').style.display ='none';
}

//---------------------------- Fonction affichage data ----------------------------------------

function displayTable(data, table) {
    table.innerHTML = ""; // Reset table
    // Ajouter l'en-tête
    var header = table.insertRow();
    Object.keys(data[0]).forEach(key => {
        var th = document.createElement("th");
        th.textContent = key;
        header.appendChild(th);
    });
    // Ajouter les lignes
    data.forEach(row => {
        var tr = table.insertRow();
        Object.values(row).forEach(value => {
            var td = tr.insertCell();
            td.textContent = value;
        });
    });
}

let chartInstances = {};

function displayChart_XYZ(data,module,ctx,id) {
    let texte = module === "G" ? "Vitesse Angulaire (Rad/sec)" : "Vitesse (m/s)";
    console.log("Affichage du graphique XYZ", data);
    if (chartInstances[id]) {
        console.log("Destruction de l'ancien graphique XYZ");
        chartInstances[id].destroy(); // Supprime l'ancien graphique
    }
    chartInstances[id] = new Chart(ctx, {
        type: "line",
        data: {
            labels: data.map(row => row[Object.keys(data[0])[0]]),
            datasets: [
                { label: "X", data: data.map(row => row[Object.keys(data[0])[1]]), borderColor: "blue", fill: false },
                { label: "Y", data: data.map(row => row[Object.keys(data[0])[2]]), borderColor: "red", fill: false },
                { label: "Z", data: data.map(row => row[Object.keys(data[0])[3]]), borderColor: "green", fill: false }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { title: { display: true, text: "Temps (s)" }, 
                    grid: { color: "rgba(167, 158, 158, 0.28)" }
                },
                y: { title: { display: true, text: `"${texte}"` }, 
                    grid: { color: "rgba(167, 158, 158, 0.28)" }
                }
            },
            plugins: {
                zoom: {
                    limits: {
                        x: { min: "original", max: "original" }, // Garde la plage originale
                        y: { min: "original", max: "original" }
                    },
                    pan: {
                        enabled: true,
                        mode: "x", // Permet le défilement horizontal
                        touch: {
                            enabled: true
                        }
                    },
                    zoom: {
                        drag: { enabled: true },
                        wheel: { enabled: true },
                        pinch: { enabled: true },
                        mode: "x" // Permet le zoom uniquement sur l'axe X
                    }
                }
            }
        }
    });
    console.log("Graphique XYZ créé avec succès !");
}

let chartInstanceRotation = {};

function rotationChart_XYZ(data_rotation, ctx ,id) {
    
    console.log("Affichage du graphique XYZ", data_rotation);
    if (chartInstanceRotation[id]) {
        console.log("Destruction de l'ancien graphique des rotations XYZ");
        chartInstanceRotation[id].destroy(); // Supprime l'ancien graphique
    }
    chartInstanceRotation[id] = new Chart(ctx, {
        type: "line",
        data: {
            labels: data_rotation.map(row => row['time']),
            datasets: [
                { label: "X", data: data_rotation.map(row => row['rotation_X']), borderColor: "blue", fill: false },
                { label: "Y", data: data_rotation.map(row => row['rotation_Y']), borderColor: "red", fill: false },
                { label: "Z", data: data_rotation.map(row => row['rotation_Z']), borderColor: "green", fill: false }
            ]	
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { title: { display: true, text: "Temps (s)" },
                    grid: { color: "rgba(167, 158, 158, 0.28)" }
                },
                y: { title: { display: true, text: "Rotation (Degré)" },
                    grid: { color: "rgba(167, 158, 158, 0.28)" }
                }
            },
            plugins: {
                zoom: {
                    limits: {
                        x: { min: "original", max: "original" }, // Garde la plage originale
                        y: { min: "original", max: "original" }
                    },
                    pan: {
                        enabled: true,
                        mode: "x", // Permet le défilement horizontal
                        touch: {
                            enabled: true
                        }
                    },
                    zoom: {
                        drag: { enabled: true },
                        wheel: { enabled: true },
                        pinch: { enabled: true },
                        mode: "x" // Permet le zoom uniquement sur l'axe X
                    }
                }
            }
        },
    });
    console.log("Graphique rotation XYZ créé avec succès !");
}

function erase_graph(){
    for (let chartId in chartInstances) {
        if (chartInstances.hasOwnProperty(chartId)) {
            console.log(`Destruction du graphique pour ID: ${chartId}`);
            chartInstances[chartId].destroy(); // Détruire chaque graphique
        }
    }
    // Réinitialiser l'objet chartInstances
    chartInstances = {};
}

//----------------------------- Traitement des données ------------------------------

function biais(chemin)
{
    fetch('/correction',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ chemin:chemin })
    })
    .then(response => response.json()) // On récupère la réponse
    .then(result => {
        console.log("coucou");
        console.log(result.dfG);
        console.log(result.dfbiais);
        console.log(result.dffusion);
        var defaut = document.getElementById('default_table');
        var kalman = document.getElementById('bias_table');
        var fusion = document.getElementById('fusion_table');
        const dfG = result.dfG;
        const dfbiais = result.dfbiais;
        const dffusion = result.dffusion;
        displayTable(dfG, defaut);
        displayTable(dfbiais, kalman);
        displayTable(dffusion, fusion);
        var ctx = document.getElementById("chart_defaut").getContext("2d");
        var ctx2 = document.getElementById("chart_filtre").getContext("2d");
        var ctx3 = document.getElementById("chart_fusion").getContext("2d");
        displayChart_XYZ(dfG, "G", ctx, "A");
        displayChart_XYZ(dfbiais, "G", ctx2, "B");
        displayChart_XYZ(dffusion, "G", ctx3, "C");
        var ctxR = document.getElementById("chart_defaut_R").getContext("2d");
        var ctxR2 = document.getElementById("chart_filtre_R").getContext("2d");
        var ctxR3 = document.getElementById("chart_fusion_R").getContext("2d");
        rotationChart_XYZ(result.dfGR, ctxR, "AR");
        rotationChart_XYZ(result.dfbiaisR, ctxR2, "BR");
        rotationChart_XYZ(result.dffusionR, ctxR3, "CR");
        document.getElementById('tab').style.display = "block";
        document.getElementById('cor').style.display = "block";
    })
    .catch(error => console.error('Erreur lors de la récupération du fichier', error)); // Si erreur
}

//---------------------------- Fonction envoie commande Arduino -------------------------------

function visible()
{
	let type = document.getElementById("choixType").value;
	let doc = document.getElementById("depot");
	let files = doc.files.length > 0;
	let envoie = document.getElementById("envoie");
	if(files && type != "Default")
		envoie.style.display = "block";
	else
		envoie.style.display = "none";
}

function register_data(){
	const fichier = document.getElementById("depot").files;
	const test = document.getElementById("choixType").value;
	const donnee = new FormData();
	for (let i = 0; i < fichier.length; i++) {
        donnee.append('files[]', fichier[i]);  // Utilise 'files[]' pour envoyer plusieurs fichiers
    }
	donnee.append("type",test);
	fetch('/register',{
		method: 'POST',
		body: donnee
	})
	.then(response => response.text())
    .then(result => {
        loadselect1();
        alert(result);
    })
    .catch(error => console.error('Erreur lors de la récupération du fichier', error));
}

//------------ Affichage Statistiques du telephone --------------

function statsall(selectedBaseFolder){
    const telephone = document.getElementById("telephone");
	const phone = document.createElement("p");
	if (telephone.firstChild) {
    	telephone.removeChild(telephone.firstChild);
	}
	phone.innerHTML = `Voici la moyenne de la vitesse, des écart types et des variances pour un ${selectedBaseFolder}.`;
	telephone.appendChild(phone);
    fetch('/statistiques', {
        method: 'POST',
       	headers: {
            'Content-Type': 'application/json'
       	},
       	body: JSON.stringify({ baseFold: selectedBaseFolder })
    })
    .then(response => response.json())
	.then(result => {
        document.getElementById('info').style.display = "block";
    	// Afficher la structure du résultat pour déboguer
    	console.log('Données reçues:', result);
    	let groupedData = {};
    	// Parcourir les éléments de la réponse
    	for (let key in result) {
        	let item = result[key];
			const M = item.M;
        	const keyGroup = `${item.path || 'defaultPath'}-${item.axe || 'defaultAxe'}-${item.vit || 0}-${item.obj || 'defaultObj'}-${item.module}-${item.M}`;
        	if (!groupedData[keyGroup]) {
            	groupedData[keyGroup] = { moy: 0, std: 0, var: 0, count: 0 };
        	}
        	if (typeof item.moy === 'number' && !isNaN(item.moy)) {
        	    groupedData[keyGroup].moy += item.moy;
        	}
        	if (typeof item.std === 'number' && !isNaN(item.std)) {
        	    groupedData[keyGroup].std += item.std;
        	}
        	if (typeof item.var === 'number' && !isNaN(item.var)) {
        	    groupedData[keyGroup].var += item.var;
        	}
        	groupedData[keyGroup].count++;
        }
    	// Calculer les moyennes et autres statistiques
    	let resultats_tab = [];
        for (let key in groupedData) {
    	    let group = groupedData[key];
        	resultats_tab.push({
        	    path: key.split('-')[0],
            	axe: key.split('-')[1],
            	vit: parseFloat(key.split('-')[2]),
            	obj: key.split('-')[3],
				module: key.split('-')[4],
				M: key.split('-')[5],
            	moy: group.count > 0 ? (group.moy / group.count).toFixed(3) : 0,
            	std: group.count > 0 ? (group.std / group.count).toFixed(3) : 0,
            	var: group.count > 0 ? (group.var / group.count).toFixed(3) : 0,
        	});
        }
    	// Afficher les résultats traités
    	console.log(resultats_tab);
		const information = document.getElementById('info');
		while (information.firstChild) {
    		information.removeChild(information.firstChild);
    	}
		resultats_tab.forEach(item => {
			const section = document.createElement("div");
			section.classList.add("info-box");
			let exo = "";
			let deplacement = "";
			let typetest = "";
			if(item.path == "Rotation")
			{
				exo = "rad/s";
				deplacement = "degré(s)";
				if (item.module == "G")
					typetest = "Gyroscope";
				else
					typetest = "Accelerometre";
			}
			else if(item.path == "Translation")
			{
				exo = "m/s";
				deplacement = "cm";
				if (item.module == "A")
					typetest = "Accelerometre";
				else
					typetest = "Gyroscope";
			}
			let titre = document.createElement("p");
			let contenu = document.createElement("h3");
			if(item.M == 1){
				titre.innerHTML = `Accelerometre + Gyroscope. <br><br> ${item.path} à une vitesse de ${item.vit} ${exo} pour un déplacement de ${item.obj} ${deplacement} selon l'axe ${item.axe} pour un ${typetest}.`;
				contenu.innerHTML = `Moyenne Vitesse : ${item.moy} ${exo} &emsp; Moyenne Ecart Type : ${item.std} &emsp; Moyenne Variance : ${item.var} &emsp;`; 
			}else{
				titre.innerHTML = `${item.path} à une vitesse de ${item.vit} ${exo} pour un déplacement de ${item.obj} ${deplacement} selon l'axe ${item.axe} pour un ${typetest}.`;
				contenu.innerHTML = `Moyenne Vitesse : ${item.moy} ${exo} &emsp; Moyenne Ecart Type : ${item.std} &emsp; Moyenne Variance : ${item.var} &emsp;`; 
			}
			section.appendChild(titre);
			section.appendChild(contenu);
			information.appendChild(section);
		});
    })
    .catch(error => console.error('Erreur lors de la récupération du fichier', error));
}

function courbe_all(){
    const selectedBaseFolder = document.getElementById('baseFoldersSelect').value; // On récupère la valeur du 1er select par ID
	const selectedSubFolder = document.getElementById('subFoldersSelect').value; // On récupère la valeur du 2e select par ID
    const actionSelect = document.getElementById('precision').value;
	const excel = document.getElementById('fichierData').value;
	const modeleselect = document.getElementById('modele').value;
	fetch('/affichage', { // On execute la fonction du chemin indiquée
        method: 'POST', // Méthode POST pour l'envoie des données
    	headers: {
	        'Content-Type': 'application/json' // On indique que l'on envoie du JSON
        },
    	body: JSON.stringify({ baseFold: selectedBaseFolder, subFold: selectedSubFolder, tierFold: actionSelect, excel: excel, fin: modeleselect })
    })
	.then(response => response.json()) // On récupère la réponse
    .then(result => {
		document.getElementById('dataTable2').style.display ='none';
		document.getElementById("chart_XYZ_second").style.display = 'none';
		var table = document.getElementById("dataTable");
	    displayTable(result.data, table);
		var ctx = document.getElementById("chart_XYZ").getContext("2d");
		if(result.module != "M")
	    	displayChart_XYZ(result.data, result.module, ctx, "chart_XYZ");
		else
		{
			document.getElementById('dataTable2').style.display ='block';
			var mod = "G";
			displayChart_XYZ(result.data, mod, ctx, "chart_XYZ");
			var table2 = document.getElementById("dataTable2");
			let order = reorderData(result.acc);
        	displayTable(order, table2);
			document.getElementById("chart_XYZ_second").style.display = 'block';
			var ctx2 = document.getElementById("chart_XYZ_second").getContext("2d");
			var mod2 = "A"
			displayChart_XYZ(order, mod2, ctx2, "chart_XYZ_second");
		}	
		document.getElementById('std').textContent = "Ecart type : " + Math.round(result.std * 1000) / 1000;
		document.getElementById('var').textContent = "Variance : " + Math.round(result.var * 1000) / 1000;
		document.getElementById('data_affichage').style.display = 'block';
		document.getElementById('graphiques').style.display = 'block';
		if(result.module != "A")
		{
			var ctx3 = document.getElementById("rotationChart_XYZ").getContext("2d");
			document.getElementById('rotchart').style.display = 'block';
        	rotationChart_XYZ(result.data_rotation, ctx3, "chartRota");
			document.getElementById('moy').textContent = "Calcul/Obj (vit) : " + Math.round(result.moy * 1000) / 1000 + " / " + result.vit + " rad/s";
			document.getElementById('max').textContent = "Calcul/Obj (ang) : " + Math.round(result.max * 1000) / 1000 + " / " + result.yValue + " degrés";
		}
		else 
		{
			document.getElementById('moy').textContent = "";
			document.getElementById('max').textContent = "";
		}
	})
    .catch(error => console.error('Erreur lors de la récupération du fichier', error)); // Si erreur
}