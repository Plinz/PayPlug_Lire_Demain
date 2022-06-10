Utilisation du logiciel :
Au lancement, sélectionnez les fichiers en cliquant sur le bouton "Parcourir".
Attention uniquement des fichiers au format .csv peuvent être utilisé.
Et choisissez l'emplacement et le nom du fichier qui sera créé en cliquant sur Enregistrer sous.
Attention uniquement un fichier au format .txt peut être sauvegardé.
Appuyez sur OK pour lancer l'exécution.

En cas d'erreur de lecture du fichier, une nouvelle fenêtre s'ouvre avec une ligne d'explication et le choix d'arrêter l'exécution ou la continuer en ignorant l'erreur.
Un rapport d'erreur sera généré (nom du fichier de sortie).err

À la fin de l'exécution, une nouvelle fenêtre s'ouvre avec différents choix :
	- Ouvrir le dossier contenant le fichier résultat
	- Ouvrir le fichier résultat
	- Fermer le logiciel

Le code source de l'application est disponible à l'adresse :
https://github.com/Plinz/PayPlug_Lire_Demain

Vous pouvez me contacter à l'adresse e-mail :
antoine.duquennoy@protonmail.com

Commande pour générer l'exécutable : $ pyinstaller -F -n PayPlugTransformer_LIRE_DEMAIN -i favicon.ico --noconsole PayPlugTransformer.py